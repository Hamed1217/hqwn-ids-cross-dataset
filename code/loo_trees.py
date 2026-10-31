"""
Trees-only leave-one-attack-out (LOO) with and without the causal window features.  CPU only - no torch, no GPU.
Runs on your own computer in a minute or two per family (training sets are subsampled to 20 000 rows, as in
hybrid_ids_torch.py --exp loo, so the numbers are directly comparable with the earlier tables).

Input: splits.npz written by  stage1_cicids2017_pipeline.py --window_feats ...   (columns = flow features, then the
n_win window features at the END; with --window_min 1,5 that is 16 columns).

For every held-out family, seed and model (HistGB, XGBoost) it trains on three feature sets
    flow       the per-flow features only (reproduces the earlier no-window LOO table - a sanity check)
    win        the window features only
    flow+win   both
and reports AUC and recall at fixed false-alarm rates (thresholds from BENIGN validation scores, 1% and 0.1%).
At the end it prints the paired difference (flow+win minus flow) per family and the pre-agreed decision rule:
   "window features help" if recall@1%FPR rises by >= 0.15 on at least two of PortScan, DDoS, FTP-Patator, SSH-Patator.

Usage (PowerShell, in the folder with the script):
  pip install xgboost scikit-learn pandas numpy      (only if missing)
  python loo_trees.py --data "stage1_win/splits.npz" --out_dir loo_trees_out --seeds 5
Stricter test - hold out a whole category (all its families removed from train/val at once):
  python loo_trees.py --data ... --out_dir loo_groups_out --seeds 5 --groups "BruteForce=Patator;DoS=DoS;Web=Web"
"""
import argparse, os, re, time, warnings
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split


def sub_idx(y, n, seed):
    """Stratified subsample of indices (random when stratification is impossible) - same as hybrid_ids_torch.py"""
    if n is None or n <= 0 or n >= len(y):
        return np.arange(len(y))
    try:
        idx, _ = train_test_split(np.arange(len(y)), train_size=n, stratify=y, random_state=seed)
    except ValueError:
        idx = np.random.default_rng(seed).choice(len(y), n, replace=False)
    return np.sort(idx)


def fixed_fpr(s_ben_val, s_ben_test, s_pos):
    out = {}
    for tag, q in (("1%", 0.99), ("0.1%", 0.999)):
        t = np.quantile(s_ben_val, q)
        out[f"recall@{tag}FPR"] = float((s_pos >= t).mean()) if len(s_pos) else float("nan")
        out[f"fpr_test@{tag}"] = float((s_ben_test >= t).mean())
    out["auc"] = float(roc_auc_score(np.r_[np.ones(len(s_pos)), np.zeros(len(s_ben_test))],
                                     np.r_[s_pos, s_ben_test])) if len(s_pos) else float("nan")
    return out


