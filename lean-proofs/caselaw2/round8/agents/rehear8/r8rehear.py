"""Round 8, move 3 (agent rehear8): rehearing grant orders -> the panel opinion they act on; no-date docket rows.

    python -X utf8 r8rehear.py window                 delay of the installed round-7 grant-order rows (stated window)
    python -X utf8 r8rehear.py orders [--procs 10]    G: grant orders (round-6 claims cache, whole corpus) -> work/orders_cands.jsonl
    python -X utf8 r8rehear.py ofeats                 texts of the orders' same-docket decisions -> work/ofeats.json
    python -X utf8 r8rehear.py grows                  -> rows_grant.jsonl, work/grant_drops.tsv, work/grant_stats.json
    python -X utf8 r8rehear.py nrows                  N: round-7 docket candidates with no date / another date
                                                         -> rows_nodate.jsonl, rows_redate.jsonl, work/nodate_drops.tsv

Rules (RULES8.md, next to this file); never rows: nothing names a case, citation, party or docket. No answer key read.
Inputs: round-6 rehear claims cache (`round6/history/rules/rehear/work/claims.*`), round-7 b4rehear candidates
(`work/cands.jsonl`, `work/feats.json`), the base history table `round7/stage/v3/history.tsv` (dedupe only).
"""
import sys

sys.dont_write_bytecode = True
import argparse, collections, json, os, re  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
R6H = os.path.join(C2, "round6", "history")
REH = os.path.join(R6H, "rules", "rehear")
B4 = os.path.join(C2, "round7", "agents", "b4rehear")
sys.path.insert(0, R6H)
sys.path.insert(0, REH)
sys.path.insert(0, B4)
import r6lib as L  # noqa: E402
import rehear_link as RL  # noqa: E402
import rehear_rules as RR  # noqa: E402
import r7rehear as R7  # noqa: E402

C = L.reader_common()
WORK = os.path.join(HERE, "work")
NL = chr(10)
NEGK = RL.NEGK
OKP = ("majority", "perCuriam", "plurality")
BASE_HIST = os.path.join(C2, "round7", "stage", "v3", "history.tsv")
# G-2: window between the order and the panel opinion it acts on (set from `window`: the 99th percentile of the
# delay of the 405 installed round-7 c-order-docket rows, rounded up; see NOTES.md)
G_WINDOW = 548


def days(d):
    return RL.days(d)


def base_by():
    by = collections.defaultdict(list)
    for line in open(BASE_HIST, encoding="utf-8"):
        f = line.rstrip(NL).split("\t")
        by[int(f[2])].append((int(f[1]), f[4], f[12]))
    return by


# ======================================================================================================== window
def stage_window():
    F = L.Facts()
    ds = []
    for line in open(BASE_HIST, encoding="utf-8"):
        f = line.rstrip(NL).split("\t")
        if f[12].startswith("r7:r7rehear:enbanc:c-order"):
            ds.append(days(int(F.date[int(f[2])])) - days(int(F.date[int(f[1])])))
    ds.sort()
    q = lambda p: ds[min(len(ds) - 1, int(p * len(ds)))]
    print("c-order rows", len(ds), "median", q(0.5), "p90", q(0.9), "p95", q(0.95), "p99", q(0.99), "max", ds[-1])


# ======================================================================================================== G: orders
DENY_EB = re.compile(r"\b(?:re)?hearing\s+" + RR.BANC + r"[^.;]{0,60}?\b(?:is|are|be|was|were|has\s+been)\s+(?:(?:hereby|also|"
                     r"accordingly|therefore)\s+)*(?:denied|rejected|refused)\b|\b(?:petition|suggestion|request|motion)s?\s+for\s+(?:re)?hearing\s+"
                     r"(?:and\s+(?:for\s+)?(?:re)?hearing\s+)?" + RR.BANC + r"[^.;]{0,80}?\b(?:is|are|be|was|were|has\s+been)\s+"
                     r"(?:(?:hereby|also|accordingly|therefore)\s+)*(?:denied|rejected|refused)\b|\bden(?:y|ies|ied)\s+(?:the\s+)?(?:petition|suggestion)s?\s+"
                     r"for\s+(?:re)?hearing\s+" + RR.BANC, re.I)
