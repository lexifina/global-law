"""Round 7, agent doctrine: candidate -> item (main quote, joined tie quote, label D, evidence, field limit, rule verdict).

    python -X utf8 make_items.py [--cands cands.jsonl] [--out items.jsonl]

For each candidate of build_registry.py (a rejection sentence of W holding an unambiguous registered label tied to X):
  1. W's text from git HEAD; the part map; the main quote = the rejection sentence.
  2. The label D: the first of (core, core + noun, noun + " of " + core) that has >= 2 words and >= 8 characters and
     stands (normalised, lower case) in the main quote.
  3. The joined (tie) quote: a sentence of an opinion-of-the-court part of W that holds D, a tie cue, and evidence that
     resolves to X inside the sentence (a citation that the index maps to X, else the caption words of X).
     Preference: W's own strict tie sentence; then a sentence with a citation; then the nearest one.
  4. The rule verdict on the main sentence (rule_ok, reason): the court's present act on D (see `act_rule`).
  5. The field limit ("in the field of ...", "as applied to ...", "insofar as ...", "to the extent ...").
Writes items.jsonl (one object per candidate, with rule_ok / reason) and items_stats.json. No answer key is read.
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round6/history"))
sys.path.insert(0, os.path.expanduser("~/Documents/us-caselaw-lean-work/caselaw-lean-2/round5/recog"))
import r6lib as L  # noqa: E402
import dcommon as DC  # noqa: E402
import recog_common as RCm  # noqa: E402
C = L.reader_common()
NL = "\n"
FACTS = None
COURT_PARTS = {"majority": "majority", "majority~": "majority", "perCuriam": "perCuriam", "plurality": "plurality"}

PAST = re.compile(r"\b(rejected|repudiated|abandoned|discarded|disapproved|overruled|abolished|renounced|disavowed|"
                  r"jettisoned|departed|receded)\b")
PASSIVE_PRESENT = re.compile(r"\b(?:is|are|be|stands?|hereby|now|must\s+be|should\s+be|will\s+be|shall\s+be)\s+"
                             r"(?:\w+\s+){0,2}$")
NEG_BEFORE = re.compile(r"\b(?:not|n't|never|decline[sd]?\s+to|refuse[sd]?\s+to|need\s+not|unwilling\s+to|reluctant\s+to|"
                        r"hesitate\s+to|would|could|might|whether|if|should\s+we|asked\s+to|ask\s+us\s+to|invite[sd]?\s+us\s+to|"
                        r"urge[sd]?\s+us\s+to|without|no\s+(?:sufficient\s+)?reason\s+to)\s+(?:\w+\s+){0,6}$")
OTHER_SPEAKER = re.compile(r"\b(?:argu\w*|contend\w*|contention|urge[sd]?|asserts?|assertion|insists?|suggests?|"
                           r"suggestion|invit\w+|asks?\s+us|petitioners?|respondents?|appellants?|appellees?|"
                           r"dissent\w*|concurr\w*|the\s+(?:trial|district|lower|circuit)\s+court|court\s+of\s+appeals?|"
                           r"commentators?|scholars?|critics?)\b")
CAUSE = re.compile(r"\b(?:statute|legislature|legislative|enact\w*|amend\w*|congress|repeal\w*|codif\w*|rules?\s+of\s+"
                   r"(?:civil|criminal|evidence|appellate)|constitution\s+(?:of|was)|act\s+of)\b")
FIELD = re.compile(r"\b(in\s+the\s+(?:field|area|realm|sphere|domain|context)\s+of\s+[^,;:.()]{3,60}?|as\s+applied\s+to\s+"
                   r"[^,;:.()]{3,60}?|in(?:\s+so|so)far\s+as\s+[^,;:.()]{3,90}?|to\s+the\s+extent\s+(?:that\s+)?"
                   r"[^,;:.()]{3,90}?|so\s+far\s+as\s+[^,;:.()]{3,90}?|as\s+(?:to|respects|regards)\s+[^,;:.()]{3,60}?)"
                   r"(?=\s*[,;:.()]|\s+(?:the|we|it|is|are|has|have|this|that|its)\b)", re.I)
REJ_CUE = re.compile(r"\b(?:has|have)\s+no\s+(?:further\s+|proper\s+|legitimate\s+)?place\b|\bno\s+longer\b|"
                     r"\b(?:reject\w*|repudiat\w*|abandon\w*|discard\w*|disapprov\w*|overrul\w*|abolish\w*|renounc\w*|"
                     r"disavow\w*|jettison\w*|recede[sd]?\s+from|depart\w*\s+from|decline\s+to\s+follow|unsound|"
                     r"erroneous|not\s+(?:the|good)\s+law|cannot\s+(?:survive|stand))\b")


def act_rule(sent, la, lb):
    """(ok, reason, cue): does the sentence state the court's present rejection of the label at [la, lb)?"""
    s = DC.nq(sent)
    best = None
    for m in REJ_CUE.finditer(s):
        a, b = m.start(), m.end()
        if a < lb and b > la:
            continue  # the cue is a word of the label ("manifestly erroneous standard")
        gap = s[min(lb, a):max(la, b)] if (a >= lb or b <= la) else ""
        dist = 0 if gap == "" else len(gap)
        if dist > 160 or ";" in gap:
            continue
        cue = re.sub(r"\s+", " ", m.group(0))
        before = s[max(0, a - 70):a]
        if NEG_BEFORE.search(before) and not cue.startswith("no longer"):
            r = "negated-or-hypothetical"
        elif re.fullmatch(r"\w+(?:ment|tion|ing)", cue.split()[0]) and not cue.startswith("departing"):
            r = "nominal-report"  # "Twigg's abrogation of", "this Court's repudiation of", "our abandonment in"
        elif REPORTED.search(s[max(0, a - 80):a]):
            r = "reported-speech"
        elif PAST.fullmatch(cue.split()[0]) and not PASSIVE_PRESENT.search(s[max(0, a - 30):a]) and \
                "today" not in s[max(0, a - 40):a]:
            r = "past-act"
        elif re.search(r"\b(?:has|have)\s+been\s+$|\bwas\s+$|\bwere\s+$|\bhad\s+(?:been\s+)?$", s[max(0, a - 15):a]) or \
                re.search(r"\bdid\s+(?:\w+\s+){0,3}$", s[max(0, a - 40):a]):
            r = "past-act"
        else:
            r = "ok"
        cand = (0 if r == "ok" else 1, dist, r, cue, a, b)
        if best is None or cand < best:
            best = cand
    if best is None:
        return False, "no-cue-near-label", "", None
    ca, cb = best[4], best[5]
    c0, c1 = clause(s, min(la, ca), max(lb, cb))
    if best[2] != "ok":
        return False, best[2], best[3], (c0, c1)
    if OTHER_SPEAKER.search(s[c0:c1]):
        return False, "other-speaker-context", best[3], (c0, c1)
    if (best[3].startswith("no longer") and CAUSE.search(s[c0:c1])) or CAUSE_SUBJ.search(s[c0:ca]):
        return False, "intervening-cause", best[3], (c0, c1)
    if "?" in s[ca:]:
        return False, "question", best[3], (c0, c1)
    if SEPARATE.search(s):
        return False, "separate-opinion-voice", best[3], (c0, c1)
    if s.lstrip()[:1] in ("“", '"', "‘", "'"):
        return False, "quotation", best[3], (c0, c1)
    return True, "ok", best[3], (c0, c1)


