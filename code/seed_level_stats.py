"""
Seed-level inference for the paper (Section 3.6 after the second review) + size of the HistGradientBoosting tree.
Works on files that already exist; no neural model is trained and the confirmatory test is NOT re-run.

PART A - paired tests with the SEED as the unit of inference
  For every level (--run) and every pair A>B, for each seed the macro-averaged difference A - B over the evaluation
  units (unit = held-out task + attack type, as in bootstrap_ci.py) is computed, and a one-sided Wilcoxon signed-rank
  test is applied to these seed-level differences (inference). The pre-specified test over seed x type cells is
  reported next to it as DESCRIPTIVE, and every pair where the two forms reach a different decision at 0.05 is flagged.
  Non-inferiority pairs A>=B (margin m = 0.02): seed-level Wilcoxon of (A - B + m) > 0, plus the pre-specified point
  rule (mean A - B >= -m).
  If --ci points to ci_pairs.csv of bootstrap_ci.py, its two-way interval is joined (stable = interval excludes 0).

PART B - Holm over the confirmatory family on CIC-UNSW-NB15 (metric recall1 = recall at threshold B, all 9 types)
  U1 known V3-SUP > TREE | U2 known V3-SUP >= V3-SUP-DENSE - 0.02 | U3 known and loo V3-MAX > V3-SUP |
  U3q known and loo V3-MAX > V3-MAX-RBF | U4 known V3-SUP-NOA >= V3-SUP - 0.02 | U5 loo V3-SUP > TREE
  Holm-adjusted seed-level p-values (8 tests). The pre-specified decisions are printed next to them.

PART C - size of the tree of branch T (and of TREE), refitted exactly as hybrid_v3.run does for the 'known' task:
  i = 30,000-flow stratified subsample (seed), k = 100,000-flow subsample of the rest (seed + 100),
  HistGradientBoostingClassifier(max_iter=200, random_state=seed). Reports trees built, nodes, leaves, depth,
  expected node comparisons per flow, pickled size. hybrid_v3.py is only read, never changed.

Run (PowerShell, from D:/revised model; the backtick ` continues a line):
  python seed_level_stats.py --selftest
  python seed_level_stats.py --out_dir "D:/revised model/seed_stats" `
     --run "easy=D:/revised model/scores_within/v3_results.csv@known" `
     --run "easy_controls_3seeds=D:/revised model/v31_within/v3_results.csv@known" `
     --run "medium=D:/revised model/v33_within10/v3_results.csv@loo" `
     --run "hard=D:/revised model/v33_cross10/v3_results.csv@known" `
     --run "hardest=D:/revised model/v33_cross10/v3_results.csv@loo" `
     --run "hard_ablation=D:/revised model/v31_ablation10/v3_results.csv@known" `
     --run "unsw_known=D:/revised model/unsw_primary/v3_results.csv@known" `
     --run "unsw_loo=D:/revised model/unsw_primary/v3_results.csv@loo" `
     --run "hard_matched=D:/revised model/scores_cross/matched_fpr_per_type.csv@known" `
     --run "hardest_matched=D:/revised model/scores_cross/matched_fpr_per_type.csv@loo" `
     --run "unsw_known_matched=D:/revised model/unsw_primary/matched_fpr_per_type.csv@known" `
     --run "unsw_loo_matched=D:/revised model/unsw_primary/matched_fpr_per_type.csv@loo" `
     --confirm "unsw_known,unsw_loo" `
     --ci "D:/revised model/ci/ci_pairs.csv" `
     --tree --s17_dir "D:/revised model/stage1_pw"
  The labels easy / medium / hard / hardest / unsw_known / unsw_loo are those of the earlier bootstrap_ci.py run, so
  its intervals are joined. A --run whose file does not exist is skipped with a warning.
Outputs in --out_dir: seed_tests.csv, holm_confirmatory.csv, tree_size.csv, seed_stats_report.txt
"""
import argparse, io, json, os, pickle, time
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

