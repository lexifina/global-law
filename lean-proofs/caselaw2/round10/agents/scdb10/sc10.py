"""scdb10 (round 10, move 4): the decision below cited without an accepted anchor.

    python -X utf8 sc10.py run [--procs 8] [--tag x]   -> work/rows_all<tag>.jsonl, work/diag10<tag>.jsonl.gz,
                                                          work/run_stats<tag>.json
    python -X utf8 sc10.py explain <node>

Base: round 9's sc9.py (round9/agents/scdb9/sc9.py: round 6 below_sc linker + round 7 R1/R2/R3 + round 8 + round 9
rules), imported read-only (no bytecode written there). Round-10 rule, general over every Supreme Court opinion:

  a10 court-named anchor for the R3 citation. Round 7's R3 (sole litigation decision of the reviewed court: caption
      test, sole, latest, no signal / other name / earlier-proceeding mark) picks the target from the citations alone;
      its row then needs an anchor quote with an anchor cue, which round 6 looked for only in the citation sentence
      and the two sentences around it. Bare citations of the decision below (the CAP footnotes printed after the
      judgment line: "... The decree of the Court of Appeals ... is Reversed. Mr. Justice X took no part ... 15 F.
      Supp. 139. 89 F. (2d) 151."; history sentences whose subject is the court named two or three sentences back:
      "... was affirmed by the Circuit Court of Appeals. It found no proof ... 98 F. 2d 980.") failed. a10: the anchor
      is extended back, sentence by sentence (at most A10_SENT sentences, A10_MAX characters from the anchor start to
      the end of the citation's sentence, inside the citation's part), to the nearest sentence that names the
      target's court (a court phrase that names it, round 6's ph_match = 2, or "the court below"); the quote must
      hold an anchor cue and no anchor disqualifier, as every anchor. For an R3 citation outside the history zone
      whose own sentence names no court (round 7's "L_outside_history_no_court"), the same tie counts as the court
      named. R3 rows that round 7 left out by sub-rule (nozone, fn) are flagged `_a10tie` when their anchor quote
      names the target's court in this sense.
No answer-key file is read.
"""
import argparse, collections, gzip, json, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(C2, "round9", "agents", "scdb9"))
import sc9  # noqa: E402  (round 9, read-only)

sc7, link, L, C, G = sc9.sc7, sc9.link, sc9.L, sc9.C, sc9.G
NL = chr(10)
WORK = os.path.join(HERE, "work")
A10_MAX = 1400
A10_SENT = 6
FLAGS = sc9.FLAGS
FLAGS["a10"] = True
A10 = {"on": False}


def names_court(p, ci):
    return link.ph_match(p, ci) == 2 or p[2] == "BELOW"


def a10_start(view, o, ci):
    """start of the nearest sentence (the citation's own text before the citation, then earlier sentences of the same
    part) that names the target's court; None when none within A10_SENT sentences / A10_MAX characters."""
    lo = o["lo"]
    a1 = o["s"][1]
    a0 = o["s"][0]
    seg_end = o["c"][0]
    for _step in range(A10_SENT + 1):
        if any(names_court(p, ci) for p in link.phrases(view, a0, seg_end)):
            return a0
        pv = link.prev_sentence(view, a0, lo)
        if not pv or a1 - pv[0] > A10_MAX:
            return None
        seg_end = a0
        a0 = pv[0]
    return None


ACT_V = (r"affirm\w*|revers\w*|vacat\w*|held|holding|dismiss\w*|denied|denying|granted|granting|sustain\w*|upheld|"
         r"uph[eo]ld\w*|entered|modified|conclud\w*|ruled|ruling|rejected|rejecting|found|finding|set\s+aside|remanded|refused|"
         r"declined|agreed|decided|enjoin\w*|ordered|overruled|annulled|struck|approved|refused")
ACT_AFTER = re.compile(r"^[’'s]{0,2}[^.;:]{0,70}?\b(?:" + ACT_V + r")\b", re.I)
ACT_BY = re.compile(r"\b(?:" + ACT_V + r")\s+(?:\w+\s+){0,2}?by\s+(?:the\s+|that\s+)?$", re.I)


def act_tie(view, a0, a1, ci):
    """a10 v2: the quote names the target's court as the actor of a judicial act: the court phrase followed (same
    clause, <= 70 characters) by a judicial verb ("The Court of Appeals affirmed", "the court below, holding ...") or
    the agent of a passive verb ("was affirmed by the Circuit Court of Appeals"); the act's clause ends inside the
    quote."""
    for p in link.phrases(view, a0, a1):
        if not names_court(p, ci):
            continue
        if ACT_AFTER.match(view[p[1]:min(a1, p[1] + 90)]) or ACT_BY.search(view[max(a0, p[0] - 60):p[0]]):
            return 1
    return 0


_build8 = link.build_row      # sc9's chain (round 8 A5 head-matter block over round 6)
_orig6 = sc9._orig_build_row  # round 6's build_row