# the object of an order's act is the panel's (or this court's) opinion / decision / judgment
PANEL_OBJ = re.compile(r"\bpanel\b|\bthe\s+opinions?\s+(?:filed|issued|entered|of|dated|announced|in\s+this|herein)|"
                       r"\bour\b|\b(?:this|the)\s+court['’]s\b|\bthis\s+court\b|\b(?:prior|previous|former|original|earlier)\s+(?:opinion|decision|"
                       r"judgment)|^(?:the|that)\s+opinions?\b", re.I)


def stage_orders(procs):
    """G-1 the population: every record of the round-6 claims cache (whole corpus) that is a short text granting
    rehearing en banc (a grant sentence that is not inside a motion "that ... be reheard"), or granting rehearing and
    stating a present act on an opinion of this court; plus the facts needed to link it."""
    os.makedirs(WORK, exist_ok=True)
    recs = RL.load_claims()
    print("records", len(recs), flush=True)
    t0 = set()
    for line in open(os.path.join(B4, "work", "dropped.tsv"), encoding="utf-8"):
        f = line.rstrip(NL).split("\t")
        if f[0] == "enbanc" and f[1] == "target_is_order":
            t0.add(int(f[5]))
    pop = []
    st = collections.Counter()
    for r in recs:
        if not r["short"]:
            continue
        gs = [g for g in r["grants"] if not RL.MOTION_THAT.search(g["t"]) and g["part"] in OKP]
        acts = [c for c in r["claims"] if c["kind"] in ("vacated", "withdrawn") and c["part"] in OKP and
                c["form"] in ("p1", "p2", "p3", "p4") and PANEL_OBJ.search(c["obj"]) and c["noun"].startswith(("opinion", "decision", "judgment"))]
        rehg = bool(r["notes"]["rehgrant"]) or bool(r["onreh"])
        if not (gs or (acts and rehg)):
            continue
        st["pop"] += 1
        st["pop:t0"] += int(r["n"] in t0)
        pop.append((r, gs, acts))
    print(dict(st), flush=True)
    want = set()
    for r, _g, _a in pop:
        for d in RL.dockets(r["docket"]):
            want.add((r["court"], d))
    idx, info = RL.docket_index(want, procs=procs)
    print("docket index", len(idx), len(info), flush=True)
    with open(os.path.join(WORK, "orders_cands.jsonl"), "w", encoding="utf-8", newline=NL) as o:
        for r, gs, acts in pop:
            ds = RL.dockets(r["docket"])
            sd = {}
            for dk in ds:
                for m in idx.get((r["court"], dk), ()):
                    if m != r["n"] and info[m][0] and info[m][0] <= r["date"]:
                        sd[m] = [info[m][0], sorted(RL.dockets(info[m][2])), info[m][3]]
            cws = [w for w in r["cws"] if w["rel"] == "same"]
            d = {"n": r["n"], "court": r["court"], "date": r["date"], "docket": r["docket"], "title": r["title"],
                 "parties": r["parties"], "d_dockets": sorted(ds), "cap": r["cap"], "enbanc": r["enbanc"], "onreh": r["onreh"],
                 "rehgrant": r["notes"]["rehgrant"], "grants": gs, "acts": acts, "t0": int(r["n"] in t0),
                 "cws": [{"j": w["j"], "key": w["key"], "c": w["c"], "part": w["part"], "fl": w["fl"]} for w in cws],
                 "sd": {str(k): v for k, v in sd.items()}}
            o.write(json.dumps(d, ensure_ascii=False) + NL)


def stage_ofeats():
    cands = [json.loads(x) for x in open(os.path.join(WORK, "orders_cands.jsonl"), encoding="utf-8")]
    nodes = set()
    for c in cands:
        nodes.add(c["n"])
        nodes.update(int(k) for k in c["sd"])
    nodes = sorted(nodes)
    print("texts", len(nodes), flush=True)
    feats = {}
    for i in range(0, len(nodes), 2000):
        chunk = nodes[i:i + 2000]
        texts = L.fetch_texts(chunk)
        for n in chunk:
            if n in texts:
                text = texts[n][1]
                f = R7.t_facts(text)
                b0 = R7.text_body(text)
                v = L.norm(text[b0:])
                f["deny_eb"] = int(bool(DENY_EB.search(v)))
                f["limit"] = int(bool(R7.LIMIT.search(v))) if f["blen"] < 6000 else 0
                feats[str(n)] = f
        print("  texts", i + len(chunk), flush=True)
    json.dump(feats, open(os.path.join(WORK, "ofeats.json"), "w", encoding="utf-8"))


