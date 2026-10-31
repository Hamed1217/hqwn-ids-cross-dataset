"""
Analysis of the saved per-flow scores (dump_scores.py). First use: the TIE problem of the tree.

The tree expert's scores take few distinct values; the 99th percentile of the calibration benign falls on a tie, so at
"1% false alarms" the tree really runs at ~0.5% on the test benign (v33_cross10: 0.0052) and its recall is
pessimistic. Here every model is compared at EXACTLY the same false-alarm rate on the test benign third:
  recall at FPR = f from the ROC curve, linearly interpolated between its points (= the expected recall of the same
  model with random tie-breaking; fair to models with ties). f = 1% and 0.1%.
This uses the test benign to place the threshold, so it is an ANALYSIS of the ranking quality at a matched operating
point, not a deployable threshold (threshold B stays the deployable rule and the primary metric).
Also: PR-AUC (average precision) per type and pooled, and the same paired tests as hybrid_v3 (one-sided Wilcoxon over
seed x type and per seed) for the pairs given with --pairs.

  python analyze_scores.py --scores_dir "D:/revised model/scores_cross"
  python analyze_scores.py --scores_dir ... --pairs "V3-SUP>TREE,V3-SUP>V3-SUP-DENSE"
"""
import argparse, glob, os, re
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, average_precision_score

TINY = 50


def tpr_at(neg, pos, f):
    y = np.r_[np.zeros(len(neg)), np.ones(len(pos))]
    fpr, tpr, _ = roc_curve(y, np.r_[neg, pos], drop_intermediate=False)
    return float(np.interp(f, fpr, tpr))


def load(scores_dir):
    ix = np.load(os.path.join(scores_dir, "target_index.npz"), allow_pickle=True)
    lab, bte_i = ix["lab"].astype(str), ix["bte_i"]
    rows = []
    for f in sorted(glob.glob(os.path.join(scores_dir, "scores_seed*.npz"))):
        seed = int(re.findall(r"scores_seed(\d+)", f)[0])
        z = np.load(f)
        for key in z.files:
            if not key.endswith("|target"):
                continue
            scen, held, model, _ = key.split("|")
            tgt, cal = z[key], z[key[:-len("target")] + "cal"]
            neg = tgt[bte_i]
            thrB = np.quantile(cal, 0.99)
            ev = ~np.isnan(tgt)
            ev[bte_i] = False
            types_ = pd.unique(lab[ev])
            for t in types_:
                pos = tgt[lab == t]
                y = np.r_[np.zeros(len(neg)), np.ones(len(pos))]
                rows.append(dict(seed=seed, scenario=scen, held=held, model=model, type=t, n=len(pos),
                                 tiny=len(pos) < TINY, recall_B=float((pos > thrB).mean()),
                                 fpr_B=float((neg > thrB).mean()), recall_at1=tpr_at(neg, pos, 0.01),
                                 recall_at01=tpr_at(neg, pos, 0.001),
                                 pr_auc=float(average_precision_score(y, np.r_[neg, pos]))))
    return pd.DataFrame(rows)


def paired(df, col, a, b, say):
    from scipy.stats import wilcoxon
    x = df[df.model == a].set_index(["seed", "held", "type"])[col]
    y = df[df.model == b].set_index(["seed", "held", "type"])[col]
    j = x.index.intersection(y.index)
    if len(j) == 0:
        return
    d = (x[j] - y[j]).values
    p = wilcoxon(d, alternative="greater").pvalue if np.any(d != 0) else np.nan
    ds = (x[j] - y[j]).groupby(level="seed").mean()
    ps = wilcoxon(ds.values, alternative="greater").pvalue if np.any(ds.values != 0) and len(ds) > 1 else np.nan
    say(f"  {a:12s} vs {b:12s} [{col:11s}] mean diff {d.mean():+.3f}  p = {p:.4f} {'SUPPORTED' if p < 0.05 else 'not supported'}"
        f"   | per seed: wins {(ds > 0).sum()}/{len(ds)}, p = {ps:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores_dir", required=True)
    ap.add_argument("--pairs", default="V3-SUP>TREE")
    a = ap.parse_args()
    df = load(a.scores_dir)
    df.to_csv(os.path.join(a.scores_dir, "matched_fpr_per_type.csv"), index=False)
    L = []
    def say(s):
        print(s)
        L.append(s)
    cols = ["recall_B", "fpr_B", "recall_at1", "recall_at01", "pr_auc"]
    for scen, g in df.groupby("scenario", sort=False):
        level = "HARD / known" if scen == "known" else "HARDEST or MEDIUM / loo"
        say(f"\n==== {scen} ({level}); mean (sd) over seeds of the mean over attack types")
        for sub, gg in (("all types", g), ("non-tiny types", g[~g.tiny.astype(bool)])):
            m = gg.groupby(["model", "seed"])[cols].mean().groupby("model").agg(["mean", "std"])
            tab = pd.DataFrame({c: m[c]["mean"].map("{:.3f}".format) + " (" + m[c]["std"].map("{:.3f}".format) + ")"
                                for c in cols})
            say(f"-- {sub}: recall_B / fpr_B = threshold B (deployable rule); recall_at1 / recall_at01 = recall at "
                f"EXACTLY 1% / 0.1% test false alarms (ROC-interpolated, tie-fair); pr_auc = average precision\n"
                + tab.sort_values("recall_at1", ascending=False).to_string())
        say("-- paired tests (one-sided Wilcoxon over seed x type; per seed = mean over types)")
        for pair in [p.strip() for p in a.pairs.split(",") if ">" in p]:
            x, y = [s.strip() for s in pair.split(">")]
            for c in ("recall_B", "recall_at1", "recall_at01", "pr_auc"):
                paired(g, c, x, y, say)
        say("-- per type, recall at exactly 1% test false alarms:")
        say(g.groupby(["type", "model"]).recall_at1.mean().unstack().round(3).to_string())
    open(os.path.join(a.scores_dir, "matched_fpr_report.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"\nsaved -> matched_fpr_report.txt, matched_fpr_per_type.csv in {a.scores_dir}")


if __name__ == "__main__":
    main()
