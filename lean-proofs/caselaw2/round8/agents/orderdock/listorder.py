"""Round 8 `orderdock` sub-rule (a2): long Supreme Court order lists (texts the memo parser skips: >= 4,000 chars).

    python -X utf8 round8/agents/orderdock/listorder.py scan    -> work/listorder.pkl (parsed lists)
    python -X utf8 round8/agents/orderdock/listorder.py rows    -> rows_listorder.jsonl, work/listorder_stats.json

An order list is one Supreme Court decision whose order part (first "## Majority" / "## Per Curiam" / "## Opinion"
part, else the head matter) is a run of entries "<court below>[ Reported below: <citation(s)>];" (with "No. ..."
docket lines between them) closed by ONE disposition that reaches every entry ("Certiorari granted, judgments vacated,
and cases remanded ..."; "Certiorari denied."). Rule:
  - at least two "Reported below" entries; the disposition = memolib.classify of the text after the last entry
    (the tail, cut at the first separate statement / next "## " heading), kind certDenied / vacated / reversed /
    affirmed / reviewDismissed; the tail names no docket number ("No. 04-1234": a per-docket split) and no part
    ("in part", "insofar", ...: memolib scope "unknown" is refused);
  - each entry's citations resolve (graph/cite_index.tsv + r6cite forms) to a decision of the entry's court
    (memolib.Courts.resolve of the entry's designation), dated before the order and at most 3,660 days older;
  - row: main quote = the disposition sentence, anchor = the entry ("<court> Reported below: <citation>"),
    evidence cite:<citation as printed>; claim orderHead when the part is head matter (certify8 checks its terms).
No answer-key file is read.
"""
import collections
import gzip
import json
import os
import pickle
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HIST = os.path.join(C2, "round6", "history")
MEMO = os.path.join(HIST, "rules", "memo")
sys.path.insert(0, HIST)
sys.path.insert(0, MEMO)
sys.path.insert(0, os.path.join(HIST, "citeforms"))
import r6lib as L  # noqa: E402
import r6cite  # noqa: E402

C = L.reader_common()
WORK = os.path.join(HERE, "work")
NL = chr(10)
KINDS = ("certDenied", "vacated", "reversed", "affirmed", "reviewDismissed")
RX_RB = re.compile(r"reported\s+below\s*[:;.,*]*\s*", re.I)
RX_ENTRY_START = re.compile(r";|\bNos?\.\s*[\w\-–]+\.\s*|\]\s*|\n")
RX_PART = re.compile(r"^## (Majority|Per Curiam|Opinion|Lead|Combined|Head matter|CAP head matter)\b.*$", re.M)


def parse_text(n, t):
    import memolib as M
    heads = [(m.start(), m.end(), m.group(1)) for m in RX_PART.finditer(t)]
    if not heads:
        return None
    part_idx = None
    for i, (s, e, nm) in enumerate(heads):
        if nm in ("Majority", "Per Curiam", "Opinion", "Lead", "Combined"):
            part_idx = i
            break
    if part_idx is None:
        part_idx = 0
    s, e, nm = heads[part_idx]
    lo = e
    nxt = re.search(r"^## ", t[lo:], re.M)
    hi = lo + nxt.start() if nxt else len(t)
    part = {"Majority": "majority", "Per Curiam": "perCuriam", "Opinion": "majority", "Lead": "plurality",
            "Combined": "majority"}.get(nm, "headmatter")
    ents = []
    for m in RX_RB.finditer(t, lo, hi):
        a = m.end()
        lim = min(hi, a + 200)
        blo = max(lo, m.start() - 160)
        back = t[blo:m.start()]
        last = 0
        for mm in RX_ENTRY_START.finditer(back):
            last = mm.end()
        court_txt = L.norm(back[last:]).strip(" ,;")
        seg = t[a:lim]
        prev = 0
        cites = []
        for cm in r6cite.finditer(seg):
            gap = seg[prev:cm.start()]
            if (prev == 0 and cm.start() > 5) or (prev > 0 and not re.fullmatch(r"[\s,]*(?:and\s+)?", gap)):
                break
            prev = cm.end()
            cites.append((C.cite_key(cm) or "", cm.group(0), a + cm.start(), a + cm.end()))
        if cites:
            ents.append((court_txt, cites, blo + last, a + prev))
    if len(ents) < 2:
        return None
    # the tail: after the last entry (and after any "; and <court>" entries without a citation)
    t0 = ents[-1][3]
    tail = t[t0:hi]
    msep = M.RX_SEP.search(tail)
    if msep:
        tail = tail[:msep.start()]
    if re.search(r"\bNos?\.\s*\d", tail):
        return {"n": n, "why": "tail_names_docket"}
    cl = M.classify(tail)
    if cl is None:
        return {"n": n, "why": "tail_no_disposition"}
    kind, scope, (m0, m1) = cl
    # quote: the sentence holding the disposition words, inside the tail
    q0 = m0
    while q0 > 0 and not re.match(r"[.;]\s", tail[q0 - 2:q0]):
        q0 -= 1
    q1 = m1
    mm = re.search(r"\.(?=\s|$)", tail[m1:])
    q1 = m1 + mm.end() if mm else len(tail)
    return {"n": n, "kind": kind, "scope": scope, "part": part, "main": [t0 + q0, t0 + q1],
            "quote": L.norm(tail[q0:q1]), "ents": ents, "len": len(t)}


