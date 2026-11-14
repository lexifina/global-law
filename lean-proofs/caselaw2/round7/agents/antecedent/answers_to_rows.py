"""Round 7, agent `antecedent`: reader answers -> DESIGN7 section 4 rows (rows.jsonl) + a self-check.

    python -X utf8 answers_to_rows.py [--ans ans] [--map packs/map.jsonl] [--out rows.jsonl] [--keep-base]

For every answer with act = true and every chosen T-number:
  main   = the reader's act_quote found in the git-HEAD text at/near the act sentence (whitespace / quote-mark tolerant;
           the text's own characters are used), else the scanned act sentence;
  target named IN the main quote (T where = act)  -> a plain row, rule `antecedent:onesentence`, no joined line;
  target named before (where = near)              -> rule `antecedent:joined`, one joined line
           {rel: antecedent, span: the naming sentence (or the reader's `naming` override found in the text), part};
  ev     = cite:<reader key> when the target's citation is inside the quote that must carry it (joined quote, or the
           main quote for a one-sentence row) and the staged index (final2 cite_index, else the graph index uniquely)
           maps it to the target; else name:<caption words of the target that stand capitalised in that quote, at most
           two>; a row with neither is dropped (`no_evidence`).
Self-check (the string functions of DESIGN7 2.1/2.2 and the plain check, as far as they can be run here): quote is
the text; main has a cue of the kind (cue table `treat`), an anaphor phrase (cue table `anaphor` when present, else
ANAPHOR_FALLBACK below), no disqualify_treat phrase; the joined quote has no disqualify_treat (or disqualify_joined)
phrase, j_end <= start, start - j_end <= 300; the evidence resolves inside the joined quote (one-sentence: inside the
main quote); parts allowed. Rows failing the self-check go to rows_rejects.tsv with the reason.
Pairs (by, target) that already have an admitted explicit base row of a status-changing kind are counted and left
out unless --keep-base. No answer key is read.
"""
import argparse, collections, glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round6", "history"))
sys.path.insert(0, HERE)
import r6lib as L  # noqa: E402
import antecands as AC  # noqa: E402
sys.path.insert(0, os.path.join(C2, "round5", "recog"))
import recog_common as RC  # noqa: E402  (find_quote, alnum, ascii_lower)

C = L.reader_common()
NL = chr(10)
CUES = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json")
ANAPHOR_FALLBACK = ["those cases", "these cases", "that case", "those decisions", "these decisions", "that decision",
                    "such cases", "such decisions", "those opinions", "these opinions", "that opinion",
                    "those holdings", "that holding", "both cases", "both decisions", "each of them", "all of them",
                    "both of them", "said case", "said cases", "said decision", "said decisions", "those authorities",
                    "these authorities", "the earlier decisions", "the earlier cases", "the prior decisions",
                    "the former decisions", "the foregoing cases", "the cases cited", "the cases above cited",
                    "the above cases", "the above-cited cases", "that line of cases", "those precedents",
                    "they are overruled", "it is overruled", "they are disapproved", "it is disapproved",
                    "they are abrogated", "it is abrogated", "overrule them", "overrule it", "disapprove them",
                    "disapprove it", "recede from them", "recede from it", "recede from those", "recede from that",
                    "they are hereby overruled", "it is hereby overruled", "it likewise is overruled",
                    "to the extent they", "to the extent that they", "insofar as they", "in so far as they",
                    "to the extent it", "to the extent that it", "insofar as it"]
PART_OUT = {"majority": "majority", "majority~": "majority", "perCuriam": "perCuriam", "plurality": "plurality"}
GAP = 300


def cue_lists():
    d = json.load(open(CUES, encoding="utf-8"))
    ana = d.get("anaphor") or ANAPHOR_FALLBACK
    dqj = d.get("disqualify_joined") or []
    gap = int(d.get("joined_gap_max") or GAP)
    return d["treat"], d["disqualify_treat"], ana, dqj, gap, bool(d.get("anaphor"))


def body_of(text):
    """Body start as antescan.py computed it (after the front matter's closing line)."""
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            return nl + 1 if nl >= 0 else len(text)
    return 0


def ascii_norm(q):
    return RC.ascii_lower(L.norm(q))


