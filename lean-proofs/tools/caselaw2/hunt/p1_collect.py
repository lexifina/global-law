"""Pattern 1 (zombie precedent), step 1: join the runner's citesOverruled / citesVacated findings with the status
witness (who negated the cited decision, when, and the quoted words) and node metadata.

    python p1_collect.py        -> hunt/data/p1_candidates.tsv
"""
import os
from collections import defaultdict
import hcommon as C

KINDS = {"citesOverruled", "citesVacated"}


def main():
    finds = [r for r in C.read_tsv(os.path.join(C.OUT, "findings.tsv")) if r[0] in KINDS and r[5] == "1"]
    C.log("findings", len(finds))
    cited = {int(r[2]) for r in finds}
    # status intervals per (node, issue)
    st = defaultdict(list)
    for r in C.read_tsv(os.path.join(C.OUT, "status.tsv")):
        n = int(r[0])
        if n in cited and r[5].startswith("neg:"):
            st[(n, r[1])].append((int(r[3]), int(r[4]), r[5], r[8], r[9]))
    # treatment and history quotes
    quotes = {}
    for fn, kcol, scol, qcol in (("treatments.tsv", 4, 5, 11), ("history.tsv", 4, 5, 9)):
        for p in C.read_tsv(os.path.join(C.DATA, fn), header=False):
            if len(p) > qcol:
                quotes[p[0]] = (p[kcol], p[scol], p[qcol])
    meta_ids = set(cited) | {int(r[1]) for r in finds}
    actors = set()
    rows = []
    for r in finds:
        citing, cit, issue = int(r[1]), int(r[2]), r[3]
        rows.append([r[0], citing, cit, issue, r[4], r[6]])
    m = C.nodes(meta_ids)
    out = []
    for kind, citing, cit, issue, detail, path in rows:
        mc, md = m.get(citing), m.get(cit)
        if not mc or not md:
            continue
        cand = [x for x in st.get((cit, issue), []) if x[0] <= mc["date"] <= x[1]]
        if not cand:
            cand = [x for x in st.get((cit, issue), [])]
        neg_from, witness, actor = (cand[0][0], cand[0][3], cand[0][4]) if cand else (0, "-", "-")
        q = quotes.get(witness, ("-", "-", "-"))
        if actor not in ("-", ""):
            actors.add(int(actor))
        out.append([kind, citing, cit, issue, detail, neg_from, witness, actor, q[0], q[1], q[2][:400],
                    mc["date"], mc["court"], mc["court_name"], mc["cite"].split("|")[0], mc["name"][:80],
                    md["date"], md["court"], md["court_name"], md["cite"].split("|")[0], md["name"][:80], path])
    am = C.nodes(actors)
    for o in out:
        a = am.get(int(o[7])) if o[7] not in ("-", "") else None
        o += [a["date"] if a else 0, (a["cite"].split("|")[0] if a else "-"), (a["name"][:80] if a else "-")]
    hdr = ["kind", "citing", "cited", "issue", "detail", "neg_from", "witness", "actor", "wkind", "wscope", "wquote",
           "citing_date", "citing_court", "citing_court_name", "citing_cite", "citing_name", "cited_date",
           "cited_court", "cited_court_name", "cited_cite", "cited_name", "path", "actor_date", "actor_cite",
           "actor_name"]
    C.write_tsv(os.path.join(C.HUNT, "data", "p1_candidates.tsv"), out, hdr)
    C.log("wrote", len(out))


if __name__ == "__main__":
    main()
