"""
Efficiency of the hybrid configurations for the proposal claims "latency < 40 ms" and "power < 15 W".
CPU only, about 5-10 minutes. Needs hybrid_v2.py and port_windows.py in the same folder and the same data.

Three separate quantities (the paper must not mix them):
  1. inference LATENCY per flow  - one flow at a time (batch = 1), median / p95 / p99 in ms, 1 thread and all threads,
                                   tree expert included for the H21 configs, plus the cost of building the 16-minute
                                   service-load sequence (PortTable) for one flow.
  2. THROUGHPUT                  - flows per second with batches of 4096 (tree expert included).
  3. ENERGY                      - (a) ESTIMATE from operation counts: MACs x 4.6 pJ (32-bit float multiply-add, 45 nm,
                                   Horowitz ISSCC 2014); spiking branch on neuromorphic hardware: synaptic
                                   accumulates x 0.9 pJ (32-bit add) from the MEASURED spike rate.
                                   (b) MEASUREMENT: --power_test N runs the largest model continuously for N seconds;
                                   read the average "CPU Package Power" in HWiNFO (Windows) during it and during an
                                   idle period -> energy per flow = (P_load - P_idle) / flows_per_s.
Detection DELAY (time until an attack is flagged) is a 4th quantity: up to 60 s, set by the 1-minute windows.

  python measure_efficiency.py --smoke                       (1-2 min, synthetic data, checks that it runs)
  python measure_efficiency.py --s17_dir "D:/revised model/stage1_pw" --cache18 "D:/revised model/cross_out4/ids2018_sample_v4.npz" --out_dir "D:/revised model/efficiency"
  python measure_efficiency.py ... --configs H21-FULL --power_test 120
"""
import argparse, os, platform, time, types, warnings
import numpy as np
import pandas as pd
import torch
import hybrid_v2 as H
from port_windows import PortTable

E_MAC_PJ, E_ADD_PJ = 4.6, 0.9                     # pJ per operation, 45 nm (Horowitz 2014)


def lat_ms(fn, n=1000, warm=50):
    for _ in range(warm):
        fn()
    t = np.empty(n)
    for r in range(n):
        t0 = time.perf_counter(); fn(); t[r] = (time.perf_counter() - t0) * 1000
    return float(np.median(t)), float(np.percentile(t, 95)), float(np.percentile(t, 99))


def flops_per_flow(model, xf, xs):
    try:
        from torch.utils.flop_counter import FlopCounterMode
        with FlopCounterMode(display=False) as fc, torch.no_grad():
            model(xf, xs)
        return fc.get_total_flops() / xf.shape[0]
    except Exception as e:
        print("  flop counter unavailable:", e)
        return np.nan


def lif_ops(model, xf, xs):
    """spike rate of the LIF branch and its operation counts per flow"""
    lif = next((b for b in model.br if isinstance(b, H.LIFTime)), None)
    if lif is None:
        return np.nan, 0.0, 0.0, 0.0
    with torch.no_grad():
        for k in range(0, len(xf), 4096):
            model(torch.tensor(xf[k:k + 4096]), torch.tensor(xs[k:k + 4096]))
    rate = float(lif.last_rate)                                   # last batch; batches are large, close to the mean
    T, C = xs.shape[1], xs.shape[2]
    hid = lif.fc.out_features
    input_macs = T * C * hid                                      # analogue input currents (dense)
    neuron_updates = T * hid                                      # membrane leak + integrate
    spikes = rate * T * hid
    sops = spikes * hid                                           # each spike accumulated into the read-out (fan-out hid)
    return rate, input_macs, neuron_updates, sops


