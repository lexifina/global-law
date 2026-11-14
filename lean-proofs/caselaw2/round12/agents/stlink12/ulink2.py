"""stlink11 rule U2: the uncited intermediate decision under review, tied by full party names + a second independent
identity tie + date + court (round-10 rule U's anchor / judgment-line machinery, ulink.finish).

    python -X utf8 ulink2.py run [--procs 8] [--tag u2a]   -> work/ulink2/<shard>.rows.jsonl, rows_<tag>.jsonl

Acting decision D: a state court-of-last-resort opinion (tier L) with no v10d review-kind row on an intermediate
decision of its state, citing (in the citation graph) no decision of its state's intermediate courts that shares a
party name with its caption; its own judgment line (round 6 decide over the intermediate court's phrases) reverses /
vacates / modifies (ulink.finish). Candidates: the state's intermediate-court decisions dated 0..5 years before D
whose graph caption is D's caption (cap 2; pop.py caption pass).
Identity (all required):
 (c) full party names: every named side of T's printed caption (T's own front matter `parties`) is matched in D's
     printed caption (D's own front matter): people by given name + surname, organisations by the whole name;
     frequent litigants (State, Commonwealth, People, United States, cities, counties, agencies, insurers, banks,
     unions, railroads / utilities) match only their own side and never count as the tie: at least one other party
     must match in full.
 (b) T is the latest such full-name decision before D; another full-name candidate on T's date = sibling -> no row.
 (d) a second independent tie (TIES env, default "docket,cite,date"): T's docket number printed in D (compact token
     >= 4 chars with a digit, D's own docket excluded; `docket` = strong: docket context / letters / >= 6 chars),
     T's reporter citation printed in D (front `cites_cases` or body), or T's decision date printed in D's opinion.
 (a) court: D's anchor sentence names T's court acting (ulink.finish); when D names a district / division / department
     of the intermediate court, T's own text must name the same one.
Evidence `name:<tokens>` (the surname / organisation tokens shared by the captions, as rule U).
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stlink as S  # noqa: E402
import ulink as U  # noqa: E402
import ties  # noqa: E402
import ties3  # noqa: E402
from stlink import BO, L  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "ulink2" + ("c" if os.environ.get("U2_CITED") == "1" else "") +
                    ("t" if os.environ.get("U2_TIE3") == "1" else "") + ("w" if os.environ.get("U2_WIDE") == "1" else ""))
TIES = set((os.environ.get("U2_TIES") or "docket,cite,date").split(","))
FULLTOK = os.environ.get("U2_FULLTOK") == "1"
BODY = os.environ.get("U2_BODY") == "1"   # u2d: a surname-only caption party completed from both texts
CITED = os.environ.get("U2_CITED") == "1"   # u2e: the decision under review is cited (graph) but unmarked
TIE3 = os.environ.get("U2_TIE3") == "1"   # u2t (stlink12): a third tie for full-names-only pairs
TIE3_FORMS = [f for f in (os.environ.get("U2_TIE3_FORMS") or "fdate,judge,author,tdocket,county").split(",") if f]
if os.environ.get("U2_BACK"):
    U.BACK = int(os.environ["U2_BACK"])
ORD = {"first": 1, "1st": 1, "one": 1, "i": 1, "second": 2, "2nd": 2, "2d": 2, "two": 2, "ii": 2, "third": 3,
       "3rd": 3, "3d": 3, "three": 3, "iii": 3, "fourth": 4, "4th": 4, "four": 4, "iv": 4, "fifth": 5, "5th": 5,
       "five": 5, "v": 5, "sixth": 6, "6th": 6, "six": 6, "vi": 6, "seventh": 7, "7th": 7, "seven": 7, "vii": 7,
       "eighth": 8, "8th": 8, "eight": 8, "viii": 8, "ninth": 9, "9th": 9, "nine": 9, "ix": 9, "tenth": 10,
       "10th": 10, "ten": 10, "eleventh": 11, "11th": 11, "twelfth": 12, "12th": 12}
ORDW = r"(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth|1st|2nd|2d|3rd|3d|" \
       r"4th|5th|6th|7th|8th|9th|10th|11th|12th|one|two|three|four|five|six|seven|eight|nine|ten|i|ii|iii|iv|v|vi|" \
       r"vii|viii|ix)"
INTER = r"(?:court\s+of\s+appeals?|appellate\s+(?:court|division)|district\s+court\s+of\s+appeal|superior\s+court|" \
        r"court\s+of\s+(?:civil|criminal|special)\s+appeals|commonwealth\s+court)"
DIV_RX = [
    re.compile(INTER + r"[,\s]+(?:for\s+the\s+)?" + ORDW + r"\s+(?:appellate\s+)?(district|division|department|circuit)\b", re.I),
    re.compile(INTER + r"[,\s]+(?:for\s+the\s+)?(district|division|department|circuit)\s+(?:no\.?\s*)?" + ORDW + r"\b", re.I),
    re.compile(r"\b" + ORDW + r"\s+(?:appellate\s+)?(district|division|department|circuit)[,\s]+(?:of\s+the\s+)?" + INTER, re.I),
    re.compile(INTER + r"[,\s]+" + ORDW + r"\s+(?:appellate\s+)?(district|division|department|circuit)\b", re.I),
]


def divisions(text):
    """{(unit word, ordinal)} named with an intermediate-court name."""
    out = set()
    for rx in DIV_RX:
        for m in rx.finditer(text):
            g = [x for x in m.groups() if x]
            unit = next((x.lower() for x in g if x.lower() in ("district", "division", "department", "circuit")), None)
            o = next((ORD.get(x.lower()) for x in g if x.lower() in ORD), None)
            if unit and o:
                out.add((unit, o))
    return out


WIDE = os.environ.get("U2_WIDE") == "1"
FWD = 1500
BACKW = 6000


def finish_wide(n, g, T, cand, st):
    """u2w: ulink.finish with a wider anchor. Any majority / per curiam sentence naming T's court (its anchor-cue
    phrases or "court below"; no act verb required), extended back to the start of the nearest earlier sentence of
    the same part that holds the name token(s), or forward (<= 1,500 characters, same part) to the end of the next
    sentence that holds them; the shortest such span. No intermediate-court citation inside; round 6's anchor guards
    on the whole span. Disposition / scope / own-disposition / dated-otherwise exactly as ulink.finish."""
    from stlink import C, FL
    j, phrases, cls, toks, gap = cand
    z = g["z"]
    if not z:
        return None
    want = (phrases & FL.CUE_PHRASES) | {"court below"}
    low = [t.lower() for t in toks]
    best = None
    for a, b, p in z["parts"]:
        apart = BO.OKPART.get(p)
        if apart is None:
            continue
        seg_words = None
        for m in BO.COURT_RX.finditer(T, a, b):
            if BO.norm_ws(m.group(1)) not in want:
                continue
            s0, s1 = C.sentence_span(T, m.start(), m.end())
            s0, s1 = max(s0, a), min(s1, b)
            spans = []
            # back: nearest earlier position where every token occurs in [x, s1)
            xs = [w.start() for w in re.finditer(r"\b(?:" + "|".join(re.escape(t) for t in low) + r")\b", T[a:s1], re.I)]
            if xs and all(re.search(r"\b" + re.escape(t) + r"\b", T[a:s1], re.I) for t in low):
                x = s0
                while not all(re.search(r"\b" + re.escape(t) + r"\b", T[x:s1], re.I) for t in low):
                    k = x - 1
                    while k > a and T[k] == " ":
                        k -= 1
                    nx = max(a, s0 - BACKW, C.sentence_span(T, k, k + 1)[0])
                    if nx >= x:
                        x = None
                        break
                    x = nx
                if x is not None:
                    spans.append((x, s1))
            # forward
            hi = min(b, s1 + FWD)
            if all(re.search(r"\b" + re.escape(t) + r"\b", T[s0:hi], re.I) for t in low):
                y = s1
                while y < hi and not all(re.search(r"\b" + re.escape(t) + r"\b", T[s0:y], re.I) for t in low):
                    y = min(b, C.sentence_span(T, y + 1, y + 2)[1])
                    if y <= s1:
                        break
                if all(re.search(r"\b" + re.escape(t) + r"\b", T[s0:y], re.I) for t in low):
                    spans.append((s0, y))
            for x, y in spans:
                if any(S.APP_REP.search(cm.group(0)) for cm in C.CITE_RX.finditer(T, x, y)):
                    st["w_cand:app_cite_inside"] += 1
                    continue
                gw = FL.guard_anchor(T, x, y, {"c": [y, y]})
                if gw:
                    st["w_cand:" + gw] += 1
                    continue
                if best is None or (y - x) < (best[1] - best[0]):
                    best = (x, y, apart)
    if best is None:
        st["drop:wide_no_anchor"] += 1
        return None
    # reuse ulink.finish for the disposition with the anchor fixed: run it with a stub anchor search
    r = _finish_with_anchor(n, g, T, cand, best, st)
    return r


def _finish_with_anchor(n, g, T, cand, anchor, st):
    """ulink.finish's disposition / scope / own / dated steps with a given anchor (copied, unchanged)."""
    from stlink import FL
    F = BO.G["F"]
    j, phrases, cls, toks, gap = cand
    z = g["z"]
    disps = BO.dispositions(g)
    res, why = BO.decide(disps, phrases, True)
    if res is None:
        st["drop:disp:" + why] += 1
        return None
    kind, scope, (q0, q1), part, dhow = res
    if kind not in S.NEG:
        st["drop:disp_kind:" + kind] += 1
        return None
    a0, a1, apart = anchor
    if scope == "all" and kind in ("reversed", "vacated"):
        zt = " ".join(e[1] for e in (z.get("ends") or []))
        if z.get("full"):
            zt = z["head"][1]
        if z.get("open"):
            zt += " " + z["open"][1]
        if BO.OWN_AFF.search(zt) or BO.OWN_MIXED.search(zt):
            scope = "unknown"
        body = " ".join(T[a:b] for a, b, p in z["parts"] if BO.OKPART.get(p))
        if S.PARTIAL_HINT.search(body):
            scope = "unknown"
    dsent = next((d[2] for d in disps if d[0] == q0), "")
    am = BO.ACT.search(dsent)
    if am and (BO.own_disposition(dsent, am.start()) or FL.COND.search(dsent[:am.start()])):
        st["drop:disposition_not_own"] += 1
        return None
    if BO.other_dated(dsent, int(F.date[j])):
        st["drop:disposition_dated_otherwise"] += 1
        return None
    st["rows"] += 1
    st["rows:%s:%s" % (kind, scope)] += 1
    return {"rule": "below:stlink10_u", "table": "history", "claim": "-", "by": n, "target": j, "kind": kind,
            "scope": scope, "disp": [q0, q1], "anchor": [a0, a1], "anchor_part": apart,
            "ev": "name:" + " ".join(t.lower() for t in toks), "part": part, "text": "by",
            "note": "%s|%s|cap2|gap%dd|L|stlink10 u uncited" % (cls, dhow, gap)}


