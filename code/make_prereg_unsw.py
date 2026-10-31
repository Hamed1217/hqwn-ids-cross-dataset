"""
Writes the PRE-REGISTRATION of the confirmatory CIC-UNSW-NB15 test (prereg_unsw.txt) with the SHA-256 of every file
the test depends on, BEFORE the test is run. It refuses to write if hybrid_v3.py is not the frozen version.
Keep prereg_unsw.txt unchanged (and send a copy for the archive) before starting the run.

  python make_prereg_unsw.py
"""
import argparse, datetime, hashlib, os

FROZEN_V3 = "30721b06ba80"

TEXT = """PRE-REGISTRATION - confirmatory test on CIC-UNSW-NB15 (run ONCE; written {when})

Model and code: hybrid_v3.py frozen since 2026-10-25 (fingerprint {v3}); nothing is tuned on UNSW. Run through
dump_scores.py, which calls hybrid_v3.run unchanged and also saves the per-flow scores. Train CIC-IDS2017 -> test UNSW.
Data: prep_unsw.py (column map reviewed line by line before the build), sample seed 0: 190,901 benign + 9 attack
classes (all >= 236 flows). Feature definitions harmonised by harmonize_unsw.py BEFORE any model saw UNSW, decided
from check_extractor.py (no labels): Subflow_* := matching totals (2017 definition); *_Flag_Count := 0 (unavailable;
the old extractor's rule cannot be rebuilt). PRIMARY = harmonised cache; SENSITIVITY = raw cache (TREE, V3-SUP only).
Threshold B = 99th (99.9th) percentile of the UNSW calibration benign third; real FPR on the separate test third.

Configurations: TREE (baseline), V3-SUP (THE model), V3-SUP-NOA (no attention, parsimony), V3-SUP-DENSE (neuromorphic
control), V3-MAX (V3-SUP + quantum IQP novelty channel), V3-MAX-RBF (classical-kernel control). 10 seeds, known + loo.
Scenarios: known = all 2017 attacks in training; loo = 2017 counterpart family held out (Reconnaissance <- PortScan;
DoS <- the five 2017 DoS/DDoS types). 7 of the 9 UNSW classes have NO 2017 counterpart (Exploits, Fuzzers, Generic,
Shellcode, Backdoor, Analysis, Worms): every mean is ALSO reported separately for (a) the 2 classes with a counterpart
and (b) the 7 new classes.

Tests: one-sided Wilcoxon over seed x type (primary form) and per seed (conservative form), alpha 0.05, no correction
claimed beyond reporting all tests.
  U1 PRIMARY      known: V3-SUP > TREE, mean recall@1% FPR (threshold B), all 9 types.
  U1b secondary   same pair at EXACTLY 1% and 0.1% test FPR (analyze_scores.py, ROC-interpolated, tie-fair), at
                  threshold B 0.1%, and PR-AUC; plus F1 / MCC / AUC / confusion matrix (derive_metrics.py).
  U2 neuromorphic V3-SUP vs V3-SUP-DENSE: recall drop <= 0.02 (non-inferiority) and estimated energy of the temporal
                  path <= 0.5 x dense (memory-access sensitivity reported).
  U3 novelty      V3-MAX > V3-SUP (known and loo); quantum: V3-MAX > V3-MAX-RBF (no advantage expected: equal in 8
                  of 8 tests on 2017 / 2018).
  U4 parsimony    V3-SUP-NOA >= V3-SUP - 0.02.
  U5 loo          V3-SUP > TREE in loo (expected: not supported, as on 2018).
Expectations written in advance (from 2017 -> 2018): U1 small or no advantage; low recall on the 7 new classes; U3
quantum = classical. Whatever the outcome, it is reported.
Attack-family stage (design fixed 2026-10-25, before this test): families DoS / Scan(<-Reconnaissance) + 'unknown'
for the 7 new classes; HistGB on 2017 attack flows, unknown if max probability < 5th percentile on 2017 validation;
run on the saved UNSW scores of V3-SUP (alarms at threshold B) and on all attack flows.
Identity confound reported: every UNSW attack flow comes from 175.45.176.x (IPs are never features).

Commands:
  python dump_scores.py --protocol cross --target unsw --target_cache "{h}" --out_dir "{out}/unsw_primary" --configs TREE,V3-SUP,V3-SUP-NOA,V3-SUP-DENSE,V3-MAX,V3-MAX-RBF --seeds 10
  python dump_scores.py --protocol cross --target unsw --target_cache "{r}" --out_dir "{out}/unsw_raw" --configs TREE,V3-SUP --seeds 10
  python derive_metrics.py --results "{out}/unsw_primary/v3_results.csv" --plots
  python analyze_scores.py --scores_dir "{out}/unsw_primary" --pairs "V3-SUP>TREE,V3-SUP>V3-SUP-DENSE,V3-MAX>V3-SUP,V3-MAX>V3-MAX-RBF"
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="D:/revised model")
    ap.add_argument("--raw", default="D:/revised model/unsw/unsw_sample_v1.npz")
    ap.add_argument("--harm", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--out", default="D:/revised model/prereg_unsw.txt")
    a = ap.parse_args()
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    files = ["hybrid_v3.py", "qkernel.py", "hybrid_v2.py", "dump_scores.py", "analyze_scores.py", "derive_metrics.py",
             "prep_unsw.py", "harmonize_unsw.py", "check_extractor.py", "port_windows.py"]
    h = {f: sha(os.path.join(a.dir, f)) for f in files if os.path.exists(os.path.join(a.dir, f))}
    miss = [f for f in files if f not in h]
    if miss:
        raise SystemExit(f"missing in {a.dir}: {miss}")
    if not h["hybrid_v3.py"].startswith(FROZEN_V3):
        raise SystemExit(f"hybrid_v3.py is NOT the frozen version ({h['hybrid_v3.py'][:12]} != {FROZEN_V3}); stop.")
    for p in (a.raw, a.harm):
        if not os.path.exists(p):
            raise SystemExit(f"missing cache {p} (run prep_unsw.py / harmonize_unsw.py first)")
    h["CACHE raw " + os.path.basename(a.raw)] = sha(a.raw)
    h["CACHE harmonised " + os.path.basename(a.harm)] = sha(a.harm)
    when = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    txt = TEXT.format(when=when, v3=FROZEN_V3, h=a.harm, r=a.raw, out=a.dir.rstrip("/\\"))
    txt += "\nSHA-256:\n" + "\n".join(f"  {k:40s} {v}" for k, v in h.items()) + "\n"
    open(a.out, "w", encoding="utf-8").write(txt)
    print(txt)
    print(f"written -> {a.out}  (do not edit it; send a copy, then start the first command)")


if __name__ == "__main__":
    main()
