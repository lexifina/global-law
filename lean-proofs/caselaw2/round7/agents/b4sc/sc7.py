"""b4sc (round 7, B4 a + e): the decision under review in Supreme Court opinions that round 6 left unlinked.

    python -X utf8 sc7.py run [--procs 22]      -> work/rows_all.jsonl (with "_" diagnostics), work/diag.jsonl.gz,
                                                    work/run_stats.json
    python -X utf8 sc7.py explain <node>        what the rules see for one decision

Base: round 6's linker `round6/history/rules/below_sc/link.py` (imported, not edited; its helpers, regexes, index,
text store). `analyze7` is link.analyze with three changes, each a general rule (RULES7.md):
  R1 shared reporter page (B4 e): a citation key that several corpus decisions carry is re-pointed to the one
     decision whose caption shares a party token with the acting decision's caption, when exactly one does and it
     is not the index node (round 6 dropped the citation). Such rows carry `name:` evidence (the shared caption
     tokens) in an anchor quote that holds them, because the compact `cite:` key resolves to another node.
  R2 modal judgment line (B4 a): an opinion of the Court whose only judgment sentences are "must be / should be /
     will be reversed ..." takes its last such sentence of the last opinion-of-the-Court part as the disposition when
     "It is so ordered" follows within 600 characters or nothing but at most 600 characters of the part follows.
  R3 sole litigation decision (B4 a): when round 6's anchor rules give no row, the decision under review is taken
     from the citations alone: the one cited decision of the reviewed court (head-matter court line, else the
     courts the judgment names, else the highest court cited) whose caption shares a party token with the acting
     caption, cited without a signal / other case name / earlier-proceeding mark; the opinion cites no other
     decision of that court sharing a party token and no such decision of any court dated after it.
The weak anchor types of round 6 (A1w, HM_A1, A2, A3) are kept when they pass the same R3 test (sole + latest +
shared token) instead of round 6's W1 (judgment sentence names the court).
Round 6's guards stay: signal / other name / former-prior-first-earlier appeal / "see also" (anchor disqualifier),
rehearing-denied, later proceeding of the same court (on remand, en banc, rehearing ...), year printed, 4-year window
(6 before 1925), one decision under review per court, trial court only on direct review, syllabus cross-check,
the anchor (or the citation) before the judgment quote (no footnotes).
No answer-key file is read.
"""
import argparse, collections, gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
R6 = os.path.join(C2, "round6", "history")
SC6 = os.path.join(R6, "rules", "below_sc")
sys.path.insert(0, SC6)
sys.path.insert(0, R6)
import link  # noqa: E402  (round 6 below_sc linker; read-only)
import certify6 as C6  # noqa: E402  (string functions of the checker)

L = link.L
C = link.C
G = link.G
NL = chr(10)
WORK = os.path.join(HERE, "work")
WEAK = {"A1w", "HM_A1", "A2", "A3"}
MODAL_SUBJ = re.compile(r"\W{0,3}(?:(?:therefore|accordingly|consequently|it\s+follows\s+that|for\s+(?:these|the)\s+(?:reasons?|"
                        r"foregoing\s+reasons?)[^,]{0,40}),?\s+)?(?:the|its|their|each|both|said)\s+(?:\w+\s+){0,1}"
                        r"(?:judgments?|decrees?|orders?|convictions?)\b", re.I)
MODAL_SUBJ2 = re.compile(r"\b(?:the|its)\s+(?:\w+\s+)?(?:judgments?|decrees?)\b[^.;]{0,120}?\b(?:must|should|will)\s+be\s+"
                         r"(?:reversed|vacated|affirmed|modified)\b", re.I)
MODAL_BAD = re.compile(r"\b(?:contend|argue|urge|insist|claim|assert|if|unless|whether|would|could|might|unless|"
                       r"asks?|request|prays?|submit)\w*\b", re.I)
MODAL_AUX = re.compile(r"\b(?:must|should|will|ought\s+to|is\s+to)\s+be\b|\bmust\b|\bshould\b", re.I)


