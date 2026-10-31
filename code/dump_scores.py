"""
Saves the PER-FLOW scores of the frozen v3 models, needed for: recall at a MATCHED real false-alarm rate (the tree's
scores have ties, so at "1%" it really runs at ~0.5%), ROC / precision-recall curves and PR-AUC, the threshold-cliff
figure, the attack-family stage (which flows raised an alarm) and the event-level metric.

How: hybrid_v3.run is called UNCHANGED (frozen fingerprint); only its function recall_at is wrapped so that every
(calibration benign, test benign, attack type) score array it receives is copied to disk. The same seeds, settings
and code give the same models, so the v3_results.csv written again here must equal the earlier run: --verify_against
compares them (it should print max difference 0).

Output in --out_dir:
  scores_seed<k>.npz   for every task x model: "<scenario>|<held>|<model>|cal" (calibration benign scores) and
                       "<scenario>|<held>|<model>|target" (one score per target flow, NaN for flows not evaluated in
                       that task, e.g. the 'fit' benign third or attack types of other tasks)
  target_index.npz     labels of the target flows, test-benign / calibration index sets
  v3_results.csv ...   the normal hybrid_v3 outputs (identical numbers)

  python dump_scores.py --smoke
  python dump_scores.py --protocol cross --target ids2018 --target_cache "D:/revised model/cross_out4/ids2018_sample_v4.npz" --out_dir "D:/revised model/scores_cross" --configs TREE,V3-SUP --seeds 10 --verify_against "D:/revised model/v33_cross10/v3_results.csv"
  (known + loo, TREE and V3-SUP, 10 seeds: about 4 h; --mode known: about 25 min)
"""
import argparse, glob, os, sys, time, types, warnings
import numpy as np
import pandas as pd


class Capture:
    """wraps recall_at. Every call = one result row (same order as v3_results.csv). Calls that receive the SAME
    calibration array object share one stored block (calibration + test-benign scores saved once)."""
    def __init__(self, orig, tmp_dir):
        self.orig, self.tmp, self.b, self.cur, self.pos, self.calls = orig, tmp_dir, -1, None, [], []
        os.makedirs(tmp_dir, exist_ok=True)

    def flush(self):
        if self.cur is not None:
            s_cal, s_bte = self.cur
            np.savez(os.path.join(self.tmp, f"b{self.b:06d}.npz"), cal=np.asarray(s_cal, "float32"),
                     bte=np.asarray(s_bte, "float32"), n=np.array([len(p) for p in self.pos]),
                     pos=np.concatenate(self.pos).astype("float32") if self.pos else np.zeros(0, "float32"))
        self.cur, self.pos = None, []

    def __call__(self, s_cal, s_bte, s_pos):
        if self.cur is None or self.cur[0] is not s_cal:            # identity; a reference is kept, ids cannot recur
            self.flush()
            self.b += 1
            self.cur = (s_cal, s_bte)
        self.calls.append((self.b, len(self.pos)))
        self.pos.append(np.array(s_pos, dtype="float32", copy=True))
        return self.orig(s_cal, s_bte, s_pos)


