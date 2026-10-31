"""
count_manifest.py - explains the row-count differences between the earlier runs and writes the first part of the
data manifest (priority 1 of the work plan). Reads files only: nothing is trained, nothing is changed.

A  CIC-IDS2017. Repeats the stage-1 cleaning step by step on the raw CSVs with the code of
   stage1_cicids2017_pipeline.py (its load_raw, then the steps of its clean()) and prints per label:
     raw       rows in the CSVs                      = what shortcut_check.py counted (e.g. DoS Hulk 231,073)
     nan_inf   rows dropped for NaN / inf
     conflict  rows dropped because the same flow features carry two different labels (all copies dropped)
     dup       exact repeats dropped (first copy kept)
     clean     what is left                          = what loo_trees.py / hybrid_v3.py see (e.g. 172,713)
     splits    rows of that label in splits.npz (train + val + test); must equal clean
     if_port   rows that would be left if Destination_Port were part of the duplicate check (what-if only)
B  CIC-IDS2018. Compares the cached 2018 samples: cross_out2 (378,521 rows, first cross_dataset runs) and
   cross_out3 / cross_out4 (378,401 rows, hybrid_v2 / hybrid_v3): rows per label, and how many rows of each label are
   the very same flow as in the sample used by hybrid_v3 (the last file of --caches18).
   Two draws with the same sampling rates give: labels kept whole (small classes) ~100% shared, labels drawn at a
   rate < 1 shared only partly.
C  Manifest: size and SHA-256 of data, caches and code; the locked model files are checked against their
   fingerprints (first 12 hex characters of SHA-256).

Run it in the folder that holds stage1_cicids2017_pipeline.py (D:/revised model):
  python count_manifest.py
  python count_manifest.py --no_raw_hash      (does not hash the raw CSVs, about 9 GB; saves a few minutes)
  python count_manifest.py --skip17           (only parts B and C; part A reads all 2017 CSVs, like stage 1)
Copy the whole printed output back. Everything is also written to --out_dir.
"""
import argparse, glob, hashlib, json, os, re, sys, time
import numpy as np
import pandas as pd

# fingerprints of the versions used for the paper (sha256, first 12 hex characters)
LOCKED = {"hybrid_v3.py": "30721b06ba80", "qkernel.py": "aa1423c82892", "hybrid_v2.py": "a55b7fcf3afe",
          "port_windows.py": "bdff25827432"}
EXPECTED = {"stage1_cicids2017_pipeline.py": "140ec0eb454b", "cross_dataset.py": "71416d6efbcb",
            "fast_novelty.py": "043b785601f9", "bootstrap_ci.py": "fe379e80fe2d", "event_metrics.py": "920bfad1b184",
            "ts_2018.py": "4eb4223e106e", "dump_scores.py": "7f395451426b", "benign_sensitivity.py": "18ee5e1180e5",
            "prep_unsw.py": "4f2e5eebc9aa", "harmonize_unsw.py": "fb3887e8fd87", "shortcut_check.py": "189177de0a85",
            "loo_trees.py": "5198133311d6", "make_figures.py": "4b1ed64bad51", "check_splits17.py": "08dd79e79923"}
# numbers printed by the earlier runs (results 03/04, 06, 08-10, 12-15 of the archive)
REF17 = {"shortcut_check.py (raw CSV)": ("raw", {"DoS Hulk": 231073, "FTP-Patator": 7938, "TOTAL": 2830743}),
         "loo_trees.py (stage-1 output)": ("clean", {"DoS Hulk": 172713, "FTP-Patator": 5931, "TOTAL": 2233030})}

LOG = []


def say(*x):
    s = " ".join(str(v) for v in x)
    print(s, flush=True)
    LOG.append(s)


def sha256(path, chunk=1 << 23):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def sha256_lf(path):
    """hash with Windows line endings turned into \\n: same content, other line endings -> same value"""
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read().replace(b"\r\n", b"\n")).hexdigest()


def counts(lab, mask=None):
    s = pd.Series(lab if mask is None else lab[mask])
    return s.value_counts()


def splits_counts(path):
    z = np.load(path, allow_pickle=True)
    labs = [np.where(z[f"y{s}"] == 0, "BENIGN", z[f"a{s}"].astype(str)) for s in ("tr", "va", "te")]
    return pd.Series(np.concatenate(labs)).value_counts(), [len(v) for v in labs]


