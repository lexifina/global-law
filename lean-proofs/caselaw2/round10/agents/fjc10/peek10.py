"""fjc10: show named_other_case / one_side miss pairs (corpus text only): CoA caption/docket, district caption/docket,
the citation in context, the CoA head matter.

    python -X utf8 peek10.py work/miss_trace.tsv STAGE N [seed]
"""
import glob, gzip, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag10  # noqa: E402
from diag10 import diag  # noqa: E402
BO, L = diag.BO, diag.L
NL = chr(10)


def meta_of(n):
    r = L.node_row(n)
    repo = r[1]
    for p in sorted(glob.glob(os.path.join(L.CACHE, repo + "*.meta.tsv.gz"))):
        for m in L.meta_rows(p):
            if int(m[0]) == n:
                return m
    return None


def show(a, d):
    sidx = diag.shard_index()
    tag = sidx.get(a)
    path = os.path.join(L.CACHE, tag + ".jsonl.gz")
    am = None
    for m in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz"):
        if int(m[0]) == a:
            am = m
            break
    dm = meta_of(d)
    print("CoA  %s date=%s docket=%r title=%r" % (a, am[3], am[5], am[7]))
    print("Dist %s date=%s docket=%r title=%r" % (d, dm[3] if dm else "?", dm[5] if dm else "?", dm[7] if dm else L.node_row(d)[6]))
    for n, g in L.decisions(path):
        if n != a:
            continue
        for cw in g["cw"]:
            if cw["j"] != d:
                continue
            w0, wt = cw["w"]
            c0, c1 = cw["c"][0] - w0, cw["c"][1] - w0
            s0, s1 = cw["s"][0] - w0, cw["s"][1] - w0
            print("--- part", cw["part"])
            print(wt[max(0, s0 - 300):c0] + "[[" + wt[c0:c1] + "]]" + wt[c1:s1 + 200])
        z = g["z"] or {}
        if z.get("head"):
            print("=== head:", z["head"][1][:700])
        break


def main():
    rows = [l.rstrip(NL).split("\t") for l in open(sys.argv[1], encoding="utf-8")][1:]
    sel = [r for r in rows if r[2] == sys.argv[2]]
    random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 1).shuffle(sel)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for r in sel[:int(sys.argv[3])]:
        print("\n######", r[0], r[1], r[2], r[3][:200])
        show(int(r[1]), int(r[0]))


if __name__ == "__main__":
    main()