# ------------------------------------------------------------------------------------------------ R2
def read_disposition7(view, parts, disps):
    disp, why = link.read_disposition(view, parts, disps)
    if disp is not None or why != "disp_not_strong":
        return disp, why, False
    last = disps[-1]
    pa, pb = next((a, b) for a, b, p in reversed(parts) if a <= last["q"][0] < b)
    if (pa, pb) != (parts[-1][0], parts[-1][1]):
        return None, "disp_not_strong", False
    q0, q1 = last["q"]
    if link.WOULD.search(view[q0:q1]) or not MODAL_AUX.search(view[q0:q1]):
        return None, "disp_not_strong", False
    sent = view[q0:q1]
    if not (MODAL_SUBJ.match(sent) or MODAL_SUBJ2.search(sent)) or MODAL_BAD.search(sent):
        return None, "disp_not_strong", False
    so = link.SO_ORDERED.search(view, q1, min(pb, q1 + 600))
    rest = view[q1:pb].strip()
    para_end = re.match(r"[ \t]*(?:\n|$)", view[q1:q1 + 3]) is not None
    late = (q0 - pa) >= 0.65 * (pb - pa)
    if not (so or len(rest) <= 600 or (para_end and late)):
        return None, "disp_not_strong", False
    d2 = dict(last)
    d2["strong"] = True
    parts2 = [(a, b, p) for a, b, p in parts]
    disps2 = [d for d in disps if d is not last] + [d2]
    disps2.sort(key=lambda d: d["q"])
    disp, why = link.read_disposition(view, parts2, disps2)
    return disp, why, disp is not None


# ------------------------------------------------------------------------------------------------ helpers
def toks_of(title):
    return {t.lower().rstrip("s") for t in (C.name_tokens(title) | C.short_name_tokens(title))}


def title_of(x):
    t = G["titles"].get(x)
    if t is None:
        try:
            t = L.node_row(x)[6]
        except Exception:
            t = ""
        G["titles"][x] = t
    return t


def shared_tokens(x, toks_low):
    """Tokens (as printed in the target's caption, lower-cased compact, >= 3 chars) that the acting caption shares."""
    t = title_of(x)
    out = []
    for w in (C.name_tokens(t) | C.short_name_tokens(t)):
        if w.lower().rstrip("s") in toks_low:
            c = C6.compact(w)
            if len(c) >= 3 and c not in out:
                out.append(c)
    return sorted(out)


SIDE = re.compile(r"\s+vs?\.?\s+", re.I)
DISTINCT_DF = 5000
# a judgment sentence that is a condition or a party's statement, not the Court's act
DISP_COND = re.compile(r"\b(?:if|unless|whether)\b[^.;:]{0,80}?\b(?:is|are|be|will\s+(?:have\s+to\s+)?be|must\s+be|should\s+be)"
                       r"\s+(?:affirmed|reversed|vacated)\b|\b(?:contends?|argues?|urges?|insists?|asserts?)\b|"
                       r"\bstates?\s+that\b", re.I)
SIDE_PROC = re.compile(r"\bmandamus\b|\bprohibition\b", re.I)   # a side proceeding (writ to the court below)


def init7():
    link.init()
    if "tokdf" not in G:
        G["tokdf"] = json.load(open(os.path.join(WORK, "tokdf.json"), encoding="utf-8"))
        G["inst"] = set(json.load(open(os.path.join(WORK, "inst_tokens.json"), encoding="utf-8")))


def sides_of(title):
    return [toks_of(s) for s in SIDE.split(title, maxsplit=1)]


def cap_ok(x, toks_low, acting_title):
    """R3 caption test: the target's caption shares a distinctive party token with the acting caption (not an
    institutional token, printed in at most DISTINCT_DF titles), or shares a token on each named side (and, when the
    target names one side only, each named side of the acting caption shares one with it)."""
    t = title_of(x)
    tall = toks_of(t)
    shared = tall & toks_low
    if not shared:
        return False
    if any(w not in G["inst"] and G["tokdf"].get(w, 0) <= DISTINCT_DF for w in shared):
        return True
    tn = [s for s in sides_of(t) if s]
    if not tn or not all(s & toks_low for s in tn):
        return False
    if len(tn) >= 2:
        return True
    an = [s for s in sides_of(acting_title) if s]
    return bool(an) and all(s & tall for s in an)


def level(ci):
    _fed, tags, _c, _s, _tier, _n = ci
    if "TRIAL" in tags or (tags & {"TAX", "BANKR", "FEDOTHER"}):
        return 0
    return 3 if "HIGH" in tags else 2


def group_key(d):
    fed, tags, circ, state, _t, _n = d["ci"]
    return ("fed", (circ or d["court"]) if "FCOA" in tags else d["court"]) if fed else ("st", state)


