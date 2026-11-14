"""Round 7, track B4 (b): en banc and docket-linked same-court history rows, tightened (agent b4rehear).

    python -X utf8 r7rehear.py cands  [--procs 22]   claims cache (round 6, read only) -> work/cands.jsonl
    python -X utf8 r7rehear.py feats                 git texts of acting / target / same-docket decisions -> work/feats.json
    python -X utf8 r7rehear.py rows                  -> rows_enbanc.jsonl, rows_docket.jsonl, rows_setaside_rehear.jsonl,
                                                        rows_stats.json, work/dropped.tsv

Starts from the round-6 `rehear` linker (rules/rehear: claims of every candidate decision, citation and docket links)
and adds the round-7 rules of RULES7.md (written next to this file). Rules, never rows: nothing here names a case,
citation, party or docket. No Shepardized, gold, split, heldout or reports file is read.
"""
import sys

sys.dont_write_bytecode = True
import argparse, collections, json, os, re  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
R6H = os.path.join(C2, "round6", "history")
REH = os.path.join(R6H, "rules", "rehear")
sys.path.insert(0, R6H)
sys.path.insert(0, REH)
import r6lib as L  # noqa: E402
import rehear_link as RL  # noqa: E402
import rehear_rules as RR  # noqa: E402

C = L.reader_common()
WORK = os.path.join(HERE, "work")
NL = chr(10)
NEGK = RL.NEGK
OKP = ("majority", "perCuriam", "plurality")


def lower(s):
    return RL.lower(s)


# ================================================================================================ stage 1: candidates
# another court is the actor (the Supreme Court of the United States, or a higher court on certiorari / remand): the
# acting decision only reports what that court did (a state supreme court naming itself is not caught)
SC_ACTOR = re.compile(r"certiorari|\bby\s+the\s+(?:united\s+states\s+|u\.\s?s\.\s+|federal\s+|state\s+)?supreme\s+court|"
                      r"\bsupreme\s+court\s+(?:of\s+the\s+united\s+states\s+)?(?:has\s+|had\s+|then\s+|subsequently\s+|later\s+)?"
                      r"(?:vacated|reversed|remanded|granted|set\s+aside)|\bunited\s+states\s+supreme\s+court|"
                      r"\bremand(?:ed)?\s+(?:from|by)\b", re.I)


