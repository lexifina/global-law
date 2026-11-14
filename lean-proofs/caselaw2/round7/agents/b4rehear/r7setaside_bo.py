"""Round 7, track B4 (d): "set aside" as a vacatur cue for the decision under review (reviewing courts other than the
Supreme Court of the United States), through the round-6 `below_other` linker, unchanged except for one step.

    python -X utf8 r7setaside_bo.py run   [--procs 22]   -> work/bo/<shard>.rows.jsonl (+ .stats.json)
    python -X utf8 r7setaside_bo.py rows                 -> rows_setaside_bo.jsonl, work/bo_setaside_drops.tsv,
                                                            rows_setaside_bo_stats.json

The one change: round 6's `kind_of` returns no row when the only act word of the clause naming the target's court is
"set aside" / "quashed" / "annulled" (`no_cue_word`, no Lean cue). Here a clause whose only negative act word is
"set aside" (not quashed / annulled) gives a `vacated` row, as the original would have for "vacated"; every other
step of the linker is the round-6 code (imported, not copied). Then (`rows`):
  - only rows that round 6 did not emit (by, target, kind) and whose disposition quote has "set aside" and no
    "vacat" are kept, with claim `setAside` (DESIGN7 3.2);
  - R7-S1 the set-aside phrase must have a judgment / decree / order / decision / ruling as its object, in the
    passive ("the judgment of the district court is ... set aside") or the active ("we set aside the judgment");
  - R7-S2 no row when the words between that noun and "set aside" (or the noun phrase itself) speak of something
    other than the court's judgment: a verdict, sentence, default, award, finding, assessment, sale, deed, an order
    of an agency, board, commission, referee, master, arbitrator, a plea, bond, lien, service, etc.;
  - R7-S3 the round-6 shared reporter page guard (below_other/shared_cite.py rule, re-applied here).
No Shepardized, gold, split, heldout or reports file is read. Writes only in this folder.
"""
import sys

sys.dont_write_bytecode = True
import argparse, collections, json, os, re  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BO_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "..", "round6", "history", "rules", "below_other"))
sys.path.insert(0, BO_DIR)
import link as BO  # noqa: E402  (round-6 below_other linker; not edited)

L = BO.L
C = BO.C
NL = chr(10)
OUTW = os.path.join(HERE, "work", "bo")
SET_ASIDE = re.compile(r"\bset\s+aside\b", re.I)
_orig_kind_of = BO.kind_of


def kind_of_r7(kinds, sent):
    k, why = _orig_kind_of(kinds, sent)
    if k is None and why == "no_cue_word" and SET_ASIDE.search(sent) and not re.search(r"\bquash|\bannul", sent, re.I):
        ks = set(kinds)
        ks.discard("vacated*")
        ks.add("vacated")
        return _orig_kind_of(ks, sent)  # "vacated" needs no cue word in the original; scope rules unchanged
    return k, why


def init_patch():
    BO.init()
    BO.WORK = OUTW
    BO.kind_of = kind_of_r7


def stage_run(procs):
    os.makedirs(OUTW, exist_ok=True)
    paths = L.shards()
    paths = [p for p in paths if not os.path.basename(p).startswith("supreme-court.")
             and os.path.exists(p[:-len(".jsonl.gz")] + ".stats.json")]
    paths.sort(key=os.path.getsize, reverse=True)
    import multiprocessing as mp
    tot = collections.Counter()
    with mp.Pool(procs, initializer=init_patch) as pool:
        for tag, st in pool.imap_unordered(BO.run_shard, [(p, False) for p in paths], chunksize=1):
            tot.update(st)
    json.dump(dict(sorted(tot.items())), open(os.path.join(OUTW, "_total_stats.json"), "w"), indent=1)
    print({k: v for k, v in tot.items() if k.startswith(("rows", "drop:no_cue"))})


NOUN = r"(?:judgments?|decrees?|orders?|decisions?|rulings?|determinations?|adjudications?)"
SA_PASSIVE = re.compile(r"\b" + NOUN + r"\b(?P<gap>[^.;]{0,200}?)\b(?:is|are|be|was|were|must\s+be|should\s+be|shall\s+be|will\s+be|"
                        r"stands?|hereby\s+is|hereby\s+are)\s+(?:(?:hereby|accordingly|therefore|now|in\s+all\s+things|,|and\s+the\s+"
                        r"same\s+(?:is|are)(?:\s+hereby)?|reversed\s+and|vacated\s+and|annulled\s+and)\s*)*set\s+aside\b", re.I)
SA_ACTIVE = re.compile(r"\b(?:we|court)\s+(?:(?:hereby|therefore|accordingly|now|must|will|do)\s+)*(?:reverse\s+and\s+)?set\s+aside\s+"
                       r"(?P<gap>(?:the|that|its|said)\s+(?:[\w'’\-]+\s+){0,3}?)" + NOUN + r"\b(?P<after>[^.;]{0,120})", re.I)
