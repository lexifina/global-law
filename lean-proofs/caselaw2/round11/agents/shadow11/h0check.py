"""h0 diagnosis of a set of (order, target) links: for each target that is a Shadow Docket h0 case, its class and the
v10d model class (round10/results/v10d/bench/shadow_docket.h0.cases.tsv, the h0-only file DESIGN11 0.2(b) allows).
    python -X utf8 round11/agents/shadow11/h0check.py LINKS.tsv [cols: order target]
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NL = chr(10)


def h0():
    out = {}
    with open(os.path.join(C2, "round10/results/v10d/bench/shadow_docket.h0.cases.tsv"), encoding="utf-8") as f:
        hdr = f.readline().rstrip(NL).split("\t")
        for line in f:
            p = dict(zip(hdr, line.rstrip(NL).split("\t")))
            out[int(p["node"])] = p
    return out


def main():
    H = h0()
    c = collections.Counter()
    for line in open(sys.argv[1], encoding="utf-8"):
        p = line.rstrip(NL).split("\t")
        if not p[1].isdigit():
            continue
        t = int(p[1])
        if t not in H:
            c["not_h0"] += 1
            continue
        r = H[t]
        c["h0 %s/%s model %s" % (r["class"], r["sub"], r["model_class"])] += 1
    for k, v in sorted(c.items()):
        print(v, k)


if __name__ == "__main__":
    main()