DEFAULT_PAIRS = ("V3-SUP>TREE,V3-MAX>V3-SUP,V3-MAX>TREE,V3-MAX>V3-MAX-RBF,V3-SUP>V3-SUP-DENSE,V3-SUP>V3-SUP-NOA,"
                 "V3-SUP>V3-SUP-NOALIGN,V3-SUP>V3-SUP-SHUF,V3-SUP>V3-SUP-NOW,V3-SUP-TT>V3-SUP-LR")
DEFAULT_NI = "V3-SUP>=V3-SUP-DENSE,V3-SUP-NOA>=V3-SUP,V3-SUP-TT>=V3-SUP"
METRICS = ("recall1", "recall01", "pauc1", "auc", "recall_at1", "recall_at01", "pr_auc", "recall_B")
REPORT_METRICS = ("recall1", "recall_at1", "pauc1", "pr_auc")
ALPHA = 0.05
# the confirmatory family of the analysis plan (prereg_unsw 2026-10-25 19:18); 'k' / 'l' = known / loo run label
FAMILY = [("U1", "k", "sup", "V3-SUP", "TREE"),
          ("U2", "k", "ni", "V3-SUP", "V3-SUP-DENSE"),
          ("U3 known", "k", "sup", "V3-MAX", "V3-SUP"),
          ("U3 loo", "l", "sup", "V3-MAX", "V3-SUP"),
          ("U3 quantum known", "k", "sup", "V3-MAX", "V3-MAX-RBF"),
          ("U3 quantum loo", "l", "sup", "V3-MAX", "V3-MAX-RBF"),
          ("U4", "k", "ni", "V3-SUP-NOA", "V3-SUP"),
          ("U5", "l", "sup", "V3-SUP", "TREE")]


# ============================================================================ helpers
def read_run(spec):
    if "=" not in spec or "@" not in spec:
        raise SystemExit(f"--run must look like LABEL=PATH@SCENARIO, got: {spec}")
    label, rest = spec.split("=", 1)
    path, scen = rest.rsplit("@", 1)
    if not os.path.exists(path):
        print(f"WARNING: {path} not found -> run '{label.strip()}' skipped")
        return None
    df = pd.read_csv(path)
    if "scenario" in df.columns:
        df = df[df.scenario == scen]
    if df.empty:
        print(f"WARNING: {path}: no rows for scenario '{scen}' -> run '{label.strip()}' skipped")
        return None
    if "held" not in df.columns:
        df["held"] = "-"
    df["held"] = df["held"].fillna("-").astype(str)
    if "tiny" not in df.columns:
        df["tiny"] = False
    df["tiny"] = df["tiny"].astype(str).str.lower().isin(["true", "1", "yes"])
    return label.strip(), df


def wil(x):
    """one-sided Wilcoxon signed-rank p-value for median(x) > 0; NaN when fewer than 3 non-zero values"""
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    if (x != 0).sum() < 3:
        return np.nan
    return float(wilcoxon(x, alternative="greater").pvalue)


def cells(df, a, b, metric):
    """paired differences A - B on the common (seed, held, type) cells"""
    if metric not in df.columns:
        return None
    A = df[df.model == a].set_index(["seed", "held", "type"])[metric]
    B = df[df.model == b].set_index(["seed", "held", "type"])[metric]
    if A.empty or B.empty:
        return None
    A = A[~A.index.duplicated()]
    B = B[~B.index.duplicated()]
    d = (A - B.reindex(A.index)).dropna()
    return d if len(d) else None


def holm(p):
    """Holm step-down adjusted p-values (NaN kept as NaN, excluded from the family size)"""
    p = np.asarray(p, float)
    out = np.full(len(p), np.nan)
    ok = np.where(~np.isnan(p))[0]
    m = len(ok)
    if m == 0:
        return out
    order = ok[np.argsort(p[ok])]
    run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (m - r) * p[i]))
        out[i] = run
    return out


