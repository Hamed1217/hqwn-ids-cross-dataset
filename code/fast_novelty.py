"""
Faster IMPLEMENTATION of the novelty channel for one flow at a time - same model, same numbers.
measure_v3.py showed ~45 ms per flow for BOTH the quantum (IQP) and the classical (RBF) novelty score, although the
IQP kernel needs 100x more multiply-adds: the time is per-call overhead of scikit-learn (quantile map, PCA, one-class
SVM), not the kernel. FastNovelty re-implements exactly the same steps in plain numpy from the FITTED objects
(qkernel.LocalNovelty is not changed; its fingerprint stays frozen):
  quantile map (same interpolation, bounds and normal clipping as sklearn's QuantileTransformer) -> PCA projection
  -> standardisation -> kernel against the SUPPORT VECTORS only -> one-class SVM decision (dual coefficients +
  intercept) -> percentile among the reference benign scores (recomputed through the same fast path, so that flows
  with identical features tie exactly as in the original).
The script checks that the outputs are identical to LocalNovelty.percentile on thousands of real target flows and
measures single-flow latency of both implementations. No torch needed.

  python fast_novelty.py --s17_dir "D:/revised model/stage1_pw" --cache "D:/revised model/cross_out4/ids2018_sample_v4.npz" --v3sup_p95 20.261
"""
import argparse, time
import numpy as np
from scipy.special import ndtri

from qkernel import LocalNovelty, novelty_features, IQPMap

BOUNDS_THRESHOLD = 1e-7


class FastNovelty:
    def __init__(self, nv, F_ref):
        qt = nv.qt
        self.q = np.asarray(qt.quantiles_, dtype="float64")            # (n_quantiles, n_features)
        self.ref_q = np.asarray(qt.references_, dtype="float64")
        self.qr = -self.q[::-1]
        self.rr = -self.ref_q[::-1]
        self.clip = (ndtri(BOUNDS_THRESHOLD - np.spacing(1)), ndtri(1 - (BOUNDS_THRESHOLD - np.spacing(1))))
        self.pmean, self.pcomp = nv.pca.mean_, nv.pca.components_
        self.mu, self.sd = nv.mu, nv.sd
        self.kind, self.scale = nv.kind, getattr(nv, "scale", None)
        m = nv.model
        sv = m.support_
        self.coef = m.dual_coef_.ravel()
        self.icpt = float(m.intercept_[0])
        if nv.kind == "rbf":
            self.Zsv = nv.Ztr[sv]
            self.Zsv2 = (self.Zsv * self.Zsv).sum(1)
        else:
            self.map = nv.map
            self.Ssv_c = nv.Str[sv].conj()
        self.ref = np.sort(self.novelty(F_ref))   # reference scores through the SAME code path (exact ties)

    def _qt(self, F):
        X = np.array(F, dtype="float64", copy=True)
        for j in range(X.shape[1]):
            x, qj = X[:, j], self.q[:, j]
            lo = x - BOUNDS_THRESHOLD < qj[0]
            hi = x + BOUNDS_THRESHOLD > qj[-1]
            ok = ~np.isnan(x)
            xf = x[ok]
            x[ok] = 0.5 * (np.interp(xf, qj, self.ref_q) - np.interp(-xf, self.qr[:, j], self.rr))
            x[hi], x[lo] = 1.0, 0.0
            X[:, j] = np.clip(ndtri(x), *self.clip)
        return X

    def novelty(self, F):
        Z = ((self._qt(F) - self.pmean) @ self.pcomp.T - self.mu) / self.sd
        if self.kind == "rbf":
            d = (Z * Z).sum(1)[:, None] + self.Zsv2[None, :] - 2 * Z @ self.Zsv.T
            K = np.exp(-self.scale * np.maximum(d, 0))
        else:
            K = np.abs(self.map.states(self.scale * Z) @ self.Ssv_c.T) ** 2
        return -(K @ self.coef + self.icpt)

    def percentile(self, F):
        return np.searchsorted(self.ref, self.novelty(F), side="right") / len(self.ref)


def lat(fn, n):
    for _ in range(min(50, n // 5 + 1)):
        fn()
    t = np.empty(n)
    for i in range(n):
        t0 = time.perf_counter(); fn(); t[i] = (time.perf_counter() - t0) * 1000
    return np.median(t), np.percentile(t, 95), np.percentile(t, 99)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--cache", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--n_check", type=int, default=5000)
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--v3sup_p95", type=float, default=float("nan"),
                    help="end-to-end p95 of V3-SUP from measure_v3.py (tree + network + sequence), to add the channel")
    a = ap.parse_args()
    from qnoise_check import target_rows
    X, S, lab, nfit, nref, bte = target_rows(a.s17_dir, a.cache)
    g = np.random.default_rng(0)
    rows = g.choice(len(lab), min(a.n_check, len(lab)), replace=False)
    F = novelty_features(X[rows], S[rows])
    print(f"checking on {len(rows)} target flows (benign and attack) of {a.cache}")
    for kind in ("iqp", "rbf"):
        nv = LocalNovelty(kind, n_qubits=8, m=2000, nu=0.1, seed=0)
        Fref = novelty_features(X[nref], S[nref])
        nv.fit(novelty_features(X[nfit], S[nfit])).set_reference(Fref)
        fn = FastNovelty(nv, Fref)
        n_ref, n_fast = nv.novelty(F), fn.novelty(F)
        p_ref, p_fast = nv.percentile(F), fn.percentile(F)
        same = float((p_ref == p_fast).mean())
        print(f"{kind.upper()}: support vectors {len(fn.coef)} of {len(nv.Ztr)} | novelty max |difference| "
              f"{np.abs(n_ref - n_fast).max():.2e} | percentile identical for {same:.2%} of flows "
              f"(max difference {np.abs(p_ref - p_fast).max():.2e})")
        x1 = F[:1]
        s = lat(lambda: nv.percentile(x1), min(300, a.reps))
        f = lat(lambda: fn.percentile(x1), a.reps)
        print(f"   one flow: scikit-learn path median {s[0]:.2f} / p95 {s[1]:.2f} ms | fast path median {f[0]:.3f} / "
              f"p95 {f[1]:.3f} / p99 {f[2]:.3f} ms")
        if np.isfinite(a.v3sup_p95):
            tot = a.v3sup_p95 + f[1]
            print(f"   V3-MAX{'' if kind == 'iqp' else '-RBF'} end-to-end p95 = V3-SUP {a.v3sup_p95:.3f} + channel {f[1]:.3f} = "
                  f"{tot:.3f} ms -> claim < 40 ms {'MET' if tot < 40 else 'NOT met'}")


if __name__ == "__main__":
    main()
