"""Cheap rules of the reader: which candidate sentences go to the model, which are rejected and why.

Every rule looks only at the citing decision's own sentence (and its +-400 window). Later courts' notes about a target
("X, overruled by Y", "abrogated by", "superseded by statute as stated in") are recognised here only so they can be
REJECTED: they are the evaluation's gold and never become treatments.
"""
import re

VERB = {
    "overrule": r"overrul\w*",
    "disapprove": r"disapprov\w*",
    "recede": r"reced\w*\s+from",
    "abrogate": r"abrogat\w*",
    "supersede": r"supersed\w*",
}
QUAL = (r"(?:\s*,?\s*(?:on\s+(?:other|another|different|unrelated|separate)\s+(?:grounds?|points?|issues?)|in\s+part|"
        r"in\s+relevant\s+part|in\s+other\s+part|sub\s+silentio|by\s+implication|implicitly|expressly|partially|"
        r"on\s+(?:a|another)\s+(?:point|ground)|to\s+the\s+extent\s+[^,()]{0,80}|as\s+stated|as\s+recognized)\s*,?)*")
# "X, overruled [on other grounds] by Y" / "(abrogated by Y)" / "superseded by statute as stated in Y" / "(overruling X)"
REPORT = re.compile(
    r"\b(?:overrul(?:ed|ing)|disapprov(?:ed|ing)|abrogat(?:ed|ing)|supersed(?:ed|ing)|receded\s+from|limited)" + QUAL +
    r"\s+(?:by|in)\s+(?!(?:this|the\s+present|today|our\s+(?:decision|opinion)\s+today|statute|statutory|rule|rules|"
    r"amendment|amendments|legislation|legislative|the\s+legislature|congress|act|enactment|section|§|"
    r"the\s+(?:\d{4}\s+)?(?:amendments?|act|statute|rules?|legislature|general\s+assembly|code)|"
    r"(?:\d{4}\s+)?(?:amendments?|acts?|statutes?))\b)"
    r"|\b(?:superseded|abrogated)\s+(?:by\s+)?(?:statute|rule|amendment|legislation)[^.;()]{0,40}?\bas\s+(?:stated|recognized|noted)\s+in\b"
    r"|\((?:overruling|disapproving|abrogating|receding\s+from|superseding|limiting|questioning|criticizing|"
    r"declining\s+to\s+follow|overruled|abrogated|disapproved|superseded)\b",
    re.I)
# narrated past acts ("X was overruled", "the court in Y overruled X", "has been overruled") - another court's act or a
# report of history, not this court's act today
PAST = re.compile(r"\b(?:was|were|has\s+been|have\s+been|had\s+been|having\s+been|since\s+been|later|subsequently|"
                  r"previously|since|once|had|has|have)\s+(?:\w+\s+){0,2}?(?:overruled|disapproved|abrogated|"
                  r"receded\s+from|superseded|limited|questioned|criticized|repudiated)\b", re.I)
# procedural "overruled": objections, motions, points of error ...
NOISE_BEFORE = re.compile(r"(objection|motion|exception|demurrer|plea|assignment|point|contention|petition|request|"
                          r"rehearing|ruling|argument|claim|issue|protest|challenge|application|suggestion|"
                          r"specification|ground|error|complaint|proposition|finding|recommendation|cross-point)s?\b"
                          r"(?:[^.]|\.(?!\s+[A-Z][a-z])){0,60}$", re.I)
NOISE_AFTER = re.compile(r"(?:overrul|disapprov)\w*\s+(?:(?:[\w.\-]+(?:['’]s?)?|the|his|her|their|its|this|that|these|"
                         r"those|all|each|both|remaining|said|such|any|every|appellants?|appellees?|defendants?|"
                         r"plaintiffs?|respondents?|petitioners?|movants?|relators?|state['’]s|first|second|third|fourth|"
                         r"fifth|sixth|seventh|eighth|ninth|tenth|sole|single|only|and|or|of|error|cross)\s+){0,8}"
                         r"(issues?|points?|contentions?|assignments?|objections?|grounds?|complaints?|arguments?|"
                         r"motions?|exceptions?|claims?|challenges?|errors?|specifications?|propositions?|cross-points?|"
                         r"demurrers?|pleas?|requests?|applications?|petitions?|protests?|counts?|sub-?issues?|"
                         r"findings?|recommendations?)\b", re.I)
