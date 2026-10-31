"""
Shortcut check for the window features on CIC-IDS2017 (raw GeneratedLabelledFlows CSVs, CPU, a few minutes).

Question: do the window features detect attack BEHAVIOUR, or do they only recognise the lab's ATTACKER HOSTS?
In CIC-IDS2017 almost every attack is launched from the same few machines. If those machines send (almost) no benign
traffic, then "this source is busy / talks to one server" is a proxy for "this is the attacker machine", and
holding out an attack family does not hold out the attacker's context - the LOO test then cannot show generalisation.

Outputs (report.txt in --out_dir):
 A. per attack label: flows, top source / destination IPs and their shares, top destination port
 B. attacker hosts (sources with >= 1% of some attack label): their benign vs attack flow counts, per day
 C. per attack label: share of its flows sent by a source that has NO benign flow on that day ("pure attacker host")
 D. a trivial IDENTITY rule - "alarm if the source IP is one of the attacker hosts" - recall per label and false-alarm
    rate on benign flows. If this rule already gets ~100% recall at ~0% FPR, CIC-IDS2017 cannot separate behaviour
    from host identity, and any context feature (window counts per source/pair) must be validated host-disjoint or
    cross-dataset.
 E. benign flows in the SAME minute and touching the same host as an attack flow (possible label noise / contamination)

Usage:
  python shortcut_check.py --data_glob "D:/revised model/GeneratedLabelledFlows(1)/**/*.csv" --out_dir shortcut_out
"""
import argparse, glob, os, re
import numpy as np
import pandas as pd

WANT = {"Source_IP", "Destination_IP", "Destination_Port", "Timestamp", "Label"}


def norm(c):
    return re.sub(r"\s+", "_", str(c).strip())


def fix_timestamp(raw):
    ts = pd.to_datetime(raw, errors="coerce", dayfirst=True, format="mixed")
    return ts + pd.to_timedelta(np.where(ts.dt.hour.between(1, 7), 12, 0), unit="h")


def load(pattern):
    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        raise SystemExit(f"no CSV matched: {pattern}")
    parts = []
    for f in files:
        d = pd.read_csv(f, low_memory=False, encoding_errors="replace", usecols=lambda c: norm(c) in WANT)
        d.columns = [norm(c) for c in d.columns]
        d = d[d["Label"].notna()]
        d["label"] = d["Label"].astype(str).str.strip().str.replace(r"[^\x20-\x7E]+", "-", regex=True)
        d["day"] = os.path.basename(f)
        ts = fix_timestamp(d["Timestamp"])
        d["minute"] = ((ts - ts.min()) // pd.Timedelta(minutes=1)).fillna(-1).astype("int64")
        d["benign"] = d["label"].str.upper().isin(["BENIGN", "0"])
        parts.append(d[["day", "minute", "Source_IP", "Destination_IP", "Destination_Port", "label", "benign"]])
        print(f"  {os.path.basename(f)}: {len(d)} flows, {int((~d['benign']).sum())} attack")
    return pd.concat(parts, ignore_index=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_glob", default="D:/revised model/GeneratedLabelledFlows(1)/**/*.csv")
    ap.add_argument("--out_dir", default="shortcut_out")
    ap.add_argument("--host_share", type=float, default=0.01, help="source share that makes an 'attacker host'")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    D = load(a.data_glob)
    ben, att = D[D.benign], D[~D.benign]
    L = []
    say = lambda s="": (print(s), L.append(s))

    say(f"flows {len(D)}  benign {len(ben)}  attack {len(att)}")
    say("\n== A. per attack label: top sources / destinations")
    hosts = set()
    for lab, g in att.groupby("label"):
        s = g["Source_IP"].value_counts(normalize=True)
        t = g["Destination_IP"].value_counts(normalize=True)
        p = g["Destination_Port"].value_counts(normalize=True)
        hosts |= set(s[s >= a.host_share].index)
        say(f"{lab:28s} n={len(g):7d} | src " + ", ".join(f"{i} {v:.0%}" for i, v in s.head(3).items())
            + " | dst " + ", ".join(f"{i} {v:.0%}" for i, v in t.head(3).items())
            + f" | port {p.index[0]} {p.iloc[0]:.0%}"
            + f" | top dst receives {int((ben.Destination_IP == t.index[0]).sum())} benign flows")

    say(f"\n== B. attacker hosts (source share >= {a.host_share:.0%} in some attack label): flows sent, per day")
    for h in sorted(hosts):
        x = D[D.Source_IP == h]
        tab = x.groupby("day")["benign"].agg(benign="sum", total="size")
        tab["attack"] = tab["total"] - tab["benign"]
        say(f"{h}: benign sent {int(tab['benign'].sum())}, attack sent {int(tab['attack'].sum())}, "
            f"benign received {int((ben.Destination_IP == h).sum())}")
        for day, r in tab.iterrows():
            say(f"     {day:55s} benign {int(r.benign):8d}  attack {int(r.attack):8d}")

    say("\n== C. share of each attack label sent by a source with NO benign flow that day ('pure attacker host')")
    ben_src = set(zip(ben.day, ben.Source_IP))
    pure = np.array([(d_, s_) not in ben_src for d_, s_ in zip(att.day, att.Source_IP)])
    for lab, idx in att.groupby("label").indices.items():
        say(f"{lab:28s} {pure[idx].mean():.1%}")

    say("\n== D. trivial identity rule: alarm if Source_IP is an attacker host (from A)")
    in_h_att = att.Source_IP.isin(hosts).values
    fpr = float(ben.Source_IP.isin(hosts).mean())
    say(f"false-alarm rate on ALL benign flows: {fpr:.4%}")
    for lab, idx in att.groupby("label").indices.items():
        say(f"{lab:28s} recall {in_h_att[idx].mean():.3f}")
    say("   (the same rule with Source OR Destination in the host set:)")
    in2 = (att.Source_IP.isin(hosts) | att.Destination_IP.isin(hosts)).values
    say(f"false-alarm rate: {float((ben.Source_IP.isin(hosts) | ben.Destination_IP.isin(hosts)).mean()):.4%}; "
        f"mean recall over labels {np.mean([in2[i].mean() for i in att.groupby('label').indices.values()]):.3f}")

    say("\n== E. benign flows in the same (day, minute) as an attack flow AND sharing its source or destination host")
    k_att = set(zip(att.day, att.minute, att.Source_IP)) | set(zip(att.day, att.minute, att.Destination_IP))
    hit = np.array([(d_, m_, s_) in k_att or (d_, m_, t_) in k_att
                    for d_, m_, s_, t_ in zip(ben.day, ben.minute, ben.Source_IP, ben.Destination_IP)])
    say(f"{int(hit.sum())} benign flows ({hit.mean():.3%} of benign) share minute + host with an attack flow")
    fromh = ben[hit & ben.Source_IP.isin(hosts).values]
    say(f"   of which sent BY an attacker host: {len(fromh)}  (likely unlabelled attack traffic / label noise)")

    say("\nReading guide: if D gives recall ~1 at FPR ~0 for most labels, family-LOO on CIC-IDS2017 cannot tell")
    say("behaviour from attacker identity. Then trust only (i) destination-side window features (--sets flow+dst),")
    say("(ii) a host-disjoint split, or (iii) a cross-dataset test (train 2017 -> test CSE-CIC-IDS2018).")
    open(os.path.join(a.out_dir, "report.txt"), "w", encoding="utf-8").write("\n".join(L))
    print(f"\nsaved -> {os.path.join(a.out_dir, 'report.txt')}")


if __name__ == "__main__":
    main()
