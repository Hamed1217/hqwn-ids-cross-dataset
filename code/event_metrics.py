"""
EVENT-LEVEL evaluation (evaluation-criteria section, point 3): an operator does not need every attack flow, only to
learn that an attack is under way, how fast, and how often the alarm is false. Uses the per-flow scores saved by
dump_scores.py and the flow timestamps; the frozen models are not run again.

Alarm rule: a flow alarms if its score is above threshold B (99th / 99.9th percentile of the calibration benign, exactly
as in hybrid_v3). Alerts are aggregated per MINUTE: a minute alarms for attack type t if at least k of its flows of
type t alarm; a benign minute raises a FALSE alarm if at least k of its test-benign flows alarm (k = 1, 3).
  episode          consecutive flows of one attack type in one capture session, a gap > --gap minutes starts a new one
  episode recall   share of episodes with at least one alarming minute
  time to detect   seconds from the first flow of the episode to the alarm that completes the first alarming minute
  minute recall    share of the minutes containing type-t flows that alarm
  false-alarm minutes   share of the minutes with test-benign flows that raise a false alarm, and per hour of capture
All per attack type, then the mean over types (as the flow metric), mean (sd) over seeds; paired tests per seed.

CAVEAT (written into the report): the caches are SAMPLES (benign subsampled, attack types capped) and the test benign
is one third of the sampled benign. Fewer flows per minute than the real traffic -> episode / minute recall are LOWER
bounds and false-alarm minute rates are also LOWER than on the full traffic (more benign flows per minute -> more
chances for a false alarm). Comparisons between models at the same setting are fair.

Timestamps: UNSW cache (harmonised or raw) has 'ts' and 'session'; 2018: run ts_2018.py first (ids2018_times_v4.npz);
2017 (easy / medium levels): no timestamps in the stage-1 output -> not available.

  python event_metrics.py --scores_dir "D:/revised model/scores_unsw" --times "D:/revised model/unsw/unsw_sample_v1h.npz" --pairs "V3-MAX>V3-SUP,V3-MAX>TREE,V3-MAX>V3-MAX-RBF"
  python event_metrics.py --scores_dir "D:/revised model/scores_cross" --times "D:/revised model/cross_out4/ids2018_times_v4.npz" --pairs "V3-SUP>TREE"
  python event_metrics.py --selftest
Outputs in --scores_dir: event_per_type.csv, event_benign.csv, event_report.txt
"""
import argparse, glob, os, re
import numpy as np
import pandas as pd


def episodes(ts, sess, gap_s):
    """episode id for flows (any order) of one attack type"""
    o = np.lexsort((ts, sess))
    brk = np.r_[True, (np.diff(ts[o]) > gap_s) | (np.diff(sess[o]) != 0)]
    ep = np.empty(len(ts), int)
    ep[o] = np.cumsum(brk) - 1
    return ep


def type_events(ts, sess, alarm, gap_s, k):
    """episode recall, minute recall, median time to detect for the flows of ONE attack type"""
    ep = episodes(ts, sess, gap_s)
    minute = np.floor(ts / 60).astype("int64")
    df = pd.DataFrame(dict(ep=ep, sess=sess, minute=minute, ts=ts, alarm=alarm))
    mins = df.groupby(["sess", "minute"]).alarm.sum()
    minute_recall = float((mins >= k).mean())
    det, ttd = [], []
    for _, g in df.groupby("ep"):
        start = g.ts.min()
        g = g.sort_values("ts")
        a = g[g.alarm]
        if len(a) == 0:
            det.append(False)
            continue
        cum = a.groupby("minute").cumcount() + 1                  # running count of alarms inside each minute
        hit = a[cum.values >= k]
        if len(hit) == 0:
            det.append(False)
            continue
        det.append(True)
        ttd.append(float(hit.ts.iloc[0] - start))
    return dict(n_episodes=len(det), episode_recall=float(np.mean(det)), minute_recall=minute_recall,
                median_ttd_s=float(np.median(ttd)) if ttd else np.nan,
                share_detected_60s=float(np.mean([t <= 60 for t in ttd] + [False] * (len(det) - len(ttd)))))