SA_BAD = re.compile(
    r"\b(?:verdicts?|sentences?|default|awards?|findings?|assessments?|deeds?|conveyances?|sales?|leases?|contracts?|"
    r"marriages?|tax(?:es|ation)?|ordinances?|elections?|board|commissions?|commissioner|agency|department|bureau|"
    r"administrative|arbitrat\w*|referee|master|magistrate|jury|pleas?|probation|bonds?|liens?|mortgages?|service|levy|"
    r"attachment|garnishment|secretary|director|council|authority|hearing\s+officer|examiner|registrar|clerk|"
    r"settlement|stipulation|consent|confession|nonsuit|dismissal\s+of\s+the\s+(?:complaint|petition)|summary)\b", re.I)


# R7-S4: the set-aside phrase is the court's own present act, not a rule, an argument, a request or a condition
SA_NOTACT = re.compile(r"\b(?:not|never|no|may|might|can|cannot|could|would|unless|if|whether|sought|seeks?|seeking|"
                       r"asks?|asked|moved?|motion|petition|contends?|argues?|argued|urges?|until|before|when|where|"
                       r"which|that|should\s+not|need\s+not|ought)\b", re.I)
SA_GENERIC = re.compile(r"\b(?:argues?|argued|contends?|contended|contention|urges?|urged|asserts?|insists?|general\s+rule|"
                        r"rule\s+is|generally|ordinarily|usually|well[- ]settled|well[- ]established|unless|whenever|"
                        r"arguments?|reiterat\w*|claims?\s+that|held|holds|holding|concluded|ruled|determined|found|"
                        r"decided|reasoned|that\s+court)\b", re.I)
SA_AUX_OK = re.compile(r"(?:\b(?:is|are|stands?)\b|\bbe,?\s+and\s+(?:the\s+same\s+)?(?:it\s+)?(?:hereby\s+)?(?:is|are)\b)"
                       r"[\s,]*(?:(?:hereby|accordingly|therefore|now|in\s+all\s+things|reversed\s+and|vacated\s+and|annulled\s+and)"
                       r"[\s,]*)*set\s+aside\b", re.I)


DATED = re.compile(r"\b(?:entered|dated|filed|rendered|made|signed|of|on)\s+(?:on\s+(?:or\s+about\s+)?)?(January|February|March|"
                   r"April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s*(\d{4})", re.I)


def other_dated(sent, jdate):
    """BO.other_dated with "June 22,1931" (no space after the comma) read too."""
    import datetime
    ds = []
    for m in DATED.finditer(sent):
        try:
            ds.append(datetime.date(int(m.group(3)), BO.MONTHS[m.group(1).lower()], int(m.group(2))).toordinal())
        except ValueError:
            continue
    return bool(ds) and all(abs(d - BO.day(jdate)) > 45 for d in ds)


# sentence ends, not after an initial ("W.") or a common abbreviation
SENT_SPLIT = re.compile(r"(?<=[.!?])(?<!\b[A-Z]\.)(?<!\bv\.)(?<!\bNo\.)(?<!\bCo\.)(?<!\bJr\.)(?<!\bSr\.)(?<!\bSt\.)"
                        r"(?<!\bInc\.)(?<!\bMr\.)(?<!\bMrs\.)(?<!\bDr\.)\s+(?=[A-Z“\"(])")


def setaside_object_ok(q, jdate=None, same_court=False, target_tier=None):
    """The quote passes when one of its sentences that says "set aside" passes `sentence_ok` (a long base quote holds
    several sentences; only the set-aside sentence is judged). R7-S5: a sentence that dates the order it sets aside
    ("the ruling of January 6, 1989 is set aside") must date the target (within 45 days, the round-6 rule)."""
    why0 = "no_judgment_object"
    for s in SENT_SPLIT.split(q):
        if not SET_ASIDE.search(s):
            continue
        ok, why = sentence_ok(s)
        if ok and jdate and other_dated(s, jdate):
            ok, why = False, "dated_otherwise"
        # R7-S6: the acting court setting aside its OWN earlier order or judgment ("our order granting the writ of
        # error", "the judgment heretofore entered by this Court", "our order of remand") does not act on the
        # decision under review of another court (every row here is a review of another court's decision)
        if ok and not same_court and OWN_ORDER.search(s[:SET_ASIDE.search(s).start()]):
            ok, why = False, "own_order_set_aside"
        # R7-S11: across courts, the set-aside sentence names the court whose judgment it sets aside ("the judgment
        # of the Court of Appeal", "the judgments of the courts below"); a bare "the judgment is set aside" may be the
        # trial court's (habeas, contempt, original proceedings), and a sentence naming only a trial court does not
        # speak of an intermediate court's decision
        if ok and not same_court and target_tier is not None:
            pre = s[:SET_ASIDE.search(s).start()]
            named = {BO.norm_ws(m.group(1)) for m in BO.COURT_RX.finditer(pre)}
            if MIL_RX.search(pre):
                named.add("court of military review")
            plural = bool(re.search(r"\bcourts\s+below\b|\blower\s+courts\b|\bjudgments\s+of\s+the\s+(?:\w+\s+){0,4}courts?\b", pre, re.I))
            if not named and not plural:
                ok, why = False, "no_court_named"
            elif target_tier in ("A", "B", "D") and not plural and named <= TRIAL_NAMES:
                ok, why = False, "names_other_court"
        if ok:
            return True, ""
        why0 = why
    return False, why0


