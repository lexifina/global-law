"""Counts of reader answers and certified doctrine rows by stratum, court group and decade.

    python -X utf8 report_counts.py [--cert cert/treatments_delta.tsv] -> prints; writes work/report_counts.json
"""
import argparse, collections, glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round6/history"))
import r6lib as L  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", default=os.path.join(HERE, "cert", "treatments_delta.tsv"))
    a = ap.parse_args()
    F = L.Facts()
    idx = {}
    for l in open(os.path.join(HERE, "packs", "index.tsv"), encoding="utf-8"):
        p = l.rstrip("\n").split("\t")
        idx[p[1]] = p
    ans = {}
    for p in sorted(glob.glob(os.path.join(HERE, "ans", "*.jsonl"))):
        for l in open(p, encoding="utf-8"):
            l = l.strip()
            if l:
                try:
                    o = json.loads(l)
                    ans[o["id"]] = o
                except (ValueError, KeyError):
                    pass
    out = {}
    st = collections.Counter()
    for k, p in idx.items():
        o = ans.get(k)
        s = p[5]
        if o is None:
            st[s + ":unread"] += 1
            continue
        st[s + ":read"] += 1
        st[s + ":reject"] += bool(o.get("reject"))
        st[s + ":tie"] += bool(o.get("tie"))
        st[s + ":both"] += bool(o.get("reject") and o.get("tie"))
    out["answers"] = dict(sorted(st.items()))

    def group(c):
        if F.is_scotus(c):
            return "scotus"
        if F.system(c) == 0:
            return "federal-other"
        return "state-last-resort" if F.tier(c) == "L" else "state-other"
    rows = []
    if os.path.exists(a.cert):
        for l in open(a.cert, encoding="utf-8"):
            p = l.rstrip("\n").split("\t")
            rows.append(p)
    byg, byd = collections.Counter(), collections.Counter()
    pairs = set()
    for p in rows:
        w, x = int(p[1]), int(p[2])
        pairs.add((w, x))
        c = int(F.court[w])
        byg[group(c)] += 1
        byd["%ds" % (int(F.date[w]) // 100000 * 10)] += 1
    out["cert_rows"] = len(rows)
    out["cert_pairs"] = len(pairs)
    out["by_group"] = dict(byg)
    out["by_decade"] = dict(sorted(byd.items()))
    json.dump(out, open(os.path.join(HERE, "work", "report_counts.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
