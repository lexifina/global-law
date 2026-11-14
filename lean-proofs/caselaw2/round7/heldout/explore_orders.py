"""Exploration only (heldout agent): how Shadow Docket (docket, date) entries meet corpus Supreme Court nodes.
Prints aggregate counts only."""
import collections
import csv
import gzip
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", ".."))
CACHE = os.path.join(C2, "round6", "history", "cache")
csv.field_size_limit(10 ** 9)


def norm_docket_tokens(s):
    s = s.replace("–", "-").replace("—", "-").replace("‒", "-")
    out = []
    for part in re.split(r"[;,]|\band\b", s):
        m = re.search(r"(\d{2})\s*-\s*0*(\d+)", part)
        if m:
            out.append("%s-%s" % (m.group(1), m.group(2)))
    return out


def main():
    orders = collections.defaultdict(list)  # docket -> [(date, node, title)]
    n = 0
    for p in sorted(glob.glob(os.path.join(CACHE, "supreme-court*.meta.tsv.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                q = line.rstrip("\n").split("\t")
                if q[4] != "2906" or q[3] < "19930000":
                    continue
                n += 1
                for d in norm_docket_tokens(q[5]):
                    orders[d].append((q[3], q[0], q[7]))
    print("scotus nodes >=1993", n, "dockets", len(orders))
    sd = os.path.join(HERE, "src", "shadow_docket_database_v2-0.csv")
    want = {"GVR", "Reversal", "Affirmed", "DIG", "Certiorari", "Vacate and Remand", "Dismiss", "Lack of Quorum"}
    cnt = collections.Counter()
    diffs = collections.Counter()
    with open(sd, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            ac = r["action_class"]
            if ac not in want:
                continue
            if ac == "Certiorari" and r["cert_granted"] == "1":
                continue
            y = r["date"][:4]
            d = r["date"].replace("-", "")
            m = re.match(r"^(\d{2})-0*(\d+)$", r["docket_number"].strip())
            key = (ac, "gap" if "2006" <= y <= "2009" else ("in" if y <= "2020" else "late"))
            cnt[key + ("all",)] += 1
            if not m:
                cnt[key + ("baddocket",)] += 1
                continue
            dk = "%s-%s" % (m.group(1), m.group(2))
            cands = orders.get(dk, [])
            same = [c for c in cands if c[0] == d]
            if len(same) == 1:
                cnt[key + ("exact1",)] += 1
            elif len(same) > 1:
                cnt[key + ("exactN",)] += 1
            elif cands:
                cnt[key + ("docket_only",)] += 1
                best = min(abs(int(c[0]) - int(d)) for c in cands)
                diffs[min(best, 99999) // 100 if best > 100 else best] += 1
            else:
                cnt[key + ("none",)] += 1
    for k in sorted(cnt):
        print(k, cnt[k])
    print("nearest diffs (docket only)", diffs.most_common(15))


if __name__ == "__main__":
    main()