MIL_RX = re.compile(r"court\s+of\s+military\s+review|court\s+of\s+criminal\s+appeals", re.I)
TRIAL_NAMES = set(BO.TRIAL_PHRASES) | {"district judge", "trial court", "trial judge", "trial justice", "magistrate",
                                        "magistrate judge", "bankruptcy court", "bankruptcy judge"}


OWN_ORDER = re.compile(r"\bour\b|\bthis\s+court|\bheretofore\b|\bherein\b|\border\s+(?:of\s+remand|granting|refusing|"
                       r"dismissing)\b|\bwrit\s+of\s+error\b|\bapplication\b|\bwrit\s+(?:granted|of\s+certiorari)\b|\bremand\b",
                       re.I)


def sentence_ok(q):
    """R7-S1 / R7-S2 / R7-S4 on one sentence -> (ok, why)."""
    found = False
    if q.lstrip()[:1] in "“\"‘'" or SA_GENERIC.search(q):
        return False, "not_own_act"
    sa = SET_ASIDE.search(q)
    if re.search(r"\b(?:if|unless|whether|when|where|whenever|until)\b", q[:sa.start()], re.I):
        return False, "not_own_act"
    # a condition after the phrase ("are set aside if they are in violation"), or the phrase inside a quotation (the
    # words of another court's rescript or of a statute)
    if re.match(r"\s*(?:only\s+)?(?:if|unless|when|where|whenever|only)\b", q[sa.end():], re.I):
        return False, "not_own_act"
    pre = q[:sa.start()]
    if pre.count("“") > pre.count("”") or pre.count('"') % 2 == 1:
        return False, "quoted"
    for m in SA_PASSIVE.finditer(q):
        found = True
        # the noun is the subject: the words between it and the auxiliary are its own modifiers, not a new clause
        # ("unnecessary to the decision and is set aside" names something else)
        gap = m.group("gap")
        if re.match(r"\s*(?:and|but|or)\b", gap, re.I) or re.search(r"\b(?:was|were|has|had|have)\b", gap, re.I):
            return False, "noun_not_subject"
        noun_ctx = q[max(0, m.start() - 60):m.start()] + " " + m.group(0)
        if SA_BAD.search(noun_ctx):
            return False, "object_other_thing"
        tail = m.group(0)[-90:]
        sa = q[:m.end()]
        # the auxiliary must be decretal: "is / are (hereby) set aside", "be, and the same is, set aside", or "be /
        # must be / should be set aside" in an order ("ordered", "adjudged", "decreed") or with "therefore / accordingly"
        if not SA_AUX_OK.search(tail):
            # "thereupon ordered that the judgment ... be set aside": a past order of some court, narrated
            if re.search(r"\b(?:thereupon|then|thereafter|had|subsequently|which|who)\s+(?:ordered|directed)\b", sa, re.I) or \
                    re.search(r"\b(?:district|trial|lower|county|circuit|superior|appellate)\s+court\s+(?:\w+\s+){0,2}?"
                              r"(?:ordered|directed)\b", sa, re.I):
                return False, "not_own_act"
            if not re.search(r"\b(?:ordered|adjudged|decreed|directed)\b", sa, re.I) and \
                    not (re.search(r"\b(?:must|should|will|shall)\s+be\s+set\s+aside", tail, re.I) and
                         re.search(r"\b(?:therefore|accordingly)\b", q[:m.end()], re.I)):
                return False, "not_own_act"
        if SA_NOTACT.search(q[max(0, m.end() - 45):m.end() - len("set aside")]):
            return False, "not_own_act"
    for m in SA_ACTIVE.finditer(q):
        found = True
        if SA_BAD.search(m.group("gap") + " " + m.group("after")[:60]):
            return False, "object_other_thing"
        if SA_NOTACT.search(q[max(0, m.start() - 30):m.start() + 4]):
            return False, "not_own_act"
    if not found:
        return False, "no_judgment_object"
    if re.search(r"\b(?:to|motion\s+to|refus\w*\s+to|failed\s+to|declin\w*\s+to)\s+set\s+aside\b", q, re.I):
        return False, "set_aside_as_infinitive"
    return True, ""


