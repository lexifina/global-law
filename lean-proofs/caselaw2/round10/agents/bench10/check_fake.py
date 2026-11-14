#!/usr/bin/env python3
"""Compare fedcir_dataset score.py output on the synthetic build with fake/expected.json; exit 1 on any mismatch."""
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
        for k, (kk, nn) in e.items():
            g = got["metrics"][k]
            ok = (g["k"], g["n"]) == (kk, nn)
            bad += not ok
            if not ok:
                print("MISMATCH", split, k, (g["k"], g["n"]), "expected", (kk, nn))
        for k in ("link_rate", "link_rate_cited", "link_rate_pre2019"):
            assert k in got["metrics"], k
        assert got["blind"] is True and got["tests"] == "same-case" and got["court"] == "federal"
    print("checks failed:", bad)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