def cand_rec(K, rec, st):
    """The round-6 link_one, with every gate that round 6 applied, plus the facts round 7 needs; no round-7 drop
    here (stage 3 applies the round-7 rules, so their counts are visible)."""
    out = []
    enbanc = bool(rec["enbanc"])
    onreh = bool(rec["onreh"]) or bool(rec["notes"]["rehgrant"])
    adopt = bool(rec["notes"]["adopt"]) or bool(rec["notes"]["adhere"])
    improv = bool(rec["notes"]["improv"])
    reinst = [c for c in rec["claims"] if c["kind"] == "reinstated"]

    def target_for(span, dates, flags):
        cl = K.cite_link(rec, span, flags)
        if cl and cl[0] in ("ambiguous", "ctx-nodocket", "ctx-two-cites"):
            st["r6_link_" + cl[0]] += 1
            if cl[0] == "ambiguous":
                return None
            cl = None
        if cl:
            how, j, key, anc, apart, w = cl
            if anc is not None and not RL.anchor_ok(w["t"], "cite:" + key):
                anc = None if how == "cite-sent" else anc
                if how != "cite-sent":
                    cl = None
            if cl:
                stt, dj, _t = K.docket_link(rec, dates)
                if dj is not None and dj != j:
                    st["r6_cite_docket_disagree"] += 1
                    return None
                return {"how": how, "j": j, "ev": "cite:" + key, "anchor": anc, "apart": apart, "atext": w["t"]}
        stt, dj, toks = K.docket_link(rec, dates)
        if dj is None:
            return None
        cap = rec.get("cap")
        ev = "name:" + " ".join(toks)
        if not (cap and RL.anchor_ok(cap["t"], ev)):
            st["r6_docket_name_not_in_caption"] += 1
            return None
        return {"how": "docket", "j": dj, "ev": ev, "anchor": cap["s"], "apart": "headmatter", "atext": cap["t"]}

    def emit(var, src, t, kind, scope, q, part, qt, form, claim, dates, obj, noun, extra=None):
        d = {"n": rec["n"], "court": rec["court"], "date": rec["date"], "docket": rec["docket"], "var": var, "src": src,
             "how": t["how"], "j": t["j"], "ev": t["ev"], "anchor": t["anchor"], "apart": t["apart"] or "",
             "atext": t.get("atext", "")[:600], "kind": kind, "scope": scope, "q": list(q), "part": part, "qt": qt[:900],
             "form": form, "claim": claim, "dates": dates, "obj": obj, "noun": noun, "enbanc": int(enbanc),
             "adopt": int(adopt), "improv": int(improv), "reinst": int(bool(reinst))}
        if extra:
            d.update(extra)
        out.append(d)

    done_neg = False
    for c in rec["claims"]:
        kind = c["kind"]
        if kind is None:
            continue
        if c["minor"] and kind in NEGK:
            kind = "modified"
        qt = c.get("t", "")
        claim = "-"
        if not RL.has_cue(kind, qt):
            # DESIGN7 3.2: "set aside" is a vacatur cue only under a setAside claim
            if kind == "vacated" and (c.get("need") == "set aside") and "set aside" in lower(qt) and \
                    not any(x in lower(qt) for x in RL.DISQ_HIST):
                claim = "setAside"
            else:
                st["r6_skip_nocue_" + kind] += 1
                continue
        if c["part"] not in OKP:
            continue
        own_opinion = c["noun"].startswith("opinion") and re.match(r"(?:the|that)\s+opinions?\b", c["obj"], re.I)
        if not c["self"] and c["form"] not in ("p5", "p3") and not own_opinion:
            continue
        if c["form"] == "p5" and re.search(r"supreme\s+court|certiorari", qt, re.I):
            continue
        if kind in NEGK and enbanc and (adopt or improv) and c["form"] not in ("p1", "p2"):
            continue
        is_banc = enbanc and (c["form"] == "p5" or re.search(r"panel", c["obj"], re.I))
        t = target_for(c["q"], c["dates"], RL.CTX_FLAGS_BANC if is_banc else RL.CTX_FLAGS_ACT)
        if t is None:
            continue
        if is_banc:
            var = "c-vac"
        elif kind == "reinstated":
            var = "e"
        elif onreh or c["inreh"]:
            var = "b"
        else:
            var = "a"
        q = c["q"]
        r0 = max(0, c["m"][0] - q[0] - 70)
        r1 = c["m"][1] - q[0]
        tail = re.split(r"[;:]", qt[r1:r1 + 160])[0]
        partial = bool(c["partial"]) or bool(RL.PARTIAL2.search(qt[r0:r1] + " " + tail))
        scope = "unknown" if (partial or kind == "modified") else "all"
        emit(var, "act", t, kind, scope, q, c["part"], qt, c["form"], claim, c["dates"], c["obj"], c["noun"],
             {"partial": int(partial), "m": c["m"]})
        if kind in NEGK and claim == "-":
            done_neg = True
    if enbanc and not done_neg:
        gs = [g for g in rec["grants"] if not RL.MOTION_THAT.search(g["t"])]
        src = None
        if gs:
            src = ("c-order", gs[0])
        elif not (adopt or improv or reinst):
            rs = [r for r in rec["recitals"] if r["past"] and r["r"] in (0, 1) and RL.REH_POS.search(r["t"]) and
                  not RL.REH_NEG.search(r["t"])]
            if rs:
                src = ("c-reh", rs[0])
        if src and src[1]["part"] in OKP and RL.has_cue("rehearingEnBancGranted", src[1]["t"]):
            g = src[1]
            t = target_for(g["q"], [], RL.CTX_FLAGS_BANC)
            if t is not None:
                emit(src[0], "order" if src[0] == "c-order" else "recital", t, "rehearingEnBancGranted", "all", g["q"],
                     g["part"], g["t"], src[0], "-", [], "", "", {"partial": 0})
    return out