def _scan_chunk(items):
    texts = L.fetch_texts(items)
    out = []
    for n in items:
        if n not in texts:
            continue
        t = texts[n][1]
        if len(RX_RB.findall(t)) < 2:
            continue
        r = parse_text(n, t)
        if r is not None:
            out.append(r)
    return out


def stage_scan():
    nodes = []
    for p in L.shards(".meta.tsv.gz"):
        if not os.path.basename(p).startswith("supreme-court"):
            continue
        for r in L.meta_rows(p):
            if int(r[2]) >= 4000:
                nodes.append(int(r[0]))
    nodes.sort()
    chunks = [nodes[i:i + 1000] for i in range(0, len(nodes), 1000)]
    out = []
    for res in L.pmap(_scan_chunk, chunks, procs=8):
        out.extend(res)
    pickle.dump(out, open(os.path.join(WORK, "listorder.pkl"), "wb"), protocol=4)
    why = collections.Counter(r.get("why", r.get("kind")) for r in out)
    print("long SC texts", len(nodes), "with >= 2 entries", len(out), dict(why))


def stage_rows():
    import memolib as M
    courts = M.Courts()
    F = L.Facts()
    lists = [r for r in pickle.load(open(os.path.join(WORK, "listorder.pkl"), "rb")) if "kind" in r]
    need = set()
    for r in lists:
        for _ct, cites, _a, _b in r["ents"]:
            for k, raw, _s, _e in cites:
                need.update(r6cite.keys(raw))
    idx = {}
    with open(os.path.join(L.W, "graph", "cite_index.tsv"), encoding="utf-8") as f:
        for line in f:
            k, _t, v = line.rstrip(NL).partition("\t")
            if k in need:
                idx[k] = int(v)
    st = collections.Counter()
    rows = []
    for r in lists:
        st["lists"] += 1
        if r["kind"] not in KINDS:
            st["list_kind_" + r["kind"]] += 1
            continue
        if r["scope"] != "all":
            st["list_scope_" + r["scope"]] += 1
            continue
        od = int(F.date[r["n"]])
        if r["part"] == "headmatter" and od < 20130101:
            st["list_headmatter_pre2013"] += 1
            continue
        seen = set()
        for court_txt, cites, e0, e1 in r["ents"]:
            ck = courts.resolve(court_txt) if re.search(r"[A-Za-z]{2}", court_txt) else None
            ids = set(courts.group.get(ck, ())) if ck is not None else set()
            for key0, raw, a, b in cites:
                st["citations"] += 1
                node, used = None, None
                for k in r6cite.keys(raw):
                    if k in idx:
                        node, used = idx[k], k
                        break
                if node is None:
                    st["unresolved"] += 1
                    continue
                tc, td = int(F.court[node]), int(F.date[node])
                if not ids:
                    st["entry_no_court"] += 1
                    continue
                if tc not in ids:
                    st["other_court"] += 1
                    continue
                if not td or td >= od or M.ordinal(od) - M.ordinal(td) > 3660:
                    st["date"] += 1
                    continue
                if node in seen:
                    continue
                seen.add(node)
                rows.append({"rule": "listorder:" + ("alias" if used != key0 else "entry"), "table": "history",
                             "by": r["n"], "target": int(node), "kind": r["kind"], "scope": "all",
                             "main": r["main"], "part": r["part"], "ev": "cite:" + (key0 or used),
                             "anchor": [e0, e1], "anchor_part": r["part"], "text": "by",
                             "claim": "orderHead" if r["part"] == "headmatter" else "-",
                             "note": "order list entry; court '%s'; key %s; %d entries" % (court_txt[:40], used,
                                                                                         len(r["ents"]))})
                st["rows"] += 1
                st["rows_" + r["kind"]] += 1
    with open(os.path.join(HERE, "rows_listorder.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for x in rows:
            f.write(json.dumps(x) + NL)
    json.dump(st, open(os.path.join(WORK, "listorder_stats.json"), "w"), indent=1)
    print(dict(st))


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    {"scan": stage_scan, "rows": stage_rows}[sys.argv[1]]()
