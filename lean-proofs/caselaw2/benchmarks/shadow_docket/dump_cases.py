#!/usr/bin/env python3
"""Write reading packets for disagreement review: work/read/<node>.txt.

    python dump_cases.py <label> <nodes file: one node per line>

Each packet: the case row (results/<label>.cases.tsv), the key rows (key.tsv) with the Supreme Court order text from
the dataset, the model's decision-level status rows, the build's history rows that target the node (any kind, with
the admitted flag), the Supreme Court order text(s) found in the corpus by docket number, and the first 6,000
characters of the lower decision's text (git HEAD).
"""
import collections
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sdlib  # noqa: E402
from sdlib import benchlib  # noqa: E402

sys.path.insert(0, os.path.join(sdlib.ROOT, "round6", "history"))
import r6lib as L  # noqa: E402


def main():
    label = sys.argv[1]
    nodes = [x.strip() for x in open(sys.argv[2], encoding="utf-8") if x.strip()]
    out_dir, data_dir = benchlib.BUILDS[label]
    ns = set(nodes)
    cases = {}
    with open(os.path.join(HERE, "results", "%s.cases.tsv" % label), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["node"] in ns:
                cases[r["node"]] = r
    keyrows = collections.defaultdict(list)
    with open(os.path.join(HERE, "key.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["node"] in ns:
                keyrows[r["node"]].append(r)
    dockets = {r["sc_docket"] for v in keyrows.values() for r in v}
    otext = collections.defaultdict(list)
    with open(os.path.join(sdlib.WORK, "orders.tsv"), encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            if r["docket_number"] in dockets:
                otext[r["docket_number"]].append("%s %s/%s: %s" % (r["date"], r["action_class"], r["relief"],
                                                                   r["action_text"]))
    stat = collections.defaultdict(list)
    with open(os.path.join(out_dir, "status.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if p[0] in ns and p[1] == "-" and p[2] == "-":
                stat[p[0]].append(line.rstrip("\n"))
    hist = benchlib.load_history(out_dir, data_dir, ns)
    sc_nodes = {int(x) for v in keyrows.values() for r in v for x in r["sc_node"].split(",") if x}
    texts = L.fetch_texts([int(n) for n in nodes] + list(sc_nodes))
    os.makedirs(os.path.join(sdlib.WORK, "read"), exist_ok=True)
    for n in nodes:
        with open(os.path.join(sdlib.WORK, "read", "%s.txt" % n), "w", encoding="utf-8", newline="\n") as o:
            o.write("== CASE (model %s)\n%s\n\n" % (label, cases.get(n)))
            for r in keyrows[n]:
                o.write("== KEY ROW %s\n%s\n" % (r["sc_docket"], r))
                for t in otext[r["sc_docket"]]:
                    o.write("   ORDER: %s\n" % t)
                for s in r["sc_node"].split(","):
                    if s and int(s) in texts:
                        o.write("   SC ORDER IN CORPUS node %s:\n%s\n" % (s, texts[int(s)][1][:2500]))
            o.write("\n== MODEL STATUS ROWS\n%s\n" % "\n".join(stat[n]))
            o.write("\n== HISTORY ROWS TARGETING NODE\n")
            for h in hist.get(n, []):
                o.write("%s\n" % h)
            o.write("\n== LOWER DECISION TEXT node %s %s\n" % (n, "\t".join(L.node_row(int(n)))))
            if int(n) in texts:
                o.write(texts[int(n)][1][:6000])
            o.write("\n")
    print("wrote", len(nodes))


if __name__ == "__main__":
    main()
