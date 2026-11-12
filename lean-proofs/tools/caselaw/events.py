"""Read every mention of overruling in US case law and sort it into acts, reports and noise.

    python tools/caselaw/events.py <extract-dir> <graph-dir> <out-dir>

* An **act** is a decision overruling an earlier one in its own majority opinion ("we overrule X", "X is hereby
  overruled", "to the extent X holds otherwise, it is overruled"). Acts are the facts given to Lean: who overruled
  whom, read from the overruling decision alone.
* A **report** is a later decision saying that X was overruled ("X, 345 U.S. 22 (1953), overruled on other grounds by
  Y, 390 U.S. 39 (1968)"). Reports are held back: they are the courts' own answers the Lean model is tested against.
* Everything else (an objection, motion or exception overruled; a dissent; a refusal to overrule) is noise.

Targets are resolved through the citation index: a citation in the window, or, for an act, a case the overruling
decision cites whose name appears in the clause.

Writes acts.tsv (by, target, how, snippet), reports.tsv (in, target, by-or-empty, qualifier, snippet), counts.json.
"""
import array, collections, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from graph import norm_cite  # noqa: E402

CITE_RX = re.compile(r"\b(\d{1,4})\s+((?:[A-Z][A-Za-z.']{0,9}\s?){1,5}(?:\d[a-z]{1,2}\.?\s?)?(?:\([^)]{1,12}\)\s?)?)\s*(\d{1,5})\b")
NOISE_BEFORE = re.compile(r"(objection|motion|exception|demurrer|plea|assignment|point|contention|petition|request|"
                          r"rehearing|ruling|argument|claim|issue|protest|challenge|application|suggestion|"
                          r"specification|ground|error|complaint|proposition|finding|recommendation|cross-point)s?\b"
                          r"(?:[^.]|\.(?!\s+[A-Z][a-z])){0,60}$", re.I)
REFUSE = re.compile(r"(decline|refuse|need not|will not|do not|did not|cannot|could not|not|asked|urge|urges|invite|"
                    r"request|ask|whether|would|should|asks|asking|urging|nor|unwilling|reluctant|hesitate)\b"
                    r"[\w\s,’']{0,60}$", re.I)
ACT_WE = re.compile(r"\b(?:we|this court|the court|it is)\b(?P<mid>(?:\s+[\w’']+){0,5}?)\s+overrul(?:e|es)\b", re.I)
NEG_MID = re.compile(r"\b(not|decline|declines|refuse|refuses|need|would|could|might|whether|if|unless|asked|ask|asks|"
                     r"urged|urge|invited|invite|requested|request|reluctant|hesitate|cannot|nor|never|have|had|did|was|"
                     r"were|previously|earlier|once|then|recently|implicitly|in|no|should|to|see|cannot|persuaded)\b", re.I)
ACT_PASSIVE = re.compile(r"\b(?:is|are|be)\s+(?:(?:hereby|now|expressly|specifically|therefore|accordingly|herewith|"
                         r"formally|explicitly|today|thus|necessarily|disapproved\s+and|modified\s+and|and\s+now\s+is|"
                         r"and\s+hereby\s+is|and\s+are\s+hereby|in\s+all\s+respects|pro\s+tanto|to\s+that\s+extent|"
                         r"to\s+this\s+extent|overruled\s+and|overturned\s+and|accordingly\s+be|must\s+be|should\s+be)\s+){0,3}"
                         r"overruled\b(?!\s+(?:by|in)\b)", re.I)
ACT_BARE = re.compile(r"(?:(?:reviewed|modified|questioned|disapproved|limited|qualified|explained|criticized|"
                      r"distinguished|doubted)\s+and\s+overruled|held\s+to\s+(?:have\s+been|be)\s+overruled|"
                      r"\d\)?,?\s+(?:\(\d{4}\)\s*)?(?:is\s+)?overruled\s*[;.:])", re.I)
