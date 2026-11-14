"""fjc9: why does the F1 linker (fjc8, as installed in v8e) not link a (district, appellate) pair?

    python -X utf8 f1why.py work/miss_trace.tsv work/f1why.tsv

Runs fjc_link.select / finish on the appellate opinion and records the drop reasons logged for it (select-level
reasons carry no target) and for the district node. Pairs come from the h0 per-case file (case identity only).
"""
import collections, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fjc_link as FL  # noqa: E402
from fjc_link import BO, L, diag  # noqa: E402

NL = chr(10)


def main(src, dst):
    rows = list(csv.reader(open(src, encoding="utf-8"), delimiter="\t"))[1:]
    FL.init()
    sidx = diag.shard_index()
    by_shard = collections.defaultdict(list)
    for r in rows:
        d, a = int(r[0]), int(r[1])
        by_shard[sidx.get(a, "-")].append((d, a, r[2]))
    out = []
    for tag, items in sorted(by_shard.items()):
        if tag == "-":
            for d, a, s in items:
                out.append((d, a, s, "no_shard"))
            continue
        path = os.path.join(L.CACHE, tag + ".jsonl.gz")
        want = {a for _, a, _ in items}
        meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz") if int(p[0]) in want}
        groups = {n: g for n, g in L.decisions(path) if n in want}
        texts = L.fetch_texts(sorted(want & set(groups)))
        for d, a, s in items:
            g = groups.get(a)
            if g is None or not g["cw"]:
                out.append((d, a, s, "no_record"))
                continue
            FL.G["why"] = []
            st = collections.Counter()
            try:
                cs = FL.select(a, g, meta.get(a), st)
                res = []
                for c in cs:
                    if a in texts:
                        T = L.norm(texts[a][1])
                        res.append((c[0], FL.finish(a, g, T, c, st)))
            except Exception as ex:  # noqa: BLE001
                out.append((d, a, s, "error:%r" % ex))
                continue
            why = [k for n, j, k in FL.G.get("why", []) if j in (None, d)]
            other = [str(c[0]) for c in cs if c[0] != d]
            if any(j == d and r for j, r in res):
                why.append("ROW")
            if other:
                why.append("cand_other:" + ",".join(other))
            out.append((d, a, s, ";".join(why) or "none"))
    with open(dst, "w", encoding="utf-8", newline=NL) as f:
        for r in out:
            f.write("\t".join(str(x) for x in r) + NL)
    c = collections.Counter((r[2], r[3].split(";")[0]) for r in out)
    for k, v in c.most_common(60):
        print(v, k)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
