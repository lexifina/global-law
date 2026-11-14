"""fjc8 linker: the district decision under review in a federal court of appeals opinion, when round 6's
below_other gives none (rules in RULES.md next to this file).

    python -X utf8 fjc_link.py run [--procs 10] [--shards a,b]   -> work/link/<shard>.rows.jsonl (+ .stats.json)
    python -X utf8 fjc_link.py merge                             -> rows_<variant>.jsonl, link_stats.json

Reads only the round-6 cache, graph/nodes.tsv, court facts, decision texts (git) and the base history table of
round7/stage/v3 (to know which opinions already have a decision-under-review row). No key, no list of cases.

Rule F1 (cap-2 extended anchor). Acting decision D: a federal court of appeals opinion (tier A, system 0) with no
round-6 below_other row and no base review-kind row on a trial / bankruptcy court decision. Candidate J: a cited
decision of a district / bankruptcy court of D's circuit, dated 0..6 years before D, whose caption is D's caption
(round 6 cap 2), cited in the opinion of the court, never with a history tag, a signal, an earlier / interlocutory /
later-proceeding mark (round 6's tests on every citation of J), and failing round 6 only because the citation
sentence (or it plus the one before) does not name the court below. Uniqueness: J is the only decision of a
district / bankruptcy court of the circuit in the window that shares a party name with D's caption (cap >= 1), and
no decision of D's court or a higher court with D's caption is dated after J (earlier appeal; round 6
`reviewed_before`). Anchor: from the start of the nearest sentence before the citation (<= 1,500 characters back,
same part, no other decision's citation in between) that names J's court by one of its phrases ("district court",
"bankruptcy court", "trial court", "court below" ...), through the end of the citation sentence; failing that, the
citation sentence through the end of the next sentence when that one names J's court. Round 6's earlier /
interlocutory / anchor-disqualifier tests run on the whole anchor and its later-events test after the citation.
Disposition: round 6's `decide` (direct review), dated-otherwise and mixed end-zone rules unchanged, with S1
(fjc_scope.py: a consequence dismissal is not a second act) and a sanity test: the act word must not sit inside a
quotation, a condition or a party's statement (round 6 tested only the text before the reader's match start).
Targets: district courts only (a bankruptcy court's order reaches a court of appeals through the district court /
BAP). Ruling-type test: when the 400 characters before the citation sentence and the sentence name a kind of
ruling (motion to dismiss, summary judgment, injunction, trial / verdict / sentence, fees, remand to state court)
and the judgment line names kinds too, they must share one (else another ruling of the same docket).
F3: when no court phrase is near, a head-matter line naming the court with the shared party tokens (name:).
F2 (one caption side, FJC8_F2=1) failed its blind audit (r8f02, 62/80) and is off by default.
"""
import argparse, collections, gzip, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diag  # noqa: E402
from diag import BO, L  # noqa: E402
import fjc_scope  # noqa: E402

fjc_scope.patch(BO)   # rule S1 (scope): a consequence dismissal does not make a whole reversal partial

C = BO.C
NL = chr(10)
WORK = os.path.join(HERE, "work", "link")
BACK = 1500
TIGHT = 400
DISTINCT_DF = 5000
F2_ON = os.environ.get("FJC8_F2") == "1"   # F2 failed its blind audit (r8f02): off by default
B4SC = os.path.join(L.C2, "round7", "agents", "b4sc", "work")
CUE_PHRASES = {"district court", "bankruptcy court", "bankruptcy judge", "trial court", "court below", "tax court",
               "court of claims"}   # court phrases that are also certificate anchor cues
REVIEW_KINDS = {"reversed", "vacated", "affirmed", "modified", "reviewDismissed"}
G = {}


class Why:
    """Counter proxy that also logs each drop:* reason with the decision (and target)."""

    def __init__(self, st, n, j=None):
        self.st, self.n, self.j = st, n, j

    def __getitem__(self, k):
        return self.st[k]

    def __setitem__(self, k, v):
        if k.startswith("drop:") or k == "rows":
            G.setdefault("why", []).append((self.n, self.j, k))
        self.st[k] = v


