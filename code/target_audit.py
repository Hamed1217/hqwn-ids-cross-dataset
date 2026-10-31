"""
Two data audits requested by the second review (Sections 3.2.3 and 3.1.3 of the paper). No model is trained, no cache
is changed, and the confirmatory test is NOT re-run: everything is computed from existing files.

context    (review point 1) The benign flows of a target sample are split into the same thirds as hybrid_v3
           (reference = alignment / novelty fit, calibration, test; seed 0, identical code). For each part: the share
           of flows whose 16-minute window [t-15, t] contains at least one ATTACK flow of the same capture session
           (network level) and, where the destination port is stored (CIC-UNSW-NB15), of the same service (service
           level). Attack minutes come from the attack flows of the SAMPLE, so these shares are LOWER bounds.
           With --scores_dir (dump_scores output): threshold-only sensitivity on the saved scores. Threshold B is
           recomputed from the calibration flows whose window has no attack flow ("clean"); recall and test FPR are
           reported at both thresholds, with the main paired comparisons under the clean threshold. The novelty
           channel and the alignment are NOT refitted (that would need a new run).
conflicts  (review point 4, CIC-UNSW-NB15) Rebuilds the seed-0 sample exactly as prep_unsw.py (same draw, same
           cleaning), checks that the kept rows equal the cache row by row, and reports which labels the removed
           conflicting rows had and how each model's recall could change had they been kept (bounds: none / all of
           them detected). Also counts the label conflicts that the harmonisation created in the primary cache
           (those rows are IN the evaluation and cannot be separated by flow features).

Run (PowerShell, from D:/revised model; prep_unsw.py must be in the same folder for 'conflicts'):
  python target_audit.py --selftest
  python target_audit.py context --label unsw --cache "D:/revised model/unsw/unsw_sample_v1h.npz" --scores_dir "D:/revised model/unsw_primary" --out_dir "D:/revised model/audit_target"
  python target_audit.py context --label ids2018 --cache "D:/revised model/cross_out4/ids2018_sample_v4.npz" --times "D:/revised model/cross_out4/ids2018_times_v4.npz" --scores_dir "D:/revised model/scores_cross" --out_dir "D:/revised model/audit_target"
  python target_audit.py conflicts --csv "D:/revised model/CIC-UNSW-NB15/CICFlowMeter_out.csv" --raw_cache "D:/revised model/unsw/unsw_sample_v1.npz" --primary_cache "D:/revised model/unsw/unsw_sample_v1h.npz" --results "D:/revised model/unsw_primary/v3_results.csv" --out_dir "D:/revised model/audit_target"
Outputs in --out_dir: context_<label>.txt / .csv, threshold_clean_<label>_*.csv, conflicts_unsw.txt / .csv
"""
import argparse, glob, json, os, re, sys, time
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

WINDOW = 16                      # minutes t-15 .. t, as the service-load sequence
PAIRS = [("V3-MAX", "V3-SUP"), ("V3-MAX", "TREE"), ("V3-SUP", "TREE"), ("V3-MAX", "V3-MAX-RBF")]


# ============================================================================ shared helpers
def is_benign(lab):
    """identical to hybrid_v3.is_benign"""
    return pd.Series(np.asarray(lab).astype(str)).str.strip().str.lower().isin(["benign"]).values