def ev_in(ev, quote, target, index):
    ql = RC.ascii_lower(L.norm(quote))
    if ev.startswith("cite:"):
        c = RC.alnum(ev[5:])
        return bool(c) and c in RC.alnum(ql) and index.get(c) == target
    if ev.startswith("name:"):
        words = set(re.findall(r"[0-9a-z]+", ql))
        toks = [RC.alnum(x) for x in ev[5:].split(" ")]
        toks = [x for x in toks if len(x) >= 3]
        return bool(toks) and all(x in words for x in toks)
    return False


CAPTION = re.compile(r"((?:[A-Z][\w.'’&-]*\s+){0,2}[A-Z][\w.'’&-]*)\s+v\.?\s+([A-Z][\w.'’&-]*(?:\s+[A-Z][\w.'’&-]*){0,2})")


def _similar(a, b):
    import difflib
    return a[:4] == b[:4] or difflib.SequenceMatcher(None, a, b).ratio() >= 0.7


def _side_tokens(s):
    return {t.lower() for t in (C.name_tokens(s) | C.short_name_tokens(s))}


def name_consistent(quote, ev, tname):
    """A `name:` evidence word must not stand only inside the caption of ANOTHER case: if every occurrence of the
    first evidence word in the quote sits in an "A v. B" caption whose other side names parties the target's
    caption does not have, the name is a collision (e.g. "Ward" of "Oosterhoudt v. Montgomery Ward" for the
    target "Ward v. State")."""
    toks = [t for t in ev[5:].split(" ") if len(t) >= 3]
    if not toks:
        return False
    sides = [_side_tokens(s) for s in re.split(r"\s+v\.?\s+|\s+vs\.?\s+", tname or "")]
    allt = set().union(*sides) if sides else set()
    tok = toks[0]
    occ = [m for m in re.finditer(r"\b%s\b" % re.escape(tok), quote)]
    if not occ:
        return False
    caps = [(m.start(), m.end(), m.group(1), m.group(2)) for m in CAPTION.finditer(quote)]
    for o in occ:
        cap = next((c for c in caps if c[0] <= o.start() < c[1]), None)
        if cap is None:
            return True
        a, b = _side_tokens(cap[2]), _side_tokens(cap[3])
        mine, other = (a, b) if tok.lower() in a else (b, a)
        if not other or any(_similar(o, t) for o in other for t in allt):
            return True
    return False


_STOP_LOW = {w.lower() for w in C.STOPW} | {"the", "and", "for", "nat", "ins", "svcs", "inc", "corp", "ltd", "co"}


def _words(s):
    return {w.lower() for w in re.findall(r"[A-Za-z]{3,}", s or "") if w.lower() not in _STOP_LOW}


def cite_consistent(quote, ev, tname):
    """A `cite:` evidence must not sit right after the caption of another case: if the 120 characters before the
    citation hold an "A v. B" caption ending just before it and no caption word is similar (OCR-tolerant: same first
    four letters or difflib ratio >= 0.7) to a word of the target's caption, the citation key resolves to a
    different decision than the one the court names (an index collision). No caption there -> consistent."""
    c = RC.alnum(ev[5:])
    tt = {t.lower() for t in (C.name_tokens(tname) | C.short_name_tokens(tname))}
    for m in RC.RC.CITE_RX.finditer(quote):
        k = RC.RC.cite_key(m)
        if not k or RC.alnum(k) != c:
            continue
        pre = quote[max(0, m.start() - 120):m.start()]
        vs = list(re.finditer(r"\bv\.?\s+(?=[A-Z])", pre))
        if not vs:
            return True
        v = vs[-1]
        right = pre[v.end():]
        if re.search(r"[;)\]]|\bsupra\b|\bid\.", right):
            return True
        lm = re.search(r"((?:[A-Z][\w.'’&-]*\s+){0,2}[A-Z][\w.'’&-]*)\s*$", pre[:v.start()])
        words = _words(lm.group(1) if lm else "") | _words(right)
        tt = _words(tname)
        if not words or not tt or any(_similar(w, t) for w in words for t in tt):
            return True
        return False
    return True


