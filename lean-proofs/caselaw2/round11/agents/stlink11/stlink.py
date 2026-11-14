"""stlink10 linker: the intermediate-court decision under review in a state court-of-last-resort opinion that
reverses / vacates / modifies it, when round 6's below_other (and v9c) gives no row (port of fjc8 F1 / fjc9 W).

    python -X utf8 stlink.py base                     -> work/base_by_app.json (v10d acting nodes with a review-kind
                                                         row on a decision of an intermediate court of their state)
    python -X utf8 stlink.py run [--procs 8] [--tag s1] -> work/link/<shard>.rows.jsonl, rows_<tag>.jsonl, stats

Reads the round-6 cache, graph/nodes.tsv, court facts, decision texts (git), the v9c history table (only to know
which opinions already have a decision-under-review row) and work/pop_capmatch.jsonl (pop.py: same-caption decisions
of the state's intermediate courts, from nodes.tsv). No key, no list of cases.

Acting decision D: an opinion of a state court of last resort (tier L at its date) with no v9c review-kind row on a
decision of its state's intermediate courts. Its judgment line (round 6 `decide` over the intermediate court's
phrases, named or bare) must reverse / vacate / modify: an affirmance gives no row (no status change).
Candidate T: a cited decision of an intermediate court (tier A) of D's state, dated 0..5 years before D, sharing a
party name with D's caption; T must be the only such decision cited (cap >= 1), with D's caption (cap 2); no decision
of D's court (or higher) with that caption dated after T and before D (round 6 `reviewed_before`); and no other
same-caption intermediate decision (cap 2, a distinctive shared party token) dated after T and before D, cited or not
(the latest decision below in the same case: the ruling under review).
Citation: round 6's tests on every citation of T (no history tag, no signal, no named-other-case, no bracket-see);
the citation fails round 6 only for want of a court phrase in its sentence (or it plus the one before), or of a
design anchor cue.
Anchor (rule F1, fjc8): the nearest sentence naming the intermediate court ("Court of Appeals", "Appellate
Division", "Superior Court", "Commonwealth Court", "court below" ...: the court's own phrases that are Lean anchor
cues) <= 1,500 characters back in the same part, no other decision's citation in between; or the next sentence.
Rule W (fjc9): failing that, the nearest such phrase up to 4,000 characters back whose sentence has the court acting
("the Court of Appeals held / reversed / affirmed / concluded ..."), no citation of another decision in it, no other
intermediate-court citation, "supra" between. Round 6's earlier / interlocutory / later-events / disqualifier guards
run on the whole anchor (and the 250 characters after it).
Disposition: round 6 decide (direct review), the mixed end-zone rule, fjc8's own-disposition test, dated otherwise;
scope rule P (fjc9 G2, state words): reversed / vacated "all" -> "unknown" when the majority says a part was not
appealed / not challenged, affirms something, or agrees with the court below.
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fjc_link as FL  # noqa: E402
from fjc_link import BO, L, C  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "link")
GAP = 1826
WIDE_BACK = 4000
NEG = {"reversed", "vacated", "modified"}
REVIEW_KINDS = {"reversed", "vacated", "affirmed", "modified", "reviewDismissed"}
# intermediate-court phrases that are Lean anchor cues (cue_table.json "anchor")
CUE_APP = {"court of appeals", "court of appeal", "appellate division", "appellate court", "appellate term",
           "superior court", "court of civil appeals", "court of criminal appeals", "commonwealth court",
           "court below", "district court of appeal"}
FL.CUE_PHRASES = set(FL.CUE_PHRASES) | CUE_APP
COURT_ACT = re.compile(
    r"^(?:['’]s)?\s+(?:\w+\s+){0,6}?(?:found|finds|held|holds|granted|grants|denied|denies|dismissed|concluded|"
    r"ruled|entered|awarded|ordered|determined|rejected|decided|reasoned|agreed|disagreed|affirmed|affirms|reversed|"
    r"reverses|vacated|modified|upheld|applied|construed|interpreted|noted|stated|explained|observed|recognized|"
    r"opinion|order|decision|judgment|memorandum|ruling|majority|panel|dissent)\b", re.I)
APP_REP = re.compile(r"App\.|A\.\s?D\.|Super\.|Commw\.|Pa\.\s?Cmwlth|Cal\.\s?Rptr|Ill\.\s?App|Ohio\s+App|N\.E\.2d|"
                     r"Misc", re.I)
PARTIAL_HINT = re.compile(
    r"\b(?:not|never)\s+(?:been\s+)?(?:appealed|challenged|contested|cross-appealed)\b|\b(?:does|do|did|has|have|had)\s+not\s+"
    r"(?:appeal|challenge|contest|cross-appeal|seek\s+review|dispute|take\s+issue)\b|\bunappealed\b|\bwe\s+(?:\w+\s+){0,2}"
    r"affirm\b|\baffirm(?:ed)?\s+(?:in\s+part|as\s+to|insofar)|\bin\s+all\s+other\s+respects\b|\bwe\s+agree\s+with\s+the\s+"
    r"(?:court\s+of\s+appeals?|appellate\s+(?:division|court)|superior\s+court|commonwealth\s+court|court\s+below)\b|"
    r"\bonly\s+(?:the|its|his|her|their)\s+(?:\w+\s+){0,4}(?:is|are)\s+(?:reversed|vacated)\b", re.I)
G = {}
GMODE = os.environ.get("STLINK_G") == "1"
GUARD_WHYS = ("earlier_proceeding", "interlocutory_ruling", "later_events")
PAST_WORD = re.compile(r"\b(?:previously|earlier|prior|first|former|once|again|second)\b", re.I)
OWN_ACT = re.compile(
    r"\b(?:we|this\s+court)\s+(?:(?:will|must|therefore|thus|accordingly|now|hereby|also|shall|do|so)\s+){0,3}"
    r"(?:reverse|vacate|remand|affirm|set\s+aside)\b|\b(?:is|are|be)\s+(?:hereby\s+|therefore\s+|accordingly\s+)?"
    r"(?:reversed|vacated|set\s+aside)\b", re.I)
OWN_UP = re.compile(r"\b(?:REVERSED|VACATED)\b")   # case-sensitive (fjc9's OWN_ACT matched any "reversed" under re.I)
APP_ACT = re.compile(r"\b(?:revers|vacat|set\s+aside|affirm|modif)\w*", re.I)
TRIAL_LATER = re.compile(r"^(?:jury|verdict|bench\s+trial|at\s+trial|was\s+tried|the\s+case\s+was\s+tried|"
                         r"(?:proceeded|went)\s+to\s+trial|trial\s+(?:followed|ensued|was\s+held|began|commenced|resulted)|"
                         r"after\s+(?:a\s+)?trial|following\s+(?:a\s+)?trial)$", re.I)
RETRIAL = re.compile(r"\bnew\s+trial\b|\bretri\w+|\bsecond\s+trial\b|\bremand|\bon\s+retrial\b|\bresentenc", re.I)
REVIEW_STEP = re.compile(r"\bpetition\w*\s+(?:\w+\s+){0,3}(?:for\s+)?(?:review|certiorari|leave|transfer|allowance)|"
                         r"\bcertiorari\b|\bleave\s+to\s+appeal\b|\b(?:we|this\s+court)\s+(?:\w+\s+){0,2}"
                         r"(?:granted|allowed|accepted)\b|\bgranted\s+(?:review|certiorari|transfer|leave)\b|"
                         r"\bappeal(?:ed)?\s+(?:to\s+)?this\s+court\b|\bapplication\s+for\s+(?:review|leave)\b", re.I)


def quoted(T, pos):
    pre = T[max(0, pos - 600):pos]
    if pre.count("“") > pre.count("”"):
        return True
    s0 = C.sentence_span(T, pos, pos + 1)[0]
    return T[s0:pos].count('"') % 2 == 1


def exempt(T, m, kind, phrases):
    """rule G-state: the guard word describes the decision under review's own act or the steps that brought it up."""
    w = BO.norm_ws(m.group(0))
    a, b = m.start(), m.end()
    if quoted(T, a):
        return "quote"
    s0, s1 = C.sentence_span(T, a, b)
    s = T[s0:s1]
    if "remand" in w and kind == "EARLIER":
        if PAST_WORD.search(s):
            return ""
        if OWN_ACT.search(s) or OWN_UP.search(s):
            return "own_remand"
        want = (phrases & FL.CUE_PHRASES) | {"court below"}
        for cm in BO.COURT_RX.finditer(T, s0, a):
            if BO.norm_ws(cm.group(1)) in want and APP_ACT.search(T[cm.end():a]):
                return "app_remand"
        return ""
    if kind == "LATER":
        if TRIAL_LATER.match(w) and not RETRIAL.search(s):
            return "trial_before_app"
        if w in ("thereafter", "subsequently", "later") and REVIEW_STEP.search(s) and not PAST_WORD.search(s):
            return "review_step"
        if w == "mandate" and re.search(r"\bmandate\s+(?:shall|will|to)\s+issue|\bissue\s+the\s+mandate", s, re.I):
            return "own_mandate"
    return ""


