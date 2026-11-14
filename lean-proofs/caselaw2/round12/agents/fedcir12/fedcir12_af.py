"""fedcir12 appeal-from identity (round-10 FJC form h ported to the Federal Circuit; DESIGN12 fedcir12 move 1 / 2).

    python -X utf8 fedcir12_af.py run [--procs 6] [--tag a1]  -> rows_<tag>.jsonl, pairs_<tag>.tsv, link_stats_<tag>.json

Reads only the round-6 cache, graph/nodes.tsv, court facts, decision texts (git), the cue table (read only) and the
v11d history table (work/based_rows.json from fedcir12_link.py base). No key, no list of cases.

Acting decision D: a Federal Circuit opinion (courts2 520). Candidates J: cited decisions (round-6 cache, rel lower) of a
tribunal the Federal Circuit reviews (district court, Claims Court / Court of Federal Claims, Court of International
Trade, Veterans Court), 0..6 years before D, caption relation cap >= 1.

Appeal-from statement S of D (the acting court's own statement of what is appealed), first that applies:
  head  a head-matter line "Appeal(s) from the United States <tribunal> ... in No(s). <docket>, <Judge X>";
  open  a sentence of the first 3,000 characters of the majority naming the appeal ("appeal(s|ed) ... from") and the
        tribunal, with a docket number ("No. ...").
Facts of S: dockets (year + serial), dates printed in S ("July 13, 1988"), the judge's surname ("Judge X", "(X, J.)").
Facts of J: its front-matter docket, decision date, author ("X, District Judge" / "X, Judge").
Identity A (J is the ruling under review): J's docket is printed in S, and
  - S prints a date: J's date is one of S's dates (form "d");
  - S prints no date: J's author is S's judge when both are known (no conflict), and J is the latest candidate of
    that docket dated before D (unique date; form "l");
  a date in S that is not J's date = J is another ruling of the docket (never linked; "date_conflict").
Base rows: D's v11d review rows on a reviewed tribunal (work/based_rows.json). Pair classes in pairs_<tag>.tsv:
  new      D has no base row; J identified;
  same     J is a base target;
  other    D's base target(s) T' differ from J (move 2): T' of the same docket excluded by S's date / latest rule
           (T' not under review: 'other_excluded') or not (consolidated / unknown: 'other_kept').
Anchor: S itself (cue "appeal from" / "district court" / tribunal words); evidence: J's citation when S holds it, else
"name:<J's docket serial>". Disposition: as fedcir11 / fjc10 (round 6 decide, mixed end zone, hyphenated in-part,
rule P, own / dated-otherwise tests).
"""
import argparse, collections, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fedcir12_link as FC  # noqa: E402
from fedcir12_link import W, FL, BO, L, C  # noqa: E402

C2 = FC.C2
sys.path.insert(0, os.path.join(C2, "round6", "history"))
import certify6 as C6  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "af")
G = FC.G
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]
MON_RX = r"(?:Jan(?:uary|\.)?|Feb(?:ruary|\.)?|Mar(?:ch|\.)?|Apr(?:il|\.)?|May|June?|July?|Aug(?:ust|\.)?|Sept?(?:ember|\.)?|Oct(?:ober|\.)?|Nov(?:ember|\.)?|Dec(?:ember|\.)?)"
DATE_RX = re.compile(r"\b(" + MON_RX + r")\s+(\d{1,2}),?\s+((?:19|20)\d\d)\b")
TRIB_WORDS = {
    "dist": r"district\s+court",
    "cfc": r"court\s+of\s+federal\s+claims|claims\s+court",
    "cit": r"court\s+of\s+international\s+trade",
    "cavc": r"court\s+of\s+appeals\s+for\s+veterans\s+claims|court\s+of\s+veterans\s+appeals|veterans\s+court",
}
HEAD_AF = re.compile(r"\bappeals?\s+from\s+(?:the\s+)?(?:United\s+States\s+)?(" + "|".join(TRIB_WORDS.values()) + r")",
                     re.I)