# ----------------------------------------------------------------------------- A. CIC-IDS2017
def part_a(a):
    say("\n[A] CIC-IDS2017: stage-1 cleaning repeated step by step")
    sys.path.insert(0, os.path.abspath(a.code_dir))
    try:
        import stage1_cicids2017_pipeline as s1
    except ImportError as e:
        raise SystemExit(f"stage1_cicids2017_pipeline.py not found in {os.path.abspath(a.code_dir)} ({e}); "
                         "run this script in that folder or give --code_dir")
    spl = os.path.join(a.s17_dir, "splits.npz")
    fn = os.path.join(a.s17_dir, "feature_names.json")
    port_kept = None
    if os.path.exists(fn):
        with open(fn) as fh:
            port_kept = "Destination_Port" in json.load(fh)
        say(f"  {fn}: Destination_Port {'IS' if port_kept else 'is NOT'} a feature "
            f"-> the stage-1 run {'did not use' if port_kept else 'used'} --drop_dst_port")
    if port_kept is None:
        port_kept = False
        say("  feature_names.json not found -> assuming --drop_dst_port (as in the final run)")
    t0 = time.time()
    df = s1.load_raw(a.data_glob)             # same reader as stage 1 (window / sequence options do not drop rows)
    say(f"  loaded {len(df):,} rows [{time.time() - t0:.0f}s]")

    # ---- the steps of s1.clean(), unchanged, with the per-label count of every step
    lab_c = next((c for c in df.columns if c.lower() == "label"), None)
    df = df.rename(columns={lab_c: "label"})
    dup_cols = [c for c in df.columns if re.search(r"\.\d+$", c) and re.sub(r"\.\d+$", "", c) in df.columns]
    df = df.drop(columns=dup_cols)
    df = df[df["label"].notna()].reset_index(drop=True)
    attack = (df["label"].astype(str).str.strip().str.replace(r"[^\x20-\x7E]+", "-", regex=True))
    y = (~attack.str.upper().isin(["BENIGN", "0"])).astype(np.int8).values
    lab = np.where(y == 0, "BENIGN", attack.values).astype(object)
    feats = [c for c in df.columns if c not in s1.ID_COLS and c != "label"]
    if not port_kept and "Destination_Port" in feats:
        feats.remove("Destination_Port")
    X = df[feats].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    port = (pd.to_numeric(df["Destination_Port"], errors="coerce").values
            if (not port_kept and "Destination_Port" in df.columns) else None)
    del df
    ok = X.notna().all(axis=1).values
    X = X[ok].reset_index(drop=True)
    lab_ok = lab[ok]
    flow_cols = [c for c in X.columns if not c.startswith(("win_", "pw_", "gl_"))]
    h = pd.util.hash_pandas_object(X[flow_cols], index=False).values
    del X
    tmp = pd.DataFrame({"h": h, "a": lab_ok})
    conflict = (tmp.groupby("h")["a"].transform("nunique") > 1).values
    dup = tmp.duplicated(["h", "a"]).values
    keep = ~(conflict | dup)

    tab = pd.DataFrame({"raw": counts(lab), "nan_inf": counts(lab, ~ok), "conflict": counts(lab_ok, conflict),
                        "dup": counts(lab_ok, dup & ~conflict), "clean": counts(lab_ok, keep)})
    if port is not None:                        # what-if: Destination_Port also in the duplicate check
        p = port[ok]
        okp = ~np.isnan(p)
        h2 = (h * np.uint64(0x9E3779B97F4A7C15)) ^ pd.util.hash_array(np.where(okp, p, -1.0))
        t2 = pd.DataFrame({"h": h2, "a": lab_ok})
        k2 = ~((t2.groupby("h")["a"].transform("nunique") > 1).values | t2.duplicated(["h", "a"]).values) & okp
        tab["if_port"] = counts(lab_ok, k2)
    if os.path.exists(spl):
        sc, sizes = splits_counts(spl)
        tab["splits"] = sc
        say(f"  {spl}: train {sizes[0]:,}  val {sizes[1]:,}  test {sizes[2]:,}  total {sum(sizes):,}")
    tab = tab.fillna(0).astype("int64").sort_values("raw", ascending=False)
    tab.loc["TOTAL"] = tab.sum()
    if "splits" in tab:
        tab["same"] = np.where(tab["clean"] == tab["splits"], "yes", "NO")
    tab.index.name = "label"
    say("\nrows per label at every cleaning step:")
    say(tab.to_string())
    tab.to_csv(os.path.join(a.out_dir, "counts_2017.csv"))

    say("\nnumbers of the earlier reports:")
    for who, (col, ref) in REF17.items():
        for k, v in ref.items():
            got = int(tab.loc[k, col]) if k in tab.index else None
            gs = "-" if got is None else f"{got:,}"
            say(f"  {who:30s} {k:12s} {v:>10,}  this run ({col}) {gs:>10}  "
                + ("same" if got == v else "not in this data" if got is None else "DIFFERENT"))
    if "same" in tab:
        bad = tab.index[tab["same"] == "NO"].tolist()
        if not bad:
            say("VERDICT A: the stage-1 cleaning reproduces splits.npz for every label. The two counts in the reports "
                "are the same data before cleaning (shortcut_check.py reads the raw CSVs) and after it (loo_trees.py "
                "reads the stage-1 output).")
        else:
            say(f"VERDICT A: labels that do NOT match splits.npz: {bad} -> splits.npz was made with other cleaning "
                "options (check --drop_dst_port / --max_train of that run)")
    if a.s17_win and os.path.exists(a.s17_win):
        wc, wsz = splits_counts(a.s17_win)
        mine = tab.drop(index="TOTAL")["clean"]
        mine = mine[mine > 0].sort_index()
        wc = wc.sort_index()
        same = bool(wc.index.equals(mine.index) and (wc.values == mine.values).all())
        say(f"\n  {a.s17_win} (loo_trees.py, cross_out, cross_out2): train {wsz[0]:,} val {wsz[1]:,} test {wsz[2]:,}"
            f" -> rows per label {'IDENTICAL to' if same else 'DIFFERENT from'} the cleaning above")