DMODE = os.environ.get("STLINK_D") == "1"
TMODE = os.environ.get("STLINK_T") == "1"
TRANSFER = re.compile(r"\b(?:grant(?:ed|ing)?|accept(?:ed)?)\s+(?:\w+\s+){0,3}transfer\b|\bon\s+transfer\b|"
                      r"\btransfer\s+(?:is|was|has\s+been|having\s+been)\s+granted\b|\bpetition\s+(?:\w+\s+){0,2}to\s+"
                      r"transfer\b|\bApp(?:ellate)?\.?\s*R(?:ule)?\.?\s*58\s*\(A\)", re.I)
TRIAL_NAMES = ("trial court", "district court", "circuit court", "superior court", "county court",
               "court of common pleas", "chancery court", "probate court", "court below")   # DESIGN10 section 6
INTER_NAMES = ("court of appeal", "appellate", "court of special appeals", "court of civil appeals",
               "court of criminal appeals", "commonwealth court", "district court of appeal")
LINE_VERB = r"(?:\s+(?:is|are)\s+(?:hereby\s+|therefore\s+|accordingly\s+|in\s+all\s+respects\s+)*|\s+)"


def court_lines(T, z, phrases):
    """rule D: own present dispositions that name the intermediate court, anywhere in the majority / per curiam
    parts: "(The) judgment / decision / order of the <court> (is) reversed / vacated / affirmed / modified", "The
    <court> is reversed"; a sentence start; not quoted, argued or generic (round 6 own_disposition)."""
    alt = "|".join(re.escape(p).replace(r"\ ", r"\s+") for p in sorted(phrases - {"court below"},
                                                                        key=len, reverse=True))
    if not alt:
        return []
    # a judgment noun first ("Judgment of the Court of Special Appeals reversed"), or "The <court> is reversed":
    # never the bare past tense "The Court of Appeals reversed" (the intermediate court's own act)
    rx = re.compile(r"(?:the\s+)?(?:(?:(?:judgments?|decisions?|orders?|opinions?|decrees?)\s+of\s+(?:the\s+)?(?:"
                    + alt + r")(?:\s+in\s+this\s+(?:case|cause|matter))?" + LINE_VERB + r")|(?:(?:" + alt +
                    r")(?:\s+in\s+this\s+(?:case|cause|matter))?\s+(?:is|are)\s+(?:hereby\s+|therefore\s+|accordingly\s+)*))"
                    r"(?P<k>affirmed|reversed|vacated|modified)\b", re.I)
    out = []
    for a, b, p in z["parts"]:
        part = BO.OKPART.get(p)
        if part is None:
            continue
        for m in rx.finditer(T, a, b):
            s0, s1 = C.sentence_span(T, m.start(), m.end())
            if T[s0:m.start()].strip(" ([“\"") or s1 - s0 > 400:
                continue   # the match must start its sentence
            sent = T[s0:s1]
            if BO.own_disposition(sent, m.start("k") - s0):
                continue
            cl = BO.parse_disposition(sent)
            if cl:
                out.append((s0, s1, sent, part, cl))
    out.sort()
    return out


