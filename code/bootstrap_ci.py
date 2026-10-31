"""
95% bootstrap confidence intervals for the paper: every model's mean score per evaluation level (ladder figure) and
every paired difference between models (the tests of the reports). Works on files that already exist; no model is
trained again.

Inputs (one --run per level, repeatable):  LABEL=PATH@SCENARIO
  PATH      v3_results.csv of hybrid_v3 / dump_scores (metrics recall1, recall01, auc, pauc1)
            or matched_fpr_per_type.csv of analyze_scores (metrics recall_at1, recall_at01, pr_auc, recall_B)
  SCENARIO  known | loo   (rows of that scenario are used)

Uncertainty has TWO sources and both are resampled (two-way bootstrap, the primary interval):
  seeds (training subsample, initialisation)  x  evaluation units (attack type, or held-out family + type in loo).
For a model mean: matrix M[seed, unit] of scores; for a difference A - B: M = A - B on the same (seed, unit) cells,
i.e. PAIRED. Each replicate draws seeds and units with replacement and takes the mean of the sub-matrix.
Also reported: seed-only and unit-only intervals (to show which source dominates) and the share of replicates <= 0.
Percentile intervals, B = 10,000 replicates, fixed random seed (reproducible).

  python bootstrap_ci.py --out_dir "D:/revised model/ci" ^
     --run "easy=D:/revised model/scores_within/v3_results.csv@known" ^
     --run "medium=D:/revised model/v33_within10/v3_results.csv@loo" ^
     --run "hard=D:/revised model/v33_cross10/v3_results.csv@known" ^
     --run "hardest=D:/revised model/v33_cross10/v3_results.csv@loo" ^
     --run "unsw_known=D:/revised model/unsw_primary/v3_results.csv@known" ^
     --run "unsw_loo=D:/revised model/unsw_primary/v3_results.csv@loo"
  python bootstrap_ci.py --selftest
Outputs: ci_models.csv, ci_pairs.csv, ci_report.txt in --out_dir (ci_models.csv feeds make_figures.py).
"""
import argparse, os
import numpy as np
import pandas as pd

DEFAULT_PAIRS = ("V3-SUP>TREE,V3-MAX>V3-SUP,V3-MAX>TREE,V3-MAX>V3-MAX-RBF,V3-SUP>V3-SUP-DENSE,V3-SUP>V3-SUP-NOA,"
                 "V3-SUP>V3-SUP-NOALIGN,V3-SUP>V3-SUP-SHUF,V3-SUP>V3-SUP-NOW")
METRICS = ("recall1", "recall01", "pauc1", "auc", "recall_at1", "recall_at01", "pr_auc", "recall_B")


def matrix(df, model, metric):
    """seed x unit table of one model (unit = held + type)"""
    d = df[df.model == model]
    if d.empty or metric not in d.columns:
        return None
    d = d.assign(unit=d["held"].astype(str) + "|" + d["type"].astype(str))
    return d.pivot_table(index="seed", columns="unit", values=metric, aggfunc="mean")


def boot(M, B, rng):
    """two-way, seed-only and unit-only bootstrap replicates of the mean of matrix M (NaN cells ignored)"""
    A = M.values.astype(float)
    ns, nu = A.shape
    si = rng.integers(0, ns, (B, ns))
    ui = rng.integers(0, nu, (B, nu))
    two = np.array([np.nanmean(A[np.ix_(si[b], ui[b])]) for b in range(B)])
    seed_only = np.array([np.nanmean(A[si[b]]) for b in range(B)])
    unit_only = np.array([np.nanmean(A[:, ui[b]]) for b in range(B)])
    return two, seed_only, unit_only


def ci(x):
    return np.nanpercentile(x, 2.5), np.nanpercentile(x, 97.5)


def analyse(runs, pairs, metrics, B, seed, tiny):
    rng = np.random.default_rng(seed)
    mod_rows, pair_rows = [], []
    for label, df in runs:
        if tiny == "exclude" and "tiny" in df.columns:
            df = df[~df.tiny.astype(bool)]
        mets = [m for m in metrics if m in df.columns]
        models = list(pd.unique(df.model))
        for met in mets:
            for mdl in models:
                M = matrix(df, mdl, met)
                if M is None or M.size == 0:
                    continue
                two, so, uo = boot(M, B, rng)
                lo, hi = ci(two)
                mod_rows.append(dict(level=label, metric=met, model=mdl, mean=float(np.nanmean(M.values)),
                                     lo=lo, hi=hi, lo_seed=ci(so)[0], hi_seed=ci(so)[1], lo_unit=ci(uo)[0],
                                     hi_unit=ci(uo)[1], n_seeds=M.shape[0], n_units=M.shape[1]))
            for a, b in pairs:
                MA, MB = matrix(df, a, met), matrix(df, b, met)
                if MA is None or MB is None:
                    continue
                MB = MB.reindex(index=MA.index, columns=MA.columns)
                D = MA - MB
                D = D.loc[D.notna().any(axis=1), D.notna().any(axis=0)]
                if D.size == 0:
                    continue
                two, so, uo = boot(D, B, rng)
                lo, hi = ci(two)
                pair_rows.append(dict(level=label, metric=met, pair=f"{a} - {b}", diff=float(np.nanmean(D.values)),
                                      lo=lo, hi=hi, lo_seed=ci(so)[0], hi_seed=ci(so)[1], lo_unit=ci(uo)[0],
                                      hi_unit=ci(uo)[1], share_le0=float(np.mean(two <= 0)),
                                      excludes_0=bool(lo > 0 or hi < 0), n_seeds=D.shape[0], n_units=D.shape[1]))
    return pd.DataFrame(mod_rows), pd.DataFrame(pair_rows)


