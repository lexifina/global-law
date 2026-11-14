"""fedcir11 linker: the decision under review in an opinion of the Federal Circuit (courts2 520) or of the Court of
Customs and Patent Appeals (655): the FJC linker (round 8 F1 / F3, round 9 W, round 10 rule P) ported to the
tribunals these courts review.

    python -X utf8 fedcir_link.py base                       -> work/based.json
    python -X utf8 fedcir_link.py run [--procs 5] [--tag a]  -> rows_<tag>.jsonl, link_stats_<tag>.json

Reads only the round-6 cache, graph/nodes.tsv, court facts, decision texts (git), the cue table (read only) and the
v10d history table (to know which opinions already have a review row). No key, no list of cases.

Acting decision D: a Federal Circuit opinion (any date) or a CCPA opinion, with no v10d review-kind history row on a
decision of a tribunal it reviews and no round-6 below_other row on one.
Tribunals reviewed (target classes; courts2 facts): Federal Circuit -> United States district courts (any district),
Claims Court / Court of Federal Claims (656), Court of International Trade (657, from 1 Nov 1980), Court of Veterans
Appeals / Court of Appeals for Veterans Claims (651); CCPA -> Customs Court / Court of International Trade (657).
Candidate J: a cited decision of a reviewed tribunal, 0..6 years before D (round 6 window).
Identity (F1): J's caption is D's caption (round 6 cap 2); J is the only decision of a reviewed tribunal in the
window that shares a party name with D's caption (cap >= 1); no decision of D's court or a higher one with D's caption
dated after J (an earlier appeal). Citation marks: round 6 eval_candidate at cap 2 on every citation of J: a history
tag, signal, bracket-see or round 6's earlier / interlocutory / later guard drops J.
Anchor (first that applies; the anchor must hold J's citation):
  r6   round 6's own anchor (citation sentence, or it and the sentence before, naming the court / procedural cue);
  back the nearest sentence before the citation (<= 1,500 characters, same part, no other decision's citation in
       between) that names J's tribunal by one of its phrases, through the end of the citation sentence;
  fwd  the citation sentence through the next sentence when that one names the tribunal.
  head (F3) the head-matter line naming the tribunal ("Appeal from the United States Court of International Trade")
       extended back over the caption lines holding the shared distinctive party tokens (evidence name:).
Every anchor passes F1's guard_anchor (round 6 earlier / interlocutory / later words, anchor disqualifiers). The
anchor's certificate cue: the Lean anchor list (cue table `anchor`); an anchor whose only tribunal word is one the
list lacks ("court of international trade", "court of federal claims", ...) is written with class `tribunal` in its
note (needs LEAN_REQUEST) and kept apart.
Disposition: round 6 decide (direct review) with the tribunal's phrases, fjc8 S1 and sanity / ruling-type /
dated-otherwise tests, mixed end zone; rule P (fjc9 PARTIAL_HINT, with the tribunal's names) and the hyphenated
partial forms of the Federal Circuit's judgment lines ("AFFIRMED-IN-PART, REVERSED-IN-PART") -> scope unknown.
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(C2, "round9", "agents", "fjc9"))
import fjc9_link as W  # noqa: E402
from fjc9_link import FL, BO, L, C, diag  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "link")
G = {}
ACT = {520, 655}
REVIEW_KINDS = {"reversed", "vacated", "affirmed", "modified", "reviewDismissed"}
BACK = 1500
LATEST = os.environ.get("FEDCIR_L", "1") == "1"
REPLACE = os.environ.get("FEDCIR_R") == "1"   # rule R: replace the base 'affirmed' row of D on T   # form L (latest of several same-caption decisions below)

TRIB_PHRASES = {
    "dist": ["district court", "district judge", "trial court", "court below", "lower court", "magistrate judge"],
    "cfc": ["court of federal claims", "claims court", "court of claims", "trial court", "court below", "lower court",
            "trial judge"],
    "cit": ["court of international trade", "customs court", "trade court", "trial court", "court below",
            "lower court", "trial judge"],
    "cavc": ["court of appeals for veterans claims", "court of veterans appeals", "veterans court", "court below",
             "lower court"],
}
ALLP = sorted({p for v in TRIB_PHRASES.values() for p in v}, key=len, reverse=True)
TRIB_RX = re.compile(r"\b(" + "|".join(p.replace(" ", r"\s+") for p in ALLP) + r")s?\b", re.I)
HEAD_RX = re.compile(r"\b(?:appeals?|petitions?\s+for\s+review)\s+from\s+(?:the\s+)?(?:United\s+States\s+)?"
                     r"(district\s+court|court\s+of\s+federal\s+claims|claims\s+court|court\s+of\s+international\s+trade|"
                     r"customs\s+court|court\s+of\s+appeals\s+for\s+veterans\s+claims|court\s+of\s+veterans\s+appeals)",
                     re.I)
HEAD_CLASS = {"district court": "dist", "court of federal claims": "cfc", "claims court": "cfc",
              "court of international trade": "cit", "customs court": "cit",
              "court of appeals for veterans claims": "cavc", "court of veterans appeals": "cavc"}
HYPH_PART = re.compile(r"\b(?:affirm|revers|vacat|modif)\w*[\s-]+in[\s-]+part\b|\bin[\s-]+part\b", re.I)
PARTIAL_X = re.compile(r"\bwe\s+agree\s+with\s+the\s+(?:court\s+of\s+(?:federal\s+claims|international\s+trade)|"
                       r"claims\s+court|veterans\s+court|trade\s+court|board)\b", re.I)


def lean_anchor_cues():
    if "lean" not in G:
        t = json.load(open(os.path.join(os.path.expanduser("~"), "Documents", "global-law-lean", "lean-proofs", "tools",
                                        "caselaw2", "cues", "cue_table.json"), encoding="utf-8"))
        G["lean"] = [c for c in t["anchor"] if c]
        G["disq"] = [c for c in t["disqualify_anchor"] if c]
    return G["lean"]


def tclass(jc, jdate, dc):
    nm, t = BO.court_at(jc, jdate)
    F = BO.G["F"]
    if dc == 655:
        return "cit" if jc == 657 else None
    if jc == 656:
        return "cfc"
    if jc == 657:
        return "cit" if jdate >= 19801101 else None
    if jc == 651:
        return "cavc"
    if F.system(jc) == 0 and t == "T" and "district court" in nm.lower() and "bankruptcy" not in nm.lower():
        return "dist"
    return None


def base():
    BO.init()
    F = BO.G["F"]
    out = set()
    brows = collections.defaultdict(list)
    with open(os.path.join(C2, "round10", "stage", "v10d", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 6 or p[4] not in REVIEW_KINDS:
                continue
            try:
                t, by = int(p[1]), int(p[2])
            except ValueError:
                continue
            dc = int(F.court[by])
            if dc in ACT and tclass(int(F.court[t]), int(F.date[t]), dc):
                out.add(by)
                brows[by].append([p[0], t, p[4], p[5], p[12]])
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    json.dump(sorted(out), open(os.path.join(HERE, "work", "based.json"), "w"))
    json.dump({str(k): v for k, v in brows.items()}, open(os.path.join(HERE, "work", "based_rows.json"), "w"))
    print("v10d Federal Circuit / CCPA opinions with a review row on a reviewed tribunal:", len(out))


def init():
    FL.init()
    G["based"] = set(json.load(open(os.path.join(HERE, "work", "based.json"))))
    G["brows"] = {int(k): v for k, v in json.load(open(os.path.join(HERE, "work", "based_rows.json"))).items()}
    lean_anchor_cues()


def select(n, g, mrow, st):
    st = FL.Why(st, n)
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    d_date = int(F.date[n])
    if dc not in ACT or not d_date:
        return []
    st["opinions"] += 1
    want_t = None
    if REPLACE:
        # rule R: D's only v10d review rows on a reviewed tribunal are "affirmed" rows on one target T; the
        # candidate must be T and D's own judgment line must reverse / vacate / modify (finish)
        br = G["brows"].get(n)
        if not br:
            return []
        if any(b[2] != "affirmed" for b in br) or len({b[1] for b in br}) != 1:
            st["drop:R_base_not_single_affirmed"] += 1
            return []
        want_t = br[0][1]
        st["R_opinions"] += 1
    else:
        if n in G["based"]:
            st["skip:base_row"] += 1
            return []
        rows = BO.process(n, g, mrow, collections.Counter(), None)
        if rows:
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
        jd = int(F.date[j])
        cls = tclass(int(F.court[j]), jd, dc)
        if cls is None:
            continue
        gap = BO.day(d_date) - BO.day(jd)
        if gap < 0 or gap > BO.MAX_GAP_DAYS:
            continue
        by_j[j].append(cw)
        info[j] = (cls, BO.cap_rel(d_all, N.name(j), d_sides), gap)
    same_lit = [j for j in by_j if info[j][1] >= 1]
    if not same_lit:
        return []
    st["op_with_samelit"] += 1
    form = "1"
    if len(same_lit) > 1:
        # form L (the latest decision below in the same case): every same-litigation decision is of the same
        # tribunal and has D's caption (cap 2); the latest of them (unique date) is the one under review
        cl = {info[x][0] for x in same_lit}
        if not LATEST or len(cl) != 1 or any(info[x][1] < 2 for x in same_lit):
            st["drop:several_same_lit"] += 1
            return []
        same_lit.sort(key=jd_of)
        if jd_of(same_lit[-1]) == jd_of(same_lit[-2]):
            st["drop:several_same_lit_tie"] += 1
            return []
        same_lit = same_lit[-1:]
        form = "L"
    j = same_lit[0]
    cls, cap, gap = info[j]
    if want_t is not None and j != want_t:
        st["drop:R_other_target"] += 1
        return []
    if cap < 2:
        st["drop:cap1"] += 1
        return []
    if later_same and jd_of(j) <= later_same < d_date:
        st["drop:reviewed_before"] += 1
        return []
    phrases = set(TRIB_PHRASES[cls])
    whys, keep = [], []
    for cw in by_j[j]:
        ok, why, anchor, apart = BO.eval_candidate(cw, 2, phrases, True)
        whys.append(why)
        if BO.OKPART.get(cw["part"]) and (ok or why in ("no_court_phrase", "no_design_cue")):
            keep.append(dict(cw, r6ok=anchor if ok else None))
    bad = [w for w in whys if w in ("history_after_cite", "history_before_cite", "signal", "bracket_see",
                                    "earlier_proceeding", "interlocutory_ruling", "later_events", "named_other_case")]
    if bad:
        st["drop:cite_marked:" + bad[0]] += 1
        return []
    if not keep:
        st["drop:no_eligible_cite:" + ",".join(sorted(set(whys)))] += 1
        return []
    shared = BO.caption(N.name(j))[0] & d_all
    return [(j, keep, phrases, cls, cap, gap, shared, form)]


def jd_of(j):
    return int(BO.G["F"].date[j])


def find_anchor(T, cw, z, phrases, jkeys):
    c0 = cw["c"][0]
    s0, s1 = cw["s"]
    pb = FL.part_bounds(z, c0)
    if pb is None:
        return None, "no_part"
    p0, p1, _p = pb
    lo = max(p0, s0 - BACK)
    best = None
    for m in TRIB_RX.finditer(T, lo, c0):
        if BO.norm_ws(m.group(1)) in phrases:
            best = m
    if best is not None:
        a0 = max(C.sentence_span(T, best.start(), best.end())[0], p0)
        for m in C.CITE_RX.finditer(T, best.end(), c0):
            k = C.cite_key(m)
            if k and re.sub(r"[^a-z0-9]", "", k.lower()) not in jkeys:
                best = None
                break
        if best is not None:
            return (a0, s1, "back"), ""
    if s1 < p1:
        k = s1
        while k < p1 and T[k] == " ":
            k += 1
        if k < p1:
            n0, n1 = C.sentence_span(T, k, k + 1)
            n1 = min(n1, p1)
            for m in TRIB_RX.finditer(T, k, n1):
                if BO.norm_ws(m.group(1)) in phrases:
                    return (s0, n1, "fwd"), ""
    return None, "no_tribunal_phrase_near"


def head_anchor(T, z, cls, shared):
    toks = sorted({t for t in shared if len(re.sub(r"[^A-Za-z0-9]", "", t)) >= 3})
    distinct = [t for t in toks if t.lower().rstrip("s") not in FL.G["inst"]
                and FL.G["tokdf"].get(t.lower().rstrip("s"), 0) <= FL.DISTINCT_DF]
    if not distinct:
        return None, "head_no_distinct_token"
    for p0, p1, p in z["parts"]:
        if p != "headmatter":
            continue
        for m in HEAD_RX.finditer(T, p0, min(p1, p0 + 6000)):
            if HEAD_CLASS.get(BO.norm_ws(m.group(1))) != cls:
                continue
            a1 = min(p1, m.end())
            lo = max(p0, m.start() - 700)
            words = {}
            for w in FL.WORD_RX.finditer(T, lo, a1):
                words.setdefault(w.group(0).lower(), w.start())
            have = [t for t in toks if t.lower() in words]
            if not any(t in have for t in distinct):
                continue
            a0 = min(words[t.lower()] for t in have)
            return (a0, a1, "name:" + " ".join(t.lower() for t in have)), ""
    return None, "head_no_line"


def guard(T, a0, a1, cw):
    """F1's guard_anchor without its design-cue test (the cue is classed after)."""
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
    return ""