def test_pair(df, a, b, metric, kind, margin):
    d = cells(df, a, b, metric)
    if d is None:
        return None
    ds = d.groupby(level="seed").mean()
    shift = margin if kind == "ni" else 0.0
    r = dict(kind="non-inferiority" if kind == "ni" else "superiority", metric=metric, A=a, B=b,
             margin=margin if kind == "ni" else np.nan, n_seeds=int(ds.size), n_cells=int(d.size),
             mean_diff=float(d.mean()), seed_min=float(ds.min()), seed_max=float(ds.max()),
             seed_wins=int((ds + shift > 0).sum()),
             p_seed=wil(ds.values + shift), p_cell_descriptive=wil(d.values + shift))
    r["seed_decision"] = bool(r["p_seed"] < ALPHA) if not np.isnan(r["p_seed"]) else False
    r["cell_decision"] = bool(r["p_cell_descriptive"] < ALPHA) if not np.isnan(r["p_cell_descriptive"]) else False
    r["forms_disagree"] = r["seed_decision"] != r["cell_decision"]
    if kind == "ni":
        r["point_rule_met"] = bool(r["mean_diff"] >= -margin)        # the pre-specified rule of the plan
    return r


# ============================================================================ part A + B
def part_ab(runs, pairs, ni_pairs, metrics, margin, tiny_modes, ci_path, confirm):
    rows = []
    for label, df in runs:
        for tm in tiny_modes:
            g = df if tm == "all types" else df[~df.tiny]
            if g.empty:
                continue
            for met in [m for m in metrics if m in g.columns]:
                for kind, plist in (("sup", pairs), ("ni", ni_pairs)):
                    for a, b in plist:
                        r = test_pair(g, a, b, met, kind, margin)
                        if r is not None:
                            rows.append(dict(level=label, types=tm, **r))
    tests = pd.DataFrame(rows)
    if ci_path and len(tests):
        ci = pd.read_csv(ci_path)
        ci = ci.rename(columns={"level": "level", "metric": "metric"})
        ci["A"] = ci["pair"].str.split(" - ").str[0].str.strip()
        ci["B"] = ci["pair"].str.split(" - ").str[1].str.strip()
        ci = ci[["level", "metric", "A", "B", "lo", "hi", "excludes_0"]].rename(
            columns={"lo": "ci_lo", "hi": "ci_hi", "excludes_0": "ci_excludes_0"})
        tests = tests.merge(ci, on=["level", "metric", "A", "B"], how="left")
        tests.loc[tests.types != "all types", ["ci_lo", "ci_hi", "ci_excludes_0"]] = np.nan   # CIs were for all types
    holm_df = pd.DataFrame()
    if confirm:
        lk, ll = [s.strip() for s in confirm.split(",")]
        lab = {"k": lk, "l": ll}
        rows = []
        for name, which, kind, a, b in FAMILY:
            hit = dict(runs).get(lab[which])
            r = test_pair(hit, a, b, "recall1", kind, margin) if hit is not None else None
            if r is None:
                rows.append(dict(hypothesis=name, level=lab[which], A=a, B=b, kind=kind, missing=True))
                continue
            pre = (r["point_rule_met"] if kind == "ni" else r["cell_decision"])
            rows.append(dict(hypothesis=name, level=lab[which], A=a, B=b, kind=r["kind"], mean_diff=r["mean_diff"],
                             seed_wins=r["seed_wins"], n_seeds=r["n_seeds"], p_seed=r["p_seed"],
                             p_cell_descriptive=r["p_cell_descriptive"],
                             pre_specified_decision=("met" if pre else "not met"), missing=False))
        holm_df = pd.DataFrame(rows)
        if "p_seed" in holm_df.columns:
            holm_df["p_seed_holm"] = holm(holm_df["p_seed"].values)
            holm_df["seed_level_decision"] = np.where(holm_df["p_seed"] < ALPHA, "met", "not met")
            holm_df["holm_decision"] = np.where(holm_df["p_seed_holm"] < ALPHA, "met", "not met")
            holm_df.loc[holm_df.p_seed.isna(), ["seed_level_decision", "holm_decision"]] = "n/a"
    return tests, holm_df


