"""fjc9 linker: rules W (anchor widening) and G (guard exception) on top of fjc8's F1 (round 8, installed in v8e).

    python -X utf8 fjc9_link.py base                     -> work/base_by_trial.json (acting nodes of v8e with a
                                                            review-kind row on a trial / bankruptcy decision)
    python -X utf8 fjc9_link.py run [--procs 8]          -> work/link/<shard>.rows.jsonl, rows_<tag>.jsonl, stats

Same candidate selection as F1 (federal court of appeals opinion with no review-kind row on a trial-court decision;
J = the unique district decision of the circuit, 0..6 years before, sharing a party with the caption; J's caption is
the opinion's caption (cap 2); no later decision of the court with that caption between J and the opinion), and the
same disposition reading. Only rows that F1 does NOT make are written (each row needs W or G):

W  anchor widening. When no court phrase is found within F1's window (1,500 characters back with no other
   decision's citation between, or the next sentence): the nearest court phrase of J's court ("district court",
   "trial court", "court below") up to 4,000 characters back in the same part, whose sentence names the court below
   acting ("the district court granted / held / found / dismissed / its order ...") and holds no citation of
   another decision, with no citation of another trial-level decision (F. Supp., F.R.D., B.R.) and no "supra" /
   case name of another case's ruling between it and J's citation. Anchor = that sentence through the end of J's
   citation sentence (one contiguous quote; the anchor cue and J's citation are inside it, as round 8).
G  guard exception. Round 6's earlier / interlocutory / later-events guards (on the citation and on the anchor) do
   not fire on a guard word that describes the decision under review's own history or this appeal:
   - the word is inside a quotation;
   - "remand" in the acting court's own disposition sentence ("we reverse ... and remand", "is vacated and the
     matter remanded"), or "on / after / following (our) remand" before J's citation in J's own citation sentence
     whose subject is the court below (the cited ruling is the ruling on remand);
   - "interlocutory" in a sentence about this appeal ("this is an interlocutory appeal from ...");
   - "preliminary / temporary (injunction | restraining)" when the opinion says the appeal is from an injunction
     ruling (appeal ... injunction, 1292(a)(1));  "denied ... motion to dismiss / summary judgment" when the opinion
     says the appeal is interlocutory (1292(b), interlocutory appeal, collateral order, qualified immunity);
   - "at first glance / blush";
   - "mandate" in "the mandate shall / will issue"; a later-events word in a sentence that certifies the cited
     ruling for appeal or enters judgment on it (Rule 54(b), 1292(b), "permitting ... to appeal");
   - "jury" in a sentence with no trial / verdict / finding / conviction word (e.g. "the evidence they would like a
     jury to accept").
   Every other guard word still fires.
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fjc_link as FL  # noqa: E402
from fjc_link import BO, L, C, diag  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "link")
WIDE_BACK = 4000
GUARD_WHYS = ("earlier_proceeding", "interlocutory_ruling", "later_events")

TRIAL_REP = re.compile(r"F\.\s?Supp|F\.\s?R\.\s?D|B\.\s?R\b|Bankr", re.I)
COURT_ACT = re.compile(
    r"^(?:['’]s)?\s+(?:\w+\s+){0,6}?(?:found|finds|held|holds|granted|grants|denied|denies|dismissed|dismisses|concluded|"
    r"ruled|entered|awarded|ordered|determined|rejected|decided|reasoned|agreed|disagreed|enjoined|sentenced|certified|"
    r"issued|refused|declined|accepted|adopted|construed|interpreted|applied|upheld|struck|excluded|admitted|"
    r"instructed|noted|stated|explained|observed|believed|thought|considered|treated|characterized|described|"
    r"opinion|order|decision|judgment|memorandum|ruling|findings|conclusion|analysis)\b", re.I)
OWN_ACT = re.compile(
    r"\b(?:we|this\s+court)\s+(?:(?:will|must|therefore|thus|accordingly|now|hereby|also|shall|do|so)\s+){0,3}"
    r"(?:reverse|vacate|remand|affirm|set\s+aside)\b|\b(?:is|are|be)\s+(?:hereby\s+|therefore\s+|accordingly\s+)?"
    r"(?:reversed|vacated|set\s+aside)\b|\b(?:REVERSED|VACATED)\b", re.I)
PAST_WORD = re.compile(r"\b(?:previously|earlier|prior|first|former|before|once)\b", re.I)
ON_REMAND = re.compile(r"\b(?:on|after|following|upon)\s+(?:(?:our|the|this\s+court['’]s|a)\s+)?remand\b", re.I)
THIS_APPEAL = re.compile(r"\b(?:this|the\s+present|the\s+instant)\s+(?:interlocutory\s+)?appeal\b|\bappeals?\s+from\b|"
                         r"\binterlocutory\s+appeal\b", re.I)
INJ_APPEAL = re.compile(r"\bappeal\w*\s+(?:\w+\s+){0,8}?(?:preliminary|temporary|permanent)?\s*injunct|\b1292\s*\(a\)\s*\(1\)|"
                        r"\b(?:grant|denial|issuance|entry|refusal)\s+of\s+(?:a\s+|the\s+|their\s+|its\s+|his\s+|her\s+)?"
                        r"(?:motions?\s+for\s+(?:a\s+)?)?(?:preliminary|temporary)\s+(?:injunct|restrain)", re.I)
INTERLOC_APPEAL = re.compile(r"\b1292\s*\(b\)|\binterlocutory\s+appeal|\bcollateral\s+order|\bqualified\s+immunity\b", re.I)
CERT_APPEAL = re.compile(r"\b54\s*\(b\)|\b1292\s*\(b\)|\bpermitting\s+(?:\w+\s+){0,4}to\s+appeal|\bcertif\w+\s+(?:\w+\s+){0,6}?"
                         r"(?:appeal|interlocutory)", re.I)
TRIAL_WORDS = re.compile(r"\btrial|\bverdict|\btried\b|\bconvict|\bfound\b|\bfinding|\breturned\b|\bawarded\b", re.I)
G = {}
# G2 (after r9f01): the exemptions whose rows were wrong rulings in the blind audit are off; G rows get rule P
G2 = os.environ.get("FJC9_G2") == "1"
G2_OFF = {"certified_for_appeal", "jury_not_trial"}
# rule P (scope): a whole reversal / vacatur read from the judgment line is "unknown" when the opinion says that a
# part of the decision below was not appealed / not challenged, affirms something, or agrees with the court below
PARTIAL_HINT = re.compile(
    r"\b(?:not|never)\s+(?:been\s+)?(?:appealed|challenged|contested|cross-appealed)\b|\b(?:does|do|did|has|have|had)\s+not\s+"
    r"(?:appeal|challenge|contest|cross-appeal|seek\s+review|dispute|take\s+issue)\b|\bunappealed\b|\bwe\s+(?:\w+\s+){0,2}"
    r"affirm\b|\baffirm(?:ed)?\s+(?:in\s+part|as\s+to|insofar)|\bin\s+all\s+other\s+respects\b|\bwe\s+agree\s+with\s+the\s+"
    r"(?:district|trial)\s+court\b|\bwithin\s+(?:its|the\s+(?:district|trial)\s+court['’]s)\s+discretion\b|\bonly\s+"
    r"(?:the|its|his|her|their)\s+(?:\w+\s+){0,4}(?:is|are)\s+(?:reversed|vacated)\b", re.I)


def quoted(T, pos):
    """inside a quotation: more opening than closing curly quotes (or an odd number of straight double quotes)
    between the start of the sentence-paragraph (<= 600 characters back) and pos."""
    pre = T[max(0, pos - 600):pos]
    if pre.count("“") > pre.count("”"):
        return True
    s0 = C.sentence_span(T, pos, pos + 1)[0]
    return T[s0:pos].count('"') % 2 == 1


def sent_of(T, a, b):
    s0, s1 = C.sentence_span(T, a, b)
    return s0, s1, T[s0:s1]


# J (D9-9, DESIGN9 section 8): the court below named only as a judge ("the district judge", "the magistrate judge",
# "the trial judge"); certified under claim anchorWide with the judge strings; no rule G, no rule P in this mode
JMODE = os.environ.get("FJC9_J") == "1"
JUDGE_CUES = ("district judge", "magistrate judge", "trial judge")
if JMODE:
    FL.CUE_PHRASES = set(FL.CUE_PHRASES) | set(JUDGE_CUES)


def anchor_cues():
    if "anchor_cues" not in G:
        import json as _j
        t = _j.load(open(os.path.join(os.path.expanduser("~"), "Documents", "global-law-lean", "lean-proofs", "tools",
                                      "caselaw2", "cues", "cue_table.json"), encoding="utf-8"))
        G["anchor_cues"] = [c for c in t["anchor"] if c]
    return G["anchor_cues"]


def exempt(T, m, kind, ctx):
    if JMODE:
        return ""
    why = exempt0(T, m, kind, ctx)
    return "" if (G2 and why in G2_OFF) else why


def exempt0(T, m, kind, ctx):
    """True when the guard word m (a match on T at absolute offsets) describes the decision under review's own
    history or this appeal (rule G)."""
    w = m.group(0).lower()
    a, b = m.start(), m.end()
    if quoted(T, a):
        return "quote"
    s0, s1, s = sent_of(T, a, b)
    if "remand" in w:
        if OWN_ACT.search(s) and not PAST_WORD.search(s):
            return "own_remand"
        cw = ctx["cw"]
        if s0 <= cw["c"][0] < s1 + 2 and a < cw["c"][0] and ON_REMAND.search(T[max(s0, a - 40):b]):
            return "on_remand_ruling"
        return ""
    if kind == "EARLY":
        if "interlocutory" in w and THIS_APPEAL.search(s):
            return "this_appeal"
        if re.match(r"(?:preliminar|temporary)", w) and ctx["inj_appeal"]:
            nxt = T[b:b + 40].lower()
            if "injunct" in nxt or "restrain" in nxt:
                return "injunction_appeal"
        if w.startswith("denied") and ctx["interloc_appeal"]:
            return "interlocutory_appeal"
        if re.match(r"at\s+first", w) and re.match(r"\s*(?:glance|blush)", T[b:b + 12], re.I):
            return "idiom"
        return ""
    if kind == "LATER":
        if w == "mandate" and re.search(r"\bmandate\s+(?:shall|will|to)\s+issue|\bissue\s+the\s+mandate", s, re.I):
            return "own_mandate"
        if CERT_APPEAL.search(s):
            return "certified_for_appeal"
        if w == "jury" and not TRIAL_WORDS.search(s):
            return "jury_not_trial"
        return ""
    if kind == "EARLIER":
        if re.match(r"at\s+first", w):
            return ""
        return ""
    return ""


def guard_x(T, a0, a1, cw, ctx, used):
    """F1's guard_anchor with rule G. -> reason or ""."""
    at = T[a0:a1]
    for kind, rx, lo, hi in (("EARLIER", BO.EARLIER, a0, a1), ("EARLY", BO.EARLY, a0, a1)):
        for m in rx.finditer(T, lo, hi):
            why = exempt(T, m, kind, dict(ctx, cw=cw))
            if not why:
                return "earlier_proceeding" if kind == "EARLIER" else "interlocutory_ruling"
            used.add("%s:%s" % (kind, why))
    c1 = cw["c"][1]
    for lo, hi in ((c1, a1), (a1, a1 + 250)):
        for m in BO.LATER.finditer(T, lo, min(hi, len(T))):
            why = exempt(T, m, "LATER", dict(ctx, cw=cw))
            if not why:
                return "later_events"
            used.add("LATER:" + why)
    low = BO.norm_ws(at)
    if any(q in low for q in BO.DESIGN_DISQ):
        return "earlier_proceeding"
    if not any(q in at.lower() for q in BO.DESIGN_ANCHOR) and not (JMODE and any(q in low for q in JUDGE_CUES)):
        return "no_design_cue"
    return ""


