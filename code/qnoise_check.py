"""
Would REAL quantum hardware have changed the quantum channel's result? Runs the model's own IQP kernel (8 qubits,
ZZ feature map, reps 2, full entanglement) as circuits and compares three versions of the SAME kernel on REAL flows of
the target network:
  exact   : our state-vector simulation (what every experiment used)
  shots   : ideal quantum computer, finite measurements (--shots), no gate noise
  noisy   : simulator carrying the noise model of a real 127-qubit IBM processor (fake backend; no IBM account needed)
Steps:
  0. convention check: the Qiskit circuit (exact state vector) must give the same kernel as our numpy code
  1. kernel error and correlation of 'shots' and 'noisy' versus 'exact', and kernel concentration (spread of values)
  2. a reduced one-class detector (--m_ref local benign reference flows, nu 0.1) built from each kernel version:
     AUC for target test-benign vs attack flows (classical RBF on the same flows for reference)
  3. hardware cost: two-qubit gates and depth after compiling to the device, time per scored flow with the full model
Input = exactly what the novelty channel sees: hybrid_v3's target thirds (seed 0), the same LocalNovelty preprocessing
(quantile map, PCA to 8, standardisation, bandwidth by the kappa rule) fitted on the 'fit' benign of the target.
No torch needed.

  pip install qiskit qiskit-aer qiskit-ibm-runtime
  python qnoise_check.py --s17_dir "D:/revised model/stage1_pw" --cache "D:/revised model/unsw/unsw_sample_v1h.npz"
  (defaults: 24 reference + 24 benign + 24 attack flows -> 1,428 circuits; about 10-40 min on a laptop / Colab)
"""
import argparse, json, os, time
import numpy as np
import pandas as pd

from qkernel import IQPMap, LocalNovelty, fidelity, novelty_features, rbf