REPORTED = re.compile(r"\b(?:declared|held|stated|noted|explained|said|recognized|observed|concluded|found|reasoned|"
                      r"announced|indicated|suggested)\s+(?:\w+\s+){0,2}that\b")
CAUSE_SUBJ = re.compile(r"\b(?:legislature|general\s+court|congress|amendment|the\s+statute|the\s+act|"
                        r"rules?\s+of\s+(?:civil|criminal|evidence|appellate))\b")
SEPARATE = re.compile(r"\b(?:in\s+my\s+(?:view|opinion|judgment)|i\s+would|i\s+concur|i\s+dissent|i\s+agree|i\s+believe|"
                      r"i\s+think)\b")


BOUND_L = re.compile(r"[;:]\s*|(?:,\s*)?(?:but|and|while|whereas|although|though|because|since)\s+(?=we|this\s+court|the\s+court)")
BOUND_R = re.compile(r"\s*(?:[;:,]|\s(?:and|but|because|which|while|whereas|although|in\s+which)\s)")


def clause(s, a, b):
    """[c0, c1): the clause of s that holds [a, b): from the last ';' / ':' (or a coordinating word before "we")
    before a, to the first ',' / ';' / ':' / "and" / "but" / "because" / "which" after b (sentence ends otherwise)."""
    c0 = 0
    for m in BOUND_L.finditer(s, 0, a):
        c0 = m.end()
    m = BOUND_R.search(s, b)
    c1 = m.start() if m else len(s)
    while c0 < a and s[c0] == " ":
        c0 += 1
    return c0, max(c1, b)