def init():
    BO.init()
    G["based"] = set(json.load(open(os.path.join(HERE, "work", "base_by_trial.json"))))
    G["tokdf"] = json.load(open(os.path.join(B4SC, "tokdf.json"), encoding="utf-8"))
    G["inst"] = set(json.load(open(os.path.join(B4SC, "inst_tokens.json"), encoding="utf-8")))


def cap_any(d_all, d_sides, j):
    return BO.cap_rel(d_all, BO.G["N"].name(j), d_sides)


def own_keys(j):
    """compact citation keys of decision j (its own citations in nodes.tsv)."""
    row = L.node_row(j)
    ks = set()
    for c in (row[5] if len(row) > 5 else "").split("|"):
        c = c.strip()
        m = C.CITE_RX.search(c)
        if m:
            k = C.cite_key(m)
            if k:
                ks.add(re.sub(r"[^a-z0-9]", "", k.lower()))
    return ks


def part_bounds(z, pos):
    for a, b, p in z["parts"]:
        if a <= pos < b:
            return a, b, p
    return None


def find_anchor(T, cw, z, phrases, jkeys):
    """(a0, a1, how) or (None, why)."""
    c0, c1 = cw["c"]
    s0, s1 = cw["s"]
    pb = part_bounds(z, c0)
    if pb is None:
        return None, "no_part"
    p0, p1, _p = pb
    want = (phrases & CUE_PHRASES) | {"court below"}
    lo = max(p0, (c0 - TIGHT) if cw.get("tight") else (s0 - BACK))
    best = None
    for m in BO.COURT_RX.finditer(T, lo, c0):
        if BO.norm_ws(m.group(1)) in want:
            best = m
    if best is not None:
        a0 = C.sentence_span(T, best.start(), best.end())[0]
        a0 = max(a0, p0)
        # no citation of another decision between the court phrase and J's citation
        for m in C.CITE_RX.finditer(T, best.end(), c0):
            k = C.cite_key(m)
            if k and re.sub(r"[^a-z0-9]", "", k.lower()) not in jkeys:
                best = None
                break
        if best is not None:
            return (a0, s1, "back"), ""
    # forward: the next sentence names the court
    if s1 < p1 and not cw.get("tight"):
        k = s1
        while k < p1 and T[k] in " ":
            k += 1
        if k < p1:
            n0, n1 = C.sentence_span(T, k, k + 1)
            n1 = min(n1, p1)
            for m in BO.COURT_RX.finditer(T, k, n1):
                if BO.norm_ws(m.group(1)) in want:
                    return (s0, n1, "fwd"), ""
    return None, "no_court_phrase_near"


WORD_RX = re.compile(r"[A-Za-z0-9]+")
SEE_TOK = re.compile(r"(?:^|[\s(\[;,])(?:[Ss]ee|[Cc]f\.|e\.\s?g\.)(?=[,\s])")
CITE_END = re.compile(r"\d\s*\)\s*[.;,]|\b\d{1,4}\s+[A-Z][A-Za-z.\s]{0,20}\d{1,5}\b")
COND = re.compile(r"\b(?:if|unless|whether|when|where|may|might|could|would|should\s+not|only)\b", re.I)


def see_before(cw):
    """the citation (or its case name) is introduced by "See" / "Cf." / "e.g.": the last such token in the 200
    characters before the citation, with no other citation or sentence end between it and the citation"""
    w0, wt = cw["w"]
    c0 = cw["c"][0] - w0
    pre = wt[max(0, c0 - 200):c0]
    last = None
    for m in SEE_TOK.finditer(pre):
        last = m
    if last is None:
        return False
    rest = pre[last.end():]
    return len(rest) <= 160 and not CITE_END.search(rest)


OFFICIAL = re.compile(
    r"\b(?:secretary|commissioner|warden|director|administrator|attorney\s+general|superintendent|sheriff|governor|"
    r"mayor|postmaster|chief|collector|comptroller|treasurer|board|commission|department|dept|agency|bureau|"
    r"service|authority|united\s+states|state|commonwealth|people|government|city|county|town|village|township|"
    r"district|officer|marshal|trustee|receiver|council|regents|chairman|chair|president|clerk|auditor|assessor|"
    r"inspector|administration|office|prison|correctional|corrections|immigration|naturalization|internal\s+revenue|"
    r"labor|health|human\s+services|social\s+security)\b", re.I)


def fold(t):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower())


