"""fjc10 linker: rule N (named-own / one-side captions with the identity of the ruling under review), on top of the
round-9 build v9c (round 6 below_other, fjc8 F1, fjc9 W and J).

    python -X utf8 fjc10_link.py base                     -> work/base_by_trial.json (acting nodes of v9c with a
                                                             review-kind row on a trial / bankruptcy decision)
    python -X utf8 fjc10_link.py run [--procs 8] [--tag n1] -> work/link/<shard>.rows.jsonl, rows_<tag>.jsonl, stats
    python -X utf8 fjc10_link.py pairs PAIRS.tsv OUT.tsv    -> diagnosis on given (district, appellate) pairs (the
                                                             same code path, per pair: the step that drops it)

Reads only the round-6 cache, graph/nodes.tsv, court facts, decision texts (git) and the v9c history table. No key,
no list of cases.

Acting decision D: a federal court of appeals opinion with no v9c review-kind row on a trial / bankruptcy decision and
no round-6 below_other row on one (as F1 / W). Candidates J: cited decisions of a district court of D's circuit, 0..6
years before D. If any J has D's caption (round 6 cap 2) the opinion is left to round 6 / F1 / W / J (no row here).

Rule N: J's caption differs from D's title (cap 0 or 1), and the ruling's identity is established at the citation
level (DESIGN10 brief move 3 (a)/(b)):
  name   the case name printed immediately before J's citation is J's own caption (every side of the printed name
         shares a word with J's caption: equal, a common prefix of >= 4 letters, or similarity >= 0.8), not another
         case's name;  [a citation with another case's name before it never qualifies]
  ties   of the ruling to this appeal, at least one of:
         H  head-matter caption: each side of J's caption shares a distinctive word with D's own head-matter caption
            block (the party lines before the docket line): consolidated appeals, parties listed in full;
         K  docket: J's docket number (year + serial) is printed in D's text;
         U  district judge: J's author ("X, District Judge") is named in D's text as a judge ("Judge X", "X, J.",
            "Honorable ... X"), outside D's own panel lines;
         T  date: J's decision date is printed in D's text ("April 18, 1978").
  N-named (named-own): name and (H or K or U or T).
  N-one   (one side, bare citation, cap 1): K or U or T (H counts as a caption tie: label "h").
  Uniqueness: exactly one J of the window qualifies (else drop: several).
Citation marks: every citation of J is tested with round 6's eval_candidate at cap 2 (the caption test is the one
above): a history tag, signal, bracket-see, or round 6's earlier / interlocutory / later guard on any citation of J
drops the candidate (no guard exceptions). Anchor: round 6's own anchor of the citation when it passes; else F1's
find_anchor (court phrase <= 1,500 back / next sentence); else fjc9's W wide anchor; F1's guard_anchor on it.
Disposition: round 6's decide (direct review) + F1's sanity, ruling-type and dated-otherwise tests, mixed end zone.
"""
import argparse, collections, difflib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FJC9 = os.path.join(C2, "round9", "agents", "fjc9")
sys.path.insert(0, HERE)
sys.path.insert(0, FJC9)
import fjc9_link as W  # noqa: E402
from fjc9_link import FL, BO, L, C, diag  # noqa: E402

NL = chr(10)
WORK = os.path.join(HERE, "work", "link")
G = {}
STOP = set("""the and of for in on at to by with from inc corp co ltd llc lp plc company corporation incorporated limited
et al ex rel re matter estate united states america usa state people commonwealth city county town village
plaintiff plaintiffs defendant defendants appellant appellants appellee appellees petitioner respondent""".split())
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
          "December"]
MON3 = ["Jan", "Feb", "Mar", "Apr", "May", "June?", "July?", "Aug", "Sept?", "Oct", "Nov", "Dec"]
HEAD_STOP = re.compile(r"\bNos?\.\s*\d|\bUnited\s+States\s+Court\s+of\s+Appeals|\bCourt\s+of\s+Appeals|\bDocket\b|"
                       r"\bArgued\b|\bSubmitted\b|\bDecided\b", re.I)
JUDGE_LINE = re.compile(r"\b([A-Z][A-Za-z'’\-]{2,}),\s+(?:Senior\s+|Chief\s+)?(?:United\s+States\s+)?"
                        r"(?:District|Magistrate)\s+Judge", re.S)
DOCKET_NUM = re.compile(r"(\d{2,4})\s*[-–]?\s*(?:[A-Za-z]{1,6}\.?\s*[-–]?\s*)?(\d{2,6})")