def field_limit(sent):
    m = FIELD.search(sent)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cands", default=os.path.join(HERE, "cands.jsonl"))
    ap.add_argument("--out", default=os.path.join(HERE, "items.jsonl"))
    a = ap.parse_args()
    cands = [json.loads(l) for l in open(a.cands, encoding="utf-8")]
    rej, tie, dq_main, dq_j, rej_lean, tie_lean = DC.lists()
    ws = sorted({c["w"] for c in cands})
    xs = {c["x"] for c in cands}
    info = RCm.nodes_info(set(ws) | xs)
    live = RCm.live_cite_index()
    global FACTS
    FACTS = L.Facts()
    st = collections.Counter()
    out = []
    B = 400
    for bi in range(0, len(ws), B):
        batch = ws[bi:bi + B]
        texts = L.fetch_texts(batch)
        print("batch", bi, len(batch), flush=True)
        # graph citation rows for every citation in these texts (one streamed pass per batch)
        views = {}
        allkeys = set()
        for w in batch:
            if w not in texts:
                continue
            sha, text = texts[w]
            b0 = RCm.body_start(text)
            hw = C.hard_wrapped(text, b0)
            view = C.unwrap_view(text, b0) if hw else text
            pm, _ = (C.part_map2(text) if hw else C.part_map(text))
            views[w] = (sha, text, view, pm)
            for m in C.CITE_RX.finditer(view):
                k = C.cite_key(m)
                if k:
                    allkeys.add(k)
        graph = {k: v for k, v in RCm.graph_cite_rows(allkeys).items()}
        for c in (c for c in cands if c["w"] in views):
            w, x = c["w"], c["x"]
            sha, text, view, pm = views[w]
            s0, s1 = c["s"]
            main_q = L.norm(text[s0:s1])
            it = dict(c)
            it.update({"sha": sha, "main": [s0, s1], "main_q": main_q, "w_name": info.get(w, ("", "", "", ""))[3],
                       "w_cite": info.get(w, ("", "", "", ""))[2], "x_name": info.get(x, ("", "", "", ""))[3],
                       "x_cite": info.get(x, ("", "", "", ""))[2], "w_repo": info.get(w, ("",))[0]})
            nmq = DC.nq(main_q)
            core, noun = c["core"].strip(), c["noun"]
            surfs = []
            for d in (core, core + " " + noun, noun + " of " + core):
                d = DC.nq(d).strip()
                if DC.label_ok(d) and d in nmq and d not in surfs:
                    surfs.append(d)
            if not surfs:
                it.update(rule_ok=False, reason="no-label-surface")
                st["reason:no-label-surface"] += 1
                out.append(it)
                continue
            # tie sentences
            lowv = DC.lower(view)
            tried = set()
            best = None
            own_s0 = {t["s"][0] for t in c.get("own_ties", [])}
            for d in surfs:
                for m in re.finditer(re.escape(d), lowv):
                    p = m.start()
                    part, _ = C.part_at(pm, p)
                    if part not in COURT_PARTS:
                        continue
                    t0, t1 = C.sentence_span(view, p, m.end())
                    if (d, t0) in tried:
                        continue
                    tried.add((d, t0))
                    jq = L.norm(text[t0:t1])
                    njq = DC.nq(jq)
                    if d not in njq:
                        continue
                    tcue = [t for t in tie if t in njq]
                    if not tcue:
                        continue
                    ev, delta = RCm.evidence_for(x, it["x_name"], it["w_name"], jq, live, graph)
                    if not ev:
                        continue
                    dq = [q for q in dq_j if q in njq]
                    pri = (1 if dq else 0, 0 if t0 in own_s0 else 1, 0 if ev.startswith("cite:") else 1,
                           abs(t0 - s0), )
                    cand = (pri, d, t0, t1, jq, COURT_PARTS[part], ev, delta, tcue, dq)
                    if best is None or cand[0] < best[0]:
                        best = cand
            if best is None:
                it.update(rule_ok=False, reason="no-tie-sentence-in-W", label=surfs[0])
                st["reason:no-tie-sentence-in-W"] += 1
                out.append(it)
                continue
            _, d, t0, t1, jq, jpart, ev, delta, tcue, dqj = best
            la, lb = c["la"]
            ok, why, cue, cl = act_rule(main_q, la - s0, lb - s0)
            m0, m1 = s0, s1
            dqm = [q for q in dq_main if q in nmq]
            if dqm and cl is not None:
                # the clause that holds the label and the rejection words, when the whole sentence is disqualified
                sub = DC.nq(main_q[cl[0]:cl[1]])
                if d in sub and not [q for q in dq_main if q in sub]:
                    m0, m1, dqm = s0 + cl[0], s0 + cl[1], []
            mq = L.norm(text[m0:m1])
            rc = [q for q in rej if q in DC.nq(mq)]
            if ok and dqm:
                ok, why = False, "main-disqualified"
            elif ok and not rc:
                ok, why = False, "no-reject-cue-in-list"
            elif ok and dqj:
                ok, why = False, "joined-disqualified"
            def win(a0, a1):
                return L.norm(text[max(0, a0 - 700):a0]) + "⟦" + L.norm(text[a0:a1]) + "⟧" + L.norm(text[a1:a1 + 700])
            it.update({"main": [m0, m1], "main_q": mq, "main_sentence": [s0, s1], "main_win": win(m0, m1), "tie_win": win(t0, t1),
                       "w_court_name": L.Facts.court_name(FACTS, c["w_court"]),
                       "x_court_name": L.Facts.court_name(FACTS, c["x_court"])})
            it.update({"lean_reject_cue": [q for q in rej_lean if q in DC.nq(mq)],
                       "lean_tie_cue": [q for q in tie_lean if q in DC.nq(jq)]})
            it.update({"label": d, "joined": [t0, t1], "joined_q": jq, "joined_part": jpart, "ev": ev,
                       "cite_delta": delta, "tie_cues": tcue, "reject_cues": rc, "dq_main": dqm, "dq_joined": dqj,
                       "same_sentence": int(t0 == s0), "own_tie": int(t0 in own_s0), "field_limit": field_limit(main_q),
                       "rule_ok": ok, "reason": why, "rule_cue": cue})
            st["reason:" + why] += 1
            out.append(it)
    with open(a.out, "w", encoding="utf-8", newline=NL) as f:
        for it in out:
            f.write(json.dumps(it, ensure_ascii=False) + NL)
    st["items"] = len(out)
    st["rule_ok"] = sum(1 for it in out if it["rule_ok"])
    with open(os.path.splitext(a.out)[0] + "_stats.json", "w", encoding="utf-8", newline=NL) as f:
        json.dump(dict(sorted(st.items())), f, indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


if __name__ == "__main__":
    main()
