#!/usr/bin/env python3
"""Compare bhk_enbanc score.py output on the synthetic build with fake/expected.json; exit 1 on any mismatch."""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "fake", "results")


def main():
    exp = json.load(open(os.path.join(HERE, "fake", "expected.json"), encoding="utf-8"))
    bad = 0
    for split, e in exp.items():
        got = json.load(open(os.path.join(RES, "fake.%s.json" % split), encoding="utf-8"))
        if set(got["metrics"]) != set(e):
            print("METRIC SET", split, sorted(got["metrics"]), sorted(e))
            bad += 1
        for k, (kk, nn) in e.items():
            g = got["metrics"].get(k, {"k": None, "n": None})
            ok = (g["k"], g["n"]) == (kk, nn)
            bad += not ok
            if not ok:
                print("MISMATCH", split, k, (g["k"], g["n"]), "expected", (kk, nn))
        if not (got["blind"] is True and got["tests"] == "same-case" and got["court"] == "federal"
                and got["primary"] == "recall" and got["split"] == split and got["dataset"] == "bhk_enbanc"):
            print("HEADER", split)
            bad += 1
        if got["link"]["linked"] != e["link_rate"][0] or got["link"]["n_items"] != e["link_rate"][1]:
            print("LINK", split)
            bad += 1
    with open(os.path.join(RES, "fake.cases.tsv"), encoding="utf-8", newline="") as f:
        cases = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    if any(int(c["panel_node"]) >= 9000000 for c in cases):
        print("UNKNOWN NODE IN CASES")
        bad += 1
    print("cases", len(cases), "checks failed:", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