def cap1_kind(d_name, j_name, head=""):
    """F2 admits a one-side caption match only when the side that does not match is (a) the same name spelt
    otherwise (folded case / accents / spacing, similarity >= 0.8: "Kruziki"/"Kruzicki", "Calderón"/"Calderon"),
    or (b) a public officer or body: an officer / body word in that side of either caption, or after that party's
    name in the acting decision's head matter ("HARGAN, Acting Secretary of Health and Human Services"): a
    substituted officer (FRCP 25(d), FRAP 43(c)). -> "fold" | "official" | ""."""
    import difflib
    ds = BO.V_SPLIT.split(d_name or "", maxsplit=1)
    js = BO.V_SPLIT.split(j_name or "", maxsplit=1)
    if len(ds) != 2 or len(js) != 2:
        return ""

    def toks(x):
        return {fold(w) for w in re.findall(r"[A-Za-zÀ-ÿ'’.-]+", x) if len(fold(w)) >= 3}
    dt, jt = [toks(x) for x in ds], [toks(x) for x in js]
    hl = head.lower()
    for a, b in ((0, 1), (1, 0)):
        for sj, sd, oj, od in ((0, a, 1, b), (1, b, 0, a)):
            if not (jt[sj] & dt[sd]) or (jt[oj] & dt[od]):
                continue
            # shared side sj/sd; differing side oj (target) / od (acting)
            if difflib.SequenceMatcher(None, fold(js[oj]), fold(ds[od])).ratio() >= 0.8:
                return "fold"
            if OFFICIAL.search(js[oj]) or OFFICIAL.search(ds[od]):
                return "official"
            for w in re.findall(r"[A-Za-zÀ-ÿ'’-]{3,}", ds[od]):
                for m in re.finditer(r"\b" + re.escape(w.lower()) + r"\b", hl):
                    if OFFICIAL.search(hl[m.end():m.end() + 150].split(" v. ")[0]):
                        return "official"
    return ""


RULING = (
    ("dismiss", re.compile(r"\bmotions?\s+to\s+dismiss\b|\b(?:partial\s+)?dismissal\b|\bdismiss(?:ed|ing)\s+(?:the\s+|his\s+|her\s+|"
                           r"their\s+|its\s+|plaintiffs?['’]?s?\s+)?(?:complaint|claims?|counts?|action|suit|petition)\b", re.I)),
    ("summary", re.compile(r"\bsummary\s+judgments?\b", re.I)),
    ("injunction", re.compile(r"\b(?:preliminary|temporary|permanent)\s+injunctions?\b|\btemporary\s+restraining\b", re.I)),
    ("trial", re.compile(r"\b(?:jury|bench)\s+(?:trial|verdict)\b|\bverdict\b|\bafter\s+(?:a\s+)?trial\b|\bjudgment\s+n\.?\s?o\.?\s?v\b|"
                         r"\bnew\s+trial\b|\bconvict(?:ion|ed)\b|\bsentenc(?:e|ed|ing)\b", re.I)),
    ("fees", re.compile(r"\battorneys?['’]?s?\s+fees?\b|\bcosts\s+and\s+fees\b|\bsanctions?\b", re.I)),
    ("remand_order", re.compile(r"\bremand(?:ing)?\s+(?:the\s+case\s+)?to\s+(?:the\s+)?state\s+court\b", re.I)),
)


def ruling_types(s):
    return {k for k, rx in RULING if rx.search(s)}


def head_anchor(T, z, phrases, shared):
    """F3: the head-matter line naming J's court ("Appeal from the United States District Court for ..."), extended
    back over the caption lines (<= 700 characters, inside one head-matter part) so that it holds the shared party
    tokens of J's caption. -> ((a0, a1, "name:<tokens>"), "") or (None, why)."""
    want = (phrases & CUE_PHRASES)
    toks = sorted({t for t in shared if len(re.sub(r"[^A-Za-z0-9]", "", t)) >= 3})
    distinct = [t for t in toks if t.lower().rstrip("s") not in G["inst"] and G["tokdf"].get(t.lower().rstrip("s"), 0)
                <= DISTINCT_DF]
    if not distinct:
        return None, "head_no_distinct_token"
    for p0, p1, p in z["parts"]:
        if p != "headmatter":
            continue
        for m in BO.COURT_RX.finditer(T, p0, min(p1, p0 + 6000)):
            if BO.norm_ws(m.group(1)) not in want:
                continue
            a1 = min(p1, C.sentence_span(T, m.start(), m.end())[1])
            lo = max(p0, a1 - 700)
            words = {}
            for w in WORD_RX.finditer(T, lo, a1):
                words.setdefault(w.group(0).lower(), w.start())
            have = [t for t in toks if t.lower() in words]
            if not any(t in have for t in distinct):
                continue
            a0 = min(words[t.lower()] for t in have)
            # start the anchor at the beginning of the word's line-free stretch (a caption line)
            return (a0, a1, "name:" + " ".join(t.lower() for t in have)), ""
    return None, "head_no_line"


