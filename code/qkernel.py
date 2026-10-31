"""
v3 quantum component: a ONE-CLASS detector of the LOCAL network's normal traffic with a quantum (IQP / ZZ-feature-map)
fidelity kernel, plus the classical controls it is compared with. Numpy only (exact statevector simulation).

Why here: under a fair comparison the only robust quantum signal reported for intrusion detection is a quantum
kernel at low false-alarm rates (Gillani et al. 2026); a one-class model trained on the target network's own benign
traffic also attacks the problem our diagnosis found (network change). The model never sees an attack.

  kind = "iqp"      quantum fidelity kernel  k(x,y) = |<psi(x)|psi(y)>|^2, psi = U_Phi H U_Phi H |0>  (Havlicek et
                    al. 2019; identical to qiskit ZZFeatureMap(reps=2, entanglement="full")), n qubits, 2^n amplitudes
  kind = "rff"      CONTROL: classical random-feature fidelity kernel with the SAME dimension 2^n
  kind = "rbf"      CONTROL: Gaussian kernel
  kind = "iforest"  CONTROL: Isolation Forest
Pipeline (fit on local benign only): quantile -> normal transform, PCA to n components, standardise, one scale
parameter chosen by the SAME rule for every kernel (mean off-diagonal kernel value on the fit set = kappa), then a
one-class SVM (nu fixed in advance). Output: novelty score (higher = less normal) and its percentile among held-out
local benign flows (domain-free scale, used as a feature by the hybrid model).

  python qkernel.py --selftest
  python qkernel.py --noise_check 24      (optional: qiskit + qiskit-aer + qiskit-ibm-runtime; hardware noise model)
"""
import argparse
import numpy as np
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import QuantileTransformer
from sklearn.svm import OneClassSVM


def _zmat(n):
    b = np.arange(2 ** n)[:, None]
    return (1 - 2 * ((b >> np.arange(n)[None, :]) & 1)).astype("float64")          # (2^n, n) eigenvalues of Z_j


def _wht(psi, n):
    """H^{(x)n} applied to a batch of statevectors (B, 2^n)"""
    B = psi.shape[0]
    v = psi.reshape((B,) + (2,) * n)
    for ax in range(1, n + 1):
        a, b = np.take(v, 0, axis=ax), np.take(v, 1, axis=ax)
        v = np.stack([a + b, a - b], axis=ax) / np.sqrt(2.0)
    return v.reshape(B, -1)


class IQPMap:
    def __init__(self, n, reps=2):
        self.n, self.reps, self.N = n, reps, 2 ** n
        self.Z = _zmat(n)
        jk = [(j, k) for j in range(n) for k in range(j + 1, n)]
        self.J, self.K = np.array([p[0] for p in jk]), np.array([p[1] for p in jk])
        self.ZZ = self.Z[:, self.J] * self.Z[:, self.K]

    def states(self, X):
        X = np.asarray(X, dtype="float64")
        ph = X @ self.Z.T + ((np.pi - X[:, self.J]) * (np.pi - X[:, self.K])) @ self.ZZ.T
        e = np.exp(1j * ph)
        psi = np.full((len(X), self.N), 1 / np.sqrt(self.N), dtype="complex128")       # H^n |0>
        for r in range(self.reps):
            psi = e * psi
            if r < self.reps - 1:
                psi = _wht(psi, self.n)
        return psi


class RFFMap:
    """classical control: random Fourier features of the same dimension, used as a 'fidelity' kernel"""
    def __init__(self, n, dim, seed=0):
        g = np.random.default_rng(seed)
        self.W, self.b, self.dim = g.normal(size=(n, dim)), g.uniform(0, 2 * np.pi, dim), dim

    def states(self, X):
        return np.exp(1j * (np.asarray(X) @ self.W + self.b)) / np.sqrt(self.dim)


def fidelity(A, B):
    return np.abs(A @ B.conj().T) ** 2


def rbf(X, Y, gamma):
    d = (X * X).sum(1)[:, None] + (Y * Y).sum(1)[None, :] - 2 * X @ Y.T
    return np.exp(-gamma * np.maximum(d, 0))


