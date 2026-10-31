"""
All the usual evaluation metrics for every hybrid_v3 run, computed from the saved v3_results.csv: confusion matrix,
accuracy, precision, recall (detection rate), F1, false-alarm rate, specificity, balanced accuracy, MCC, ROC-AUC and
partial AUC, at the operating point of the paper (threshold B = 1% false alarms on the local calibration benign) and
at 0.1%. The model itself is NOT touched and nothing is re-run, so the frozen code fingerprint stays the same and the
script also works for runs that are already finished (easy, medium, hard levels).

Why this is exact: v3_results.csv stores, per seed x task x model x attack type, recall = TP/n and the false-alarm
rate on the test benign third = FP/n_benign_test. With n (column "n") and n_benign_test the counts TP, FN, FP, TN are
recovered exactly. ROC-AUC and the standardised partial AUC over all attack types together are the n-weighted means of
the per-type values (AUC = probability that an attack flow outranks a benign flow, averaged over attack flows; the
McClish standardisation is linear). n_benign_test is inferred from the stored rates (they are fractions k/n_benign_test)
or can be given with --n_bte.

Notes for the paper:
- The model is a BINARY detector (benign vs attack), so the confusion matrix is 2x2. The per-type table (share of each
  attack type detected) plays the role of the multi-class matrix; the model does not name the attack type.
- Accuracy, precision and F1 depend on the attack share of the evaluation set (here: test benign third + all flows of
  the evaluated attack types; printed as "prevalence"). Recall, false-alarm rate, balanced accuracy, AUC do not.
  precision_at_prev1 = precision if attacks were 1% of the traffic (same recall and false-alarm rate).
- "loo": every attack type is scored by the model trained WITHOUT its family; attack counts are summed over those
  models and the benign side (FP, TN) is the mean over them.

  python derive_metrics.py --results "D:/revised model/v33_within10/v3_results.csv" --plots
  python derive_metrics.py --results "D:/revised model/v31_within/v3_results.csv" "D:/revised model/v33_cross10/v3_results.csv" --plots
"""
import argparse, os
from fractions import Fraction
from math import gcd

import numpy as np
import pandas as pd

TINY = 50


def infer_n_bte(df):
    v = pd.concat([df["fpr_test1"], df["fpr_test01"]]).dropna()
    v = v[(v > 0) & (v < 1)].unique()
    if len(v) == 0:
        raise SystemExit("cannot infer the size of the test benign third (all false-alarm rates are 0); give --n_bte")
    n = 1
    for x in v:
        d = Fraction(float(x)).limit_denominator(20_000_000).denominator
        n = n * d // gcd(n, d)
    k = np.array(v) * n
    if n < 1000 or n > 20_000_000 or np.abs(k - np.round(k)).max() > 1e-4:
        raise SystemExit(f"inferred test-benign size {n} is not consistent; give --n_bte")
    return int(n)


def scores(tp, fn, fp, tn):
    tp, fn, fp, tn = (np.asarray(x, float) for x in (tp, fn, fp, tn))
    P, N = tp + fn, fp + tn
    with np.errstate(divide="ignore", invalid="ignore"):
        rec = tp / P
        fpr = fp / N
        prec = np.where(tp + fp > 0, tp / (tp + fp), np.nan)
        f1 = np.where(prec + rec > 0, 2 * prec * rec / (prec + rec), 0.0)
        den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        mcc = np.where(den > 0, (tp * tn - fp * fn) / den, 0.0)
        p1 = 0.01
        prec1 = np.where(rec * p1 + fpr * (1 - p1) > 0, rec * p1 / (rec * p1 + fpr * (1 - p1)), np.nan)
    return dict(accuracy=(tp + tn) / (P + N), precision=prec, recall=rec, f1=f1, fpr=fpr, specificity=1 - fpr,
                balanced_acc=(rec + 1 - fpr) / 2, mcc=mcc, prevalence=P / (P + N), precision_at_prev1=prec1)


def per_type(df, n_bte):
    out = []
    for tag in ("1", "01"):
        d = df.copy()
        d["op"] = "1%" if tag == "1" else "0.1%"
        d["TP"] = np.round(d[f"recall{tag}"] * d["n"]).astype(int)
        d["FN"] = d["n"] - d["TP"]
        d["FP"] = np.round(d[f"fpr_test{tag}"] * n_bte).astype(int)
        d["TN"] = n_bte - d["FP"]
        for k, v in scores(d.TP, d.FN, d.FP, d.TN).items():
            d[k] = v
        out.append(d)
    return pd.concat(out, ignore_index=True)


def overall(pt):
    rows = []
    keys = ["protocol", "scenario", "op", "seed", "model"]
    for key, g in pt.groupby(keys):
        tasks = g.groupby("held")
        fp = np.mean([t.FP.iloc[0] for _, t in tasks])                   # one benign test set per task (model)
        n_bte = int(g.FP.iloc[0] + g.TN.iloc[0])
        tp, fn = g.TP.sum(), g.FN.sum()
        r = dict(zip(keys, key), TP=int(tp), FN=int(fn), FP=float(fp), TN=float(n_bte - fp))
        r.update({k: float(v) for k, v in scores(tp, fn, fp, n_bte - fp).items()})
        r["macro_recall"] = g.recall.mean()                               # = the primary metric of the paper
        nt = g[~g.tiny.astype(bool)]
        r["macro_recall_nontiny"] = nt.recall.mean() if len(nt) else np.nan
        w = g.n.astype(float)
        r["auc"] = float(np.average(g.auc, weights=w)) if g.auc.notna().all() else np.nan
        r["pauc1"] = float(np.average(g.pauc1, weights=w)) if "pauc1" in g and g.pauc1.notna().all() else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


