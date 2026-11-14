#!/usr/bin/env python3
"""Synthetic build for the bhk_enbanc score.py self-test (no model output involved).

Writes fake/out/status.tsv, fake/out/certs.tsv, fake/data/history.tsv with statuses chosen by a fixed rule from the
key's own units, decoy rows that must be ignored (expired interval, issue-level row, unknown node ids above the corpus
node count, an unadmitted history row), and fake/expected.json with the metric counts implied (computed independently).
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
KEYDIR = os.path.join(HERE, "..", "..", "..", "benchmarks", "bhk_enbanc")
FAKE = os.path.join(HERE, "fake")
EXTRA = 9000000  # node ids above the corpus node count (staged order nodes)


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def main():
    os.makedirs(os.path.join(FAKE, "out"), exist_ok=True)
    os.makedirs(os.path.join(FAKE, "data"), exist_ok=True)
    units = rd(os.path.join(KEYDIR, "key_nodes.tsv"))
    items = rd(os.path.join(KEYDIR, "key.tsv"))
    srows, hrows, certs = [], [], []
    for i, u in enumerate(units):
        n = u["panel_node"]
        ebc = [x for x in u["eb_confirmed"].split(";") if x not in ("-", "")]
        # rule by position: i%5 0,1 -> NEG_HIST, 2 -> UNK_HIST, 3 -> NEG_OTHER, 4 -> GOOD
        m = ("NEG_HIST", "NEG_HIST", "UNK_HIST", "NEG_OTHER", "GOOD")[i % 5]
        # history 'by': i%5==0 -> confirmed eb node (admitted); i%5==1 -> other node or unadmitted eb row
        by_ok = False
        srows.append([n, "-", "-", "19000101", "19991231", "neg:vacated", "-", "-", "x", "x", "history"])  # expired
        srows.append([n, "i1", "-", "19000101", "20991231", "neg:vacated", "-", "-", "x", "x", "history"])  # issue
        if m == "NEG_HIST":
            srows.append([n, "-", "-", "20000101", "20991231", "neg:vacated", "-", "-", "w", "a", "history"])
            if i % 5 == 0 and ebc:
                hrows.append(["h%s" % n, n, ebc[0], "19900101", "vacated", "-"])
                certs.append("h%s" % n)
                by_ok = True
            elif ebc:
                hrows.append(["h%s" % n, n, ebc[0], "19900101", "vacated", "-"])  # not admitted
                hrows.append(["g%s" % n, n, "12345", "19900101", "vacated", "-"])
                certs.append("g%s" % n)
        elif m == "UNK_HIST":
            srows.append([n, "-", "-", "20000101", "20991231", "unknown:history", "-", "-", "w", "a", "history"])
            if ebc:
                hrows.append(["h%s" % n, n, ebc[0], "19900101", "vacated", "-"])
                certs.append("h%s" % n)
        elif m == "NEG_OTHER":
            srows.append([n, "-", "-", "20000101", "20991231", "neg:overruled", "-", "-", "w", "a", "treatment"])
        u["_m"], u["_by"] = m, by_ok
    for k in range(5):  # unknown nodes: must be ignored
        x = str(EXTRA + k)
        srows.append([x, "-", "-", "19000101", "20991231", "neg:vacated", "-", "-", "w", "a", "history"])
        hrows.append(["x%d" % k, x, "1", "19900101", "vacated", "-"])
        certs.append("x%d" % k)
    with open(os.path.join(FAKE, "out", "status.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("node\tissue\tholding\tfrom\tto\tstatus\tc6\tc7\twitness\tactor\tpath\n")
        for r in srows:
            o.write("\t".join(r) + "\n")
    with open(os.path.join(FAKE, "out", "certs.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for c in certs:
            o.write("history\t%s\tok\n" % c)
    with open(os.path.join(FAKE, "data", "history.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for r in hrows:
            o.write("\t".join(r) + "\n")

    exp = {}
    for split in ("h0", "h1", "all"):
        us = [u for u in units if split == "all" or u["half"] == split]
        its = [r for r in items if split == "all" or r["half"] == split]
        conf = [u for u in us if u["confirmed"] == "1"]

        def rc(xs):
            return [sum(u["_m"] == "NEG_HIST" for u in xs), len(xs)]
        exp[split] = {
            "recall": rc(us),
            "recall_lenient": [sum(u["_m"] in ("NEG_HIST", "UNK_HIST") for u in us), len(us)],
            "recall_R": rc([u for u in us if u["sub"] == "R"]),
            "recall_S": rc([u for u in us if u["sub"] == "S"]),
            "recall_U": rc([u for u in us if u["sub"] == "U"]),
            "recall_confirmed": rc(conf),
            "recall_by_enbanc": [sum(u["_by"] for u in conf), len(conf)],
            "link_rate": [sum(r["status"] == "linked" for r in its), len(its)],
        }
    with open(os.path.join(FAKE, "expected.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(exp, o, indent=1)
    print("fake units", len(units), "status rows", len(srows), "history rows", len(hrows))


if __name__ == "__main__":
    main()
