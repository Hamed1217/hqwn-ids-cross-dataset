"""
EXPLORATORY, post-hoc (run after the confirmatory test of 2026-10-25; NOT part of it).
Question: which inputs of the benign-reference novelty channel carry its gain on CIC-UNSW-NB15?
The channel (V3-MAX) scores each flow with a one-class model fitted on benign flows of the target network. Its input is
  flow features (the harmonised CICFlowMeter columns)  +  a 6-number summary of the 16-minute service-load sequence
  (load of the flow's own service in the last minute, and the maximum over the 16 minutes; 3 load channels each).
The frozen hybrid_v3.run is called UNCHANGED; only the function that builds the novelty input is replaced
(hybrid_v3.novelty_features), exactly as benign_sensitivity.py / ctx_clean_run.py replace other parts. The supervised
models (TREE, V3-SUP) do not use that function and are therefore identical in every variant (sanity check).

Variants
  base       flow + load summary (original input)       -> must reproduce V3-MAX 0.163 (all types) / 0.388 (held-out)
  load_only  the 6 load-summary numbers only, 6 qubits  (PCA cannot give 8 components from 6 inputs; the RBF twin uses the
             same 6 inputs, so the quantum-kernel comparison stays like-for-like)
  flow_only  flow features only, 8 qubits (the load summary removed)

Decision rules, written BEFORE running (2026-11-03). R = recall at nominal FPR 1% (threshold B), mean over attack types,
mean over ten seeds; "share" = R(variant, V3-MAX) / R(base, V3-MAX), computed separately for the all-types ("known")
and the held-out ("loo") scenario. A variant is valid only if the observed test FPR of V3-MAX is between 0.5% and 2%.
  (1) base reproduces the main result within +-0.005, otherwise the run is not interpreted.
  (2) load_only share >= 0.8 in both scenarios  -> "the load summary carries essentially all of the gain".
      0.4 <= share < 0.8                          -> "both input groups contribute".
      share < 0.4 in both scenarios               -> "the flow features carry the gain".
  (3) the same three-way rule is applied to flow_only; if both shares are >= 0.8 the inputs are redundant.
  (4) For V3-MAX in load_only, the number of seeds with V3-MAX > V3-SUP is reported (>= 8 of 10 = the advantage over the
      supervised model persists with load only).
  (5) Reconnaissance recall is reported for every variant, because the earlier audit located the gain there.
  (6) IQP versus RBF (V3-MAX vs V3-MAX-RBF) is reported again in load_only; no claim of a quantum advantage is made unless
      the seed-level Wilcoxon p < 0.05 with the difference in favour of IQP in >= 8 of 10 seeds.
Whatever the outcome, it is reported as exploratory. The settings above are not changed after the first full run.

  python load_only_run.py --selftest
  python load_only_run.py --smoke --variants base,load_only --mode known --out_dir smoke_lo
  python load_only_run.py --seeds 3  --out_dir "D:/revised model/load_only_unsw"      (pilot)
  python load_only_run.py --seeds 10 --out_dir "D:/revised model/load_only_unsw"      (full)
  python load_only_run.py --compare_only --out_dir "D:/revised model/load_only_unsw"
"""
import argparse, os, time, types, warnings
import numpy as np
import pandas as pd
import benign_sensitivity as BS

VARIANTS = ("base", "load_only", "flow_only")


def feats(variant, Xflow, S):
    X = np.asarray(Xflow, dtype="float64")
    S = np.asarray(S, dtype="float64")
    load = np.hstack([S[:, -1, :], S.max(axis=1)])
    if variant == "base":
        return np.hstack([X, load])
    if variant == "load_only":
        return load
    if variant == "flow_only":
        return X
    raise ValueError(variant)


def qubits_for(variant, default):
    return 6 if variant == "load_only" else default


def _shares(df, scen, model="V3-MAX"):
    out = {}
    for v, d in df.items():
        s = d[(d.scenario == scen) & (d.model == model)]
        out[v] = s.groupby("seed").recall1.mean().mean() if len(s) else np.nan
    return out


def verdict(share):
    if not np.isfinite(share):
        return "n/a"
    return "carries essentially all" if share >= 0.8 else ("both contribute" if share >= 0.4 else "carries little")