def stage_cands(procs):
    os.makedirs(WORK, exist_ok=True)
    F = L.Facts()
    recs = RL.load_claims()
    print("records", len(recs), flush=True)
    want = set()
    for r in recs:
        for d in RL.dockets(r["docket"]):
            want.add((r["court"], d))
    idx, info = RL.docket_index(want, procs=procs)
    print("docket index", len(idx), len(info), flush=True)
    K = RL.Linker(F, idx, info, 1154)  # round-6 window (99th percentile of citation-linked delays), RULES.md
    st = collections.Counter()
    n = 0
    with open(os.path.join(WORK, "cands.jsonl"), "w", encoding="utf-8", newline=NL) as o:
        for rec in recs:
            for d in cand_rec(K, rec, st):
                # same-docket earlier decisions of the same court (for the latest-opinion and unique-date tests)
                sd = set()
                for dk in RL.dockets(rec["docket"]):
                    for m in idx.get((rec["court"], dk), ()):
                        if m != rec["n"] and info[m][0] and info[m][0] <= rec["date"]:
                            sd.add(m)
                d["same_docket"] = sorted(sd)
                d["sd_info"] = {str(m): [info[m][0], sorted(RL.dockets(info[m][2]))] for m in sd}
                d["d_dockets"] = sorted(RL.dockets(rec["docket"]))
                d["j_date"] = int(F.date[d["j"]])
                d["fed"] = int(F.system(int(F.court[d["j"]])) == 0)
                o.write(json.dumps(d, ensure_ascii=False) + NL)
                n += 1
    json.dump(dict(st), open(os.path.join(WORK, "cands_stats.json"), "w"), indent=1)
    print("candidates", n, dict(st), flush=True)


# ================================================================================================ stage 2: text facts
BANC = RR.BANC
DENIED_BANC = re.compile(r"\b(?:petition|suggestion|request|motion)s?\b[^.;]{0,160}?\b(?:is|are|be|was|were|has\s+been|"
                         r"have\s+been)\s+(?:hereby\s+)?(?:denied|rejected|refused)\b|\brehearing\s+" + BANC +
                         r"\s+(?:is\s+)?denied\b|\bden(?:y|ies|ied)\s+(?:the\s+)?(?:petition|suggestion|rehearing)", re.I)
ORDER_HEAD = re.compile(r"^\s*(?:#+\s*)?(?:ORDER|O\s*R\s*D\s*E\s*R|ORDERS?\s+GRANTING|ORDER\s+GRANTING|AMENDED\s+ORDER)\b",
                        re.M)
REARG = re.compile(r"\brestored\s+to\s+the\s+calendar\b|\bset\s+(?:down\s+)?for\s+reargument\b|\breargument\s+(?:is\s+)?"
                   r"(?:ordered|granted)\b|\bordered\s+(?:to\s+be\s+)?reargued\b", re.I)
# the en banc court limits what it rehears, or acts as to some parties / issues only
LIMIT = re.compile(r"\blimited\s+to\b|\bsole\s+(?:issue|question)\b|\blimited\s+(?:its|our|the)\s+(?:consideration|review|"
                   r"rehearing)\b|\bonly\s+(?:as\s+to|on\s+the\s+(?:issue|question)|with\s+respect\s+to|insofar)\b|"
                   r"\bas\s+to\s+(?:the\s+)?(?:appellants?|appellees?|defendants?|petitioners?|respondents?|plaintiffs?)\b|"
                   r"\bon\s+the\s+(?:limited\s+)?(?:issue|question)s?\s+of\b|\binsofar\s+as\b|\bin\s+part\b|\bportions?\s+of\b|"
                   r"\b(?:part|section)\s+[IVX\d]+[A-D]?\b|\bto\s+the\s+extent\b|\bonly\s+(?:the|one|two)\s+(?:issue|question)",
                   re.I)
