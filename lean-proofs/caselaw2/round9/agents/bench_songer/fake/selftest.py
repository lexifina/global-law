#!/usr/bin/env python3
"""Self-test of benchmarks/songer_treat/score.py on a SYNTHETIC build (no model output is read or scored).

Writes fake/out/status.tsv, fake/out/certs.tsv, fake/data/history.tsv with a deterministic pseudo-random model class
per key unit (plus decoy rows: issue-level rows, rows outside the as-of interval, unrelated nodes), computes the
expected metrics independently, runs score.py --results fake/results, and compares every metric k/n.
"""
import csv
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
BENCH = os.path.join(C2, "benchmarks", "songer_treat")
OUT, DATA, RES = (os.path.join(HERE, d) for d in ("out", "data", "results"))
ASOF = 20261112
CLASSES = ["NEG_HIST", "UNK_HIST", "NEG_OTHER", "UNK_OTHER", "GOOD", "GOOD_ROW", "NONE"]


def pick(node):
    return CLASSES[int(hashlib.sha1(("fake:" + node).encode()).hexdigest(), 16) % len(CLASSES)]


def main():
    for d in (OUT, DATA, RES):
        os.makedirs(d, exist_ok=True)
    with open(os.path.join(BENCH, "key_nodes.tsv"), encoding="utf-8", newline="") as f:
        units = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    hdr = "node\tissue\tholding\tfrom\tto\tstatus\tx6\tx7\twitness\tactor\tpath\n"
    mcls = {}
    with open(os.path.join(OUT, "status.tsv"), "w", encoding="utf-8", newline="\n") as s, \
            open(os.path.join(DATA, "history.tsv"), "w", encoding="utf-8", newline="\n") as h, \
            open(os.path.join(OUT, "certs.tsv"), "w", encoding="utf-8", newline="\n") as c:
        s.write(hdr)
        for i, u in enumerate(units):
            n = u["below_node"]
            k = pick(n)
            mcls[n] = "GOOD" if k in ("GOOD", "GOOD_ROW", "NONE") else k
            # decoys that must be ignored: issue-level negative row, and an expired negative interval
            s.write("\t".join([n, "1", "-", "19000101", "29991231", "neg:reversed", "-", "-", "w", "a",
                               "history"]) + "\n")
            s.write("\t".join([n, "-", "-", "19000101", "20000101", "neg:vacated", "-", "-", "w", "a",
                               "history"]) + "\n")
            if k == "NONE":
                continue
            st, path = {"NEG_HIST": ("neg:reversed", "history"), "UNK_HIST": ("unknown:partial", "history"),
                        "NEG_OTHER": ("neg:overruled", "overruling"), "UNK_OTHER": ("unknown:questioned", "other"),
                        "GOOD": ("good", "-"), "GOOD_ROW": ("good", "history")}[k]
            s.write("\t".join([n, "-", "-", "20000102", "29991231", st, "-", "-", "w", "a", path]) + "\n")
            if path == "history":
                h.write("\t".join(["H%d" % i, n, "999", "19900101", "reversed", "whole"]) + "\n")
                c.write("\t".join(["history", "H%d" % i, "ok"]) + "\n")
        s.write("\t".join(["999999999", "-", "-", "19000101", "29991231", "neg:reversed", "-", "-", "w", "a",
                           "history"]) + "\n")
    expect = {}
    for split in ("h0", "h1", "all"):
        for pop, suf in (("cited", ""), ("any", "_any")):
            us = [u for u in units if (split == "all" or u["half"] == split) and (pop == "any" or u["cited"] == "1")]
            neg = [mcls[u["below_node"]] for u in us if u["class"] == "NEG"]
            part = [mcls[u["below_node"]] for u in us if u["class"] == "PART"]
            clean = [mcls[u["below_node"]] for u in us if u["class"] == "CLEAN"]
            mneg = [u["class"] for u in us if mcls[u["below_node"]] == "NEG_HIST" and u["class"] != "OTHER"]
            e = expect.setdefault(split, {})
            e["recall" + suf] = (sum(m == "NEG_HIST" for m in neg), len(neg))
            e["recall_lenient" + suf] = (sum(m in ("NEG_HIST", "UNK_HIST") for m in neg), len(neg))
            e["precision" + suf] = (sum(x == "NEG" for x in mneg), len(mneg))
            e["precision_lenient" + suf] = (sum(x in ("NEG", "PART") for x in mneg), len(mneg))
            e["clean" + suf] = (sum(m in ("GOOD", "NEG_OTHER", "UNK_OTHER") for m in clean), len(clean))
            e["part" + suf] = (sum(m in ("NEG_HIST", "UNK_HIST") for m in part), len(part))
    r = subprocess.run([sys.executable, "-I", os.path.join(BENCH, "score.py"), "--out", OUT, "--data", DATA,
                        "--label", "fake", "--asof", str(ASOF), "--results", RES], capture_output=True, text=True)
    print(r.stdout, r.stderr)
    if r.returncode:
        sys.exit("score.py failed")
    bad = 0
    for split, e in expect.items():
        got = json.load(open(os.path.join(RES, "fake.%s.json" % split), encoding="utf-8"))
        for k, (kk, nn) in e.items():
            g = got["metrics"][k]
            ok = (g["k"], g["n"]) == (kk, nn)
            bad += not ok
            if not ok:
                print("MISMATCH", split, k, (g["k"], g["n"]), (kk, nn))
        if got["dataset"] != "songer_treat" or got["split"] != split:
            bad += 1
    hs = [json.load(open(os.path.join(RES, "fake.%s.json" % s), encoding="utf-8")) for s in ("h0", "h1", "all")]
    for k in hs[2]["metrics"]:
        if hs[0]["metrics"][k]["n"] + hs[1]["metrics"][k]["n"] != hs[2]["metrics"][k]["n"]:
            bad += 1
            print("HALF SUM MISMATCH", k)
    print("SELFTEST", "PASS" if not bad else "FAIL (%d)" % bad, "units", len(units))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