OPEN_AF = re.compile(r"\bappeal(?:s|ed)?\b[^.]{0,200}?\bfrom\b|\bappeal(?:s|ed)?\s+(?:the|a|an)\b", re.I)
NO_RX = re.compile(r"\b(?:Civil\s+Action\s+|Case\s+|Docket\s+|C\.\s*A\.\s+)?Nos?\.\s*", re.I)
JUDGE_RX = re.compile(r"\b(?:Chief\s+|Senior\s+)?(?:District\s+|Magistrate\s+|Bankruptcy\s+)?Judge\s+((?:[A-Z][\w'’.\-]*\s+){0,3}"
                      r"[A-Z][\w'’\-]+)|\(([A-Z][\w'’\-]+),\s*(?:Chief\s+|Senior\s+)?(?:District\s+|Magistrate\s+)?J\.\)")
J_AUTHOR = re.compile(r"^## Majority \(([^,()]+?),\s*(?:Senior\s+|Chief\s+)?(?:United\s+States\s+)?"
                      r"(?:District|Magistrate|Bankruptcy|Trial|Special\s+Trial)?\s*Judge", re.M | re.I)


DK_RX = re.compile(r"\d:(\d{2})\s*[-–]?\s*[A-Za-z]{1,5}\s*[-–]?\s*(\d{2,6})"          # 1:10-cv-00123
                   r"|\b(\d{2})\s*[-–]\s*\d{2}\s*[-–]\s*(\d{5})\b"                          # CIT 85-03-00341
                   r"|\b(\d{2,4})\s*[-–]\s*(?:[A-Za-z]{1,6}\s*[-–]?\s*)?(\d{2,6})"            # 88-1554, 84-C-123
                   r"|\b(\d{2})\s+[A-Z]{1,3}\s+(\d{3,6})\b"                                  # 84 C 10670
                   r"|\b(\d{3,6})\s*[-–]\s*(\d{2})\s*[A-Z]\b", re.I)                         # Cl. Ct. 123-82C


def norm_dk(s):
    """docket number tokens: (year, serial) pairs (same normalisation for both sides; serial >= 3 digits)."""
    out = []
    for m in DK_RX.finditer(s or ""):
        gs = m.groups()
        if gs[0]:
            y, n = gs[0], gs[1]
        elif gs[2]:
            y, n = gs[2], gs[3]
        elif gs[4]:
            y, n = gs[4], gs[5]
        elif gs[6]:
            y, n = gs[6], gs[7]
        else:
            y, n = gs[9], gs[8]
        n = n.lstrip("0") or "0"
        if len(n) < 3 and len(y) < 3:
            continue
        out.append((y[-2:].lstrip("0") or "0", n))
    return out


def stmt_facts(S):
    dks = set()
    for m in NO_RX.finditer(S):
        seg = S[m.end():m.end() + 160]
        seg = re.split(r"\b(?:Judge|Senior|Chief|\(|[A-Z][a-z]+\s+\d{1,2},)", seg)[0]
        dks.update(norm_dk(seg))
    dates = {int("%s%02d%02d" % (m.group(3), month_of(m.group(1)), int(m.group(2)))) for m in DATE_RX.finditer(S)}
    judges = set()
    for m in JUDGE_RX.finditer(S):
        nm = (m.group(1) or m.group(2) or "").split()
        if nm:
            judges.add(nm[-1].strip(".").lower())
    return dks, dates, judges


def month_of(s):
    s = s[:3].lower()
    return [x[:3].lower() for x in MONTHS].index(s) + 1