def select(n, g, mrow, st):
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    sysid = F.system(dc)
    d_date = int(F.date[n])
    if sysid in (0, -1) or not d_date:
        return None
    d_cname, d_tier = BO.court_at(dc, d_date)
    if d_tier != "L":
        return None
    st["opinions"] += 1
    if n in S.G["based"]:
        return None
    cands = S.G["capm"].get(n)
    if not cands:
        return None
    st["op_with_capm"] += 1
    d_all, d_sides = BO.caption(mrow[7] if mrow else "")
    if not d_all and mrow:
        d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
    cited = collections.defaultdict(list)
    for cw in g["cw"]:
        j = cw["j"]
        jc = int(F.court[j])
        if F.system(jc) == sysid and BO.court_at(jc, int(F.date[j]))[1] == "A" and \
                BO.cap_rel(d_all, N.name(j), d_sides) >= 1:
            cited[j].append(cw)
    if cited and not CITED:
        st["drop:cited_samelit"] += 1
        return None
    if CITED:
        # u2e: D cites exactly one same-litigation intermediate decision; it must be the one U2 identifies
        if not cited:
            return None
        if len(cited) != 1:
            st["drop:several_cited_samelit"] += 1
            return None
        (cj, cws), = cited.items()
        phrases, _cls = BO.tphr(int(F.court[cj]), int(F.date[cj]))
        whys = [BO.eval_candidate(cw, 2, phrases, True)[1] for cw in cws]
        bad = [w for w in whys if w in ("history_after_cite", "history_before_cite", "signal", "bracket_see")
               + (S.GUARD_WHYS if os.environ.get("U2_CITED_NOGUARD") == "1" else ())]
        if bad:
            st["drop:cite_marked:" + bad[0]] += 1
            return None
        st["cited_whys:" + ",".join(sorted(set(whys)))] += 1
    later_same = 0
    for cw in g["cw"]:
        if cw["rel"] != "lower" and BO.cap_rel(d_all, N.name(cw["j"]), d_sides) >= 2:
            later_same = max(later_same, int(F.date[cw["j"]]))
    d_name = BO.norm_ws(d_cname).replace("courts of", "court of")
    return {"cited": next(iter(cited)) if CITED else None, "cands": list(cands), "later_same": later_same, "d_all": d_all, "d_sides": d_sides, "d_name": d_name,
            "d_date": d_date}