def caption_tokens(c, title, where):
    """Party-name tokens shared by the order's title / parties and T's title that stand in `where` (the order's
    caption, or the 400 characters around its act sentence) (at least two, or all of T's when it has fewer: the
    round-6 docket-link test)."""
    dt = RL.ascii_tokens(c["title"]) | set(t for p in c["parties"].split(" | ")[:2] for t in RL.ascii_tokens(p))
    tt = RL.ascii_tokens(title)
    capw = RL.words(where) if where else ""
    sh = {x for x in tt & dt if " " + x.lower() + " " in capw}
    if sh and len(sh) >= min(2, len(tt)):
        return sorted(sh)
    return None


OTEXT = {}
# G-4b a poll that failed ("all the other active judges voted against it", "failed to receive a majority")
VOTE_FAIL = re.compile(r"\bvoted\s+against\b|\bfail(?:ed|s)?\s+to\s+(?:receive|obtain|command|garner|win|produce|attract|"
                       r"carry|get)\b|\b(?:poll|vote|suggestion|petition|motion)\b[^.]{0,80}?\bfail(?:s|ed)\b|\bdid\s+not\s+"
                       r"(?:receive|obtain|command|vote)\b|\bnot\s+(?:having\s+)?(?:received|voted|obtained)\b|\binsufficient\s+"
                       r"(?:number|votes)\b|\bless\s+than\s+a\s+majority\b|\bno\s+(?:active\s+)?judge\b[^.]{0,60}?\b(?:requested|"
                       r"called|voted)\b", re.I)
MAJ_FOR = re.compile(r"\bmajority\s+of\s+[^.]{0,80}?\b(?:voted|having\s+voted)\s+(?:to|in\s+favor|for)\b|\bmajority\s+"
                     r"(?:of\s+[^.]{0,60}?)?having\s+voted\s+(?:to|in\s+favor|for)\b", re.I)