def statements(T, z):
    out = []
    for p0, p1, p in z["parts"]:
        if p == "headmatter":
            for m in HEAD_AF.finditer(T, p0, min(p1, p0 + 8000)):
                e = T.find(NL, m.end())
                e = min(p1, e if e > 0 else p1, m.end() + 600)
                b = T.rfind(NL, p0, m.start()) + 1
                b = max(b, p0)
                out.append(("head", b, e, BO.norm_ws(m.group(1))))
    maj = [(p0, p1) for p0, p1, p in z["parts"] if BO.OKPART.get(p) == "majority" or p == "majority"]
    if maj:
        p0, p1 = maj[0]
        lim = min(p1, p0 + 3000)
        k = p0
        while k < lim:
            s0, s1 = C.sentence_span(T, k, k + 1)
            s1 = min(max(s1, k + 1), p1)
            sent = T[s0:s1]
            if OPEN_AF.search(sent) and NO_RX.search(sent):
                for cls, rx in TRIB_WORDS.items():
                    mm = re.search(rx, sent, re.I)
                    if mm:
                        out.append(("open", s0, s1, BO.norm_ws(mm.group(0))))
                        break
            k = s1 + 1
    return out


def stmt_class(w):
    for cls, rx in TRIB_WORDS.items():
        if re.fullmatch(rx, w, re.I):
            return cls
    return None


def j_facts(TJ):
    dk = ""
    m = re.search(r'^docket:\s*"([^"]*)"', TJ[:3000], re.M)
    if m:
        dk = m.group(1)
    jm = J_AUTHOR.search(TJ[:20000])
    judge = jm.group(1).split()[-1].lower() if jm else ""
    return dk, judge


def select(n, g, mrow, st):
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    d_date = int(F.date[n])
    if dc != 520 or not d_date:
        return []
    st["opinions"] += 1
    d_all, d_sides = BO.caption(mrow[7] if mrow else "")
    if not d_all and mrow:
        d_all, d_sides = BO.caption("", mrow[8].split(" | ")[:2])
    by_j = collections.defaultdict(list)
    info = {}
    for cw in g["cw"]:
        if cw["rel"] != "lower":
            continue
        j = cw["j"]
        jd = int(F.date[j])
        cls = FC.tclass(int(F.court[j]), jd, dc)
        if cls is None:
            continue
        gap = BO.day(d_date) - BO.day(jd)
        if gap < 0 or gap > BO.MAX_GAP_DAYS:
            continue
        cap = BO.cap_rel(d_all, N.name(j), d_sides)
        if cap < 1:
            continue
        by_j[j].append(cw)
        info[j] = (cls, cap, gap)
    if not by_j:
        return []
    st["op_with_cand"] += 1
    return [(by_j, info)]


