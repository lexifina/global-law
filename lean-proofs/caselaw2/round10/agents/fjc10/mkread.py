"""fjc10: reader packs (corpus text only) for a stratified sample of named_other_case / one_side miss pairs.

    python -X utf8 mkread.py work/miss_trace.tsv OUTDIR N_NAMED N_ONESIDE SEED PER_PACK
Items: the appellate opinion's head matter, each citation of the district decision in context (+-900 chars), and the
district decision's caption, court, date, docket and opening text. No key field is written.
"""
import collections, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag10  # noqa: E402
from diag10 import diag  # noqa: E402
import peek10  # noqa: E402
BO, L = diag.BO, diag.L
NL = chr(10)


def item(a, d):
    sidx = diag.shard_index()
    path = os.path.join(L.CACHE, sidx[a] + ".jsonl.gz")
    am = next((m for m in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz") if int(m[0]) == a), None)
    dm = peek10.meta_of(d)
    tx = L.fetch_texts([a, d])
    TA = tx[a][1]
    TD = tx[d][1] if d in tx else ""
    ctx = []
    for n, g in L.decisions(path):
        if n != a:
            continue
        for cw in g["cw"]:
            if cw["j"] != d:
                continue
            c0, c1 = cw["c"]
            ctx.append("[part %s] ...%s[[CITED: %s]]%s..." % (cw["part"], TA[max(0, c0 - 900):c0], TA[c0:c1],
                                                              TA[c1:c1 + 600]))
        break
    return {
        "appellate": {"caption": am[7], "docket": am[5], "date": am[3], "opening": TA[:1800]},
        "cited_decision": {"caption": dm[7] if dm else L.node_row(d)[6], "court": L.node_row(d)[2].split("/")[1],
                           "date": dm[3] if dm else L.node_row(d)[4], "docket": dm[5] if dm else "",
                           "citation": L.node_row(d)[5], "opening": TD[:1200]},
        "citations_in_appellate_opinion": ctx[:3],
    }


def main():
    src, out, nn, no, seed, per = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), \
        int(sys.argv[6])
    rows = [l.rstrip(NL).split("\t") for l in open(src, encoding="utf-8")][1:]
    rng = random.Random(seed)
    pick = []
    for stage, k in (("cand_named_other_case", nn), ("cand_one_side_caption", no)):
        sel = [r for r in rows if r[2] == stage]
        by_dec = collections.defaultdict(list)
        for r in sel:
            by_dec[r[-2][:3]].append(r)   # dist_date decade
        for v in by_dec.values():
            rng.shuffle(v)
        decs = sorted(by_dec)
        i = 0
        got = []
        while len(got) < min(k, len(sel)):
            v = by_dec[decs[i % len(decs)]]
            if v:
                got.append(v.pop())
            i += 1
        pick += [(stage, r) for r in got]
    rng.shuffle(pick)
    os.makedirs(out, exist_ok=True)
    key = []
    for i in range(0, len(pick), per):
        items = []
        for k, (stage, r) in enumerate(pick[i:i + per]):
            iid = "i%02d" % (i + k)
            it = item(int(r[1]), int(r[0]))
            it["item"] = iid
            items.append(it)
            key.append((iid, r[0], r[1], stage))
        with open(os.path.join(out, "items_%d.json" % (i // per)), "w", encoding="utf-8", newline=NL) as f:
            json.dump(items, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "sample.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for k in key:
            f.write("\t".join(k) + NL)
    print(len(pick))


if __name__ == "__main__":
    main()