def port_table_cost(n_flows=1_000_000, n_ports=2000, minutes=600, seed=0):
    """ms per flow to build the 16x3 sequence from the per-(port, minute) table (synthetic traffic, same code)"""
    rng = np.random.default_rng(seed)
    port = rng.zipf(1.3, n_flows) % n_ports
    minute = np.sort(rng.integers(0, minutes, n_flows))
    zb = rng.random(n_flows) < 0.1
    t0 = time.perf_counter(); pt = PortTable(port, minute, zb); build = time.perf_counter() - t0
    rows = rng.integers(0, n_flows, 4096)
    pt.sequences(rows)
    t0 = time.perf_counter(); pt.sequences(rows); batch = (time.perf_counter() - t0) / 4096 * 1000
    one = lat_ms(lambda: pt.sequences(rows[:1]), n=300)
    return dict(table_build_s_per_1M_flows=build * 1e6 / n_flows, seq_ms_per_flow_batched=batch,
                seq_ms_single_med=one[0], seq_ms_single_p95=one[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--cache18", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--out_dir", default="efficiency")
    ap.add_argument("--configs", default="TREE,FLOW-MLP,SEQ-GRU,FULL,H21-FLOW,H21-FULL,H21-QD")
    ap.add_argument("--rate", type=float, default=10000, help="flows/s for the estimated average compute power")
    ap.add_argument("--reps", type=int, default=1000, help="repetitions for the batch=1 latency")
    ap.add_argument("--power_test", type=int, default=0, help="seconds of continuous inference (largest config)")
    ap.add_argument("--smoke", action="store_true")
    a0 = ap.parse_args()
    warnings.filterwarnings("ignore")
    os.makedirs(a0.out_dir, exist_ok=True)
    a = types.SimpleNamespace(s17_dir=a0.s17_dir, cache18=a0.cache18, max_train=30000, val_max=10000, epochs=6,
                              patience=2, bs=512, lr=2e-3, tree_train=100000, lb=0.1)
    if a0.smoke:
        D = H.make_smoke(); a.epochs, a.max_train, a.tree_train, a0.reps = 2, 3000, 3000, 100
    else:
        D = H.load_real(a)
    nthr_all = torch.get_num_threads()
    cpu = platform.processor() or platform.machine()
    print(f"CPU: {cpu} | torch threads {nthr_all} | logical cores {os.cpu_count()} | torch {torch.__version__}")
    dev, seed = torch.device("cpu"), 0

    i = H.sub_idx(D["ytr"], a.max_train, seed); j = H.sub_idx(D["yva"], a.val_max, seed)
    Xf, Xs, y = D["Xtr"][i], D["Str"][i], D["ytr"][i]
    Vf, Vs, vy = D["Xva"][j], D["Sva"][j], D["yva"][j]
    from sklearn.ensemble import HistGradientBoostingClassifier
    rest = np.setdiff1d(np.arange(len(D["ytr"])), i)
    k = rest[H.sub_idx(D["ytr"][rest], a.tree_train, seed + 100)]
    tree = HistGradientBoostingClassifier(max_iter=200, random_state=seed).fit(D["Xtr"][k], D["ytr"][k])

    def tlogit(M):
        p = np.clip(tree.predict_proba(M)[:, 1], 1e-6, 1 - 1e-6)
        return (np.clip(np.log(p / (1 - p)), -10, 10) / 5).astype("float32")[:, None]

    ben = np.where(D["lab18"] == "Benign")[0][:20000]
    B18f, B18s = D["X18"][ben], D["S18"][ben]
    nb = min(4096, len(ben))
    t_tree1 = lat_ms(lambda: tree.predict_proba(B18f[:1]), n=min(300, a0.reps))
    t0 = time.perf_counter()
    for _ in range(3):
        tree.predict_proba(B18f[:nb])
    tree_thr = 3 * nb / (time.perf_counter() - t0)
    print("PortTable cost (synthetic 1M flows) ...", flush=True)
    ptc = port_table_cost(200_000 if a0.smoke else 1_000_000)

    rows, models = [], {}
    for cfg in [c.strip() for c in a0.configs.split(",") if c.strip()]:
        if cfg not in H.CONFIGS:
            print("unknown config", cfg); continue
        uses_tree = cfg in H.TREE_CFG
        tf_, vf_, bf_ = (np.hstack([M, tlogit(M)]) if uses_tree else M for M in (Xf, Vf, B18f))
        print(f"[{cfg}] training ...", flush=True)
        m = H.fit(cfg, tf_, Xs, y, vf_, Vs, vy, seed, a, dev, d=D["X18"].shape[1])
        m.eval()
        models[cfg] = (m, bf_, uses_tree)
        params = sum(p.numel() for p in m.parameters())
        x1f, x1s = torch.tensor(bf_[:1]), torch.tensor(B18s[:1])
        lat = {}
        with torch.no_grad():
            for nt in sorted({1, nthr_all}):
                torch.set_num_threads(nt)
                lat[nt] = lat_ms(lambda: m(x1f, x1s), n=a0.reps)
            torch.set_num_threads(nthr_all)
            xb_f, xb_s = torch.tensor(bf_[:nb]), torch.tensor(B18s[:nb])
            m(xb_f, xb_s)
            t0 = time.perf_counter()
            for _ in range(5):
                m(xb_f, xb_s)
            nn_thr = 5 * nb / (time.perf_counter() - t0)
        thr = 1 / (1 / nn_thr + 1 / tree_thr) if uses_tree else nn_thr
        fl = flops_per_flow(m, torch.tensor(bf_[:512]), torch.tensor(B18s[:512]))
        rate, lif_in, lif_upd, sops = lif_ops(m, bf_, B18s)
        macs = fl / 2 if np.isfinite(fl) else np.nan
        e_dense = macs * E_MAC_PJ                                  # pJ/flow, everything on a conventional chip
        # neuromorphic variant: the LIF branch's dense input MACs stay, its spike-driven part becomes accumulates
        e_neuro = (e_dense + (lif_upd + sops) * E_ADD_PJ) if lif_in else np.nan
        tot_p95 = lat[1][1] + (t_tree1[1] if uses_tree else 0.0) + ptc["seq_ms_single_p95"]
        rows.append(dict(config=cfg, params=params,
                         lat1_med_ms=lat[1][0], lat1_p95_ms=lat[1][1], lat1_p99_ms=lat[1][2],
                         latN_med_ms=lat[nthr_all][0], latN_p95_ms=lat[nthr_all][1],
                         tree_p95_ms=t_tree1[1] if uses_tree else 0.0, seq_build_p95_ms=ptc["seq_ms_single_p95"],
                         end_to_end_p95_ms=tot_p95, flows_per_s=thr,
                         MFLOPs_per_flow=fl / 1e6, gru_not_counted="G" in m.names, lif_spike_rate=rate,
                         SOPs_per_flow=sops, energy_nJ_per_flow_est=e_dense / 1e3,
                         energy_nJ_neuromorphic_est=e_neuro / 1e3,
                         compute_mW_at_rate_est=e_dense * 1e-12 * a0.rate * 1e3))
        print(f"  params {params:,} | batch=1 (1 thread) median {lat[1][0]:.3f} ms, p95 {lat[1][1]:.3f} ms | "
              f"end-to-end p95 {tot_p95:.3f} ms | {thr:,.0f} flows/s | {fl / 1e6:.4f} MFLOPs/flow", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(a0.out_dir, "efficiency.csv"), index=False)
    pd.DataFrame([dict(cpu=cpu, threads=nthr_all, torch=torch.__version__, **ptc,
                       tree_flows_per_s=tree_thr, tree_lat_med_ms=t_tree1[0])]).to_csv(
        os.path.join(a0.out_dir, "efficiency_env.csv"), index=False)
    worst = df.end_to_end_p95_ms.max()
    L = [f"EFFICIENCY | CPU {cpu} | torch threads {nthr_all} | torch {torch.__version__}",
         df.round(4).to_string(index=False), "",
         f"16-minute sequence from the PortTable: p95 {ptc['seq_ms_single_p95']:.3f} ms per flow, "
         f"table build {ptc['table_build_s_per_1M_flows']:.2f} s per 1M flows (offline; online it is a counter update)",
         f"Claim latency < 40 ms: worst end-to-end p95 (1 thread) = {worst:.3f} ms -> "
         + ("MET" if worst < 40 else "NOT met"),
         "Energy columns are ESTIMATES (45 nm, Horowitz 2014); the neuromorphic column assumes the spiking branch on",
         "neuromorphic hardware and everything else dense. For a MEASURED value run --power_test with HWiNFO.",
         "Detection delay of the service-load windows: up to 60 s (1-minute windows), report separately."]
    open(os.path.join(a0.out_dir, "report.txt"), "w", encoding="utf-8").write("\n".join(L))
    print("\n".join(L))

    if a0.power_test > 0 and models:
        cfg = max(models, key=lambda c: df.set_index("config").loc[c, "MFLOPs_per_flow"])
        m, bf_, uses_tree = models[cfg]
        xb_f, xb_s = torch.tensor(bf_[:nb]), torch.tensor(B18s[:nb])
        print(f"\nPOWER TEST [{cfg}]: start HWiNFO logging NOW (CPU Package Power). Running {a0.power_test} s ...",
              flush=True)
        n, t0 = 0, time.perf_counter()
        with torch.no_grad():
            while time.perf_counter() - t0 < a0.power_test:
                m(xb_f, xb_s)
                if uses_tree:
                    tree.predict_proba(B18f[:nb])
                n += nb
        fps = n / (time.perf_counter() - t0)
        msg = (f"POWER TEST [{cfg}] done: {fps:,.0f} flows/s for {a0.power_test} s. Energy per flow = "
               f"(P_load - P_idle) / {fps:,.0f}  [J/flow]; also measure P_idle for {a0.power_test} s with nothing running.")
        print(msg)
        open(os.path.join(a0.out_dir, "report.txt"), "a", encoding="utf-8").write("\n\n" + msg)


if __name__ == "__main__":
    main()