REHEAR_SENT = re.compile(r"\b" + BANC + r"\b|\brehear|\breheard\b|\bvacat\w*\s+the\s+panel|\bpanel\s+(?:opinion|decision)", re.I)
ADOPT2 = re.compile(
    r"\badopt\w*\b[^.]{0,100}?\b(?:panel|original|former|prior|division(?:al)?)\b[^.]{0,30}?\b(?:opinion|decision|majority|"
    r"reasoning|analysis|holding|judgment)|\breinstat\w*\b[^.]{0,80}?\b(?:panel|mandate|original\s+(?:opinion|judgment|"
    r"decision)|division)|\b(?:panel|original)\s+(?:majority\s+)?(?:opinion|decision|judgment)\s+(?:is|be|are)\s+(?:hereby\s+)?"
    r"reinstated|\bfor\s+the\s+reasons\s+(?:set\s+(?:forth|out)|stated|given|expressed)\s+in\s+the\s+(?:original\s+|panel\s+|"
    r"prior\s+|former\s+)(?:majority\s+)?opinion|\b(?:affirm|uphold)\w*\s+the\s+(?:judgment\s+of\s+the\s+|decision\s+of\s+"
    r"the\s+)?panel\b|\breaffirm\w*\s+the\s+panel|\badhere\w*\s+to\s+the\s+panel", re.I)
REVPANEL = re.compile(r"\b(?:we|the\s+court(?:\s+en\s+ban[ce])?|the\s+en\s+ban[ce]\s+court)\s+(?:now\s+|therefore\s+|hereby\s+|"
                      r"accordingly\s+)?revers\w*\s+(?:the\s+)?(?:judgment\s+of\s+the\s+|decision\s+of\s+the\s+)?panel\b|"
                      r"\bthe\s+panel(?:['’]s)?\s+(?:opinion|decision|judgment)\s+(?:is|are)\s+(?:hereby\s+)?reversed\b", re.I)
NEGWORD = re.compile(r"\bnot\b|\bnever\b|n['’]t\b|\bwhether\b|\bif\b|\bwould\b", re.I)


def text_body(text):
    body0 = 0
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    return body0


def t_facts(text):
    """Facts of a target text: is it an order about rehearing / rehearing en banc / reargument, an en banc decision?"""
    b0 = text_body(text)
    body = text[b0:]
    blen = len(body)
    hw = C.hard_wrapped(text, b0)
    view = C.unwrap_view(text, b0) if hw else text
    v = L.norm(view[b0:])
    grant = any(rx.search(v) for rx in RR.GRANT)
    denied = bool(DENIED_BANC.search(v)) and bool(RR.BANC_RX.search(v) or re.search(r"rehearing", v, re.I))
    rearg = bool(REARG.search(v))
    order_head = bool(ORDER_HEAD.search(view[b0:b0 + 3000]))
    banc_head = False
    for m in RR.BANC_RX.finditer(v[:1500]):
        ctx = v[max(0, m.start() - 110):m.end() + 30]
        if RR.PET_BANC.search(ctx) and not re.search(r"\b(?:on|upon)\s+rehearing\s+" + BANC + r"|opinions?\s+" + BANC +
                                                    r"|\breheard\s+" + BANC + r"|" + BANC + r"\s+(?:court|opinion)|sitting\s+" + BANC,
                                                    ctx, re.I):
            continue
        banc_head = True
        break
    short = blen < 6000
    order_like = short and (grant or denied or rearg or (order_head and bool(re.search(r"rehear|" + BANC, v, re.I))))
    return {"blen": blen, "grant": int(grant), "denied": int(denied), "rearg": int(rearg), "order_head": int(order_head),
            "banc_head": int(banc_head), "order_like": int(order_like)}