ACT_MODAL = re.compile(r"\b(?:should|must|ought\s+to|shall|will)\s+(?:now\s+|therefore\s+|accordingly\s+|properly\s+|"
                       r"also\s+|thus\s+)?be\s+(?:(?:and\s+now\s+is|and\s+hereby\s+is|and\s+is|expressly|specifically|"
                       r"now|accordingly|formally|explicitly|and\s+it\s+is)\s+){0,2}overruled\b(?!\s+(?:by|in)\b)", re.I)
NEG_BEFORE_MODAL = re.compile(r"\b(whether|ask|asks|asked|asking|urge|urges|urged|argue|argues|argued|contend|contends|"
                              r"suggest|suggests|suggested|consider|question|invite|invites|petition|request|requests|seek|"
                              r"seeks|if|unless|would|might|could|claim|claims|insist|insists|maintain|maintains|"
                              r"submit|submits|propose|proposes|assert|asserts|asserted|implies|imply|sought|until|not|plurality|"
                              r"dissent|dissenting|mock|considered|believes|believed|thinks|thought)\b[^.]{0,120}$", re.I)
ACT_EXTENT = re.compile(r"(?:to the extent|insofar as|in so far as|so far as)[^.]{0,250}\b(?:is|are|be)\s+(?:\w+\s+)?overruled\b"
                        r"(?!\s+(?:by|in)\b)|\b(?:is|are|be)\s+overruled\s+to the extent", re.I)
REPORT = re.compile(r"\boverruled,?\s*((?:(?:on other grounds|in part|on another point|on other points|on different grounds|"
                    r"on a different point|sub silentio|by implication|implicitly|in relevant part|on unrelated grounds|"
                    r"in other part|on other issues?|on another issue|on another ground)[\s,]*){0,2}),?\s*(?:by|in)\s", re.I)
NOISE_AFTER = re.compile(r"overrul\w*\s+(?:(?:[\w.\-]+(?:['’]s?)?|the|his|her|their|its|this|that|these|those|all|each|both|"
                         r"remaining|said|such|any|every|appellants?|appellees?|defendants?|plaintiffs?|respondents?|"
                         r"petitioners?|movants?|relators?|state['’]s|first|second|third|fourth|fifth|sixth|seventh|"
                         r"eighth|ninth|tenth|sole|single|only|and|or|of|error|cross)\s+){0,8}"
                         r"(issues?|points?|contentions?|assignments?|objections?|grounds?|complaints?|arguments?|"
                         r"motions?|exceptions?|claims?|challenges?|errors?|specifications?|propositions?|cross-points?|"
                         r"demurrers?|pleas?|requests?|applications?|petitions?|protests?|counts?|parts?|sub-?issues?)\b",
                         re.I)
REPORT_HAS = re.compile(r"\b(?:was|were|has been|have been|had been|since)\s+(?:\w+\s+)?overruled\b", re.I)
MAJ = re.compile(r"^(Majority|Per Curiam|Opinion|Head matter|Lead|Plurality|$)", re.I)
DISAPPROVE = re.compile(r"\bdisapprov(?:e|es|ed|ing)\b", re.I)
SWAP = {"disapprove": "overrule  ", "disapproves": "overrules  ", "disapproved": "overruled  ",
        "disapproving": "overruling  "}


ABBR = set("""v vs No Nos Co Inc Corp Ltd al seq Bros Ry App Supp Ct Dist Div Cir Rep Rptr Super Misc Dept Cas Ed
    Eq Ga Va Md Pa Me Vt Del Ky La Mo Ohio Iowa Wash Mass Conn Penn Mich Minn Wis Ill Ind Kan Neb Okla Ariz Colo Cal Fla
    Ala Tenn Miss Ark Ore Nev Mont Wyo Utah Tex Civ Crim Pac Atl Fed Wall Pet How Cranch Dall Wheat Black Mr Mrs Dr St
    Ave Assn Ass Comm Comr Commr Sec Stat Ann Gen Laws Rev Cl Pt Art Ch Sess Reg Id Ibid Jr Sr So Wn Hun Barb Paige Wend
    Johns Cow Abb Pr Hill Den Daly Bosw Sandf Duer Hilt Bradf Edw Redf Dem Wheel Rob""".split())


