"""fjc8: proxy effect of new rows on the FJC h0 cited population (scorer-side only; no rule reads this).

    python -X utf8 proxy_h0.py ROWS.jsonl [ROWS2.jsonl ...]
For every h0 cited unit (district node) touched by a new row: IDB class x the base model class x new row kind/scope.
A unit becomes NEG_HIST when it was not and a new reversed/vacated/all row targets it (approximation: Lean decides).
"""
import collections, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "..", "..", "results", "v3", "bench", "fjc_idb_appeals.h0.cases.tsv")


def main():
    cases = {}
    for l in open(CASES, encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        if p[0] == "dist_node" or p[3] != "1":
            continue
        cases[int(p[0])] = (p[2], p[4], set(int(x) for x in p[13].split(",") if x))
    rows = collections.defaultdict(list)
    for f in sys.argv[1:]:
        for l in open(f, encoding="utf-8"):
            r = json.loads(l)
            rows[r["target"]].append(r)
    c = collections.Counter()
    for d, (cls, mcls, apps) in cases.items():
        rs = rows.get(d, [])
        if not rs:
            continue
        for r in rs:
            same = "app" if r["by"] in apps else "other_by"
            c[(cls, mcls, r["kind"], r["scope"], same)] += 1
    for k, v in sorted(c.items(), key=lambda x: (x[0][0], -x[1])):
        print(v, *k)
    neg = collections.Counter()
    for d, (cls, mcls, apps) in cases.items():
        rs = rows.get(d, [])
        if mcls != "NEG_HIST" and any(r["kind"] in ("reversed", "vacated") and r["scope"] == "all" for r in rs):
            neg[cls] += 1
    print("new NEG_HIST (approx) by IDB class:", dict(neg))


if __name__ == "__main__":
    main()