def assemble(rows, calls, tmp_dir, tg, out_dir, is_benign):
    """row i of v3_results.csv <-> call i of recall_at; one target array per seed x task x model"""
    if len(calls) != len(rows):
        raise SystemExit(f"capture mismatch: {len(calls)} calls vs {len(rows)} result rows")
    lab = np.asarray(tg["lab"])
    idx_of = {t: np.where(lab == t)[0] for t in pd.unique(rows.type)}
    blocks = {}
    def block(b):
        if b not in blocks:
            blocks.clear()
            z = np.load(os.path.join(tmp_dir, f"b{b:06d}.npz"))
            blocks[b] = dict(cal=z["cal"], bte=z["bte"], pos=np.split(z["pos"], np.cumsum(z["n"])[:-1]))
        return blocks[b]
    keys = ["seed", "scenario", "held", "model"]
    gid = (rows[keys] != rows[keys].shift()).any(axis=1).cumsum().values
    per_seed = {}
    for g in np.unique(gid):
        ii = np.where(gid == g)[0]
        b0 = calls[ii[0]][0]
        arr = np.full(len(lab), np.nan, "float32")
        arr[tg["bte_i"]] = block(b0)["bte"]
        for i in ii:
            b, k = calls[i]
            if b != b0:
                raise SystemExit("capture mismatch: one task x model spans two calibration arrays")
            piece, t = block(b)["pos"][k], rows.type.iloc[i]
            if len(piece) != len(idx_of[t]):
                raise SystemExit(f"capture mismatch for type {t}")
            arr[idx_of[t]] = piece
        r = rows.iloc[ii[0]]
        key = f"{r.scenario}|{r.held}|{r.model}"
        d = per_seed.setdefault(int(r.seed), {})
        d[key + "|cal"], d[key + "|target"] = block(b0)["cal"], arr
    for s, d in per_seed.items():
        np.savez_compressed(os.path.join(out_dir, f"scores_seed{s}.npz"), **d)
    np.savez_compressed(os.path.join(out_dir, "target_index.npz"), lab=lab.astype(str),
                        bte_i=np.asarray(tg["bte_i"]),
                        cal_i=np.asarray(tg["cal_i"]) if tg.get("cal_i") is not None else np.zeros(0, int),
                        benign=is_benign(lab))
    for f in glob.glob(os.path.join(tmp_dir, "b*.npz")):
        os.remove(f)
    try:
        os.rmdir(tmp_dir)
    except OSError:
        pass
    return int(gid.max()), sorted(per_seed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", choices=["cross", "within"], default="cross")
    ap.add_argument("--target", default="ids2018")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--target_cache", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--out_dir", default="scores_out")
    ap.add_argument("--mode", choices=["known", "loo", "both"], default="both")
    ap.add_argument("--configs", default="TREE,V3-SUP")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--verify_against", default="", help="earlier v3_results.csv with the same settings")
    ap.add_argument("--smoke", action="store_true")
    a0 = ap.parse_args()
    warnings.filterwarnings("ignore")
    import torch
    import hybrid_v3 as V
    # the defaults of hybrid_v3.main (every earlier run used them)
    a = types.SimpleNamespace(protocol=a0.protocol, target=a0.target, s17_dir=a0.s17_dir, target_cache=a0.target_cache,
                              out_dir=a0.out_dir, mode=a0.mode, configs=a0.configs, within_fams=",".join(V.WITHIN_FAMS),
                              seeds=a0.seeds, max_train=30000, val_max=10000, tree_train=100000, epochs=6, patience=2,
                              bs=512, lr=2e-3, lb=0.1, qubits=8, q_m=2000, q_nu=0.1, device="cpu")
    os.makedirs(a.out_dir, exist_ok=True)
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    if a0.smoke:
        a.seeds, a.epochs, a.max_train, a.val_max, a.tree_train, a.q_m, a.qubits = 1, 2, 3000, 1500, 3000, 300, 6
        a.target = "ids2018"
        D = V.make_smoke(a.protocol)
    else:
        D = V.load_data(a)
    import hashlib
    here = os.path.dirname(os.path.abspath(V.__file__))
    sha = {f: hashlib.sha256(open(os.path.join(here, f), "rb").read()).hexdigest()[:12] for f in ("hybrid_v3.py", "qkernel.py")}
    print(f"code fingerprint (must equal the run you compare with): {sha}", flush=True)
    tmp = os.path.join(a.out_dir, "_capture_tmp")
    for f in glob.glob(os.path.join(tmp, "b*.npz")):
        os.remove(f)
    cap = Capture(V.recall_at, tmp)
    V.recall_at = cap                                              # the only change: copy the arrays it receives
    t0 = time.time()
    V.run(D, a, torch.device("cpu"), a.out_dir)
    cap.flush()
    rows = pd.read_csv(os.path.join(a.out_dir, "v3_results.csv"))
    tg = V.build_target(D, a)
    n, seeds = assemble(rows, cap.calls, tmp, tg, a.out_dir, V.is_benign)
    print(f"\nsaved scores of {n} task x model combinations, seeds {seeds}, in {a.out_dir} [{time.time() - t0:.0f}s]")
    if a0.verify_against:
        old = pd.read_csv(a0.verify_against)
        k = ["seed", "scenario", "held", "model", "type"]
        m = rows.merge(old, on=k, suffixes=("", "_old"))
        if len(m) == 0:
            print("verify: no common rows (different configs / seeds?)")
        else:
            diff = max(float((m[c] - m[c + "_old"]).abs().max()) for c in ("recall1", "fpr_test1", "auc"))
            print(f"verify against {a0.verify_against}: {len(m)} common rows, max difference {diff:.2e} "
                  + ("-> IDENTICAL" if diff < 1e-9 else "-> DIFFERENT (check fingerprint / settings)"))


if __name__ == "__main__":
    main()