def benign_events(ts, sess, alarm, k):
    minute = np.floor(ts / 60).astype("int64")
    mins = pd.DataFrame(dict(sess=sess, minute=minute, alarm=alarm)).groupby(["sess", "minute"]).alarm.sum()
    hours = sum((ts[sess == s].max() - ts[sess == s].min()) / 3600 for s in np.unique(sess))
    fa = int((mins >= k).sum())
    return dict(n_benign_minutes=len(mins), fa_minute_rate=float((mins >= k).mean()),
                fa_minutes_per_hour=fa / max(hours, 1e-9), hours=hours)


def analyse(scores_dir, ts_all, sess_all, gap_min, ks, fprs):
    ix = np.load(os.path.join(scores_dir, "target_index.npz"), allow_pickle=True)
    lab, bte_i = ix["lab"].astype(str), ix["bte_i"]
    if len(lab) != len(ts_all):
        raise SystemExit(f"timestamps ({len(ts_all)}) do not match the target flows ({len(lab)}): wrong --times file")
    okt = np.isfinite(ts_all)
    is_bte = np.zeros(len(lab), bool)
    is_bte[bte_i] = True
    T, Bn = [], []
    for f in sorted(glob.glob(os.path.join(scores_dir, "scores_seed*.npz"))):
        seed = int(re.findall(r"scores_seed(\d+)", f)[0])
        z = np.load(f)
        for key in z.files:
            if not key.endswith("|target"):
                continue
            scen, held, model, _ = key.split("|")
            tgt, cal = z[key], z[key[:-len("target")] + "cal"]
            ev = ~np.isnan(tgt) & ~is_bte & okt
            types_ = pd.unique(lab[ev])
            for fpr in fprs:
                thr = np.quantile(cal, 1 - fpr)
                alarm = np.nan_to_num(tgt, nan=-np.inf) > thr
                for k in ks:
                    base = dict(seed=seed, scenario=scen, held=held, model=model, fpr=fpr, k=k)
                    b = is_bte & okt
                    Bn.append(dict(base, flow_fpr=float(alarm[b].mean()),
                                   **benign_events(ts_all[b], sess_all[b], alarm[b], k)))
                    for t in types_:
                        r = ev & (lab == t)
                        T.append(dict(base, type=t, n_flows=int(r.sum()), flow_recall=float(alarm[r].mean()),
                                      **type_events(ts_all[r], sess_all[r], alarm[r], gap_min * 60, k)))
    return pd.DataFrame(T), pd.DataFrame(Bn)


def report(T, Bn, pairs, out_dir, gap_min):
    from scipy.stats import wilcoxon
    L = [f"EVENT-LEVEL metrics (episodes split at gaps > {gap_min} min; minute alarm = >= k alarming flows).",
         "CAVEAT: sampled caches -> event recall and false-alarm minutes are lower bounds of the full-traffic values;",
         "model comparisons at the same setting are fair.", ""]
    cols = ["flow_recall", "episode_recall", "minute_recall", "share_detected_60s", "median_ttd_s"]
    for (scen, fpr, k), g in T.groupby(["scenario", "fpr", "k"], sort=False):
        ps = g.groupby(["model", "seed"])[cols].mean()
        bb = Bn[(Bn.scenario == scen) & (Bn.fpr == fpr) & (Bn.k == k)].groupby(["model", "seed"])[
            ["flow_fpr", "fa_minute_rate", "fa_minutes_per_hour"]].mean()
        tab = ps.join(bb).groupby("model").agg(["mean", "std"])
        show = pd.DataFrame({c: tab[c]["mean"].map("{:.3f}".format) + " (" + tab[c]["std"].map("{:.3f}".format) + ")"
                             for c in cols + ["flow_fpr", "fa_minute_rate", "fa_minutes_per_hour"]})
        L.append(f"==== {scen} | threshold B at {fpr:.1%} flow false alarms | minute rule k = {k}")
        L.append("mean over attack types, mean (sd) over seeds; ttd = time to detect (s); fa = false-alarm minutes")
        L.append(show.sort_values("episode_recall", ascending=False).to_string())
        L.append("-- per type (mean over seeds): episode recall / minute recall / median time to detect (s)")
        per = g.groupby(["type", "model"])[["n_episodes", "episode_recall", "minute_recall", "median_ttd_s"]].mean()
        L.append(per.round(3).unstack("model").to_string())
        for p in pairs:
            a, b = p
            for c in ("episode_recall", "minute_recall"):
                x = ps.loc[a, c] if a in ps.index.get_level_values(0) else None
                y = ps.loc[b, c] if b in ps.index.get_level_values(0) else None
                if x is None or y is None:
                    continue
                d = (x - y.reindex(x.index)).dropna()
                pv = wilcoxon(d, alternative="greater").pvalue if (d != 0).sum() >= 3 else np.nan
                L.append(f"  {a} vs {b} [{c}] mean diff {d.mean():+.3f}, wins {(d > 0).sum()}/{len(d)} seeds, p = {pv:.4f}")
        L.append("")
    txt = "\n".join(L)
    open(os.path.join(out_dir, "event_report.txt"), "w", encoding="utf-8").write(txt + "\n")
    print(txt)