def words(s):
    return [W2 for W2 in (re.sub(r"[^a-z0-9]", "", w.lower()) for w in re.findall(r"[A-Za-z0-9À-ÿ'’.\-]+", s or ""))
            if len(W2) >= 3 and W2 not in STOP]


def wmatch(a, b):
    if a == b:
        return True
    if len(a) >= 4 and len(b) >= 4 and a[:4] == b[:4] and (a.startswith(b[:len(a)]) or b.startswith(a[:len(b)])
                                                          or os.path.commonprefix([a, b]).__len__() >= 4):
        return True
    return len(a) >= 5 and len(b) >= 5 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.8


def side_hits(side_words, pool):
    return any(wmatch(a, b) for a in side_words for b in pool)


def printed_name(T, c0):
    """the case name printed immediately before a citation: (left words, right words) or None."""
    pre = T[max(0, c0 - 240):c0]
    if not re.search(r",\s*$", pre):
        return None
    pre = pre.rstrip()[:-1]
    m = None
    for m in re.finditer(r"\s(?:v\.?|vs\.?)\s", pre):
        pass
    if m is None:
        mi = re.search(r"\b(?:In\s+re|Ex\s+parte|Matter\s+of)\s+([^;:()\[\]]{2,120})$", pre)
        if mi:
            return words(mi.group(1))[:8], []
        return None
    left = pre[:m.start()]
    right = pre[m.end():]
    if re.search(r"[;()\[\]]", right) or len(right) > 160:
        return None
    # the left side: back to a boundary (; ( ) [ ] “ " or a sentence end "word. Capital")
    cut = max(left.rfind(x) for x in (";", "(", ")", "[", "]", "“", '"', "”"))
    for mm in re.finditer(r"[a-z]{3,}[.!?]\s+(?=[A-Z])", left):
        cut = max(cut, mm.end() - 1)
    left = left[cut + 1:]
    left = re.sub(r"^\s*(?:[Ss]ee\s+(?:also\s+)?|[Cc]f\.\s+|[Ii]n\s+)", "", left)
    lw, rw = words(left)[-6:], words(right)[:8]
    if not lw or not rw:
        return None
    return lw, rw


def name_is_j(pn, jname):
    if pn is None:
        return False
    jw = words(jname)
    lw, rw = pn
    return side_hits(lw, jw) and (not rw or side_hits(rw, jw))


def head_block(z):
    if not z or not z.get("head"):
        return ""
    h = z["head"][1][:6000]
    k = h.find("Head matter")
    if k >= 0:
        h = h[k + len("Head matter"):]
    m = HEAD_STOP.search(h)
    return h[:m.start()] if m else h[:1500]


def head_tie(hb, jname):
    """H: each side of J's caption shares a distinctive word with D's head-matter caption block."""
    hw = words(hb)
    if not hw:
        return False
    sides = [words(x) for x in BO.V_SPLIT.split(jname or "", maxsplit=1)]
    sides = [s for s in sides if s]
    if not sides:
        return False
    dist = lambda w: w.rstrip("s") not in FL.G["inst"] and FL.G["tokdf"].get(w.rstrip("s"), 0) <= FL.DISTINCT_DF
    return all(any(dist(a) and any(wmatch(a, b) for b in hw) for a in s) for s in sides) and \
        any(dist(a) for s in sides for a in s)


def j_facts(TJ):
    """(docket, author surname) from J's text (front matter + opening)."""
    dk = ""
    m = re.search(r'^docket:\s*"([^"]*)"', TJ[:3000], re.M)
    if m:
        dk = m.group(1)
    body = TJ[:12000]
    k = body.find("\n---", 4)
    if k > 0:
        body = body[k + 4:]
    jm = JUDGE_LINE.search(body[:8000])
    judge = jm.group(1) if jm else ""
    if judge.upper() in ("UNITED", "STATES", "THE", "CHIEF", "SENIOR"):
        judge = ""
    return dk, judge


def docket_tie(T, dk, d_docket):
    for m in DOCKET_NUM.finditer(dk or ""):
        yr, ser = m.group(1), m.group(2)
        if len(ser) < 3 and len(yr) < 3:
            continue
        rx = re.compile(r"(?<![\d-])0*%s\s*[-–]?\s*(?:[A-Za-z]{1,6}\.?\s*[-–]?\s*)?0*%s(?!\d)" % (re.escape(yr.lstrip("0") or "0"),
                                                                                         re.escape(ser.lstrip("0") or "0")))
        for mm in rx.finditer(T):
            if d_docket and mm.group(0).strip() in d_docket:
                continue
            return mm.group(0)
    return ""


