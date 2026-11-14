"""
EXPLORATORY, post-hoc (run after the confirmatory test of 2026-10-25; NOT part of it).
Question (from review): is the gain of V3-MAX on CIC-UNSW-NB15 specific to the one-class SVM with a quantum or RBF
kernel, or does any standard one-class detector fitted on the same benign reference give it?

The frozen hybrid_v3.run is called UNCHANGED. Only two things are added at run time, as in load_only_run.py:
  * hybrid_v3.LocalNovelty is replaced by ExtNovelty, which keeps every original kind (iqp, rbf, rff, iforest) exactly
    and adds three standard detectors: 'lof' (Local Outlier Factor), 'mahal' (Mahalanobis distance) and 'ae'
    (a small autoencoder, reconstruction error). They see the SAME input as the kernel models: the flow features plus
    the six-number load summary, after the same quantile transform, PCA to n_qubits components and standardisation,
    fitted on the same m benign reference flows. The percentile scale (set_reference) is unchanged.
  * new configurations are added to hybrid_v3.CONFIGS: V3-MAX-IF, V3-MAX-LOF, V3-MAX-MAHAL, V3-MAX-AE (late fusion with
    V3-SUP, exactly like V3-MAX) and Q-LOF, Q-MAHAL, Q-AE (novelty score alone, like the existing Q-IQP, Q-RBF, Q-IF).
The target split is the main one (benign_sensitivity.make_target 'base'), as in the other audits.

Decision rules, written BEFORE running. R = recall at nominal FPR 1% (threshold B), mean over attack types, mean over
ten seeds, per scenario (known = all types, loo = held-out types).
  (1) V3-MAX in this run reproduces the main result (0.163 known, 0.388 loo) within +-0.005, otherwise nothing is
      interpreted.
  (2) For each baseline X, D = R(V3-MAX-X) - R(V3-MAX). If D >= -0.02 in both scenarios, X is called "equivalent":
      the gain belongs to benign-reference novelty detection in general, not to the kernel model.
      If D < -0.02 in a scenario and the one-sided seed-level Wilcoxon (V3-MAX > V3-MAX-X) gives p < 0.05 there, the
      kernel one-class SVM is "better than X" in that scenario. Otherwise "inconclusive".
  (3) For every V3-MAX-X, the number of seeds with V3-MAX-X > V3-SUP is reported (>= 8 of 10: the advantage over the
      supervised model holds with that detector).
  (4) Reconnaissance recall and the observed test FPR of every model are reported. A model whose observed FPR is
      outside 0.5%-2% is marked invalid.
  (5) No claim of a quantum advantage is made from this run.
Whatever the outcome, it is reported as exploratory.

  python novelty_baselines_run.py --selftest
  python novelty_baselines_run.py --smoke --out_dir smoke_nb
  python novelty_baselines_run.py --seeds 3  --out_dir "D:/revised model/novelty_baselines_unsw"   (pilot)
  python novelty_baselines_run.py --seeds 10 --out_dir "D:/revised model/novelty_baselines_unsw"   (full)
  python novelty_baselines_run.py --compare_only --out_dir "D:/revised model/novelty_baselines_unsw"
Copy this file into code/ (next to hybrid_v3.py, qkernel.py and benign_sensitivity.py) before running.
"""
import argparse, os, time, types, warnings
import numpy as np
import pandas as pd

NEW_KINDS = ("lof", "mahal", "ae")
FUSED = ("V3-MAX", "V3-MAX-RBF", "V3-MAX-IF", "V3-MAX-LOF", "V3-MAX-MAHAL", "V3-MAX-AE")
ALONE = ("Q-IQP", "Q-RBF", "Q-IF", "Q-LOF", "Q-MAHAL", "Q-AE")
DEFAULT_CONFIGS = ("TREE", "V3-SUP") + FUSED + ALONE