def guard_anchor(T, a0, a1, cw):
    at = T[a0:a1]
    low = BO.norm_ws(at)
    if BO.EARLIER.search(at):
        return "earlier_proceeding"
    if BO.EARLY.search(at):
        return "interlocutory_ruling"
    c1 = cw["c"][1]
    if BO.LATER.search(T[c1:a1]) or BO.LATER.search(T[a1:a1 + 250]):
        return "later_events"
    if any(q in low for q in BO.DESIGN_DISQ):
        return "earlier_proceeding"
    if not any(q in at.lower() for q in BO.DESIGN_ANCHOR):
        return "no_design_cue"
    return ""


def select(n, g, mrow, st):
    st = Why(st, n)
    """-> list of (j, [cw...], phrases, cls, cap) F1 candidates of decision n (before text checks)."""
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    d_date = int(F.date[n])
    if F.system(dc) != 0 or not d_date:
        return []
    d_cname, d_tier = BO.court_at(dc, d_date)
    if d_tier != "A":
        return []
    st["opinions"] += 1
    if n in G["based"]:
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
        if cls != "trial":   # a bankruptcy court's order reaches a court of appeals through the district court / BAP
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
    if cap < 2 and not F2_ON:
        st["drop:cap1"] += 1
        return []
    if cap < 2:
        # F2: one caption side shared (substituted officers, another lead party, a spelling variant): a shared
        # party token must be distinctive (not institutional, printed in <= 5,000 titles; round 7 b4sc tables)
        shared = {w.lower().rstrip("s") for w in (BO.caption(N.name(j))[0] & d_all)}
        if not any(w not in G["inst"] and G["tokdf"].get(w, 0) <= DISTINCT_DF for w in shared):
            st["drop:cap1_not_distinctive"] += 1
            return []
        if not cap1_kind(mrow[7] if mrow else "", N.name(j), (g["z"] or {}).get("head", [0, ""])[1][:3000]):
            st["drop:cap1_private_side_differs"] += 1
            return []
    if later_same and int(F.date[j]) <= later_same < d_date:
        st["drop:reviewed_before"] += 1
        return []
    whys = []
    keep = []
    for cw in by_j[j]:
        ok, why, anchor, apart = BO.eval_candidate(cw, 2, phrases, True)   # caption tested above
        whys.append(why)
        if cap == 1 and see_before(cw):
            # F2: a decision of one shared caption side introduced by "See" may be authority: the court below must
            # then be named within 400 characters before the citation
            cw = dict(cw, tight=1)
        if BO.OKPART.get(cw["part"]) and (why in ("no_court_phrase", "no_design_cue")
                                          or (cap == 1 and ok and why in ("own", "own_bare"))):
            keep.append(cw)
    bad = [w for w in whys if w in ("history_after_cite", "history_before_cite", "signal", "earlier_proceeding",
                                    "interlocutory_ruling", "later_events", "bracket_see", "named_other_case")]
    if bad:
        st["drop:cite_marked:" + bad[0]] += 1
        return []
    if not keep:
        st["drop:no_eligible_cite:" + ",".join(sorted(set(whys)))] += 1
        return []
    shared = BO.caption(N.name(j))[0] & d_all
    return [(j, keep, phrases, cls, cap, gap, shared)]  # cap 2: F1, cap 1: F2


