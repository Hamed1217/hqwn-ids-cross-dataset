"""
WHERE does the 2017 -> 2018 detection loss come from?  Diagnostic before designing v3 (no model is changed here).
Trees only (HistGB), CPU, about 15-25 minutes.  No torch needed.  Same data and the same benign thirds of 2018 as
hybrid_v2.py / cross_dataset.py (fit / calibration / test), recall at 1% FPR with the threshold from the calibration
third, real FPR measured on the test third.

  A  CEILING inside 2018 (no network change).  2018 labels are used ONLY here, as an upper bound, never for a model:
       A1 known   train on 2018 (fit-third benign + half of every attack type), test the other half
       A2 unseen  the same, but the tested type is removed from training (pure unseen-attack generalisation,
                  same network)
     If A1 is high and A2 is close to the 2017->2018 numbers -> the hard part is UNSEEN attacks (objective/data),
     if A2 is high but 2017->2018 is low -> the hard part is the NETWORK CHANGE (domain shift).
  B  SHIFT between the networks
       B1 benign 2017 vs benign 2018: domain-classifier AUC (0.5 = indistinguishable) + per-feature KS distance
       B2 the SAME attack in the two networks (2017 counterpart vs 2018 type): AUC; ~1.0 means the attack looks
          different in 2018 (other tool/configuration/flow extractor) and no 2017-trained model can be expected
          to recognise it from its signature
  C  STABLE FEATURES  keep only flow features whose BENIGN distribution is similar in both networks (KS < tau,
     computed from benign traffic only = legitimate, the same assumption as threshold B), train on 2017, test on 2018.

  python diagnose_shift.py --smoke
  python diagnose_shift.py --s17_dir "D:/revised model/stage1_pw" --cache18 "D:/revised model/cross_out4/ids2018_sample_v4.npz" --out_dir "D:/revised model/diagnose"
"""
import argparse, json, os, time, warnings
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

COUNTERPART = {"FTP-BruteForce": "FTP-Patator", "SSH-Bruteforce": "SSH-Patator",
               "DoS attacks-GoldenEye": "DoS GoldenEye", "DoS attacks-Slowloris": "DoS slowloris",
               "DoS attacks-Hulk": "DoS Hulk", "DoS attacks-SlowHTTPTest": "DoS Slowhttptest",
               "DDoS attacks-LOIC-HTTP": "DDoS", "DDOS attack-HOIC": None, "DDOS attack-LOIC-UDP": None,
               "Brute Force -Web": "Web Attack - Brute Force", "Brute Force -XSS": "Web Attack - XSS",
               "SQL Injection": "Web Attack - Sql Injection", "Infilteration": "Infiltration", "Bot": "Bot"}


