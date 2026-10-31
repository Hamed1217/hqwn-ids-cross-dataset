"""
make_appendix_tables.py - builds the appendix tables of the paper from the files that already exist. Reads files only:
nothing is trained, nothing is changed.

  A1  RUN REGISTRY: every result folder under --root (hybrid_v3 / dump_scores / benign_sensitivity / hybrid_v2 /
      cross_dataset), with the code fingerprint written by the run itself (prereg_v3.txt), protocol, target, scenarios,
      seeds, configurations, number of result rows, saved scores and the analysis files found next to them.
  A2  CIC-IDS2017: rows per label after cleaning in train / validation / test (splits.npz), the cleaning counts of
      count_manifest.py if present, the labels held out in turn at level L2, and the 'tiny' flag (< 50 test flows).
  A3  CSE-CIC-IDS2018 and A4 CIC-UNSW-NB15: rows per attack type in the raw dataset (numbers printed by the earlier
      runs) and in the cleaned sample (counted here from the caches), the 2017 counterpart used at level L4
      (taken from the model code itself), and the 'tiny' flag.
  A5  analysis outputs (efficiency, bootstrap, learning curves, ...) found under --root, with their dates.

Run it in the folder that holds hybrid_v2.py / hybrid_v3.py (D:/revised model):
  python make_appendix_tables.py
Send back the file appendix_tables.md (and the printed output). CSV copies of every table are in --out_dir.
"""
import argparse, glob, json, os, re, sys, time
import numpy as np
import pandas as pd

# raw label counts printed by the earlier runs (cross_dataset.py pass 1 over the 10 CSE-CIC-IDS2018 files;
# inspect_unsw.py over CICFlowMeter_out.csv of CIC-UNSW-NB15)
RAW18 = {"Benign": 13484708, "DDOS attack-HOIC": 686012, "DDoS attacks-LOIC-HTTP": 576191, "DoS attacks-Hulk": 461912,
         "Bot": 286191, "FTP-BruteForce": 193360, "SSH-Bruteforce": 187589, "Infilteration": 161934,
         "DoS attacks-SlowHTTPTest": 139890, "DoS attacks-GoldenEye": 41508, "DoS attacks-Slowloris": 10990,
         "DDOS attack-LOIC-UDP": 1730, "Brute Force -Web": 611, "Brute Force -XSS": 230, "SQL Injection": 87}
RAWUNSW = {"Benign": 3450658, "Exploits": 30951, "Fuzzers": 29613, "Reconnaissance": 16735, "Generic": 4632,
           "DoS": 4467, "Shellcode": 2102, "Backdoor": 452, "Analysis": 385, "Worms": 246}
RESULT_FILES = {"v3_results.csv": "hybrid_v3", "hybrid_v2_results.csv": "hybrid_v2",
                "cross_dataset_results.csv": "cross_dataset"}
ANALYSIS_FILES = ["latency_end_to_end.csv", "energy_memory_sensitivity.csv", "ci_pairs.csv", "learning_curves.csv",
                  "matched_fpr_per_type.csv", "metrics_overall.csv", "event_report.txt", "family_metrics.csv",
                  "sensitivity_report.txt", "fast_novelty_report.txt", "qnoise_report.txt", "check_report.txt"]
SKIP = ("generatedlabelledflows", "ids2018", "_capture_tmp", "__pycache__", "manifest", ".git")
LOG = []


def say(*x):
    s = " ".join(str(v) for v in x)
    print(s, flush=True)
    LOG.append(s)


