"""
Recall of the main CIC-UNSW-NB15 run (ten seeds) WITHOUT the Reconnaissance type (descriptive, post-hoc).
Reads only an existing results file; nothing is trained and the confirmatory test is not re-run.
  macro recall at nominal FPR 1% (threshold B) = mean over the attack types, per seed; types listed in --drop are left out.
  For each scenario (known = all types, loo = held-out types) the script prints, per model, mean +- sd over seeds,
  the paired difference V3-MAX - V3-SUP with the number of seeds in which V3-MAX is higher and the one-sided
  seed-level Wilcoxon p, and the share of the macro gain (V3-MAX - V3-SUP) that comes from the dropped type(s).
  In the held-out scenario only two types are evaluated (DoS and Reconnaissance); without Reconnaissance a single type
  remains, so that number is a single-type result and is labelled as such.

  python no_recon.py --selftest
  python no_recon.py --csv "D:/revised model/unsw_primary/v3_results.csv" --out_dir "D:/revised model/no_recon"
"""
import argparse, os
import numpy as np
import pandas as pd

MODELS = ["TREE", "V3-SUP", "V3-MAX", "V3-MAX-RBF"]


def per_seed(df, scen, model, drop):
    s = df[(df.scenario == scen) & (df.model == model)]
    s = s[~s.type.astype(str).str.contains("|".join(drop), case=False)] if drop else s
    return s.groupby(["seed", "type"]).recall1.mean().groupby("seed").mean()


def analyse(df, drop=("Recon",)):
    from scipy.stats import wilcoxon
    L, rows = [], []
    L.append("RECALL AT NOMINAL FPR 1% WITH AND WITHOUT " + "/".join(drop).upper() + " (descriptive, post-hoc)")
    for scen, label in (("known", "all types"), ("loo", "held-out types")):
        d = df[df.scenario == scen]
        if d.empty:
            continue
        types_all = sorted(d.type.astype(str).unique())
        types_kept = [t for t in types_all if not any(x.lower() in t.lower() for x in drop)]
        L.append(f"\n==== scenario {scen} ({label}); types: {len(types_all)} -> {len(types_kept)} after dropping")
        if len(types_kept) == 1:
            L.append(f"  NOTE: only one type remains ({types_kept[0]}); this is a single-type result.")
        res = {}
        for m in MODELS:
            full, part = per_seed(df, scen, m, ()), per_seed(df, scen, m, drop)
            if full.empty:
                continue
            res[m] = (full, part)
            rows.append(dict(scenario=scen, model=m, R_all=full.mean(), sd_all=full.std(), R_without=part.mean(),
                             sd_without=part.std(), seeds=len(part)))
        L.append(pd.DataFrame(rows)[lambda t: t.scenario == scen].drop(columns="scenario").round(4).to_string(index=False))
        if "V3-MAX" in res and "V3-SUP" in res:
            for nm, k in (("all types", 0), ("without dropped type(s)", 1)):
                diff = (res["V3-MAX"][k] - res["V3-SUP"][k]).dropna()
                p = wilcoxon(diff, alternative="greater").pvalue if (diff != 0).sum() >= 3 else float("nan")
                L.append(f"  V3-MAX - V3-SUP, {nm}: {diff.mean():+.3f}; seeds with V3-MAX higher: {(diff > 0).sum()}/{len(diff)}; "
                         f"one-sided p {p:.4f}")
            g_all = (res["V3-MAX"][0] - res["V3-SUP"][0]).mean()
            g_part = (res["V3-MAX"][1] - res["V3-SUP"][1]).mean()
            n_all, n_kept = len(types_all), len(types_kept)
            if g_all > 0 and n_all > 0:
                dropped_contrib = (g_all * n_all - g_part * n_kept) / (g_all * n_all)
                L.append(f"  share of the macro gain (V3-MAX - V3-SUP) contributed by the dropped type(s): {dropped_contrib:.0%}")
        if "V3-MAX" in res and "V3-MAX-RBF" in res:
            diff = (res["V3-MAX"][1] - res["V3-MAX-RBF"][1]).dropna()
            L.append(f"  without dropped type(s): IQP - RBF = {diff.mean():+.3f}; seeds with IQP higher: {(diff > 0).sum()}/{len(diff)}")
        pt = d[d.model.isin(["V3-SUP", "V3-MAX"])].groupby(["type", "model"]).recall1.mean().unstack().round(3)
        L.append("  per type (mean over seeds):\n" + "\n".join("    " + x for x in pt.to_string().split("\n")))
    return "\n".join(L), pd.DataFrame(rows)


def selftest():
    r = np.random.default_rng(0)
    rows = []
    for sc, types in (("known", ["Fuzzers", "Generic", "Reconnaissance", "Exploits"]), ("loo", ["DoS", "Reconnaissance"])):
        for sd in range(10):
            for m, base in (("TREE", .02), ("V3-SUP", .01), ("V3-MAX", .1), ("V3-MAX-RBF", .1)):
                for t in types:
                    v = base + (0.6 if (t == "Reconnaissance" and m.startswith("V3-MAX")) else 0) + r.normal(0, .005)
                    rows.append(dict(scenario=sc, seed=sd, model=m, type=t, recall1=v))
    df = pd.DataFrame(rows)
    txt, t = analyse(df)
    ok = True
    def chk(n, c):
        nonlocal ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + n)
    k = t[(t.scenario == "known") & (t.model == "V3-MAX")].iloc[0]
    chk("known: with Recon macro ~ (0.1*3+0.7)/4 = 0.25", abs(k.R_all - 0.25) < 0.01)
    chk("known: without Recon macro ~ 0.1", abs(k.R_without - 0.10) < 0.01)
    chk("share of gain from the dropped type is large (~72%)", "72%" in txt or "71%" in txt or "73%" in txt)
    chk("loo: single-type note printed", "single-type result" in txt)
    chk("seeds counted as 10/10", "10/10" in txt)
    print("ALL PASS" if ok else "SOME CHECKS FAILED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="D:/revised model/unsw_primary/v3_results.csv")
    ap.add_argument("--out_dir", default="no_recon_out")
    ap.add_argument("--drop", default="Recon")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    df = pd.read_csv(a.csv)
    txt, t = analyse(df, tuple(x.strip() for x in a.drop.split(",") if x.strip()))
    os.makedirs(a.out_dir, exist_ok=True)
    open(os.path.join(a.out_dir, "no_recon_report.txt"), "w", encoding="utf-8").write(txt + "\n")
    t.to_csv(os.path.join(a.out_dir, "no_recon_table.csv"), index=False)
    print(txt)


if __name__ == "__main__":
    main()
