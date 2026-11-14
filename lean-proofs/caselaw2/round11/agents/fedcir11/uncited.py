"""fedcir11: Federal Circuit / CCPA opinions with an own judgment line and no cited decision of a reviewed tribunal of
their caption, that caption-match (round 6 cap 2) a corpus decision of a reviewed tribunal dated 0..5 years before.

    python -X utf8 uncited.py   -> work/uncited.tsv
Per pair: tribunal class, gap, judgment line (round 6 decide), docket tie (the tribunal decision's docket number
printed in the acting text), whether the acting text prints the tribunal's name, and J's v10d status.
"""
import collections, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fedcir_link as FC  # noqa: E402
from fedcir_link import BO, L  # noqa: E402

NL = chr(10)


def main():
    FC.init()
    F, N = BO.G["F"], BO.G["N"]
    import numpy as np
    court = np.asarray(F.court)
    trib = {}
    for c in (651, 656, 657):
        for j in np.nonzero(court == c)[0].tolist():
            trib[j] = c
    # captions + dockets of tribunal decisions from the cache meta
    meta = {}
    for p in L.shards(".meta.tsv.gz"):
        b = os.path.basename(p)
        if not b.startswith(("federal-special.", "cafc.")):
            continue
        for r in L.meta_rows(p):
            n = int(r[0])
            if n in trib or int(r[4]) in FC.ACT:
                meta[n] = r
    idx = collections.defaultdict(list)
    for j in trib:
        nm = N.name(j)
        for t in BO.caption(nm)[0]:
            idx[t].append(j)
    st = collections.Counter()
    status = collections.defaultdict(list)
    with open(os.path.join(FC.C2, "round10", "out", "v10d", "status.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) > 9 and p[1] == "-" and int(p[0]) in trib and p[5] != "good":
                status[int(p[0])].append(p[5] + "@" + p[9])
    pairs = []
    acting = []
    for path in L.shards():
        b = os.path.basename(path)
        if not b.startswith(("cafc.", "federal-special.0")):
            continue
        for n, g in L.decisions(path):
            dc = int(F.court[n])
            if dc not in FC.ACT:
                continue
            acting.append((n, g))
    for n, g in acting:
        dc = int(F.court[n])
        d_date = int(F.date[n])
        mrow = meta.get(n)
        if not mrow:
            continue
        d_all, d_sides = BO.caption(mrow[7])
        cited = {cw["j"] for cw in g["cw"]}
        st["opinions"] += 1
        disps = BO.dispositions(g)
        res, why = BO.decide(disps, {"trial court", "court below"}, True)
        kind = res[0] if res else "-"
        cand = collections.Counter()
        for t in d_all:
            lst = idx.get(t, [])
            if len(lst) > 3000:
                continue
            for j in lst:
                cand[j] += 1
        hits = []
        for j in cand:
            jd = int(F.date[j])
            gap = BO.day(d_date) - BO.day(jd)
            if gap < 0 or gap > 5 * 365 + 1:
                continue
            cls = FC.tclass(trib[j], jd, dc)
            if cls is None:
                continue
            if BO.cap_rel(d_all, N.name(j), d_sides) < 2:
                continue
            hits.append((j, cls, gap))
        if not hits:
            continue
        cited_hits = [h for h in hits if h[0] in cited]
        st["op_with_capmatch"] += 1
        if cited_hits:
            st["op_capmatch_cited"] += 1
            continue
        st["op_capmatch_uncited"] += 1
        st["op_capmatch_uncited:" + kind] += 1
        for j, cls, gap in hits:
            dk = (meta.get(j) or [""] * 6)[5]
            pairs.append([n, j, dc, d_date // 10000, cls, gap // 365, len(hits), kind, dk,
                          ";".join(status.get(j, [])) or "-", mrow[7][:70], N.name(j)[:70]])
    with open(os.path.join(HERE, "work", "uncited.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.write("acting\tjnode\tacourt\tayear\ttclass\tgapy\tnhits\tjudgment\tjdocket\tjstatus\tatitle\tjname" + NL)
        for r in pairs:
            f.write("\t".join(str(x).replace("\t", " ") for x in r) + NL)
    print(dict(st))


if __name__ == "__main__":
    main()