def sentence_of(s, at):
    """The sentence around position `at`: from the last sentence end before it (within 350 characters) to the next
    one after it (within 250). A full stop followed by a capital ends a sentence unless it closes an abbreviation of a
    court, reporter or name (a word in ABBR, or of one or two letters)."""
    def is_end(i):
        if s[i] != ".":
            return False
        j = i + 1
        while j < len(s) and s[j] == " ":
            j += 1
        if j == i + 1 or j >= len(s) or not (s[j].isupper() or s[j] in "“\"("):
            return False
        w = re.search(r"([A-Za-z’']+)$", s[max(0, i - 15):i])
        if w and (w.group(1) in ABBR or len(w.group(1)) <= 2):
            return False
        return True
    a0 = max(0, at - 350)
    for i in range(at - 1, max(0, at - 350) - 1, -1):
        if is_end(i):
            a0 = i + 1
            break
    a1 = min(len(s), at + 250)
    for i in range(at, min(len(s), at + 250)):
        if is_end(i):
            a1 = i + 1
            break
    return a0, a1


def cites_in(text, idx):
    out = []
    for m in CITE_RX.finditer(text):
        k = norm_cite(f"{m.group(1)} {re.sub(r'[()]', '', m.group(2))} {m.group(3)}")
        j = idx.get(k) if k else None
        if j is not None:
            out.append((m.start(), m.end(), j))
    return out