# ------------------------------------------------------------------------------------------------ data
def load(a):
    import joblib
    feats = json.load(open(os.path.join(a.s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    fidx = np.array([feats.index(c) for c in flow])
    z = np.load(os.path.join(a.s17_dir, "splits.npz"), allow_pickle=True)
    q = np.load(os.path.join(a.s17_dir, "seq17.npz"))
    qt = joblib.load(os.path.join(a.s17_dir, "quantile_transformer.joblib"))
    zc = np.load(a.cache18, allow_pickle=True)
    X18raw = pd.DataFrame(zc["X"], columns=list(zc["cols"]))
    full = pd.DataFrame(0.0, index=X18raw.index, columns=feats)
    for c in feats:
        if c in X18raw.columns:
            full[c] = X18raw[c].values
    seq = lambda S: (np.clip(np.asarray(S, dtype="float32"), -8, 8) / 4.0).reshape(len(S), -1)
    return dict(names=flow, Xtr=z["Xtr"][:, fidx].astype("float32"), ytr=z["ytr"].astype(int),
                atr=z["atr"].astype(str), Str=seq(q["Str"]),
                X18=qt.transform(full)[:, fidx].astype("float32"), S18=seq(zc["seq"]), lab18=zc["lab"].astype(str))


def smoke(seed=0):
    rng = np.random.default_rng(seed)
    t17 = ["BENIGN"] * 6000 + sum([[c] * 300 for c in set(v for v in COUNTERPART.values() if v)], [])
    t18 = ["Benign"] * 9000 + sum([[t] * 200 for t in COUNTERPART], [])
    def mk(types, shift):
        X = rng.normal(0, 1, (len(types), 20)).astype("float32"); S = rng.normal(0, .3, (len(types), 48)).astype("float32")
        for k, t in enumerate(sorted(set(types))):
            m = np.array(types) == t
            if t.lower() != "benign":
                X[m, k % 20] += 2.5; S[m, -3] += 1.0
        X[:, :5] += shift
        return X, S
    Xtr, Str = mk(t17, 0.0); X18, S18 = mk(t18, 0.8)
    return dict(names=[f"f{i}" for i in range(20)], Xtr=Xtr, ytr=(np.array(t17) != "BENIGN").astype(int),
                atr=np.array(t17), Str=Str, X18=X18, S18=S18, lab18=np.array(t18))


# ------------------------------------------------------------------------------------------------ helpers
def strat(y, n, seed):
    if n >= len(y):
        return np.arange(len(y))
    try:
        return np.sort(train_test_split(np.arange(len(y)), train_size=n, stratify=y, random_state=seed)[0])
    except ValueError:
        return np.sort(np.random.default_rng(seed).choice(len(y), n, replace=False))


def hgb(X, y, seed):
    return HistGradientBoostingClassifier(max_iter=200, random_state=seed).fit(X, y)


def at_fpr(s_cal, s_bte, s_types, fpr=0.01):
    thr = np.quantile(s_cal, 1 - fpr)
    return {t: float((s > thr).mean()) for t, s in s_types.items()}, float((s_bte > thr).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--cache18", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--out_dir", default="diagnose")
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--train17", type=int, default=100000)
    ap.add_argument("--taus", default="0.05,0.1,0.2,0.3,1.0")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    warnings.filterwarnings("ignore")
    os.makedirs(a.out_dir, exist_ok=True)
    D = smoke() if a.smoke else load(a)
    if a.smoke:
        a.train17 = 3000
    t0 = time.time()
    lab = D["lab18"]
    ben = np.where(lab == "Benign")[0]
    rng = np.random.default_rng(0); rng.shuffle(ben)
    k3 = len(ben) // 3
    fit_b, cal, bte = ben[:k3], ben[k3:2 * k3], ben[2 * k3:]          # identical thirds to hybrid_v2.py
    types = [t for t in pd.Series(lab[lab != "Benign"]).value_counts().index]
    loo_types = [t for t in types if COUNTERPART.get(t)]
    F18 = {"flow": D["X18"], "flow+seq": np.hstack([D["X18"], D["S18"]])}
    out, L = [], []
    say = lambda s: (print(s, flush=True), L.append(s))
    say(f"2017 train {len(D['ytr'])} | 2018 sample {len(lab)} | benign thirds {k3} | types {len(types)}")

    # ---------------------------------------------------------------- A: ceiling inside 2018
    say("\n== A  ceiling INSIDE 2018 (upper bound only; 2018 labels never used for the real models)")
    for seed in range(a.seeds):
        r = np.random.default_rng(100 + seed)
        half = {}
        for t in types:
            idx = np.where(lab == t)[0].copy(); r.shuffle(idx)
            half[t] = (idx[: len(idx) // 2], idx[len(idx) // 2:])
        nb = min(len(fit_b), 100000)
        fb = fit_b[r.choice(len(fit_b), nb, replace=False)] if len(fit_b) > nb else fit_b
        for fs, X in F18.items():
            def train_on(excl):
                atk = np.concatenate([half[t][0] for t in types if t != excl])
                atk = atk[r.choice(len(atk), min(len(atk), 100000), replace=False)] if len(atk) > 100000 else atk
                idx = np.r_[fb, atk]
                return hgb(X[idx], np.r_[np.zeros(len(fb)), np.ones(len(atk))].astype(int), seed)
            m = train_on(None)
            rec, f = at_fpr(m.predict_proba(X[cal])[:, 1], m.predict_proba(X[bte])[:, 1],
                            {t: m.predict_proba(X[half[t][1]])[:, 1] for t in types})
            for t, v in rec.items():
                out.append(dict(part="A1 known-2018", features=fs, seed=seed, type=t, recall=v, fpr_test=f))
            for t in loo_types:                                       # the type itself held out
                m2 = train_on(t)
                rec2, f2 = at_fpr(m2.predict_proba(X[cal])[:, 1], m2.predict_proba(X[bte])[:, 1],
                                  {t: m2.predict_proba(X[half[t][1]])[:, 1]})
                out.append(dict(part="A2 unseen-2018", features=fs, seed=seed, type=t, recall=rec2[t], fpr_test=f2))
        print(f"  A seed {seed} done [{time.time() - t0:.0f}s]", flush=True)

    # ---------------------------------------------------------------- B: shift
    say("\n== B  shift between the networks")
    b17 = np.where(D["ytr"] == 0)[0]
    b17 = b17[np.random.default_rng(0).choice(len(b17), min(len(b17), 50000), replace=False)]
    b18 = fit_b[: min(len(fit_b), 50000)]
    def dom_auc(A, B, seed=0):
        X = np.r_[A, B]; y = np.r_[np.zeros(len(A)), np.ones(len(B))].astype(int)
        i, j = train_test_split(np.arange(len(y)), test_size=0.5, stratify=y, random_state=seed)
        m = hgb(X[i], y[i], seed)
        return roc_auc_score(y[j], m.predict_proba(X[j])[:, 1])
    au_f = dom_auc(D["Xtr"][b17], D["X18"][b18]); au_s = dom_auc(D["Str"][b17], D["S18"][b18])
    say(f"B1 benign 2017 vs benign 2018, domain-classifier AUC: flow features {au_f:.3f} | service-load sequences {au_s:.3f}"
        "   (0.5 = same distribution)")
    ks = pd.DataFrame([dict(feature=n, KS=ks_2samp(D["Xtr"][b17, k], D["X18"][b18, k]).statistic)
                       for k, n in enumerate(D["names"])]).sort_values("KS", ascending=False)
    ks.to_csv(os.path.join(a.out_dir, "benign_ks.csv"), index=False)
    say("   most shifted flow features (benign KS): " + ", ".join(f"{r.feature} {r.KS:.2f}" for r in ks.head(10).itertuples()))
    say(f"   features with KS < 0.1 / 0.2 / 0.3: {(ks.KS < .1).sum()} / {(ks.KS < .2).sum()} / {(ks.KS < .3).sum()} of {len(ks)}")
    rows_b2 = []
    for t in loo_types:
        c = COUNTERPART[t]
        i17 = np.where(D["atr"] == c)[0]; i18 = np.where(lab == t)[0]
        if len(i17) < 20 or len(i18) < 20:
            continue
        n = min(len(i17), len(i18), 20000)
        g = np.random.default_rng(0)
        i17, i18 = g.choice(i17, n, replace=False), g.choice(i18, n, replace=False)
        rows_b2.append(dict(type18=t, counterpart17=c, n=n, AUC_flow=dom_auc(D["Xtr"][i17], D["X18"][i18]),
                            AUC_seq=dom_auc(D["Str"][i17], D["S18"][i18])))
    b2 = pd.DataFrame(rows_b2)
    b2.to_csv(os.path.join(a.out_dir, "same_attack_shift.csv"), index=False)
    say("B2 the SAME attack, 2017 counterpart vs 2018 (AUC; ~1.0 = looks completely different):")
    say(b2.round(3).to_string(index=False))
    print(f"  B done [{time.time() - t0:.0f}s]", flush=True)

    # ---------------------------------------------------------------- C: stable features, 2017 -> 2018
    say("\n== C  2017 -> 2018 with only the benign-stable flow features (HistGB, threshold B)")
    s_types = {t: np.where(lab == t)[0] for t in types}
    for tau in [float(x) for x in a.taus.split(",")]:
        keep = np.array([k for k, n in enumerate(D["names"]) if ks.set_index("feature").loc[n, "KS"] < tau or tau >= 1])
        if len(keep) < 3:
            say(f"  tau {tau}: only {len(keep)} features, skipped"); continue
        for seed in range(a.seeds):
            for held in [None] + sorted({COUNTERPART[t] for t in loo_types}):
                mt = np.ones(len(D["ytr"]), bool) if held is None else D["atr"] != held
                pool = np.where(mt)[0]
                k = pool[strat(D["ytr"][pool], a.train17, seed)]
                m = hgb(D["Xtr"][k][:, keep], D["ytr"][k], seed)
                ev = types if held is None else [t for t in loo_types if COUNTERPART[t] == held]
                rec, f = at_fpr(m.predict_proba(D["X18"][cal][:, keep])[:, 1],
                                m.predict_proba(D["X18"][bte][:, keep])[:, 1],
                                {t: m.predict_proba(D["X18"][s_types[t]][:, keep])[:, 1] for t in ev})
                for t, v in rec.items():
                    out.append(dict(part="C known 17->18" if held is None else "C unseen 17->18",
                                    features=f"KS<{tau}" if tau < 1 else "all", n_feat=len(keep), seed=seed,
                                    type=t, recall=v, fpr_test=f))
        print(f"  C tau {tau} done [{time.time() - t0:.0f}s]", flush=True)

    df = pd.DataFrame(out)
    df.to_csv(os.path.join(a.out_dir, "diagnose_long.csv"), index=False)
    per_seed = df.groupby(["part", "features", "seed"]).agg(recall=("recall", "mean"), fpr=("fpr_test", "mean")).reset_index()
    summ = per_seed.groupby(["part", "features"]).agg(mean=("recall", "mean"), sd=("recall", "std"),
                                                      real_fpr=("fpr", "mean")).round(3)
    say("\n== SUMMARY: mean recall @ 1% FPR over 2018 types (sd over seeds)")
    say(summ.to_string())
    pt = df[df.part.isin(["A1 known-2018", "A2 unseen-2018"]) & (df.features == "flow+seq")]
    pt = pt.groupby(["type", "part"]).recall.mean().unstack()
    c_all = df[(df.part == "C unseen 17->18") & (df.features == "all")].groupby("type").recall.mean().rename("17->18 unseen (trees)")
    say("\n-- per type: inside 2018 (flow+seq) vs 2017->2018 unseen")
    say(pd.concat([pt, c_all], axis=1).round(3).to_string())
    open(os.path.join(a.out_dir, "report.txt"), "w", encoding="utf-8").write("\n".join(L))
    print(f"\nsaved -> {a.out_dir} [{time.time() - t0:.0f}s]")


if __name__ == "__main__":
    main()
