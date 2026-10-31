"""
Inventory + attacker-identity check for CSE-CIC-IDS2018 processed CSVs (CPU, reads in chunks - large files are OK).

For every CSV it reports: rows, number of columns, whether Src IP / Dst IP exist, timestamp resolution
(share of timestamps with non-zero seconds), label counts, and repeated header lines (a known glitch of these files).
For the files WITH IP columns it repeats the shortcut test we ran on CIC-IDS2017:
  * how many distinct source hosts each attack label comes from (and how many hosts cover 90% of its flows)
  * the trivial identity rule "alarm if Src IP is one of the attacker hosts": recall per label and false-alarm rate
If attacks come from many hosts and the identity rule has a high false-alarm rate, a host-disjoint / cross-dataset
test on 2018 is meaningful - unlike CIC-IDS2017, where one host (172.16.0.1) explains 12 of 14 attack types.

Usage:
  python ids2018_check.py --data_glob "D:/revised model/CSE-CIC-IDS2018/**/*.csv" --out_dir "D:/revised model/ids2018_check"
"""
import argparse, glob, os, re
from collections import Counter, defaultdict
import numpy as np
import pandas as pd


def norm(c):
    return re.sub(r"\s+", " ", str(c).strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_glob", default="D:/revised model/CSE-CIC-IDS2018/**/*.csv")
    ap.add_argument("--out_dir", default="ids2018_check")
    ap.add_argument("--chunk", type=int, default=500000)
    ap.add_argument("--host_share", type=float, default=0.01)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    files = sorted(glob.glob(a.data_glob, recursive=True))
    if not files:
        raise SystemExit(f"no CSV matched: {a.data_glob}")
    L = []
    say = lambda s="": (print(s, flush=True), L.append(s))

    total = Counter()
    ben_src, att_src = Counter(), defaultdict(Counter)          # benign flows per src ; label -> src -> flows
    for f in files:
        cols = [norm(c) for c in pd.read_csv(f, nrows=0).columns]
        lab_c = next((c for c in cols if c.lower() == "label"), None)
        has_ip = "Src IP" in cols and "Dst IP" in cols
        use = [c for c in (lab_c, "Timestamp", "Src IP", "Dst IP") if c in cols]
        labs, n, nz, nts, hdr = Counter(), 0, 0, 0, 0
        reader = pd.read_csv(f, usecols=lambda c: norm(c) in use, chunksize=a.chunk, low_memory=False,
                             encoding_errors="replace")
        for ch in reader:
            ch.columns = [norm(c) for c in ch.columns]
            rep = ch[lab_c].astype(str).str.strip().str.lower() == "label"       # repeated header lines
            hdr += int(rep.sum())
            ch = ch[~rep & ch[lab_c].notna()]
            lab = ch[lab_c].astype(str).str.strip()
            labs.update(lab.value_counts().to_dict())
            n += len(ch)
            if "Timestamp" in ch:
                ts = pd.to_datetime(ch["Timestamp"], errors="coerce", dayfirst=True, format="mixed")
                ok = ts.notna()
                nts += int(ok.sum()); nz += int((ts[ok].dt.second != 0).sum())
            if has_ip:
                ben = lab.str.upper() == "BENIGN"
                ben_src.update(ch.loc[ben, "Src IP"].astype(str).value_counts().to_dict())
                for l_, g in ch.loc[~ben].groupby(lab[~ben]):
                    att_src[l_].update(g["Src IP"].astype(str).value_counts().to_dict())
        total.update(labs)
        say(f"\n{os.path.basename(f)}: rows {n}, columns {len(cols)}, IP columns: {'YES' if has_ip else 'no'}, "
            f"repeated header lines {hdr}, timestamps with non-zero seconds {nz / max(nts, 1):.1%}")
        for l_, c in labs.most_common():
            say(f"     {l_:32s} {c:9d}")

    say("\n== all files: label totals")
    for l_, c in total.most_common():
        say(f"     {l_:32s} {c:9d}")

    if att_src:
        say("\n== files with IP columns: attacker hosts per label")
        hosts = set()
        for l_, cnt in sorted(att_src.items()):
            tot = sum(cnt.values())
            share = np.array(sorted(cnt.values(), reverse=True)) / tot
            k90 = int(np.searchsorted(np.cumsum(share), 0.9) + 1)
            hosts |= {h for h, c in cnt.items() if c / tot >= a.host_share}
            say(f"{l_:32s} flows {tot:8d} | distinct sources {len(cnt):6d} | hosts covering 90%: {k90:5d} | top "
                + ", ".join(f"{h} {c / tot:.0%}" for h, c in cnt.most_common(3)))
        nb = sum(ben_src.values())
        fp = sum(ben_src.get(h, 0) for h in hosts)
        say(f"\n== trivial identity rule (alarm if Src IP in the {len(hosts)} attacker hosts): "
            f"false-alarm rate on benign {fp / max(nb, 1):.3%} ({fp} of {nb})")
        for l_, cnt in sorted(att_src.items()):
            tot = sum(cnt.values())
            say(f"{l_:32s} recall {sum(c for h, c in cnt.items() if h in hosts) / tot:.3f}")
        say("Reading guide: low FPR + recall ~1 means attacker identity is still a shortcut inside 2018 itself.")
        say("  Few hosts per label  -> like CIC-IDS2017: only the cross-dataset test (train 2017 -> test 2018) is clean.")
        say("  Many hosts per label -> a host-disjoint split (attacker hosts in test never seen in train) is possible.")
    else:
        say("\nno file has Src IP / Dst IP -> window features cannot be built from these CSVs")
    open(os.path.join(a.out_dir, "report.txt"), "w", encoding="utf-8").write("\n".join(L))
    print(f"\nsaved -> {os.path.join(a.out_dir, 'report.txt')}")


if __name__ == "__main__":
    main()
