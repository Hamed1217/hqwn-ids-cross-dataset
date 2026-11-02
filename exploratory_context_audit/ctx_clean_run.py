"""
EXPLORATORY test of the temporal-context objection (reviewer request): does the gain of the benign-reference novelty
channel (V3-MAX) on CIC-UNSW-NB15 survive when attack flows cannot influence (a) the service-load context or (b) the
benign flows used for fitting, calibrating and testing? The frozen hybrid_v3.run is called UNCHANGED; only the cache
(sequences) and build_target (which benign flows form the thirds) are replaced, exactly as in benign_sensitivity.py.
The confirmatory test was run once on 2026-10-25; nothing here is confirmatory and the result is reported as exploratory.

Variants (the novelty model is refitted, the threshold B and the percentile scale are recalibrated, and the target
alignment is redone inside hybrid_v3.run in every variant):
  base          original cache, usual benign thirds            (must reproduce the main results; sanity check)
  orig_win      original cache, benign flows restricted to those with NO sampled attack flow in their 16-minute window
                (fit, calibration and test thirds are all attack-free-window flows)
  ctx_clean     cache with sequences from a benign-only service-load table, usual thirds
  ctx_clean_win both: benign-only sequences AND attack-free-window thirds
Attack flows keep all their own features; only the benign set and the context change. 'Window' = the 16 minutes ending at
the flow's minute, whole capture session (the definition of the S7 audit, based on the sampled flows).

Expectations written BEFORE running (2026-11-01): (1) base reproduces the main V3-MAX 0.163 / 0.388; (2) V3-MAX stays
above V3-SUP in ctx_clean and ctx_clean_win, but its recall may drop by a few points (we do not predict the size); (3) if
V3-MAX falls to the level of V3-SUP the gain was carried by attack-induced context; (4) the restricted variants have fewer
benign flows and may change the real false-alarm rate. Decision rule fixed in advance: the gain 'survives' if V3-MAX minus
V3-SUP stays positive in at least 8 of 10 seeds in ctx_clean_win; otherwise it is reported as not surviving.

  python ctx_clean_run.py --cache "D:/revised model/unsw/unsw_sample_v1h.npz" ^
     --cache_clean "D:/revised model/unsw/unsw_sample_v1h_ctxclean.npz" --out_dir "D:/revised model/ctx_clean_unsw" --seeds 3
  (pilot with --seeds 3, then --seeds 10)   |   python ctx_clean_run.py --selftest   |   --smoke
"""
import argparse, os, time, types, warnings
import numpy as np
import pandas as pd
import benign_sensitivity as BS

WINDOW = 16


def window_flags(group, minute, is_att, valid, w):
    group = np.asarray(group, "int64"); minute = np.asarray(minute, "int64"); ok = np.asarray(valid, bool)
    out = np.zeros(len(minute), bool)
    if not ok.any():
        return out
    big = int(minute[ok].max()) + w + 10
    a = ok & np.asarray(is_att, bool)
    codes = np.unique(group[a] * big + minute[a])
    if len(codes) == 0:
        return out
    hi = group * big + minute
    idx = np.searchsorted(codes, hi - (w - 1), side="left")
    found = codes[np.minimum(idx, len(codes) - 1)]
    return (idx < len(codes)) & (found <= hi) & ok


def attack_window_flag(lab, ts, sess, is_benign):
    valid = np.isfinite(ts) & (sess >= 0)
    m_abs = np.where(valid, np.floor(np.where(valid, ts, 0) / 60), 0).astype("int64")
    smin = pd.Series(m_abs[valid]).groupby(sess[valid]).min()
    rel = np.zeros(len(ts), "int64")
    rel[valid] = m_abs[valid] - smin.reindex(sess[valid]).values
    return window_flags(sess, rel, ~is_benign(lab), valid, WINDOW), valid


