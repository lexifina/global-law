"""Pattern 2: unpublished or not-citable decisions treated as binding.

Predicate (Spec.citesUnpublishedAsBinding, with the 'followed' input read from the citing passage instead of the
reader's treatment rows, which hold only 14 'followed' rows): the citing decision treats as binding a decision whose
publication is not 'published' and whose force on the citing court, under the unpublished-opinion rule of the court
that issued it (system_rules unpubForce, keyed by the cited decision's date, as precedent_ref.unpub_cap), is below
bindingAbsentConflict.

    python p2_unpub.py collect   -> work/p2_edges.tsv (every citation into a non-published decision, same system)
    python p2_unpub.py prep      -> work/p2_passages.jsonl, work/p2_in.jsonl (passages with a binding cue)
    python llm_run.py unpub work/p2_in.jsonl work/p2_out.jsonl
    python p2_unpub.py score     -> data/p2_unpub.tsv
"""
import json, os, random, sys
from collections import Counter, defaultdict
import hcommon as C
import passages as P

UNPUB = ("unpublished", "table", "summaryOrder", "memorandum")
RANK = ["none", "resultOnly", "notCitable", "citableNoWeight", "persuasive", "persuasiveStrong",
        "bindingAbsentConflict", "binding"]


def rules():
    R = defaultdict(list)
    for p in C.read_tsv(os.path.join(C.DATA, "system_rules.tsv"), header=False):
        if p[1] == "unpubForce":
            R[int(p[0])].append((p[2], int(p[3]), int(p[4]) or 99991231))
    sysof = {}
    tier = {}
    for p in C.read_tsv(os.path.join(C.DATA, "courts2.tsv"), header=False):
        sysof.setdefault(int(p[0]), int(p[4]))
        tier.setdefault(int(p[0]), p[5])
    return R, sysof, tier


def cap(R, sysof, court, date, pub):
    for key in (-court, sysof.get(court, -1)):
        vals = [v for (v, a, b) in R.get(key, ()) if a <= date <= b]
        spec = [v.split(":", 1)[1] for v in vals if v.startswith(pub + ":")]
        if spec:
            return spec[0], "court" if key < 0 else "system"
        gen = [v for v in vals if ":" not in v]
        if gen:
            return gen[0], "court" if key < 0 else "system"
    return "persuasive", "default"


def collect():
    con = C.db()
    U = {}
    for n, c2, pub, d in con.execute("select d.node,d.court2,d.pub,n.date from dec d join nodes n on n.id=d.node "
                                     "where d.pub in ('unpublished','table','summaryOrder','memorandum')"):
        U[n] = (c2, pub, d)
    C.log("non-published decisions", len(U))
    R, sysof, tier = rules()
    rows = []
    want = set(U)
    citing_need = defaultdict(list)
    for a, b in C.iter_edges(want_cited=want):
        citing_need[a].append(b)
    C.log("edges into non-published", sum(len(v) for v in citing_need.values()), "citing", len(citing_need))
    ids = list(citing_need)
    meta = {}
    for k in range(0, len(ids), 900):
        chunk = ids[k:k + 900]
        for n, c2, d in con.execute("select d.node,d.court2,n.date from dec d join nodes n on n.id=d.node where "
                                    "d.node in (%s)" % ",".join("?" * len(chunk)), chunk):
            meta[n] = (c2, d)
    for a, bs in citing_need.items():
        if a not in meta:
            continue
        ca, da = meta[a]
        for b in bs:
            cb, pub, db_ = U[b]
            if sysof.get(ca) != sysof.get(cb) or da <= db_:
                continue
            f, lvl = cap(R, sysof, cb, db_, pub)
            same = int(ca == cb)
            rows.append((a, b, ca, cb, same, pub, f, lvl, da, db_))
    C.write_tsv(os.path.join(C.HWORK, "p2_edges.tsv"), rows,
                ["citing", "cited", "citing_court2", "cited_court2", "same_court", "cited_pub", "force", "rule_level",
                 "citing_date", "cited_date"])
    c = Counter((r[4], r[6]) for r in rows)
    C.log("same-system later citations", len(rows), c.most_common())