def judge_tie(T, judge, captions):
    if not judge or len(judge) < 3:
        return ""
    jl = judge.lower()
    if any(jl in c.lower() for c in captions):
        return ""
    rx = re.compile(r"\b(?:Judge|Hon\.|Honorable)\s+(?:[A-Z][\w.'’]*\s+){0,3}%s\b|\b%s,\s+(?:J\.|C\.\s?J\.|U\.\s?S\.\s?D\.\s?J|"
                    r"(?:Senior\s+|Chief\s+)?(?:United\s+States\s+)?(?:District|Magistrate)\s+Judge)" % (judge, judge), re.I)
    for m in rx.finditer(T):
        if re.search(r"sitting\s+by\s+designation", T[m.start():m.end() + 160], re.I):
            continue
        return m.group(0)
    return ""


def date_tie(T, jdate):
    y, mo, d = jdate // 10000, (jdate // 100) % 100, jdate % 100
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    rx = re.compile(r"\b(?:%s|%s\.?)\s+%d,?\s+%d\b|\b%d\s+(?:%s|%s\.?),?\s+%d\b" % (
        MONTHS[mo - 1], MON3[mo - 1], d, y, d, MONTHS[mo - 1], MON3[mo - 1], y))
    m = rx.search(T)
    return m.group(0) if m else ""


def base_by_trial():
    BO.init()
    F = BO.G["F"]
    out = set()
    with open(os.path.join(C2, "round9", "stage", "v9c", "history.tsv"), encoding="utf-8") as f:
        for line in f:
            p = line.rstrip(NL).split("\t")
            if len(p) < 6 or p[4] not in FL.REVIEW_KINDS:
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
    os.makedirs(os.path.join(HERE, "work"), exist_ok=True)
    json.dump(sorted(out), open(os.path.join(HERE, "work", "base_by_trial.json"), "w"))
    print("v9c acting nodes with a trial-court review row:", len(out))


def init():
    FL.init()
    FL.G["based"] = set(json.load(open(os.path.join(HERE, "work", "base_by_trial.json"))))


GUARDS = ("earlier_proceeding", "interlocutory_ruling", "later_events")


def select(n, g, mrow, st, only_j=None):
    st = FL.Why(st, n)
    F, N = BO.G["F"], BO.G["N"]
    dc = int(F.court[n])
    d_date = int(F.date[n])
    if F.system(dc) != 0 or not d_date:
        return []
    if BO.court_at(dc, d_date)[1] != "A":
        return []
    st["opinions"] += 1
    if n in FL.G["based"]:
        st["drop:base_row"] += 1
        return []
    rows = BO.process(n, g, mrow, collections.Counter(), None)
    if any(BO.tphr(int(F.court[r["target"]]), int(F.date[r["target"]]))[1] in ("trial", "bankr") for r in rows):
        st["drop:r6_row"] += 1
        return []
    d_title = mrow[7] if mrow else ""
    d_all, d_sides = BO.caption(d_title)
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
        if cls != "trial" or not BO.circuit_ok(dc, jc, d_date):
            continue
        gap = BO.day(d_date) - BO.day(F.date[j])
        if gap < 0 or gap > BO.MAX_GAP_DAYS:
            continue
        by_j[j].append(cw)
        info[j] = (phrases, cls, BO.cap_rel(d_all, N.name(j), d_sides), gap)
    if not by_j:
        return []
    if any(v[2] >= 2 for v in info.values()):
        st["drop:cap2_exists"] += 1
        return []
    hb = head_block(g["z"])
    elig = []
    for j, cws in by_j.items():
        phrases, cls, cap, gap = info[j]
        jname = N.name(j)
        named_other = False
        for cw in cws:
            w0, wt = cw["w"]
            pn = printed_name(wt, cw["c"][0] - w0)
            if pn is not None and not name_is_j(pn, jname):
                named_other = True   # J's citation printed inside another case's name
        h = head_tie(hb, jname)
        if named_other or not (cap >= 1 or h):
            continue
        elig.append((j, h))
    if not elig:
        return []
    st["op_with_elig"] += 1
    if len(elig) > 1:
        st["several_elig"] += 1
    out = []
    for j, h in elig:
        phrases, cls, cap, gap = info[j]
        if later_same and int(F.date[j]) <= later_same < d_date:
            out.append((j, None, "reviewed_before"))
            continue
        whys, keep = [], []
        for cw in by_j[j]:
            ok, why, anchor, apart = BO.eval_candidate(cw, 2, phrases, True)
            whys.append(why)
            if BO.OKPART.get(cw["part"]) and (ok or why in ("no_court_phrase", "no_design_cue")):
                keep.append(dict(cw, r6ok=anchor if ok else None))
        bad = [w for w in whys if w in ("history_after_cite", "history_before_cite", "signal", "bracket_see") + GUARDS]
        if bad:
            out.append((j, None, "cite_marked:" + bad[0]))
            continue
        if not keep:
            out.append((j, None, "no_eligible_cite:" + ",".join(sorted(set(whys)))))
            continue
        out.append((j, (keep, phrases, cls, cap, gap, h), ""))
    return [out]