def guard_s(T, a0, a1, cw, phrases, used):
    """fjc8 guard_anchor with rule G-state -> reason or ''."""
    at = T[a0:a1]
    for kind, rx in (("EARLIER", BO.EARLIER), ("EARLY", BO.EARLY)):
        for m in rx.finditer(T, a0, a1):
            why = exempt(T, m, kind, phrases) if GMODE else ""
            if not why:
                return "earlier_proceeding" if kind == "EARLIER" else "interlocutory_ruling"
            used.add("%s:%s" % (kind, why))
    c1 = cw["c"][1]
    for lo, hi in ((c1, a1), (a1, a1 + 250)):
        for m in BO.LATER.finditer(T, lo, min(hi, len(T))):
            why = exempt(T, m, "LATER", phrases) if GMODE else ""
            if not why:
                return "later_events"
            used.add("LATER:" + why)
    low = BO.norm_ws(at)
    if any(q in low for q in BO.DESIGN_DISQ):
        return "earlier_proceeding"
    if not any(q in at.lower() for q in BO.DESIGN_ANCHOR):
        return "no_design_cue"
    return ""


def init():
    BO.init()
    G["based"] = set(json.load(open(os.path.join(HERE, "work", "base_by_app.json"))))
    G["pairs"] = set(tuple(x) for x in json.load(open(os.path.join(HERE, "work", "base_pairs.json"))))
    B4 = os.path.join(L.C2, "round7", "agents", "b4sc", "work")
    G["tokdf"] = json.load(open(os.path.join(B4, "tokdf.json"), encoding="utf-8"))
    G["inst"] = set(json.load(open(os.path.join(B4, "inst_tokens.json"), encoding="utf-8")))
    FL.G["tokdf"], FL.G["inst"] = G["tokdf"], G["inst"]
    cm = {}
    for l in open(os.path.join(HERE, "work", "pop_capmatch.jsonl"), encoding="utf-8"):
        d = json.loads(l)
        cm[d["n"]] = [j for j, _g in d["m"]]
    G["capm"] = cm


