#!/usr/bin/env python3
"""Self-test of benchmarks/brace_hall_state/score.py on a synthetic build (never a model build).

Builds round9/agents/bench_bh/fake/{out,data}/ from the key: a fake status.tsv / certs.tsv / history.tsv /
treatments.tsv covering every branch of the scorer (NEG_HIST, UNK_HIST, NEG_OTHER, UNK_OTHER, GOOD by no row, rows
that must be ignored: issue-level, holding-level, interval not live at the as-of date, unknown node), runs score.py
with --results into fake/results, and checks every metric against counts computed here independently.
Exit code 0 = pass.
"""
import csv
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BENCH = os.path.join(C2, "benchmarks", "brace_hall_state")
FAKE = os.path.join(HERE, "fake")
OUT, DATA, RES = os.path.join(FAKE, "out"), os.path.join(FAKE, "data"), os.path.join(FAKE, "results")
ASOF = 20261112
CLEAN_M = {"GOOD", "NEG_OTHER", "UNK_OTHER"}


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def main():
    units = rows(os.path.join(BENCH, "key_nodes.tsv"))
    items = [r for r in rows(os.path.join(BENCH, "key.tsv")) if r["key_item"] == "1"]
    rnd = random.Random(20261114)
    # pick a sample covering every class x cited x half
    pick = []
    for c in ("NEG", "PART", "CLEAN"):
        for cited in ("1", "0"):
            for h in ("h0", "h1"):
                pool = [u for u in units if u["class"] == c and u["cited"] == cited and u["half"] == h]
                pick += rnd.sample(pool, min(6, len(pool)))
    kinds = ["NEG_HIST", "UNK_HIST", "NEG_OTHER", "UNK_OTHER", "GOOD", "GOOD_EXPIRED"]
    model = {}  # node -> intended mclass
    for i, u in enumerate(pick):
        model[u["below_node"]] = kinds[i % len(kinds)]
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    hdr = ["node", "issue", "holding", "from", "to", "status", "x6", "x7", "witness", "actor", "path"]
    with open(os.path.join(OUT, "status.tsv"), "w", encoding="utf-8", newline="\n") as s, \
            open(os.path.join(DATA, "history.tsv"), "w", encoding="utf-8", newline="\n") as hf, \
            open(os.path.join(DATA, "treatments.tsv"), "w", encoding="utf-8", newline="\n") as tf, \
            open(os.path.join(OUT, "certs.tsv"), "w", encoding="utf-8", newline="\n") as cf:
        s.write("\t".join(hdr) + "\n")
        for k, (n, m) in enumerate(sorted(model.items())):
            by = "9%06d" % k
            if m == "NEG_HIST":
                s.write("\t".join([n, "-", "-", "19960101", "99991231", "neg:reversed", "-", "-", "h%d" % k, by,
                                   "history"]) + "\n")
                hf.write("\t".join(["h%d" % k, n, by, "19970101", "reversed", "whole"]) + "\n")
                cf.write("history\th%d\tok\n" % k)
            elif m == "UNK_HIST":
                s.write("\t".join([n, "-", "-", "19960101", "99991231", "unknown:partial", "-", "-", "h%d" % k, by,
                                   "history"]) + "\n")
                hf.write("\t".join(["h%d" % k, n, by, "19970101", "reversed", "part"]) + "\n")
            elif m == "NEG_OTHER":
                s.write("\t".join([n, "-", "-", "20000101", "99991231", "neg:overruled", "-", "-", "t%d" % k, by,
                                   "citation"]) + "\n")
                tf.write("\t".join(["t%d" % k, by, n, "20000101", "overruled", "whole"]) + "\n")
            elif m == "UNK_OTHER":
                s.write("\t".join([n, "-", "-", "20000101", "99991231", "unknown:questioned", "-", "-", "t%d" % k,
                                   by, "citation"]) + "\n")
            elif m == "GOOD_EXPIRED":  # a negative interval that ended before the as-of date -> GOOD
                s.write("\t".join([n, "-", "-", "19960101", "20001231", "neg:vacated", "-", "-", "h%d" % k, by,
                                   "history"]) + "\n")
                s.write("\t".join([n, "-", "-", "20010101", "99991231", "good", "-", "-", "-", "-", "-"]) + "\n")
            # rows that must be ignored for every picked node: issue-level and holding-level negatives
            s.write("\t".join([n, "issue1", "-", "19960101", "99991231", "neg:reversed", "-", "-", "x", by,
                               "history"]) + "\n")
            s.write("\t".join([n, "-", "hold1", "19960101", "99991231", "neg:reversed", "-", "-", "x", by,
                               "history"]) + "\n")
        # a node not in the key
        s.write("\t".join(["999999999", "-", "-", "19960101", "99991231", "neg:reversed", "-", "-", "x", "1",
                           "history"]) + "\n")
    expect_m = {n: ("GOOD" if m == "GOOD_EXPIRED" else m) for n, m in model.items()}
    r = subprocess.run([sys.executable, "-I", os.path.join(BENCH, "score.py"), "--out", OUT, "--data", DATA,
                        "--label", "selftest", "--results", RES], capture_output=True, text=True)
    print(r.stdout)
    if r.returncode:
        print(r.stderr)
        return 1
    fails = 0

    def check(name, got, k, n):
        nonlocal fails
        ok = got["k"] == k and got["n"] == n
        fails += not ok
        print("%-28s %s got %d/%d expected %d/%d" % (name, "ok  " if ok else "FAIL", got["k"], got["n"], k, n))

    for split in ("h0", "h1", "all"):
        res = json.load(open(os.path.join(RES, "selftest.%s.json" % split), encoding="utf-8"))
        us = [u for u in units if split == "all" or u["half"] == split]
        its = [i for i in items if split == "all" or i["half"] == split]
        for suffix, pop in (("", [u for u in us if u["cited"] == "1"]), ("_all", us)):
            mc = [(u["class"], expect_m.get(u["below_node"], "GOOD")) for u in pop]
            neg = [m for c, m in mc if c == "NEG"]
            check(split + " recall" + suffix, res["metrics"]["recall" + suffix],
                  sum(m == "NEG_HIST" for m in neg), len(neg))
            check(split + " recall_lenient" + suffix, res["metrics"]["recall_lenient" + suffix],
                  sum(m in ("NEG_HIST", "UNK_HIST") for m in neg), len(neg))
            mneg = [c for c, m in mc if m == "NEG_HIST"]
            check(split + " precision" + suffix, res["metrics"]["precision" + suffix],
                  sum(c == "NEG" for c in mneg), len(mneg))
            check(split + " precision_lenient" + suffix, res["metrics"]["precision_lenient" + suffix],
                  sum(c in ("NEG", "PART") for c in mneg), len(mneg))
            cl = [m for c, m in mc if c == "CLEAN"]
            check(split + " clean" + suffix, res["metrics"]["clean" + suffix], sum(m in CLEAN_M for m in cl), len(cl))
            pt = [m for c, m in mc if c == "PART"]
            check(split + " part" + suffix, res["metrics"]["part" + suffix],
                  sum(m in ("NEG_HIST", "UNK_HIST") for m in pt), len(pt))
        ia = [i for i in its if i["rev_ct"] == "3"]
        check(split + " link_rate", res["metrics"]["link_rate"], sum(i["status"] == "linked" for i in ia), len(ia))
        check(split + " link_rate_cited", res["metrics"]["link_rate_cited"],
              sum(i["status"] == "linked" and i["cited"] == "1" for i in ia), len(ia))
        check(split + " link_rate_all", res["metrics"]["link_rate_all"],
              sum(i["status"] == "linked" for i in its), len(its))
        ok = res["link"]["n_items"] == len(its) and res["court"] == "state" and res["tests"] == "same-case"
        fails += not ok
        print("%-28s %s" % (split + " link/meta", "ok" if ok else "FAIL"))
    # per-case file: every picked node carries its intended class
    cases = {c["below_node"]: c for c in rows(os.path.join(RES, "selftest.cases.tsv"))}
    bad = [n for n, m in expect_m.items() if cases[n]["mclass"] != m]
    fails += bool(bad) + (len(cases) != len(units))
    print("cases.tsv rows %d (units %d); picked nodes with wrong mclass: %d" % (len(cases), len(units), len(bad)))
    seen = {m for m in expect_m.values()}
    print("model classes exercised:", sorted(seen), "| picked units:", len(pick))
    print("SELFTEST", "PASS" if fails == 0 else "FAIL (%d)" % fails)
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