def compare(out_dir, variants):
    from scipy.stats import wilcoxon
    dfs = {v: pd.read_csv(os.path.join(out_dir, v, "v3_results.csv")) for v in variants
           if os.path.exists(os.path.join(out_dir, v, "v3_results.csv"))}
    L = ["LOAD-ONLY / FLOW-ONLY NOVELTY (exploratory, post-hoc). R = recall at nominal FPR 1% (threshold B), mean over",
         "attack types, then over seeds. fpr = observed test FPR of the model. Rules are in the header of load_only_run.py.", ""]
    for scen in ("known", "loo"):
        L.append(f"==== scenario {scen}")
        rows = []
        for v, d in dfs.items():
            s = d[d.scenario == scen]
            if s.empty:
                continue
            ps = s.groupby(["model", "seed"])[["recall1", "fpr_test1", "pauc1"]].mean()
            for mdl, g in ps.groupby(level="model"):
                rec = s[(s.model == mdl) & (s.type.astype(str).str.contains("Recon", case=False))].groupby("seed").recall1.mean()
                rows.append(dict(variant=v, model=mdl, R=g.recall1.mean(), fpr=g.fpr_test1.mean(), pauc=g.pauc1.mean(),
                                 R_recon=rec.mean() if len(rec) else np.nan, seeds=g.shape[0]))
        if not rows:
            continue
        t = pd.DataFrame(rows)
        L.append(t.round(4).to_string(index=False))
        sh = _shares(dfs, scen)
        b = sh.get("base", np.nan)
        for v in dfs:
            if v == "base":
                continue
            d = dfs[v]; s = d[(d.scenario == scen) & (d.model == "V3-MAX")]
            fp = s.groupby("seed").fpr_test1.mean().mean() if len(s) else np.nan
            share = sh[v] / b if b and np.isfinite(b) else np.nan
            L.append(f"  share of base V3-MAX recall kept by {v}: {share:.2f} -> {verdict(share)}   (observed FPR {fp:.4f}; "
                     f"{'valid' if 0.005 <= fp <= 0.02 else 'INVALID: FPR outside 0.5-2%'})")
        if "base" in dfs and np.isfinite(b):
            L.append(f"  base V3-MAX R = {b:.3f}  (rule 1: must be within 0.005 of the main result)")
        for v, d in dfs.items():
            pv = d[(d.scenario == scen) & d.model.isin(["V3-MAX", "V3-SUP"])].groupby(["model", "seed"]).recall1.mean().unstack(0)
            if {"V3-MAX", "V3-SUP"} <= set(pv.columns):
                diff = (pv["V3-MAX"] - pv["V3-SUP"]).dropna()
                p = wilcoxon(diff, alternative="greater").pvalue if (diff != 0).sum() >= 3 else np.nan
                L.append(f"  {v}: V3-MAX - V3-SUP = {diff.mean():+.3f}; seeds with V3-MAX > V3-SUP: {(diff > 0).sum()}/{len(diff)}; one-sided p {p:.3f}")
            pq = d[(d.scenario == scen) & d.model.isin(["V3-MAX", "V3-MAX-RBF"])].groupby(["model", "seed"]).recall1.mean().unstack(0)
            if {"V3-MAX", "V3-MAX-RBF"} <= set(pq.columns):
                diff = (pq["V3-MAX"] - pq["V3-MAX-RBF"]).dropna()
                p = wilcoxon(diff, alternative="greater").pvalue if (diff != 0).sum() >= 3 else np.nan
                L.append(f"  {v}: IQP - RBF = {diff.mean():+.3f}; seeds with IQP > RBF: {(diff > 0).sum()}/{len(diff)}; one-sided p {p:.3f}")
        L.append("")
    txt = "\n".join(L)
    open(os.path.join(out_dir, "load_only_report.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)


def selftest():
    ok = True
    def chk(nm, c):
        nonlocal ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + nm)
    g = np.random.default_rng(0)
    X = g.normal(size=(300, 12)); S = np.abs(g.normal(size=(300, 16, 3)))
    chk("base = flow + 6 load numbers", feats("base", X, S).shape == (300, 18))
    chk("load_only has 6 inputs", feats("load_only", X, S).shape == (300, 6))
    chk("flow_only has the flow columns unchanged", np.array_equal(feats("flow_only", X, S), X))
    import qkernel
    chk("base equals qkernel.novelty_features (the frozen original)", np.allclose(feats("base", X, S), qkernel.novelty_features(X, S)))
    for v in ("load_only", "flow_only"):
        for kind in ("iqp", "rbf"):
            nq = qubits_for(v, 8 if v == "flow_only" else 8)
            tm = qkernel.LocalNovelty(kind, n_qubits=nq, m=120, nu=0.1, seed=0)
            F = feats(v, X, S)
            tm.fit(F[:150]).set_reference(F[150:250])
            p = tm.percentile(F[250:])
            chk(f"{v}/{kind}: percentiles in [0,1], {nq} qubits", len(p) == 50 and ((p >= 0) & (p <= 1)).all())
    chk("qubits: load_only 6, others default", qubits_for("load_only", 8) == 6 and qubits_for("base", 8) == 8)
    import tempfile
    d = tempfile.mkdtemp()
    r = np.random.default_rng(1)
    for v, lift in (("base", 0.4), ("load_only", 0.35), ("flow_only", 0.05)):
        os.makedirs(os.path.join(d, v))
        rows = []
        for sc in ("known", "loo"):
            for sd in range(10):
                for m, base_r in (("V3-SUP", 0.02), ("V3-MAX", lift), ("V3-MAX-RBF", lift), ("TREE", 0.02)):
                    for t in ("Reconnaissance", "Fuzzers"):
                        rows.append(dict(scenario=sc, seed=sd, model=m, type=t, recall1=base_r + r.normal(0, .01),
                                         fpr_test1=0.011, pauc1=0.5))
        pd.DataFrame(rows).to_csv(os.path.join(d, v, "v3_results.csv"), index=False)
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        compare(d, list(VARIANTS))
    txt = buf.getvalue()
    chk("report: load_only classified 'carries essentially all'", "load_only: 0.8" in txt.replace("by load_only: ", "load_only: ") or "carries essentially all" in txt)
    chk("report: flow_only classified 'carries little'", "carries little" in txt)
    chk("report mentions Reconnaissance column and seed counts", "R_recon" in txt and "/10" in txt)
    print("ALL PASS" if ok else "SOME CHECKS FAILED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="unsw")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--cache", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--out_dir", default="load_only_unsw")
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--configs", default="TREE,V3-SUP,V3-MAX,V3-MAX-RBF")
    ap.add_argument("--mode", choices=["known", "loo", "both"], default="both")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--compare_only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a0 = ap.parse_args()
    if a0.selftest:
        return selftest()
    variants = [v.strip() for v in a0.variants.split(",") if v.strip()]
    if a0.compare_only:
        return compare(a0.out_dir, variants)
    warnings.filterwarnings("ignore")
    import torch, hashlib
    import hybrid_v3 as V
    a = types.SimpleNamespace(protocol="cross", target=a0.target, s17_dir=a0.s17_dir, target_cache=a0.cache,
                              out_dir=a0.out_dir, mode=a0.mode, configs=a0.configs, within_fams=",".join(V.WITHIN_FAMS),
                              seeds=a0.seeds, max_train=30000, val_max=10000, tree_train=100000, epochs=6, patience=2,
                              bs=512, lr=2e-3, lb=0.1, qubits=8, q_m=2000, q_nu=0.1, device="cpu")
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    if a0.smoke:
        a.seeds, a.epochs, a.max_train, a.val_max, a.tree_train, a.q_m, a.qubits = 1, 2, 3000, 1500, 3000, 300, 6
        a.target = "ids2018"
    here = os.path.dirname(os.path.abspath(V.__file__))
    print("code fingerprint:", {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()[:12]
                                for f in ("hybrid_v3.py", "qkernel.py")}, flush=True)
    D = V.make_smoke("cross") if a0.smoke else V.load_data(a)
    orig_nf, orig_bt = V.novelty_features, V.build_target
    V.build_target = lambda D_, a_: BS.make_target(D_, a_, "base", V.is_benign, V.CP[a_.target], None)
    default_q = a.qubits
    for v in variants:
        od = os.path.join(a0.out_dir, v)
        os.makedirs(od, exist_ok=True)
        V.novelty_features = lambda X, S, v=v: feats(v, X, S)
        a.qubits = 6 if (v == "load_only" and not a0.smoke) else (min(6, default_q) if v == "load_only" else default_q)
        t0 = time.time()
        print(f"\n######## variant {v} (novelty inputs: {v}; qubits {a.qubits}) ########", flush=True)
        V.run(D, a, torch.device("cpu"), od)
        print(f"variant {v} done [{time.time() - t0:.0f}s]", flush=True)
    V.novelty_features, V.build_target = orig_nf, orig_bt
    compare(a0.out_dir, variants)


if __name__ == "__main__":
    main()