def distinct_shared(d_all, j_name):
    sh = {t.lower().rstrip("s") for t in (BO.caption(j_name)[0] & d_all)}
    return any(t not in G["inst"] and G["tokdf"].get(t, 0) <= 5000 for t in sh)


def wide_anchor(T, cw, z, phrases, jkeys):
    """rule W (state): -> ((a0, a1, "wide"), "") or (None, why)."""
    c0 = cw["c"][0]
    s0, s1 = cw["s"]
    pb = FL.part_bounds(z, c0)
    if pb is None:
        return None, "no_part"
    p0, p1, _p = pb
    want = (phrases & FL.CUE_PHRASES) | {"court below"}
    lo = max(p0, s0 - WIDE_BACK)
    ms = [m for m in BO.COURT_RX.finditer(T, lo, c0) if BO.norm_ws(m.group(1)) in want]
    for m in reversed(ms):
        if not COURT_ACT.match(T[m.end():m.end() + 90]):
            continue
        a0, e0 = C.sentence_span(T, m.start(), m.end())
        a0 = max(a0, p0)
        for k in C.CITE_RX.finditer(T, a0, min(e0, c0)):
            key = C.cite_key(k)
            if key and re.sub(r"[^a-z0-9]", "", key.lower()) not in jkeys:
                return None, "wide_court_sentence_cites_other"
        for k in C.CITE_RX.finditer(T, m.end(), c0):
            key = C.cite_key(k)
            if key and re.sub(r"[^a-z0-9]", "", key.lower()) not in jkeys and APP_REP.search(k.group(0)):
                return None, "wide_other_app_cite_between"
        if re.search(r"\bsupra\b", T[m.end():c0]):
            return None, "wide_supra_between"
        return (a0, s1, "wide"), ""
    return None, "wide_no_court_act" if ms else "wide_no_phrase"


