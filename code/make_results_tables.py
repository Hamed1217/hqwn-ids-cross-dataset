"""
Results tables for Section 4 of the paper, built ONLY from files that already exist (no model is run, nothing is
re-run). Every number in the Results text is meant to come from results_tables.md / the CSV files written here.

Tables (each is skipped with a note if its input file is missing):
  R1  four-level ladder + confirmatory: per level and model, macro recall at threshold B (1% and 0.1%), observed test
      FPR, pAUC(1%), mean (sd) over seeds, two-way bootstrap CI (ci/ci_models.csv), all types and non-tiny types
  R2  confirmatory hypotheses U1-U5 (seed_stats/holm_confirmatory.csv) + bootstrap CI (ci/ci_pairs.csv)
  R3  paired comparisons per level, seed level (seed_stats/seed_tests.csv), recall1 and pauc1, with CI
  R4  L3 ablation (v31_ablation10): model means + seed-level tests
  R5  CIC-UNSW-NB15 per attack type (recall at B, mean over seeds), counterpart vs new types
  R6  CIC-UNSW-NB15 ROC-interpolated recall and average precision (unsw_primary/matched_fpr_per_type.csv)
  R7  event-level metric (event_per_type.csv / event_benign.csv of unsw_primary and scores_cross)
  R8  latency and energy (efficiency_v3)
  R9  benign-reference sensitivity (sens_unsw/<variant>/v3_results.csv)
  R10 context and conflict audits (audit_target)
  R11 attack-family naming (family_metrics.csv)
  R12 derived metrics (every metrics_overall.csv found under --root)

  python make_results_tables.py --root "D:/revised model" --out_dir "D:/revised model/results_tables"
  python make_results_tables.py --selftest
Outputs: results_tables.md, results_tables_log.txt, R*.csv in --out_dir. Send results_tables.md (and the log).
"""
import argparse, glob, os, re
import numpy as np
import pandas as pd

LEVELS = [("easy (L1)", "scores_within/v3_results.csv", "known"),
          ("medium (L2)", "v33_within10/v3_results.csv", "loo"),
          ("hard (L3)", "v33_cross10/v3_results.csv", "known"),
          ("hardest (L4)", "v33_cross10/v3_results.csv", "loo"),
          ("UNSW known (L3)", "unsw_primary/v3_results.csv", "known"),
          ("UNSW held-out (L4)", "unsw_primary/v3_results.csv", "loo")]
CI_LABEL = {"easy (L1)": "easy", "medium (L2)": "medium", "hard (L3)": "hard", "hardest (L4)": "hardest",
            "UNSW known (L3)": "unsw_known", "UNSW held-out (L4)": "unsw_loo"}
MODEL_ORDER = ["TREE", "V3-SUP", "V3-SUP-DENSE", "V3-SUP-NOA", "V3-MAX", "V3-MAX-RBF", "V3-SUP-NOALIGN",
               "V3-SUP-NOW", "V3-SUP-SHUF", "V3-SUP-TT", "V3-SUP-LR"]
UNSW_COUNTERPART = {"DoS", "Reconnaissance"}


class Out:
    def __init__(self, out_dir):
        self.dir, self.md, self.log = out_dir, [], []
        os.makedirs(out_dir, exist_ok=True)

    def say(self, s):
        print(s, flush=True)
        self.log.append(s)

    def table(self, name, title, df, note=""):
        self.md.append(f"## {name}. {title}\n")
        if note:
            self.md.append(note + "\n")
        if df is None or len(df) == 0:
            self.md.append("_(no data)_\n")
            return
        df.to_csv(os.path.join(self.dir, f"{name}.csv"), index=False)
        self.md.append(md_table(df) + "\n")

    def missing(self, name, title, what):
        self.md.append(f"## {name}. {title}\n\n_skipped: {what} not found_\n")
        self.say(f"{name}: skipped ({what} not found)")

    def write(self):
        open(os.path.join(self.dir, "results_tables.md"), "w", encoding="utf-8").write("\n".join(self.md))
        open(os.path.join(self.dir, "results_tables_log.txt"), "w", encoding="utf-8").write("\n".join(self.log) + "\n")


