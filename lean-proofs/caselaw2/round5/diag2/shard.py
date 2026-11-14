"""diag2: add a `shard` column to pairs.tsv (pairs of one overruling decision stay together; balanced by weight).

    python shard.py [N]      default 6 shards
"""
import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    p = os.path.join(HERE, "pairs.tsv")
    with open(p, encoding="utf-8", newline="") as f:
        rd = csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        cols = [c for c in rd.fieldnames if c != "shard"]
        rows = list(rd)
    ncand = defaultdict(int)
    cp = os.path.join(HERE, "later_cands.tsv")
    if os.path.exists(cp):
        with open(cp, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                if r["type"] == "both":
                    ncand[r["idx"]] += 1
    groups = defaultdict(list)
    for r in rows:
        groups[r["by_node"]].append(r)
    w = {y: sum(1.0 + (0.4 if r["outcome"] == "c" else 0) + min(ncand[r["idx"]], 10) * 0.05 for r in g)
         for y, g in groups.items()}
    load = [0.0] * n
    for y in sorted(groups, key=lambda y: -w[y]):
        k = load.index(min(load))
        load[k] += w[y]
        for r in groups[y]:
            r["shard"] = str(k + 1)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(cols + ["shard"]) + "\n")
        for r in rows:
            f.write("\t".join(r[c] for c in cols + ["shard"]) + "\n")
    cnt = defaultdict(lambda: defaultdict(int))
    for r in rows:
        cnt[r["shard"]][r["outcome"]] += 1
    for k in sorted(cnt):
        print("shard", k, dict(cnt[k]), "load %.1f" % load[int(k) - 1])


if __name__ == "__main__":
    main()