def select(n, g, mrow, st):
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    sysid = F.system(dc)
    d_date = int(F.date[n])
    if sysid in (0, -1) or not d_date:
        return []
    d_cname, d_tier = BO.court_at(dc, d_date)
    if d_tier != "L":
        return []
    st["opinions"] += 1
    if n in G["based"]:
        st["skip:base_row"] += 1
        return []
    d_all, d_sides = BO.caption(mrow[7] if mrow else "")
    if not d_all and mrow:
        d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
    d_name = BO.norm_ws(d_cname).replace("courts of", "court of")
    later_same = 0
    for cw in g["cw"]:
        if cw["rel"] != "lower" and BO.cap_rel(d_all, N.name(cw["j"]), d_sides) >= 2:
            later_same = max(later_same, int(F.date[cw["j"]]))
    by_j = collections.defaultdict(list)
    info = {}
    for cw in g["cw"]:
        j = cw["j"]
        jc = int(F.court[j])
        if F.system(jc) != sysid:
            continue
        jd = int(F.date[j])
        if BO.court_at(jc, jd)[1] != "A":
            continue
        phrases, cls = BO.tphr(jc, jd)
        if cls != "app":
            continue
        gap = BO.day(d_date) - BO.day(jd)
        if gap < 0 or gap > GAP:
            continue
        cap = BO.cap_rel(d_all, N.name(j), d_sides)
        by_j[j].append(cw)
        ph = {p for p in phrases if p not in d_name}
        if "appellate division" in ph:
            ph.discard("superior court")   # New Jersey: the Superior Court's trial divisions
        info[j] = (ph, cls, cap, gap)
    same_lit = [j for j in by_j if info[j][2] >= 1]
    if not same_lit:
        return []
    st["op_with_samelit"] += 1
    if len(same_lit) > 1:
        st["drop:several_same_lit"] += 1
        return []
    j = same_lit[0]
    phrases, cls, cap, gap = info[j]
    if cap < 2:
        st["drop:cap1"] += 1
        return []
    if (n, j) in G["pairs"]:
        st["skip:pair_in_base"] += 1
        return []
    if later_same and int(F.date[j]) <= later_same < d_date:
        st["drop:reviewed_before"] += 1
        return []
    # the latest decision below in the same case: no other same-caption intermediate decision after T
    jd = int(F.date[j])
    for i in G["capm"].get(n, ()):
        if i != j and int(F.date[i]) > jd and distinct_shared(d_all, N.name(i)):
            st["drop:later_same_caption_below"] += 1
            return []
    whys, keep = [], []
    for cw in by_j[j]:
        ok, why, anchor, apart = BO.eval_candidate(cw, 2, phrases, True)
        whys.append(why)
        if BO.OKPART.get(cw["part"]) and why in ("no_court_phrase", "no_design_cue") + (GUARD_WHYS if GMODE else ()) \
                + (("own", "own_bare") if TMODE else ()):
            keep.append(dict(cw, r6why=why))
    bad = [w for w in whys if w in ("history_after_cite", "history_before_cite", "signal", "bracket_see",
                                    "named_other_case") + (() if GMODE else GUARD_WHYS)]
    if bad:
        st["drop:cite_marked:" + bad[0]] += 1
        return []
    if not keep:
        st["drop:no_eligible_cite:" + ",".join(sorted(set(whys)))] += 1
        return []
    return [(j, keep, phrases, cls, cap, gap)]