def md_table(df, title):
    cols = list(df.columns)
    out = [f"### {title}", "", "| " + " | ".join(str(c) for c in cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join("" if pd.isna(v) else (f"{v:,}" if isinstance(v, (int, np.integer)) else str(v))
                                      for v in r.values) + " |")
    return "\n".join(out) + "\n"


def walk(root, depth=3):
    root = os.path.abspath(root)
    for d, sub, files in os.walk(root):
        rel = os.path.relpath(d, root)
        lvl = 0 if rel == "." else rel.count(os.sep) + 1
        sub[:] = [s for s in sub if not s.lower().startswith(SKIP) and lvl < depth]
        yield d, rel, files


def fingerprint(d):
    """code fingerprints written by the run itself (hybrid_v3 main writes prereg_v3.txt)"""
    fp, settings = {}, {}
    p = os.path.join(d, "prereg_v3.txt")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8", errors="replace"):
            m = re.match(r"sha256 (\S+) ([0-9a-f]{64})", line.strip())
            if m:
                fp[m.group(1)] = m.group(2)[:12]
            if line.startswith("settings "):
                try:
                    settings = json.loads(line[len("settings "):])
                except Exception:
                    pass
    js = os.path.join(d, "v3_settings.json")
    if not settings and os.path.exists(js):
        try:
            settings = json.load(open(js))
        except Exception:
            pass
    return fp, settings


def target_name(settings, df, kind):
    if kind == "cross_dataset":
        return "CSE-CIC-IDS2018"
    if kind == "hybrid_v2":
        return "CSE-CIC-IDS2018"
    prot = settings.get("protocol") or (df["protocol"].iloc[0] if "protocol" in df else "")
    if prot == "within":
        return "CIC-IDS2017"
    t = str(settings.get("target", "")) + " " + os.path.basename(str(settings.get("target_cache", "")))
    types = set(df["type"].astype(str)) if "type" in df else set()
    if "unsw" in t.lower() or types & set(RAWUNSW):
        cache = os.path.basename(str(settings.get("target_cache", "")))
        return "CIC-UNSW-NB15" + (" (raw)" if cache.endswith("_v1.npz") else " (harmonised)" if cache.endswith("v1h.npz") else "")
    return "CSE-CIC-IDS2018"


def part_registry(a):
    say("\n[A1] run registry (folders under", os.path.abspath(a.root) + ")")
    rows, extra = [], []
    for d, rel, files in walk(a.root):
        for f in files:
            if f in ANALYSIS_FILES and not any(r in files for r in RESULT_FILES):
                extra.append(dict(folder=rel, file=f, date=time.strftime("%Y-%m-%d %H:%M",
                                                                          time.localtime(os.path.getmtime(os.path.join(d, f))))))
        hit = [f for f in RESULT_FILES if f in files]
        if not hit:
            continue
        f = hit[0]
        kind = RESULT_FILES[f]
        try:
            df = pd.read_csv(os.path.join(d, f))
        except Exception as e:
            say(f"  {rel}: cannot read {f} ({e})")
            continue
        fp, st = fingerprint(d)
        scores = sorted(glob.glob(os.path.join(d, "scores_seed*.npz")))
        parent = os.path.dirname(d)
        if scores:
            kind = "dump_scores"
        if os.path.exists(os.path.join(parent, "sensitivity_report.txt")):
            kind = f"benign_sensitivity ({os.path.basename(d)})"
        seeds = sorted(df["seed"].dropna().astype(int).unique()) if "seed" in df else []
        model_col = "model" if "model" in df else None
        scen = sorted(df["scenario"].astype(str).unique()) if "scenario" in df else []
        type_col = "type" if "type" in df else ("type18" if "type18" in df else None)
        here = [x for x in ANALYSIS_FILES if x in files]
        rows.append(dict(
            folder=rel, script=kind,
            protocol=st.get("protocol") or (df["protocol"].iloc[0] if "protocol" in df else ("cross" if kind != "hybrid_v3" else "")),
            target=target_name(st, df, RESULT_FILES[f]),
            scenarios="+".join(scen), seeds=len(seeds), seed_range=f"{seeds[0]}-{seeds[-1]}" if seeds else "",
            configs=",".join(sorted(df[model_col].astype(str).unique())) if model_col else "",
            types=int(df[type_col].nunique()) if type_col else None, rows=len(df),
            hybrid_v3=fp.get("hybrid_v3.py", ""), qkernel=fp.get("qkernel.py", ""),
            max_train=st.get("max_train", ""), scores_saved="yes" if scores else "",
            analysis_files=",".join(here),
            date=time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(os.path.join(d, f))))))
    R = pd.DataFrame(rows)
    if len(R):
        R = R.sort_values("date").reset_index(drop=True)
        say(R.drop(columns=["analysis_files"]).to_string(index=False))
        R.to_csv(os.path.join(a.out_dir, "A1_run_registry.csv"), index=False)
        noprint = R[(R.script.str.startswith("hybrid_v3")) & (R.hybrid_v3 == "")]
        if len(noprint):
            say(f"  {len(noprint)} hybrid_v3 folders without prereg_v3.txt (fingerprint unknown): {list(noprint.folder)}")
        say("  dump_scores folders have no prereg file of their own: their fingerprint is that of the code in the folder "
            "they were run from; the verify line in their console output shows they reproduced the original run.")
    else:
        say("  no result folders found -> check --root")
    E = pd.DataFrame(extra).sort_values("date") if extra else pd.DataFrame(columns=["folder", "file", "date"])
    if len(E):
        say("\n[A5] analysis outputs without a results table in the same folder:")
        say(E.to_string(index=False))
    E.to_csv(os.path.join(a.out_dir, "A5_analysis_outputs.csv"), index=False)
    return R, E