def adopts_in_court_part(text):
    """A sentence of the court's own part (majority / per curiam / plurality) adopting, adhering to or reinstating
    the panel / original decision (round-6 ADOPT, ADHERE; round-7 ADOPT2), not negated."""
    if not text:
        return False
    b0 = R7.text_body(text)
    hw = C.hard_wrapped(text, b0)
    view = C.unwrap_view(text, b0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    for rx in (RR.ADOPT, RR.ADHERE, R7.ADOPT2):
        for m in rx.finditer(view, b0):
            p, _s = C.part_at(pm, m.start())
            if p not in RR.OK_PARTS:
                continue
            s0, s1 = C.sentence_span(view, m.start(), m.end(), back=300, fwd=300)
            if R7.NEGWORD.search(L.norm(view[s0:m.end()])):
                continue
            return True
    return False


# G-3b the grant words belong to a motion about the petition ("motion to withdraw the petition ... is GRANTED")
MOTION_TO = re.compile(r"\b(?:motion|request|application|stipulation)s?\b[^.;]{0,60}?\bto\s+(?:withdraw|dismiss|strike|"
                       r"extend|file|stay|exceed|supplement|amend|enlarge|consolidate)\b", re.I)
# G-3c the grant sentence is about another case ("voted to rehear the Lee case en banc", "X v. Y")
# G-3d a vote of named judges ("Judges X and Y voted to rehear the case en banc") reports a minority, not the grant
MINORITY = re.compile(r"^\W*(?:Chief\s+|Senior\s+|Circuit\s+)?Judges?\s+[A-Z][^.]{0,240}?\b(?:have\s+|has\s+|would\s+have\s+)?"
                      r"(?:voted|vote)\b")
OTHER_CASE = re.compile(r"\bthe\s+[A-Z][\w.'’-]+\s+(?:case|appeal|matter|decision)\b|\bv\.\s|\bIn\s+re\b|\bin\s+No\.")


def stage_grows():
    """G-2 .. G-6 (RULES8.md): link each order to the panel opinion it acts on; one row per order."""
    cands = [json.loads(x) for x in open(os.path.join(WORK, "orders_cands.jsonl"), encoding="utf-8")]
    TF = json.load(open(os.path.join(WORK, "ofeats.json"), encoding="utf-8"))
    base = base_by()
    st = collections.Counter()
    rows, drops = [], []
    OTEXT.update({n: v[1] for n, v in L.fetch_texts([c["n"] for c in cands]).items()})

    def drop(c, why, extra=""):
        st["drop:" + why] += 1
        st["drop:%s:t0" % why] += c["t0"]
        drops.append((why, c["n"], c["t0"], extra))

    for c in cands:
        of = TF.get(str(c["n"]))
        if of is None:
            drop(c, "no_order_text")
            continue
        # G-1b the acting text is itself a short order about rehearing (not an opinion that recites a grant)
        if not (of["order_like"] or (c["acts"] and c["rehgrant"] and of["blen"] < 6000)):
            drop(c, "acting_not_order")
            continue
        # G-3 the act sentence: an explicit present act of the order on the panel / this court's opinion, else the
        # grant of rehearing en banc; a panel-rehearing grant with no act words changes no status: no row
        act = None
        for a in c["acts"]:
            if R7.SC_ACTOR.search(a["t"]) or not RL.has_cue(a["kind"], a["t"]):
                continue
            if R7.OBJ_BAD.search(a["obj"]) or RECITE.search(a["t"]) or re.search(r"reinstat", a["t"], re.I):
                continue
            # N-7 / N-8 as for docket rows: another court's decree inside the act span; a part of the opinion
            mspan = a["t"][max(0, a["m"][0] - a["q"][0]):a["m"][1] - a["q"][0]]
            if any(not ACTED_ON.search(mspan[max(0, m.start() - 40):m.start()]) for m in OTHER_COURT.finditer(mspan)) or \
                    re.search(r"\bdecree\b|\bdistrict\s+court['’]s\b", mspan, re.I):
                continue
            oi = a["t"].find(a["obj"][:30]) if a["obj"] else -1
            if oi >= 0 and PART_OF.search(a["t"][max(0, oi - 90):oi]):
                a = dict(a, partial=1)
            act = a
            break
        gs = [x for x in c["grants"] if not MOTION_TO.search(x["t"]) and not OTHER_CASE.search(x["t"]) and
              not MINORITY.search(x["t"])]
        g = gs[0] if gs else None
        if act is None and g is None:
            drop(c, "panel_grant_no_act" if not c["grants"] else "grant_motion_or_other_case")
            continue
        if act is None and not RL.has_cue("rehearingEnBancGranted", g["t"]):
            drop(c, "grant_nocue")
            continue
        # G-4 the vote failed / the order denies rehearing en banc
        text = OTEXT.get(c["n"], "")
        body = L.norm(text[R7.text_body(text):]) if text else ""
        if of["deny_eb"] or DENY_EB.search(body) or (VOTE_FAIL.search(body) and not MAJ_FOR.search(body)):
            drop(c, "order_denies_en_banc")
            continue
        # G-7 the order (or a short en banc decision) adopts / adheres to / reinstates the panel decision, in the
        # court's own part (not a dissent or concurrence): no row
        if adopts_in_court_part(text):
            drop(c, "adopts_panel")
            continue
        q = act if act is not None else g
        named = [days(x) for x in (q.get("dates") or RR.dates_in(q["t"]))]
        # G-2 candidates: same court, identical docket-number set, strictly earlier, within the window, not an order
        # about rehearing / reargument, not an en banc decision
        dd = set(c["d_dockets"])
        if not dd:
            drop(c, "no_docket")
            continue
        opins = []
        for k, (dt, dks, title) in c["sd"].items():
            m = int(k)
            f = TF.get(k)
            if f is None or dt >= c["date"] or days(c["date"]) - days(dt) > G_WINDOW:
                continue
            if f["order_like"] or f["banc_head"]:
                continue
            # G-2b a short text under an ORDER heading (an order of the court, e.g. an en banc remand order whose
            # bench is listed by name) is not the panel opinion
            if f["order_head"] and f["blen"] < 3000:
                continue
            opins.append((dt, m, set(dks), title))
        same = [x for x in opins if x[2] == dd]
        if not same:
            drop(c, "no_earlier_opinion" if not opins else "docket_sets_differ")
            continue
        # G-5 which opinion: the one whose date the act / grant sentence names (+-3 days), else the latest; an
        # opinion of the docket with a different docket set later than it, or a tie at its date: no row
        if named:
            hit = [x for x in same if any(abs(days(x[0]) - y) <= 3 for y in named)]
            if len(hit) != 1:
                drop(c, "named_date_not_unique" if hit else "named_date_no_opinion")
                continue
            t = hit[0]
            how = "date"
        else:
            bd = max(x[0] for x in same)
            top = [x for x in same if x[0] == bd]
            if len(top) != 1:
                drop(c, "tie_latest")
                continue
            t = top[0]
            how = "latest"
            if any(x[0] > t[0] for x in opins):
                drop(c, "later_opinion_other_docket_set")
                continue
        # G-5b a same-court citation in the order names another decision: no row
        cited = {w["j"] for w in c["cws"] if w["part"] != "headmatter" or "H" in w["fl"]}
        if cited and t[1] not in cited and any(int(F_DATE(j)) < c["date"] for j in cited):
            drop(c, "cites_other_decision")
            continue
        # G-6 name evidence: anchored in the order's caption; else (an order with no caption line, or a caption
        # without an anchor cue) unanchored, the names standing within 400 characters of the act sentence
        cap = c["cap"]
        toks = caption_tokens(c, t[3], cap["t"] if cap else "")
        anchor = None
        if toks and RL.anchor_ok(cap["t"], "name:" + " ".join(toks)):
            anchor = list(cap["s"])
        else:
            text = OTEXT.get(c["n"])
            win = L.norm(text[max(0, q["q"][0] - 400):q["q"][1] + 400]) if text else ""
            toks = caption_tokens(c, t[3], win)
            if not toks:
                drop(c, "caption_not_shared")
                continue
        ev = "name:" + " ".join(toks)
        # base: a row of this order already installed
        b = base.get(c["n"], [])
        if any(x[0] == t[1] for x in b):
            drop(c, "already_in_base")
            continue
        if b:
            drop(c, "base_row_other_target", ";".join("%d:%s" % (x[0], x[1]) for x in b))
            continue
        if act is not None:
            kind = act["kind"]
            partial = bool(act["partial"]) or bool(RL.PARTIAL2.search(act["t"]))
            if partial and kind == "withdrawn":
                drop(c, "partial_withdrawal")
                continue
            scope = "unknown" if (partial or of["limit"]) else "all"
            var = "act"
        else:
            kind = "rehearingEnBancGranted"
            scope = "unknown" if of["limit"] else "all"
            var = "grant"
        rule = "r8rehear:order:%s-%s" % (var, how)
        rows.append({"rule": rule, "table": "history", "by": c["n"], "target": t[1], "kind": kind, "scope": scope,
                     "main": list(q["q"]), "part": q["part"], "ev": ev, "joined": [], "claim": "-", "doctrine": "-",
                     "field_limit": "-", "text": "by", "anchor": anchor, "anchor_part": "headmatter" if anchor else "",
                     "note": "t0" if c["t0"] else ""})
        st["rows:" + rule + ":" + kind] += 1
        st["rows:t0"] += c["t0"]
    st["rows"] = len(rows)
    with open(os.path.join(HERE, "rows_grant.jsonl"), "w", encoding="utf-8", newline=NL) as o:
        for r in rows:
            o.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, "grant_drops.tsv"), "w", encoding="utf-8", newline=NL) as o:
        for d in drops:
            o.write("\t".join(str(x) for x in d) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "grant_stats.json"), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


