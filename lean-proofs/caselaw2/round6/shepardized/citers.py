#!/usr/bin/env python3
"""For the disagreement reading: list, for every linked case that is not a plain CLEAN/GOOD agreement, the later corpus
decisions that cite it (graph/edges.bin: little-endian uint32 pairs citing -> cited), with a party-name overlap flag.

Usage: python -I citers.py [results/<tag>/cases.tsv]
Output next to cases.tsv: citers.tsv
  casenum, target node, citing node, repo, court_id, date, cite, name, shared party tokens, same_case_guess (1 if the
  citing decision is the Supreme Court or the same circuit, is later, and shares a party token)
"""
import array
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = os.path.join(HERE, "..", "..", "..", "graph")
STOP = set("""v vs the of and in re ex parte rel et al inc co corp corporation company ltd united states america state
people commonwealth city county board commissioner commission national association assn dept department a an for to on
by no al la de del el united u s us matter estate administrator secretary director general attorney labor relations
internal revenue insurance bank railroad railway ry r commissioner's""".split())


def toks(name):
    return {t for t in re.findall(r"[a-z]{3,}", name.lower()) if t not in STOP}


def main():
    cases = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "results", "asof20101119", "cases.tsv")
    want = {}
    with open(cases, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["node"] and not (r["sclass"] == "CLEAN" and r["mclass"] == "GOOD"):
                want[int(r["node"])] = r
    cit = {n: [] for n in want}
    path = os.path.join(GRAPH, "edges.bin")
    with open(path, "rb") as f:
        while True:
            b = f.read(8 * 1 << 20)
            if not b:
                break
            a = array.array("I")
            a.frombytes(b)
            for i in range(1, len(a), 2):
                d = a[i]
                if d in cit:
                    cit[d].append(a[i - 1])
    need = set(want)
    for v in cit.values():
        need.update(v)
    meta = {}
    with open(os.path.join(GRAPH, "nodes.tsv"), encoding="utf-8", newline="") as f:
        for line in f:
            i = line.find("\t")
            n = int(line[:i])
            if n in need:
                p = line.rstrip("\r\n").split("\t")
                meta[n] = p
    out = os.path.join(os.path.dirname(cases), "citers.tsv")
    with open(out, "w", encoding="utf-8", newline="\n") as o:
        o.write("casenum\ttarget\tciting\trepo\tcourt_id\tdate\tcite\tname\tshared\tsame_case_guess\n")
        for n, r in want.items():
            tm = meta[n]
            tt = toks(tm[6])
            for c in sorted(set(cit[n]), key=lambda x: meta[x][4] if x in meta else ""):
                m = meta.get(c)
                if not m or m[4] < tm[4] or c == n:
                    continue
                sh = tt & toks(m[6])
                same = int(bool(sh) and (m[1] == "supreme-court" or m[1] == tm[1]))
                o.write("\t".join([r["casenum"], str(n), str(c), m[1], m[3], m[4], m[5], m[6], ",".join(sorted(sh)),
                                   str(same)]) + "\n")
    print("targets", len(want), "written", out)


if __name__ == "__main__":
    main()