# a performative/present cue somewhere in the sentence: "we ...", "this court ...", "is/are (hereby) Xed",
# "to the extent", "should be Xed", "today" ...
PERF = re.compile(
    r"\b(?:we|us|this\s+court|the\s+court\s+(?:now|hereby|today)|today|hereby|herewith|henceforth|hereafter|"
    r"no\s+longer)\b"
    r"|\b(?:is|are|be|stands?)\s+(?:\w+\s+){0,3}?(?:overruled|disapproved|abrogated|receded\s+from|superseded|limited|"
    r"repudiated|modified\s+and\s+overruled)\b"
    r"|\b(?:to\s+the\s+extent|insofar\s+as|in\s+so\s+far\s+as|so\s+far\s+as)\b", re.I)
SUPERSEDE_LAW = re.compile(r"supersed\w*\s+(?:\w+\s+){0,3}?by\s+(?:the\s+)?(?:\d{4}\s+)?(?:statute|statutory|rule|"
                           r"amendment|legislation|legislative|enactment|congress|the\s+legislature|act\b|section|§|"
                           r"[A-Z][\w.]*(?:\s+[A-Z][\w.]*){0,6}\s+(?:Act|Code|Rule|Rules|Amendment))"
                           r"|legislatively\s+(?:superseded|overruled|abrogated)|(?:statute|amendment|legislation|"
                           r"act|rule)\s+(?:\w+\s+){0,3}supersed\w*", re.I)
OPINION_SUPERSEDE = re.compile(r"\b(?:this|the\s+following|our|the\s+present|instant)\s+(?:amended\s+|substituted\s+|"
                               r"revised\s+)?opinion\s+(?:is\s+)?(?:substituted|supersedes|replaces|is\s+filed\s+in\s+lieu)"
                               r"|\bopinion\s+(?:previously\s+)?(?:filed|issued|released)\s+[^.]{0,80}?\bis\s+(?:hereby\s+)?"
                               r"(?:withdrawn|vacated)", re.I)
REFUSE = re.compile(r"\b(?:decline|declines|declined|refuse|refuses|need\s+not|will\s+not|do\s+not|did\s+not|cannot|"
                    r"could\s+not|not|asked|urge|urges|invite|invites|request|ask|asks|whether|would|should\s+we|nor|"
                    r"unwilling|reluctant|hesitate)\b[\w\s,’']{0,60}$", re.I)


def is_report(s, a):
    if REPORT.match(s, a) or (a > 0 and REPORT.match(s, a - 1)):
        return True
    # citator style: the verb straight after a citation or its parenthetical ("906 P.2d 1365 (Alaska 1995), superseded
    # by statute, ...", "263 Cal.App.2d 41 (1968) (since superseded by statute)")
    return bool(CITATOR_BEFORE.search(s, max(0, a - 40), a))


CITATOR_BEFORE = re.compile(r"(?:\d|\)|\]|supra|id\.)\s*,?\s*\(?(?:since|later|subsequently|now|implicitly|partially|"
                            r"expressly|effectively|abrogated\s+and|modified\s+and)?\s*$", re.I)
ADV = (r"(?:now|hereby|therefore|thus|today|expressly|specifically|accordingly|also|further|formally|explicitly|"
       r"necessarily|must|shall|will|do|does|have\s+decided\s+to|decide\s+to|choose\s+to|elect\s+to|are\s+compelled\s+to|"
       r"herewith|respectfully|unanimously|consequently|henceforth|similarly|likewise|so|clearly|squarely|and|"
       r"[a-z]+ly|(?:disavow|reconsider|reject|repudiate|abandon|modify|disapprove|criticize|question|limit|recede\s+from)"
       r"\s+and)")
SUBJ = r"(?:we|this\s+court|the\s+court|i|this\s+tribunal|our\s+court|this\s+commission)"
PRES = {"overrule": r"overrule[s]?", "disapprove": r"disapprove[s]?", "recede": r"recede[s]?\s+from",
        "abrogate": r"abrogate[s]?", "supersede": r"supersede[s]?", "repudiate": r"(?:repudiate|abandon|reject)[s]?",
        "limit": r"limit[s]?", "question": r"(?:question|doubt)[s]?", "declineFollow": r"(?:decline|refuse)[s]?\s+to\s+follow"}
PART = {"overrule": r"overruled", "disapprove": r"disapproved", "recede": r"receded\s+from", "abrogate": r"abrogated",
        "supersede": r"superseded", "repudiate": r"(?:repudiated|abandoned|rejected)", "limit": r"limited",
        "question": r"(?:questioned|doubted)"}