def build_row10(n, view, t, an, kind, scope, dq, flags, src, in_zone, multi, date):
    row = _build8(n, view, t, an, kind, scope, dq, flags, src, in_zone, multi, date)
    if not (A10["on"] and isinstance(row, str) and row == "anchor_no_cue"):
        return row
    for o in an:
        if o["part"] == "headmatter":
            continue
        a0 = a10_start(view, o, t["ci"])
        if a0 is None:
            continue
        a0, a1 = link.trim(view, a0, o["s"][1])
        q = L.norm(view[a0:a1])
        if not link.has_cue(q) or link.has_disq(q):
            continue
        o2 = dict(o)
        o2["ctx0"], o2["s"] = a0, (a0, a1)
        r2 = _orig6(n, view, t, [o2], kind, scope, dq, flags, src, in_zone, multi, date)
        if isinstance(r2, str):
            continue
        r2["_a10"] = 1
        r2["_a10act"] = act_tie(view, a0, a1, t["ci"])
        if r2["anchor"] is None:   # the court-naming quote is the evidence: always kept as the anchor line
            r2["anchor"] = [a0, a1]
            r2["anchor_part"] = o["part"]
        return r2
    return row


link.build_row = build_row10
_loose9 = sc7.loose


def anchor_names_court(view, row, ci):
    if not row.get("anchor"):
        return 0
    a0, a1 = row["anchor"]
    return int(any(names_court(p, ci) for p in link.phrases(view, a0, a1)))


def loose10(cands, ctx):
    rows, reason = _loose9(cands, ctx)
    view = ctx["view"]
    for r in rows:
        if r.get("_sub") in ("nozone", "fn"):
            t = next((d for d in cands.values() if d["j"] == r["target"]), None)
            r["_a10tie"] = anchor_names_court(view, r, t["ci"]) if t else 0
            r["_a10act"] = act_tie(view, r["anchor"][0], r["anchor"][1], t["ci"]) if (t and r.get("anchor")) else 0
    if rows or not FLAGS.get("a10", True) or reason not in ("L_anchor_no_cue", "L_outside_history_no_court"):
        return rows, reason
    ph_end = ctx["ph_end"]
    saved = []
    if reason == "L_outside_history_no_court":
        for d in cands.values():
            for o in d["occ"]:
                if o["part"] != "headmatter" and ph_end is not None and o["c"][0] >= ph_end and not o["any"] and \
                        a10_start(view, o, d["ci"]) is not None:
                    saved.append((o, o["any"]))
                    o["any"] = 2
    A10["on"] = True
    try:
        rows2, reason2 = _loose9(cands, ctx)
    finally:
        A10["on"] = False
        for o, v in saved:
            o["any"] = v
    for r in rows2:
        r["_a10"] = 1
        r["_a10why"] = reason
        if "_a10act" not in r:
            t = next((d for d in cands.values() if d["j"] == r["target"]), None)
            r["_a10act"] = act_tie(view, r["anchor"][0], r["anchor"][1], t["ci"]) if (t and r.get("anchor")) else 0
    if rows2:
        return rows2, None
    return [], reason


sc7.loose = loose10

# a10n decided below under another caption: in the history zone (before "we granted certiorari"), a citation printed
# with a case name other than the acting caption (round 6: "other case name", never an anchor) is the decision under
# review when it closes the report of that court's act: (i) the citation sentence is only the case name and the
# citation, and the sentence before it names the target's court as the actor of a judicial act ("The Court of Appeals
# for the District of Columbia Circuit affirmed ... . Danik, Inc. v. Hartmarx Corp., 875 F. 2d 890 (1989)."), or
# (ii) the case name follows the act's clause after a comma ("The New Mexico Supreme Court has upheld ..., Arizona
# Public Serv. Co. v. O'Chesky, 91 N. M. 485"); and the cited decision is the latest decision of its court that the
# opinion cites. The occurrence then counts as an A1 anchor; every other round-6/7 check is unchanged.
NAME_SENT = re.compile(r"\W{0,3}(?:[^.;:]|\.(?=\s?[A-Za-z]{1,6}\.)|\.(?=\s?\d)|\b(?:v|Co|Inc|Corp|Ltd|No|Nos|Bd|Comm|Ass|Assn|Dept|Mfg|"
                       r"Ry|R|Bros|Nat|St|Mt|Ft|Sav|Ins|Mut|Mun|Dist|Fed|Int|Gen|Am)\.){3,220}?,\s*$")
# the act reported is of another case ("In a similar case ...", "in the Spiegel case", "in a companion case")
OTHER_CASE = re.compile(r"\b(?:similar|another|companion|other|related|parallel|earlier|prior|previous|first)\b|"
                        r"\bin\s+the\s+[A-Z][\w’'.\-]*\s+(?:case|litigation|decision)")
CLAUSE_END = re.compile(r"\b(?:" + ACT_V + r")\b[^.;:()]{0,160}?,\s*$", re.I)


