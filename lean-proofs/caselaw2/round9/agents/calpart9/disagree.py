"""calpart9: zone-check disagreements of a rowcheck.tsv (build_zones.py) against a Lean certs.tsv.

    python -X utf8 disagree.py work/v8e [--certs round8/out/v8e/certs.tsv]

A quote is refused by the DESIGN9 section-4 zone check when its row passes (result_all ok*) and no single zone of
its text node contains it with the row's part (main: `part`; joined: `j_part`). Writes <dir>/refused.tsv (rowcheck
columns + result) and prints counts by table / part pair / court / straddle pattern, old map vs new map.
"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import partzone as PZ  # noqa: E402

L = PZ.L
C2 = PZ.C2
NL, TAB = "\n", "\t"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--certs", default=os.path.join(C2, "round8", "out", "v8e", "certs.tsv"))
    a = ap.parse_args()
    res = {}
    with open(a.certs, encoding="utf-8") as f:
        next(f)
        for ln in f:
            p = ln.rstrip(NL).split(TAB)
            if p[0] in ("treatment", "history"):
                res[p[1]] = p[2]
    F = L.Facts()
    cnt = collections.Counter()
    pair = collections.Counter()
    pair_old = collections.Counter()
    court = collections.Counter()
    strad = collections.Counter()
    src = collections.Counter()
    out = open(os.path.join(a.dir, "refused.tsv"), "w", encoding="utf-8", newline=NL)
    for ln in open(os.path.join(a.dir, "rowcheck.tsv"), encoding="utf-8"):
        p = ln.rstrip(NL).split(TAB)
        rid, table, qk, part, zp, zo = p[0], p[1], p[2], p[6], p[7], p[8]
        r = res.get(rid, "absent")
        adm = r.startswith("ok")
        cnt[("rows", table, qk)] += 1
        cnt[("admitted", table, qk)] += adm
        if not adm:
            continue
        if zo != part:
            pair_old[(table, part, zo)] += 1
        if zp == part:
            continue
        cnt[("refused", table, qk)] += 1
        pair[(table, part, zp)] += 1
        court[F.court_name(int(p[12]))] += 1
        if zp == "straddle":
            strad[p[11]] += 1
        out.write(ln.rstrip(NL) + TAB + r + NL)
    out.close()
    for k in sorted(cnt):
        print("%-40s %d" % (" ".join(k), cnt[k]))
    print("\nrefused by (table, row part -> zone part), new map:")
    for k, v in pair.most_common():
        print("  %6d  %s" % (v, " ".join(k)))
    print("\nold map (no PJ) disagreements:", sum(pair_old.values()))
    for k, v in pair_old.most_common(12):
        print("  %6d  %s" % (v, " ".join(k)))
    print("\nstraddle: zone parts overlapped:")
    for k, v in strad.most_common(15):
        print("  %6d  %s" % (v, k))
    print("\ncourts:")
    for k, v in court.most_common(25):
        print("  %6d  %s" % (v, k))


if __name__ == "__main__":
    main()
