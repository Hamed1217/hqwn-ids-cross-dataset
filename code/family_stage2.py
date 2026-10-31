"""
STAGE 2 - naming the attack FAMILY of the flows the frozen detector flags (design fixed 2026-10-25 and written into
prereg_unsw.txt BEFORE the UNSW test). The detector (V3-SUP, threshold B) is not touched; its saved per-flow scores
(dump_scores.py) say which flows raised an alarm.

Families (2017 -> family): DoS = Hulk, GoldenEye, slowloris, Slowhttptest | DDoS = DDoS | Scan = PortScan |
  BruteForce = FTP-Patator, SSH-Patator | Web = Web Attack Brute Force / XSS / Sql Injection | Bot | Infiltration.
  Heartbleed (11 flows) is not trained. 2018 names map to the same families; UNSW: DoS -> DoS, Reconnaissance -> Scan,
  the 7 other UNSW classes have no 2017 family -> the correct answer is 'unknown' (open set).
Classifier: ONE model, HistGradientBoosting multi-class (200 iterations, random_state = seed) on the flow features +
  a summary of the 16-minute sequence (last minute, maximum; qkernel.novelty_features), trained on 2017 TRAINING
  attack flows, at most --cap flows per family (class-balanced subsample, seed). In a 'loo' task the held-out 2017
  types are removed from the classifier's training too (their family becomes unknown to it).
Open-set rule: 'unknown' if the maximum class probability < tau, tau = 5th percentile of the maximum probability on the
  2017 VALIDATION attack flows (95% of known-family flows accepted). Nothing is tuned on a target dataset.
Two views per seed x task:
  classification-only : every attack flow of the task's evaluated types (isolates stage 2)
  end-to-end          : only flows with an alarm of the detector at threshold B; detector misses counted separately;
                        false alarms (benign flows with an alarm) also receive a family -> reported
Metrics: multi-class confusion matrix (true family or 'unknown' x predicted family or 'unknown'), accuracy on
  known-family flows, macro-F1 (known families and with 'unknown' as a class), per-family recall, unknown-recall
  (flows of families the classifier never saw called 'unknown'), false-unknown rate on known families, AUROC of
  (1 - max probability) for new vs known. UNSW DoS: strict (DoS) primary, lenient (DoS or DDoS) secondary.

  python family_stage2.py --scores_dir "D:/revised model/scores_cross" --protocol cross --target ids2018 --target_cache "D:/revised model/cross_out4/ids2018_sample_v4.npz"
  python family_stage2.py --scores_dir "D:/revised model/unsw_primary" --protocol cross --target unsw --target_cache "D:/revised model/unsw/unsw_sample_v1h.npz"
"""
import argparse, glob, os, re, time, types, warnings
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score

UNK = "unknown"


def fam17(l):
    l = str(l).strip().lower()
    if "heartbleed" in l or l in ("benign", ""):
        return None
    if l == "ddos":
        return "DDoS"
    if l.startswith("dos"):
        return "DoS"
    if "portscan" in l:
        return "Scan"
    if "patator" in l:
        return "BruteForce"
    if l.startswith("web"):
        return "Web"
    if l == "bot":
        return "Bot"
    if "infiltration" in l:
        return "Infiltration"
    return None


def fam_target(l, target):
    s = str(l).strip().lower()
    if s == "benign":
        return "benign"
    if target == "unsw":
        return {"dos": "DoS", "reconnaissance": "Scan"}.get(s, "new:" + str(l).strip())
    if target == "ids2018":
        if "ddos" in s:
            return "DDoS"
        if s.startswith("dos"):
            return "DoS"
        if ("ftp" in s or "ssh" in s) and "brute" in s:
            return "BruteForce"
        if "brute force -web" in s or "xss" in s or "sql" in s:
            return "Web"
        if s == "bot":
            return "Bot"
        if s.startswith("infilt"):
            return "Infiltration"
        return "new:" + str(l).strip()
    f = fam17(l)                                                     # within 2017
    return f if f else "new:" + str(l).strip()


def load_inputs(a):
    """2017 train / validation (flows, sequences, labels) and the target rows in the order of hybrid_v3.build_target"""
    import hybrid_v3 as V
    ns = types.SimpleNamespace(protocol=a.protocol, target=a.target, s17_dir=a.s17_dir, target_cache=a.target_cache)
    D = V.load_data(ns)
    tg = V.build_target(D, ns)
    return dict(Xtr=D["Xtr"], Str=D["Str"], atr=D["atr"], ytr=D["ytr"], Xva=D["Xva"], Sva=D["Sva"], ava=D["ava"],
                yva=D["yva"], X=tg["X"], S=tg["S"], lab=np.asarray(tg["lab"]).astype(str))