def ties_of(T, TJ, j, h, mrow):
    F, N = BO.G["F"], BO.G["N"]
    dk, judge = j_facts(TJ or "")
    d_docket = mrow[5] if mrow else ""
    ties, ev = [], []
    if h:
        ties.append("H")
    k = docket_tie(T, dk, d_docket)
    if k:
        ties.append("K")
        ev.append(k)
    u = judge_tie(T, judge, [N.name(j), mrow[7] if mrow else ""])
    if u:
        ties.append("U")
        ev.append(u)
    t = date_tie(T, int(F.date[j]))
    if t:
        ties.append("T")
        ev.append(t)
    return ties, ev


def finish(n, g, T, TJS, group, mrow, st):
    """group: [(j, cand | None, why)] (every eligible J of the opinion). The ruling under review: the eligible J
    with a tie (H / K / U / T); among several, the unique one with a date tie, else the unique one with a K / U / T
    tie; else none."""
    st0 = st
    tied = []
    for j, cand, why in group:
        if cand is None:
            continue
        keep, phrases, cls, cap, gap, h = cand
        ties, ev = ties_of(T, TJS.get(j, ""), j, h, mrow)
        if ties:
            tied.append((j, cand, ties, ev))
    if len(group) == 1:
        j, cand, why = group[0]
        if cand is None:
            FL.Why(st0, n, j)["drop:" + why] += 1
            return None
        if not tied:
            FL.Why(st0, n, j)["drop:no_tie"] += 1
            return None
        pick = tied[0]
    else:
        for j, cand, why in group:
            if cand is None:
                FL.Why(st0, n, j)["drop:several:" + why] += 1
        tt = [x for x in tied if "T" in x[2]]
        tx = [x for x in tied if set(x[2]) & {"K", "U", "T"}]
        if len(tt) == 1:
            pick = tt[0]
        elif not tt and len(tx) == 1:
            pick = tx[0]
        else:
            for j, cand, why in group:
                if cand is not None:
                    FL.Why(st0, n, j)["drop:several_unresolved"] += 1
            return None
        for j, cand, why in group:
            if j != pick[0] and cand is not None:
                FL.Why(st0, n, j)["drop:several_other_picked"] += 1
    j, (cws, phrases, cls, cap, gap, h), ties, tev = pick
    form = "s" if len(group) > 1 else ("h" if ties == ["H"] else "x")
    st = FL.Why(st0, n, j)
    F = BO.G["F"]
    z = g["z"]
    if not z:
        st["drop:no_zone"] += 1
        return None
    k = u = t = ""
    jkeys = FL.own_keys(j)
    anchor, why = None, "no_cite"
    for cw in cws:
        if cw.get("r6ok"):
            a0, a1 = cw["r6ok"]
            how = "r6"
        else:
            res, why = FL.find_anchor(T, cw, z, phrases, jkeys)
            if res is None:
                res, why = W.wide_anchor(T, cw, z, phrases, jkeys)
            if res is None:
                continue
            a0, a1, how = res
        gw = FL.guard_anchor(T, a0, a1, cw)
        if gw:
            why = gw
            continue
        anchor = (a0, a1, how, cw)
        break
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
    if am and (BO.own_disposition(dsent, am.start()) or FL.COND.search(dsent[:am.start()])):
        st["drop:disposition_not_own"] += 1
        return None
    ca = T[max(cw["s"][0] - 400, 0):cw["s"][1]]
    ta, td = FL.ruling_types(ca), FL.ruling_types(dsent)
    if ta and td and not (ta & td):
        st["drop:ruling_mismatch"] += 1
        return None
    if BO.other_dated(dsent, int(F.date[j])):
        st["drop:disposition_dated_otherwise"] += 1
        return None
    apart = BO.OKPART.get(cw["part"], cw["part"])
    tl = "".join(ties) or "-"
    st["rows"] += 1
    st["rows:%s:%s:%s:%s" % (form, tl, kind, scope)] += 1
    return {"rule": "below:fjc10_%s" % form, "table": "history", "claim": "-", "by": n, "target": j, "kind": kind,
            "scope": scope, "disp": [q0, q1], "anchor": [a0, a1], "anchor_part": apart,
            "ev": "cite:" + cw["key"], "part": part, "text": "by",
            "note": "%s|%s|cap%d|gap%dd|A|fjc10 %s %s ties=%s %s" % (cls, dhow, cap, gap, form, how, tl,
                                                                    "|".join(tev)[:120])}