def finish(n, g, T, TJS, cand, st, pairs_out):
    F = BO.G["F"]
    by_j, info = cand
    z = g["z"]
    base = G["brows"].get(n, [])
    btargets = {b[1] for b in base}
    if not z:
        st["drop:no_zone"] += 1
        return None
    stm = statements(T, z)
    if not stm:
        st["no_statement"] += 1
        for j in by_j:
            pairs_out.append((n, j, info[j][0], "-", "no_statement", "", ",".join(map(str, sorted(btargets)))))
        return None
    st["with_statement:" + stm[0][0]] += 1
    facts = []
    for how, s0, s1, w in stm:
        dks, dates, judges = stmt_facts(T[s0:s1])
        facts.append((how, s0, s1, stmt_class(w), dks, dates, judges))
    jf = {j: j_facts(TJS.get(j, "")) for j in by_j}
    # all reviewed-tribunal decisions of D's base rows too (for the 'other' classes)
    verdict = {}
    for j in set(by_j) | btargets:
        dk, judge = jf[j] if j in jf else j_facts(TJS.get(j, ""))
        jd = int(F.date[j])
        jdk = set(norm_dk(dk))
        best = None
        for how, s0, s1, cls, dks, dates, judges in facts:
            if not jdk or not (jdk & dks):
                continue
            if dates:
                v = "date_eq" if jd in dates else "date_conflict"
            elif judges and judge:
                v = "judge_eq" if judge in judges else "judge_conflict"
            else:
                v = "docket_only"
            rank = {"date_eq": 0, "judge_eq": 1, "docket_only": 2, "judge_conflict": 3, "date_conflict": 4}[v]
            if best is None or rank < best[0]:
                best = (rank, v, how, s0, s1)
        verdict[j] = best
    # identity A
    ok = [j for j in by_j if verdict[j] and verdict[j][1] in ("date_eq", "judge_eq", "docket_only")]
    pick, form = None, ""
    if ok:
        d_eq = [j for j in ok if verdict[j][1] == "date_eq"]
        if len(d_eq) == 1:
            pick, form = d_eq[0], "d"
        elif not d_eq:
            # latest of the docket candidates (unique date) dated before D; base targets of the docket count too
            pool = ok + [t for t in btargets if t not in by_j and verdict.get(t) and verdict[t][1] in
                         ("judge_eq", "docket_only")]
            pool.sort(key=lambda x: int(F.date[x]))
            if len(pool) == 1 or int(F.date[pool[-1]]) != int(F.date[pool[-2]]):
                if pool[-1] in by_j:
                    pick, form = pool[-1], "l"
                else:
                    st["latest_is_uncited_base"] += 1
            else:
                st["latest_tie"] += 1
        else:
            st["several_date_eq"] += 1
    for j in by_j:
        v = verdict[j]
        cls = "new" if not btargets else ("same" if j in btargets else "other")
        pairs_out.append((n, j, info[j][0], v[1] if v else "no_docket_tie", "pick" if j == pick else "-", cls,
                          ",".join("%d:%s:%s" % (t, verdict[t][1] if verdict.get(t) else "x", b2)
                                   for t, b2 in sorted({(b[1], b[2]) for b in base}))))
    if pick is None:
        st["no_pick"] += 1
        return None
    j = pick
    cls, cap, gap = info[j]
    rank, v, how, a0, a1 = verdict[j]
    if j in btargets:
        st["pick_same_as_base"] += 1
        return None
    oclass = "new"
    if btargets:
        excl = [t for t in btargets if verdict.get(t) and (verdict[t][1] == "date_conflict" or
                                                          (form == "l" and int(F.date[t]) < int(F.date[j])))]
        oclass = "other_excluded" if len(excl) == len(btargets) else "other_kept"
    st["pick:%s:%s:%s" % (oclass, form, cls)] += 1
    # anchor guard (round 6 earlier / later words) on the opening statement only
    if how == "open":
        gw = FC.guard(T, a0, a1, {"c": [a1, a1]})
        if gw:
            st["drop:anchor_guard:" + gw] += 1
            return None
    # evidence
    aq = T[a0:a1]
    ev = None
    for cw in by_j[j]:
        if a0 <= cw["c"][0] and cw["c"][1] <= a1:
            ev = "cite:" + cw["key"]
            break
    if ev is None:
        dk = jf[j][0]
        sers = [s for _y, s in norm_dk(dk)]
        for s in sers:
            for cand_ev in ("name:" + s, "name:" + s.zfill(5)):
                if C6.ev_in(cand_ev, aq):
                    ev = cand_ev
                    break
            if ev:
                break
        if ev is None:
            st["drop:ev_not_in_anchor"] += 1
            return None
    low = BO.norm_ws(aq)
    if not any(q in low for q in FC.lean_anchor_cues()) and not any(q in low for q in FC.ALLP):
        st["drop:anchor_no_cue"] += 1
        return None
    cc = "lean" if any(q in low for q in FC.lean_anchor_cues()) else "tribunal"
    phrases = set(FC.TRIB_PHRASES[cls])
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
        if other_rx.search(zt) or BO.OWN_MIXED.search(zt) or FC.HYPH_PART.search(zt):
            scope = "unknown"
            st["scope_unknown_mixed_endzone"] += 1
    dsent = next((d[2] for d in disps if d[0] == q0), "")
    if scope == "all" and FC.HYPH_PART.search(dsent):
        scope = "unknown"
    if scope == "all" and kind in ("reversed", "vacated"):
        body = " ".join(T[a:b] for a, b, p in z["parts"] if BO.OKPART.get(p))
        if W.PARTIAL_HINT.search(body) or FC.PARTIAL_X.search(body):
            scope = "unknown"
            st["scope_unknown_partial_hint"] += 1
    am = BO.ACT.search(dsent)
    if am and (BO.own_disposition(dsent, am.start()) or FL.COND.search(dsent[:am.start()])):
        st["drop:disposition_not_own"] += 1
        return None
    if BO.other_dated(dsent, int(F.date[j])):
        st["drop:disposition_dated_otherwise"] += 1
        return None
    apart = "headmatter" if how == "head" else "majority"
    st["rows"] += 1
    st["rows:%s:%s:%s:%s:%s:%s" % (oclass, form, cls, how, kind, scope)] += 1
    return {"rule": "below:fedcir12_af%s_%s_%s" % (form, cls, how), "table": "history", "claim": "-", "by": n,
            "target": j, "kind": kind, "scope": scope, "disp": [q0, q1], "anchor": [a0, a1], "anchor_part": apart,
            "ev": ev, "part": part, "text": "by",
            "note": "%s|%s|cap%d|gap%dd|A|fedcir12 af %s %s %s %s cue=%s" % (cls, dhow, cap, gap, form, how, v, oclass,
                                                                       cc),
            "oclass": oclass, "base_rows": base}