def pick_ev(target, quote, name, other_name, res, index):
    for k, c in RC.cite_keys_in(quote):
        if res.get(k) == target and index.get(c, target) == target:
            return "cite:" + k
    ev = RC.name_evidence(name, other_name, quote)
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ans", default=os.path.join(HERE, "ans"))
    ap.add_argument("--map", default=os.path.join(HERE, "packs", "map.jsonl"))
    ap.add_argument("--out", default=os.path.join(HERE, "rows.jsonl"))
    ap.add_argument("--keep-base", action="store_true")
    a = ap.parse_args()
    treat, dq_treat, ana, dqj, gapmax, ana_final = cue_lists()
    items = {}
    for line in open(a.map, encoding="utf-8"):
        m = json.loads(line)
        items[m["id"]] = m
    answers = {}
    for p in sorted(glob.glob(os.path.join(a.ans, "*.jsonl"))):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("id") in items:
                answers[r["id"]] = r
    st = collections.Counter()
    st["answers"] = len(answers)
    pairs = AC.base_pairs()
    # texts and citation resolution
    want = [items[i] for i, r in answers.items() if r.get("act") is True and r.get("targets")]
    st["act_true"] = len(want)
    texts = {}
    nodes = sorted({it["n"] for it in want})
    for i in range(0, len(nodes), 2000):
        texts.update(L.fetch_texts(nodes[i:i + 2000]))
    keys = set()
    for it in want:
        sha, t = texts.get(it["n"], (None, ""))
        for k, _c in RC.cite_keys_in(t):
            keys.add(k)
    res = AC.resolver(keys)
    index = {RC.alnum(k): v for k, v in res.items()}
    tnodes = set(it["n"] for it in want) | {x["t"] for it in want for x in it["T"].values()}
    NM = AC.names_of(tnodes)
    rows, rejects = [], []
    seen = {}
    for i, r in answers.items():
        it = items[i]
        if r.get("act") is not True:
            st["act_false"] += 1
            continue
        tl = [t for t in (r.get("targets") or []) if t in it["T"]]
        if not tl:
            st["act_true_no_target"] += 1
            continue
        kind = r.get("kind")
        if kind not in ("overruled", "disapproved", "abrogated", "recededFrom"):
            st["bad_kind"] += 1
            continue
        scope = "all" if r.get("scope") == "all" else "partialUnknown"
        sha, t = texts[it["n"]]
        view = C.unwrap_view(t, body_of(t)) if it["hw"] else t
        s0, s1 = it["s"]
        ms, me = s0, s1
        q = (r.get("act_quote") or "").strip()
        if q:
            lo = max(0, s0 - 50)
            seg = L.norm(view[lo:s1 + 50])
            fq = RC.find_quote(seg, L.norm(q), s0 - lo, hyphen=True)
            if fq:
                ms, me = lo + fq[0], lo + fq[1]
            else:
                st["act_quote_not_found"] += 1
        while me > ms and view[me - 1] in " \n":
            me -= 1
        part = PART_OUT.get(it["part"])
        mains = [(ms, me)]
        if (s0, s1) != (ms, me) and s0 <= ms and me <= s1:
            mains.append((s0, s1))
        for T in tl:
            x = it["T"][T]
            tgt = x["t"]
            nm_t = NM.get(tgt, ("", ""))[0]
            nm_w = NM.get(it["n"], ("", ""))[0]
            override = (r.get("naming") or {}).get(T)
            jspans = []
            if override:
                lo = max(0, ms - 2000)
                seg = L.norm(view[lo:ms])
                fq = RC.find_quote(seg, L.norm(override), len(seg), hyphen=True)
                if fq:
                    jspans.append((lo + fq[0], lo + fq[1]))
                else:
                    st["naming_override_not_found"] += 1
            if x["where"] != "act":
                js, je = x["span"]
                jspans.append((js, je))
                # shorter joined quotes that still end at the naming sentence's end: start after a clause boundary
                # before the hit (drops a disqualifying phrase earlier in a long sentence)
                h0 = x["hit"][0]
                starts = [js] + [js + m.end() for m in re.finditer(r"(?:[;:]\s|\.\s|\(|,\s)", view[js:h0])] + [h0]
                for j0 in starts[1:]:
                    jspans.append((j0, je))
                # a naming far back (a list of citations "just cited"): the joined quote runs from the naming up to
                # the act sentence (j_end = start of the act sentence), at most 1200 characters
                for j0 in starts:
                    if 0 < s0 - j0 <= 1200 and je < s0:
                        jspans.append((j0, s0))
            row, reason = None, None
            tries = []
            for (m0, m1) in mains:
                while m1 > m0 and view[m1 - 1] in " \n":
                    m1 -= 1
                mq = L.norm(view[m0:m1])
                ev = pick_ev(tgt, mq, nm_t, nm_w, res, index)
                if ev and ev_in(ev, mq, tgt, index):
                    tries.append(("antecedent:onesentence", m0, m1, None, ev))
                for (j0, j1) in jspans:
                    while j1 > j0 and view[j1 - 1] in " \n":
                        j1 -= 1
                    while j0 < j1 and view[j0] in " \n":
                        j0 += 1
                    jq = L.norm(view[j0:j1])
                    ev = pick_ev(tgt, jq, nm_t, nm_w, res, index)
                    tries.append(("antecedent:joined", m0, m1, (j0, j1), ev))
            # last resort: a plain row whose evidence stands in the certifier's window [start-400, end+400)
            for (m0, m1) in mains:
                while m1 > m0 and view[m1 - 1] in " \n":
                    m1 -= 1
                wq = L.norm(view[max(0, m0 - 400):m1 + 400])
                ev = pick_ev(tgt, wq, nm_t, nm_w, res, index)
                tries.append(("antecedent:window", m0, m1, None, ev))
            first_reason = None
            for rule, m0, m1, jsp, ev in tries:
                mq = L.norm(view[m0:m1])
                ml = RC.ascii_lower(mq)
                why = None
                if rule == "antecedent:joined":
                    j0, j1 = jsp
                    jq = L.norm(view[j0:j1])
                    if j1 <= j0:
                        why = "joinedMismatch"
                    elif j1 > m0:
                        why = "joinedAfterMain"
                    elif m0 - j1 > gapmax:
                        why = "joinedGap"
                    elif any(d in RC.ascii_lower(jq) for d in list(dq_treat) + list(dqj)):
                        why = "joinedDisqualified"
                    elif not any(p in ml for p in ana):
                        why = "noAnaphor"
                    carrier = jq
                    ctx = L.norm(view[max(0, j0 - 200):j1])
                elif rule == "antecedent:onesentence":
                    carrier = mq
                    ctx = L.norm(view[max(0, m0 - 200):m1])
                else:
                    carrier = L.norm(view[max(0, m0 - 400):m1 + 400])
                    ctx = L.norm(view[max(0, m0 - 600):m1 + 400])
                if why is None:
                    if not ev:
                        why = "no_evidence"
                    elif not ev_in(ev, carrier, tgt, index):
                        why = "evidenceNotInCarrier"
                    elif ev.startswith("name:") and not name_consistent(ctx, ev, nm_t):
                        why = "nameCollision"
                    elif ev.startswith("cite:") and not cite_consistent(ctx, ev, nm_t):
                        why = "citeCaptionMismatch"
                    elif part is None:
                        why = "part"
                    elif not any(v in ml for v in treat[kind]):
                        why = "noCue"
                    elif any(d in ml for d in dq_treat):
                        why = "disqualified"
                if why is None:
                    row = {"rule": rule, "table": "treatments", "by": it["n"], "target": tgt, "kind": kind,
                           "scope": scope, "main": [m0, m1], "part": part, "ev": ev,
                           "joined": ([{"rel": "antecedent", "span": list(jsp), "part": part, "label": "-"}]
                                      if jsp else []),
                           "claim": "-", "doctrine": "-", "field_limit": "-", "anchor": None, "anchor_part": "-",
                           "reader": "claude-subagent:antecedent", "confidence": r.get("confidence"),
                           "note": "antecedent %s %s tier=%s jlen=%s gap=%s" % (
                               i, T, it.get("tier", ""), (jsp[1] - jsp[0]) if jsp else "-",
                               (m0 - jsp[1]) if jsp else "-")}
                    break
                if first_reason is None:
                    first_reason = why
            if row is None:
                reason = first_reason or "no_try"
            ev = row["ev"] if row else None
            key = (it["n"], tgt)
            if reason is None and key in pairs and not a.keep_base:
                reason = "base_has_pair"
            if reason is None and key in seen:
                reason = "duplicate_pair"
            if reason:
                st["rej_" + reason] += 1
                rejects.append([i, T, reason, it["n"], tgt, kind, row["rule"] if row else "-", ev or "-"])
                continue
            seen[key] = 1
            rows.append(row)
            st["rows_" + row["rule"].split(":")[1]] += 1
            st["kind_" + kind] += 1
    with open(a.out, "w", encoding="utf-8", newline=NL) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + NL)
    with open(os.path.join(os.path.dirname(a.out), "rows_rejects.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for rj in rejects:
            f.write("\t".join(str(v) for v in rj) + NL)
    st["anaphor_list"] = "cue_table" if ana_final else "fallback"
    with open(os.path.join(os.path.dirname(a.out), "rows_stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(st), f, indent=1)
    print(json.dumps(dict(st), indent=1))


if __name__ == "__main__":
    main()