def part_2017(a, V):
    say("\n[A2] CIC-IDS2017 per label and split")
    spl = os.path.join(a.s17_dir, "splits.npz")
    if not os.path.exists(spl):
        say("  splits.npz not found:", spl)
        return None
    z = np.load(spl, allow_pickle=True)
    cols = {}
    for s, name in (("tr", "train"), ("va", "validation"), ("te", "test")):
        lab = np.where(z[f"y{s}"] == 0, "BENIGN", z[f"a{s}"].astype(str))
        cols[name] = pd.Series(lab).value_counts()
    T = pd.DataFrame(cols).fillna(0).astype("int64")
    cm = os.path.join(a.manifest_dir, "counts_2017.csv")
    if os.path.exists(cm):
        c = pd.read_csv(cm).set_index("label")
        T.insert(0, "raw", c["raw"].reindex(T.index).fillna(0).astype("int64"))
        T.insert(1, "after_cleaning", c["clean"].reindex(T.index).fillna(0).astype("int64"))
    else:
        say("  (counts_2017.csv of count_manifest.py not found: raw / cleaned columns left out)")
    held = set(V.WITHIN_FAMS) if V is not None else {          # copy of hybrid_v3.WITHIN_FAMS
        "DDoS", "PortScan", "DoS Hulk", "DoS GoldenEye", "DoS slowloris", "DoS Slowhttptest", "FTP-Patator",
        "SSH-Patator", "Bot", "Web Attack - Brute Force"}
    T["held_out_in_L2"] = ["yes" if i in held else "" for i in T.index]
    T["tiny_in_test"] = ["yes" if (i != "BENIGN" and T.loc[i, "test"] < 50) else "" for i in T.index]
    T = T.sort_values("train", ascending=False)
    tot = T.select_dtypes("number").sum()
    T.loc["TOTAL"] = list(tot.values) + ["", ""] if len(tot) else None
    T.index.name = "label"
    say(T.to_string())
    T.to_csv(os.path.join(a.out_dir, "A2_cicids2017.csv"))
    return T


