"""
SENSITIVITY of the results to the LOCAL BENIGN CALIBRATION DATA (answer to external review 2, point 4).
Every deployable number in the thesis assumes the operator has a period of clean benign traffic of the new network:
one third fits the novelty model and the alignment, one third sets threshold B, one third measures the real false
alarms. The frozen hybrid_v3.run is called UNCHANGED; only build_target (which rows form the thirds) is replaced.
The TEST benign third and all attack flows stay the same as in the main runs wherever the variant allows, so the
numbers are directly comparable with the main results (same seeds).

Variants (--variants, comma list):
  base        the main split again (sanity check: must reproduce the main results exactly)
  time        thirds in TIME order: fit = earliest third of the benign flows, calibration = middle, test = latest
              (the realistic 'calibrate on the past, run on the future'; needs --times)
  size25      only 25% of the fit and calibration thirds are available (test third unchanged)
  size10      only 10%
  contam1     1% of the fit and of the calibration flows are ATTACK flows the operator did not know about (copies
              of random attack flows of the target, any type, labelled benign in those two thirds only; evaluation rows
              unchanged) -> what if an attack was running during the calibration period
  contam5     5%
Expectations written BEFORE running (2026-10-26): size25/size10 change recall@1% by less than 0.02 and keep the real
false-alarm rate near 1%; time raises the real false-alarm rate above 1% (benign drift) and changes recall by a few
points; contamination hurts V3-MAX (the novelty channel learns the attack as normal) more than the supervised models,
most for the attack types that contaminated the calibration. These are exploratory (not pre-registered tests).

  python benign_sensitivity.py --target unsw --target_cache "D:/revised model/unsw/unsw_sample_v1h.npz" --times "D:/revised model/unsw/unsw_sample_v1h.npz" --out_dir "D:/revised model/sens_unsw" --variants base,time,size25,size10,contam1,contam5 --configs TREE,V3-SUP,V3-MAX --seeds 5
  python benign_sensitivity.py --target ids2018 --target_cache "D:/revised model/cross_out4/ids2018_sample_v4.npz" --times "D:/revised model/cross_out4/ids2018_times_v4.npz" --out_dir "D:/revised model/sens_2018" --configs TREE,V3-SUP,V3-MAX --seeds 5
  python benign_sensitivity.py --selftest
Each variant writes its own folder (v3_results.csv, v3_report.txt); the comparison is in sensitivity_report.txt.
"""
import argparse, os, time, types, warnings
import numpy as np
import pandas as pd