class LocalNovelty:
    def __init__(self, kind="iqp", n_qubits=8, m=2000, nu=0.1, kappa=0.3, seed=0):
        self.kind, self.n, self.m, self.nu, self.kappa, self.seed = kind, n_qubits, m, nu, kappa, seed

    # ---------------------------------------------------------------- preprocessing (benign only)
    def _prep_fit(self, F):
        g = np.random.default_rng(self.seed)
        sub = F[g.choice(len(F), min(len(F), 50000), replace=False)]
        self.qt = QuantileTransformer(output_distribution="normal", n_quantiles=min(1000, len(sub)),
                                      subsample=10 ** 9, random_state=self.seed).fit(sub)
        self.pca = PCA(n_components=self.n, random_state=self.seed).fit(self.qt.transform(sub))
        z = self.pca.transform(self.qt.transform(sub))
        self.mu, self.sd = z.mean(0), z.std(0) + 1e-9

    def _z(self, F):
        return (self.pca.transform(self.qt.transform(F)) - self.mu) / self.sd

    def _gram(self, A, B):
        if self.kind == "rbf":
            return rbf(A, B, self.scale)
        return fidelity(self.map.states(self.scale * A), self.map.states(self.scale * B))

    def _choose_scale(self, Z):
        """ONE rule for every kernel: mean off-diagonal kernel value on the fit set = kappa (no attack labels)"""
        S = Z[: min(len(Z), 400)]
        grid = np.geomspace(1e-3, 10, 60)
        best, best_err = grid[0], np.inf
        for s in grid:
            self.scale = s
            K = self._gram(S, S)
            off = (K.sum() - np.trace(K)) / (K.size - len(K))
            if abs(off - self.kappa) < best_err:
                best, best_err = s, abs(off - self.kappa)
        self.scale = best

    def fit(self, F_benign):
        F_benign = np.asarray(F_benign, dtype="float64")
        self._prep_fit(F_benign)
        g = np.random.default_rng(self.seed + 1)
        idx = g.choice(len(F_benign), min(self.m, len(F_benign)), replace=False)
        self.Ztr = self._z(F_benign[idx])
        if self.kind == "iforest":
            self.model = IsolationForest(n_estimators=200, random_state=self.seed).fit(self.Ztr)
            return self
        if self.kind == "iqp":
            self.map = IQPMap(self.n)
        elif self.kind == "rff":
            self.map = RFFMap(self.n, 2 ** self.n, seed=self.seed)
        elif self.kind != "rbf":
            raise ValueError(self.kind)
        self._choose_scale(self.Ztr)
        if self.kind != "rbf":
            self.Str = self.map.states(self.scale * self.Ztr)
        self.model = OneClassSVM(kernel="precomputed", nu=self.nu).fit(self._gram_train())
        return self

    def _gram_train(self):
        return rbf(self.Ztr, self.Ztr, self.scale) if self.kind == "rbf" else fidelity(self.Str, self.Str)

    def novelty(self, F, chunk=10000):
        """higher = less like the local benign traffic"""
        F = np.asarray(F, dtype="float64")
        out = np.empty(len(F))
        for a in range(0, len(F), chunk):
            Z = self._z(F[a:a + chunk])
            if self.kind == "iforest":
                out[a:a + chunk] = -self.model.score_samples(Z)
                continue
            K = rbf(Z, self.Ztr, self.scale) if self.kind == "rbf" else fidelity(self.map.states(self.scale * Z), self.Str)
            out[a:a + chunk] = -self.model.decision_function(K)
        return out

    def set_reference(self, F_ref_benign):
        """held-out local benign flows -> percentile scale"""
        self.ref = np.sort(self.novelty(F_ref_benign))
        return self

    def percentile(self, F=None, nov=None):
        nov = self.novelty(F) if nov is None else nov
        return np.searchsorted(self.ref, nov, side="right") / len(self.ref)


def novelty_features(Xflow, S):
    """flow features + a short summary of the 16-minute service-load sequence (last minute, max over the window)"""
    S = np.asarray(S, dtype="float64")
    return np.hstack([np.asarray(Xflow, dtype="float64"), S[:, -1, :], S.max(axis=1)])


