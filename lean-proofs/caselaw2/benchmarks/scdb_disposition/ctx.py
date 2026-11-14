#!/usr/bin/env python3
"""Print, for SCDB caseIds, the linked below decision and the context of its citation in our SC opinion text.

python -I ctx.py [--below] caseId ...      (--below also prints the last 1,500 characters of the below decision)
python -I ctx.py --sample N SEED           (N random linked caseIds, for the link audit)
Reads links.tsv, key.tsv, graph/nodes.tsv rows of the nodes involved, texts from git. No model file is read.
"""
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import link as L  # noqa: E402


def rows(p):
    with open(p, encoding="utf-8") as f:
        h = next(f).rstrip("\n").split("\t")
        for line in f:
            yield dict(zip(h, line.rstrip("\n").split("\t")))


def node_rows(ns):
    ns = set(ns)
    out = {}
    with open(L.NODES, encoding="utf-8") as f:
        for line in f:
            i = line.find("\t")
            n = int(line[:i])
            if n in ns:
                out[n] = line.rstrip("\n").split("\t")
                if len(out) == len(ns):
                    break
    return out


def main():
    a = sys.argv[1:]
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    lk = {r["caseId"]: r for r in rows(os.path.join(HERE, "links.tsv"))}
    ky = {r["caseId"]: r for r in rows(os.path.join(HERE, "key.tsv"))}
    show_below = False
    if a and a[0] == "--below":
        show_below = True
        a = a[1:]
    if a and a[0] == "--sample":
        ids = sorted(c for c, r in lk.items() if r["link"] == "linked")
        random.Random(int(a[2])).shuffle(ids)
        a = ids[:int(a[1])]
    ns = []
    for c in a:
        r = lk[c]
        ns += [int(r["sc_node"])] if r["sc_node"] else []
        ns += [int(r["below"])] if r["below"] else []
    nr = node_rows(ns)
    for c in a:
        r, k = lk[c], ky[c]
        print("=" * 100)
        print(c, "|", k["caseName"], "|", k["usCite"], k["dateDecision"], "| disp", k["caseDisposition"], k["class"],
              "| source:", r["source_label"], k["caseSourceState"])
        if not r["sc_node"]:
            print("  no SC node:", r["link"])
            continue
        sn = int(r["sc_node"])
        print("  SC node", sn, nr[sn][6], nr[sn][4], "| link:", r["link"], r["method"])
        if not r["below"]:
            print("  candidates:", r["candidates"])
            continue
        b = int(r["below"])
        br = nr[b]
        print("  BELOW", b, br[1], br[4], br[5][:60], "|", br[6], "|", r["below_court_name"])
        tx = L.fetch("supreme-court", [(sn, nr[sn][2])])[sn]
        head, opening = L.region(tx)
        keys = set()
        for cc in br[5].split("|"):
            keys.update(L.cite_keys(cc))
        for where, t in (("head", head), ("open", opening)):
            for m in L.r6cite.finditer(t):
                if set(L.r6cite.keys(m)) & keys:
                    s = re.sub(r"\s+", " ", t[max(0, m.start() - 350):m.end() + 120])
                    print("  [%s] ...%s..." % (where, s))
        if show_below:
            bt = L.fetch(br[1], [(b, br[2])])[b]
            print("  --- below text tail:", re.sub(r"\s+", " ", bt[-1500:]))


if __name__ == "__main__":
    main()