def finish(n, g, T, cand, st):
    st = Why(st, n, cand[0])
    F = BO.G["F"]
    j, cws, phrases, cls, cap, gap, shared = cand
    z = g["z"]
    if not z:
        st["drop:no_zone"] += 1
        return None
    jkeys = own_keys(j)
    anchor, why = None, "no_cite"
    for cw in cws:
        res, why = find_anchor(T, cw, z, phrases, jkeys)
        if res is None:
            continue
        a0, a1, how = res
        gw = guard_anchor(T, a0, a1, cw)
        if gw:
            why = gw
            continue
        anchor = (a0, a1, how, cw)
        break
    ev = None
    if anchor is None and why == "no_court_phrase_near":
        res, why2 = head_anchor(T, z, phrases, shared)
        if res is not None:
            a0, a1, ev = res
            gw = guard_anchor(T, a0, a1, {"c": [a1, a1]})
            if not gw:
                anchor = (a0, a1, "head", cws[0])
            else:
                why = "head_" + gw
        else:
            why = why2
    if anchor is None:
        st["drop:anchor:" + why] += 1
        return None
    a0, a1, how, cw = anchor
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
    if am and (BO.own_disposition(dsent, am.start()) or COND.search(dsent[:am.start()])):
        # the act word is inside a quotation, a condition or a party's statement ("which may be reversed only when",
        # "unless that award must be vacated"): round 6 tested only the text before the reader's match start
        st["drop:disposition_not_own"] += 1
        return None
    ca = T[max(cw["s"][0] - 400, 0):cw["s"][1]] if how != "head" else ""
    ta, td = ruling_types(ca), ruling_types(dsent)
    if ta and td and not (ta & td):
        # the ruling described at the citation (a motion to dismiss, a summary judgment, an injunction, a verdict,
        # fees) is not the kind of ruling the judgment line acts on: another ruling of the same docket
        st["drop:ruling_mismatch"] += 1
        return None
    if BO.other_dated(dsent, int(F.date[j])):
        st["drop:disposition_dated_otherwise"] += 1
        return None
    apart = BO.OKPART.get(cw["part"], cw["part"])
    st["rows"] += 1
    st["rows:%s:%s:%s:%s" % ("f1" if cap >= 2 else "f2", how, kind, scope)] += 1
    fam = "f1" if cap >= 2 else "f2"
    return {"rule": "below:fjc8_%s_%s" % (fam, how), "table": "history", "claim": "-", "by": n, "target": j, "kind": kind,
            "scope": scope, "disp": [q0, q1], "anchor": [a0, a1], "anchor_part": "headmatter" if how == "head" else apart,
            "ev": ev or ("cite:" + cw["key"]),
            "part": part, "text": "by",
            "note": "%s|%s|cap%d|gap%dd|A|fjc8 %s %s" % (cls, dhow, cap, gap, fam, how)}


def run_shard(path):
    if "F" not in BO.G or "based" not in G:
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
        except Exception as ex:
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
        except Exception as ex:
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
        for n, j, k in G.pop("why", []):
            f.write("\t".join((str(n), "-" if j is None else str(j), k)) + NL)
    return tag, len(rows)


def base_by_trial():
    """acting nodes with a base review-kind history row on a trial / bankruptcy court decision."""
    BO.init()
    F = BO.G["F"]
    out = set()
    with open(os.path.join(L.C2, "round7", "stage", "v3", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 6 or p[4] not in REVIEW_KINDS:
                continue
            try:
                t, by = int(p[1]), int(p[2])
            except ValueError:
                continue
            if F.system(int(F.court[by])) != 0:
                continue
            _ph, cls = BO.tphr(int(F.court[t]), int(F.date[t]))
            if cls in ("trial", "bankr"):
                out.add(by)
    json.dump(sorted(out), open(os.path.join(HERE, "work", "base_by_trial.json"), "w"))
    print("base acting nodes with a trial-court review row:", len(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=10)
    ap.add_argument("--shards")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    if a.cmd == "base":
        base_by_trial()
        return
    paths = [p for p in L.shards() if diag.APP_RX.match(os.path.basename(p)[:-len(".jsonl.gz")])]
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
        with open(os.path.join(HERE, "rows_f1.jsonl"), "w", encoding="utf-8", newline=NL) as f:
            f.writelines(rows)
        json.dump(dict(sorted(tot.items())), open(os.path.join(HERE, "link_stats.json"), "w"), indent=1)
        print("rows", len(rows))


if __name__ == "__main__":
    main()
