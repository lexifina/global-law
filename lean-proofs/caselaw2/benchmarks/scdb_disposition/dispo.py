#!/usr/bin/env python3
"""Print the disposition-looking sentences of SC opinion nodes (for reading disagreements).

python -I dispo.py <sc node> ...
For each node: every sentence (outside the YAML front matter) containing affirm/revers/vacat/dismiss/remand/modif,
with its section heading; at most 14 per node, preferring the head-matter syllabus line and the end of sections.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import link as L  # noqa: E402
import ctx as C  # noqa: E402

CUE = re.compile(r"affirm|revers|vacat|dismiss|remand|modif|set aside", re.I)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ns = [int(x) for x in sys.argv[1:]]
    nr = C.node_rows(ns)
    for n in ns:
        tx = L.fetch("supreme-court", [(n, nr[n][2])])[n]
        if tx.startswith("---"):
            tx = tx[tx.find("\n---", 3) + 4:]
        print("=" * 90)
        print(n, nr[n][4], nr[n][5].split("|")[0], nr[n][6], "chars", len(tx))
        sec = "?"
        hits = []
        for line in tx.split("\n"):
            if line.startswith("## "):
                sec = line[3:40]
                continue
            for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", line):
                if CUE.search(s) and len(s) < 400:
                    hits.append((sec, s.strip()))
        for sec, s in hits[:4] + (hits[-10:] if len(hits) > 14 else hits[4:]):
            print("  [%s] %s" % (sec, s[:300]))


if __name__ == "__main__":
    main()