def part_target(a, path, raw, cp, name, tag):
    say(f"\n[{tag}] {name}: {path}")
    if not os.path.exists(path):
        say("  cache not found")
        return None, None
    z = np.load(path, allow_pickle=True)
    lab = z["lab"].astype(str)
    s = pd.Series(lab).value_counts()
    T = pd.DataFrame({"raw_dataset": pd.Series(raw), "cleaned_sample": s}).fillna(0).astype("int64")
    T["counterpart_2017_(L4)"] = [("benign" if i.lower() == "benign" else
                                   (" + ".join(cp[i]) if cp.get(i) else "none (L3 only)")) for i in T.index]
    T["tiny"] = ["yes" if (i.lower() != "benign" and T.loc[i, "cleaned_sample"] < 50) else "" for i in T.index]
    T = T.sort_values("cleaned_sample", ascending=False)
    nb = int(T.loc[[i for i in T.index if i.lower() == "benign"], "cleaned_sample"].sum())
    k3 = nb // 3
    thirds = (k3, k3, nb - 2 * k3)
    tot = T[["raw_dataset", "cleaned_sample"]].sum()
    T.loc["TOTAL"] = [int(tot["raw_dataset"]), int(tot["cleaned_sample"]), "", ""]
    T.index.name = "type"
    say(T.to_string())
    say(f"  benign thirds (reference+alignment / calibration / test): {thirds[0]:,} / {thirds[1]:,} / {thirds[2]:,}")
    extra = [k for k in z.files if k not in ("X", "cols", "lab", "missing")]
    say(f"  cache: {len(lab):,} rows, {len(z['cols'])} columns, also {extra}")
    T.to_csv(os.path.join(a.out_dir, f"{tag}_{name.replace(' ', '_')}.csv"))
    return T, thirds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="D:/revised model")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--manifest_dir", default="D:/revised model/manifest")
    ap.add_argument("--cache18", default="D:/revised model/cross_out4/ids2018_sample_v4.npz")
    ap.add_argument("--cacheunsw", default="D:/revised model/unsw/unsw_sample_v1h.npz")
    ap.add_argument("--code_dir", default=".")
    ap.add_argument("--out_dir", default="D:/revised model/manifest/appendix")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    say(f"make_appendix_tables.py  {time.strftime('%Y-%m-%d %H:%M')}")
    sys.path.insert(0, os.path.abspath(a.code_dir))
    V = H = None
    try:
        import hybrid_v2 as H
        import hybrid_v3 as V
    except Exception as e:                                  # mappings then come from the copies below
        say(f"  could not import hybrid_v2 / hybrid_v3 ({e}); using the copies of the counterpart tables in this file")
    cp18 = ({k: ((v,) if v else None) for k, v in H.COUNTERPART.items()} if H is not None else
            {"FTP-BruteForce": ("FTP-Patator",), "SSH-Bruteforce": ("SSH-Patator",),
             "DoS attacks-GoldenEye": ("DoS GoldenEye",), "DoS attacks-Slowloris": ("DoS slowloris",),
             "DoS attacks-Hulk": ("DoS Hulk",), "DoS attacks-SlowHTTPTest": ("DoS Slowhttptest",),
             "DDoS attacks-LOIC-HTTP": ("DDoS",), "DDOS attack-HOIC": None, "DDOS attack-LOIC-UDP": None,
             "Brute Force -Web": ("Web Attack - Brute Force",), "Brute Force -XSS": ("Web Attack - XSS",),
             "SQL Injection": ("Web Attack - Sql Injection",), "Infilteration": ("Infiltration",), "Bot": ("Bot",)})
    cpu = (V.CP["unsw"] if V is not None else
           {"Reconnaissance": ("PortScan",), "DoS": ("DoS Hulk", "DoS GoldenEye", "DoS slowloris", "DoS Slowhttptest", "DDoS")})
    R, E = part_registry(a)
    T17 = part_2017(a, V)
    T18, th18 = part_target(a, a.cache18, RAW18, cp18, "CSE-CIC-IDS2018", "A3")
    TU, thu = part_target(a, a.cacheunsw, RAWUNSW, cpu, "CIC-UNSW-NB15", "A4")

    md = [f"# Appendix tables (generated {time.strftime('%Y-%m-%d %H:%M')} by make_appendix_tables.py)\n"]
    if R is not None and len(R):
        md.append(md_table(R, "A1 Run registry"))
    if T17 is not None:
        md.append(md_table(T17.reset_index(), "A2 CIC-IDS2017 per label and split"))
    if T18 is not None:
        md.append(md_table(T18.reset_index(), f"A3 CSE-CIC-IDS2018 sample (benign thirds {th18[0]:,} / {th18[1]:,} / {th18[2]:,})"))
    if TU is not None:
        md.append(md_table(TU.reset_index(), f"A4 CIC-UNSW-NB15 sample (benign thirds {thu[0]:,} / {thu[1]:,} / {thu[2]:,})"))
    if E is not None and len(E):
        md.append(md_table(E, "A5 Analysis outputs"))
    with open(os.path.join(a.out_dir, "appendix_tables.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    with open(os.path.join(a.out_dir, "appendix_log.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(LOG) + "\n")
    print(f"\nwritten to {a.out_dir}: appendix_tables.md, appendix_log.txt and the CSV tables")


if __name__ == "__main__":
    main()
