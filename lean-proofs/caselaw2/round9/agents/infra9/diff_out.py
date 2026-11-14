"""infra9: line-level difference of two Lean output folders (multiset of lines per table; summary.tsv without the
timing lines). Prints counts per table and up to --show lines removed (-) / added (+).

    python -X utf8 round9/agents/infra9/diff_out.py <dir A (reference)> <dir B> [--show 40]
"""
import argparse
import collections
import os

TABLES = ("status", "certs", "classes", "findings", "splits", "horty", "status_lines", "summary")


def lines(p, t):
    f = os.path.join(p, t + ".tsv")
    if not os.path.exists(f):
        return None
    with open(f, encoding="utf-8") as fh:
        ls = fh.read().split("\n")
    if t == "summary":
        ls = [l for l in ls if not (l.startswith("load_ms\t") or l.startswith("run_ms\t"))]
    return collections.Counter(ls)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--show", type=int, default=40)
    a = ap.parse_args()
    for t in TABLES:
        x, y = lines(a.a, t), lines(a.b, t)
        if x is None or y is None:
            print("%-13s missing in %s" % (t, "A" if x is None else "B"))
            continue
        rem, add = x - y, y - x
        nr, na = sum(rem.values()), sum(add.values())
        print("%-13s -%d +%d" % (t, nr, na))
        if t == "summary":
            rem = collections.Counter({k: v for k, v in rem.items()})
        shown = 0
        for sign, c in (("-", rem), ("+", add)):
            for l in sorted(c):
                if shown >= a.show:
                    break
                print("   %s %s" % (sign, l[:300]))
                shown += 1


if __name__ == "__main__":
    main()