def wide_anchor(T, cw, z, phrases, jkeys):
    """rule W -> ((a0, a1, "wide"), "") or (None, why)."""
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
        # the court phrase's sentence holds no citation of another decision
        bad = False
        for k in C.CITE_RX.finditer(T, a0, min(e0, c0)):
            key = C.cite_key(k)
            if key and re.sub(r"[^a-z0-9]", "", key.lower()) not in jkeys:
                bad = True
                break
        if bad:
            return None, "wide_court_sentence_cites_other"
        # no other trial-level decision, "supra" or another case's name between the court phrase and J's citation
        for k in C.CITE_RX.finditer(T, m.end(), c0):
            key = C.cite_key(k)
            if key and re.sub(r"[^a-z0-9]", "", key.lower()) not in jkeys and TRIAL_REP.search(k.group(2)):
                return None, "wide_other_trial_cite_between"
        if re.search(r"\bsupra\b", T[m.end():c0]):
            return None, "wide_supra_between"
        return (a0, s1, "wide"), ""
    return None, "wide_no_court_act" if ms else "wide_no_phrase"


def ctx_of(T):
    return {"inj_appeal": bool(INJ_APPEAL.search(T)), "interloc_appeal": bool(INTERLOC_APPEAL.search(T))}


def select(n, g, mrow, st):
    """F1's select (fjc8), except that a citation marked only by round 6's earlier / interlocutory / later-events
    guard is kept as a G candidate (the guard is re-run with rule G on the anchor in finish)."""
    st = FL.Why(st, n)
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    d_date = int(F.date[n])
    if F.system(dc) != 0 or not d_date:
        return []
    d_cname, d_tier = BO.court_at(dc, d_date)
    if d_tier != "A":
        return []
    st["opinions"] += 1
    if n in FL.G["based"]:
        st["skip:base_row"] += 1
        return []
    rows = BO.process(n, g, mrow, collections.Counter(), None)
    if any(BO.tphr(int(F.court[r["target"]]), int(F.date[r["target"]]))[1] in ("trial", "bankr") for r in rows):
        st["skip:r6_row"] += 1
        return []
    d_all, d_sides = BO.caption(mrow[7] if mrow else "")
    if not d_all and mrow:
        d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
    later_same = 0
    for cw in g["cw"]:
        if cw["rel"] != "lower" and BO.cap_rel(d_all, N.name(cw["j"]), d_sides) >= 2:
            later_same = max(later_same, int(F.date[cw["j"]]))
    by_j = collections.defaultdict(list)
    info = {}
    for cw in g["cw"]:
        if cw["rel"] != "lower":
            continue
        j = cw["j"]
        jc = int(F.court[j])
        phrases, cls = BO.tphr(jc, int(F.date[j]))
        if cls != "trial":
            continue
        if not BO.circuit_ok(dc, jc, d_date):
            continue
        gap = BO.day(d_date) - BO.day(F.date[j])
        if gap < 0 or gap > BO.MAX_GAP_DAYS:
            continue
        cap = BO.cap_rel(d_all, N.name(j), d_sides)
        by_j[j].append(cw)
        info[j] = (phrases, cls, cap, gap)
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
    if later_same and int(F.date[j]) <= later_same < d_date:
        st["drop:reviewed_before"] += 1
        return []
    whys, keep = [], []
    for cw in by_j[j]:
        ok, why, anchor, apart = BO.eval_candidate(cw, 2, phrases, True)
        whys.append(why)
        if BO.OKPART.get(cw["part"]) and why in ("no_court_phrase", "no_design_cue") + GUARD_WHYS:
            keep.append(dict(cw, r6why=why))
    bad = [w for w in whys if w in ("history_after_cite", "history_before_cite", "signal", "bracket_see",
                                    "named_other_case")]
    if bad:
        st["drop:cite_marked:" + bad[0]] += 1
        return []
    if not keep:
        st["drop:no_eligible_cite:" + ",".join(sorted(set(whys)))] += 1
        return []
    shared = BO.caption(N.name(j))[0] & d_all
    return [(j, keep, phrases, cls, cap, gap, shared)]


