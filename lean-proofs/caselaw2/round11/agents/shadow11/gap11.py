"""Diagnosis only (h0-only file, DESIGN11 0.2(b)): the Shadow Docket h0 NEG cases whose Supreme Court order is not in
the corpus (sc_in_corpus = no; round-10 count 281) against the order-list nodes and shadow11's links.
    python -X utf8 round11/agents/shadow11/gap11.py --data round11/data_orders --links work/build11_<tag>_links.tsv
Per gap case: no node with its docket / node present but not a GVR-type disposition / node, no link (why) /
linked to it / linked to another decision. No rule reads this output.
"""
import argparse
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import h0check  # noqa: E402

NL = chr(10)


def dkc(s):
    return re.sub(r"[^0-9a-z]", "", s.lower().replace("no.", ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--links", required=True)
    a = ap.parse_args()
    H = h0check.h0()
    gap = {n: r for n, r in H.items() if r["class"] in ("NEG", "PART") and r["sc_in_corpus"] == "no"}
    by_dk = collections.defaultdict(list)
    with open(os.path.join(a.data, "nodes.tsv"), encoding="utf-8") as f:
        hdr = f.readline().rstrip(NL).split("\t")
        for line in f:
            p = dict(zip(hdr, line.rstrip(NL).split("\t")))
            for d in p["docket"].split(";"):
                by_dk[dkc(d)].append(p)
    lk = {}
    for line in open(a.links, encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        lk[p[0]] = (p[2], p[6], p[4])
    c = collections.Counter()
    yr = collections.Counter()
    for n, r in gap.items():
        y = r["order_date"][:4]
        dks = [dkc(d) for d in re.split(r"[;,| ]+", r["sc_dockets"]) if dkc(d)]
        nodes = [p for d in dks for p in by_dk.get(d, ())]
        if not nodes:
            k = "no_node"
        else:
            res = [lk.get(p["local_id"]) for p in nodes]
            res = [x for x in res if x]
            if not res:
                k = "node_not_built"
            elif any(x[0] == str(n) for x in res):
                k = "linked_right"
            elif any(x[0] != "-" for x in res):
                k = "linked_other"
            else:
                k = "no_link:" + ",".join(sorted({x[1] + "/" + x[2] for x in res}))
        c[k] += 1
        yr[(y, k.split(":")[0])] += 1
    print("gap cases (h0 NEG/PART, order not in corpus):", len(gap))
    for k, v in c.most_common():
        print(v, k)
    for k, v in sorted(yr.items()):
        print(" ", k, v)


if __name__ == "__main__":
    main()
