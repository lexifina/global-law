"""Round 8, agent `multicase`: reader answers -> DESIGN7 section 4 rows (rows.jsonl) for certify8.

    python -X utf8 mcrows.py [--ans DIR] [--out rows.jsonl]

For every answer with act = true, one treatments row per chosen target, all with the same main quote (the ACT
sentence, or the reader's act_quote found in the text within [prev start - 600, act end + 400)):
  - target named in the act sentence  -> rule multicase:onesentence, plain row, evidence inside the main quote;
  - target named only in the sentence before -> rule multicase:joined, one `antecedent` joined line = that sentence
    (gap <= joined_gap_max), the evidence inside it, an `anaphor` phrase and a plain cue of the kind in the main quote.
kind: the reader's per-target kind, else its kind. scope (DESIGN7 section 6, from the sentence itself): a limiting
phrase in the main quote -> partialUnknown; else the reader's scope (all | partialUnknown).
Guards (round 7 antecedent, answers_to_rows.py): cite evidence whose printed caption names another case
(citeCaptionMismatch); name evidence that stands only inside another case's caption (nameCollision).
Rejected targets -> rows_rejects.tsv. No answer key is read.
"""
import argparse, collections, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, os.path.join(C2, "round7", "agents", "antecedent"))
import r6lib as L  # noqa: E402
import answers_to_rows as AA  # noqa: E402  (cite_consistent, name_consistent, ev_in helpers)
import mcpack as MP  # noqa: E402
C = L.reader_common()
NL = chr(10)
CUES = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json")
KINDS = ("overruled", "disapproved", "abrogated", "recededFrom")
LIMIT = re.compile(r"to the extent|in\s*so far|insofar|so far as|in part\b|on this point|on this issue|"
                   r"on other grounds|as to\b|in the field of|to that extent|to this extent|pro tanto|"
                   r"in this respect|in that respect|to the degree|the language of|the dictum|dicta|"
                   r"the holding that|the rule announced|in so far as|in the particular|so far as", re.I)


