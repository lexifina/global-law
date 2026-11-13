"""Pattern 1, known instances: later courts' own call-outs of reliance on overruled authority.

gold/reports_typed.tsv holds every later-court note ("X, which was overruled by Y"). We keep the notes whose snippet
says some court or decision relied on the overruled case, read +-1,200 characters of the noting opinion, and ask the
LLM (task `callout`) who relied. Named decisions are resolved through the citation index; "the lower court in this
case" through history.tsv (the decision the noting court reviewed). A known zombie instance is a relying decision in
the corpus, dated after the overruling, that cites the overruled decision.

    python p1_callouts.py prep      -> work/p1_callout_in.jsonl
    python llm_run.py callout work/p1_callout_in.jsonl work/p1_callout_out.jsonl
    python p1_callouts.py resolve   -> data/p1_known_callouts.tsv, work/p1_known_zombie_in.jsonl
"""
import csv, json, os, re, sys
from collections import defaultdict
import hcommon as C

csv.field_size_limit(10 ** 9)
RX = re.compile(r"(relied|relying|reliance|based (?:its|his|her) (?:decision|ruling)|court below|trial court|"
                r"district court|court of appeals|appellate court|the panel|lower court)[^.]{0,200}(?:which|that|since|"
                r"has since|had been|was|were)[^.]{0,40}(overruled|abrogated|disapproved|receded)|"
                r"(overruled|abrogated)[^.]{0,200}(trial court|district court|court below|court of appeals|lower court)"
                r" (?:relied|erred|was bound|followed|applied)", re.I)


def prep():
    hits = []
    with open(os.path.join(C.GOLD, "reports_typed.tsv"), encoding="utf-8") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        h = next(r)
        for p in r:
            d = dict(zip(h, p))
            if d["kind"] in ("overruled", "abrogated", "disapproved", "receded") and RX.search(d["snippet"]):
                hits.append(d)
    meta = C.nodes({int(d["note_node"]) for d in hits})
    texts = C.fetch(meta)
    with open(os.path.join(C.HWORK, "p1_callout_in.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        for d in hits:
            n = int(d["note_node"])
            t = texts.get(n)
            if not t:
                continue
            b = t  # note_offset is into the file text
            snip = d["snippet"][100:220]
            k = b.find(snip[:60]) if snip else -1
            if k < 0:
                k = int(d["note_offset"])
            w = b[max(0, k - 1200):k + 1200]
            f.write(json.dumps(dict(hkey="callout|%s|%s" % (d["id"], n), note_id=d["id"], note_node=n,
                                    note_name=meta[n]["name"], note_date=meta[n]["date"], target=int(d["target_node"]),
                                    by=int(d["by_node"]), window=w)) + "\n")
    C.log("callout notes", len(hits))


def norm_cite(s):
    s = re.sub(r"[.,]", "", s or "").lower()
    s = re.sub(r"\s+", " ", s).strip()
    m = re.search(r"(\d+)\s+([a-z][a-z0-9 ]*?)\s+(\d+)", s)
    if not m:
        return None
    return "%s %s %s" % (m.group(1), m.group(2).replace(" ", ""), m.group(3))


def resolve():
    ins = {json.loads(l)["hkey"]: json.loads(l) for l in open(os.path.join(C.HWORK, "p1_callout_in.jsonl"),
                                                               encoding="utf-8")}
    outs = [json.loads(l) for l in open(os.path.join(C.HWORK, "p1_callout_out.jsonl"), encoding="utf-8")]
    hist = defaultdict(list)  # reviewing node -> lower nodes
    for p in C.read_tsv(os.path.join(C.DATA, "history.tsv"), header=False):
        if p[2].lstrip("-").isdigit() and int(p[2]) >= 0:
            hist[int(p[2])].append(int(p[1]))
    # status: date the target became negative
    tset = {ins[o["key"]]["target"] for o in outs}
    negd = {}
    for r in C.read_tsv(os.path.join(C.OUT, "status.tsv")):
        n = int(r[0])
        if n in tset and r[1] == "-" and r[5].startswith(("neg:", "unknown:partial")):
            negd[n] = min(negd.get(n, 99999999), int(r[3]))
    finds = set()
    for r in C.read_tsv(os.path.join(C.OUT, "findings.tsv")):
        if r[0] == "citesOverruled" and r[5] == "1":
            finds.add((int(r[1]), int(r[2])))
    cand = []
    for o in outs:
        a, i = o["ans"], ins[o["key"]]
        if "error" in a:
            continue
        reliers = []
        if a["relier_kind"] == "named_court_decision":
            c = norm_cite(a["relier_cite"])
            ns = C.node_of_cite(c) if c else []
            reliers = ns[:1]
        elif a["relier_kind"] == "lower_court_in_this_case":
            reliers = hist.get(i["note_node"], [])[:1]
        for rl in reliers:
            cand.append((i, a, rl))
    meta = C.nodes({rl for _, _, rl in cand} | {i["target"] for i, _, _ in cand} | {i["by"] for i, _, _ in cand if i["by"] > 0})
    cites_t = defaultdict(set)
    want = {i["target"] for i, _, _ in cand}
    rl_set = {rl for _, _, rl in cand}
    for x, y in C.iter_edges(want_cited=want, want_citing=rl_set):
        cites_t[x].add(y)
    rows, zin = [], []
    for i, a, rl in cand:
        t = i["target"]
        if rl not in meta or t not in meta:
            continue
        cites = t in cites_t.get(rl, set())
        nd = negd.get(t, 0)
        after = bool(nd) and meta[rl]["date"] >= nd
        known = cites and after
        rows.append([i["note_node"], i["note_name"][:60], rl, meta[rl]["name"][:60], meta[rl]["date"],
                     meta[rl]["court_name"], t, meta[t]["name"][:60], nd or "-", int(cites), int(after),
                     int(known), int((rl, t) in finds), a["relier_kind"], a["relied_after_overruling"]])
    C.write_tsv(os.path.join(C.HUNT, "data", "p1_known_callouts.tsv"), rows,
                ["note_node", "note_name", "relier", "relier_name", "relier_date", "relier_court", "target",
                 "target_name", "target_neg_from", "relier_cites_target", "relier_after_neg", "known_zombie",
                 "in_findings", "relier_kind", "llm_after"])
    k = [r for r in rows if r[11] == 1]
    C.log("call-out rows", len(rows), "known zombie instances", len(k), "in citesOverruled findings",
          sum(r[12] for r in k))


if __name__ == "__main__":
    {"prep": prep, "resolve": resolve}[sys.argv[1]]()
