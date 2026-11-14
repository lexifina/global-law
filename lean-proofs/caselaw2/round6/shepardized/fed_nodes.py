#!/usr/bin/env python3
"""Stream graph/nodes.tsv and keep every node whose citation column holds an F.2d or F.3d citation.

Output work/fed_nodes.tsv: key (e.g. "842 f2d 556"), node, court_id, date, repo, path, name, cite column.
A node with several citations in its cite column gets one line per F.2d/F.3d citation.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPH = os.path.join(HERE, "..", "..", "..", "graph")
CITE = re.compile(r"\b(\d{1,4}) F\. ?(2d|3d) (\d{1,5})\b")


def main():
    nodes = sys.argv[1] if len(sys.argv) > 1 else os.path.join(GRAPH, "nodes.tsv")
    n = k = 0
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    with open(nodes, encoding="utf-8", newline="") as f, \
            open(os.path.join(HERE, "work", "fed_nodes.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for line in f:
            n += 1
            if " F." not in line:
                continue
            p = line.rstrip("\r\n").split("\t")
            if len(p) < 7:
                continue
            seen = set()
            for m in CITE.finditer(p[5] + " ; " + (p[7] if len(p) > 7 else "")):
                key = "%d f%s %d" % (int(m.group(1)), m.group(2), int(m.group(3)))
                if key in seen:
                    continue
                seen.add(key)
                o.write("\t".join([key, p[0], p[3], p[4], p[1], p[2], p[6], p[5], p[7] if len(p) > 7 else ""]) + "\n")
                k += 1
    print("nodes read", n, "F.2d/F.3d lines written", k)


if __name__ == "__main__":
    main()