def thirds(lab):
    """identical to hybrid_v3.build_target (protocol cross): benign thirds with numpy rng seed 0"""
    rng = np.random.default_rng(0)
    ben = np.where(is_benign(lab))[0]
    rng.shuffle(ben)
    k3 = len(ben) // 3
    fitb, cal, bte = ben[:k3], ben[k3:2 * k3], ben[2 * k3:]
    nfit, nref = fitb[: len(fitb) // 2], fitb[len(fitb) // 2:]
    return dict(fit=nfit, ref=nref, cal=cal, test=bte, reference_all=fitb)


def window_flags(group, minute, is_att, valid, w):
    """True where an attack row of the same group has a minute in [m - w + 1, m] (m = the row's own minute)"""
    group = np.asarray(group, "int64")
    minute = np.asarray(minute, "int64")
    ok = np.asarray(valid, bool)
    out = np.zeros(len(minute), bool)
    if not ok.any():
        return out
    big = int(minute[ok].max()) + w + 10
    a = ok & np.asarray(is_att, bool)
    codes = np.unique(group[a] * big + minute[a])
    if len(codes) == 0:
        return out
    hi = group * big + minute
    lo = hi - (w - 1)
    idx = np.searchsorted(codes, lo, side="left")
    found = codes[np.minimum(idx, len(codes) - 1)]
    out = (idx < len(codes)) & (found <= hi) & ok
    return out


def wil(x):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    return float(wilcoxon(x, alternative="greater").pvalue) if (x != 0).sum() >= 3 else np.nan


# ============================================================================ context
def load_target(cache, times):
    z = np.load(cache, allow_pickle=True)
    lab = z["lab"].astype(str)
    if times:
        t = np.load(times, allow_pickle=True)
        ts, sess = np.asarray(t["ts"], float), np.asarray(t["session"])
    elif "ts" in z.files:
        ts = np.asarray(z["ts"], float)
        sess = np.asarray(z["session"]) if "session" in z.files else np.zeros(len(lab), int)
    else:
        raise SystemExit(f"{cache} has no 'ts': give --times (2018: ids2018_times_v4.npz from ts_2018.py)")
    if len(ts) != len(lab) or len(sess) != len(lab):
        raise SystemExit(f"length mismatch: lab {len(lab)}, ts {len(ts)}, session {len(sess)}")
    dport = np.asarray(z["dport"], float) if "dport" in z.files else None
    return lab, ts, np.asarray(sess, "int64"), dport


def context_flags(lab, ts, sess, dport):
    valid = np.isfinite(ts) & (sess >= 0)
    m_abs = np.where(valid, np.floor(np.where(valid, ts, 0) / 60), 0).astype("int64")
    sess_min = pd.Series(m_abs[valid]).groupby(sess[valid]).min()
    rel = np.zeros(len(ts), "int64")
    rel[valid] = m_abs[valid] - sess_min.reindex(sess[valid]).values
    att = ~is_benign(lab)
    F = {}
    for w, name in ((WINDOW, "16 min"), (1, "same minute")):
        F[("network", name)] = window_flags(sess, rel, att, valid, w)
    if dport is not None:
        vs = valid & np.isfinite(dport)
        g = pd.factorize(pd.Series(sess.astype(str)) + "|" + pd.Series(np.nan_to_num(dport, nan=-1).astype("int64").astype(str)))[0]
        for w, name in ((WINDOW, "16 min"), (1, "same minute")):
            F[("service", name)] = window_flags(g, rel, att, vs, w)
    att_min = pd.Series(list(zip(sess[valid & att], rel[valid & att]))).nunique() if (valid & att).any() else 0
    all_min = pd.Series(list(zip(sess[valid], rel[valid]))).nunique() if valid.any() else 0
    return F, valid, int(att_min), int(all_min)


def threshold_clean(scores_dir, lab, parts, clean, out_dir, label, say):
    ti = np.load(os.path.join(scores_dir, "target_index.npz"), allow_pickle=True)
    if len(ti["lab"]) != len(lab) or not np.array_equal(ti["lab"].astype(str), lab):
        say("  target_index.npz labels differ from the cache -> threshold sensitivity skipped")
        return
    same_cal = "cal_i" in ti.files and np.array_equal(np.asarray(ti["cal_i"]), parts["cal"])
    same_bte = np.array_equal(np.asarray(ti["bte_i"]), parts["test"])
    say(f"  rebuilt thirds vs saved index: calibration {'IDENTICAL' if same_cal else 'DIFFERENT'}, "
        f"test {'IDENTICAL' if same_bte else 'DIFFERENT'}")
    if not (same_cal and same_bte):
        say("  -> threshold sensitivity skipped (the thirds must match the saved run)")
        return
    cal, bte = parts["cal"], parts["test"]
    cal_c, bte_c = clean[cal], clean[bte]
    say(f"  clean calibration flows {int(cal_c.sum()):,} of {len(cal):,}; clean test benign {int(bte_c.sum()):,} of "
        f"{len(bte):,}")
    if cal_c.sum() < 1000:
        say("  -> fewer than 1,000 clean calibration flows: threshold sensitivity skipped")
        return
    ben = is_benign(lab)
    rows, frows = [], []
    for f in sorted(glob.glob(os.path.join(scores_dir, "scores_seed*.npz"))):
        seed = int(re.findall(r"scores_seed(\d+)", f)[0])
        z = np.load(f)
        for key in z.files:
            if not key.endswith("|target"):
                continue
            scen, held, model, _ = key.split("|")
            tgt, cs = z[key], z[key[: -len("target")] + "cal"]
            if len(cs) != len(cal):
                continue
            neg = tgt[bte]
            ev = ~np.isnan(tgt) & ~ben
            types = pd.unique(lab[ev])
            for fpr, tag in ((0.01, "1"), (0.001, "01")):
                thr, thr_c = np.quantile(cs, 1 - fpr), np.quantile(cs[cal_c], 1 - fpr)
                frows.append(dict(seed=seed, scenario=scen, held=held, model=model, nominal=fpr, thr_B=thr,
                                  thr_Bclean=thr_c, fpr_test_B=float((neg > thr).mean()),
                                  fpr_cleantest_B=float((neg[bte_c] > thr).mean()),
                                  fpr_cleantest_Bclean=float((neg[bte_c] > thr_c).mean()),
                                  fpr_attackwindow_test_B=float((neg[~bte_c] > thr).mean()) if (~bte_c).any() else np.nan))
                for t in types:
                    pos = tgt[lab == t]
                    rows.append(dict(seed=seed, scenario=scen, held=held, model=model, type=t, nominal=fpr,
                                     recall_B=float((pos > thr).mean()), recall_Bclean=float((pos > thr_c).mean())))
    if not rows:
        say("  no score arrays found")
        return
    R, Fp = pd.DataFrame(rows), pd.DataFrame(frows)
    R.to_csv(os.path.join(out_dir, f"threshold_clean_{label}_per_type.csv"), index=False)
    Fp.to_csv(os.path.join(out_dir, f"threshold_clean_{label}_fpr.csv"), index=False)
    res = os.path.join(scores_dir, "v3_results.csv")
    if os.path.exists(res):                                    # recall at B must equal the saved results exactly
        v = pd.read_csv(res)
        v["held"] = v["held"].fillna("-").astype(str)
        m = R[R.nominal == 0.01].merge(v, on=["seed", "scenario", "held", "model", "type"], how="inner")
        if len(m):
            say(f"  check: recall at B rebuilt from the scores vs v3_results.csv recall1 -> max |diff| "
                f"{np.abs(m.recall_B - m.recall1).max():.2e} over {len(m):,} rows")
    for fpr in (0.01, 0.001):
        say(f"\n  -- nominal FPR {fpr:.1%}: mean over seeds of the macro recall (all types); test FPR on clean / "
            "attack-window test benign")
        r = R[R.nominal == fpr]
        per = r.groupby(["scenario", "model", "seed"])[["recall_B", "recall_Bclean"]].mean()
        tab = per.groupby(["scenario", "model"]).mean()
        fp = Fp[Fp.nominal == fpr].groupby(["scenario", "model"])[
            ["fpr_test_B", "fpr_cleantest_B", "fpr_cleantest_Bclean", "fpr_attackwindow_test_B"]].mean()
        say((tab.join(fp)).round(4).to_string())
        for scen in per.index.get_level_values(0).unique():
            s = per.loc[scen]
            for a, b in PAIRS:
                if a in s.index.get_level_values(0) and b in s.index.get_level_values(0):
                    for col in ("recall_B", "recall_Bclean"):
                        d = (s.loc[a][col] - s.loc[b][col]).dropna()
                        say(f"     {scen:5s} {a:10s} vs {b:10s} [{col:13s}] diff {d.mean():+.3f}  seeds "
                            f"{int((d > 0).sum())}/{len(d)}  p_seed {wil(d.values):.4f}")


def run_context(a):
    os.makedirs(a.out_dir, exist_ok=True)
    L = []
    def say(s):
        print(s, flush=True)
        L.append(s)
    lab, ts, sess, dport = load_target(a.cache, a.times)
    parts = thirds(lab)
    F, valid, att_min, all_min = context_flags(lab, ts, sess, dport)
    att = ~is_benign(lab)
    say(f"== context audit: {a.label}  ({len(lab):,} flows, {int(att.sum()):,} attack, {int((~att).sum()):,} benign; "
        f"time known for {valid.mean():.1%}; sessions {sorted(pd.unique(sess[valid]).tolist())})")
    say(f"   minutes with at least one sampled flow: {all_min:,}; with at least one sampled attack flow: {att_min:,} "
        f"({att_min / max(all_min, 1):.1%})")
    say("   share of benign flows whose window contains a sampled attack flow (LOWER bound: attacks are sampled)")
    rows = []
    for pname, idx in parts.items():
        r = dict(part=pname, n=len(idx))
        for (lvl, win), fl in F.items():
            r[f"{lvl} | {win}"] = float(fl[idx].mean())
        rows.append(r)
    T = pd.DataFrame(rows).set_index("part")
    say(T.round(4).to_string())
    T.to_csv(os.path.join(a.out_dir, f"context_{a.label}.csv"))
    if dport is None:
        say("   (no destination port in this cache -> network level only)")
    by_sess = pd.DataFrame({"session": sess[parts["cal"]], "attack_in_window": F[("network", "16 min")][parts["cal"]]})
    say("   calibration benign by session (network level, 16 min):\n"
        + by_sess.groupby("session").attack_in_window.agg(["size", "mean"]).round(4).to_string())
    if a.scores_dir:
        clean, lvl = ~F[("network", "16 min")], "network level"
        if clean[parts["cal"]].sum() < 1000 and ("service", "16 min") in F:
            clean, lvl = ~F[("service", "16 min")], "service level (too few calibration flows are clean at network level)"
        say(f"\n== threshold-only sensitivity: threshold B from calibration flows WITHOUT sampled attack flows in "
            f"their 16-minute window ({lvl}); novelty channel and alignment unchanged")
        threshold_clean(a.scores_dir, lab, parts, clean, a.out_dir, a.label, say)
    open(os.path.join(a.out_dir, f"context_{a.label}.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"\nsaved -> {a.out_dir}: context_{a.label}.txt / .csv" + (f", threshold_clean_{a.label}_*.csv" if a.scores_dir else ""))


# ============================================================================ conflicts (CIC-UNSW-NB15)
def rebuild_unsw_sample(csv, s17_dir, feats_json, ben, cap, chunk, gap_hours, say):
    """the sampling and cleaning of prep_unsw.main, step by step (pass 1 reads only label and time; the random draw
    depends only on the row count and the label rates). Returns everything needed to inspect the removed rows."""
    sys.path.insert(0, os.getcwd())
    from prep_unsw import map_columns, find, parse_ts
    feats = json.load(open(feats_json or os.path.join(s17_dir, "feature_names.json")))
    flow = [f for f in feats if not f.startswith(("win_", "pw_", "gl_"))]
    cols = list(pd.read_csv(csv, nrows=0).columns)
    col_for, how, missing = map_columns(cols, flow)
    c_lab, c_ts = find(cols, "label"), find(cols, "timestamp")
    t0 = time.time()
    labs, tss = [], []
    for ch in pd.read_csv(csv, usecols=[c_lab, c_ts], chunksize=chunk, low_memory=False):
        labs.append(ch[c_lab].astype(str).str.strip().values)
        tss.append(parse_ts(ch[c_ts].astype(str)).values)
    lab_all, ts_all = np.concatenate(labs), pd.to_datetime(np.concatenate(tss))
    N = len(lab_all)
    okt = ts_all.notna()
    sec = np.where(okt, ts_all.values.astype("datetime64[s]").astype("int64"), np.nan)
    order = np.argsort(np.where(np.isfinite(sec), sec, np.inf), kind="stable")
    ss = sec[order]
    brk = np.r_[False, np.diff(ss) > gap_hours * 3600]
    session = np.full(N, -1, "int64")
    session[order] = np.where(np.isfinite(ss), np.cumsum(brk), -1)
    cnt = pd.Series(lab_all).value_counts()
    rng = np.random.default_rng(0)
    n_ben = int(cnt.get("Benign", 0))
    rate = {k: (min(1.0, ben / max(n_ben, 1)) if k == "Benign" else min(1.0, cap / v)) for k, v in cnt.items()}
    keep = rng.random(N) < pd.Series(lab_all).map(rate).fillna(0).values
    keep &= session >= 0
    rows = np.where(keep)[0]
    say(f"pass 1: {N:,} rows, sampled {len(rows):,} [{time.time() - t0:.0f}s]")
    use2 = set(col_for.values())
    want = np.zeros(N, bool)
    want[rows] = True
    parts, off = [], 0
    for ch in pd.read_csv(csv, usecols=lambda c: c in use2, chunksize=chunk, low_memory=False):
        w = want[off:off + len(ch)]
        off += len(ch)
        sub = ch[w]
        parts.append(pd.DataFrame({f: pd.to_numeric(sub[c], errors="coerce").values for f, c in col_for.items()}))
    D = pd.concat(parts, ignore_index=True)
    for f in missing:
        D[f] = 0.0
    lab = lab_all[rows]
    Xf = D[flow].replace([np.inf, -np.inf], np.nan)
    ok = Xf.notna().all(axis=1).values
    h = pd.util.hash_pandas_object(Xf, index=False).values
    t = pd.DataFrame({"h": h, "a": lab})
    conflict = (t.groupby("h")["a"].transform("nunique") > 1).values
    dup = t.duplicated(["h", "a"]).values
    k = ok & ~(conflict | dup)
    say(f"pass 2: dropped NaN/inf {int((~ok).sum()):,}, conflicting {int((conflict & ok).sum()):,}, duplicates "
        f"{int((dup & ~conflict & ok).sum()):,} -> kept {int(k.sum()):,} [{time.time() - t0:.0f}s]")
    return dict(rows=rows, lab=lab, h=h, ok=ok, conflict=conflict, dup=dup, keep=k)


def recall_bounds(results, kept_counts, conf_counts, say):
    v = pd.read_csv(results)
    rows = []
    for (scen, model), g in v.groupby(["scenario", "model"]):
        per = g.groupby("type").recall1.mean()
        lo, hi, obs = [], [], []
        for t, r in per.items():
            nk, nc = kept_counts.get(t, 0), conf_counts.get(t, 0)
            obs.append(r)
            lo.append(r * nk / (nk + nc) if nk + nc else np.nan)
            hi.append((r * nk + nc) / (nk + nc) if nk + nc else np.nan)
        rows.append(dict(scenario=scen, model=model, types=len(per), macro_recall=np.mean(obs),
                         macro_low_none_detected=np.nanmean(lo), macro_high_all_detected=np.nanmean(hi)))
    B = pd.DataFrame(rows)
    say("\n== recall bounds had the conflicting attack rows been kept (threshold unchanged; mean over seeds, macro)")
    say(B.round(4).to_string(index=False))
    for scen, g in B.groupby("scenario"):
        g = g.set_index("model")
        if {"V3-MAX", "V3-SUP"} <= set(g.index):
            worst = g.loc["V3-MAX", "macro_low_none_detected"] - g.loc["V3-SUP", "macro_high_all_detected"]
            say(f"   {scen}: worst case V3-MAX - V3-SUP = {worst:+.3f} (observed "
                f"{g.loc['V3-MAX', 'macro_recall'] - g.loc['V3-SUP', 'macro_recall']:+.3f})")
    return B


def harmonisation_conflicts(primary_cache, say):
    z = np.load(primary_cache, allow_pickle=True)
    X, lab = np.asarray(z["X"], float), z["lab"].astype(str)
    h = pd.util.hash_pandas_object(pd.DataFrame(X), index=False).values
    t = pd.DataFrame({"h": h, "a": lab})
    conf = (t.groupby("h")["a"].transform("nunique") > 1).values
    dup = t.duplicated(["h", "a"], keep=False).values
    say(f"\n== primary (harmonised) cache: {len(lab):,} rows; rows in label conflicts created by the harmonisation: "
        f"{int(conf.sum()):,}; rows sharing a vector with the same label: {int(dup.sum()):,}")
    if conf.any():
        say("   conflicting rows per label (they stay in the evaluation; flow features cannot separate them):\n"
            + pd.Series(lab[conf]).value_counts().to_string())
    return int(conf.sum())


def run_conflicts(a):
    os.makedirs(a.out_dir, exist_ok=True)
    L = []
    def say(s):
        print(s, flush=True)
        L.append(s)
    S = rebuild_unsw_sample(a.csv, a.s17_dir, a.feats_json, a.ben, a.cap, a.chunk, a.gap_hours, say)
    raw = np.load(a.raw_cache, allow_pickle=True)
    kept_rows = S["rows"][S["keep"]]
    same = "row" in raw.files and np.array_equal(kept_rows, np.asarray(raw["row"]))
    same_lab = np.array_equal(S["lab"][S["keep"]], raw["lab"].astype(str))
    say(f"check vs raw cache: kept rows {'IDENTICAL' if same else 'DIFFERENT'}, labels "
        f"{'IDENTICAL' if same_lab else 'DIFFERENT'}")
    if not (same and same_lab):
        say("-> the rebuilt sample does not match the cache; the composition below would not describe it. Stopped.")
        open(os.path.join(a.out_dir, "conflicts_unsw.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
        return
    c = S["conflict"] & S["ok"]
    lab, h = S["lab"], S["h"]
    g = pd.DataFrame({"h": h[c], "lab": lab[c]})
    labsets = g.groupby("h")["lab"].agg(lambda s: tuple(sorted(set(s))))
    g["group_labels"] = g["h"].map(labsets)
    g["with_benign"] = g["group_labels"].map(lambda s: "Benign" in s)
    g["kind"] = np.where(g["lab"] == "Benign", "benign row",
                         np.where(g["with_benign"], "attack row sharing a vector with benign",
                                  "attack row sharing a vector with another attack type only"))
    say(f"\n== conflicting rows removed from the sample: {int(c.sum()):,} in {g.h.nunique():,} distinct vectors")
    say(pd.crosstab(g["lab"], g["kind"], margins=True).to_string())
    say("   other labels in the conflict groups of each attack type (rows of that type, by partner label):")
    for t, gg in g[g.lab != "Benign"].groupby("lab"):
        partners = pd.Series([x for tup in gg["group_labels"] for x in tup if x != t]).value_counts()
        say(f"     {t}: " + ", ".join(f"{k} {v}" for k, v in partners.items()))
    g.to_csv(os.path.join(a.out_dir, "conflicts_unsw_rows.csv"), index=False)
    prim = np.load(a.primary_cache, allow_pickle=True)
    kept_counts = pd.Series(prim["lab"].astype(str)).value_counts().to_dict()
    conf_counts = g[g.lab != "Benign"]["lab"].value_counts().to_dict()
    say(f"   benign rows removed as conflicting: {int((g.lab == 'Benign').sum()):,} (about one third would have joined "
        "the test benign part)")
    if a.results:
        recall_bounds(a.results, kept_counts, conf_counts, say).to_csv(
            os.path.join(a.out_dir, "conflicts_unsw_recall_bounds.csv"), index=False)
    harmonisation_conflicts(a.primary_cache, say)
    open(os.path.join(a.out_dir, "conflicts_unsw.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"\nsaved -> {a.out_dir}: conflicts_unsw.txt, conflicts_unsw_rows.csv, conflicts_unsw_recall_bounds.csv")


# ============================================================================ selftest
def selftest():
    ok = []
    rng = np.random.default_rng(5)
    n = 4000
    grp = rng.integers(0, 3, n)
    minute = rng.integers(0, 200, n)
    att = rng.random(n) < 0.03
    valid = rng.random(n) < 0.97
    fl = window_flags(grp, minute, att, valid, WINDOW)
    brute = np.array([valid[i] and bool(np.any(att & valid & (grp == grp[i]) & (minute <= minute[i])
                                               & (minute >= minute[i] - WINDOW + 1))) for i in range(n)])
    ok.append(np.array_equal(fl, brute))
    print(f"{'PASS' if ok[-1] else 'FAIL'} window flags equal brute force ({fl.mean():.3f} flagged)")
    fl1 = window_flags(grp, minute, att, valid, 1)
    brute1 = np.array([valid[i] and bool(np.any(att & valid & (grp == grp[i]) & (minute == minute[i]))) for i in range(n)])
    ok.append(np.array_equal(fl1, brute1))
    print(f"{'PASS' if ok[-1] else 'FAIL'} same-minute flags equal brute force")
    lab = np.where(rng.random(12001) < 0.8, "Benign", "DoS").astype(str)
    p = thirds(lab)
    r2 = np.random.default_rng(0)
    ben = np.where(lab == "Benign")[0]
    r2.shuffle(ben)
    k3 = len(ben) // 3
    ok.append(np.array_equal(p["cal"], ben[k3:2 * k3]) and np.array_equal(p["test"], ben[2 * k3:])
              and len(p["fit"]) + len(p["ref"]) == k3)
    print(f"{'PASS' if ok[-1] else 'FAIL'} thirds = hybrid_v3.build_target (seed 0)")
    # threshold sensitivity on a synthetic dump_scores folder
    import tempfile
    d = tempfile.mkdtemp()
    ts = np.where(lab == "DoS", rng.uniform(0, 3600, len(lab)), rng.uniform(0, 3600 * 10, len(lab)))  # attacks: hour 1
    sess = np.zeros(len(lab), int)
    F, valid2, _, _ = context_flags(lab, ts, sess, None)
    clean = ~F[("network", "16 min")]
    np.savez_compressed(os.path.join(d, "target_index.npz"), lab=lab, bte_i=p["test"], cal_i=p["cal"],
                        benign=lab == "Benign")
    rows = []
    for seed in range(3):
        dd = {}
        for model, shift in (("TREE", 0.0), ("V3-SUP", 0.1), ("V3-MAX", 0.6)):
            s = rng.normal(0, 1, len(lab)) + np.where(lab == "DoS", shift + 1.0, 0)
            tgt = s.astype("float32").copy()
            tgt[p["reference_all"]] = np.nan
            dd[f"known|-|{model}|target"] = tgt
            dd[f"known|-|{model}|cal"] = s[p["cal"]].astype("float32")
            thr = np.quantile(s[p["cal"]].astype("float32"), 0.99)
            rows.append(dict(seed=seed, scenario="known", held="-", model=model, type="DoS",
                             recall1=float((tgt[lab == "DoS"] > thr).mean())))
        np.savez_compressed(os.path.join(d, f"scores_seed{seed}.npz"), **dd)
    pd.DataFrame(rows).to_csv(os.path.join(d, "v3_results.csv"), index=False)
    L = []
    threshold_clean(d, lab, p, clean, d, "syn", L.append)
    txt = "\n".join(L)
    if "max |diff|" not in txt:
        print(txt)
    m = re.search(r"max \|diff\| ([0-9.e+-]+)", txt)
    ok.append("IDENTICAL" in txt and m is not None and float(m.group(1)) < 1e-9)
    print(f"{'PASS' if ok[-1] else 'FAIL'} threshold sensitivity: thirds identical, recall at B equals saved results "
          f"(max |diff| {m.group(1) if m else '?'})")
    B = recall_bounds_selftest()
    ok.append(B)
    print("ALL PASS" if all(ok) else "SOME CHECKS FAILED")
    return all(ok)


def recall_bounds_selftest():
    import tempfile
    d = tempfile.mkdtemp()
    v = pd.DataFrame([dict(scenario="known", model="M", seed=0, type="A", recall1=0.5),
                      dict(scenario="known", model="M", seed=1, type="A", recall1=0.5)])
    v.to_csv(os.path.join(d, "r.csv"), index=False)
    B = recall_bounds(os.path.join(d, "r.csv"), {"A": 100}, {"A": 100}, lambda s: None)
    r = B.iloc[0]
    good = abs(r.macro_low_none_detected - 0.25) < 1e-12 and abs(r.macro_high_all_detected - 0.75) < 1e-12
    print(f"{'PASS' if good else 'FAIL'} recall bounds: 0.5 on 100 kept + 100 conflicting -> [0.25, 0.75]")
    return good


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", nargs="?", choices=["context", "conflicts"])
    ap.add_argument("--label", default="target")
    ap.add_argument("--cache")
    ap.add_argument("--times", default="")
    ap.add_argument("--scores_dir", default="")
    ap.add_argument("--csv")
    ap.add_argument("--raw_cache", default="D:/revised model/unsw/unsw_sample_v1.npz")
    ap.add_argument("--primary_cache", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--results", default="")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--feats_json", default="")
    ap.add_argument("--ben", type=int, default=300000)
    ap.add_argument("--cap", type=int, default=20000)
    ap.add_argument("--chunk", type=int, default=500000)
    ap.add_argument("--gap_hours", type=float, default=6.0)
    ap.add_argument("--out_dir", default="audit_target")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.mode == "context":
        if not a.cache:
            raise SystemExit("context needs --cache")
        return run_context(a)
    if a.mode == "conflicts":
        if not a.csv:
            raise SystemExit("conflicts needs --csv (the UNSW CSV used with prep_unsw.py)")
        return run_conflicts(a)
    raise SystemExit("give a mode: context | conflicts (or --selftest); see the header of this file")


if __name__ == "__main__":
    main()