# ----------------------------------------------------------------------------- B. CIC-IDS2018
def part_b(a):
    say("\n[B] CIC-IDS2018: cached samples")
    paths = [p.strip() for p in a.caches18.split(",") if p.strip()]
    have = [p for p in paths if os.path.exists(p)]
    for p in paths:
        if p not in have:
            say(f"  not found (skipped): {p}")
    if not have:
        say("  no 2018 cache found")
        return
    meta = {}
    for p in have:
        z = np.load(p, allow_pickle=True)
        meta[p] = (list(z["cols"].astype(str)), z.files)
    common = [c for c in meta[have[0]][0] if all(c in meta[p][0] for p in have)]
    say(f"  {len(common)} flow columns in all caches (duplicates were judged on these)")
    keys, labs = {}, {}
    for p in have:
        z = np.load(p, allow_pickle=True)
        cols = meta[p][0]
        X = np.asarray(z["X"], dtype="float64")[:, [cols.index(c) for c in common]]
        lab = z["lab"].astype(str)
        hx = pd.util.hash_pandas_object(pd.DataFrame(X, columns=common), index=False).values
        keys[p] = hx ^ pd.util.hash_array(lab.astype(object))
        labs[p] = lab
        extra = [f for f in meta[p][1] if f not in ("X", "cols", "lab", "missing")]
        say(f"  {p}: {len(lab):,} rows, {len(cols)} columns" + (f", also {extra}" if extra else "")
            + (f", columns filled 0: {list(z['missing'])}" if "missing" in z.files and len(z["missing"]) else ""))
        del X
    ref = have[-1]
    short = {p: os.path.basename(os.path.dirname(p)) or p for p in have}
    if len(set(short.values())) < len(have):          # two caches in one folder -> use the file names
        short = {p: os.path.splitext(os.path.basename(p))[0] for p in have}
    tab = pd.DataFrame({short[p]: pd.Series(labs[p]).value_counts() for p in have})
    for p in have[:-1]:
        shared = np.isin(keys[p], keys[ref])
        tab[f"{short[p]}&{short[ref]}"] = pd.Series(labs[p][shared]).value_counts()
    tab = tab.fillna(0).astype("int64").sort_values(short[ref], ascending=False)
    tab.loc["TOTAL"] = tab.sum()
    for p in have[:-1]:
        c = f"{short[p]}&{short[ref]}"
        tab[f"share_{short[p]}"] = (tab[c] / tab[short[p]].replace(0, np.nan)).round(3)
    tab.index.name = "label"
    say(f"\nrows per label; '&' = rows that are the same flow (all {len(common)} columns + label) in {short[ref]}, "
        f"the sample of hybrid_v2 / hybrid_v3:")
    say(tab.to_string())
    tab.to_csv(os.path.join(a.out_dir, "counts_2018.csv"))
    for p in have[:-1]:
        same = len(keys[p]) == len(keys[ref]) and bool(np.isin(keys[p], keys[ref]).all())
        if same:
            say(f"VERDICT B: {short[p]} and {short[ref]} hold the SAME sample.")
        else:
            sh = tab.loc["TOTAL", f"share_{short[p]}"]
            say(f"VERDICT B: {short[p]} ({len(keys[p]):,}) and {short[ref]} ({len(keys[ref]):,}) are DIFFERENT draws; "
                f"{sh:.1%} of the rows of {short[p]} are also in {short[ref]}. A share near 1 for the small labels "
                "(kept whole) and well below 1 for the labels drawn at a rate < 1 means: same files and sampling "
                "rates, another random draw.")