def finish(n, g, T, cand, st):
    F = BO.G["F"]
    j, cws, phrases, cls, cap, gap = cand
    z = g["z"]
    if not z:
        st["drop:no_zone"] += 1
        return None
    disps = BO.dispositions(g)
    res, why = BO.decide(disps, phrases, True)
    if DMODE:
        # rule D: only opinions where round 6 found no own disposition; the court-named present-tense lines anywhere
        # in the majority / per curiam parts (judgment line before trailing footnotes)
        if res is not None or why != "no_disposition":
            st["drop:d_not_needed"] += 1
            return None
        disps = court_lines(T, z, phrases)
        res, why = BO.decide(disps, phrases, True)
    if TMODE:
        # class T (DESIGN10 section 6): the judgment line names only another court; it must reverse / vacate the
        # TRIAL court's judgment by name, with no intermediate-court name in the line (trialBridgeD)
        if res is not None or why != "disposition_names_another_court":
            st["drop:t_not_trial_line"] += 1
            return None
        d_name = BO.norm_ws(BO.court_at(int(F.court[n]), int(F.date[n]))[0]).replace("courts of", "court of")
        tph = {p for p in set(BO.TRIAL_PHRASES) | {"trial court", "chancery court", "court of chancery"}
               if p not in d_name and p not in phrases}
        res, why = BO.decide(disps, tph, False)
        if res is None or res[4] != "named" or res[0] not in ("reversed", "vacated"):
            st["drop:t_trial_line:" + (why or (res[0] + ":" + res[4]))] += 1
            return None
        ql = L.norm(T[res[2][0]:res[2][1]]).lower()
        if not any(p in ql for p in TRIAL_NAMES) or any(p in ql for p in INTER_NAMES):
            st["drop:t_line_names"] += 1
            return None
    if res is None:
        st["drop:disp:" + why] += 1
        return None
    kind, scope, (q0, q1), part, dhow = res
    if kind not in NEG:
        st["drop:disp_kind:" + kind] += 1
        return None
    jkeys = FL.own_keys(j)
    anchor, why = None, "no_cite"
    for cw in cws:
        res, why = FL.find_anchor(T, cw, z, phrases, jkeys)
        if res is None:
            res, why = wide_anchor(T, cw, z, phrases, jkeys)
        if res is None:
            continue
        a0, a1, how = res
        used = set()
        gw = guard_s(T, a0, a1, cw, phrases, used)
        if gw:
            why = gw
            continue
        if cw["r6why"] in GUARD_WHYS:
            # the round-6 citation guard fired: rule G-state must clear it on the round-6 spans too
            w0, wt = cw["w"]
            ps = BO.prev_sentence(wt, cw["s"][0] - w0)
            b0 = w0 + ps[0] if ps else cw["s"][0]
            g6 = guard_s(T, min(b0, a0), max(cw["s"][1], a1), cw, phrases, used)
            if g6:
                why = "r6_" + g6
                continue
        if GMODE and not used:
            why = "not_g"   # the plain F1 / W row (class s1)
            continue
        anchor = (a0, a1, how + ("_g" if used else ""), cw, sorted(used))
        break
    if anchor is None:
        st["drop:anchor:" + why] += 1
        return None
    a0, a1, how, cw, used = anchor
    for u in used:
        st["g_used:" + u] += 1
    if scope == "all" and kind in ("affirmed", "reversed", "vacated"):
        zt = " ".join(e[1] for e in (z.get("ends") or []))
        if z.get("full"):
            zt = z["head"][1]
        if z.get("open"):
            zt += " " + z["open"][1]
        other_rx = BO.OWN_NEG if kind == "affirmed" else BO.OWN_AFF
        if other_rx.search(zt) or BO.OWN_MIXED.search(zt):
            scope = "unknown"
            st["scope_unknown_mixed_endzone"] += 1
    dsent = next((d[2] for d in disps if d[0] == q0), "")
    am = BO.ACT.search(dsent)
    if am and (BO.own_disposition(dsent, am.start()) or FL.COND.search(dsent[:am.start()])):
        st["drop:disposition_not_own"] += 1
        return None
    if scope == "all" and kind in ("reversed", "vacated"):
        body = " ".join(T[a:b] for a, b, p in z["parts"] if BO.OKPART.get(p))
        if PARTIAL_HINT.search(body):
            scope = "unknown"
            st["scope_unknown_partial_hint"] += 1
    if TMODE and kind == "reversed" and TRANSFER.search(" ".join(T[a:b] for a, b, p in z["parts"] if BO.OKPART.get(p))):
        # rule T-transfer: a grant of transfer (Indiana App. R. 58(A) and kin) vacates the intermediate opinion
        kind = "vacated"
        st["t_transfer_vacated"] += 1
    if BO.other_dated(dsent, int(F.date[j])):
        st["drop:disposition_dated_otherwise"] += 1
        return None
    apart = BO.OKPART.get(cw["part"], cw["part"])
    st["rows"] += 1
    st["rows:%s:%s:%s" % (how, kind, scope)] += 1
    return {"rule": "below:stlink10_%s%s" % ("t_" if TMODE else "", how), "table": "history", "claim": "-", "by": n, "target": j, "kind": kind,
            "scope": scope, "disp": [q0, q1], "anchor": [a0, a1], "anchor_part": apart,
            "ev": "cite:" + cw["key"], "part": part, "text": "by",
            "note": "%s|%s|cap%d|gap%dd|L|stlink10 %s %s" % (cls, dhow, cap, gap, how, ",".join(used))}