def md_table(df):
    def f(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else (f"{v:.4f}" if abs(v) < 0.001 and v != 0 else f"{v:.3f}")
        return str(v)
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(f(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def order_models(df, col="model"):
    rank = {m: i for i, m in enumerate(MODEL_ORDER)}
    return df.assign(_o=df[col].map(lambda m: rank.get(m, 99))).sort_values(["_o", col]).drop(columns="_o")


def read_results(path, scen):
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df = df[df.scenario == scen] if "scenario" in df.columns else df
    df["held"] = df.get("held", "-")
    df["held"] = df["held"].fillna("-").astype(str)
    df["tiny"] = df["tiny"].astype(str).str.lower().isin(["true", "1"]) if "tiny" in df.columns else False
    return df


def seed_macro(df, cols):
    """mean over (held, type) cells per seed and model, then mean and sd over seeds"""
    per = df.groupby(["model", "seed"])[cols].mean()
    m, s = per.groupby("model").mean(), per.groupby("model").std()
    return m, s, per.groupby("model").size()


# ============================================================================ tables
def r1_ladder(root, O):
    ci = os.path.join(root, "ci", "ci_models.csv")
    C = pd.read_csv(ci) if os.path.exists(ci) else None
    rows = []
    for level, rel, scen in LEVELS:
        df = read_results(os.path.join(root, rel), scen)
        if df is None or df.empty:
            O.say(f"R1: {rel}@{scen} missing")
            continue
        cols = [c for c in ("recall1", "recall01", "fpr_test1", "pauc1") if c in df.columns]
        m, s, n = seed_macro(df, cols)
        mt, _, _ = seed_macro(df[~df.tiny], ["recall1"]) if df.tiny.any() else (None, None, None)
        for model in m.index:
            r = dict(level=level, model=model, seeds=int(n[model]),
                     recall1=m.loc[model, "recall1"], recall1_sd=s.loc[model, "recall1"])
            if C is not None:
                c = C[(C.level == CI_LABEL[level]) & (C.metric == "recall1") & (C.model == model)]
                if len(c):
                    r["ci_lo"], r["ci_hi"] = float(c.lo.iloc[0]), float(c.hi.iloc[0])
            if mt is not None and model in mt.index:
                r["recall1_nontiny"] = mt.loc[model, "recall1"]
            for c2 in ("fpr_test1", "recall01", "pauc1"):
                if c2 in m.columns:
                    r[c2] = m.loc[model, c2]
            rows.append(r)
    T = pd.DataFrame(rows)
    if len(T):
        T["_l"] = T.level.map({l[0]: i for i, l in enumerate(LEVELS)})
        T = order_models(T).sort_values("_l", kind="stable").drop(columns="_l")
    O.table("R1", "Four-level ladder and confirmatory test: macro recall at threshold B",
            T, "recall1 / recall01 = recall at threshold B for nominal FPR 1% / 0.1% (macro over attack types, mean "
               "over seeds); recall1_sd = sd over seeds; ci = two-way bootstrap 95% interval; fpr_test1 = observed FPR "
               "on the test benign part; pauc1 = McClish-standardised partial AUC up to 1% FPR.")


def r2_confirmatory(root, O):
    p = os.path.join(root, "seed_stats", "holm_confirmatory.csv")
    if not os.path.exists(p):
        return O.missing("R2", "Confirmatory hypotheses U1-U5", p)
    H = pd.read_csv(p)
    ci = os.path.join(root, "ci", "ci_pairs.csv")
    if os.path.exists(ci):
        C = pd.read_csv(ci)
        C = C[C.metric == "recall1"]
        H["ci_lo"] = [float(C[(C.level == r.level) & (C.pair == f"{r.A} - {r.B}")].lo.iloc[0])
                      if len(C[(C.level == r.level) & (C.pair == f"{r.A} - {r.B}")]) else np.nan for r in H.itertuples()]
        H["ci_hi"] = [float(C[(C.level == r.level) & (C.pair == f"{r.A} - {r.B}")].hi.iloc[0])
                      if len(C[(C.level == r.level) & (C.pair == f"{r.A} - {r.B}")]) else np.nan for r in H.itertuples()]
    keep = [c for c in ("hypothesis", "level", "A", "B", "kind", "mean_diff", "ci_lo", "ci_hi", "seed_wins", "n_seeds",
                        "p_seed", "p_seed_holm", "p_cell_descriptive", "seed_level_decision", "holm_decision",
                        "pre_specified_decision") if c in H.columns]
    O.table("R2", "Confirmatory hypotheses on CIC-UNSW-NB15 (calibrated recall at nominal FPR 1%, all nine types)",
            H[keep], "p_seed = one-sided Wilcoxon on the ten seed-level differences (inference); p_seed_holm = Holm "
                     "over the eight tests; p_cell_descriptive = pre-specified seed x type form, descriptive. For "
                     "non-inferiority (U2, U4) the test is of (A - B + 0.02) > 0.")


def r3_pairs(root, O):
    p = os.path.join(root, "seed_stats", "seed_tests.csv")
    if not os.path.exists(p):
        return O.missing("R3", "Paired comparisons per level", p)
    S = pd.read_csv(p)
    lv = ["easy", "medium", "hard", "hardest", "unsw_known", "unsw_loo"]
    T = S[S.level.isin(lv) & S.metric.isin(["recall1", "pauc1"]) & (S.types == "all types")]
    keep = [c for c in ("level", "metric", "kind", "A", "B", "mean_diff", "ci_lo", "ci_hi", "ci_excludes_0", "seed_wins",
                        "n_seeds", "p_seed", "p_cell_descriptive", "point_rule_met") if c in T.columns]
    T = T.assign(_l=T.level.map({l: i for i, l in enumerate(lv)})).sort_values(["_l", "metric", "kind"]).drop(columns="_l")
    O.table("R3", "Paired comparisons per level (seed level; all attack types)", T[keep],
            "stable = two-way bootstrap interval excludes zero (interval available for recall1 and pauc1 of the levels "
            "that bootstrap_ci.py was run on).")


def r4_ablation(root, O):
    df = read_results(os.path.join(root, "v31_ablation10", "v3_results.csv"), "known")
    p = os.path.join(root, "seed_stats", "seed_tests.csv")
    if df is None:
        return O.missing("R4", "L3 ablation", "v31_ablation10/v3_results.csv")
    m, s, n = seed_macro(df, [c for c in ("recall1", "pauc1") if c in df.columns])
    M = m.add_suffix("_mean").join(s.add_suffix("_sd")).reset_index()
    O.table("R4a", "L3 ablation (CSE-CIC-IDS2018, ten seeds, v3.2 code before the lock): model means", order_models(M))
    if os.path.exists(p):
        S = pd.read_csv(p)
        T = S[(S.level == "hard_ablation") & (S.metric == "recall1")]
        keep = [c for c in ("types", "kind", "A", "B", "mean_diff", "seed_wins", "n_seeds", "p_seed",
                            "p_cell_descriptive", "point_rule_met") if c in T.columns]
        O.table("R4b", "L3 ablation: seed-level paired tests (recall at B, 1%)", T[keep])


def r5_unsw_types(root, O):
    df = read_results(os.path.join(root, "unsw_primary", "v3_results.csv"), "known")
    if df is None:
        return O.missing("R5", "CIC-UNSW-NB15 per attack type", "unsw_primary/v3_results.csv")
    P = df.groupby(["type", "model"]).recall1.mean().unstack()
    P = P[[m for m in MODEL_ORDER if m in P.columns]]
    n = df.groupby("type").n.first() if "n" in df.columns else None
    P.insert(0, "group", ["counterpart" if t in UNSW_COUNTERPART else "new" for t in P.index])
    if n is not None:
        P.insert(1, "flows", n.reindex(P.index).values)
    P = P.reset_index().sort_values(["group", "type"])
    g = df.assign(group=df.type.map(lambda t: "counterpart" if t in UNSW_COUNTERPART else "new"))
    G = g.groupby(["group", "model", "seed"]).recall1.mean().groupby(["group", "model"]).mean().unstack()
    G = G[[m for m in MODEL_ORDER if m in G.columns]].reset_index().rename(columns={"group": "type"})
    G.insert(0, "group", "mean")
    O.table("R5", "CIC-UNSW-NB15 (known scenario): recall at B per attack type, mean over ten seeds",
            pd.concat([P, G], ignore_index=True))


def r6_unsw_matched(root, O):
    p = os.path.join(root, "unsw_primary", "matched_fpr_per_type.csv")
    if not os.path.exists(p):
        return O.missing("R6", "CIC-UNSW-NB15 ROC-interpolated recall and average precision", p)
    D = pd.read_csv(p)
    cols = [c for c in ("recall_B", "fpr_B", "recall_at1", "recall_at01", "pr_auc") if c in D.columns]
    rows = []
    for scen, g in D.groupby("scenario"):
        m, s, _ = seed_macro(g, cols)
        for model in m.index:
            rows.append(dict(scenario=scen, model=model, **{c: m.loc[model, c] for c in cols}))
    O.table("R6", "CIC-UNSW-NB15: calibrated recall, ROC-interpolated recall (test FPR 1% / 0.1%) and average precision",
            order_models(pd.DataFrame(rows)).sort_values("scenario", kind="stable"))


def r7_events(root, O):
    found = False
    for name, sub in (("CIC-UNSW-NB15", "unsw_primary"), ("CSE-CIC-IDS2018", "scores_cross")):
        pt, pb = os.path.join(root, sub, "event_per_type.csv"), os.path.join(root, sub, "event_benign.csv")
        if not os.path.exists(pt):
            O.say(f"R7: {pt} not found")
            continue
        found = True
        T = pd.read_csv(pt)
        O.say(f"R7 {name}: event_per_type columns {list(T.columns)}")
        num = [c for c in T.columns if c not in ("seed", "scenario", "held", "model", "fpr", "k", "type")
               and pd.api.types.is_numeric_dtype(T[c])]
        A = (T.groupby(["scenario", "fpr", "k", "model", "seed"])[num].mean()
             .groupby(["scenario", "fpr", "k", "model"]).mean().reset_index())
        if os.path.exists(pb):
            B = pd.read_csv(pb)
            O.say(f"R7 {name}: event_benign columns {list(B.columns)}")
            nb = [c for c in B.columns if c not in ("seed", "scenario", "held", "model", "fpr", "k")
                  and pd.api.types.is_numeric_dtype(B[c])]
            Bm = (B.groupby(["scenario", "fpr", "k", "model", "seed"])[nb].mean()
                  .groupby(["scenario", "fpr", "k", "model"]).mean().reset_index())
            A = A.merge(Bm, on=["scenario", "fpr", "k", "model"], how="left", suffixes=("", "_benign"))
        O.table(f"R7_{sub}", f"Event-level metric, {name} (mean over attack types, then over seeds)",
                order_models(A).sort_values(["scenario", "fpr", "k"], kind="stable"))
    if not found:
        O.missing("R7", "Event-level metric", "event_per_type.csv")


def r8_efficiency(root, O):
    d = os.path.join(root, "efficiency_v3")
    if not os.path.isdir(d):
        return O.missing("R8", "Latency and energy", d)
    for f, title in (("latency_end_to_end.csv", "End-to-end p95 latency (batch 1) and throughput"),
                     ("latency_parts.csv", "Latency of each part"),
                     ("energy_memory_sensitivity.csv", "Energy estimate with memory-access sensitivity")):
        p = os.path.join(d, f)
        if os.path.exists(p):
            T = pd.read_csv(p)
            O.say(f"R8 {f}: columns {list(T.columns)}")
            O.table(f"R8_{f[:-4]}", title, T)
        else:
            O.say(f"R8: {p} not found")


def r9_sensitivity(root, O):
    files = sorted(glob.glob(os.path.join(root, "sens_unsw", "*", "v3_results.csv")))
    if not files:
        return O.missing("R9", "Benign-reference sensitivity", "sens_unsw/<variant>/v3_results.csv")
    rows = []
    for f in files:
        var = os.path.basename(os.path.dirname(f))
        D = pd.read_csv(f)
        for scen, g in D.groupby("scenario"):
            m, s, n = seed_macro(g, [c for c in ("recall1", "fpr_test1") if c in g.columns])
            for model in m.index:
                rows.append(dict(variant=var, scenario=scen, model=model, seeds=int(n[model]),
                                 recall1=m.loc[model, "recall1"], recall1_sd=s.loc[model, "recall1"],
                                 fpr_test1=m.loc[model, "fpr_test1"] if "fpr_test1" in m.columns else np.nan))
    order = {v: i for i, v in enumerate(["base", "size25", "size10", "time", "contam1", "contam5"])}
    T = pd.DataFrame(rows)
    T = order_models(T).assign(_v=T.variant.map(lambda v: order.get(v, 9))).sort_values(
        ["scenario", "_v"], kind="stable").drop(columns="_v")
    O.table("R9", "CIC-UNSW-NB15: sensitivity to the benign reference (five seeds, exploratory)", T)


def r10_audits(root, O):
    d = os.path.join(root, "audit_target")
    if not os.path.isdir(d):
        return O.missing("R10", "Context and conflict audits", d)
    for lab in ("unsw", "ids2018"):
        p = os.path.join(d, f"context_{lab}.csv")
        if os.path.exists(p):
            O.table(f"R10_context_{lab}", f"Share of benign flows with a sampled attack flow in their window ({lab})",
                    pd.read_csv(p))
        p = os.path.join(d, f"threshold_clean_{lab}_per_type.csv")
        if os.path.exists(p):
            R = pd.read_csv(p)
            A = (R.groupby(["nominal", "scenario", "model", "seed"])[["recall_B", "recall_Bclean"]].mean()
                 .groupby(["nominal", "scenario", "model"]).mean().reset_index())
            fp = os.path.join(d, f"threshold_clean_{lab}_fpr.csv")
            if os.path.exists(fp):
                F = pd.read_csv(fp).groupby(["nominal", "scenario", "model"])[
                    ["fpr_test_B", "fpr_cleantest_B", "fpr_cleantest_Bclean", "fpr_attackwindow_test_B"]].mean().reset_index()
                A = A.merge(F, on=["nominal", "scenario", "model"], how="left")
            O.table(f"R10_threshold_clean_{lab}", f"Threshold B from attack-free-window calibration flows ({lab})",
                    order_models(A).sort_values(["nominal", "scenario"], ascending=[False, True], kind="stable"))
    p = os.path.join(d, "conflicts_unsw_recall_bounds.csv")
    if os.path.exists(p):
        O.table("R10_conflict_bounds", "CIC-UNSW-NB15: recall bounds had the conflicting rows been kept",
                order_models(pd.read_csv(p)).sort_values("scenario", kind="stable"))
    p = os.path.join(d, "conflicts_unsw_rows.csv")
    if os.path.exists(p):
        G = pd.read_csv(p)
        O.table("R10_conflict_composition", "CIC-UNSW-NB15: removed conflicting rows by label and kind",
                pd.crosstab(G["lab"], G["kind"], margins=True).reset_index())


def r11_family(root, O):
    found = False
    for name, sub in (("CSE-CIC-IDS2018", "scores_cross"), ("CIC-UNSW-NB15", "unsw_primary"),
                      ("CIC-IDS2017", "scores_within")):
        p = os.path.join(root, sub, "family_metrics.csv")
        if not os.path.exists(p):
            continue
        found = True
        F = pd.read_csv(p)
        O.say(f"R11 {name}: family_metrics columns {list(F.columns)}")
        keys = [c for c in ("view", "scenario") if c in F.columns]
        num = [c for c in F.columns if c not in keys + ["seed", "held"] and pd.api.types.is_numeric_dtype(F[c])]
        A = F.groupby(keys)[num].mean().reset_index() if keys else F[num].mean().to_frame().T
        O.table(f"R11_{sub}", f"Attack-family naming, {name} (mean over seeds and tasks)", A)
    if not found:
        O.missing("R11", "Attack-family naming", "family_metrics.csv")


def r12_derived(root, O):
    files = sorted(glob.glob(os.path.join(root, "**", "metrics_overall.csv"), recursive=True))
    if not files:
        return O.missing("R12", "Derived metrics", "metrics_overall.csv")
    for f in files:
        D = pd.read_csv(f)
        rel = os.path.relpath(f, root).replace("\\", "/")
        O.say(f"R12 {rel}: columns {list(D.columns)}")
        name = "R12_" + re.sub(r"[^A-Za-z0-9]+", "_", os.path.dirname(rel))[:40]
        O.table(name, f"Derived metrics from {rel}", D)


def build(root, out_dir):
    O = Out(out_dir)
    O.md.append(f"# Results tables (built from saved files under {root}; nothing re-run)\n")
    for fn in (r1_ladder, r2_confirmatory, r3_pairs, r4_ablation, r5_unsw_types, r6_unsw_matched, r7_events,
               r8_efficiency, r9_sensitivity, r10_audits, r11_family, r12_derived):
        try:
            fn(root, O)
        except Exception as e:                       # one broken input must not stop the other tables
            O.say(f"{fn.__name__}: ERROR {type(e).__name__}: {e}")
            O.md.append(f"## {fn.__name__}\n\n_error: {type(e).__name__}: {e}_\n")
    O.write()
    print(f"\nsaved -> {out_dir}: results_tables.md, results_tables_log.txt, R*.csv")
    return O


def selftest():
    import tempfile
    root = tempfile.mkdtemp()
    rng = np.random.default_rng(0)
    rows = []
    for scen, types in (("known", ["DoS", "Reconnaissance", "Exploits", "Worms"]), ("loo", ["DoS", "Reconnaissance"])):
        for seed in range(10):
            for t in types:
                for mdl, base in (("TREE", .02), ("V3-SUP", .02), ("V3-MAX", .2), ("V3-MAX-RBF", .2)):
                    rows.append(dict(protocol="cross", scenario=scen, held="-", seed=seed, model=mdl, type=t, n=100,
                                     tiny=False, recall1=base + rng.normal(0, .01), fpr_test1=.01,
                                     recall01=base / 3, fpr_test01=.001, auc=.7, pauc1=.55))
    os.makedirs(os.path.join(root, "unsw_primary"))
    pd.DataFrame(rows).to_csv(os.path.join(root, "unsw_primary", "v3_results.csv"), index=False)
    O = build(root, os.path.join(root, "out"))
    md = open(os.path.join(root, "out", "results_tables.md"), encoding="utf-8").read()
    r1 = pd.read_csv(os.path.join(root, "out", "R1.csv"))
    v = r1[(r1.level == "UNSW known (L3)") & (r1.model == "V3-MAX")].recall1.iloc[0]
    exp = pd.DataFrame(rows).query("scenario == 'known' and model == 'V3-MAX'").groupby("seed").recall1.mean().mean()
    ok1 = abs(v - exp) < 1e-12
    ok2 = "## R5." in md and "skipped" in md and "## R2." in md
    print(f"{'PASS' if ok1 else 'FAIL'} R1 macro recall = mean over seeds of the mean over types ({v:.4f})")
    print(f"{'PASS' if ok2 else 'FAIL'} missing inputs are skipped, available tables are written")
    print("ALL PASS" if ok1 and ok2 else "SOME CHECKS FAILED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="D:/revised model")
    ap.add_argument("--out_dir", default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    build(a.root, a.out_dir or os.path.join(a.root, "results_tables"))


if __name__ == "__main__":
    main()