def tree_models(seed):
    from sklearn.ensemble import HistGradientBoostingClassifier
    ms = {"HistGB": HistGradientBoostingClassifier(max_iter=200, random_state=seed)}
    try:
        from xgboost import XGBClassifier
        ms["XGBoost"] = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1, subsample=0.8,
                                      colsample_bytree=0.8, n_jobs=-1, tree_method="hist",
                                      random_state=seed, eval_metric="logloss")
    except ImportError:
        if not getattr(tree_models, "_warned", False):
            print("  xgboost نصب نیست -> فقط HistGB اجرا می‌شود (pip install xgboost)")
            tree_models._warned = True
    return ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="stage1_win/splits.npz")
    ap.add_argument("--out_dir", default="loo_trees_out")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--n_win", type=int, default=16, help="number of window features at the end of the feature matrix")
    ap.add_argument("--loo_fams", default="Bot,PortScan,SSH-Patator,Infiltration,DDoS,FTP-Patator")
    ap.add_argument("--groups", default="",
                    help='hold out whole categories, e.g. "BruteForce=Patator;DoS=DoS;Web=Web" (regex on labels)')
    ap.add_argument("--sets", default="flow,win,flow+win",
                    help="feature sets; also src,dst,pair and flow+src,flow+dst,flow+pair (window sub-groups)")
    ap.add_argument("--pos_split", choices=["all", "test"], default="all",
                    help="where the held-out family's flows come from: all splits (default) or the test split only")
    ap.add_argument("--max_train", type=int, default=20000)
    ap.add_argument("--val_max", type=int, default=20000)
    ap.add_argument("--test_max", type=int, default=100000)
    ap.add_argument("--fam_max", type=int, default=20000)
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    os.makedirs(a.out_dir, exist_ok=True)

    z = np.load(a.data, allow_pickle=True)
    Xtr, Xva, Xte = z["Xtr"], z["Xva"], z["Xte"]
    ytr, yva, yte = (z[k].astype(int) for k in ("ytr", "yva", "yte"))
    atr, ava, ate = (z[k].astype(str) for k in ("atr", "ava", "ate"))
    d = Xtr.shape[1]
    if not 0 < a.n_win < d:
        raise SystemExit(f"--n_win {a.n_win} does not fit {d} columns")
    fn = os.path.join(os.path.dirname(os.path.abspath(a.data)), "feature_names.json")
    if os.path.exists(fn):
        import json
        names = json.load(open(fn))
        if len(names) == d and not all(n.startswith("win_") for n in names[-a.n_win:]):
            raise SystemExit("the last --n_win columns are not win_* features (stage-1 run with --port_windows?) "
                             "-> use the splits made with --window_feats only (stage1_win)")
    nf = d - a.n_win
    sets_all = {"flow": np.arange(nf), "win": np.arange(nf, d), "flow+win": np.arange(d)}
    if a.n_win == 16:   # stage-1 layout for w=1,5: src_flows,src_dports,src_dips,dst_flows,dst_srcs,pair_flows,pair_dports,pairport
        grp = {"src": [0, 1, 2], "dst": [3, 4], "pair": [5, 6, 7]}
        for g, off in grp.items():
            cols = np.array([nf + o for o in off] + [nf + 8 + o for o in off])
            sets_all[g] = cols
            sets_all["flow+" + g] = np.r_[np.arange(nf), cols]
    want = [s.strip() for s in a.sets.split(",") if s.strip()]
    bad = [s for s in want if s not in sets_all]
    if bad:
        raise SystemExit(f"unknown --sets {bad}; available: {list(sets_all)}")
    sets = {s: sets_all[s] for s in want}
    print(f"train {len(ytr)}  val {len(yva)}  test {len(yte)}  columns {d} = {d - a.n_win} flow + {a.n_win} window")

    # ---- held-out units: single families (default) or whole categories (--groups, regex over labels) ----
    labs = sorted(set(np.unique(atr)) | set(np.unique(ava)) | set(np.unique(ate)))
    labs = [l for l in labs if l.upper() not in ("BENIGN", "0")]
    cnt = {l: int((atr == l).sum() + (ava == l).sum() + (ate == l).sum()) for l in labs}
    print("attack labels in file:", ", ".join(f"{l} ({cnt[l]})" for l in labs))
    if a.groups:
        units = []
        for part in a.groups.split(";"):
            if not part.strip():
                continue
            name, pat = part.split("=", 1)
            rx = re.compile(pat.strip(), re.I)
            mem = [l for l in labs if rx.search(l)]
            print(f"  group {name.strip():12s} = {mem}")
            units.append((name.strip(), mem))
    else:
        units = [(f.strip(), [f.strip()] if f.strip() in labs else []) for f in a.loo_fams.split(",") if f.strip()]

    te = sub_idx(yte, a.test_max, 0)
    ben_te_all = Xte[te][yte[te] == 0]
    rows, mrows, t0 = [], [], time.time()
    for unit, members in units:
        if not members:
            print(f"  '{unit}' not found, skipped")
            continue
        pos_l, lab_l = [], []
        for m in members:                       # every member capped at fam_max (keeps tiny families such as SQLi)
            pm = Xte[ate == m] if a.pos_split == "test" else np.concatenate([Xtr[atr == m], Xva[ava == m], Xte[ate == m]])
            if len(pm) == 0:
                print(f"  {m}: no flows in the test split -> skipped for --pos_split test")
                continue
            if len(pm) > a.fam_max:
                pm = pm[np.random.default_rng(0).choice(len(pm), a.fam_max, replace=False)]
            pos_l.append(pm); lab_l.append(np.full(len(pm), m))
        if not pos_l:
            continue
        pos, pos_lab = np.concatenate(pos_l), np.concatenate(lab_l)
        n_fam = sum(cnt[m] for m in members)
        mt, mv = ~np.isin(atr, members), ~np.isin(ava, members)
        Xtr_f, ytr_f, Xva_f, yva_f = Xtr[mt], ytr[mt], Xva[mv], yva[mv]
        for seed in range(a.seeds):
            i, j = sub_idx(ytr_f, a.max_train, seed), sub_idx(yva_f, a.val_max, seed)
            for sname, sl in sets.items():
                for mname, mdl in tree_models(seed).items():
                    mdl.fit(Xtr_f[i][:, sl], ytr_f[i])
                    sv = mdl.predict_proba(Xva_f[j][:, sl])[:, 1]
                    sv_ben = sv[yva_f[j] == 0]
                    sp = mdl.predict_proba(pos[:, sl])[:, 1]
                    fx = fixed_fpr(sv_ben, mdl.predict_proba(ben_te_all[:, sl])[:, 1], sp)
                    rows.append(dict(family=unit, n_family=n_fam, feature_set=sname, model=mname, seed=seed, **fx))
                    if len(members) > 1:
                        t1 = np.quantile(sv_ben, 0.99)
                        for m in members:
                            mrows.append(dict(group=unit, member=m, feature_set=sname, model=mname, seed=seed,
                                              rec1=float((sp[pos_lab == m] >= t1).mean())))
                    print(f"  {unit:14s} seed={seed} {sname:9s} {mname:8s} auc={fx['auc']:.3f} "
                          f"rec@1%={fx['recall@1%FPR']:.3f} rec@0.1%={fx['recall@0.1%FPR']:.3f}", flush=True)
        print(f"[{unit} done, elapsed {time.time() - t0:.0f}s]")

    tag = "groups" if a.groups else "families"
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(a.out_dir, f"loo_trees_{tag}.csv"), index=False)
    fam_order = [u for u, _ in units if u in set(df["family"])]
    for col in ("recall@1%FPR", "recall@0.1%FPR", "auc"):
        print(f"\n-- {col} (mean over {a.seeds} seeds)")
        pv = df.pivot_table(index="family", columns=["model", "feature_set"], values=col, aggfunc="mean")
        print(pv.reindex(fam_order).round(3).to_string())
    if mrows:
        md = pd.DataFrame(mrows)
        md.to_csv(os.path.join(a.out_dir, "loo_trees_group_members.csv"), index=False)
        print("\n-- recall@1%FPR per member family inside each held-out group (mean over seeds)")
        print(md.pivot_table(index=["group", "member"], columns=["model", "feature_set"], values="rec1",
                             aggfunc="mean").round(3).to_string())

    print("\n-- paired difference  (flow+win) - (flow)  of recall@1%FPR   [mean (sd) ; seeds improved / total]")
    gain = {}
    for mname in sorted(set(df["model"])):
        for fam in fam_order:
            x = df[(df.family == fam) & (df.model == mname)]
            p = x.pivot_table(index="seed", columns="feature_set", values="recall@1%FPR")
            if "flow" not in p or "flow+win" not in p:
                continue
            dlt = (p["flow+win"] - p["flow"]).values
            gain[(mname, fam)] = dlt.mean()
            print(f"  {mname:8s} {fam:14s} {dlt.mean():+.3f} ({dlt.std(ddof=1) if len(dlt) > 1 else 0:.3f}) ; "
                  f"{int((dlt > 0).sum())}/{len(dlt)}")
    key = [u for u in ("BruteForce", "DoS", "Web") if u in fam_order] if a.groups else \
          ["PortScan", "DDoS", "FTP-Patator", "SSH-Patator"]
    for mname in sorted(set(df["model"])):
        k = sum(gain.get((mname, f), -1) >= 0.15 for f in key)
        print(f"\nDECISION RULE ({mname}): units among {key} with recall@1%FPR gain >= 0.15 : {k}  ->  "
              + ("window features HELP (rule met)" if k >= 2 else "rule NOT met"))
    print(f"\nsaved -> {a.out_dir}")


if __name__ == "__main__":
    main()
