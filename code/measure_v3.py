"""
Efficiency of the FINAL v3 models for the proposal claims "latency < 40 ms" and "power < 15 W", with the honest
comparisons the reviewers asked for. hybrid_v3.py and qkernel.py are IMPORTED UNCHANGED (frozen fingerprint).
Needs hybrid_v3.py, hybrid_v2.py, qkernel.py, measure_efficiency.py, port_windows.py in the same folder.
CPU, about 10-20 minutes. Run it on an IDLE machine (no other run at the same time, laptop on the charger,
power plan "best performance"), otherwise the times are wrong.

What it measures (seed 0, models trained exactly as in the 'known' task of hybrid_v3, 2017 -> 2018):
  1. LATENCY per flow, one flow at a time (batch = 1), median / p95 / p99 in ms, 1 thread and all threads, for every
     part: tree expert, V3-SUP network, V3-SUP-DENSE network, quantum (IQP) and classical (RBF) novelty channel, and the
     16-minute sequence (PortTable). End-to-end p95 per configuration = SUM of the parts' p95 (conservative).
  2. THROUGHPUT, batches of 4096 flows.
  3. SPIKING vs DENSE on a CPU: a CPU simulates spikes as ordinary numbers, so the spiking model is NOT faster here;
     its energy advantage needs event-driven neuromorphic hardware. Reported as is.
  4. ENERGY ESTIMATE with a MEMORY-ACCESS SENSITIVITY (review point 5): compute only (4.6 pJ/MAC, 0.9 pJ/add, 45 nm,
     Horowitz 2014), then + 5 pJ and + 50 pJ per weight/state read for every operation (small / large on-chip SRAM,
     Horowitz 2014; batch = 1, no reuse). Memory narrows the spiking advantage (Dampfhoffer et al., IEEE TETCI 2023).
  5. COST OF THE SIMULATED QUANTUM CHANNEL: operation count of the IQP kernel (state vector of 2^n amplitudes, inner
     products with the m stored benign states) versus the RBF kernel on the same 8 PCA components.
  6. --power_test N: N seconds of continuous V3-SUP inference (tree + network). Read the average "CPU Package Power"
     in HWiNFO during it and during N idle seconds: energy per flow = (P_load - P_idle) / flows_per_s;
     the "< 15 W" claim is about P_load.

  python measure_v3.py --smoke
  python measure_v3.py --s17_dir "D:/revised model/stage1_pw" --target_cache "D:/revised model/cross_out4/ids2018_sample_v4.npz" --out_dir "D:/revised model/efficiency_v3"
  python measure_v3.py ... --power_test 120
"""
import argparse, os, platform, time, types, warnings
import numpy as np
import pandas as pd
import torch
import hybrid_v3 as V
import hybrid_v2 as H
from qkernel import LocalNovelty, novelty_features
from measure_efficiency import lat_ms, port_table_cost

E_MAC, E_ADD = V.E_MAC_PJ, V.E_AC_PJ