def run_shard(path):
    if "based" not in G:
        init()
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    st = collections.Counter()
    pend = []
    for n, g in L.decisions(path):
        if not g["cw"]:
            continue
        try:
            cs = select(n, g, meta.get(n), st)
        except Exception as ex:  # noqa: BLE001
            st["error_select"] += 1
            if st["error_select"] <= 3:
                sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
            continue
        for c in cs:
            pend.append((n, g, c))
    st["candidates"] = len(pend)
    texts = L.fetch_texts([n for n, _, _ in pend]) if pend else {}
    rows = []
    for n, g, c in pend:
        if n not in texts:
            st["drop:no_text"] += 1
            continue
        T = L.norm(texts[n][1])
        try:
            r = finish(n, g, T, c, st)
        except Exception as ex:  # noqa: BLE001
            st["error_finish"] += 1
            if st["error_finish"] <= 3:
                sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
            continue
        if r:
            rows.append(r)
    with open(os.path.join(WORK, tag + ".rows.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, tag + ".stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    return tag, len(rows)


def base():
    BO.init()
    F = BO.G["F"]
    out, pairs = set(), set()
    with open(os.path.join(L.C2, "round10", "stage", "v10d", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 6:
                continue
            try:
                t, by = int(p[1]), int(p[2])
            except ValueError:
                continue
            pairs.add((by, t))
            if p[4] not in REVIEW_KINDS:
                continue
            bc, tc = int(F.court[by]), int(F.court[t])
            if F.system(bc) in (0, -1) or F.system(bc) != F.system(tc):
                continue
            if BO.court_at(tc, int(F.date[t]))[1] == "A":
                out.add(by)
    json.dump(sorted(out), open(os.path.join(HERE, "work", "base_by_app.json"), "w"))
    json.dump(sorted(pairs), open(os.path.join(HERE, "work", "base_pairs.json"), "w"))
    print("v10d acting nodes with a review row on an intermediate decision of their state:", len(out), "pairs", len(pairs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--shards")
    ap.add_argument("--tag", default="s1")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    if a.cmd == "base":
        base()
        return
    import pop
    paths = pop.state_shards()
    if a.shards:
        want = set(a.shards.split(","))
        paths = [p for p in paths if os.path.basename(p)[:-len(".jsonl.gz")] in want]
    paths.sort(key=os.path.getsize, reverse=True)
    if a.cmd == "run":
        if a.procs <= 1:
            init()
            for p in paths:
                print(run_shard(p), flush=True)
        else:
            for tag, k in L.pmap(run_shard, paths, procs=a.procs, initializer=init):
                print(tag, k, flush=True)
    if a.cmd in ("run", "merge") and not a.shards:
        tot = collections.Counter()
        rows = []
        for p in sorted(paths):
            tag = os.path.basename(p)[:-len(".jsonl.gz")]
            rp = os.path.join(WORK, tag + ".rows.jsonl")
            if os.path.exists(rp):
                rows += [l for l in open(rp, encoding="utf-8") if l.strip()]
                tot.update(json.load(open(os.path.join(WORK, tag + ".stats.json"))))
        with open(os.path.join(HERE, "rows_%s.jsonl" % a.tag), "w", encoding="utf-8", newline=NL) as f:
            f.writelines(rows)
        json.dump(dict(sorted(tot.items())), open(os.path.join(HERE, "link_stats_%s.json" % a.tag), "w"), indent=1)
        print("rows", len(rows))


if __name__ == "__main__":
    main()