def target_rows(s17_dir, cache):
    """same transformation and benign thirds as hybrid_v3.load_data / build_target (cross protocol)"""
    import joblib
    feats = json.load(open(os.path.join(s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    fidx = np.array([feats.index(c) for c in flow])
    qt = joblib.load(os.path.join(s17_dir, "quantile_transformer.joblib"))
    zc = np.load(cache, allow_pickle=True)
    raw = pd.DataFrame(zc["X"], columns=list(zc["cols"]))
    full = pd.DataFrame(0.0, index=raw.index, columns=feats)
    for c in feats:
        if c in raw.columns:
            full[c] = raw[c].values
    X = qt.transform(full)[:, fidx].astype("float32")
    S = np.clip(np.asarray(zc["seq"], dtype="float32"), -8, 8) / 4.0          # hybrid_v2.prep_seq
    lab = zc["lab"].astype(str)
    ben = np.where(pd.Series(lab).str.strip().str.lower().eq("benign").values)[0]
    np.random.default_rng(0).shuffle(ben)
    k3 = len(ben) // 3
    fitb, bte = ben[:k3], ben[2 * k3:]
    return X, S, lab, fitb[: len(fitb) // 2], fitb[len(fitb) // 2:], bte


def feature_map(n):
    try:
        from qiskit.circuit.library import zz_feature_map
        return zz_feature_map(n, reps=2, entanglement="full")
    except ImportError:
        from qiskit.circuit.library import ZZFeatureMap
        return ZZFeatureMap(n, reps=2, entanglement="full")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--cache", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--m_ref", type=int, default=24)
    ap.add_argument("--n_test", type=int, default=24, help="benign and attack test flows (each)")
    ap.add_argument("--shots", type=int, default=2000)
    ap.add_argument("--backend", default="FakeBrisbane")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rate", type=float, default=4000, help="assumed shots per second of a real device")
    a = ap.parse_args()
    t0 = time.time()
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Statevector
    from qiskit_aer import AerSimulator
    from sklearn.svm import OneClassSVM
    from sklearn.metrics import roc_auc_score

    X, S, lab, nfit, nref, bte = target_rows(a.s17_dir, a.cache)
    nv = LocalNovelty("iqp", n_qubits=8, m=2000, nu=0.1, seed=0)
    nv.fit(novelty_features(X[nfit], S[nfit])).set_reference(novelty_features(X[nref], S[nref]))
    nv_rbf = LocalNovelty("rbf", n_qubits=8, m=2000, nu=0.1, seed=0).fit(novelty_features(X[nfit], S[nfit]))
    print(f"novelty model fitted as in the runs (8 qubits, m 2000, bandwidth {nv.scale:.4g}) [{time.time() - t0:.0f}s]")
    g = np.random.default_rng(a.seed)
    att = np.where(~pd.Series(lab).str.lower().eq("benign").values)[0]
    t_att = g.choice(att, a.n_test, replace=False)
    t_ben = g.choice(bte, a.n_test, replace=False)
    Zref = nv.Ztr[g.choice(len(nv.Ztr), a.m_ref, replace=False)]
    Ztest = nv._z(novelty_features(X[np.r_[t_ben, t_att]], S[np.r_[t_ben, t_att]]))
    ytest = np.r_[np.zeros(a.n_test), np.ones(a.n_test)]
    pts = nv.scale * np.vstack([Zref, Ztest])                          # circuit parameters = what the model uses
    n_all = len(pts)
    # ---- 0. exact kernel (numpy, ours) and Qiskit state vector of the same circuits
    mp = IQPMap(8)
    K_exact = fidelity(mp.states(pts), mp.states(pts))
    fm = feature_map(8)
    sv = np.array([Statevector(fm.assign_parameters(p)).data for p in pts])
    K_qsv = np.abs(sv.conj() @ sv.T) ** 2
    conv = float(np.abs(K_qsv - K_exact).max())
    print(f"0. convention check, Qiskit circuit vs our numpy kernel: max difference {conv:.2e} "
          + ("-> SAME kernel" if conv < 1e-8 else "-> DIFFERENT (stop: results below would not be about our kernel)"))
    # ---- circuits for all pairs needed: reference x reference (upper) and test x reference
    pairs = [(i, j) for i in range(a.m_ref) for j in range(i + 1, a.m_ref)]
    pairs += [(a.m_ref + t, j) for t in range(2 * a.n_test) for j in range(a.m_ref)]
    def circ(i, j):
        qc = QuantumCircuit(8)
        qc.compose(fm.assign_parameters(pts[i]), inplace=True)
        qc.compose(fm.assign_parameters(pts[j]).inverse(), inplace=True)
        qc.measure_all()
        return qc
    circs = [circ(i, j) for i, j in pairs]
    try:
        import qiskit_ibm_runtime.fake_provider as fp
        backend = getattr(fp, a.backend)()
        dev_name = a.backend + " (calibration snapshot of the real IBM device)"
    except ImportError:
        from qiskit.providers.fake_provider import GenericBackendV2
        backend = GenericBackendV2(num_qubits=27, seed=a.seed)
        dev_name = "GenericBackendV2 27 qubits (generic noise; qiskit-ibm-runtime not installed)"
        a.backend = "GenericBackendV2"
    print(f"noise model: {dev_name}")
    sims = {"shots": AerSimulator(seed_simulator=a.seed), "noisy": AerSimulator.from_backend(backend, seed_simulator=a.seed)}
    tc_dev = transpile(circs[:20], backend=backend, optimization_level=1, seed_transpiler=a.seed)
    two_q = np.mean([sum(v for k, v in c.count_ops().items() if k in ("cx", "ecr", "cz")) for c in tc_dev])
    depth = np.mean([c.depth() for c in tc_dev])
    print(f"{len(circs)} circuits | compiled for {a.backend}: {two_q:.0f} two-qubit gates, depth {depth:.0f} per kernel value")
    K = {}
    for name, sim in sims.items():
        Kn = np.eye(n_all)
        t1 = time.time()
        for b in range(0, len(circs), 200):
            tc = transpile(circs[b:b + 200], sim if name == "shots" else backend, optimization_level=1,
                           seed_transpiler=a.seed)
            res = sim.run(tc, shots=a.shots).result()
            for c, (i, j) in enumerate(pairs[b:b + 200]):
                Kn[i, j] = Kn[j, i] = res.get_counts(c).get("0" * 8, 0) / a.shots
            done = min(b + 200, len(circs))
            el = time.time() - t1
            print(f"   {name}: {done}/{len(circs)} circuits [{el:.0f}s, ~{el / done * (len(circs) - done):.0f}s left]", flush=True)
        K[name] = Kn
    # ---- 1. kernel agreement
    sel = np.zeros((n_all, n_all), bool)
    for i, j in pairs:
        sel[i, j] = True
    ex = K_exact[sel]
    L = [f"QUANTUM-HARDWARE CHECK on {os.path.basename(a.cache)}: {a.m_ref} reference + {a.n_test} benign + {a.n_test} "
         f"attack flows, {a.shots} shots, backend {a.backend}", "",
         f"0. Qiskit circuit = our kernel: max difference {conv:.2e}",
         f"   exact kernel values (off-diagonal): mean {ex.mean():.3f}, sd {ex.std():.3f}"]
    for name in ("shots", "noisy"):
        v = K[name][sel]
        L.append(f"1. {name:6s}: mean |error| {np.abs(v - ex).mean():.4f}, max {np.abs(v - ex).max():.3f}, correlation "
                 f"{np.corrcoef(v, ex)[0, 1]:.3f}, values mean {v.mean():.3f} sd {v.std():.3f}")
    # ---- 2. reduced one-class detector from each kernel
    r, t = slice(0, a.m_ref), slice(a.m_ref, n_all)
    def auc_of(Kmat):
        m = OneClassSVM(kernel="precomputed", nu=0.1).fit(Kmat[r, r])
        return roc_auc_score(ytest, -m.decision_function(Kmat[t, r]))
    Zall = np.vstack([Zref, Ztest])                                   # same preprocessing for both kernels
    Kr = rbf(Zall, Zall, nv_rbf.scale)                                # classical kernel, bandwidth by the same rule
    L.append("")
    L.append(f"2. reduced detector ({a.m_ref} reference flows), AUC benign vs attack on the same {2 * a.n_test} test flows:")
    for name, Km in (("exact (our simulation)", K_exact), ("ideal QC, finite shots", K["shots"]),
                     ("noisy IBM hardware model", K["noisy"]), ("classical RBF (reference)", Kr)):
        L.append(f"   {name:28s} AUC {auc_of(Km):.3f}")
    full_auc = roc_auc_score(ytest, nv.novelty(novelty_features(X[np.r_[t_ben, t_att]], S[np.r_[t_ben, t_att]])))
    L.append(f"   full model as in the runs (2,000 reference flows, exact) AUC {full_auc:.3f}")
    # ---- 3. hardware cost of the full model
    per_flow = 2000 * a.shots / a.rate
    L += ["", f"3. cost on a real device: each kernel value = 1 circuit ({two_q:.0f} two-qubit gates, depth {depth:.0f}) x "
          f"{a.shots} shots; one flow needs 2,000 kernel values -> {2000 * a.shots:,} shots ~ {per_flow:,.0f} s per flow "
          f"at {a.rate:,.0f} shots/s (budget 0.040 s)",
          "", f"time {time.time() - t0:.0f}s"]
    out = os.path.join(os.path.dirname(os.path.abspath(a.cache)), "qnoise_report.txt")
    open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L) + f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