# ============================================================================ part C
def sub_idx_local(y, n, seed):
    """identical copy of hybrid_v2.sub_idx (used only if hybrid_v2 cannot be imported)"""
    from sklearn.model_selection import train_test_split
    if n is None or n <= 0 or n >= len(y):
        return np.arange(len(y))
    try:
        idx, _ = train_test_split(np.arange(len(y)), train_size=n, stratify=y, random_state=seed)
    except ValueError:
        idx = np.random.default_rng(seed).choice(len(y), n, replace=False)
    return np.sort(idx)


def tree_size(s17_dir, seeds, max_train=30000, tree_train=100000, say=print):
    from sklearn.ensemble import HistGradientBoostingClassifier
    try:
        import hybrid_v2 as H
        sub_idx, src = H.sub_idx, "hybrid_v2.sub_idx"
    except Exception as e:                                     # torch missing etc.
        sub_idx, src = sub_idx_local, f"local copy ({type(e).__name__})"
    feats = json.load(open(os.path.join(s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    fidx = np.array([feats.index(c) for c in flow])
    z = np.load(os.path.join(s17_dir, "splits.npz"), allow_pickle=True)
    X = z["Xtr"][:, fidx].astype("float32")
    y = z["ytr"].astype(int)
    say(f"tree refit: {len(flow)} flow features, {len(y):,} training flows, subsample function = {src}")
    rows = []
    for seed in seeds:
        pool = np.arange(len(y))                                # 'known' task: nothing held out
        i = pool[sub_idx(y[pool], max_train, seed)]
        rest = np.setdiff1d(pool, i)
        k = rest[sub_idx(y[rest], tree_train, seed + 100)]
        t0 = time.time()
        tree = HistGradientBoostingClassifier(max_iter=200, random_state=seed).fit(X[k], y[k])
        fit_s = time.time() - t0
        r = dict(seed=seed, n_train=int(len(k)), attack_share=float(y[k].mean()), trees_built=int(tree.n_iter_),
                 early_stopping=str(tree.early_stopping), max_leaf_nodes=int(tree.max_leaf_nodes), fit_seconds=fit_s)
        try:
            preds = [p for it in tree._predictors for p in it]
            nodes = [p.nodes for p in preds]
            r["nodes_total"] = int(sum(len(n) for n in nodes))
            r["leaves_total"] = int(sum(int(n["is_leaf"].sum()) for n in nodes))
            r["max_depth"] = int(max(int(n["depth"].max()) for n in nodes))
            # expected comparisons per flow = sum over trees of the leaf depth, weighted by training counts
            exp_cmp = 0.0
            for n in nodes:
                lf = n[n["is_leaf"].astype(bool)]
                w = lf["count"].astype(float)
                exp_cmp += float((w * lf["depth"]).sum() / max(w.sum(), 1.0))
            r["expected_comparisons_per_flow"] = exp_cmp
        except Exception as e:
            r["node_stats_error"] = f"{type(e).__name__}: {e}"
        buf = io.BytesIO()
        pickle.dump(tree, buf, protocol=pickle.HIGHEST_PROTOCOL)
        r["pickled_bytes"] = buf.tell()
        rows.append(r)
        say(f"  seed {seed}: {r['trees_built']} trees, {r.get('nodes_total', '?')} nodes "
            f"({r.get('leaves_total', '?')} leaves, max depth {r.get('max_depth', '?')}), "
            f"~{r.get('expected_comparisons_per_flow', float('nan')):.0f} comparisons per flow, "
            f"{r['pickled_bytes'] / 1024:.0f} KiB pickled, fit {fit_s:.1f} s")
    return pd.DataFrame(rows)


# ============================================================================ report
def fmt_p(p):
    return "  n/a " if p is None or (isinstance(p, float) and np.isnan(p)) else f"{p:.4f}"


def write_report(tests, holm_df, trees, out_dir, margin, report_metrics):
    L = ["Seed-level inference (unit = seed; one-sided Wilcoxon on the seed-level mean differences).",
         "p_cell = the pre-specified seed x type test, now DESCRIPTIVE. '<>' marks pairs where the two forms disagree "
         f"at {ALPHA}. NI = non-inferiority with margin {margin}: test of (A - B + margin) > 0; "
         "'point' = pre-specified point rule (mean diff >= -margin).", ""]
    if len(tests):
        t = tests[tests.metric.isin(report_metrics)]
        for (lvl, ty, met), g in t.groupby(["level", "types", "metric"], sort=False):
            L.append(f"== {lvl} | {ty} | {met}")
            for _, r in g.iterrows():
                tag = "NI " if r.kind == "non-inferiority" else "   "
                ci = ""
                if "ci_lo" in r and not pd.isna(r.get("ci_lo")):
                    ci = f"  CI [{r.ci_lo:+.3f}, {r.ci_hi:+.3f}] {'stable' if r.ci_excludes_0 else 'not stable'}"
                pt = f"  point {'met' if r.point_rule_met else 'not met'}" if r.kind == "non-inferiority" else ""
                L.append(f"  {tag}{r.A:12s} vs {r.B:13s} diff {r.mean_diff:+.3f}  seeds {r.seed_wins}/{r.n_seeds}  "
                         f"p_seed {fmt_p(r.p_seed)} {'SIG' if r.seed_decision else '   '}  "
                         f"p_cell {fmt_p(r.p_cell_descriptive)}{'  <>' if r.forms_disagree else ''}{pt}{ci}")
            L.append("")
        dis = tests[tests.forms_disagree & tests.metric.isin(report_metrics)]
        L.append(f"== decisions that CHANGE when the seed is the unit ({len(dis)} rows; all metrics in seed_tests.csv)")
        for _, r in dis.iterrows():
            L.append(f"  {r.level} | {r.types} | {r.metric} | {r.A} vs {r.B}: cell {'SIG' if r.cell_decision else 'n.s.'}"
                     f" -> seed {'SIG' if r.seed_decision else 'n.s.'} (p_seed {fmt_p(r.p_seed)},"
                     f" p_cell {fmt_p(r.p_cell_descriptive)})")
        L.append("")
    if len(holm_df):
        L.append("== confirmatory family (CIC-UNSW-NB15, recall at threshold B, all 9 types), Holm over the 8 tests")
        for _, r in holm_df.iterrows():
            if r.get("missing", False):
                L.append(f"  {r.hypothesis:17s} MISSING ({r.A} or {r.B} not in {r.level})")
                continue
            L.append(f"  {r.hypothesis:17s} {r.A:11s} vs {r.B:13s} diff {r.mean_diff:+.3f}  seeds {r.seed_wins}/{r.n_seeds}"
                     f"  p_seed {fmt_p(r.p_seed)}  Holm {fmt_p(r.p_seed_holm)}  -> seed {r.seed_level_decision},"
                     f" Holm {r.holm_decision}; pre-specified {r.pre_specified_decision}")
        L.append("")
    if trees is not None and len(trees):
        L.append("== HistGradientBoosting tree of branch T / TREE ('known' task)")
        L.append(trees.round(3).to_string(index=False))
    txt = "\n".join(L)
    open(os.path.join(out_dir, "seed_stats_report.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)


# ============================================================================ selftest
def selftest():
    ok = []
    # 1) Holm against a hand-computed example
    h = holm([0.01, 0.04, 0.03, np.nan, 0.005])
    exp = [0.03, 0.06, 0.06, np.nan, 0.02]
    ok.append(np.allclose(h[~np.isnan(h)], [e for e in exp if not np.isnan(e)]))
    print(f"{'PASS' if ok[-1] else 'FAIL'} Holm: {np.round(h, 4)} (expected {exp})")
    # 2) shared seed effect: cells look significant, seeds do not
    rng = np.random.default_rng(3)
    rows = []
    for s in range(10):
        se = rng.normal(0, 0.05)                                   # seed-level difference, mean ~0
        for t in range(9):
            base = rng.uniform(0.1, 0.6)
            rows += [dict(scenario="known", held="-", seed=s, type=f"t{t}", model="B", recall1=base, tiny=False),
                     dict(scenario="known", held="-", seed=s, type=f"t{t}", model="A",
                          recall1=base + se + 0.004 + rng.normal(0, 0.002), tiny=False),
                     dict(scenario="known", held="-", seed=s, type=f"t{t}", model="C",
                          recall1=base + 0.05 + rng.normal(0, 0.01), tiny=False),
                     dict(scenario="known", held="-", seed=s, type=f"t{t}", model="N",
                          recall1=base - 0.007 + rng.normal(0, 0.003), tiny=False)]
    df = pd.DataFrame(rows)
    r_ab = test_pair(df, "A", "B", "recall1", "sup", 0.02)
    r_cb = test_pair(df, "C", "B", "recall1", "sup", 0.02)
    r_nb = test_pair(df, "N", "B", "recall1", "ni", 0.02)
    ok.append(r_cb["seed_decision"] and r_cb["seed_wins"] == 10 and abs(r_cb["p_seed"] - 1 / 1024) < 1e-9)
    print(f"{'PASS' if ok[-1] else 'FAIL'} consistent +0.05: 10/10 seeds, exact p_seed = 1/1024 ({r_cb['p_seed']:.6f})")
    ok.append(r_ab["n_cells"] == 90 and r_ab["n_seeds"] == 10)
    print(f"{'PASS' if ok[-1] else 'FAIL'} cell / seed counts: {r_ab['n_cells']} cells, {r_ab['n_seeds']} seeds; "
          f"seed-effect pair: p_cell {r_ab['p_cell_descriptive']:.4f}, p_seed {r_ab['p_seed']:.4f}, "
          f"disagree = {r_ab['forms_disagree']}")
    ok.append(r_nb["point_rule_met"] and r_nb["seed_decision"] and r_nb["seed_wins"] == 10)
    print(f"{'PASS' if ok[-1] else 'FAIL'} non-inferiority -0.007 vs margin 0.02: point rule met, "
          f"seed-level p {r_nb['p_seed']:.6f}")
    # 3) family on synthetic UNSW-like runs
    fam_rows = []
    for scen in ("known", "loo"):
        for s in range(10):
            for t in (["t1", "t2"] if scen == "loo" else [f"t{i}" for i in range(9)]):
                held = "fam" if scen == "loo" else "-"
                b = rng.uniform(0, 0.05)
                for mdl, add in (("TREE", 0.0), ("V3-SUP", rng.normal(0, .01)), ("V3-SUP-DENSE", rng.normal(0, .01)),
                                 ("V3-SUP-NOA", -0.007 + rng.normal(0, .002)), ("V3-MAX", 0.14 + rng.normal(0, .02)),
                                 ("V3-MAX-RBF", 0.14 + rng.normal(0, .02))):
                    fam_rows.append(dict(scenario=scen, held=held, seed=s, type=t, model=mdl, recall1=b + add, tiny=False))
    fdf = pd.DataFrame(fam_rows)
    runs = [("uk", fdf[fdf.scenario == "known"]), ("ul", fdf[fdf.scenario == "loo"])]
    _, hdf = part_ab(runs, [], [], ["recall1"], 0.02, ["all types"], None, "uk,ul")
    u3 = hdf[hdf.hypothesis == "U3 known"].iloc[0]
    ok.append(len(hdf) == 8 and u3.holm_decision == "met" and not hdf.missing.any())
    print(f"{'PASS' if ok[-1] else 'FAIL'} confirmatory family: 8 tests, U3 known met after Holm "
          f"(p {u3.p_seed:.4f} -> {u3.p_seed_holm:.4f})")
    print("ALL PASS" if all(ok) else "SOME CHECKS FAILED")
    return all(ok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", default=[], help="LABEL=PATH@SCENARIO (repeat)")
    ap.add_argument("--pairs", default=DEFAULT_PAIRS, help="comma list A>B (superiority); missing models are skipped")
    ap.add_argument("--ni", default=DEFAULT_NI, help="comma list A>=B (non-inferiority, margin --margin)")
    ap.add_argument("--margin", type=float, default=0.02)
    ap.add_argument("--metrics", default=",".join(METRICS))
    ap.add_argument("--report_metrics", default=",".join(REPORT_METRICS))
    ap.add_argument("--tiny", choices=["keep", "exclude", "both"], default="both")
    ap.add_argument("--ci", default="", help="ci_pairs.csv of bootstrap_ci.py (same --run labels), optional")
    ap.add_argument("--confirm", default="", help="KNOWN_LABEL,LOO_LABEL of the CIC-UNSW-NB15 runs -> Holm family")
    ap.add_argument("--tree", action="store_true", help="refit the branch-T tree and report its size")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--tree_seeds", default="0")
    ap.add_argument("--out_dir", default="seed_stats")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.run and not a.tree:
        raise SystemExit("give --run LABEL=PATH@SCENARIO (repeat) and/or --tree (see the header of this file)")
    os.makedirs(a.out_dir, exist_ok=True)
    pairs = [tuple(x.strip() for x in p.split(">")) for p in a.pairs.split(",") if ">" in p and ">=" not in p]
    ni = [tuple(x.strip() for x in p.split(">=")) for p in a.ni.split(",") if ">=" in p]
    tiny_modes = {"keep": ["all types"], "exclude": ["non-tiny types"], "both": ["all types", "non-tiny types"]}[a.tiny]
    tests, holm_df = pd.DataFrame(), pd.DataFrame()
    if a.run:
        runs = [r for r in (read_run(s) for s in a.run) if r is not None]
        labels = [r[0] for r in runs]
        if len(set(labels)) != len(labels):
            raise SystemExit(f"--run labels must be unique, got {labels}")
        for label, df in runs:
            print(f"loaded {label}: {len(df):,} rows, models {sorted(df.model.unique())}, "
                  f"{df.seed.nunique()} seeds, {df.groupby(['held', 'type']).ngroups} units")
        tests, holm_df = part_ab(runs, pairs, ni, [m.strip() for m in a.metrics.split(",")], a.margin, tiny_modes,
                                 a.ci or None, a.confirm or None)
        tests.to_csv(os.path.join(a.out_dir, "seed_tests.csv"), index=False)
        if len(holm_df):
            holm_df.to_csv(os.path.join(a.out_dir, "holm_confirmatory.csv"), index=False)
    trees = None
    if a.tree:
        trees = tree_size(a.s17_dir, [int(s) for s in a.tree_seeds.split(",")])
        trees.to_csv(os.path.join(a.out_dir, "tree_size.csv"), index=False)
    write_report(tests, holm_df, trees, a.out_dir, a.margin, [m.strip() for m in a.report_metrics.split(",")])
    print(f"\nsaved -> {a.out_dir}: seed_tests.csv, holm_confirmatory.csv, tree_size.csv, seed_stats_report.txt")


if __name__ == "__main__":
    main()
