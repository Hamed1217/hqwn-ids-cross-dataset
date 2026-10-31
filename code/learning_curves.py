"""
Learning curves (over- / under-fitting check) for the frozen v3 models. hybrid_v3.py is IMPORTED UNCHANGED; the
training loop below is a copy of hybrid_v3.fit with logging added. Everything that is logged is computed inside
torch.random.fork_rng, so the training itself (random numbers, batches, dropout) is exactly the one of hybrid_v3:
the first epochs reproduce the real model, the curve is only continued further (--epochs) to show what WOULD happen.

Per epoch (networks V3-SUP and V3-SUP-DENSE) and per boosting iteration (the HistGB tree expert):
  - loss on the 2017 TRAINING rows (fixed subset, eval mode) and on the 2017 VALIDATION rows (the early-stopping set)
  - accuracy (threshold 0.5) and AUC on both
  - on the TARGET network (2018, labels used for the PLOT ONLY, never for training or stopping): AUC, partial AUC up to
    1% FPR, mean recall over attack types at threshold B (1% false alarms on the target calibration benign third)
The real setting (6 epochs, early stopping patience 2 on the 2017 validation loss) is marked on the figure.

How to read it:
  overfitting  = training loss keeps falling while validation loss rises (gap opens)
  underfitting = both losses still high and still falling where training stops
  NETWORK SHIFT (our case, expected) = 2017 train and validation agree (no overfitting) but the target AUC / recall
  stay far lower: the loss across networks is a distribution-shift gap, not an over-fitting gap.

  python learning_curves.py --smoke
  python learning_curves.py --s17_dir "D:/revised model/stage1_pw" --target_cache "D:/revised model/cross_out4/ids2018_sample_v4.npz" --out_dir "D:/revised model/curves"
  (about 1-1.5 h with the defaults: 2 networks x 3 seeds x 20 epochs + the tree; --seeds 1 for a quick look)
"""
import argparse, os, time, types, warnings
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score, log_loss
import hybrid_v3 as V
import hybrid_v2 as H


def target_metrics(s_all, s_cal, s_bte, lab, types_):
    thr = np.quantile(s_cal, 0.99)
    rec = [float((s_all[lab == t] > thr).mean()) for t in types_]
    pos = s_all[~V.is_benign(lab)]
    y = np.r_[np.zeros(len(s_bte)), np.ones(len(pos))]
    s = np.r_[s_bte, pos]
    return dict(target_auc=roc_auc_score(y, s), target_pauc1=roc_auc_score(y, s, max_fpr=0.01),
                target_recall1=float(np.mean(rec)), target_fpr=float((s_bte > thr).mean()))


def src_metrics(prefix, p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return {f"{prefix}_loss": log_loss(y, p, labels=[0, 1]), f"{prefix}_auc": roc_auc_score(y, p),
            f"{prefix}_acc": float(((p > 0.5) == y).mean())}


def fit_logged(cfg, Xf, Xs, y, Vf, Vs, vy, Af, As, seed, a, dev, d, evalfn, epochs):
    """= hybrid_v3.fit (same order of random draws) + a log row per epoch; runs `epochs` epochs without stopping"""
    torch.manual_seed(seed); np.random.seed(seed)
    c = V.CONFIGS[cfg]
    model = V.HybridV3(d, Xs.shape[1], Xs.shape[2], branches=c["branches"], spiking=c.get("spiking", True),
                       wavelet=c.get("wavelet", True), attn=c.get("attn", True), shuffle=c.get("shuffle", False),
                       compact=c.get("compact"), rank=c.get("rank", 4)).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    pos = max(int(y.sum()), 1)
    lossf = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(min((len(y) - pos) / pos, 20.0), device=dev))
    tf, ts, ty = (torch.tensor(v) for v in (Xf, Xs, y.astype("float32")))
    vf, vs, vt = (torch.tensor(v, device=dev) for v in (Vf, Vs, vy.astype("float32")))
    use_align = c["align"] > 0 and Af is not None and len(c["branches"]) > 1
    if use_align:
        af, as_ = torch.tensor(Af), torch.tensor(As)
    g = torch.Generator().manual_seed(seed)
    best, bad, real_stop, log = np.inf, 0, None, []
    for ep in range(epochs):
        model.train()
        perm = torch.randperm(len(ty), generator=g)
        run_bce, run_mmd, nb = 0.0, 0.0, 0
        for k in range(0, len(perm), a.bs):
            b = perm[k:k + a.bs]
            out, z = model(tf[b].to(dev), ts[b].to(dev), return_z=True)
            yb = ty[b].to(dev)
            bce = lossf(out, yb)
            loss = bce + 0.1 * model.regularizer().to(dev) + a.lb * model.balance_loss().to(dev)
            if use_align:
                zb = z[yb == 0][:256]
                if len(zb) >= 16:
                    tb = torch.randint(0, len(af), (len(zb),), generator=g)
                    _, zt = model(af[tb].to(dev), as_[tb].to(dev), return_z=True)
                    m = V.mmd(zb, zt)
                    loss = loss + c["align"] * m
                    run_mmd += float(m)
            opt.zero_grad(); loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            run_bce += float(bce); nb += 1
        model.eval()
        with torch.no_grad(), torch.random.fork_rng(devices=[]):
            torch.manual_seed(12345)
            vl = float(np.mean([lossf(model(vf[k:k + 4096], vs[k:k + 4096]), vt[k:k + 4096]).item()
                                for k in range(0, len(vt), 4096)]))
        improved = vl < best - 1e-4
        if improved:
            best, bad = vl, 0
        else:
            bad += 1
        if real_stop is None and (bad >= a.patience or ep + 1 >= a.epochs):
            real_stop = ep + 1                                     # where hybrid_v3.fit stops
        with torch.random.fork_rng(devices=[]):
            row = evalfn(model)
        row.update(epoch=ep + 1, train_bce_running=run_bce / max(nb, 1), align_mmd=run_mmd / max(nb, 1),
                   val_bce_weighted=vl, improved=improved)
        log.append(row)
        print(f"    epoch {ep + 1:2d}: val loss {vl:.4f} | target AUC {row['target_auc']:.3f} recall@1% "
              f"{row['target_recall1']:.3f}{'  <- real training stops here' if real_stop == ep + 1 else ''}", flush=True)
    return log, real_stop