def make_target_win(D, a, is_benign, cp_table, att_in_window, valid):
    """as benign_sensitivity.make_target('base') but only benign flows with a valid time and no attack in the window"""
    X, S, lab = D["XT"], D["ST"], np.asarray(D["labT"]).astype(str)
    rng = np.random.default_rng(0)
    ben = np.where(is_benign(lab) & valid & ~att_in_window)[0]
    rng.shuffle(ben)
    k3 = len(ben) // 3
    fitb, cal, bte = ben[:k3], ben[k3:2 * k3], ben[2 * k3:]
    nfit, nref = fitb[: len(fitb) // 2], fitb[len(fitb) // 2:]
    return dict(X=X, S=S, lab=lab, calX=X[cal], calS=S[cal], bteX=X[bte], bteS=S[bte], nfitX=X[nfit], nfitS=S[nfit],
                nrefX=X[nref], nrefS=S[nref], alX=X[fitb], alS=S[fitb], cp=cp_table, cal_i=cal, bte_i=bte, al_i=fitb)


def selftest():
    g = np.random.default_rng(0)
    n = 4000
    lab = np.where(g.random(n) < 0.97, "Benign", g.choice(["A", "B"], n))
    ts = np.sort(g.uniform(0, 3600 * 24, n)); sess = np.zeros(n, int)
    is_b = lambda l: np.asarray(l).astype(str) == "Benign"
    f, v = attack_window_flag(lab, ts, sess, is_b)
    ok = True
    def chk(nm, c):
        nonlocal ok; ok &= bool(c); print(("PASS " if c else "FAIL ") + nm)
    mn = np.floor(ts / 60).astype(int); mn -= mn.min()
    att_min = set(mn[lab != "Benign"])
    brute = np.array([any((mn[i] - k) in att_min for k in range(WINDOW)) for i in range(n)])
    chk("window flag equals brute force", (brute == f).all())
    chk("some but not all benign flows have an attack in the window", 0 < f[is_b(lab)].mean() < 1)
    D = dict(XT=g.normal(size=(n, 5)).astype("float32"), ST=g.normal(size=(n, 16, 3)).astype("float32"), labT=lab)
    t = make_target_win(D, None, is_b, {}, f, v)
    allb = np.r_[t["al_i"], t["cal_i"], t["bte_i"]]
    chk("restricted thirds: benign, attack-free window, disjoint",
        is_b(lab[allb]).all() and (~f[allb]).all() and len(np.unique(allb)) == len(allb))
    base = BS.make_target(D, None, "base", is_b, {})
    chk("base thirds from benign_sensitivity (unchanged)", len(base["cal_i"]) > 0)
    print("ALL PASS" if ok else "SOME CHECKS FAILED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="unsw")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--cache", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--cache_clean", default="D:/revised model/unsw/unsw_sample_v1h_ctxclean.npz")
    ap.add_argument("--out_dir", default="ctx_clean_unsw")
    ap.add_argument("--variants", default="base,orig_win,ctx_clean,ctx_clean_win")
    ap.add_argument("--configs", default="TREE,V3-SUP,V3-MAX")
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
        return BS.compare(a0.out_dir, variants)
    warnings.filterwarnings("ignore")
    import torch
    import hybrid_v3 as V
    a = types.SimpleNamespace(protocol="cross", target=a0.target, s17_dir=a0.s17_dir, target_cache=a0.cache,
                              out_dir=a0.out_dir, mode=a0.mode, configs=a0.configs, within_fams=",".join(V.WITHIN_FAMS),
                              seeds=a0.seeds, max_train=30000, val_max=10000, tree_train=100000, epochs=6, patience=2,
                              bs=512, lr=2e-3, lb=0.1, qubits=8, q_m=2000, q_nu=0.1, device="cpu")
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    if a0.smoke:
        a.seeds, a.epochs, a.max_train, a.val_max, a.tree_train, a.q_m, a.qubits = 1, 2, 3000, 1500, 3000, 300, 6
        a.target = "ids2018"
    import hashlib
    here = os.path.dirname(os.path.abspath(V.__file__))
    print("code fingerprint:", {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()[:12]
                                for f in ("hybrid_v3.py", "qkernel.py")}, flush=True)
    if a0.smoke:
        ts = sess = None
    else:
        z = np.load(a0.cache, allow_pickle=True)
        ts, sess = np.asarray(z["ts"], float), np.asarray(z["session"]).astype("int64")
    orig = V.build_target
    cache_of = {"base": a0.cache, "orig_win": a0.cache, "ctx_clean": a0.cache_clean, "ctx_clean_win": a0.cache_clean}
    Dcache = {}
    for v in variants:
        od = os.path.join(a0.out_dir, v)
        os.makedirs(od, exist_ok=True)
        a.target_cache = cache_of[v]
        if a.target_cache not in Dcache:
            Dcache[a.target_cache] = V.make_smoke("cross") if a0.smoke else V.load_data(a)
        D = Dcache[a.target_cache]
        if not a0.smoke and len(D["labT"]) != len(ts):
            raise SystemExit("cache length differs from the original cache")
        if v.endswith("_win"):
            labT = np.asarray(D["labT"]).astype(str)
            if a0.smoke:
                f, val = np.zeros(len(labT), bool), np.ones(len(labT), bool)
            else:
                f, val = attack_window_flag(labT, ts, sess, V.is_benign)
            print(f"{v}: {int(((~f) & val & V.is_benign(labT)).sum()):,} benign flows with an attack-free window", flush=True)
            V.build_target = lambda D_, a_, f=f, val=val: make_target_win(D_, a_, V.is_benign, V.CP[a_.target], f, val)
        else:
            V.build_target = lambda D_, a_: BS.make_target(D_, a_, "base", V.is_benign, V.CP[a_.target], None)
        t0 = time.time()
        print(f"\n######## variant {v} ########", flush=True)
        V.run(D, a, torch.device("cpu"), od)
        print(f"variant {v} done [{time.time() - t0:.0f}s]", flush=True)
    V.build_target = orig
    BS.compare(a0.out_dir, variants)


if __name__ == "__main__":
    main()