def run_shard(path):
    if "based" not in G:
        FC.init()
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    st = collections.Counter()
    F = BO.G["F"]
    pend = []
    for n, g in L.decisions(path):
        if not g["cw"] or int(F.court[n]) != 520:
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
    want = set()
    for n, g, c in pend:
        want.add(n)
        want.update(c[0].keys())
        want.update(b[1] for b in G["brows"].get(n, []))
    texts = L.fetch_texts(sorted(want)) if pend else {}
    rows, pairs_out = [], []
    for n, g, c in pend:
        if n not in texts:
            st["drop:no_text"] += 1
            continue
        T = L.norm(texts[n][1])
        TJS = {x: texts.get(x, ("", ""))[1] for x in want}
        try:
            r = finish(n, g, T, TJS, c, st, pairs_out)
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
    with open(os.path.join(WORK, tag + ".pairs.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for p in pairs_out:
            f.write("\t".join(map(str, p)) + NL)
    with open(os.path.join(WORK, tag + ".stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    return tag, len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--tag", default="a1")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    FL.WORK = WORK
    paths = [p for p in L.shards() if os.path.basename(p).startswith(("cafc.", "federal-special.0"))]
    paths.sort(key=os.path.getsize, reverse=True)
    if a.cmd == "run":
        for tag, k in L.pmap(run_shard, paths, procs=a.procs, initializer=FC.init):
            print(tag, k, flush=True)
    tot = collections.Counter()
    rows, prs = [], []
    for p in sorted(paths):
        tag = os.path.basename(p)[:-len(".jsonl.gz")]
        rp = os.path.join(WORK, tag + ".rows.jsonl")
        if os.path.exists(rp):
            rows += [l for l in open(rp, encoding="utf-8") if l.strip()]
            prs += [l for l in open(os.path.join(WORK, tag + ".pairs.tsv"), encoding="utf-8") if l.strip()]
            tot.update(json.load(open(os.path.join(WORK, tag + ".stats.json"))))
    with open(os.path.join(HERE, "rows_%s.jsonl" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        f.writelines(rows)
    with open(os.path.join(HERE, "work", "pairs_%s.tsv" % a.tag), "w", encoding="utf-8", newline=NL) as f:
        f.write("acting\tj\tcls\tverdict\tpick\tbase_class\tbase\n")
        f.writelines(prs)
    json.dump(dict(sorted(tot.items())), open(os.path.join(HERE, "link_stats_%s.json" % a.tag), "w"), indent=1)
    print("rows", len(rows))


if __name__ == "__main__":
    main()