def main(ex, gdir, out):
    os.makedirs(out, exist_ok=True)
    idx = {}
    for line in open(os.path.join(gdir, "cite_index.tsv"), encoding="utf-8"):
        k, v = line.rstrip("\n").split("\t")
        idx[k] = int(v)
    node = {}
    names = {}
    for line in open(os.path.join(gdir, "nodes.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        node[(f[1], f[2])] = int(f[0])
        names[int(f[0])] = f[6]
    ed = array.array("I")
    with open(os.path.join(gdir, "edges.bin"), "rb") as fe:
        ed.frombytes(fe.read())
    cites_of = collections.defaultdict(list)
    for i in range(0, len(ed), 2):
        cites_of[ed[i]].append(ed[i + 1])
    del ed

    STOPW = set("""United States America State States People Commonwealth Commissioner Commissioners Company Corporation
        Railway Railroad Insurance County City Town Village Board Bank National Department Dept Director Secretary
        Administrator Estate Matter Ex Parte Re In The Of And For Inc Co Corp Ltd Association Assn Mutual Life Fire
        Trust Savings Loan Federal District Court Mr Mrs Supreme Appeals Plaintiff Defendant Appellant Appellee
        Petitioner Respondent Others Al Et Use Ins Ry Bros Brothers Sons General Central Southern Northern Eastern
        Western American New Mexico York Texas Pacific Atlantic Missouri Union Steamship Ship Steamboat Lessee Lessees
        Heirs Executor Executors Executrix Administratrix Guardian Trustee Trustees Receiver Collector Warden Sheriff
        Treasurer Auditor Governor Attorney Superintendent Mayor Council Town Township School Schools Church Hospital
        Motor Motors Oil Gas Electric Power Light Water Telephone Telegraph Coal Iron Steel Lumber Mining Land Lands
        Title Guaranty Surety Casualty Indemnity Fidelity Accident Assurance Express Transportation Transit Bus Lines
        Line Mills Mill Manufacturing Products Services Service Industries Enterprises Holdings Group Partners""".split())

    def name_tokens(nm):
        nm = re.sub(r"\(.*?\)", " ", nm)
        return {t for t in re.findall(r"\b[A-Z][a-z][A-Za-z'\-]{2,}", nm) if t.rstrip("'s") not in STOPW and t not in STOPW}

    acts = open(os.path.join(out, "acts.tsv"), "w", encoding="utf-8", newline="\n")
    reps = open(os.path.join(out, "reports.tsv"), "w", encoding="utf-8", newline="\n")
    unres = open(os.path.join(out, "acts_unresolved.tsv"), "w", encoding="utf-8", newline="\n")
    cnt = collections.Counter()
    for f in sorted(glob.glob(os.path.join(ex, "*.overrul.jsonl"))):
        repo = os.path.basename(f)[:-len(".overrul.jsonl")]
        for line in open(f, encoding="utf-8"):
            r = json.loads(line)
            y = node.get((repo, r["path"]))
            if y is None:
                cnt["no-node"] += 1
                continue
            s, at, sec = r["s"], r["at"], r.get("sec", "")
            # "disapprove" (the California Supreme Court's word for overruling a lower court) is read as "overrule",
            # padded so that every offset stays the same
            dis = s[at:at + 9].lower() == "disapprov"
            if "isapprov" in s:
                s = DISAPPROVE.sub(lambda m: SWAP[m.group(0).lower()].capitalize() if m.group(0)[0].isupper()
                                   else SWAP[m.group(0).lower()], s)
            before, after = s[:at], s[at:]
            snippet = s[max(0, at - 220):at + 180].replace("\t", " ")
            # report: "X ..., overruled [on other grounds] by Y"
            m = REPORT.match(after)
            if m or REPORT_HAS.search(s[max(0, at - 25):at + 12]):
                cb = [c for c in cites_in(before[-320:], idx)]
                ca = [c for c in cites_in(after[:260], idx)] if m else []
                if cb:
                    x = cb[-1][2]
                    yb = ca[0][2] if ca else ""
                    qual = ((m.group(1) or '').strip() if m else '') + (' [disapproved]' if dis else '')
                    reps.write(f"{y}\t{x}\t{yb}\t{qual.strip()}\t{snippet}\n")
                    cnt["report"] += 1
                    cnt["report-with-by" if ca else "report-no-by"] += 1
                else:
                    cnt["report-unresolved"] += 1
                continue
            if NOISE_BEFORE.search(before[-90:]) or NOISE_AFTER.match(after[:120]):
                cnt["noise"] += 1
                continue
            # inside a quotation (another court's words): an opening quote after the last closing one, closed soon after
            q = before[-300:]
            if q.rfind("“") > q.rfind("”") and "”" in after[:220]:
                cnt["quoted"] += 1
                continue
            win = s[max(0, at - 160):at + 30]
            kind = None
            for rx, k in ((ACT_WE, "we"), (ACT_PASSIVE, "passive"), (ACT_MODAL, "modal"), (ACT_EXTENT, "extent"),
                          (ACT_BARE, "bare")):
                mm = None
                for mm in rx.finditer(win):
                    pass
                if mm and mm.end() >= 150:
                    if k == "we" and (NEG_MID.search(mm.group("mid") or "") or REFUSE.search(win[:mm.start()])):
                        kind = "refused"
                        break
                    if k in ("modal", "passive") and NEG_BEFORE_MODAL.search(win[:mm.start()]):
                        kind = "refused"
                        break
                    kind = k
                    break
            if kind is None:
                cnt["other"] += 1
                continue
            if kind == "refused":
                cnt["refused"] += 1
                continue
            if not MAJ.match(sec):
                cnt["act-in-separate-opinion"] += 1
                continue
            a0, a1 = sentence_of(s, at)
            region = s[a0:a1]
            targets = [j for _, _, j in cites_in(region, idx) if j != y]
            how = "cite"
            if not targets:
                how = "name"
                near = region.replace("-", "")
                for j in cites_of.get(y, []):
                    for t in name_tokens(names.get(j, "")):
                        if re.search(r"\b" + re.escape(t.replace("-", "")) + r"\b", near):
                            targets.append(j)
                            break
            if not targets:
                cnt["act-unresolved"] += 1
                unres.write(f"{y}\t{kind}\t{len(cites_of.get(y, []))}\t{snippet}\n")
                continue
            for j in dict.fromkeys(targets):
                acts.write(f"{y}\t{j}\t{'disapprove-' if dis else ''}{kind}:{how}\t{snippet}\n")
                cnt["act"] += 1
            cnt["act-windows"] += 1
    acts.close(); reps.close(); unres.close()
    json.dump(cnt, open(os.path.join(out, "counts.json"), "w"), indent=1)
    print(json.dumps(cnt))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