def a10n_upgrade(cands, ctx):
    view, ph_end = ctx["view"], ctx["ph_end"]
    if ph_end is None:
        return
    for d in cands.values():
        later = [e for e in cands.values() if e is not d and sc7.group_key(e) == sc7.group_key(d) and e["date"] > d["date"]]
        if later:
            continue
        for o in d["occ"]:
            if o["named"] != "other" or o["sig"] or o["disq"] or o["rehden"] or o["part"] == "headmatter" or \
                    o["c"][0] >= ph_end:
                continue
            s0, c0 = o["s"][0], o["c"][0]
            sent0 = view[s0:c0]
            mn = link.NAME_BEFORE.search(sent0)
            if not mn or not re.search(r"\bv\.?\s|\bIn\s+re\b|\bEx\s+parte\b", mn.group(1)):
                continue
            ok = False
            if NAME_SENT.fullmatch(sent0) and len(re.findall(r"\b[a-z]{4,}\b", sent0)) <= 1:
                pv = link.prev_sentence(view, s0, o["lo"])
                if pv and act_tie(view, pv[0], s0, d["ci"]) and not OTHER_CASE.search(view[pv[0]:s0]):
                    ok = "prev"
            else:
                head = view[s0:s0 + mn.start(1)]
                if CLAUSE_END.search(head) and act_tie(view, s0, s0 + mn.start(1), d["ci"]) and not OTHER_CASE.search(head):
                    ok = "clause"
            if ok:
                o["named"] = None
                o["typ"] = "A1"
                o["a10n"] = ok


_strict9 = sc7.strict


def strict10(cands, ctx):
    if FLAGS.get("a10n", True):
        a10n_upgrade(cands, ctx)
    rows, reasons = _strict9(cands, ctx)
    for r in rows:
        t = next((d for d in cands.values() if d["j"] == r["target"]), None)
        if not t:
            continue
        a0, a1 = r["anchor"] if r.get("anchor") else r["disp"]
        hit = [o for o in t["occ"] if o.get("a10n") and a0 <= o["c"][0] < a1 + 400]
        if hit and not any(sc7.good(o) and not o.get("a10n") for o in t["occ"]):
            r["_a10n"] = hit[0]["a10n"]
    return rows, reasons


sc7.strict = strict10


def work_run(arg):
    path, off = arg[0], arg[1]
    for k in off:
        FLAGS[k] = False
    sc7.init7()
    link.STEM = sc9._stem_set()
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            try:
                d = sc9.analyze8(r["n"], r["text"], r["date"])
            except Exception as ex:
                d = {"n": r["n"], "date": r["date"], "rows": [],
                     "reason": "error:" + type(ex).__name__ + ":" + str(ex)[:80]}
            d["type"] = r["type"]
            d["len"] = len(r["text"])
            out.append(d)
    return out


def run(procs, off=(), tag=""):
    os.makedirs(WORK, exist_ok=True)
    rows = []
    st = collections.Counter()
    with gzip.open(os.path.join(WORK, "diag10%s.jsonl.gz" % tag), "wt", encoding="utf-8", newline=NL,
                   compresslevel=3) as fd:
        for res in L.pmap(work_run, [(p, tuple(off)) for p in link.shard_files()], procs=procs):
            for d in res:
                st["decisions"] += 1
                if d["rows"]:
                    st["decisions_with_row"] += 1
                else:
                    r = d["reason"] or "?"
                    st["no_row:" + (r.split(":")[0] + ":" + r.split(":")[1] if r.startswith("error") else r)] += 1
                for r in d["rows"]:
                    if r.get("_a10"):
                        st["a10_rows:" + r.get("_a10why", "")] += 1
                    if r.get("_a10tie"):
                        st["a10tie_rows"] += 1
                rows.extend(d["rows"])
                fd.write(json.dumps(d, ensure_ascii=False, default=str) + NL)
    rows.sort(key=lambda r: (r["by"], r["target"]))
    with open(os.path.join(WORK, "rows_all%s.jsonl" % tag), "w", encoding="utf-8", newline=NL) as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + NL)
    st["rows"] = len(rows)
    json.dump(st, open(os.path.join(WORK, "run_stats%s.json" % tag), "w"), indent=1, sort_keys=True)
    print(json.dumps(st, indent=1, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("node", nargs="?")
    ap.add_argument("--procs", type=int, default=8)
    ap.add_argument("--off", default="")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    if a.cmd == "run":
        run(min(a.procs, 8), [x for x in a.off.split(",") if x], a.tag)
    elif a.cmd == "explain":
        sc7.init7()
        link.STEM = sc9._stem_set()
        n = int(a.node)
        sha, text = L.fetch_texts([n])[n]
        d = sc9.analyze8(n, text, int(G["F"].date[n]))
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print("reason:", d.get("reason"), "| reasons:", d.get("reasons"), "| ph_end:", d.get("ph_end"))
        print("disp:", d.get("disp_text"))
        for r in d["rows"]:
            print("ROW", json.dumps({k: v for k, v in r.items()}, ensure_ascii=False)[:3000])
            print("   disp :", L.norm(text[r["disp"][0]:r["disp"][1]]))
            if r["anchor"]:
                print("   anchor:", L.norm(text[r["anchor"][0]:r["anchor"][1]]))


if __name__ == "__main__":
    main()