# ------------------------------------------------------------------------------------------------ analyze7
def analyze7(n, text, date):
    F = G["F"]
    out = {"n": n, "date": date, "rows": [], "reason": None}
    body0 = 0
    fm = ""
    if text.startswith("---"):
        e = text.find(NL + "---", 3)
        if e >= 0:
            fm = text[:e]
            nl = text.find(NL, e + 4)
            body0 = nl + 1 if nl >= 0 else len(text)
    hw = C.hard_wrapped(text, body0)
    view = C.unwrap_view(text, body0) if hw else text
    pm, _ = (C.part_map2(text) if hw else C.part_map(text))
    op_parts = [(a, b, p.rstrip("~")) for a, b, p, _s in pm if p in ("majority", "perCuriam", "plurality", "majority~")]
    hm_parts = [(a, b) for a, b, p, _s in pm if p in ("headmatter", "headmatter~", "title")]
    if not op_parts:
        out["reason"] = "no_opinion_part"
        return out
    disps = link.find_dispositions(view, op_parts)
    disp, why, modal = read_disposition7(view, op_parts, disps)
    if disp is None:
        out["reason"] = why
        return out
    out["modal"] = int(modal)
    out["disp_text"] = disp["text"][:300]
    mt = re.search(r"^# (.+)$", text[body0:body0 + 3000], re.M)
    title = mt.group(1).strip() if mt else ""
    toks = C.name_tokens(title) | C.short_name_tokens(title)
    mp = re.search(r"^parties:\s*(.*)$", fm, re.M)
    if mp:
        toks |= C.name_tokens(mp.group(1))
    toks_low = {t.lower().rstrip("s") for t in toks}
    hm_specs = []
    hm_flags = set()
    for a, b in hm_parts:
        for m in link.HM_LINE.finditer(view, a, b):
            if len(m.group(0).strip()) > 300:
                continue
            what = m.group("what").upper()
            ct = m.group("court")
            for rx, rep in link.OCR_FIX:
                ct = rx.sub(rep, ct)
            if what.startswith("CERTIF") or "QUESTION" in what:
                hm_flags.add("certificate")
                continue
            if re.search(r"before\s+judgment", m.group(0), re.I):
                hm_flags.add("before_judgment")
            ph = [p for p in link.phrases(ct) if p[2] not in ("BELOW", "ENBANC")]
            if ph:
                hm_specs.append(ph)
    cands = {}
    unresolved = []
    zones = [(a, b, "headmatter") for a, b in hm_parts] + op_parts
    rx = link.r6cite.WIDE_RX if link.r6cite else C.CITE_RX
    for a, b, part in zones:
        for m in rx.finditer(view, a, b):
            j, ikey, rkey, form = link.resolve(m)
            if j is None:
                if form:
                    unresolved.append((m.start(), m.end(), part))
                continue
            rp = None
            if ikey in G["multi"]:
                share = [x for x in G["multi"][ikey] if link.name_share(x, toks_low)]
                if share == [j]:
                    pass
                elif len(share) == 1 and share[0] != n and int(F.court[share[0]]) != L.SCOTUS2 and \
                        cap_ok(share[0], toks_low, title):
                    rp = j            # R1: re-pointed from the index node j
                    j = share[0]
                else:
                    out.setdefault("collisions", []).append([ikey, j, share])
                    continue
            jc = int(F.court[j])
            if jc == L.SCOTUS2 or j == n:
                continue
            jd = int(F.date[j])
            if not jd or jd >= date or date - jd > (link.WINDOW_MODERN if date >= 19250000 else link.WINDOW):
                continue
            my = re.match(r"(?:,\s*\d[\d\-–, n.]*)?\s*\((?:[^()]{0,24}\s)?(\d{4})\)", view[m.end():m.end() + 40])
            if my and abs(int(my.group(1)) - jd // 10000) > 1:
                continue
            ci = link.court_info(jc)
            s0, s1 = C.sentence_span(view, m.start(), m.end())
            s0, s1 = max(s0, a), min(s1, b)
            prefix = view[s0:m.start()]
            cite_sentence = not re.search(r"\b[a-z]{4,}\b", link.NOT_CITE_WORD.sub("", prefix))
            after_end = bool(re.search(r"[.!?][”\"’)]*\s+$", view[max(s0, m.start() - 8):m.start()]))
            ctx0 = s0
            if cite_sentence:
                ps = link.prev_sentence(view, s0, a)
                if ps:
                    ctx0 = ps[0]
            st0 = m.start()
            mm = re.search(r"((?:\d{1,4}\s+[A-Z][^,;]{1,40}\d\s*(?:\(\d{4}\))?,\s*)+)$", view[max(s0, st0 - 120):st0])
            if mm:
                st0 = max(s0, st0 - 120) + mm.start(1)
            named, sig_at = link.name_class(view, s0, st0, toks_low)
            sig = bool(link.SIGNAL.search(view[max(s0, sig_at - 30):sig_at]))
            sent = view[ctx0:s1]
            disq = bool(link.DISQ.search(sent)) or bool(re.search(r"\bsee\s+also\b", sent, re.I))
            phs = link.phrases(view, ctx0, s1)
            before = [p for p in phs if p[1] <= m.start()]
            gov = before[-1] if before else (phs[0] if phs else None)
            strength = link.ph_match(gov, ci) if gov else 0
            any_strength = max((link.ph_match(p, ci) for p in phs), default=0)
            typ = None
            rehden = bool(link.REHDEN.search(view[max(ctx0, m.start() - 170):m.start()]))
            if rehden:
                pass
            elif part == "headmatter":
                line0 = view.rfind(NL, a, m.start()) + 1
                line0 = max(line0, a)
                line1 = view.find(NL, m.end(), b)
                line1 = b if line1 < 0 else line1
                ms = link.SYL_LINE.match(view[line0:line1])
                if ms and line0 + ms.start("v") >= m.end() and len(re.findall(r"\b[a-z]{4,}\b", ms.group("cites"))) <= 3:
                    typ = "HM_SYL"
                    out.setdefault("syl", {})[j] = ms.group("v").lower()
                elif link.REPORTED.search(view[max(line0, m.start() - 200):m.start()]):
                    typ = "HM_REP"
                elif strength:
                    typ = "HM_A1"
            else:
                if strength:
                    typ = "A1"
                elif any_strength:
                    typ = "A1w"
                elif link.REPORTED.search(view[max(ctx0, m.start() - 200):m.start()]) or \
                        re.search(r"sub\s+nom|decision\s+below|opinion\s+below|judgment\s+below", sent, re.I):
                    typ = "A2"
            occ = {"c": (m.start(), m.end()), "s": (s0, s1), "ctx0": ctx0, "part": part, "typ": typ, "sig": sig,
                   "bare": cite_sentence or after_end, "named": named, "disq": disq, "key": rkey, "ikey": ikey,
                   "form": form, "gov": (gov[2], gov[3], gov[4]) if gov else None, "lo": a, "hi": b,
                   "rehden": rehden, "rp": rp, "any": any_strength}
            d = cands.setdefault(j, {"j": j, "court": jc, "date": jd, "ci": ci, "occ": []})
            d["occ"].append(occ)
    if not cands:
        out["reason"] = "no_lower_cite"
        return out
    out["cands"] = [{"j": d["j"], "court": d["court"], "date": d["date"], "rp": [o["rp"] for o in d["occ"] if o["rp"]][:1],
                     "occ": [(o["c"][0], o["part"], o["typ"], int(o["sig"]), o["named"], int(o["disq"]), o["gov"])
                             for o in d["occ"]][:6]} for d in cands.values()]
    op_a = op_parts[0][0]
    ph_end = None
    for a, b, _p in op_parts:
        m = link.PH_END.search(view, a, b)
        if m:
            ph_end = C.sentence_span(view, m.start(), m.end())[1]
            break
    out["ph_end"] = ph_end
    if ph_end is not None:
        for d in cands.values():
            for o in d["occ"]:
                if o["typ"] is None and o["bare"] and o["part"] != "headmatter" and o["c"][0] < ph_end and \
                        not o["rehden"]:
                    w0 = max(o["lo"], o["s"][0] - 700)
                    if any(link.ph_match(p, d["ci"]) == 2 for p in link.phrases(view, w0, o["c"][0])):
                        o["typ"] = "A3"
    hm_only = [(a, b) for a, b, p, _s in pm if p in ("headmatter", "headmatter~")]
    ctx = {"view": view, "disp": disp, "ph_end": ph_end, "op_parts": op_parts, "hm_parts": hm_parts,
           "hm_only": hm_only,
           "hm_specs": hm_specs, "hm_flags": hm_flags, "toks_low": toks_low, "unresolved": unresolved, "op_a": op_a,
           "date": date, "n": n, "out": out, "modal": modal, "title": title}
    rows, reasons = strict(cands, ctx)
    if not rows:
        lrows, lreason = loose(cands, ctx)
        rows = lrows
        if not rows:
            reasons.append(lreason)
    out["rows"] = rows
    out["reasons"] = reasons
    if not rows:
        out["reason"] = reasons[0] if reasons else "no_row"
    return out


def clean(o):
    return not o["sig"] and o["named"] != "other" and not o["disq"] and not o["rehden"]


def good(o):
    return bool(o["typ"]) and clean(o)


def later_flags(view, tt, an, ph_end, unresolved, op_a):
    """Round 6's later-proceeding test (link.analyze), for target tt and its anchors an."""
    flags = []
    zone_an = [o for o in an if o["part"] != "headmatter" and (ph_end is None or o["c"][0] < ph_end)]
    if zone_an and ph_end is not None:
        z0 = max(o["s"][1] for o in zone_an)
        for (u0, u1, upart) in unresolved:
            if upart == "headmatter" or not (z0 <= u0 < ph_end):
                continue
            us0, us1 = C.sentence_span(view, u0, u1)
            if link.SIGNAL.search(view[max(us0, u0 - 30):u0]) or link.NAME_BEFORE.search(view[max(us0, u0 - 170):u0]):
                continue
            if re.search(r"\d\s*(?:\(\d{4}\))?,\s*$", view[max(us0, u0 - 14):u0]):
                continue
            ups = link.prev_sentence(view, us0, op_a)
            if any(link.ph_match(p, tt["ci"]) == 2 for p in link.phrases(view, ups[0] if ups else us0, us1)):
                flags.append("later_unresolved")
                break
        for m in link.LATER.finditer(view, z0, ph_end):
            ms0, ms1 = C.sentence_span(view, m.start(), m.end())
            if any(link.ph_match(p, tt["ci"]) == 2 for p in link.phrases(view, ms0, ms1)):
                flags.append("later_marker")
                break
    return flags


def strict(cands, ctx):
    """link.analyze's selection, unchanged (on the R1/R2 inputs); weak types are tagged for the R3 test later."""
    view, disp, ph_end = ctx["view"], ctx["disp"], ctx["ph_end"]
    op_parts, hm_parts, hm_specs, hm_flags = ctx["op_parts"], ctx["hm_parts"], ctx["hm_specs"], ctx["hm_flags"]
    toks_low, date, n = ctx["toks_low"], ctx["date"], ctx["n"]

    def anchors(d, zone_only):
        r = [o for o in d["occ"] if good(o)]
        if zone_only and ph_end is not None:
            r = [o for o in r if o["part"] == "headmatter" or o["c"][0] < ph_end]
        return r
    J = [d for d in cands.values() if anchors(d, False)]
    if not J:
        return [], ["no_anchor"]
    JZ = [d for d in J if anchors(d, True)]
    in_zone = bool(JZ)
    if in_zone:
        J = JZ
    if "certificate" in hm_flags and not hm_specs:
        return [], ["certificate"]
    if hm_specs:
        JR = [d for d in J if any(link.spec_match(s, d["ci"]) == 2 for s in hm_specs) or
              ("before_judgment" in hm_flags and "DIST" in d["ci"][1])]
        if not JR:
            return [], ["court_not_head_matter"]
    else:
        JR = [d for d in J if not (d["ci"][1] & {"TAX", "BANKR", "FEDOTHER"})]
        if not JR:
            return [], ["no_reviewable_court"]
    kinds = {}
    whys = []
    for d in JR:
        k, why = link.kind_for(view, disp, d["ci"])
        if k:
            kinds[d["j"]] = k
        else:
            whys.append(why)
    JK = [d for d in JR if d["j"] in kinds]
    if not JK:
        return [], [whys[0] if whys else "disp_unusable"]
    disp_specs = [c[0] for c in disp["clauses"] if c[0]]
    src = "hm"
    if not hm_specs:
        op_has_coa = any(link.COA_WORD.search(view, a, b) for a, b, _p in op_parts)
        direct_cue = any(link.DIRECT.search(view, a, min(b, a + 6000)) for a, b, _p in op_parts) or \
            any(link.DIRECT.search(view, a, b) for a, b in hm_parts)
        named_ok = [d for d in JK if any(link.spec_match(s, d["ci"]) == 2 for s in disp_specs)]
        if named_ok:
            src = "disp"
            JK = named_ok
            if max(level(d["ci"]) for d in JK) == 0:
                if (op_has_coa and not direct_cue) or any(level(d["ci"]) > 0 for d in J):
                    return [], ["trial_not_direct"]
            else:
                JK = [d for d in JK if level(d["ci"]) > 0]
        else:
            src = "inferred"
            if max(level(d["ci"]) for d in JK) == 0:
                if not direct_cue or op_has_coa:
                    return [], ["trial_not_direct"]
            else:
                JK = [d for d in JK if level(d["ci"]) > 0]
    groups = collections.defaultdict(list)
    for d in JK:
        groups[group_key(d)].append(d)
    if len(groups) > 1 and len(hm_specs) < 2 and ph_end is not None:
        strong = {k: ds for k, ds in groups.items()
                  if any(o["typ"] in ("A1", "HM_A1", "HM_SYL", "HM_REP") and (o["part"] == "headmatter" or o["c"][0] < ph_end)
                         for d in ds for o in anchors(d, True))}
        if len(strong) == 1:
            groups = strong
    if len(groups) > 1 and len(hm_specs) < 2:
        return [], ["several_courts"]
    multi = len(groups) > 1
    rows, reasons = [], []
    for key, ds in groups.items():
        if key[0] == "st":
            topl = max(level(d["ci"]) for d in ds)
            ds = [d for d in ds if level(d["ci"]) == topl]
        ds.sort(key=lambda d: d["date"])
        t = ds[-1]
        targets = [t]
        an_t = anchors(t, in_zone)
        bad_tie = False
        for d in ds[:-1]:
            comp = False
            for o in anchors(d, in_zone):
                for ot in an_t:
                    if o["s"] == ot["s"] and o["part"] == ot["part"]:
                        x0, x1 = sorted((o["c"], ot["c"]))
                        between = view[x0[1]:x1[0]]
                        if len(between) <= 90 and not link.COMPANION_BAD.search(between):
                            comp = True
            if comp:
                targets.append(d)
            elif d["date"] == t["date"]:
                bad_tie = True
        if bad_tie:
            reasons.append("same_date_ambiguous")
            continue
        later = [d for d in J if d["date"] > t["date"] and d["ci"][0] == t["ci"][0] and
                 (d["court"] == t["court"] or (level(d["ci"]) < level(t["ci"]) and (d["ci"][0] or d["ci"][3] == t["ci"][3])))]
        if later:
            reasons.append("later_decision_cited")
            continue
        for tt in targets:
            an = sorted(anchors(tt, in_zone), key=lambda o: (link.TYP_ORDER[o["typ"]], o["c"][0]))
            flags = later_flags(view, tt, an, ph_end, ctx["unresolved"], ctx["op_a"])
            kind, scope, dq = kinds[tt["j"]]
            all_st = set()
            for c in disp["clauses"]:
                all_st |= c[1]
            if (multi or len(targets) > 1) and scope == "all" and len(all_st & {"affirm", "revers", "vacat", "modif"}) >= 2:
                scope = "unknown"
            syl = ctx["out"].get("syl", {}).get(tt["j"])
            if syl:
                sst = link.stems(syl)
                if link.CUE_OF[kind] not in sst and not ({link.CUE_OF[kind]} | sst <= {"revers", "vacat"}):
                    reasons.append("syllabus_conflict")
                    continue
            row = link.build_row(n, view, tt, an, kind, scope, dq, flags, src, in_zone, multi or len(targets) > 1, date)
            if isinstance(row, str):
                reasons.append(row)
                continue
            if row["_flags"]:
                reasons.append("later_" + row["_flags"][0].split("_")[-1])
                continue
            share = link.name_share(tt["j"], toks_low)
            row["_share"] = int(share)
            if not share and (date < 19000000 or row["_typ"] in WEAK):
                reasons.append("no_name_" + ("pre1900" if date < 19000000 else row["_typ"].lower()))
                continue
            if not in_zone and ph_end is not None and (row["_typ"] != "A1" or src == "inferred"):
                reasons.append("outside_history")
                continue
            row["_path"] = "strict"
            row["_ntargets"] = len(targets)
            finish(row, tt, cands, ctx)
            rows.append(row)
    return rows, reasons


def sole_latest(t, cands, toks_low):
    """R3: no other cited decision of t's court group sharing a party token; none of any court dated after t."""
    lit = [d for d in cands.values() if link.name_share(d["j"], toks_low)]
    same = [d for d in lit if d["j"] != t["j"] and group_key(d) == group_key(t) and level(d["ci"]) == level(t["ci"])]
    later = [d for d in lit if d["j"] != t["j"] and d["date"] > t["date"]]
    return (not same), (not later)


def finish(row, t, cands, ctx):
    """Diagnostics used by the post-filter: R3 test, R1 flag, footnote test."""
    view = ctx["view"]
    s_ok, l_ok = sole_latest(t, cands, ctx["toks_low"])
    row["_sole"] = int(s_ok)
    row["_latest"] = int(l_ok)
    row["_cap"] = int(cap_ok(t["j"], ctx["toks_low"], ctx["title"]))
    row["_rp"] = int(any(o["rp"] for o in t["occ"]))
    row["_modal"] = int(ctx["modal"])
    row["_hm_specs"] = int(bool(ctx["hm_specs"]))
    sp = row["anchor"] or [o["s"][0] for o in t["occ"]][:1] + [o["s"][1] for o in t["occ"]][:1]
    row["_side"] = int(bool(SIDE_PROC.search(view[sp[0]:sp[1]]))) if len(sp) == 2 else 0
    row["_dcond"] = int(bool(DISP_COND.search(view[row["disp"][0]:row["disp"][1]])))
    q0 = row["disp"][0]
    if row["anchor"] is not None:
        row["_before_disp"] = int(row["anchor"][0] < q0 or row["anchor_part"] == "headmatter")
    else:
        pos = [o["c"][0] for o in t["occ"] if o["part"] != "headmatter"]
        row["_before_disp"] = int(bool(pos) and min(pos) < q0) or int(any(o["part"] == "headmatter" for o in t["occ"]))
    if row["_rp"]:
        name_ev(row, t, ctx)


def name_ev(row, t, ctx):
    """R1: `name:` evidence = the target-caption tokens the acting caption shares, inside an anchor quote."""
    view = ctx["view"]
    toks = shared_tokens(t["j"], ctx["toks_low"])
    row["_name_toks"] = toks
    if not toks:
        row["_name_fail"] = "no tokens"
        return

    def ok(a0, a1):
        q = L.norm(view[a0:a1])
        ql = link.lower(q)
        if not link.has_cue(q) or link.has_disq(q):
            return None
        present = [x for x in toks if (" " + x + " ") in C6.words(q)]
        return present or None
    cand = []
    if row["anchor"] is not None:
        cand.append((row["anchor"][0], row["anchor"][1], row["anchor_part"]))
        a0, a1 = row["anchor"]
        lo = next((a for a, b, p in ctx["op_parts"] if a <= a0 < b), None)
        if lo is not None:
            for _ in range(3):
                pv = link.prev_sentence(view, a0, lo)
                if not pv or row["anchor"][1] - pv[0] > 1400:
                    break
                a0 = pv[0]
                cand.append((a0, row["anchor"][1], row["anchor_part"]))
    for a, b in ctx["hm_only"]:
        seg = view[a:b]
        pos = 0
        lines = []
        for ln in seg.split(NL):
            lines.append((a + pos, a + pos + len(ln), ln))
            pos += len(ln) + 1
        for i, (l0, l1, ln) in enumerate(lines):
            if not ln.strip():
                continue
            if not any((" " + x + " ") in C6.words(ln) for x in toks):
                continue
            for k in range(i, min(len(lines), i + 8)):
                e = lines[k][1]
                if e - l0 > 700:
                    break
                cand.append((l0, e, "headmatter"))
            break
    for a0, a1, part in cand:
        a0, a1 = link.trim(view, a0, a1)
        if a1 <= a0:
            continue
        pres = ok(a0, a1)
        if pres:
            row["anchor"] = [a0, a1]
            row["anchor_part"] = part
            row["ev"] = "name:" + " ".join(pres)
            row["_ev_cite"] = row.get("_ev_cite") or ""
            return
    row["_name_fail"] = "no anchor with the tokens"


def loose(cands, ctx):
    """R3 as a selection rule when round 6's anchors give no row."""
    view, disp, ph_end = ctx["view"], ctx["disp"], ctx["ph_end"]
    op_parts, hm_parts, hm_specs, hm_flags = ctx["op_parts"], ctx["hm_parts"], ctx["hm_specs"], ctx["hm_flags"]
    toks_low, date, n = ctx["toks_low"], ctx["date"], ctx["n"]
    q_final = disp["final"]["q"][0]
    if "certificate" in hm_flags and not hm_specs:
        return [], "L_certificate"

    def occs(d):
        # before the judgment quote (or head matter); else a bare citation after it (CAP prints the footnotes
        # after the opinion: "1 229 F. 2d 592.")
        r = [o for o in d["occ"] if clean(o) and (o["part"] == "headmatter" or o["c"][0] < q_final)]
        if not r:
            r = [dict(o, fn=1) for o in d["occ"] if clean(o) and o["bare"] and o["part"] != "headmatter"]
        return r
    lit = [d for d in cands.values() if cap_ok(d["j"], toks_low, ctx["title"]) and occs(d)]
    if not lit:
        return [], "L_no_shared_caption"
    if hm_specs:
        R = [d for d in lit if any(link.spec_match(s, d["ci"]) == 2 for s in hm_specs) or
             ("before_judgment" in hm_flags and "DIST" in d["ci"][1])]
        src = "hm"
        if not R:
            return [], "L_court_not_head_matter"
    else:
        R = [d for d in lit if not (d["ci"][1] & {"TAX", "BANKR", "FEDOTHER"})]
        disp_specs = [c[0] for c in disp["clauses"] if c[0]]
        named = [d for d in R if any(link.spec_match(s, d["ci"]) == 2 for s in disp_specs)]
        src = "disp" if named else "inferred"
        if named:
            R = named
        if not R:
            return [], "L_no_reviewable_court"
    top = max(level(d["ci"]) for d in R)
    if top == 0:
        op_has_coa = any(link.COA_WORD.search(view, a, b) for a, b, _p in op_parts)
        direct_cue = any(link.DIRECT.search(view, a, min(b, a + 6000)) for a, b, _p in op_parts) or \
            any(link.DIRECT.search(view, a, b) for a, b in hm_parts)
        if op_has_coa or not direct_cue or any(level(d["ci"]) > 0 for d in lit):
            return [], "L_trial_not_direct"
    R = [d for d in R if level(d["ci"]) == top]
    gk = {group_key(d) for d in R}
    if len(gk) != 1:
        return [], "L_several_courts"
    if len(R) != 1:
        return [], "L_several_decisions_of_the_court"
    t = R[0]
    s_ok, l_ok = sole_latest(t, cands, toks_low)
    if not s_ok:
        return [], "L_not_sole"
    if not l_ok:
        return [], "L_later_litigation_decision"
    k, why = link.kind_for(view, disp, t["ci"])
    if not k:
        return [], "L_" + why
    kind, scope, dq = k
    syl = ctx["out"].get("syl", {}).get(t["j"])
    if syl:
        sst = link.stems(syl)
        if link.CUE_OF[kind] not in sst and not ({link.CUE_OF[kind]} | sst <= {"revers", "vacat"}):
            return [], "L_syllabus_conflict"
    an = occs(t)

    def rank(o):
        if o.get("fn"):
            return (4, o["c"][0])
        if o["part"] == "headmatter":
            return (0, o["c"][0])
        if ph_end is not None and o["c"][0] < ph_end:
            return (1, o["c"][0])
        return (2 if o["any"] else 3, o["c"][0])
    an.sort(key=rank)
    zone = rank(an[0])[0]
    if ph_end is not None and zone >= 2:
        # outside the procedural history: the citation's sentence (or the one before) must at least speak of a court
        # that may be the target's
        if zone == 3:
            return [], "L_outside_history_no_court"
    sub = {0: "hm", 1: "zone", 2: "body", 3: "body", 4: "fn"}[zone] if ph_end is not None else \
        {0: "hm", 4: "fn"}.get(zone, "nozone")
    for o in an:
        o["typ"] = o["typ"] or "L"
    flags = later_flags(view, t, [o for o in an], ph_end, ctx["unresolved"], ctx["op_a"])
    if flags:
        return [], "L_" + flags[0]
    an2 = [dict(o, typ="HM_SYL" if o["typ"] == "HM_SYL" else ("HM_REP" if o["typ"] == "HM_REP" else "L")) for o in an]
    row = link.build_row(n, view, t, an2, kind, scope, dq, flags, src, ph_end is not None, False, date)
    if isinstance(row, str):
        return [], "L_" + row
    row["rule"] = "below:sc_l_" + sub
    row["_typ"] = "L"
    row["_path"] = "loose"
    row["_share"] = 1
    row["_sub"] = sub
    row["_ntargets"] = 1
    finish(row, t, cands, ctx)
    return [row], None


# ------------------------------------------------------------------------------------------------ driver
def work_run(path):
    init7()
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            try:
                d = analyze7(r["n"], r["text"], r["date"])
            except Exception as ex:
                d = {"n": r["n"], "date": r["date"], "rows": [],
                     "reason": "error:" + type(ex).__name__ + ":" + str(ex)[:80]}
            d["type"] = r["type"]
            d["len"] = len(r["text"])
            out.append(d)
    return out


def run(procs):
    os.makedirs(WORK, exist_ok=True)
    rows = []
    st = collections.Counter()
    with gzip.open(os.path.join(WORK, "diag.jsonl.gz"), "wt", encoding="utf-8", newline=NL, compresslevel=3) as fd:
        for res in L.pmap(work_run, link.shard_files(), procs=procs):
            for d in res:
                st["decisions"] += 1
                if d["rows"]:
                    st["decisions_with_row"] += 1
                else:
                    r = d["reason"] or "?"
                    st["no_row:" + (r.split(":")[0] + ":" + r.split(":")[1] if r.startswith("error") else r)] += 1
                rows.extend(d["rows"])
                fd.write(json.dumps(d, ensure_ascii=False, default=str) + NL)
    rows.sort(key=lambda r: (r["by"], r["target"]))
    with open(os.path.join(WORK, "rows_all.jsonl"), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    st["rows"] = len(rows)
    json.dump(st, open(os.path.join(WORK, "run_stats.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("node", nargs="?")
    ap.add_argument("--procs", type=int, default=22)
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.procs)
    elif a.cmd == "explain":
        init7()
        n = int(a.node)
        sha, text = L.fetch_texts([n])[n]
        d = analyze7(n, text, int(G["F"].date[n]))
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print("reason:", d.get("reason"), "| reasons:", d.get("reasons"), "| ph_end:", d.get("ph_end"), "| modal:",
              d.get("modal"))
        print("disp:", d.get("disp_text"))
        for c in d.get("cands", []):
            print(" cand", c["j"], c["date"], G["F"].court_name(c["court"]), "rp" if c["rp"] else "", title_of(c["j"])[:60])
            for o in c["occ"]:
                print("    ", o, "|", L.norm(text[max(0, o[0] - 90):o[0] + 40]))
        for r in d["rows"]:
            print("ROW", json.dumps(r, ensure_ascii=False))
            print("   disp :", L.norm(text[r["disp"][0]:r["disp"][1]]))
            if r["anchor"]:
                print("   anchor:", L.norm(text[r["anchor"][0]:r["anchor"][1]]))


if __name__ == "__main__":
    main()