NEG_WE = re.compile(r"\b(?:not|never|decline[sd]?\s+to|refuse[sd]?\s+to|need\s+not|cannot|could|would|might|may|if|"
                    r"whether|unless|asked|urged|invited|reluctant|hesitate|unwilling|nor)\b", re.I)
NEG_BEFORE = re.compile(r"\b(?:whether|ask|asks|asked|asking|urge|urges|urged|urging|argue|argues|argued|arguing|contend|"
                        r"contends|contended|suggest|suggests|suggested|invite|invites|invited|petition|request|requests|"
                        r"requested|seek|seeks|sought|if|unless|would|might|could|claim|claims|insist|insists|maintain|"
                        r"maintains|submit|submits|propose|proposes|assert|asserts|asserted|until|not|plurality|dissent|"
                        r"dissenting|consider|considered|believes|believed|thinks|thought|why|when|whenever|persuaded|"
                        r"convinced|reason\s+to|no\s+need|need\s+not)\b[^.;]{0,120}$", re.I)
PASSIVE_ADV = (r"(?:(?:hereby|now|expressly|specifically|therefore|accordingly|herewith|formally|explicitly|today|thus|"
               r"necessarily|in\s+all\s+respects|pro\s+tanto|to\s+that\s+extent|to\s+this\s+extent|insofar|partially|"
               r"in\s+part|also|likewise|similarly|(?:modified|disapproved|questioned|criticized|limited|overruled|"
               r"overturned|receded\s+from)\s+and|and\s+(?:now|hereby)\s+(?:is|are)|and\s+are\s+hereby|and\s+is\s+hereby)"
               r"\s+){0,3}")


def act_shaped(s, fam):
    """Positions in sentence s where a verb of family fam is used as this court's own present act."""
    out = []
    if fam in PRES:
        rx = re.compile(r"\b" + SUBJ + r"((?:\s+" + ADV + r"){0,4})\s+(" + PRES[fam] + r")\b", re.I)
        for m in rx.finditer(s):
            if NEG_WE.search(m.group(1) or ""):
                continue
            if fam != "declineFollow" and REFUSE.search(s[max(0, m.start() - 70):m.start()]):
                continue
            out.append((m.start(2), "we"))
    if fam in PART:
        rx = re.compile(r"\b(?:is|are|be|stands?|remains?)\s+(" + PASSIVE_ADV + r")(" + PART[fam] + r")\b", re.I)
        for m in rx.finditer(s):
            after = s[m.end():m.end() + 40]
            if re.match(r"\s*(?:,\s*)?(?:by|in)\s", after, re.I) and not (fam == "supersede" and SUPERSEDE_LAW.search(s)):
                continue
            pre = s[max(0, m.start() - 30):m.start()]
            if re.search(r"\bnot\s*$", pre, re.I):
                continue
            if re.search(r"\b(?:should|must|ought\s+to|shall|will|would|could|might|may|can|cannot|to)\s*$", pre, re.I):
                # modal passive: an act only without argument/negation words before it
                if NEG_BEFORE.search(s[max(0, m.start() - 160):m.start()]):
                    continue
            elif re.search(r"\b(?:whether|if|unless|not|when|whenever)\b", s[max(0, m.start() - 60):m.start()], re.I):
                continue
            out.append((m.start(2), "passive"))
    if fam in ("overrule", "disapprove", "abrogate", "recede"):
        for m in re.finditer(r"(?:to\s+the\s+extent|insofar\s+as|in\s+so\s+far\s+as|so\s+far\s+as|inasmuch\s+as)[^.]{0,250}?"
                             r"\b(" + PART[fam] + r")\b(?!\s*,?\s*(?:by|in)\s)", s, re.I):
            out.append((m.start(1), "extent"))
        for m in re.finditer(r"\b(" + PART[fam] + r")\s+to\s+the\s+extent\b", s, re.I):
            out.append((m.start(1), "extent"))
    if fam == "supersede":
        for m in SUPERSEDE_LAW.finditer(s):
            if is_report(s, m.start()):
                continue
            out.append((m.start(), "law"))
    if fam == "repudiate":
        for m in re.finditer(r"\bno\s+longer\s+(?:follow|adhere\s+to|recognize|be\s+followed|good\s+law|the\s+law|"
                             r"controlling|authoritative|valid)\b", s, re.I):
            if not NEG_BEFORE.search(s[max(0, m.start() - 80):m.start()]):
                out.append((m.start(), "nolonger"))
    if fam == "declineFollow":
        for m in re.finditer(r"\b(?:we|this\s+court|i)\s+(?:(?:therefore|thus|accordingly|respectfully|also|must|"
                             r"now|will|shall)\s+)*(?:decline|refuse|will\s+not|do\s+not|cannot|shall\s+not|no\s+longer|"
                             r"are\s+unwilling|are\s+not\s+inclined)\s+(?:to\s+)?(?:follow|adhere\s+to)\b", s, re.I):
            out.append((m.start(), "we"))
    if fam == "limit":
        for m in re.finditer(r"\blimit(?:ed|s)?\s+(?:[\w’']+\s+){0,5}?to\s+(?:its|their)\s+(?:\w+\s+)?facts", s, re.I):
            pre = s[max(0, m.start() - 80):m.start()]
            if re.search(r"\b(?:has|have|had|was|were|been)\s+(?:\w+\s+)?$", pre, re.I):
                continue
            out.append((m.start(), "limit"))
    if fam == "question":
        for m in re.finditer(r"\b(?:we|this\s+court)\s+(?:(?:now|therefore|also|seriously|must|do|have\s+come\s+to)\s+)*"
                             r"(?:question|doubt)\b|\b(?:we|this\s+court)\s+(?:(?:now|therefore|also)\s+)*(?:call|cast|place)\s+"
                             r"(?:[\w’']+\s+){0,5}?(?:into|in)\s+(?:question|doubt)", s, re.I):
            if not NEG_WE.search(s[m.start():m.end()]):
                out.append((m.start(), "we"))
    return out