_F = [None]


def F_DATE(j):
    if _F[0] is None:
        _F[0] = L.Facts()
    return _F[0].date[int(j)]


# ======================================================================================================== N: no date
# N-4 the act sentence recites what an earlier opinion did, or another body's act
RECITE = re.compile(r"\breiterat\w*|\breaffirm\w*|\bin\s+(?:our|the)\s+(?:initial|prior|previous|original|earlier|first)\s+"
                    r"(?:opinion|decision)\b[^.]{0,40}?\bthat\b|\bas\s+we\s+(?:held|stated|said)\b|"
                    r"\bsupreme\s+court\b[^.;]{0,80}?\bhaving\s+(?:reversed|vacated|remanded|granted)", re.I)
# N-7 the act's own span (object .. verb) names another court's judgment ("the judgment of this court ... and the
# judgment of the district court is vacated")
OTHER_COURT = re.compile(r"\b(?:district|trial|tax|bankruptcy|lower|circuit|superior|county|juvenile|probate|family|municipal|"
                         r"claims|chancery)\s+court\b|\bcourt\s+below\b", re.I)
# ... unless that court is what our judgment acted on ("our judgment reversing the district court ... is vacated")
ACTED_ON = re.compile(r"\b(?:affirm|revers|dismiss|remand|vacat|deny|deni|modif|enforc)\w*\b", re.I)
# N-8 the object is a part of the opinion ("any expression in our former opinion", "the language of our opinion")
PART_OF = re.compile(r"\b(?:expressions?|language|statements?|discussion|passages?|footnotes?|paragraphs?|sentences?|dict(?:um|a)|"
                     r"portions?|parts?|words?|references?|observations?|remarks?)\s+(?:[\w’']+\s+){0,6}?(?:in|of|from)\s+$", re.I)
