"""
Quick inventory of CIC-UNSW-NB15 CICFlowMeter_out.csv (columns, labels, timestamps, IP/port fields). Reads in chunks.
  python inspect_unsw.py "D:/revised model/CIC-UNSW-NB15/CICFlowMeter_out.csv"
"""
import sys
import pandas as pd

path = sys.argv[1]
head = pd.read_csv(path, nrows=5, low_memory=False)
cols = list(head.columns)
print(f"{len(cols)} columns:\n" + ", ".join(cols))
print("\nfirst 3 rows (first 12 columns):\n", head.iloc[:3, :12].to_string())
lab = next((c for c in cols if "label" in c.lower().strip()), cols[-1])
att = next((c for c in cols if c.lower().strip() in ("attack", "attack_cat", "category", "class")), None)
ts = next((c for c in cols if "timestamp" in c.lower()), None)
keys = [c for c in cols if any(k in c.lower().replace(" ", "_") for k in ("src_ip", "dst_ip", "source_ip",
        "destination_ip", "src_port", "dst_port", "source_port", "destination_port", "protocol", "flow_id"))]
print(f"\nlabel column: {lab!r} | attack-category column: {att!r} | timestamp column: {ts!r}\nid columns: {keys}")
counts, cat_counts, n, tmin, tmax, ts_examples = {}, {}, 0, None, None, []
for ch in pd.read_csv(path, usecols=[c for c in [lab, att, ts] if c], chunksize=500_000, low_memory=False):
    n += len(ch)
    for k, v in ch[lab].astype(str).str.strip().value_counts().items():
        counts[k] = counts.get(k, 0) + v
    if att:
        for k, v in ch[att].astype(str).str.strip().value_counts().items():
            cat_counts[k] = cat_counts.get(k, 0) + v
    if ts:
        if len(ts_examples) < 3:
            ts_examples += list(ch[ts].astype(str).head(3))
        t = pd.to_datetime(ch[ts], errors="coerce", dayfirst=True)
        tmin = t.min() if tmin is None else min(tmin, t.min())
        tmax = t.max() if tmax is None else max(tmax, t.max())
print(f"\nrows: {n:,}")
print("label counts:", dict(sorted(counts.items(), key=lambda kv: -kv[1])))
if att:
    print("category counts:", dict(sorted(cat_counts.items(), key=lambda kv: -kv[1])))
if ts:
    print(f"timestamp examples: {ts_examples[:3]} | parsed range: {tmin} -> {tmax}")