def run_shard(path, only=None):
    if "F" not in BO.G or "based" not in FL.G:
        init()
    tag = os.path.basename(path)[:-len(".jsonl.gz")]
    meta = {int(p[0]): p for p in L.meta_rows(path[:-len(".jsonl.gz")] + ".meta.tsv.gz")}
    st = collections.Counter()
    pend = []
    for n, g in L.decisions(path):
        if not g["cw"] or (only is not None and n not in only):
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
    texts = L.fetch_texts([n for n, _, _ in pend] + [x[0] for _, _, c in pend for x in c]) if pend else {}
    rows = []
    for n, g, c in pend:
        if n not in texts:
            st["drop:no_text"] += 1
            continue
        T = L.norm(texts[n][1])
        TJS = {x[0]: texts.get(x[0], ("", ""))[1] for x in c}
        try:
            r = finish(n, g, T, TJS, c, meta.get(n), st)
        except Exception as ex:  # noqa: BLE001
            st["error_finish"] += 1
            if st["error_finish"] <= 3:
                sys.stderr.write("%s %d: %r\n" % (tag, n, ex))
            continue
        if r:
            rows.append(r)
    if only is not None:
        return rows, FL.G.pop("why", []), st
    with open(os.path.join(WORK, tag + ".rows.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    with open(os.path.join(WORK, tag + ".stats.json"), "w", encoding="utf-8", newline=NL) as f:
        json.dump(st, f)
    with open(os.path.join(WORK, tag + ".why.tsv"), "w", encoding="utf-8", newline=NL) as f:
        for n, j, k in FL.G.pop("why", []):
            f.write("\t".join((str(n), "-" if j is None else str(j), k)) + NL)
    return tag, len(rows)


def pairs(src, out):
    """diagnosis on (district, appellate) pairs: the rows / drop reasons of the appellate opinions."""
    init()
    ps = [l.rstrip(NL).split("\t") for l in open(src, encoding="utf-8")][1:]
    sidx = diag.shard_index()
    by = collections.defaultdict(set)
    for p in ps:
        if p[1].isdigit() and int(p[1]) in sidx:
            by[sidx[int(p[1])]].add(int(p[1]))
    res = {}
    tot = collections.Counter()
    for tag, apps in sorted(by.items()):
        rows, why, st = run_shard(os.path.join(L.CACHE, tag + ".jsonl.gz"), only=apps)
        tot.update(st)
        for n, j, k in why:
            res.setdefault((n, j), []).append(k)
            res.setdefault((n, None), []).append(k)
        for r in rows:
            res.setdefault((r["by"], r["target"]), []).append("ROW:%s:%s:%s:%s" % (r["rule"], r["kind"], r["scope"],
                                                                                 r["note"].split("ties=")[1][:40]))
    c = collections.Counter()
    with open(out, "w", encoding="utf-8", newline=NL) as f:
        for p in ps:
            d, a = int(p[0]), int(p[1])
            ks = res.get((a, d)) or ["(sel) " + ";".join(res.get((a, None), ["no_candidate"]))]
            f.write("\t".join([p[0], p[1], p[2], " ".join(ks)]) + NL)
            c[(p[2], ks[-1].split(":")[0] + ":" + ks[-1].split(":")[1] if ":" in ks[-1] else ks[-1])] += 1
    for k, v in sorted(c.items(), key=lambda x: -x[1])[:60]:
        print(v, k)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("args", nargs="*")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--tag", default="n1")
    a = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    FL.WORK = WORK
    if a.cmd == "base":
        base_by_trial()
        return
    if a.cmd == "pairs":
        pairs(a.args[0], a.args[1])
        return
    paths = [p for p in L.shards() if diag.APP_RX.match(os.path.basename(p)[:-len(".jsonl.gz")])]
    paths.sort(key=os.path.getsize, reverse=True)
    if a.cmd == "run":
        for tag, k in L.pmap(run_shard, paths, procs=a.procs, initializer=init):
            print(tag, k, flush=True)
    if a.cmd in ("run", "merge"):
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