def timed(fn, reps):
    return lat_ms(fn, n=reps, warm=min(50, reps // 5 + 1))


def per_thread(fn, reps, nthr_all):
    out = {}
    for nt in sorted({1, nthr_all}):
        torch.set_num_threads(nt)
        out[nt] = timed(fn, reps)
    torch.set_num_threads(nthr_all)
    return out


def throughput(fn, n_rows, reps=5):
    fn()
    t0 = time.perf_counter()
    for _ in range(reps):
        fn()
    return reps * n_rows / (time.perf_counter() - t0)


def novelty_macs(nv, n_feat):
    """multiply-adds per flow of one novelty score (simulation on a classical computer)"""
    prep = n_feat * nv.n                                           # PCA projection (quantile map ~ lookups)
    m = len(nv.Ztr)
    if nv.kind == "rbf":
        return prep + m * (nv.n + 2)
    N = 2 ** nv.n
    pairs = nv.n * (nv.n - 1) // 2
    state = nv.map.reps * N * (nv.n + pairs + 1) + (nv.map.reps - 1) * nv.n * N   # phases, e^(i ph), Hadamards
    return prep + state + m * N * 4                                # complex inner product = 4 real MACs


def energy_table(rows):
    """compute-only and memory-sensitive energy (nJ per flow); every operation reads one weight / state word"""
    out = []
    for r in rows:
        for e_mem in (0.0, 5.0, 50.0):
            p = r["P_mac"] * (E_MAC + e_mem) + r["P_ac"] * (E_ADD + e_mem)
            tot = p + r["other_mac"] * (E_MAC + e_mem)
            out.append(dict(model=r["model"], mem_pJ_per_read=e_mem, P_energy_nJ=p / 1e3, total_energy_nJ=tot / 1e3))
    df = pd.DataFrame(out)
    piv = df.pivot_table(index="mem_pJ_per_read", columns="model", values=["P_energy_nJ", "total_energy_nJ"])
    return df, piv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--target_cache", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--out_dir", default="efficiency_v3")
    ap.add_argument("--reps", type=int, default=1000, help="repetitions for the batch=1 latency")
    ap.add_argument("--power_test", type=int, default=0, help="seconds of continuous V3-SUP inference")
    ap.add_argument("--smoke", action="store_true")
    a0 = ap.parse_args()
    warnings.filterwarnings("ignore")
    os.makedirs(a0.out_dir, exist_ok=True)
    a = types.SimpleNamespace(protocol="cross", target="ids2018", s17_dir=a0.s17_dir, target_cache=a0.target_cache,
                              mode="known", max_train=30000, val_max=10000, tree_train=100000, epochs=6, patience=2,
                              bs=512, lr=2e-3, lb=0.1, qubits=8, q_m=2000, q_nu=0.1)
    if a0.smoke:
        a.epochs, a.max_train, a.val_max, a.tree_train, a.q_m, a.qubits, a0.reps = 2, 3000, 1500, 3000, 300, 6, 100
        D = V.make_smoke("cross")
    else:
        D = V.load_data(a)
    dev, seed = torch.device("cpu"), 0
    nthr = max(1, os.cpu_count() or 1)
    torch.set_num_threads(nthr)
    cpu = platform.processor() or platform.machine()
    print(f"CPU: {cpu} | threads {nthr} | torch {torch.__version__} | reps {a0.reps}", flush=True)

    # ---------------- train exactly as the 'known' task of hybrid_v3.run (seed 0)
    tg = V.build_target(D, a)
    i = H.sub_idx(D["ytr"], a.max_train, seed)
    j = H.sub_idx(D["yva"], a.val_max, seed)
    rest = np.setdiff1d(np.arange(len(D["ytr"])), i)
    k = rest[H.sub_idx(D["ytr"][rest], a.tree_train, seed + 100)]
    from sklearn.ensemble import HistGradientBoostingClassifier
    print("training the tree expert ...", flush=True)
    tree = HistGradientBoostingClassifier(max_iter=200, random_state=seed).fit(D["Xtr"][k], D["ytr"][k])

    def tlogit(M):
        p = np.clip(tree.predict_proba(M)[:, 1], 1e-6, 1 - 1e-6)
        return (np.clip(np.log(p / (1 - p)), -10, 10) / 5).astype("float32")[:, None]

    def cat(X):
        return np.hstack([X, tlogit(X), np.zeros((len(X), 1), "float32")]).astype("float32")

    d = D["Xtr"].shape[1]
    Af = cat(tg["alX"])
    models = {}
    for cfg in ("V3-SUP", "V3-SUP-DENSE"):
        print(f"training {cfg} ...", flush=True)
        models[cfg] = V.fit(cfg, cat(D["Xtr"][i]), D["Str"][i], D["ytr"][i], cat(D["Xva"][j]), D["Sva"][j],
                            D["yva"][j], Af, tg["alS"], seed, a, dev, d)
    nov = {}
    for kind in ("iqp", "rbf"):
        print(f"fitting the novelty model '{kind}' ...", flush=True)
        nv = LocalNovelty(kind, n_qubits=a.qubits, m=a.q_m, nu=a.q_nu, seed=seed)
        nv.fit(novelty_features(tg["nfitX"], tg["nfitS"]))
        nv.set_reference(novelty_features(tg["nrefX"], tg["nrefS"]))
        nov[kind] = nv

    # ---------------- inputs: target-network benign flows (test third)
    nb = min(4096, len(tg["bteX"]))
    BX, BS = tg["bteX"][:nb], tg["bteS"][:nb]
    BXc = cat(BX)
    x1, s1 = BX[:1], BS[:1]
    xf1, xs1 = torch.tensor(BXc[:1]), torch.tensor(BS[:1])
    xfb, xsb = torch.tensor(BXc), torch.tensor(BS)
    F1, Fb = novelty_features(x1, s1), novelty_features(BX, BS)

    print("measuring latency (batch = 1) ...", flush=True)
    parts = {}
    parts["tree (incl. logit)"] = per_thread(lambda: tlogit(x1), min(300, a0.reps), nthr)
    with torch.no_grad():
        for cfg, m in models.items():
            parts[f"{cfg} network"] = per_thread(lambda m=m: m(xf1, xs1), a0.reps, nthr)
    for kind, nv in nov.items():
        parts[f"novelty {kind.upper()}"] = per_thread(lambda nv=nv: nv.percentile(F1), min(300, a0.reps), nthr)
    print("PortTable sequence cost ...", flush=True)
    ptc = port_table_cost(200_000 if a0.smoke else 1_000_000)
    seq = (ptc["seq_ms_single_med"], ptc["seq_ms_single_p95"], np.nan)
    lat_rows = [dict(part=p, med_1thr=v[1][0], p95_1thr=v[1][1], p99_1thr=v[1][2], med_all=v[nthr][0], p95_all=v[nthr][1])
                for p, v in parts.items()]
    lat_rows.append(dict(part="16-minute sequence (PortTable)", med_1thr=seq[0], p95_1thr=seq[1], p99_1thr=np.nan,
                         med_all=np.nan, p95_all=np.nan))
    lat = pd.DataFrame(lat_rows)
    p95 = lat.set_index("part").p95_1thr
    e2e = {"TREE": p95["tree (incl. logit)"],
           "V3-SUP": p95["tree (incl. logit)"] + p95["V3-SUP network"] + p95["16-minute sequence (PortTable)"],
           "V3-SUP-DENSE": p95["tree (incl. logit)"] + p95["V3-SUP-DENSE network"] + p95["16-minute sequence (PortTable)"]}
    e2e["V3-MAX (IQP)"] = e2e["V3-SUP"] + p95["novelty IQP"]
    e2e["V3-MAX-RBF"] = e2e["V3-SUP"] + p95["novelty RBF"]

    print("measuring throughput (batches of 4096) ...", flush=True)
    thr = {"tree": throughput(lambda: tlogit(BX), nb)}
    with torch.no_grad():
        for cfg, m in models.items():
            thr[cfg] = throughput(lambda m=m: m(xfb, xsb), nb)
    for kind, nv in nov.items():
        thr[f"novelty {kind}"] = throughput(lambda nv=nv: nv.percentile(Fb), nb, reps=2)
    comb = lambda *xs: 1 / sum(1 / x for x in xs)
    fps = {"TREE": thr["tree"], "V3-SUP": comb(thr["tree"], thr["V3-SUP"]),
           "V3-SUP-DENSE": comb(thr["tree"], thr["V3-SUP-DENSE"]),
           "V3-MAX (IQP)": comb(thr["tree"], thr["V3-SUP"], thr["novelty iqp"]),
           "V3-MAX-RBF": comb(thr["tree"], thr["V3-SUP"], thr["novelty rbf"])}

    print("energy estimate ...", flush=True)
    en = [dict(model=cfg, **V.energy(m, BXc, BS, dev)) for cfg, m in models.items()]
    en_df, piv = energy_table(en)
    nmac = {kind: novelty_macs(nv, Fb.shape[1]) for kind, nv in nov.items()}

    # ---------------- report
    summ = pd.DataFrame([dict(config=c, end_to_end_p95_ms=e2e[c], flows_per_s=fps[c]) for c in e2e])
    L = [f"EFFICIENCY v3 | CPU {cpu} | threads {nthr} | torch {torch.__version__} | seed 0, 'known' task models",
         "", "latency per part, ms (batch = 1):", lat.round(4).to_string(index=False), "",
         "end-to-end per configuration = sum of the parts' p95 (1 thread; conservative) and throughput:",
         summ.round(3).to_string(index=False), "",
         f"Claim latency < 40 ms: worst end-to-end p95 = {summ.end_to_end_p95_ms.max():.3f} ms -> "
         + ("MET" if summ.end_to_end_p95_ms.max() < 40 else "NOT met"),
         f"Spiking vs dense twin on this CPU: p95 {p95['V3-SUP network']:.3f} vs {p95['V3-SUP-DENSE network']:.3f} ms "
         "(a CPU computes spikes as ordinary numbers; any energy gain needs event-driven neuromorphic hardware)", "",
         "energy estimate per flow (nJ) with memory-access sensitivity (pJ added per weight/state read, one read per "
         "operation):", piv.round(1).to_string(), ""]
    for e_mem in (0.0, 5.0, 50.0):
        r = en_df[en_df.mem_pJ_per_read == e_mem].set_index("model")
        L.append(f"  memory +{e_mem:>4.0f} pJ/read: spiking/dense temporal path "
                 f"{r.loc['V3-SUP', 'P_energy_nJ'] / r.loc['V3-SUP-DENSE', 'P_energy_nJ']:.3f}, whole model "
                 f"{r.loc['V3-SUP', 'total_energy_nJ'] / r.loc['V3-SUP-DENSE', 'total_energy_nJ']:.3f} "
                 "(pre-registered claim <= 0.5)")
    L += ["", "simulated novelty channel, multiply-adds per flow (classical simulation):",
          f"  IQP quantum kernel {nmac['iqp']:,.0f} MAC (~{nmac['iqp'] * E_MAC / 1e3:,.0f} nJ) | RBF kernel "
          f"{nmac['rbf']:,.0f} MAC (~{nmac['rbf'] * E_MAC / 1e3:,.0f} nJ) | ratio {nmac['iqp'] / nmac['rbf']:,.0f}x "
          f"| V3-SUP network {en[0]['other_mac'] + en[0]['P_mac']:,.0f} MAC + {en[0]['P_ac']:,.0f} adds",
          "  (same detection result in all tests; on real quantum hardware the cost would be shots x circuits instead)",
          "", "Energy values are ESTIMATES (45 nm). For a MEASURED value run --power_test with HWiNFO."]
    lat.to_csv(os.path.join(a0.out_dir, "latency_parts.csv"), index=False)
    summ.to_csv(os.path.join(a0.out_dir, "latency_end_to_end.csv"), index=False)
    en_df.to_csv(os.path.join(a0.out_dir, "energy_memory_sensitivity.csv"), index=False)
    pd.DataFrame([dict(cpu=cpu, threads=nthr, torch=torch.__version__, **ptc)]).to_csv(
        os.path.join(a0.out_dir, "environment.csv"), index=False)
    open(os.path.join(a0.out_dir, "report_v3.txt"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))

    if a0.power_test > 0:
        m = models["V3-SUP"]
        print(f"\nPOWER TEST [V3-SUP, tree + network]: start HWiNFO logging NOW (CPU Package Power). "
              f"Running {a0.power_test} s ...", flush=True)
        n, t0 = 0, time.perf_counter()
        with torch.no_grad():
            while time.perf_counter() - t0 < a0.power_test:
                m(torch.tensor(cat(BX)), xsb)                     # includes the tree expert (inside cat)
                n += nb
        rate = n / (time.perf_counter() - t0)
        msg = (f"POWER TEST done: {rate:,.0f} flows/s for {a0.power_test} s. Energy per flow = (P_load - P_idle) / "
               f"{rate:,.0f} J. Measure P_idle for {a0.power_test} s with nothing running. Claim: P_load < 15 W.")
        print(msg)
        open(os.path.join(a0.out_dir, "report_v3.txt"), "a", encoding="utf-8").write("\n" + msg + "\n")


if __name__ == "__main__":
    main()