def cue_class(T, a0, a1):
    low = BO.norm_ws(T[a0:a1])
    hit = [q for q in G["lean"] if q in low]
    if hit:
        return "lean", hit[0]
    m = TRIB_RX.search(T, a0, a1)
    return "tribunal", (BO.norm_ws(m.group(1)) if m else "-")


def finish(n, g, T, cand, st):
    st = FL.Why(st, n, cand[0])
    F = BO.G["F"]
    j, cws, phrases, cls, cap, gap, shared, form = cand
    z = g["z"]
    if not z:
        st["drop:no_zone"] += 1
        return None
    jkeys = FL.own_keys(j)
    anchor, why = None, "no_cite"
    for cw in cws:
        if cw.get("r6ok"):
            a0, a1 = cw["r6ok"]
            how = "r6"
        else:
            res, why = find_anchor(T, cw, z, phrases, jkeys)
            if res is None:
                continue
            a0, a1, how = res
        gw = guard(T, a0, a1, cw)
        if gw:
            why = gw
            continue
        anchor = (a0, a1, how, cw)
        break
    ev = None
    if anchor is None and why == "no_tribunal_phrase_near":
        res, why2 = head_anchor(T, z, cls, shared)
        if res is not None:
            a0, a1, ev = res
            gw = guard(T, a0, a1, {"c": [a1, a1]})
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
    cc, cue = cue_class(T, a0, a1)
    disps = BO.dispositions(g)
    res, why = BO.decide(disps, phrases, True)
    if res is None:
        st["drop:disp:" + why] += 1
        return None
    kind, scope, (q0, q1), part, dhow = res
    zt = " ".join(e[1] for e in (z.get("ends") or []))
    if z.get("full"):
        zt = z["head"][1]
    if z.get("open"):
        zt += " " + z["open"][1]
    if scope == "all" and kind in ("affirmed", "reversed", "vacated"):
        other_rx = BO.OWN_NEG if kind == "affirmed" else BO.OWN_AFF
        if other_rx.search(zt) or BO.OWN_MIXED.search(zt) or HYPH_PART.search(zt):
            scope = "unknown"
            st["scope_unknown_mixed_endzone"] += 1
    dsent = next((d[2] for d in disps if d[0] == q0), "")
    if scope == "all" and HYPH_PART.search(dsent):
        scope = "unknown"
        st["scope_unknown_hyphen_part"] += 1
    if scope == "all" and kind in ("reversed", "vacated"):
        body = " ".join(T[a:b] for a, b, p in z["parts"] if BO.OKPART.get(p))
        if W.PARTIAL_HINT.search(body) or PARTIAL_X.search(body):
            scope = "unknown"
            st["scope_unknown_partial_hint"] += 1
    if REPLACE and kind not in ("reversed", "vacated", "modified"):
        st["drop:R_judgment_not_negative"] += 1
        return None
    am = BO.ACT.search(dsent)
    if am and (BO.own_disposition(dsent, am.start()) or FL.COND.search(dsent[:am.start()])):
        st["drop:disposition_not_own"] += 1
        return None
    if how != "head":
        ca = T[max(cw["s"][0] - 400, 0):cw["s"][1]]
        ta, td = FL.ruling_types(ca), FL.ruling_types(dsent)
        if ta and td and not (ta & td):
            st["drop:ruling_mismatch"] += 1
            return None
    if BO.other_dated(dsent, int(F.date[j])):
        st["drop:disposition_dated_otherwise"] += 1
        return None
    apart = "headmatter" if how == "head" else BO.OKPART.get(cw["part"], cw["part"])
    st["rows"] += 1
    st["rows:%s:%s:%s:%s:%s:%s" % (form, cls, how, cc, kind, scope)] += 1
    return {"rule": "below:fedcir11_%s_%s_%s" % (form, cls, how), "table": "history", "claim": "-", "by": n, "target": j,
            "kind": kind, "scope": scope, "disp": [q0, q1], "anchor": [a0, a1], "anchor_part": apart,
            "ev": ev or ("cite:" + cw["key"]), "part": part, "text": "by",
            "note": "%s|%s|cap%d|gap%dd|A|fedcir11 %s %s %s cue=%s:%s" % (cls, dhow, cap, gap, form, cls, how, cc, cue)}


def run_shard(path):
    if "based" not in G:
        init()
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    st = collections.Counter()
    pend = []
    F = BO.G["F"]
    for n, g in L.decisions(path):
        if not g["cw"] or int(F.court[n]) not in ACT:
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
    ap.add_argument("--procs", type=int, default=5)
    ap.add_argument("--tag", default="a")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    FL.WORK = WORK
    if a.cmd == "base":
        base()
        return
    paths = [p for p in L.shards() if os.path.basename(p).startswith(("cafc.", "federal-special.0"))]
    paths.sort(key=os.path.getsize, reverse=True)
    if a.cmd == "run":
        for tag, k in L.pmap(run_shard, paths, procs=a.procs, initializer=init):
            print(tag, k, flush=True)
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
