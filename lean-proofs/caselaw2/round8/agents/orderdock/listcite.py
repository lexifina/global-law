"""Round 8 `orderdock` sub-rule (a): every "Reported below" entry of a Supreme Court order list, with reporter forms.

    python -X utf8 round8/agents/orderdock/listcite.py   -> rows_listcite.jsonl, work/listcite_stats.json,
                                                            work/listcite_refused.tsv

The round-6 memo linker reads the citations of the FIRST "Reported below" of an order (420 characters) and keys them
with the reader's citation key only. Combined orders list dozens of cases, each entry "<court> Reported below:
<citation(s)>" separated by ";" (Booker / Dorsey GVR lists), and print the unpublished reporter as "Fed. Appx."
while the corpus files it as "F. App'x". Rule:
  - parse the order core (orders.pkl: the order's words, cut at the first separate statement) into entries: every
    "Reported below:" occurrence, its citations up to the next ";" / "No." / sentence end (at most 160 characters);
    the entry's court = the designation between the previous ";" (or the start of the core / a "No. ..." run) and
    "Reported below" (memolib.Courts.resolve); none -> the courts the order names;
  - each citation is resolved through graph/cite_index.tsv with the round-6 citation forms (r6cite.keys: reader key,
    parentheses, audited reporter aliases such as fedappx -> fappx);
  - target: a decision of the entry's court, dated before the order, at most 3,660 days older (the memo:cite rule);
  - one row per (order, target): kind and scope = the order's disposition (memo parse; scope "unknown" kept), main
    quote = the disposition sentence, anchor = the entry ("<court> Reported below: <citation>") when the citation
    is more than 400 characters from the disposition (as memo:cite), evidence cite:<key as printed>.
  - an order whose disposition does not reach every listed case (granted + denied mixed, "in part") keeps the memo
    parse's scope; orders of kind reviewGranted are not rows.
No answer-key file is read.
"""
import collections
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
RX_ENTRY_START = re.compile(r";|\bNos?\.\s*[\w\-–]+\.\s*|\]\s*|\b(?:granted|denied|dismissed|vacated|reversed|affirmed|remanded)\b[^.]{0,80}\.\s+")


def entries(o):
    """[(court text, key, raw citation, start, end)] for every citation after every 'Reported below'."""
    T, off = o["T"], o["off"]
    c0 = o["disp"][0] - off
    # the order core: from the start of the order's words (the first opinion part, or head matter) to the cut
    core_lo = 0
    m_part = re.search(r"## (?:Majority|Per Curiam|Lead|Opinion|Combined)\b", T)
    if m_part and m_part.end() <= c0:
        core_lo = m_part.end()
    out = []
    for m in RX_RB.finditer(T, core_lo):
        a = m.end()
        lim = min(len(T), a + 200)
        # entry court: back to the previous ';' / 'No. x.' run / start of the core
        lo = max(core_lo, m.start() - 160)
        back = T[lo:m.start()]
        last = 0
        for mm in RX_ENTRY_START.finditer(back):
            last = mm.end()
        court_txt = back[last:].strip(" ,;")
        # the citations of this entry: consecutive citations right after "Reported below:"
        prev = 0
        seg = T[a:lim]
        for cm in r6cite.finditer(seg):
            gap = seg[prev:cm.start()]
            if (prev == 0 and cm.start() > 5) or (prev > 0 and not re.fullmatch(r"[\s,]*(?:and\s+)?", gap)):
                break
            prev = cm.end()
            out.append((court_txt, C.cite_key(cm) or "", cm.group(0), off + a + cm.start(), off + a + cm.end(),
                        off + lo + last, off + a + prev))
    return out


def main():
    import memolib as M
    courts = M.Courts()
    F = L.Facts()
    orders = pickle.load(open(os.path.join(MEMO, "work", "orders.pkl"), "rb"))["orders"]
    cand = []
    need = set()
    for o in orders:
        if o["kind"] not in KINDS:
            continue
        es = entries(o)
        if not es:
            continue
        ks = []
        for e in es:
            kk = r6cite.keys(e[2])
            ks.append(kk)
            need.update(kk)
        cand.append((o, es, ks))
    idx = {}
    with open(os.path.join(L.W, "graph", "cite_index.tsv"), encoding="utf-8") as f:
        for line in f:
            k, _t, v = line.rstrip(NL).partition("\t")
            if k in need:
                idx[k] = int(v)
    st = collections.Counter()
    rows, refused = [], []
    for o, es, ks in cand:
        oids = set()
        for k in o["courts"]:
            if k is not None:
                oids.update(courts.group.get(k, ()))
        seen = set()
        old_nodes = {n2 for n2, _k, _a, _b in o["rbn"] if n2 is not None}
        for e, kk in zip(es, ks):
            court_txt, key0, raw, a, b, e0, e1 = e
            st["citations"] += 1
            node, used = None, None
            for k in kk:
                if k in idx:
                    node, used = idx[k], k
                    break
            if node is None:
                st["unresolved"] += 1
                refused.append((o["n"], raw, "unresolved", court_txt[:60]))
                continue
            ck = courts.resolve(court_txt) if re.search(r"[A-Za-z]{2}", court_txt) else None
            ids = set(courts.group.get(ck, ())) if ck is not None else oids
            tc, td = int(F.court[node]), int(F.date[node])
            why = None
            if not ids:
                why = "no_court"
            elif tc not in ids:
                why = "other_court"
            elif not td or td >= o["date"] or node == o["n"]:
                why = "date"
            elif M.ordinal(o["date"]) - M.ordinal(td) > 3660:
                why = "too_old"
            if why:
                st[why] += 1
                refused.append((o["n"], raw, why, court_txt[:60]))
                continue
            if node in seen:
                continue
            seen.add(node)
            new = node not in old_nodes
            st["new_vs_memo" if new else "memo_had"] += 1
            q0, q1 = o["disp"]
            if a >= q0 - 400 and b <= q1 + 400:
                anchor, ap = None, ""
            else:
                anchor, ap = [e0, max(e1, b)], o["part"]
            ev = "cite:" + (key0 or used)
            rows.append({"rule": "listcite:" + ("alias" if used != key0 else "entry"), "table": "history",
                         "by": o["n"], "target": int(node), "kind": o["kind"], "scope": o["scope"],
                         "main": [q0, q1], "part": o["part"], "ev": ev, "anchor": anchor, "anchor_part": ap,
                         "text": "by", "claim": "orderHead" if o["part"] == "headmatter" else "-",
                         "note": "reported below entry; court '%s'; key %s" % (court_txt[:40], used)})
            st["rows"] += 1
            st["rows_" + o["kind"]] += 1
    with open(os.path.join(HERE, "rows_listcite.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r) + NL)
    with open(os.path.join(WORK, "listcite_refused.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for r in refused:
            f.write("\t".join(str(x) for x in r) + NL)
    json.dump(st, open(os.path.join(WORK, "listcite_stats.json"), "w"), indent=1)
    print(dict(st))


if __name__ == "__main__":
    main()