def balanced(fam, cap, seed):
    rng = np.random.default_rng(seed)
    out = []
    for f in pd.unique(fam):
        idx = np.where(fam == f)[0]
        out.append(rng.choice(idx, min(cap, len(idx)), replace=False))
    return np.sort(np.concatenate(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores_dir", required=True)
    ap.add_argument("--protocol", choices=["cross", "within"], default="cross")
    ap.add_argument("--target", default="ids2018", help="ids2018 | unsw (within: ignored)")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--target_cache", default="")
    ap.add_argument("--detector", default="V3-SUP")
    ap.add_argument("--cap", type=int, default=20000)
    ap.add_argument("--q_unknown", type=float, default=5.0, help="percentile of the 2017 validation max-probability")
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    from qkernel import novelty_features
    from sklearn.ensemble import HistGradientBoostingClassifier
    t0 = time.time()
    I = load_inputs(a)
    ix = np.load(os.path.join(a.scores_dir, "target_index.npz"), allow_pickle=True)
    if len(ix["lab"]) != len(I["lab"]) or not np.array_equal(ix["lab"].astype(str), I["lab"]):
        raise SystemExit("target rows differ from the saved scores (other cache / protocol?)")
    tgt_name = "within" if a.protocol == "within" else a.target
    truth_all = np.array([fam_target(l, tgt_name) for l in I["lab"]], dtype=object)
    benign = truth_all == "benign"
    F_tr = novelty_features(I["Xtr"], I["Str"]).astype("float32")
    F_va = novelty_features(I["Xva"], I["Sva"]).astype("float32")
    F_T = novelty_features(I["X"], I["S"]).astype("float32")
    f_tr = np.array([fam17(x) for x in I["atr"]], dtype=object)
    f_va = np.array([fam17(x) for x in I["ava"]], dtype=object)
    rows, cms = [], {}
    files = sorted(glob.glob(os.path.join(a.scores_dir, "scores_seed*.npz")), key=lambda p: int(re.findall(r"(\d+)\.npz$", p)[0]))
    for path in files:
        seed = int(re.findall(r"(\d+)\.npz$", path)[0])
        z = np.load(path)
        for key in [k for k in z.files if k.endswith(f"|{a.detector}|target")]:
            scen, held, _, _ = key.split("|")
            held_types = [] if held == "-" else held.split("+")
            okt = (I["ytr"] == 1) & pd.notna(f_tr) & ~np.isin(I["atr"], held_types)
            okv = (I["yva"] == 1) & pd.notna(f_va) & ~np.isin(I["ava"], held_types)
            tr = np.where(okt)[0][balanced(f_tr[okt], a.cap, seed)]
            clf = HistGradientBoostingClassifier(max_iter=200, random_state=seed).fit(F_tr[tr], f_tr[tr].astype(str))
            cls = clf.classes_
            pv = clf.predict_proba(F_va[okv]).max(1)
            tau = float(np.percentile(pv, a.q_unknown))
            tgt, cal = z[key], z[key[:-len("target")] + "cal"]
            thr = np.quantile(cal, 0.99)
            ev = ~np.isnan(tgt)
            att = ev & ~benign
            P = clf.predict_proba(F_T[att])
            mp = P.max(1)
            pred = np.where(mp < tau, UNK, cls[P.argmax(1)]).astype(object)
            truth = truth_all[att]
            teff = np.array([t if t in cls else UNK for t in truth], dtype=object)
            alarm = tgt[att] > thr
            known = teff != UNK
            r = dict(seed=seed, scenario=scen, held=held, tau=tau, families_trained=len(cls),
                     n_known_flows=int(known.sum()), n_unknown_flows=int((~known).sum()))
            for view, m in (("cls", np.ones(len(pred), bool)), ("e2e", alarm)):
                k, u = known & m, (~known) & m
                r[f"{view}_n"] = int(m.sum())
                r[f"{view}_acc_known"] = float((pred[k] == teff[k]).mean()) if k.any() else np.nan
                labs_k = sorted(set(teff[k]))
                r[f"{view}_macro_f1_known"] = (float(f1_score(teff[k], pred[k], labels=labs_k, average="macro", zero_division=0))
                                               if k.any() else np.nan)
                labs_all = sorted(set(teff[m]))
                r[f"{view}_macro_f1_with_unknown"] = (float(f1_score(teff[m], pred[m], labels=labs_all, average="macro",
                                                                     zero_division=0)) if m.any() else np.nan)
                r[f"{view}_unknown_recall"] = float((pred[u] == UNK).mean()) if u.any() else np.nan
                r[f"{view}_false_unknown"] = float((pred[k] == UNK).mean()) if k.any() else np.nan
                if tgt_name == "unsw":
                    d = m & (truth == "DoS") & known
                    r[f"{view}_dos_lenient_acc"] = float(np.isin(pred[d], ["DoS", "DDoS"]).mean()) if d.any() else np.nan
                c = cms.setdefault((view, scen), {})
                for t_, p_ in zip(teff[m], pred[m]):
                    c[(t_, p_)] = c.get((t_, p_), 0) + 1
            try:
                r["auroc_new_vs_known"] = float(roc_auc_score(~known, 1 - mp)) if known.any() and (~known).any() else np.nan
            except ValueError:
                r["auroc_new_vs_known"] = np.nan
            r["detected_share"] = float(alarm.mean())
            fa = ev & benign & (tgt > thr)
            if fa.any():
                Pb = clf.predict_proba(F_T[fa])
                pb = np.where(Pb.max(1) < tau, UNK, cls[Pb.argmax(1)])
                r["false_alarms"] = int(fa.sum())
                r["false_alarms_called_unknown"] = float((pb == UNK).mean())
                c = cms.setdefault(("e2e", scen), {})
                for p_ in pb:
                    c[("benign (false alarm)", p_)] = c.get(("benign (false alarm)", p_), 0) + 1
            for f in sorted(set(teff)):
                sel = teff == f
                r[f"recall_cls[{f}]"] = float((pred[sel] == f).mean())
            rows.append(r)
            print(f"  seed {seed} {scen:5s} {held[:30]:30s} acc(known) {r['cls_acc_known']:.3f} | unknown recall "
                  f"{r['cls_unknown_recall']:.3f} | end-to-end acc {r['e2e_acc_known']:.3f} [{time.time() - t0:.0f}s]", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(a.scores_dir, "family_metrics.csv"), index=False)
    L = [f"ATTACK-FAMILY STAGE | detector {a.detector} @ threshold B | target {tgt_name} | {len(files)} seeds"]
    main_cols = ["cls_acc_known", "cls_macro_f1_known", "cls_macro_f1_with_unknown", "cls_unknown_recall",
                 "cls_false_unknown", "auroc_new_vs_known", "detected_share", "e2e_acc_known", "e2e_macro_f1_known",
                 "e2e_unknown_recall"] + [c for c in df.columns if c.endswith("dos_lenient_acc")] + \
                ["false_alarms_called_unknown"]
    main_cols = [c for c in main_cols if c in df]
    for scen, g in df.groupby("scenario", sort=False):
        s = g.groupby("seed")[main_cols].mean().agg(["mean", "std"]).T.round(3)
        L += ["", f"== {scen}: mean (sd) over seeds (loo: mean over held-out families first)", s.to_string()]
        rc = [c for c in g.columns if c.startswith("recall_cls[")]
        L += ["per-family recall (classification-only; 'unknown' = families the classifier never saw):",
              g.groupby("seed")[rc].mean().mean().round(3).to_string()]
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        plt = None
    for (view, scen), c in cms.items():
        cm = pd.Series(c).unstack(fill_value=0)
        cm.index.name, cm.columns.name = "true", "predicted"
        cm.to_csv(os.path.join(a.scores_dir, f"family_confusion_{view}_{scen}.csv"))
        L += ["", f"confusion counts summed over seeds ({view}, {scen}):", cm.to_string()]
        if plt is not None:
            R = cm.div(cm.sum(1), axis=0)
            fig, ax = plt.subplots(figsize=(1.0 + 0.7 * R.shape[1], 0.8 + 0.45 * R.shape[0]))
            ax.imshow(R.values, cmap="Blues", vmin=0, vmax=1)
            for i in range(R.shape[0]):
                for j in range(R.shape[1]):
                    ax.text(j, i, f"{R.values[i, j]:.0%}", ha="center", va="center", fontsize=7,
                            color="white" if R.values[i, j] > 0.6 else "black")
            ax.set_xticks(range(R.shape[1]), R.columns, rotation=45, ha="right", fontsize=8)
            ax.set_yticks(range(R.shape[0]), R.index, fontsize=8)
            ax.set_xlabel("predicted family"); ax.set_ylabel("true family")
            ax.set_title(f"Attack-family stage - {'all attack flows' if view == 'cls' else 'flows flagged by the detector'} ({scen})",
                         fontsize=9)
            fig.tight_layout()
            p = os.path.join(a.scores_dir, f"family_confusion_{view}_{scen}")
            fig.savefig(p + ".png", dpi=600); fig.savefig(p + ".pdf"); plt.close(fig)
            L.append(f"figure saved: {p}.png / .pdf")
    open(os.path.join(a.scores_dir, "family_report.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
