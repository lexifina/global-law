"""Counts for courts_validation.md: field values, evidence sources, tier changes v1 -> v2, unit recovery per family.

    python report.py > work/courts/report.txt
"""
import collections, json, os

WORK = os.path.expanduser("~/Documents/us-caselaw-lean-work")
DATA = os.path.join(WORK, "caselaw-lean-2", "data")
WD = os.path.join(WORK, "caselaw-lean-2", "work", "courts")


def main():
    ep = collections.defaultdict(list)
    for line in open(os.path.join(DATA, "courts2.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        ep[int(f[0])].append((int(f[1]), int(f[2]), f[5], int(f[4]), f[3]))
    v1t = {}
    for line in open(os.path.join(WORK, "lean-in-v3/courts.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        v1t[f[0]] = f[2]
    keys = json.load(open(os.path.join(WD, "court_keys.json"), encoding="utf-8"))
    fam = {v: k for k, v in keys["cid_of"].items()}
    vals = {k: collections.Counter() for k in ("bench", "publication", "form")}
    srcs = {k: collections.Counter() for k in ("c", "u", "b", "p", "f")}
    trans = collections.Counter()
    trans_names = collections.Counter()
    unitrec = collections.defaultdict(collections.Counter)
    sha_missing = 0
    n = 0
    scotus_v1 = next(f.split("\t")[0] for f in open(os.path.join(WORK, "lean-in-v3/courts_named.tsv"), encoding="utf-8")
                     if f.split("\t")[1] == "Supreme Court of the United States")
    scot = collections.Counter()
    idchg = collections.Counter()
    alias_ok = set()
    for line in open(os.path.join(DATA, "court_alias.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        alias_ok.add((f[0], f[5]))
    # v1 era-split names: either v1 id of the name may route to either target
    v1name = {}
    for line in open(os.path.join(WORK, "lean-in-v3/courts_named.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        v1name[f[0]] = f[1]
    same_name = collections.defaultdict(set)
    for k, nm in v1name.items():
        same_name[nm].add(k)
    per_tier = collections.Counter()
    with open(os.path.join(DATA, "decisions2.tsv"), encoding="utf-8") as fd, \
            open(os.path.join(WORK, "lean-in-v3/decisions.tsv"), encoding="utf-8") as fv:
        for a, b in zip(fd, fv):
            r = a.rstrip("\n").split("\t")
            v = b.rstrip("\n").split("\t")
            assert r[0] == v[0], (r[0], v[0])
            n += 1
            cid, date = int(r[1]), int(r[2])
            e = next((x for x in ep[cid] if x[0] <= date <= x[1]), ep[cid][-1])
            t2 = e[2]
            t1 = v1t.get(v[1], "T")
            per_tier[t2] += 1
            if v[1] == scotus_v1 or str(cid) == scotus_v1:
                scot[(v[1] == scotus_v1, str(cid) == scotus_v1)] += 1
            if v[1] != r[1]:
                idchg[(v[1], r[1])] += 1
            if t1 != t2:
                trans[(t1, t2)] += 1
                trans_names[(t1, t2, e[4])] += 1
            for k, col in (("bench", 4), ("publication", 5), ("form", 6)):
                vals[k][r[col]] += 1
            src = dict(x.split(":", 1) for x in r[8].split(";"))
            for k in srcs:
                srcs[k][src[k]] += 1
            if r[7] == "-":
                sha_missing += 1
            if cid in fam and fam[cid] in ("FL-DCA", "TX-COA", "CA-COA", "NY-AD", "NY-AT", "LA-COA", "OH-COA",
                                           "IL-APP", "MO-COA", "WA-COA", "AZ-COA", "IN-COA", "OK-COCA", "TN-COA",
                                           "TN-CCA"):
                unitrec[fam[cid]]["total"] += 1
                unitrec[fam[cid]][src["u"] if r[3] != "0" else "none"] += 1
    print("decisions", n, "sha missing", sha_missing)
    print("SCOTUS check (v3 court is SCOTUS, decisions2 court is SCOTUS id %s):" % scotus_v1, dict(scot))
    bad = {k: m for k, m in idchg.items()
           if not any((x, k[1]) in alias_ok for x in same_name.get(v1name.get(k[0], ""), {k[0]}))}
    print("court_id changes v3 -> v2: %d decisions in %d id pairs; unexplained by court_alias.tsv: %d decisions"
          % (sum(idchg.values()), len(idchg), sum(bad.values())))
    for k, m in sorted(bad.items(), key=lambda x: -x[1])[:20]:
        print("  unexplained", k, m)
    print("tier (v2)", dict(per_tier))
    for k, c in vals.items():
        print("\n##", k)
        for x, m in c.most_common():
            print("  %s\t%d" % (x, m))
    for k, c in srcs.items():
        print("\n## src", k)
        for x, m in c.most_common(30):
            print("  %s\t%d" % (x, m))
    print("\n## tier changes v1 -> v2 (decisions)")
    for (a, b), m in trans.most_common():
        print("  %s -> %s\t%d" % (a, b, m))
    print("\n## tier changes by court epoch")
    for (a, b, nm), m in trans_names.most_common(60):
        print("  %s -> %s\t%d\t%s" % (a, b, m, nm))
    print("\n## unit recovery")
    for f, c in sorted(unitrec.items()):
        tot = c["total"]
        rec = tot - c["none"]
        print("  %s\ttotal %d\trecovered %d (%.1f%%)\t%s" % (f, tot, rec, 100 * rec / max(tot, 1),
              ", ".join("%s %d" % (k, m) for k, m in c.most_common() if k not in ("total", "none"))))


if __name__ == "__main__":
    main()