def d_facts(text):
    """Facts of an en banc acting text: limitation, adoption / reinstatement of the panel's decision, reversal of the
    panel, a denial of rehearing en banc."""
    b0 = text_body(text)
    hw = C.hard_wrapped(text, b0)
    view = C.unwrap_view(text, b0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    out = {"limit": [], "adopt": [], "revpanel": [], "denied": 0}
    for m in REHEAR_SENT.finditer(view, b0):
        p, _s = C.part_at(pm, m.start())
        if p not in RR.OK_PARTS:
            continue
        s0, s1 = C.sentence_span(view, m.start(), m.end(), back=500, fwd=500)
        sent = L.norm(view[s0:s1])
        if LIMIT.search(sent):
            out["limit"].append(sent[:300])
        if ADOPT2.search(sent) and not NEGWORD.search(sent):
            out["adopt"].append(sent[:300])
    for m in re.finditer(r"panel", view[b0:]):
        pass
    for m in REVPANEL.finditer(view, b0):
        p, _s = C.part_at(pm, m.start())
        if p not in ("majority", "perCuriam", "plurality", "majority~"):
            continue
        s0, s1 = C.sentence_span(view, m.start(), m.end(), back=500, fwd=500)
        sent = L.norm(view[s0:s1])
        if NEGWORD.search(sent[:m.start() - s0 + 1]) or RR.REQUEST.search(sent):
            continue
        out["revpanel"].append({"q": [s0, s1], "part": RR.CERT_PARTS.get(p, p), "t": sent[:600]})
    v = L.norm(view[b0:])
    if len(v) < 6000 and DENIED_BANC.search(v):
        out["denied"] = 1
    for k in ("limit", "adopt"):
        out[k] = out[k][:4]
    out["revpanel"] = out["revpanel"][:2]
    return out


def stage_feats():
    cands = [json.loads(x) for x in open(os.path.join(WORK, "cands.jsonl"), encoding="utf-8")]
    tnodes, dnodes = set(), set()
    for c in cands:
        tnodes.add(c["j"])
        if c["enbanc"] or c["var"].startswith("c-"):
            dnodes.add(c["n"])
            tnodes.update(c["same_docket"])
        elif c["how"] == "docket":
            tnodes.update(c["same_docket"])
    print("targets", len(tnodes), "acting", len(dnodes), flush=True)
    feats = {"t": {}, "d": {}}
    allnodes = sorted(tnodes | dnodes)
    for i in range(0, len(allnodes), 2000):
        chunk = allnodes[i:i + 2000]
        texts = L.fetch_texts(chunk)
        for n in chunk:
            if n not in texts:
                continue
            text = texts[n][1]
            if n in tnodes:
                feats["t"][str(n)] = t_facts(text)
            if n in dnodes:
                feats["d"][str(n)] = d_facts(text)
        print("  texts", i + len(chunk), flush=True)
    json.dump(feats, open(os.path.join(WORK, "feats.json"), "w", encoding="utf-8"))


# ================================================================================================ stage 3: rows
OBJ_BAD = re.compile(r"\b(?:suspension|stay|mandate|order\s+(?:granting|denying|of\s+dismissal|dismissing|allowing|"
                     r"staying|recalling)|motion|petition|briefing|oral\s+argument|submission|certificate|remittitur)\b",
                     re.I)


def days(d):
    return RL.days(d)


def latest_opinion(c, TF):
    """The latest earlier same-court decision sharing a docket number with D that is not an order about rehearing /
    reargument and not an en banc decision itself (None when there is none)."""
    best, bd = None, 0
    for m in c["same_docket"]:
        f = TF.get(str(m))
        dt = c["sd_info"][str(m)][0]
        if f is None or f["order_like"] or f["banc_head"] or dt >= c["date"]:
            continue
        if dt > bd or (dt == bd and best is not None and m > best):
            best, bd = m, dt
    return best, bd


def to_row(c, rule, kind=None, scope=None, q=None, part=None, claim=None, note=""):
    r = {"rule": rule, "table": "history", "by": c["n"], "target": c["j"], "kind": kind or c["kind"],
         "scope": scope or c["scope"], "main": list(q or c["q"]), "part": part or c["part"], "ev": c["ev"],
         "joined": [], "claim": claim or c["claim"], "doctrine": "-", "field_limit": "-", "text": "by",
         "anchor": None, "anchor_part": "", "note": note}
    q0, q1 = r["main"]
    if c["anchor"] is not None and not (q0 - 400 <= c["anchor"][0] and c["anchor"][1] <= q1 + 400 and c["ev"].startswith("cite:")):
        r["anchor"], r["anchor_part"] = list(c["anchor"]), c["apart"]
    elif c["how"] == "docket":
        r["anchor"], r["anchor_part"] = list(c["anchor"]), c["apart"]
    return r


SA_PRESENT = re.compile(r"\b(?:is|are|be|stands?)\s+(?:hereby\s+|now\s+|accordingly\s+|therefore\s+)*set\s+aside\b|"
                        r"\bbe,?\s+and\s+(?:the\s+same\s+)?(?:it\s+)?(?:hereby\s+)?(?:is|are),?\s+(?:hereby\s+)?set\s+aside\b|"
                        r"\bwe\s+(?:(?:hereby|now|therefore|accordingly|must|do|will)\s+)*set\s+aside\b", re.I)
SA_PAST = re.compile(r"\b(?:previously|earlier|then|thereafter|subsequently|in\s+[A-Z][a-z]+(?:\s+of)?\s+\d{4}|on\s+[A-Z][a-z]+\.?\s+\d)",
                     re.I)
SA_OBJ_BAD = re.compile(r"\b(?:board|commission|agency|department|secretary|administrative|referee|master|arbitrat\w*|"
                        r"verdict|sentence|default|award|finding|tax\s+court|district\s+court|trial\s+court|lower\s+court|"
                        r"assessment|damages|costs|fees|that\s+the)\b",
                        re.I)
_NAMES = {}


def node_tokens(n):
    if n not in _NAMES:
        p = L.node_row(n)
        _NAMES[n] = RL.ascii_tokens(p[6] if len(p) > 6 else "")
    return _NAMES[n]


def setaside_gate(c):
    """Track (d) on a rehear row: R7-S8 a present decretal form ("is set aside", "be, and is, set aside", "we set aside")
    with no past-time marker before it; R7-S9 nothing in the sentence up to "set aside" names another body's order
    (board, agency, district court ...) or a verdict / sentence / default / award; R7-S10 T's caption shares a party
    word with D's (a case cited as the reason, "on the basis of our decision in X", is not the opinion set aside)."""
    q = c["qt"]
    m = SA_PRESENT.search(q)
    if not m:
        return "not_present_form"
    if SA_PAST.search(q[:m.start()]):
        return "past_recital"
    if SA_OBJ_BAD.search(q[:m.end()]):
        return "object_other_thing"
    if not (node_tokens(c["n"]) & node_tokens(c["j"])):
        return "caption_not_shared"
    return ""


def stage_rows():
    cands = [json.loads(x) for x in open(os.path.join(WORK, "cands.jsonl"), encoding="utf-8")]
    feats = json.load(open(os.path.join(WORK, "feats.json"), encoding="utf-8"))
    TF, DF = feats["t"], feats["d"]
    st = collections.Counter()
    drops = []
    out = {"enbanc": [], "docket": [], "setaside": []}

    def drop(c, why):
        st["drop:%s:%s" % (cls_of(c), why)] += 1
        drops.append((cls_of(c), why, c["var"], c["how"], c["n"], c["j"], c["kind"], c["qt"][:200]))

    def cls_of(c):
        if c["var"].startswith("c-"):
            return "enbanc"
        if c["how"] == "docket":
            return "docket"
        return "panelcite"

    for c in cands:
        cls = cls_of(c)
        st["cand:%s:%s-%s" % (cls, c["var"], c["how"])] += 1
        tf = TF.get(str(c["j"]))
        if tf is None:
            drop(c, "no_target_text")
            continue
        if SC_ACTOR.search(c["qt"]):
            drop(c, "supreme_court_or_remand_in_sentence")
            continue
        if c["claim"] == "setAside":
            why = setaside_gate(c)
            if why:
                drop(c, "setaside_" + why)
                continue
        if cls == "panelcite":
            # installed in round 6 (panel-cite); only the setAside rows of this class are new (track d)
            if c["claim"] == "setAside":
                if tf["order_like"]:
                    drop(c, "target_is_order")
                    continue
                out["setaside"].append(to_row(c, "r7setaside:rehear:%s-%s" % (c["var"], c["how"])))
            continue
        if cls == "docket":
            # R7-D1: the act sentence names the earlier opinion's date; T has that date (+-3 days) and is the only
            # same-docket (identical docket set) earlier decision of the court with it
            if not c["dates"]:
                drop(c, "no_date_named")
                continue
            named = [days(x) for x in c["dates"]]
            dd = set(c["d_dockets"])
            hits = [m for m in c["same_docket"] if set(c["sd_info"][str(m)][1]) == dd and c["sd_info"][str(m)][0] < c["date"]
                    and any(abs(days(c["sd_info"][str(m)][0]) - x) <= 3 for x in named)]
            if c["j"] not in hits:
                drop(c, "target_date_not_named")
                continue
            if len(hits) != 1:
                drop(c, "date_not_unique")
                continue
            # R7-D2: the object is this court's opinion / decision / judgment itself (not a stay, suspension, mandate
            # or an order about a motion); T is not itself an order about rehearing / reargument
            if OBJ_BAD.search(c["obj"]) or OBJ_BAD.search(c["qt"][max(0, c["m"][0] - c["q"][0] - 40):c["m"][0] - c["q"][0] + len(c["obj"]) + 40]):
                drop(c, "object_not_opinion")
                continue
            if not (c["noun"].startswith(("opinion", "decision")) or (c["noun"].startswith("judgment") and
                                                                       re.search(r"\bour\b|this\s+court|herein|in\s+this\s+(?:case|appeal)", c["qt"], re.I))):
                drop(c, "noun_not_opinion")
                continue
            if tf["order_like"]:
                drop(c, "target_is_order")
                continue
            # R7-D3: a partial act: vacated -> scope unknown; withdrawn / superseded / reinstated in part -> no row
            if c["partial"] and c["kind"] in ("withdrawn", "substitutedBy", "reinstated"):
                drop(c, "partial_withdrawal")
                continue
            rule = ("r7setaside:rehear:%s-docket" if c["claim"] == "setAside" else "r7rehear:docket:%s-docket") % c["var"]
            out["setaside" if c["claim"] == "setAside" else "docket"].append(to_row(c, rule))
            continue
        # ------------------------------------------------------------------ en banc
        df = DF.get(str(c["n"]))
        if df is None:
            drop(c, "no_acting_text")
            continue
        # R7-E1: T is the panel's opinion: not an order about rehearing en banc / reargument, not an en banc decision
        if tf["order_like"]:
            drop(c, "target_is_order")
            continue
        if tf["banc_head"]:
            drop(c, "target_is_en_banc")
            continue
        # R7-E2: T shares a docket number with D and is the latest earlier opinion of that docket (orders skipped)
        if not (set(c["d_dockets"]) & set(c["sd_info"].get(str(c["j"]), [0, []])[1])):
            drop(c, "no_shared_docket")
            continue
        lo, _ = latest_opinion(c, TF)
        if lo != c["j"]:
            drop(c, "not_latest_opinion")
            continue
        if set(c["sd_info"][str(c["j"])][1]) != set(c["d_dockets"]) and not (RL.EB_THIS.search(c["qt"]) or RL.EB_THIS.search(c["atext"])):
            drop(c, "docket_sets_differ")
            continue
        limit = bool(df["limit"])
        adopt = bool(df["adopt"])
        if c["var"] == "c-reh":
            # R7-E3: a silent en banc opinion (D6-4): the panel decision identified by citation, no limitation, no
            # adoption / reinstatement / affirmance of the panel; "we reverse the panel" -> a reversed row instead
            if not c["how"].startswith("cite"):
                drop(c, "silent_not_cited")
                continue
            if adopt or c["adopt"] or c["reinst"] or c["improv"]:
                drop(c, "silent_adopts_panel")
                continue
            if limit:
                drop(c, "silent_limited")
                continue
            if df["revpanel"]:
                rp = df["revpanel"][0]
                if RL.has_cue("reversed", rp["t"]) and rp["part"] in OKP:
                    out["enbanc"].append(to_row(c, "r7rehear:enbanc:c-revpanel-%s" % c["how"], kind="reversed", scope="all",
                                                q=rp["q"], part=rp["part"], note="en banc reverses the panel"))
                    st["revpanel_rows"] += 1
                else:
                    drop(c, "silent_revpanel_nocue")
                continue
            out["enbanc"].append(to_row(c, "r7rehear:enbanc:c-reh-%s" % c["how"]))
            continue
        if c["var"] == "c-order":
            if df["denied"]:
                drop(c, "order_denies")
                continue
            scope = "unknown" if limit else "all"
            out["enbanc"].append(to_row(c, "r7rehear:enbanc:c-order-%s" % c["how"], scope=scope))
            continue
        # c-vac: the en banc court's own words vacate / withdraw the panel decision
        if c["form"] not in ("p1", "p2", "p1sub", "p2sub", "p3", "p4") and (adopt or c["adopt"] or c["reinst"]):
            drop(c, "recital_but_adopts_panel")
            continue
        partial = bool(c["partial"]) or bool(LIMIT.search(c["qt"]))
        # R7-E5: a negative act whose own sentence also reinstates (part of) the panel decision says the panel
        # decision stands; a partial reinstatement ("Part B", "the remainder", "except") is no row either
        if c["kind"] in NEGK and re.search(r"reinstat", c["qt"], re.I):
            drop(c, "vacates_and_reinstates")
            continue
        if c["kind"] == "reinstated" and (partial or re.search(r"\bremainder\b|\bother\s+than\b|\bpart\s+[A-Z]\b|"
                                                                r"\bother\s+respects\b|\bexcept\b", c["qt"], re.I)):
            drop(c, "partial_reinstatement")
            continue
        # R7-E6: a recital whose actor is another panel ("the second panel vacated the first panel's decision") is
        # not the en banc court's act
        if c["form"] == "p5" and re.search(r"\b(?:second|new|another|later|subsequent|rehearing|original|the|a)\s+panel\s+"
                                           r"(?:then\s+|subsequently\s+|later\s+|thereafter\s+|sua\s+sponte\s+)?"
                                           r"(?:vacated|withdrew|vacating|withdrawing)\b", c["qt"], re.I):
            drop(c, "recital_actor_other_panel")
            continue
        if (partial or limit) and c["kind"] in ("withdrawn", "substitutedBy"):
            drop(c, "partial_withdrawal")
            continue
        scope = "unknown" if (partial or limit or c["kind"] == "modified") else "all"
        rule = ("r7setaside:rehear:c-vac-%s" if c["claim"] == "setAside" else "r7rehear:enbanc:c-vac-%s") % c["how"]
        out["setaside" if c["claim"] == "setAside" else "enbanc"].append(to_row(c, rule, scope=scope))
    for k, rows in out.items():
        seen, fin = set(), []
        for r in rows:
            key = (r["by"], r["target"], r["kind"])
            if key in seen:
                st["dup:" + k] += 1
                continue
            seen.add(key)
            fin.append(r)
        with open(os.path.join(HERE, "rows_%s.jsonl" % ("setaside_rehear" if k == "setaside" else k)), "w", encoding="utf-8",
                  newline=NL) as o:
            for r in fin:
                o.write(json.dumps(r, ensure_ascii=False) + NL)
        st["rows:" + k] = len(fin)
        for r in fin:
            st["rows:%s:%s:%s" % (k, r["rule"], r["kind"])] += 1
    with open(os.path.join(WORK, "dropped.tsv"), "w", encoding="utf-8", newline=NL) as o:
        for d in drops:
            o.write("\t".join(str(x).replace("\t", " ") for x in d) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(HERE, "rows_stats.json"), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["cands", "feats", "rows"])
    ap.add_argument("--procs", type=int, default=22)
    a = ap.parse_args()
    if a.stage == "cands":
        stage_cands(a.procs)
    elif a.stage == "feats":
        stage_feats()
    else:
        stage_rows()


if __name__ == "__main__":
    main()