def classify(cand_sentence, fams, part):
    """('llm', reason) to send to the model, or ('reject', reason)."""
    s = cand_sentence
    if part.startswith(("dissent", "concurrence")):
        return "reject", "separate-opinion"
    if part == "headmatter":
        return "reject", "headmatter"
    if fams == ["supersede"] and OPINION_SUPERSEDE.search(s):
        return "reject", "opinion-substitution"  # same-case history, handled by the history reader
    shapes = []
    for f in fams:
        for pos, how in act_shaped(s, f):
            if f in ("overrule", "disapprove") and (NOISE_BEFORE.search(s[max(0, pos - 90):pos]) or NOISE_AFTER.match(s, pos)):
                continue
            if how != "law" and is_report(s, pos):
                continue
            shapes.append((f, how))
    if shapes:
        return "llm", shapes[0][0] + ":" + shapes[0][1]
    verbs = list(re.finditer(r"\b(?:overrul\w*|disapprov\w*|abrogat\w*|supersed\w*|reced\w*\s+from)", s, re.I))
    if verbs and all(is_report(s, m.start()) for m in verbs):
        return "reject", "report"
    if verbs and all(NOISE_BEFORE.search(s[max(0, m.start() - 90):m.start()]) or NOISE_AFTER.match(s, m.start())
                     for m in verbs):
        return "reject", "procedural"
    if PAST.search(s):
        return "reject", "past"
    return "reject", "not-act-shaped"


# cue table: the words a certificate quote must contain for each kind (mirrored in data/reader_cues.tsv for Lean)
CUES = {
    "overruled": ["overrul", "repudiat", "abandon", "no longer follow", "no longer good law", "no longer the law",
                  "no longer be followed", "no longer adhere"],
    "disapproved": ["disapprov"],
    "recededFrom": ["reced"],
    "abrogated": ["abrogat"],
    "supersededByEnactment": ["supersed", "legislatively overruled", "abrogat"],
    "limited": ["limit"],
    "questioned": ["question", "doubt", "no longer good law", "no longer valid", "continued validity",
                   "continued vitality", "continuing validity", "continuing vitality"],
    "criticized": ["criticiz", "criticis"],
    "declinedToFollow": ["decline", "refuse", "not follow", "no longer follow", "no longer be followed", "not be followed",
                         "not adhere", "unwilling", "not inclined"],
    "distinguished": ["distinguish"],
    "followed": ["follow"],
}
DISQUAL = ["objection", "assignment of error", "point of error", "motion is overruled", "motions are overruled",
           "decline to overrule", "declines to overrule", "need not overrule", "would overrule", "dissent would",
           "as stated in", "as recognized in"]


def cue_ok(kind, quote):
    q = quote.lower()
    return any(c in q for c in CUES.get(kind, []))