def selftest():
    """synthetic: one attack type in 3 bursts; model A alarms on every flow of bursts 1-2 only, so episode recall
    must be 2/3 with time to detect 0; a benign stream with 2 alarming minutes"""
    ts = np.r_[np.arange(0, 600, 10), np.arange(5000, 5300, 10), np.arange(9000, 9100, 10)].astype(float)
    sess = np.zeros(len(ts), int)
    alarm = ts < 6000
    r = type_events(ts, sess, alarm, 300, 1)
    ok1 = r["n_episodes"] == 3 and abs(r["episode_recall"] - 2 / 3) < 1e-9 and r["median_ttd_s"] == 0
    alarm2 = ts >= 5000                                              # bursts 2 and 3, starting at their first flow
    r2 = type_events(ts, sess, alarm2, 300, 3)                       # k = 3: needs 3 alarms inside one minute
    ok2 = abs(r2["episode_recall"] - 2 / 3) < 1e-9 and r2["median_ttd_s"] == 20
    bts = np.arange(0, 3600, 6).astype(float)
    ba = np.zeros(len(bts), bool)
    ba[[3, 4, 300]] = True                                           # minute 0 (2 alarms) and minute 30 (1 alarm)
    b1, b3 = benign_events(bts, np.zeros(len(bts), int), ba, 1), benign_events(bts, np.zeros(len(bts), int), ba, 2)
    ok3 = b1["fa_minute_rate"] == 2 / 60 and b3["fa_minute_rate"] == 1 / 60
    for name, ok, info in (("episodes, recall and time to detect (k=1)", ok1, r), ("k = 3 rule", ok2, r2),
                           ("false-alarm minutes for k = 1 and 2", ok3, (b1["fa_minute_rate"], b3["fa_minute_rate"]))):
        print(("PASS " if ok else "FAIL ") + name, info)
    print("ALL PASS" if ok1 and ok2 and ok3 else "SOME CHECKS FAILED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores_dir")
    ap.add_argument("--times", help="npz with 'ts' (seconds) and 'session' aligned with the target cache rows")
    ap.add_argument("--pairs", default="V3-SUP>TREE")
    ap.add_argument("--gap", type=float, default=5, help="minutes without flows of a type that end an episode")
    ap.add_argument("--k", default="1,3")
    ap.add_argument("--fprs", default="0.01,0.001")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    z = np.load(a.times, allow_pickle=True)
    ts = np.asarray(z["ts"], "float64")
    sess = np.asarray(z["session"]) if "session" in z.files else np.zeros(len(ts), int)
    T, Bn = analyse(a.scores_dir, ts, sess, a.gap, [int(x) for x in a.k.split(",")],
                    [float(x) for x in a.fprs.split(",")])
    T.to_csv(os.path.join(a.scores_dir, "event_per_type.csv"), index=False)
    Bn.to_csv(os.path.join(a.scores_dir, "event_benign.csv"), index=False)
    pairs = [tuple(x.strip() for x in p.split(">")) for p in a.pairs.split(",") if ">" in p]
    report(T, Bn, pairs, a.scores_dir, a.gap)
    print(f"saved -> event_per_type.csv, event_benign.csv, event_report.txt in {a.scores_dir}")


if __name__ == "__main__":
    main()