def lc(s):
    return L.norm(s).lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ans", default=os.path.join(HERE, "ans"))
    ap.add_argument("--out", default=os.path.join(HERE, "rows.jsonl"))
    a = ap.parse_args()
    cue = json.load(open(CUES, encoding="utf-8"))
    treat, ana, gapmax = cue["treat"], cue["anaphor"], int(cue.get("joined_gap_max") or 300)
    items = {}
    for line in open(os.path.join(HERE, "packs", "map.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        items[r["id"]] = r
    answers = {}
    for p in sorted(glob.glob(os.path.join(a.ans, "*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(o, dict) and o.get("id") in items:
                answers[o["id"]] = o
    st = collections.Counter()
    st["answers"] = len(answers)
    st["act_true"] = sum(1 for o in answers.values() if o.get("act") is True)
    need = sorted({items[i]["n"] for i, o in answers.items() if o.get("act") is True})
    texts = {}
    for k in range(0, len(need), 2000):
        texts.update(L.fetch_texts(need[k:k + 2000]))
    rows, rej = [], []
    for iid, o in sorted(answers.items()):
        if o.get("act") is not True:
            continue
        it = items[iid]
        n = it["n"]
        if n not in texts:
            st["no_text"] += 1
            continue
        v = MP.view_of(texts[n][1])
        s0, s1 = it["s"]
        p0, p1 = it["p"]
        m0, m1 = s0, s1
        aq = (o.get("act_quote") or "").strip()
        if aq:
            lo = max(0, min(p0, s0) - 600)
            hi = min(len(v), s1 + 400)
            seg = L.norm(v[lo:hi])
            k = seg.find(L.norm(aq))
            if k >= 0:
                m0, m1 = lo + k, lo + k + len(aq)
                st["act_quote_used"] += 1
            else:
                st["act_quote_not_found"] += 1
        mq = L.norm(v[m0:m1])
        mql = mq.lower()
        part = {"majority": "majority", "majority~": "majority", "perCuriam": "perCuriam",
                "plurality": "plurality"}.get(it["part"])
        tl = o.get("targets") or []
        if not isinstance(tl, list):
            tl = []
        kinds = o.get("kinds") if isinstance(o.get("kinds"), dict) else {}
        scopes = o.get("scopes") if isinstance(o.get("scopes"), dict) else {}
        for tn in tl:
            t = it["targets"].get(tn)
            if t is None:
                rej.append((iid, tn, "noSuchTarget", ""))
                continue
            kind = kinds.get(tn) or o.get("kind")
            if kind not in KINDS:
                rej.append((iid, tn, "kind", str(kind)))
                continue
            sc = scopes.get(tn) or o.get("scope") or "partialUnknown"
            scope = "partialUnknown" if (LIMIT.search(mq) or sc != "all") else "all"
            ev = t["ev"]
            note = {"item": iid, "T": tn, "ntargets": len(tl), "nlisted": len(it["targets"]), "own": it["own"][0],
                    "conf": o.get("confidence"), "reader_scope": sc, "where": t["where"]}
            row = {"rule": "", "table": "treatments", "by": n, "target": t["t"], "kind": kind, "scope": scope,
                   "main": [m0, m1], "part": part, "ev": ev, "joined": [], "claim": "-", "doctrine": "-",
                   "field_limit": "-", "anchor": None, "anchor_part": "-",
                   "reader": "r8:multicase", "confidence": o.get("confidence", 0.9)}
            if not any(c in mql for c in treat.get(kind, [])):
                rej.append((iid, tn, "noCueOfKind", kind))
                continue
            in_main = m0 <= t["hit"][0] and t["hit"][1] <= m1
            if in_main and ev.startswith("name:"):
                in_main = AA.ev_in(ev, mq, t["t"], {})
            if in_main:
                if ev.startswith("cite:") and not AA.cite_consistent(mq, ev, t["name"]):
                    rej.append((iid, tn, "citeCaptionMismatch", t["name"]))
                    continue
                if ev.startswith("name:") and not AA.name_consistent(mq, ev, t["name"]):
                    rej.append((iid, tn, "nameCollision", t["name"]))
                    continue
                row["rule"] = "multicase:onesentence"
            else:
                # named before the act sentence: joined antecedent line = the previous sentence
                if not (p1 > p0 and p0 <= t["hit"][0] and t["hit"][1] <= p1):
                    rej.append((iid, tn, "notInQuoteOrPrev", ""))
                    continue
                jq = L.norm(v[p0:p1])
                if p1 > m0 or m0 - p1 > gapmax:
                    rej.append((iid, tn, "joinedGap", "%d" % (m0 - p1)))
                    continue
                if not any(c in mql for c in ana):
                    rej.append((iid, tn, "noAnaphor", ""))
                    continue
                if ev.startswith("cite:") and not AA.cite_consistent(jq, ev, t["name"]):
                    rej.append((iid, tn, "citeCaptionMismatch", t["name"]))
                    continue
                if ev.startswith("name:") and not AA.name_consistent(jq, ev, t["name"]):
                    rej.append((iid, tn, "nameCollision", t["name"]))
                    continue
                row["rule"] = "multicase:joined"
                row["joined"] = [{"rel": "antecedent", "span": [p0, p1], "part": part, "label": "-"}]
            row["note"] = json.dumps(note, ensure_ascii=False)
            rows.append(row)
            st["rows:" + row["rule"]] += 1
    with open(a.out, "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(HERE, "rows_rejects.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for x in rej:
            f.write("\t".join(map(str, x)) + NL)
    for x in rej:
        st["reject:" + x[2]] += 1
    st["rows"] = len(rows)
    with open(os.path.join(HERE, "rows_stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(sorted(st.items())), f, indent=1)
    print(json.dumps(dict(sorted(st.items())), indent=1))


if __name__ == "__main__":
    main()