def stage_rows():
    import glob
    old = set()
    for line in open(os.path.join(BO_DIR, "rows.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        old.add((r["by"], r["target"], r["kind"]))
    for line in open(os.path.join(BO_DIR, "work", "rows.preshared.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        old.add((r["by"], r["target"], r["kind"]))
    rows = []
    for p in sorted(glob.glob(os.path.join(OUTW, "*.rows.jsonl"))):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            if r["kind"] == "vacated" and (r["by"], r["target"], r["kind"]) not in old:
                rows.append(r)
    print("new vacated rows", len(rows), flush=True)
    FD = L.Facts()
    BO.init()
    texts = {}
    nodes = sorted({r["by"] for r in rows})
    for i in range(0, len(nodes), 3000):
        texts.update(L.fetch_texts(nodes[i:i + 3000]))
    st = collections.Counter()
    keep, drops = [], []
    for r in rows:
        t = texts.get(r["by"])
        if t is None:
            st["drop:no_text"] += 1
            continue
        q = L.norm(t[1][r["disp"][0]:r["disp"][1]])
        ql = q.lower()
        if "vacat" in ql or "set aside" not in ql:
            st["drop:not_setaside_quote"] += 1
            drops.append(("not_setaside_quote", r["by"], r["target"], q[:300]))
            continue
        tt = int(r["target"])
        ok, why = setaside_object_ok(q, int(FD.date[tt]),
                                     target_tier=BO.court_at(int(FD.court[tt]), int(FD.date[tt]))[1])
        if not ok:
            st["drop:" + why] += 1
            drops.append((why, r["by"], r["target"], q[:300]))
            continue
        r["q"] = q
        # R7-S7: "the remainder of the judgment ... is set aside", "insofar as", "as to X": a partial act
        if r["scope"] == "all" and re.search(r"\bremainder\b|\bportions?\b|\bpart\s+of\b|\binsofar\b|\bin\s+so\s+far\b|"
                                             r"\bas\s+to\b|\bexcept\b|\bto\s+the\s+extent\b|\bin\s+part\b", q, re.I):
            r["scope"] = "unknown"
            st["scope_unknown_partial_words"] += 1
        keep.append(r)
    # R7-S3: the round-6 shared reporter page guard (below_other/shared_cite.py, same rule)
    keys = {r["ev"][5:] for r in keep if r["ev"].startswith("cite:")}
    holders = collections.defaultdict(set)
    with open(L.NODES, encoding="utf-8") as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 7 or not p[5]:
                continue
            for c in p[5].split("|"):
                k = C.norm_cite(c.replace("(", "").replace(")", ""))
                if k in keys:
                    holders[k].add(int(p[0]))
    BO.init()
    N = BO.G["N"]
    out = []
    for r in keep:
        hs = holders.get(r["ev"][5:], set()) | {r["target"]}
        if len(hs) > 1:
            d_all, d_sides = BO.caption(N.name(r["by"]))
            good = [h for h in hs if BO.cap_rel(d_all, N.name(h), d_sides) >= 2]
            if good != [r["target"]]:
                st["drop:shared_cite"] += 1
                drops.append(("shared_cite", r["by"], r["target"], r["q"][:300]))
                continue
        out.append(r)
    F = BO.G["F"]
    with open(os.path.join(HERE, "rows_setaside_bo.jsonl"), "w", encoding="utf-8", newline=NL) as o:
        for r in out:
            row = {"rule": "r7setaside:" + r["rule"], "table": "history", "by": r["by"], "target": r["target"], "kind": "vacated",
                   "scope": r["scope"], "main": r["disp"], "part": r["part"], "ev": r["ev"], "joined": [], "claim": "setAside",
                   "doctrine": "-", "field_limit": "-", "text": "by", "anchor": r["anchor"], "anchor_part": r["anchor_part"] or "",
                   "note": r["note"]}
            o.write(json.dumps(row, ensure_ascii=False) + NL)
            st["rows"] += 1
            st["rows:%s" % ("federal" if F.system(int(F.court[r["by"]])) == 0 else "state")] += 1
    with open(os.path.join(HERE, "work", "bo_setaside_drops.tsv"), "w", encoding="utf-8", newline=NL) as o:
        for d in drops:
            o.write("\t".join(str(x).replace("\t", " ") for x in d) + NL)
    json.dump(dict(sorted(st.items())), open(os.path.join(HERE, "rows_setaside_bo_stats.json"), "w"), indent=1)
    print(dict(sorted(st.items())))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["run", "rows"])
    ap.add_argument("--procs", type=int, default=22)
    a = ap.parse_args()
    if a.stage == "run":
        stage_run(a.procs)
    else:
        stage_rows()


if __name__ == "__main__":
    main()