REINST_PART = re.compile(r"\bremainder\b|\bother\s+than\b|\bpart\s+[A-Z]\b|\bother\s+respects\b|\bexcept\b|\bresentenc\w*|"
                         r"\bsentenc\w*\b[^.]{0,40}?\b(?:vacat|remand)|\bportion|\bin\s+part\b|\binsofar\b|\bto\s+the\s+extent\b", re.I)
JUDG_SELF = re.compile(r"\bour\b|\bthis\s+court|\bherein\b|\bin\s+this\s+(?:case|appeal|cause)|\b(?:prior|previous|former|original|"
                       r"earlier)\b", re.I)


def stage_nrows():
    cands = [json.loads(x) for x in open(os.path.join(B4, "work", "cands.jsonl"), encoding="utf-8")]
    TF = json.load(open(os.path.join(B4, "work", "feats.json"), encoding="utf-8"))["t"]
    base = base_by()
    st = collections.Counter()
    out = {"nodate": [], "redate": []}
    drops = []

    def drop(c, why, sub):
        st["drop:%s:%s" % (sub, why)] += 1
        drops.append((sub, why, c["var"], c["n"], c["j"], c["kind"], c["qt"][:240]))

    for c in cands:
        if c["var"].startswith("c-") or c["how"] != "docket":
            continue
        if c["claim"] != "-":
            continue  # set-aside rows: round-7 track (d), not redone here
        if R7.SC_ACTOR.search(c["qt"]):
            continue
        named = [days(x) for x in c["dates"]]
        dd = set(c["d_dockets"])
        if named:
            hits = [m for m in c["same_docket"] if set(c["sd_info"][str(m)][1]) == dd and c["sd_info"][str(m)][0] < c["date"]
                    and any(abs(days(c["sd_info"][str(m)][0]) - x) <= 3 for x in named)]
            if c["j"] in hits:
                continue  # round-7 R7-D1 (installed or dropped by round 7)
            sub = "redate"
        else:
            sub = "nodate"
        st["cand:" + sub] += 1
        tf = TF.get(str(c["j"]))
        if tf is None:
            drop(c, "no_target_text", sub)
            continue
        if sub == "redate":
            # N-5 the sentence names a date that is not T's: re-point to the unique same-docket earlier opinion with
            # that date (not an order), with name evidence in D's caption; else no row
            ok = [m for m in hits if TF.get(str(m)) and not TF[str(m)]["order_like"] and not TF[str(m)]["banc_head"]]
            if len(ok) != 1:
                drop(c, "named_date_no_unique_opinion", sub)
                continue
            j = ok[0]
            p = L.node_row(j)
            tit = p[6] if len(p) > 6 else ""
            dtoks = RL.ascii_tokens(L.node_row(c["n"])[6]) | R7.node_tokens(c["n"])
            sh = sorted(RL.ascii_tokens(tit) & dtoks)
            ev = "name:" + " ".join(sh)
            if not sh or not RL.anchor_ok(c["atext"], ev):
                drop(c, "redate_name_not_in_caption", sub)
                continue
            c = dict(c, j=j, ev=ev)
            tf = TF[str(j)]
        else:
            # N-1 T is the latest earlier same-court decision of D's docket (any shared docket number) that is not an
            # order about rehearing / reargument and not an en banc decision; no tie at its date; identical docket
            # sets; no other opinion of the docket between T and D
            lo, _ = R7.latest_opinion(c, TF)
            if lo != c["j"]:
                drop(c, "not_latest_opinion", sub)
                continue
            jd = c["sd_info"][str(c["j"])][0]
            ties = [m for m in c["same_docket"] if m != c["j"] and c["sd_info"][str(m)][0] == jd and TF.get(str(m)) and
                    not TF[str(m)]["order_like"] and not TF[str(m)]["banc_head"]]
            if ties:
                drop(c, "tie_latest", sub)
                continue
            if set(c["sd_info"][str(c["j"])][1]) != dd:
                drop(c, "docket_sets_differ", sub)
                continue
        # N-2 (= R7-D2) the object is this court's opinion / decision / judgment, not a stay, mandate, motion ...
        if R7.OBJ_BAD.search(c["obj"]) or R7.OBJ_BAD.search(c["qt"][max(0, c["m"][0] - c["q"][0] - 40):c["m"][0] - c["q"][0] + len(c["obj"]) + 40]):
            drop(c, "object_not_opinion", sub)
            continue
        if c["noun"].startswith("judgment"):
            # N-3 a judgment is this court's only when its own noun phrase says so ("our judgment", "the prior judgment
            # of this court"), not when "our" stands elsewhere in the sentence
            if not (c.get("self") or JUDG_SELF.search(c["obj"]) or
                    re.search(re.escape(c["obj"][:40]) + r"\s*(?:of|by|in)\s+this\s+(?:court|case|appeal)", c["qt"], re.I)):
                drop(c, "judgment_not_this_courts", sub)
                continue
        elif not c["noun"].startswith(("opinion", "decision")):
            drop(c, "noun_not_opinion", sub)
            continue
        if tf["order_like"]:
            drop(c, "target_is_order", sub)
            continue
        # N-4 a recital of an earlier opinion's ruling is not an act on it
        if RECITE.search(c["qt"]):
            drop(c, "recital_of_earlier_ruling", sub)
            continue
        mspan = c["qt"][max(0, c["m"][0] - c["q"][0]):c["m"][1] - c["q"][0]]
        if any(not ACTED_ON.search(mspan[max(0, m.start() - 40):m.start()]) for m in OTHER_COURT.finditer(mspan)):
            drop(c, "act_span_other_court", sub)
            continue
        oi = c["qt"].find(c["obj"][:30]) if c["obj"] else -1
        if oi >= 0 and PART_OF.search(c["qt"][max(0, oi - 90):oi]):
            if c["kind"] in ("withdrawn", "substitutedBy", "reinstated"):
                drop(c, "part_of_opinion", sub)
                continue
            c = dict(c, scope="unknown")
        # R7-D3 partial acts; N-6 a reinstatement with a part excepted or a sentence remanded is partial: no row
        if c["partial"] and c["kind"] in ("withdrawn", "substitutedBy", "reinstated"):
            drop(c, "partial_withdrawal", sub)
            continue
        if c["kind"] == "reinstated" and REINST_PART.search(c["qt"]):
            drop(c, "partial_reinstatement", sub)
            continue
        if any(x[0] == c["j"] for x in base.get(c["n"], [])):
            drop(c, "already_in_base", sub)
            continue
        rule = "r8rehear:docket:%s-%s" % (c["var"], sub)
        out[sub].append(R7.to_row(c, rule))
    for k, rows in out.items():
        seen, fin = set(), []
        for r in rows:
            key = (r["by"], r["target"], r["kind"])
            if key in seen:
                st["dup:" + k] += 1
                continue
            seen.add(key)
            fin.append(r)
        with open(os.path.join(HERE, "rows_%s.jsonl" % k), "w", encoding="utf-8", newline=NL) as o:
            for r in fin:
                o.write(json.dumps(r, ensure_ascii=False) + NL)
        st["rows:" + k] = len(fin)
        for r in fin:
            st["rows:%s:%s:%s" % (k, r["rule"], r["kind"])] += 1
    with open(os.path.join(WORK, "nodate_drops.tsv"), "w", encoding="utf-8", newline=NL) as o:
        for d in drops:
            o.write("\t".join(str(x).replace("\t", " ") for x in d) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(WORK, "nodate_stats.json"), "w"), indent=1)
    for k, v in sorted(st.items()):
        print(k, v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["window", "orders", "ofeats", "grows", "nrows"])
    ap.add_argument("--procs", type=int, default=10)
    a = ap.parse_args()
    {"window": stage_window, "orders": lambda: stage_orders(a.procs), "ofeats": stage_ofeats, "grows": stage_grows,
     "nrows": stage_nrows}[a.stage]()


if __name__ == "__main__":
    main()