def plot(df, out_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("(figures skipped: matplotlib is not installed; send learning_curves.csv to make them elsewhere)")
        return
    for mod, g in df.groupby("model"):
        xk = "iteration" if mod.startswith("HistGB") else "epoch"
        num = g.select_dtypes("number").drop(columns=[c for c in ("epoch", "iteration", "seed") if c in g])
        agg = num.groupby(g[xk]).agg(["mean", "std"])
        x = agg.index.values
        fig, ax = plt.subplots(1, 4, figsize=(17, 3.6))
        def band(axi, col, label, color, ls="-"):
            m, s = agg[col]["mean"].values, agg[col]["std"].fillna(0).values
            axi.plot(x, m, ls, color=color, label=label, lw=1.8)
            axi.fill_between(x, m - s, m + s, color=color, alpha=0.15, lw=0)
        band(ax[0], "train_loss", "2017 train", "#1f77b4"); band(ax[0], "val_loss", "2017 validation", "#ff7f0e")
        ax[0].set_title("Loss (log loss)"); ax[0].set_xlabel(xk)
        band(ax[1], "train_auc", "2017 train", "#1f77b4"); band(ax[1], "val_auc", "2017 validation", "#ff7f0e")
        band(ax[1], "target_auc", "2018 target", "#2ca02c")
        ax[1].set_title("ROC-AUC"); ax[1].set_xlabel(xk)
        band(ax[3], "train_acc", "2017 train", "#1f77b4"); band(ax[3], "val_acc", "2017 validation", "#ff7f0e")
        ax[3].set_title("Accuracy (threshold 0.5)"); ax[3].set_xlabel(xk)
        band(ax[2], "target_recall1", "2018 mean recall @1% FPR", "#2ca02c")
        band(ax[2], "target_pauc1", "2018 partial AUC (1% FPR)", "#9467bd", "--")
        ax[2].set_title("Target network (labels for the plot only)"); ax[2].set_xlabel(xk)
        if "real_stop" in g and g.real_stop.notna().any():
            for axi in ax:
                for rs in sorted(set(g.real_stop.dropna().astype(int))):
                    axi.axvline(rs, color="grey", ls=":", lw=1)
            ax[0].text(0.98, 0.95, "dotted: where the real training stops", transform=ax[0].transAxes, ha="right",
                       va="top", fontsize=7, color="grey")
        for axi in ax:
            axi.legend(fontsize=7); axi.grid(alpha=0.3)
        fig.suptitle(f"Learning curves - {mod} (mean +- sd over seeds)", fontsize=10)
        fig.tight_layout()
        path = os.path.join(out_dir, f"learning_curve_{mod.replace(' ', '_')}")
        fig.savefig(path + ".png", dpi=600); fig.savefig(path + ".pdf"); plt.close(fig)
        print(f"  figure saved: {path}.png / .pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--target_cache", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--out_dir", default="curves")
    ap.add_argument("--configs", default="V3-SUP,V3-SUP-DENSE")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=20, help="continued beyond the real 6 to show the trend")
    ap.add_argument("--tree_every", type=int, default=10, help="evaluate the tree every k boosting iterations")
    ap.add_argument("--smoke", action="store_true")
    a0 = ap.parse_args()
    warnings.filterwarnings("ignore")
    os.makedirs(a0.out_dir, exist_ok=True)
    a = types.SimpleNamespace(protocol="cross", target="ids2018", s17_dir=a0.s17_dir, target_cache=a0.target_cache,
                              mode="known", max_train=30000, val_max=10000, tree_train=100000, epochs=6, patience=2,
                              bs=512, lr=2e-3, lb=0.1)
    if a0.smoke:
        a.max_train, a.val_max, a.tree_train = 3000, 1500, 3000
        a0.seeds, a0.epochs = 1, 4
        D = V.make_smoke("cross")
    else:
        D = V.load_data(a)
    dev = torch.device("cpu")
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    tg = V.build_target(D, a)
    lab = tg["lab"]
    types_ = [t for t in pd.Series(lab[~V.is_benign(lab)]).value_counts().index]
    d = D["Xtr"].shape[1]
    rows, t0 = [], time.time()
    from sklearn.ensemble import HistGradientBoostingClassifier
    for seed in range(a0.seeds):
        i = H.sub_idx(D["ytr"], a.max_train, seed)
        j = H.sub_idx(D["yva"], a.val_max, seed)
        rest = np.setdiff1d(np.arange(len(D["ytr"])), i)
        k = rest[H.sub_idx(D["ytr"][rest], a.tree_train, seed + 100)]
        tree = HistGradientBoostingClassifier(max_iter=200, random_state=seed).fit(D["Xtr"][k], D["ytr"][k])
        # ---- tree expert, staged over its boosting iterations
        ktr = k[:20000]
        stages = zip(tree.staged_predict_proba(D["Xtr"][ktr]), tree.staged_predict_proba(D["Xva"][j]),
                     tree.staged_predict_proba(tg["X"]), tree.staged_predict_proba(tg["calX"]))
        for it, (ptr, pva, pall, pcal) in enumerate(stages, start=1):
            if it % a0.tree_every and it != tree.n_iter_:
                continue
            sa, sc = pall[:, 1], pcal[:, 1]
            sb = sa[tg["bte_i"]] if tg.get("bte_i") is not None and len(sa) == len(lab) else pall[:, 1]
            r = dict(model="HistGB tree expert", seed=seed, iteration=it, **src_metrics("train", ptr[:, 1], D["ytr"][ktr]),
                     **src_metrics("val", pva[:, 1], D["yva"][j]), **target_metrics(sa, sc, sb, lab, types_))
            rows.append(r)
        print(f"  seed {seed}: tree curve done ({tree.n_iter_} iterations) [{time.time() - t0:.0f}s]", flush=True)

        def tlogit(M):
            p = np.clip(tree.predict_proba(M)[:, 1], 1e-6, 1 - 1e-6)
            return (np.clip(np.log(p / (1 - p)), -10, 10) / 5).astype("float32")[:, None]

        def cat(X):
            return np.hstack([X, tlogit(X), np.zeros((len(X), 1), "float32")]).astype("float32")

        Xi, Xj = cat(D["Xtr"][i]), cat(D["Xva"][j])
        XT, XC = cat(tg["X"]), cat(tg["calX"])
        sub = np.random.default_rng(seed).choice(len(i), min(20000, len(i)), replace=False)

        def evalfn(model):
            ptr, _ = V.score(model, Xi[sub], D["Str"][i][sub], dev)
            pva, _ = V.score(model, Xj, D["Sva"][j], dev)
            sa, _ = V.score(model, XT, tg["S"], dev)
            sc, _ = V.score(model, XC, tg["calS"], dev)
            sb = sa[tg["bte_i"]]
            return dict(**src_metrics("train", ptr, D["ytr"][i][sub]), **src_metrics("val", pva, D["yva"][j]),
                        **target_metrics(sa, sc, sb, lab, types_))

        for cfg in [c.strip() for c in a0.configs.split(",") if c.strip()]:
            print(f"  seed {seed}: {cfg} ...", flush=True)
            log, real_stop = fit_logged(cfg, Xi, D["Str"][i], D["ytr"][i], Xj, D["Sva"][j], D["yva"][j],
                                        cat(tg["alX"]), tg["alS"], seed, a, dev, d, evalfn, a0.epochs)
            rows += [dict(model=cfg, seed=seed, real_stop=real_stop, **r) for r in log]
        pd.DataFrame(rows).to_csv(os.path.join(a0.out_dir, "learning_curves.csv"), index=False)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(a0.out_dir, "learning_curves.csv"), index=False)
    L = ["LEARNING CURVES (mean over seeds)"]
    for mod, g in df.groupby("model"):
        xk = "iteration" if mod.startswith("HistGB") else "epoch"
        m = g.groupby(xk)[["train_loss", "val_loss", "train_acc", "val_acc", "train_auc", "val_auc", "target_auc",
                           "target_recall1"]].mean()
        L += ["", f"== {mod}", m.round(4).to_string()]
        if "real_stop" in g and g.real_stop.notna().any():
            L.append(f"real training stops at epoch(s) {sorted(set(g.real_stop.dropna().astype(int)))}")
        last = m.iloc[-1]
        L.append(f"final: train-validation loss gap {last.val_loss - last.train_loss:+.4f} | validation-target AUC gap "
                 f"{last.val_auc - last.target_auc:+.4f}")
    open(os.path.join(a0.out_dir, "learning_curves_report.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))
    plot(df, a0.out_dir)


if __name__ == "__main__":
    main()