# ----------------------------------------------------------------------------- C. manifest
def part_c(a):
    say("\n[C] manifest (size, SHA-256)")
    rows = []

    def add(role, path, full=True):
        if not os.path.exists(path):
            rows.append(dict(role=role, path=path, bytes=None, sha256=None, fingerprint=None, check="NOT FOUND"))
            return
        d = sha256(path) if full else None
        rows.append(dict(role=role, path=path, bytes=os.path.getsize(path), sha256=d,
                         fingerprint=d[:12] if d else None,
                         modified=time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(path))), check=""))

    for f in ("splits.npz", "seq17.npz", "feature_names.json", "quantile_transformer.joblib",
              "label_time_windows.csv"):
        add("2017 stage-1 output (hybrid_v3)", os.path.join(a.s17_dir, f))
    if a.s17_win:
        add("2017 stage-1 output (loo_trees, cross_out, cross_out2)", a.s17_win)
    for p in [p.strip() for p in a.caches18.split(",") if p.strip()]:
        add("2018 sample cache", p)
    for p in [p.strip() for p in a.extra.split(",") if p.strip()]:
        add("extra", p)
    for f in sorted(set(LOCKED) | set(EXPECTED)):
        p = os.path.join(a.code_dir, f)
        add("code (locked)" if f in LOCKED else "code", p)
        r = rows[-1]
        want = LOCKED.get(f) or EXPECTED.get(f)
        if r["sha256"]:
            if r["fingerprint"] == want:
                r["check"] = "OK"
            elif sha256_lf(p)[:12] == want:
                r["check"] = "OK (same content, Windows line endings)"
            else:
                r["check"] = f"DIFFERS from {want}" + (" -- LOCKED FILE CHANGED" if f in LOCKED else "")
    for p in sorted(glob.glob(a.data_glob, recursive=True)):
        add("raw CSV (2017)", p, full=not a.no_raw_hash)
    for p in sorted(glob.glob(a.data18)):
        add("raw CSV (2018)", p, full=not a.no_raw_hash)
    m = pd.DataFrame(rows)
    m.to_csv(os.path.join(a.out_dir, "manifest_files.csv"), index=False)
    show = m.assign(name=m["path"].map(os.path.basename), MB=(m["bytes"] / 1e6).round(1))
    say(show[["role", "name", "MB", "fingerprint", "check"]].to_string(index=False))
    lk = m[m["role"] == "code (locked)"]
    ok = len(lk) == len(LOCKED) and lk["check"].astype(str).str.startswith("OK").all()
    say("LOCKED MODEL FILES: " + ("all match the paper version" if ok else "CHECK the lines above"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_glob", default="D:/revised model/GeneratedLabelledFlows(1)/**/*.csv")
    ap.add_argument("--s17_dir", default="D:/revised model/stage1_pw")
    ap.add_argument("--s17_win", default="D:/revised model/stage1_win/splits_win.npz")
    ap.add_argument("--caches18", default="D:/revised model/cross_out2/ids2018_sample.npz,"
                                          "D:/revised model/cross_out3/ids2018_sample_v3.npz,"
                                          "D:/revised model/cross_out4/ids2018_sample_v4.npz",
                    help="comma separated; the LAST one is the sample of hybrid_v3")
    ap.add_argument("--data18", default="D:/revised model/ids2018/*.csv")
    ap.add_argument("--code_dir", default=".")
    ap.add_argument("--extra", default="", help="more files to fingerprint, comma separated (e.g. the UNSW cache)")
    ap.add_argument("--out_dir", default="D:/revised model/manifest")
    ap.add_argument("--skip17", action="store_true", help="skip part A")
    ap.add_argument("--no_raw_hash", action="store_true", help="list the raw CSVs without hashing them")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    say(f"count_manifest.py  {time.strftime('%Y-%m-%d %H:%M')}  python {sys.version.split()[0]}  "
        f"numpy {np.__version__}  pandas {pd.__version__}")
    try:
        if not a.skip17:
            part_a(a)
        part_b(a)
        part_c(a)
    finally:
        with open(os.path.join(a.out_dir, "count_manifest_log.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(LOG) + "\n")
        print(f"\nwritten to {a.out_dir}: counts_2017.csv, counts_2018.csv, manifest_files.csv, count_manifest_log.txt")


if __name__ == "__main__":
    main()