def finish(n, g, T, cand, st):
    st = FL.Why(st, n, cand[0])
    F = BO.G["F"]
    j, cws, phrases, cls, cap, gap, shared = cand
    z = g["z"]
    if not z:
        st["drop:no_zone"] += 1
        return None
    jkeys = FL.own_keys(j)
    ctx = ctx_of(T)
    anchor, why, f1_would = None, "no_cite", False
    for cw in cws:
        used = set()
        res, why = FL.find_anchor(T, cw, z, phrases, jkeys)
        how_extra = ""
        if res is None:
            res, why = wide_anchor(T, cw, z, phrases, jkeys)
        if res is None:
            continue
        a0, a1, how = res
        gw = guard_x(T, a0, a1, cw, ctx, used)
        if gw:
            why = gw
            continue
        if cw["r6why"] in GUARD_WHYS:
            # the round-6 citation guard fired: rule G must clear it on the round-6 spans too (sentence + previous)
            w0, wt = cw["w"]
            ps = BO.prev_sentence(wt, cw["s"][0] - w0)
            b0 = w0 + ps[0] if ps else cw["s"][0]
            g6 = guard_x(T, min(b0, a0), max(cw["s"][1], a1), cw, ctx, used)
            if g6:
                why = "r6_" + g6
                continue
        if not JMODE and how in ("back", "fwd") and cw["r6why"] not in GUARD_WHYS and not used:
            f1_would = True   # F1 makes this row (in v8e already, or dropped there for another reason)
            why = "f1_row"
            continue
        anchor = (a0, a1, how + ("_g" if used else ""), cw, sorted(used))
        break
    if anchor is None:
        st["drop:anchor:" + why] += 1
        return None
    a0, a1, how, cw, used = anchor
    disps = BO.dispositions(g)
    res, why = BO.decide(disps, phrases, True)
    if res is None:
        st["drop:disp:" + why] += 1
        return None
    kind, scope, (q0, q1), part, dhow = res
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
    if JMODE:
        aq = BO.norm_ws(T[a0:a1])
        if any(c in aq for c in anchor_cues()) or not any(c in aq for c in JUDGE_CUES):
            st["drop:j_not_needed"] += 1
            return None
        how = "j_" + how
    if G2:
        if not used:
            st["drop:g2_not_g"] += 1
            return None
        if scope == "all" and kind in ("reversed", "vacated"):
            body = " ".join(T[a:b] for a, b, p in z["parts"] if BO.OKPART.get(p))
            if PARTIAL_HINT.search(body):
                scope = "unknown"
                st["scope_unknown_partial_hint"] += 1
    ca = T[max(cw["s"][0] - 400, 0):cw["s"][1]]
    ta, td = FL.ruling_types(ca), FL.ruling_types(dsent)
    if ta and td and not (ta & td):
        st["drop:ruling_mismatch"] += 1
        return None
    if BO.other_dated(dsent, int(F.date[j])):
        st["drop:disposition_dated_otherwise"] += 1
        return None
    apart = BO.OKPART.get(cw["part"], cw["part"])
    st["rows"] += 1
    st["rows:%s:%s:%s" % (how, kind, scope)] += 1
    for u in used:
        st["g_used:" + u] += 1
    return {"rule": "below:fjc9_%s" % how, "table": "history", "claim": "anchorWide" if JMODE else "-", "by": n, "target": j, "kind": kind,
            "scope": scope, "disp": [q0, q1], "anchor": [a0, a1], "anchor_part": apart,
            "ev": "cite:" + cw["key"], "part": part, "text": "by",
            "note": "%s|%s|cap%d|gap%dd|A|fjc9 %s %s" % (cls, dhow, cap, gap, how, ",".join(used))}


def run_shard(path):
    if "F" not in BO.G or "based" not in FL.G:
        FL.init()
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
    with open(os.path.join(WORK, tag + ".why.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for n, j, k in FL.G.pop("why", []):
            f.write("\t".join((str(n), "-" if j is None else str(j), k)) + NL)
    return tag, len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--shards")
    ap.add_argument("--tag", default="w1")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    FL.WORK = WORK
    if a.cmd == "base":
        FL.base_by_trial()
        return
    paths = [p for p in L.shards() if diag.APP_RX.match(os.path.basename(p)[:-len(".jsonl.gz")])]
    if a.shards:
        want = set(a.shards.split(","))
        paths = [p for p in paths if os.path.basename(p)[:-len(".jsonl.gz")] in want]
    paths.sort(key=os.path.getsize, reverse=True)
    if a.cmd == "run":
        if a.procs <= 1:
            FL.init()
            for p in paths:
                print(run_shard(p), flush=True)
        else:
            for tag, k in L.pmap(run_shard, paths, procs=a.procs, initializer=FL.init):
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