def report(ov, pt, out_dir, plots, say):
    cols = ["macro_recall", "recall", "precision", "f1", "mcc", "accuracy", "balanced_acc", "fpr", "auc", "pauc1",
            "precision_at_prev1"]
    order = sorted(ov.groupby(["protocol", "scenario", "op"]).groups,
                   key=lambda k: (k[0] != "within", k[1] != "known", k[2] != "1%"))     # easy -> hardest, 1% first
    for proto, scen, op in order:
        g = ov[(ov.protocol == proto) & (ov.scenario == scen) & (ov.op == op)]
        level = {("within", "known"): "EASY", ("within", "loo"): "MEDIUM", ("cross", "known"): "HARD",
                 ("cross", "loo"): "HARDEST"}.get((proto, scen), "")
        say(f"\n==== {level} ({proto}, {scen}), operating point {op} false alarms on the local calibration benign")
        say(f"evaluation set per task: {int(g.TN.iloc[0] + g.FP.iloc[0])} test benign flows + attack flows; "
            f"attack share (prevalence) {g.prevalence.mean():.3f} -> accuracy / precision / F1 depend on it")
        m = g.groupby("model")[cols].agg(["mean", "std"])
        tab = pd.DataFrame({c: m[c]["mean"].map("{:.3f}".format) + " (" + m[c]["std"].map("{:.3f}".format) + ")"
                            for c in cols})
        say("mean (sd) over seeds; macro_recall = mean recall over attack types (primary metric), recall = pooled "
            "over all attack flows:\n" + tab.sort_values("macro_recall", ascending=False).to_string())
        say("\nconfusion matrix, mean over seeds  [rows: true benign / true attack; columns: no alarm / alarm]")
        cm = g.groupby("model")[["TN", "FP", "FN", "TP"]].mean()
        for mod, r in cm.iterrows():
            nb, na = r.TN + r.FP, r.FN + r.TP
            say(f"  {mod:13s} benign [{r.TN:10.0f} {r.FP:8.0f}]  ({r.TN / nb:6.1%} / {r.FP / nb:5.1%})\n"
                f"  {'':13s} attack [{r.FN:10.0f} {r.TP:8.0f}]  ({r.FN / na:6.1%} / {r.TP / na:5.1%})")
        p = pt[(pt.protocol == proto) & (pt.scenario == scen) & (pt.op == op)]
        say("\nper attack type: share of its flows that raised an alarm (recall), mean over seeds. (No per-type F1: a\n"
            "binary detector does not assign false alarms to a type; per-family F1 comes from the family stage.)")
        say(p.groupby(["type", "model"]).recall.mean().unstack().round(3).to_string())
        if plots:
            plot_cm(cm, f"{level or proto + '-' + scen} level, {op} false alarms", os.path.join(
                out_dir, f"confusion_{proto}_{scen}_{op.replace('%', 'pct').replace('.', '')}"))


def plot_cm(cm, title, path):
    try:
        import matplotlib
    except ImportError:
        print("  (figures skipped: matplotlib is not installed -> pip install matplotlib)")
        return False
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    k = len(cm)
    fig, axes = plt.subplots(1, k, figsize=(2.6 * k, 2.9), squeeze=False)
    for ax, (mod, r) in zip(axes[0], cm.iterrows()):
        M = np.array([[r.TN, r.FP], [r.FN, r.TP]], float)
        R = M / M.sum(1, keepdims=True)
        ax.imshow(R, cmap="Blues", vmin=0, vmax=1)
        for a in range(2):
            for b in range(2):
                ax.text(b, a, f"{R[a, b]:.1%}\n({M[a, b]:,.0f})", ha="center", va="center", fontsize=8,
                        color="white" if R[a, b] > 0.6 else "black")
        ax.set_xticks([0, 1], ["no alarm", "alarm"], fontsize=8)
        ax.set_yticks([0, 1], ["benign", "attack"], fontsize=8)
        ax.set_title(mod, fontsize=9)
    fig.suptitle(f"Confusion matrix (row-normalised, mean over seeds) - {title}", fontsize=9)
    fig.tight_layout()
    fig.savefig(path + ".png", dpi=600)
    fig.savefig(path + ".pdf")
    plt.close(fig)
    print(f"  figure saved: {path}.png / .pdf")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", nargs="+", required=True, help="one or more v3_results.csv files")
    ap.add_argument("--n_bte", type=int, nargs="*", help="size of the test benign third, one per results file")
    ap.add_argument("--plots", action="store_true", help="also save confusion-matrix figures (png 600 dpi + pdf)")
    a = ap.parse_args()
    for fi, path in enumerate(a.results):
        df = pd.read_csv(path)
        if "tiny" not in df:
            df["tiny"] = df.n < TINY
        if "pauc1" not in df:
            df["pauc1"] = np.nan
        n_bte = a.n_bte[fi] if a.n_bte else infer_n_bte(df)
        out_dir = os.path.dirname(os.path.abspath(path))
        lines = []
        def say(s):
            print(s)
            lines.append(s)
        say(f"##### {path}\ntest benign third: {n_bte} flows ({'given' if a.n_bte else 'inferred from the stored rates'})")
        pt = per_type(df, n_bte)
        ov = overall(pt)
        pt.to_csv(os.path.join(out_dir, "metrics_per_type.csv"), index=False)
        ov.to_csv(os.path.join(out_dir, "metrics_overall.csv"), index=False)
        report(ov, pt, out_dir, a.plots, say)
        open(os.path.join(out_dir, "metrics_report.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        say(f"\nsaved -> metrics_overall.csv, metrics_per_type.csv, metrics_report.txt"
            f" in {out_dir}")


if __name__ == "__main__":
    main()
