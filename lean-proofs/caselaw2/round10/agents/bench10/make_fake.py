#!/usr/bin/env python3
"""Synthetic build for the fedcir_dataset score.py self-test (no model output involved).

Writes fake/out/status.tsv, fake/out/certs.tsv, fake/data/history.tsv with statuses chosen by a fixed rule from the
key's own classes, and fake/expected.json with the metric counts that rule implies (computed independently here).
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.join(HERE, "..", "..", "..", "benchmarks", "fedcir_dataset", "key_nodes.tsv")
FAKE = os.path.join(HERE, "fake")


def main():
    os.makedirs(os.path.join(FAKE, "out"), exist_ok=True)
    os.makedirs(os.path.join(FAKE, "data"), exist_ok=True)
    with open(KEY, encoding="utf-8", newline="") as f:
        units = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    # rule by position i within class: NEG -> i%3==0 good, i%3==1 neg history, i%3==2 unknown history
    # CLEAN -> i%4==0 neg history, i%4==1 neg other path, else good; PART -> i%2==0 unknown history, else good
    # plus an expired interval row (to < asof) that must be ignored, and an issue-level row that must be ignored
    pos = {"NEG": 0, "CLEAN": 0, "PART": 0}
    exp = {}
    srows, hrows = [], []
    for u in units:
        c = u["class"]
        i = pos[c]
        pos[c] += 1
        n = u["below_node"]
        if c == "NEG":
            m = ("GOOD", "NEG_HIST", "UNK_HIST")[i % 3]
        elif c == "CLEAN":
            m = "NEG_HIST" if i % 4 == 0 else ("NEG_OTHER" if i % 4 == 1 else "GOOD")
        else:
            m = "UNK_HIST" if i % 2 == 0 else "GOOD"
        u["_m"] = m
        # decoys: expired negative row, issue-level negative row
        srows.append([n, "-", "-", "19000101", "20000101", "neg:reversed", "-", "-", "x", "x", "history"])
        srows.append([n, "i1", "-", "19000101", "20991231", "neg:reversed", "-", "-", "x", "x", "history"])
        if m == "NEG_HIST":
            srows.append([n, "-", "-", "20000102", "20991231", "neg:reversed", "-", "-", "w", "a", "history"])
            hrows.append(["h%s" % n, n, "999", "20100101", "reversed", "-"])
        elif m == "UNK_HIST":
            srows.append([n, "-", "-", "20000102", "20991231", "unknown:history", "-", "-", "w", "a", "history"])
        elif m == "NEG_OTHER":
            srows.append([n, "-", "-", "20000102", "20991231", "neg:overruled", "-", "-", "w", "a", "treatment"])
    with open(os.path.join(FAKE, "out", "status.tsv"), "w", encoding="utf-8", newline="\n") as o:
        o.write("node\tissue\tholding\tfrom\tto\tstatus\tc6\tc7\twitness\tactor\tpath\n")
        for r in srows:
            o.write("\t".join(r) + "\n")
    with open(os.path.join(FAKE, "out", "certs.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for r in hrows:
            o.write("history\t%s\tok\n" % r[0])
    with open(os.path.join(FAKE, "data", "history.tsv"), "w", encoding="utf-8", newline="\n") as o:
        for r in hrows:
            o.write("\t".join(r) + "\n")

    def counts(us):
        neg = [u["_m"] for u in us if u["class"] == "NEG"]
        clean = [u["_m"] for u in us if u["class"] == "CLEAN"]
        part = [u["_m"] for u in us if u["class"] == "PART"]
        mneg = [u["class"] for u in us if u["_m"] == "NEG_HIST"]
        return {
            "recall": [sum(m == "NEG_HIST" for m in neg), len(neg)],
            "recall_lenient": [sum(m in ("NEG_HIST", "UNK_HIST") for m in neg), len(neg)],
            "precision": [sum(c == "NEG" for c in mneg), len(mneg)],
            "precision_lenient": [sum(c in ("NEG", "PART") for c in mneg), len(mneg)],
            "clean": [sum(m in ("GOOD", "NEG_OTHER", "UNK_OTHER") for m in clean), len(clean)],
            "part": [sum(m in ("NEG_HIST", "UNK_HIST") for m in part), len(part)],
        }

    for split in ("h0", "h1", "all"):
        us = [u for u in units if split == "all" or u["half"] == split]
        e = counts([u for u in us if u["cited"] == "1"])
        e.update({k + "_all": v for k, v in counts(us).items()})
        exp[split] = e
    with open(os.path.join(FAKE, "expected.json"), "w", encoding="utf-8", newline="\n") as o:
        json.dump(exp, o, indent=1)
    print("fake units", len(units), "status rows", len(srows))


if __name__ == "__main__":
    main()