def identity(n, sel, texts, st):
    """-> (j, tie forms, names detail) or None."""
    F = BO.G["F"]
    D = ties.parse(texts[n][1])
    df = D["front"]
    dfull = "\n".join("%s: %s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in df.items() if k != "docket") + \
        "\n" + D["body"]
    full = []
    best = collections.Counter()
    for j in sel["cands"]:
        if j not in texts:
            continue
        Tp = ties.parse(texts[j][1])
        tf = Tp["front"]
        if BODY:
            nm, nd = ties.names_tie(df.get("parties"), tf.get("parties"), D["body"], Tp["body"])
        else:
            nm, nd = ties.names_tie(df.get("parties"), tf.get("parties"))
        best[nm] += 1
        if nm in ("full", "full_body"):
            if nm == "full_body":
                st["names_full_body"] += 1
            full.append((int(F.date[j]), j, tf, nd))
    if not full:
        for k in ("mismatch", "surname_only", "frequent_only", "none", "no_parties"):
            if best[k]:
                st["drop:names:" + k] += 1
                return None
        st["drop:names:no_text"] += 1
        return None
    full.sort()
    td, j, tf, nd = full[-1]
    if any(d == td and k != j for d, k, _t, _n in full):
        st["drop:sibling_same_date"] += 1
        return None
    if sel["later_same"] and td <= sel["later_same"] < sel["d_date"]:
        st["drop:reviewed_before"] += 1
        return None
    if (n, j) in S.G["pairs"]:
        st["skip:pair_in_base"] += 1
        return None
    if CITED and j != sel["cited"]:
        st["drop:cited_not_identified"] += 1
        return None
    forms = []
    dk, _tok, _ctx = ties.docket_tie(dfull, df, tf)
    if dk == "strong":
        forms.append("docket")
    elif dk == "weak":
        forms.append("docketweak")
    elif dk == "same_as_D_docket" and (re.search(r"[a-z]", _tok) or len(_tok) >= 6):
        forms.append("docket")   # D's own head matter prints T's docket (the case kept its number)
    ct, _c = ties.cite_tie(dfull, df, L.node_row(j)[5])
    if ct in ("front", "body"):
        forms.append("cite")
    if ties.date_tie(D["body"], tf) == "present":
        forms.append("date")
    # an earlier full-name decision holding the docket / citation tie while the latest one does not: ambiguous
    use = [f for f in forms if f in TIES]
    if TIE3:
        # u2t (stlink12): pairs with NO docket / citation / date tie (those are U2's), full names of real parties
        # (strict: no role phrase / "X et al" entity), and a third tie from ties3 (TIE3_FORMS)
        if use:
            st["t3_skip:has_u2_tie"] += 1
            return None
        if not ties3.strict_names(nd):
            st["drop:t3_names_not_strict"] += 1
            return None
        Tp = ties.parse(texts[j][1])
        t3 = ties3.all_ties(D, Tp)
        use = [f for f in TIE3_FORMS if f in t3]
        if not use:
            st["drop:no_third_tie"] += 1
            return None
        for _d, k, tf2, _n in full[:-1]:
            if ties.docket_tie(dfull, df, tf2)[0] == "strong" or                     ties.cite_tie(dfull, df, L.node_row(k)[5])[0] in ("front", "body"):
                st["drop:tie_on_earlier"] += 1
                return None
        forms = ["t3" + f for f in use]
        st["t3_forms:" + "+".join(sorted(t3))] += 1
    if not use:
        st["drop:no_second_tie"] += 1
        for _d, k, tf2, _n in full[:-1]:
            if ties.docket_tie(dfull, df, tf2)[0] == "strong" or \
                    ties.cite_tie(dfull, df, L.node_row(k)[5])[0] in ("front", "body"):
                st["drop:tie_on_earlier"] += 1
                break
        return None
    # (a) district / division
    dv = divisions(D["body"])
    if dv:
        tt = texts[j][1][:6000]
        tv = divisions(tt)
        if not (dv & tv):
            dk2 = str(tf.get("docket") or "")
            ok = False
            for unit, o in dv:
                roman = {1: "i", 2: "ii", 3: "iii", 4: "iv", 5: "v", 6: "vi", 7: "vii", 8: "viii"}.get(o)
                if roman and re.search(r"-" + roman + r"\b", dk2, re.I):
                    ok = True
            if not ok:
                st["drop:division_differs" if tv else "drop:division_unknown"] += 1
                return None
        st["division_checked"] += 1
    return j, forms, nd


def run_shard(path):
    if "based" not in S.G:
        S.init()
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    st = collections.Counter()
    pend = []
    for n, g in L.decisions(path):
        try:
            sel = select(n, g, meta.get(n), st)
        except Exception as ex:  # noqa: BLE001
            st["error_select"] += 1
            if st["error_select"] <= 3:
                sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
            continue
        if sel:
            pend.append((n, g, sel))
    F, N = BO.G["F"], BO.G["N"]
    rows, drops = [], []
    for k in range(0, len(pend), 300):
        chunk = pend[k:k + 300]
        want = set()
        for n, _g, sel in chunk:
            want.add(n)
            want |= set(sel["cands"])
        texts = L.fetch_texts(sorted(want))
        for n, g, sel in chunk:
            if n not in texts:
                st["drop:no_text"] += 1
                continue
            try:
                idt = identity(n, sel, texts, st)
                if idt is None:
                    continue
                j, forms, nd = idt
                phrases, cls = BO.tphr(int(F.court[j]), int(F.date[j]))
                if cls != "app":
                    st["drop:not_app"] += 1
                    continue
                ph = {p for p in phrases if p not in sel["d_name"]}
                if "appellate division" in ph:
                    ph.discard("superior court")
                j_all, j_sides = BO.caption(N.name(j))
                toks = []
                if FULLTOK:
                    # u2b: the anchor carries the name of a party matched in full (identity is settled by the
                    # full names + second tie outside the quote): surname of a person, rarest word of an organisation
                    for e in nd.split("|"):
                        if ties.is_org(e):
                            ws = [w for w in re.findall(r"[a-z]{3,}", ties.org_key(e)) if w not in S.G["inst"]]
                            ws.sort(key=lambda t: S.G["tokdf"].get(t.rstrip("s"), 0))
                            if ws:
                                toks = [ws[0]]
                                break
                        else:
                            sur = ties.person_key(e)[1]
                            if sur and len(sur) >= 3 and re.fullmatch(r"[a-z]+", sur):
                                toks = [sur]
                                break
                for side in ([] if FULLTOK else j_sides):
                    if not side:
                        continue
                    sh = sorted(side & sel["d_all"], key=lambda t: S.G["tokdf"].get(t.lower().rstrip("s"), 0))
                    if not sh:
                        toks = None
                        break
                    toks.append(sh[0])
                if not toks:
                    st["drop:side_not_shared"] += 1
                    continue
                st["identified"] += 1
                for f in forms:
                    st["ident_tie:" + f] += 1
                st["ident_forms:" + "+".join(forms)] += 1
                gap = BO.day(sel["d_date"]) - BO.day(F.date[j])
                before = collections.Counter(st)
                r = U.finish(n, g, L.norm(texts[n][1]), (j, ph, cls, toks, gap), st)
                if not r:
                    why = [k for k in st if st[k] != before.get(k, 0) and k.startswith("drop:")]
                    drops.append("%d\t%d\t%s\t%s\n" % (n, j, "+".join(forms), ",".join(why)))
                if WIDE:
                    # u2w: only pairs whose rule-U anchor failed for want of the name near a court act
                    # (tokens_not_near / no_court_act); the u2c rows themselves are not repeated
                    if r or not any(w in ("drop:anchor:tokens_not_near", "drop:anchor:no_court_act") for w in why):
                        st["w_skip"] += 1
                        continue
                    r = finish_wide(n, g, L.norm(texts[n][1]), (j, ph, cls, toks, gap), st)
                    if r:
                        r["note"] = r["note"].replace("stlink10 u uncited", "stlink10 u uncited wide")
            except Exception as ex:  # noqa: BLE001
                st["error_finish"] += 1
                if st["error_finish"] <= 3:
                    sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
                continue
            if r:
                if TIE3:
                    r["rule"] = "below:stlink12_u2t" + ("w" if WIDE else "")
                    r["note"] = r["note"].replace("stlink10 u uncited", "stlink12 u2t " + "+".join(forms))
                else:
                    r["rule"] = "below:stlink11_u2" + ("c" if CITED else "") + ("w" if WIDE else "")
                    r["note"] = r["note"].replace("stlink10 u uncited", "stlink11 u2 " + "+".join(forms))
                st["rows_tie:" + "+".join(forms)] += 1
                rows.append(r)
    with open(os.path.join(WORK, tag + ".rows.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, tag + ".stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    with open(os.path.join(WORK, tag + ".drops.tsv"), "w", encoding="utf-8", newline=NL) as f:
        f.writelines(drops)
    return tag, len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--shards")
    ap.add_argument("--tag", default="u2a")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    import pop
    paths = pop.state_shards()
    if a.shards:
        want = set(a.shards.split(","))
        paths = [p for p in paths if os.path.basename(p)[:-len(".jsonl.gz")] in want]
    paths.sort(key=os.path.getsize, reverse=True)
    if a.procs <= 1:
        S.init()
        for p in paths:
            print(run_shard(p), flush=True)
    else:
        for tag, k in L.pmap(run_shard, paths, procs=a.procs, initializer=S.init):
            print(tag, k, flush=True)
    if not a.shards:
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