def read_run(spec):
    if "=" not in spec or "@" not in spec:
        raise SystemExit(f"--run must look like LABEL=PATH@SCENARIO, got: {spec}")
    label, rest = spec.split("=", 1)
    path, scen = rest.rsplit("@", 1)
    df = pd.read_csv(path)
    if "scenario" in df.columns:
        df = df[df.scenario == scen]
    if df.empty:
        raise SystemExit(f"{path}: no rows for scenario '{scen}'")
    if "held" not in df.columns:
        df["held"] = "-"
    return label.strip(), df


def write(models, pairs_df, out_dir, B, tiny):
    os.makedirs(out_dir, exist_ok=True)
    models.to_csv(os.path.join(out_dir, "ci_models.csv"), index=False)
    pairs_df.to_csv(os.path.join(out_dir, "ci_pairs.csv"), index=False)
    L = [f"95% bootstrap intervals (two-way: seeds x attack types, B = {B}; tiny types {tiny}).",
         "[lo, hi] = two-way (primary); seed-only and type-only intervals in the CSV files.", ""]
    f = lambda v: f"{v:.3f}"
    for (lvl, met), g in models.groupby(["level", "metric"], sort=False):
        L.append(f"== {lvl} | {met}: model means")
        for _, r in g.sort_values("mean", ascending=False).iterrows():
            L.append(f"   {r.model:14s} {f(r['mean'])}  [{f(r.lo)}, {f(r.hi)}]  ({r.n_seeds} seeds x {r.n_units} types)")
        p = pairs_df[(pairs_df.level == lvl) & (pairs_df.metric == met)] if len(pairs_df) else pairs_df
        for _, r in p.iterrows():
            L.append(f"   diff {r.pair:24s} {r['diff']:+.3f}  [{r.lo:+.3f}, {r.hi:+.3f}]  "
                     f"{'excludes 0' if r.excludes_0 else 'includes 0'}  (seed-only [{r.lo_seed:+.3f}, {r.hi_seed:+.3f}],"
                     f" type-only [{r.lo_unit:+.3f}, {r.hi_unit:+.3f}])")
        L.append("")
    txt = "\n".join(L)
    open(os.path.join(out_dir, "ci_report.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)
    print(f"saved -> {out_dir}/ci_models.csv, ci_pairs.csv, ci_report.txt")


def selftest():
    """synthetic results with known structure: A = B + 0.05 everywhere -> diff CI must contain 0.05 and exclude 0;
    a pure-noise pair must include 0; model mean CI must contain the true mean"""
    rng = np.random.default_rng(1)
    rows = []
    for s in range(10):
        se = rng.normal(0, 0.08)                       # shared seed effect (threshold cliff)
        for t in range(9):
            te = rng.normal(0.3, 0.15)
            base = te + se + rng.normal(0, 0.02)
            rows += [dict(scenario="known", held="-", seed=s, type=f"t{t}", model="B", recall1=base),
                     dict(scenario="known", held="-", seed=s, type=f"t{t}", model="A", recall1=base + 0.05),
                     dict(scenario="known", held="-", seed=s, type=f"t{t}", model="N", recall1=base + rng.normal(0, .03))]
    df = pd.DataFrame(rows)
    m, p = analyse([("syn", df)], [("A", "B"), ("N", "B")], ["recall1"], 2000, 0, "keep")
    ab = p[p.pair == "A - B"].iloc[0]
    nb = p[p.pair == "N - B"].iloc[0]
    ok1 = ab.lo <= 0.05 <= ab.hi and ab.excludes_0
    ok2 = nb.lo <= 0 <= nb.hi
    mb = m[m.model == "B"].iloc[0]
    ok3 = mb.lo < df[df.model == "B"].recall1.mean() < mb.hi
    print(f"{'PASS' if ok1 else 'FAIL'} constant +0.05 difference: {ab['diff']:+.3f} [{ab.lo:+.3f}, {ab.hi:+.3f}]")
    print(f"{'PASS' if ok2 else 'FAIL'} noise difference includes 0: {nb['diff']:+.3f} [{nb.lo:+.3f}, {nb.hi:+.3f}]")
    print(f"{'PASS' if ok3 else 'FAIL'} model mean inside its interval: {mb['mean']:.3f} [{mb.lo:.3f}, {mb.hi:.3f}]")
    print("ALL PASS" if ok1 and ok2 and ok3 else "SOME CHECKS FAILED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", default=[], help="LABEL=PATH@SCENARIO (repeat)")
    ap.add_argument("--pairs", default=DEFAULT_PAIRS, help="comma list A>B; pairs whose models are missing are skipped")
    ap.add_argument("--metrics", default=",".join(METRICS))
    ap.add_argument("--B", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tiny", choices=["keep", "exclude"], default="keep",
                    help="keep = all attack types (the primary metric); exclude = types with < 50 flows removed")
    ap.add_argument("--out_dir", default="ci_out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.run:
        raise SystemExit("give at least one --run LABEL=PATH@SCENARIO (see the header of this file)")
    runs = [read_run(s) for s in a.run]
    pairs = [tuple(x.strip() for x in p.split(">")) for p in a.pairs.split(",") if ">" in p]
    models, pairs_df = analyse(runs, pairs, [m.strip() for m in a.metrics.split(",")], a.B, a.seed, a.tiny)
    write(models, pairs_df, a.out_dir, a.B, a.tiny)


if __name__ == "__main__":
    main()