def make_ext(LocalNovelty):
    """subclass of the frozen qkernel.LocalNovelty; original kinds are passed through untouched"""
    class ExtNovelty(LocalNovelty):
        def fit(self, F_benign):
            if self.kind not in NEW_KINDS:
                return super().fit(F_benign)
            F_benign = np.asarray(F_benign, dtype="float64")
            self._prep_fit(F_benign)                                  # same quantile transform + PCA + scaling
            g = np.random.default_rng(self.seed + 1)
            idx = g.choice(len(F_benign), min(self.m, len(F_benign)), replace=False)
            self.Ztr = self._z(F_benign[idx])                         # same m reference flows as the kernel models
            if self.kind == "lof":
                from sklearn.neighbors import LocalOutlierFactor
                self.model = LocalOutlierFactor(n_neighbors=35, novelty=True).fit(self.Ztr)
            elif self.kind == "mahal":
                from sklearn.covariance import LedoitWolf
                self.model = LedoitWolf().fit(self.Ztr)
            else:                                                     # autoencoder n -> n/2 -> n
                from sklearn.neural_network import MLPRegressor
                h = max(2, self.n // 2)
                self.model = MLPRegressor(hidden_layer_sizes=(16, h, 16), activation="relu", alpha=1e-4,
                                          max_iter=400, early_stopping=True, random_state=self.seed).fit(self.Ztr, self.Ztr)
            return self

        def novelty(self, F, chunk=10000):
            if self.kind not in NEW_KINDS:
                return super().novelty(F, chunk)
            F = np.asarray(F, dtype="float64")
            out = np.empty(len(F))
            for a in range(0, len(F), chunk):
                Z = self._z(F[a:a + chunk])
                if self.kind == "lof":
                    out[a:a + chunk] = -self.model.score_samples(Z)
                elif self.kind == "mahal":
                    out[a:a + chunk] = self.model.mahalanobis(Z)
                else:
                    out[a:a + chunk] = ((self.model.predict(Z) - Z) ** 2).mean(axis=1)
            return out
    return ExtNovelty


def add_configs(CONFIGS):
    new = {"V3-MAX-IF": dict(max_of=("V3-SUP", "iforest")),
           "V3-MAX-LOF": dict(max_of=("V3-SUP", "lof")),
           "V3-MAX-MAHAL": dict(max_of=("V3-SUP", "mahal")),
           "V3-MAX-AE": dict(max_of=("V3-SUP", "ae")),
           "Q-LOF": dict(novelty_only="lof"), "Q-MAHAL": dict(novelty_only="mahal"), "Q-AE": dict(novelty_only="ae")}
    for k, v in new.items():
        if k in CONFIGS and CONFIGS[k] != v:
            raise SystemExit(f"config {k} already exists with another meaning")
        CONFIGS[k] = v
    return CONFIGS


def compare(out_dir):
    from scipy.stats import wilcoxon
    df = pd.read_csv(os.path.join(out_dir, "v3_results.csv"))
    L = ["NOVELTY-DETECTOR BASELINES (exploratory, post-hoc). R = recall at nominal FPR 1% (threshold B), mean over",
         "attack types, then over seeds. fpr = observed test FPR. Rules are in the header of novelty_baselines_run.py.", ""]
    target = {"known": 0.163, "loo": 0.388}
    verdicts = {}
    for scen in ("known", "loo"):
        s = df[df.scenario == scen]
        if s.empty:
            continue
        L.append(f"==== scenario {scen}")
        ps = s.groupby(["model", "seed"])[["recall1", "fpr_test1", "pauc1"]].mean()
        rec = s[s.type.astype(str).str.contains("Recon", case=False)].groupby(["model", "seed"]).recall1.mean()
        rows = []
        for mdl, g in ps.groupby(level="model"):
            fp = g.fpr_test1.mean()
            rr = rec.loc[mdl].mean() if mdl in rec.index.get_level_values(0) else np.nan
            rows.append(dict(model=mdl, R=g.recall1.mean(), fpr=fp, pauc=g.pauc1.mean(), R_recon=rr,
                             seeds=g.shape[0], valid="yes" if 0.005 <= fp <= 0.02 else "NO"))
        L.append(pd.DataFrame(rows).sort_values("R", ascending=False).round(4).to_string(index=False))
        piv = ps.recall1.unstack(0)
        if "V3-MAX" in piv:
            b = piv["V3-MAX"].mean()
            ok = abs(b - target[scen]) <= 0.005
            L.append(f"  rule 1: V3-MAX R = {b:.3f} (main result {target[scen]:.3f}) -> {'reproduced' if ok else 'NOT reproduced: do not interpret'}")
        for x in FUSED[1:]:
            if x not in piv or "V3-MAX" not in piv:
                continue
            d = (piv[x] - piv["V3-MAX"]).dropna()
            p = wilcoxon(-d, alternative="greater").pvalue if (d != 0).sum() >= 3 else np.nan
            if d.mean() >= -0.02:
                v = "equivalent"
            elif np.isfinite(p) and p < 0.05:
                v = "kernel OCSVM better"
            else:
                v = "inconclusive"
            verdicts.setdefault(x, {})[scen] = v
            sup = (piv[x] - piv["V3-SUP"]).dropna() if "V3-SUP" in piv else pd.Series(dtype=float)
            L.append(f"  {x:13s} D = {d.mean():+.3f} vs V3-MAX (V3-MAX ahead in {(d < 0).sum()}/{len(d)} seeds, p {p:.3f}) -> {v};"
                     f" beats V3-SUP in {(sup > 0).sum()}/{len(sup)} seeds")
        L.append("")
    L.append("Rule 2 verdicts (both scenarios must agree for 'equivalent'):")
    for x, v in verdicts.items():
        both = "equivalent" if all(w == "equivalent" for w in v.values()) and len(v) == 2 else ", ".join(f"{k}: {w}" for k, w in v.items())
        L.append(f"  {x}: {both}")
    txt = "\n".join(L)
    open(os.path.join(out_dir, "novelty_baselines_report.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)
    return txt


def selftest():
    ok = True
    def chk(nm, c):
        nonlocal ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + nm)
    import qkernel
    Ext = make_ext(qkernel.LocalNovelty)
    g = np.random.default_rng(0)
    ben = g.normal(size=(3000, 12))
    att = g.normal(size=(300, 12)) + 3.0
    for kind in ("rbf", "iforest") + NEW_KINDS:
        m = Ext(kind, n_qubits=6, m=600, seed=0).fit(ben[:2000]).set_reference(ben[2000:2600])
        pb = m.percentile(ben[2600:])
        pa = m.percentile(att)
        thr = np.quantile(pb, 0.99)
        chk(f"{kind}: percentiles in [0,1]", ((pb >= 0) & (pb <= 1)).all())
        chk(f"{kind}: shifted anomalies detected (recall {np.mean(pa > thr):.2f} > 0.2)", np.mean(pa > thr) > 0.2)
    o = qkernel.LocalNovelty("rbf", n_qubits=6, m=600, seed=0).fit(ben[:2000]).set_reference(ben[2000:2600])
    e = Ext("rbf", n_qubits=6, m=600, seed=0).fit(ben[:2000]).set_reference(ben[2000:2600])
    chk("original kinds are unchanged (rbf identical to the frozen class)", np.allclose(o.novelty(att), e.novelty(att)))
    C = add_configs({"V3-MAX": dict(max_of=("V3-SUP", "iqp"))})
    chk("configs added", all(k in C for k in ("V3-MAX-LOF", "Q-AE", "V3-MAX-IF")))
    import tempfile
    d = tempfile.mkdtemp(); r = np.random.default_rng(1); rows = []
    for sc, base in (("known", 0.163), ("loo", 0.388)):
        for sd in range(10):
            for mdl, val in (("V3-SUP", 0.02), ("V3-MAX", base), ("V3-MAX-RBF", base - 0.005), ("V3-MAX-IF", base - 0.1),
                             ("V3-MAX-LOF", base), ("V3-MAX-MAHAL", base - 0.03), ("V3-MAX-AE", base)):
                for t in ("Reconnaissance", "Fuzzers"):
                    rows.append(dict(scenario=sc, seed=sd, model=mdl, type=t, recall1=val + r.normal(0, .002),
                                     fpr_test1=0.01, pauc1=0.5))
    pd.DataFrame(rows).to_csv(os.path.join(d, "v3_results.csv"), index=False)
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        txt = compare(d)
    chk("report: rule 1 reproduced", "reproduced" in txt)
    chk("report: LOF equivalent", "V3-MAX-LOF: equivalent" in txt)
    chk("report: IF kernel better", "V3-MAX-IF: known: kernel OCSVM better" in txt)
    print("ALL PASS" if ok else "SOME CHECKS FAILED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="unsw")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--cache", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--out_dir", default="novelty_baselines_unsw")
    ap.add_argument("--configs", default=",".join(DEFAULT_CONFIGS))
    ap.add_argument("--mode", choices=["known", "loo", "both"], default="both")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--compare_only", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a0 = ap.parse_args()
    if a0.selftest:
        return selftest()
    if a0.compare_only:
        return compare(a0.out_dir)
    warnings.filterwarnings("ignore")
    import torch, hashlib
    import hybrid_v3 as V
    import benign_sensitivity as BS
    here = os.path.dirname(os.path.abspath(V.__file__))
    print("code fingerprint:", {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()[:12]
                                for f in ("hybrid_v3.py", "qkernel.py")}, flush=True)
    a = types.SimpleNamespace(protocol="cross", target=a0.target, s17_dir=a0.s17_dir, target_cache=a0.cache,
                              out_dir=a0.out_dir, mode=a0.mode, configs=a0.configs, within_fams=",".join(V.WITHIN_FAMS),
                              seeds=a0.seeds, max_train=30000, val_max=10000, tree_train=100000, epochs=6, patience=2,
                              bs=512, lr=2e-3, lb=0.1, qubits=8, q_m=2000, q_nu=0.1, device="cpu")
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    if a0.smoke:
        a.seeds, a.epochs, a.max_train, a.val_max, a.tree_train, a.q_m, a.qubits = 1, 2, 3000, 1500, 3000, 300, 6
        a.target = "ids2018"
    D = V.make_smoke("cross") if a0.smoke else V.load_data(a)
    orig_ln, orig_bt = V.LocalNovelty, V.build_target
    V.LocalNovelty = make_ext(orig_ln)
    add_configs(V.CONFIGS)
    V.build_target = lambda D_, a_: BS.make_target(D_, a_, "base", V.is_benign, V.CP[a_.target], None)
    os.makedirs(a0.out_dir, exist_ok=True)
    t0 = time.time()
    V.run(D, a, torch.device("cpu"), a0.out_dir)
    print(f"done [{time.time() - t0:.0f}s]", flush=True)
    V.LocalNovelty, V.build_target = orig_ln, orig_bt
    compare(a0.out_dir)


if __name__ == "__main__":
    main()
