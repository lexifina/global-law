"""Citation index of corpus decisions dated up to 1930 (the tables end in 1922), streamed from graph/nodes.tsv.

    python -X utf8 build_index.py <out.tsv>

Output rows: key, node, date, system(repo), court, name, cite_as_printed, path (in the repo)
Keys: every candidate key that round6/history/citeforms/r6cite.keys() gives for each citation of the node
(nodes.tsv column 6, citations separated by '|' or '; ').
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(os.path.dirname(HERE))
ROOT = os.path.dirname(BENCH)
sys.path.insert(0, os.path.join(ROOT, "round6", "history", "citeforms"))
import r6cite  # noqa: E402

NODES = os.path.join(os.path.dirname(ROOT), "graph", "nodes.tsv")
MAXD = 19301231


def main(out):
    n = k = 0
    with open(NODES, encoding="utf-8") as f, open(out, "w", encoding="utf-8", newline="\n") as o:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 7:
                continue
            try:
                d = int(p[4])
            except ValueError:
                continue
            if d > MAXD or not p[5]:
                continue
            n += 1
            seen = set()
            for c in re.split(r"\||;\s+", p[5]):
                c = c.strip()
                if not c:
                    continue
                for key in r6cite.keys(c):
                    if key in seen:
                        continue
                    seen.add(key)
                    o.write("\t".join([key, p[0], p[4], p[1], p[3], p[6].replace("\t", " "), c, p[2]]) + "\n")
                    k += 1
    print("nodes", n, "keys", k)


if __name__ == "__main__":
    main(sys.argv[1])