def prep():
    random.seed(7)
    rows = list(C.read_tsv(os.path.join(C.HWORK, "p2_edges.tsv")))
    # candidate: same court, force below bindingAbsentConflict
    cand = [r for r in rows if r[4] == "1" and RANK.index(r[6]) < RANK.index("bindingAbsentConflict")]
    C.log("same-court citations of non-binding non-published decisions", len(cand))
    items = [dict(citing=int(r[0]), cited=int(r[1]), actor=None, cited_pub=r[5], force=r[6], rule_level=r[7])
             for r in cand]
    out = os.path.join(C.HWORK, "p2_passages.jsonl")
    if not os.path.exists(out):
        P.run(items, out, workers=8)
    ps = [json.loads(l) for l in open(out, encoding="utf-8")]
    C.log("passages", len(ps), Counter((p["hits"] > 0, p.get("binding_lang"), p.get("unpub_lang")) for p in ps))
    # LLM: every passage with a binding cue and no unpublished marker, plus 300 random others with a cue (leak check)
    a = [p for p in ps if p["hits"] > 0 and p["binding_lang"] and not p["unpub_lang"]]
    b = [p for p in ps if p["hits"] > 0 and p["binding_lang"] and p["unpub_lang"]]
    pick = a + random.sample(b, min(300, len(b)))
    meta = C.nodes({p["citing"] for p in pick} | {p["cited"] for p in pick})
    with open(os.path.join(C.HWORK, "p2_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for p in pick:
            mc, md = meta[p["citing"]], meta[p["cited"]]
            p.update(hkey="unpub|%s|%s" % (p["citing"], p["cited"]), stratum="cue" if not p["unpub_lang"] else "cue+marked",
                     weight=1 if not p["unpub_lang"] else len(b) / max(1, min(300, len(b))),
                     cited_name=md["name"], cited_cite=md["cite"].split("|")[0], cited_court_name=md["court_name"],
                     cited_date=md["date"], citing_name=mc["name"], citing_cite=mc["cite"].split("|")[0],
                     citing_court_name=mc["court_name"], citing_date=mc["date"])
            f.write(json.dumps(p) + "\n")
    C.log("LLM rows", len(pick), "cue-only", len(a), "cue+marked", len(b))


def score():
    ins = {json.loads(l)["hkey"]: json.loads(l) for l in open(os.path.join(C.HWORK, "p2_in.jsonl"), encoding="utf-8")}
    outs = [json.loads(l) for l in open(os.path.join(C.HWORK, "p2_out.jsonl"), encoding="utf-8")]
    rows = []
    for o in outs:
        a, r = o["ans"], ins[o["key"]]
        if "error" in a:
            continue
        rows.append([r["citing"], r["citing_name"][:70], r["citing_cite"], r["citing_date"], r["citing_court_name"],
                     r["cited"], r["cited_name"][:70], r["cited_cite"], r["cited_date"], r["cited_pub"], r["force"],
                     r["stratum"], round(r["weight"], 2), int(a["treats_as_binding"]), int(a["notes_unpublished"]),
                     int(a["same_case"]), int(a["violation"]), a["quote"], a["reason"]])
    rows.sort(key=lambda x: (-x[16], x[10] != "notCitable", -x[3]))
    C.write_tsv(os.path.join(C.HUNT, "data", "p2_unpub.tsv"), rows,
                ["citing", "citing_name", "citing_cite", "citing_date", "citing_court", "cited", "cited_name",
                 "cited_cite", "cited_date", "cited_pub", "force", "stratum", "weight", "treats_as_binding",
                 "notes_unpublished", "same_case", "violation", "quote", "reason"])
    C.log("classified", len(rows), "violations", sum(r[16] for r in rows),
          Counter((r[11], r[10], r[16]) for r in rows).most_common())
    C.log("by court", Counter(r[4] for r in rows if r[16]).most_common(12))


if __name__ == "__main__":
    {"collect": collect, "prep": prep, "score": score}[sys.argv[1]]()