# ------------------------------------------------------------------------------------------- checks
def selftest():
    ok = True
    def check(name, cond, info=""):
        nonlocal ok
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + name, info)
    n = 4
    mp = IQPMap(n)
    X = np.random.default_rng(0).uniform(0, np.pi, (5, n))
    S = mp.states(X)
    check("IQP states normalised", np.allclose((np.abs(S) ** 2).sum(1), 1))
    # brute-force unitary construction (dense matrices)
    H1 = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    Hn = H1
    for _ in range(n - 1):
        Hn = np.kron(Hn, H1)
    def brute(x):
        ph = mp.Z @ x + mp.ZZ @ ((np.pi - x[mp.J]) * (np.pi - x[mp.K]))
        U = np.diag(np.exp(1j * ph))
        v = np.zeros(2 ** n, complex); v[0] = 1
        return U @ Hn @ U @ Hn @ v
    B = np.array([brute(x) for x in X])
    check("IQP equals brute-force U H U H |0>", np.allclose(np.abs(B.conj() @ S.T) ** 2, fidelity(B, S)) and
          np.allclose(fidelity(B, B), fidelity(S, S)))
    K = fidelity(S, S)
    check("kernel symmetric, diag = 1, in [0,1]", np.allclose(K, K.T) and np.allclose(np.diag(K), 1) and K.min() >= -1e-12)
    check("kernel positive semidefinite", np.linalg.eigvalsh(K).min() > -1e-9)
    g = np.random.default_rng(1)
    ben = g.normal(size=(3000, 12))
    att = g.normal(size=(500, 12)) + np.r_[3.0, -3.0, np.zeros(10)]
    for kind in ("iqp", "rff", "rbf", "iforest"):
        ln = LocalNovelty(kind, n_qubits=6, m=600, seed=0).fit(ben[:2000]).set_reference(ben[2000:2600])
        pb, pa = ln.percentile(ben[2600:]), ln.percentile(att)
        thr = np.quantile(pb, 0.99)
        rec = (pa > thr).mean()
        extra = f"(scale {getattr(ln, 'scale', float('nan')):.3g}, recall@1%FPR {rec:.2f})"
        check(f"{kind}: shifted anomalies detected (better than chance 0.01)", rec > 0.2, extra)
        check(f"{kind}: benign percentiles ~ uniform", abs(pb.mean() - 0.5) < 0.08, f"(mean {pb.mean():.2f})")
    print("ALL PASS" if ok else "SOME CHECKS FAILED")
    return ok


def noise_check(n_points=24, n_qubits=8, shots=4000, seed=0):
    """compare the exact kernel with the same circuits executed on a simulator carrying the noise model of a real IBM
    processor (fake backend, no account needed). Reports mean |K_noisy - K_exact|."""
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit.circuit.library import ZZFeatureMap
        from qiskit_aer import AerSimulator
        from qiskit_ibm_runtime.fake_provider import FakeBrisbane
    except ImportError as e:
        print("needs: pip install qiskit qiskit-aer qiskit-ibm-runtime   (", e, ")")
        return
    g = np.random.default_rng(seed)
    X = g.normal(size=(n_points, n_qubits)) * 0.5
    exact = fidelity(IQPMap(n_qubits).states(X), IQPMap(n_qubits).states(X))
    fm = ZZFeatureMap(n_qubits, reps=2, entanglement="full")
    sim = AerSimulator.from_backend(FakeBrisbane())
    circs, pairs = [], []
    for i in range(n_points):
        for j in range(i + 1, n_points):
            qc = QuantumCircuit(n_qubits)
            qc.compose(fm.assign_parameters(X[i]), inplace=True)
            qc.compose(fm.assign_parameters(X[j]).inverse(), inplace=True)
            qc.measure_all()
            circs.append(qc); pairs.append((i, j))
    res = sim.run(transpile(circs, sim, optimization_level=1, seed_transpiler=seed), shots=shots).result()
    noisy = np.eye(n_points)
    for c, (i, j) in enumerate(pairs):
        p0 = res.get_counts(c).get("0" * n_qubits, 0) / shots
        noisy[i, j] = noisy[j, i] = p0
    iu = np.triu_indices(n_points, 1)
    err = np.abs(noisy[iu] - exact[iu])
    corr = np.corrcoef(noisy[iu], exact[iu])[0, 1]
    print(f"hardware-noise kernel vs exact ({n_points} points, {len(pairs)} circuits, {n_qubits} qubits): "
          f"mean |error| {err.mean():.3f}, max {err.max():.3f}, correlation {corr:.3f}")
    return err.mean(), corr


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--noise_check", type=int, default=0)
    a = ap.parse_args()
    if a.noise_check:
        noise_check(a.noise_check)
    else:
        raise SystemExit(0 if selftest() else 1)