def make_target(D, a, variant, is_benign, cp_table, times=None):
    """index sets as hybrid_v3.build_target (cross protocol) for one variant"""
    X, S, lab = D["XT"], D["ST"], np.asarray(D["labT"]).astype(str)
    rng = np.random.default_rng(0)
    ben = np.where(is_benign(lab))[0]
    rng.shuffle(ben)                                                 # identical to build_target
    k3 = len(ben) // 3
    fitb, cal, bte = ben[:k3], ben[k3:2 * k3], ben[2 * k3:]
    if variant == "time":
        if times is None:
            raise SystemExit("variant 'time' needs --times")
        tb = times[ben]
        o = ben[np.argsort(np.where(np.isfinite(tb), tb, np.inf), kind="stable")]
        fitb, cal, bte = o[:k3], o[k3:2 * k3], o[2 * k3:]
        fitb = fitb[np.random.default_rng(1).permutation(len(fitb))]   # random halves for novelty fit / reference
    elif variant.startswith("size"):
        f = int(variant[4:]) / 100
        fitb, cal = fitb[: max(int(f * len(fitb)), 10)], cal[: max(int(f * len(cal)), 10)]
    elif variant.startswith("contam"):
        f = int(variant[6:]) / 100
        att = np.where(~is_benign(lab))[0]
        g = np.random.default_rng(2)
        cf = g.choice(att, int(round(f * len(fitb))), replace=len(att) < f * len(fitb))
        cc = g.choice(att, int(round(f * len(cal))), replace=len(att) < f * len(cal))
        n0 = len(X)
        X = np.vstack([X, X[cf], X[cc]])                              # appended COPIES; evaluation rows unchanged
        S = np.concatenate([S, S[cf], S[cc]])
        lab = np.r_[lab, np.full(len(cf) + len(cc), "Benign")]
        fitb = np.r_[fitb, np.arange(n0, n0 + len(cf))]
        cal = np.r_[cal, np.arange(n0 + len(cf), n0 + len(cf) + len(cc))]
        fitb, cal = fitb[g.permutation(len(fitb))], cal[g.permutation(len(cal))]
    elif variant != "base":
        raise SystemExit(f"unknown variant {variant}")
    nfit, nref = fitb[: len(fitb) // 2], fitb[len(fitb) // 2:]
    return dict(X=X, S=S, lab=lab, calX=X[cal], calS=S[cal], bteX=X[bte], bteS=S[bte], nfitX=X[nfit], nfitS=S[nfit],
                nrefX=X[nref], nrefS=S[nref], alX=X[fitb], alS=S[fitb], cp=cp_table, cal_i=cal, bte_i=bte, al_i=fitb)


def compare(out_dir, variants):
    from scipy.stats import wilcoxon
    dfs = {v: pd.read_csv(os.path.join(out_dir, v, "v3_results.csv")) for v in variants
           if os.path.exists(os.path.join(out_dir, v, "v3_results.csv"))}
    if "base" not in dfs:
        print("no 'base' variant -> differences cannot be computed; tables only")
    L = ["BENIGN-CALIBRATION SENSITIVITY (exploratory). recall1 = recall@1% (threshold B, mean over attack types),",
         "fpr = real false-alarm rate on the test benign (nominal 1%), pauc1 = partial AUC to 1%. Mean over seeds.", ""]
    for scen in ("known", "loo"):
        tab = []
        for v, df in dfs.items():
            s = df[df.scenario == scen]
            if s.empty:
                continue
            ps = s.groupby(["model", "seed"])[["recall1", "fpr_test1", "pauc1"]].mean()
            for mdl, g in ps.groupby(level="model"):
                row = dict(variant=v, model=mdl, recall1=g.recall1.mean(), fpr=g.fpr_test1.mean(), pauc1=g.pauc1.mean())
                if "base" in dfs and v != "base":
                    b = dfs["base"]
                    b = b[b.scenario == scen].groupby(["model", "seed"]).recall1.mean()
                    if mdl in b.index.get_level_values(0):
                        d = (g.recall1.droplevel(0) - b.loc[mdl].reindex(g.recall1.droplevel(0).index)).dropna()
                        row["d_recall1_vs_base"] = d.mean()
                        row["p_two_sided"] = (wilcoxon(d).pvalue if (d != 0).sum() >= 3 else np.nan)
                tab.append(row)
        if tab:
            t = pd.DataFrame(tab)
            L.append(f"==== scenario {scen}")
            L.append(t.round(4).to_string(index=False))
            if {"V3-MAX", "V3-SUP"} <= set(t.model):
                piv = t.pivot(index="variant", columns="model", values="recall1")
                L.append("V3-MAX - V3-SUP per variant (does the novelty advantage survive?): "
                         + ", ".join(f"{v} {piv.loc[v, 'V3-MAX'] - piv.loc[v, 'V3-SUP']:+.3f}" for v in piv.index))
            L.append("")
    txt = "\n".join(L)
    open(os.path.join(out_dir, "sensitivity_report.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)


def selftest():
    is_benign = lambda lab: np.asarray(lab).astype(str) == "Benign"
    g = np.random.default_rng(0)
    n = 3000
    lab = np.where(g.random(n) < 0.7, "Benign", g.choice(["A", "B"], n))
    D = dict(XT=g.normal(size=(n, 5)).astype("float32"), ST=g.normal(size=(n, 16, 3)).astype("float32"), labT=lab)
    times = g.uniform(0, 1e5, n)
    ok = True
    def check(name, c):
        nonlocal ok
        ok &= bool(c)
        print(("PASS " if c else "FAIL ") + name)
    base = make_target(D, None, "base", is_benign, {})
    ben = np.where(is_benign(lab))[0]; r = np.random.default_rng(0); r.shuffle(ben); k3 = len(ben) // 3
    check("base = the thirds of hybrid_v3.build_target", np.array_equal(base["cal_i"], ben[k3:2 * k3])
          and np.array_equal(base["bte_i"], ben[2 * k3:]) and np.array_equal(base["al_i"], ben[:k3]))
    tm = make_target(D, None, "time", is_benign, {}, times)
    check("time: fit < calibration < test in time", times[tm["al_i"]].max() <= times[tm["cal_i"]].min()
          and times[tm["cal_i"]].max() <= times[tm["bte_i"]].min())
    check("time: all three benign and disjoint", is_benign(lab[np.r_[tm["al_i"], tm["cal_i"], tm["bte_i"]]]).all()
          and len(np.unique(np.r_[tm["al_i"], tm["cal_i"], tm["bte_i"]])) == 3 * k3)
    s10 = make_target(D, None, "size10", is_benign, {})
    check("size10: 10% of fit / calibration, same test third", len(s10["cal_i"]) == int(0.1 * k3)
          and np.array_equal(s10["bte_i"], base["bte_i"]) and set(s10["cal_i"]) <= set(base["cal_i"]))
    c5 = make_target(D, None, "contam5", is_benign, {})
    extra_f = c5["al_i"][c5["al_i"] >= n]; extra_c = c5["cal_i"][c5["cal_i"] >= n]
    check("contam5: 5% attack copies in fit and calibration", len(extra_f) == round(0.05 * k3)
          and len(extra_c) == round(0.05 * k3))
    check("contam5: evaluation rows and test third unchanged",
          np.array_equal(c5["X"][:n], D["XT"]) and (c5["lab"][:n] == lab).all()
          and np.array_equal(c5["bte_i"], base["bte_i"]))
    src = {tuple(np.round(x, 6)) for x in D["XT"][~is_benign(lab)]}
    check("contam5: every copy equals some attack flow", all(tuple(np.round(c5["X"][i], 6)) in src for i in extra_c))
    print("ALL PASS" if ok else "SOME CHECKS FAILED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="unsw")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--target_cache", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--times", default="", help="npz with 'ts' aligned with the target cache (UNSW cache itself; "
                                                "2018: ids2018_times_v4.npz from ts_2018.py)")
    ap.add_argument("--out_dir", default="sens_out")
    ap.add_argument("--variants", default="base,time,size25,size10,contam1,contam5")
    ap.add_argument("--configs", default="TREE,V3-SUP,V3-MAX")
    ap.add_argument("--mode", choices=["known", "loo", "both"], default="both")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--compare_only", action="store_true", help="only rebuild sensitivity_report.txt")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a0 = ap.parse_args()
    if a0.selftest:
        return selftest()
    variants = [v.strip() for v in a0.variants.split(",") if v.strip()]
    if a0.compare_only:
        return compare(a0.out_dir, variants)
    warnings.filterwarnings("ignore")
    import torch
    import hybrid_v3 as V
    a = types.SimpleNamespace(protocol="cross", target=a0.target, s17_dir=a0.s17_dir, target_cache=a0.target_cache,
                              out_dir=a0.out_dir, mode=a0.mode, configs=a0.configs, within_fams=",".join(V.WITHIN_FAMS),
                              seeds=a0.seeds, max_train=30000, val_max=10000, tree_train=100000, epochs=6, patience=2,
                              bs=512, lr=2e-3, lb=0.1, qubits=8, q_m=2000, q_nu=0.1, device="cpu")
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    if a0.smoke:
        a.seeds, a.epochs, a.max_train, a.val_max, a.tree_train, a.q_m, a.qubits = 1, 2, 3000, 1500, 3000, 300, 6
        a.target = "ids2018"
        D = V.make_smoke("cross")
        times = np.random.default_rng(0).uniform(0, 1e5, len(D["labT"]))
    else:
        D = V.load_data(a)
        times = np.asarray(np.load(a0.times, allow_pickle=True)["ts"], "float64") if a0.times else None
        if times is not None and len(times) != len(D["labT"]):
            raise SystemExit("--times does not match the target cache")
    import hashlib
    here = os.path.dirname(os.path.abspath(V.__file__))
    print("code fingerprint:", {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()[:12]
                                for f in ("hybrid_v3.py", "qkernel.py")}, flush=True)
    orig = V.build_target
    for v in variants:
        od = os.path.join(a0.out_dir, v)
        os.makedirs(od, exist_ok=True)
        V.build_target = lambda D_, a_, v=v: make_target(D_, a_, v, V.is_benign, V.CP[a_.target], times)
        t0 = time.time()
        print(f"\n######## variant {v} ########", flush=True)
        V.run(D, a, torch.device("cpu"), od)
        print(f"variant {v} done [{time.time() - t0:.0f}s]", flush=True)
    V.build_target = orig
    compare(a0.out_dir, variants)


if __name__ == "__main__":
    main()
