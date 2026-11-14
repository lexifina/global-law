"""state8 rule R8S: repairs of the treatments reader's cheap rules (tools/caselaw2/reader/rules.py), as a candidate
generator over the sentences the reader rejected. Each repair is general (no case, citation or party is named):

  REP  `rules.REPORT` reads "overruled in so far as ..." / "overruled in that respect" / "overruled in this
       particular" as "overruled in <case>" (a report of another case's act). A verb followed by a limiting phrase
       is not a report.
  NOI  `rules.NOISE_BEFORE` marks a verb as procedural when a word such as "ruling", "error", "ground", "point" stands
       within 60 characters before it. Not procedural when the word is the subject naming a decision ("the ruling(s)
       / decision(s) / holding(s) in|of <case>", "the ruling here made", "the ruling in this case") or part of a party
       designation ("plaintiff in error", "defendant in error").
  COM  a comma clause between the subject / auxiliary and the verb ("We, therefore, disapprove", "is, on review,
       expressly overruled", "are, therefore, now overruled", "must be, and hereby are, overruled", "this court now,
       upon a review of ..., overrules"): commas of a short inserted clause are read as spaces, and "on review
       (thereof)", "upon (a) review (of ...)", "after (careful|mature|full) consideration", "distinctly",
       "squarely", "directly" are allowed adverbs.
  INF  own act in an infinitive / gerund after a duty or resolve phrase of the court: "it is our duty to overrule",
       "we have no hesitation in overruling", "we feel constrained/compelled/bound/obliged to overrule", "we now
       proceed to overrule", with no negation before it.
  PF   part map: in a Majority section, a "<judge>, J., concurring." line inside the opening block (the section's
       first 400 characters, before any prose of the opinion) records a judge joining the opinion; it does not start
       a separate opinion. A candidate rejected `separate-opinion` only because of such a line is re-classified as
       majority.
The original rules are imported unchanged; a sentence is RESCUED when the original classify() rejects it and the
repaired one sends it to the reader. No answer-key file is read.
"""
import os, re, sys

READER = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/reader")
if READER not in sys.path:
    sys.path.insert(0, READER)
import rules as R  # noqa: E402

LIMIT_AFTER = re.compile(r"\s*,?\s*(?:in\s+so\s+far|insofar|so\s+far|in\s+(?:this|that|these|those|so\s+many|some)\s+"
                         r"(?:respects?|particulars?|points?|regards?)|in\s+part|in\s+all\s+respects|in\s+toto|"
                         r"to\s+(?:the|that|this)\s+extent)", re.I)
NOISE_WORD = re.compile(r"(objection|motion|exception|demurrer|plea|assignment|point|contention|petition|request|"
                        r"rehearing|ruling|argument|claim|issue|protest|challenge|application|suggestion|"
                        r"specification|ground|error|complaint|proposition|finding|recommendation|cross-point)s?\b",
                        re.I)
SUBJ_DECISION = re.compile(r"\s+(?:of\s+this\s+court\s+|of\s+the\s+supreme\s+court\s+|announced\s+|made\s+|laid\s+down\s+|"
                           r"rendered\s+)?(?:in|of)\s+(?:the\s+(?:case|cases|decision)\s+of\s+|the\s+[A-Z]|[A-Z0-9])|"
                           r"\s+(?:here|now|herein)\s+made|\s+in\s+(?:this|the\s+present|the\s+instant)\s+case", re.I)
PARTY_ERR = re.compile(r"(?:plaintiffs?|defendants?)\s+in\s+$", re.I)
COMMA_CLAUSE = re.compile(r",\s*((?:on|upon)\s+(?:a\s+|further\s+)?review(?:\s+thereof|\s+of\s+[^,.;]{1,90})?|"
                          r"after\s+(?:careful|mature|full|due|further)\s+consideration|on\s+(?:further\s+)?consideration|"
                          r"therefore|accordingly|thus|now|then|however|hereby|consequently|also|likewise|"
                          r"in\s+our\s+(?:opinion|judgment)|we\s+think|so\s+far\s+as\s+[^,.;]{1,90}|"
                          r"to\s+(?:that|this|the\s+same)\s+extent|pro\s+tanto|and\s+(?:hereby\s+|now\s+)?(?:is|are)|"
                          r"(?:therefore|accordingly|thus)\s+(?:now|hereby))\s*,", re.I)
EXTRA_ADV = (r"(?:on\s+review(?:\s+thereof)?|upon\s+(?:a\s+|further\s+)?review(?:\s+thereof|\s+of\s+[^,.;]{1,90}?)?|"
             r"after\s+(?:careful|mature|full|due|further)\s+consideration|distinctly|squarely|directly|"
             r"and\s+(?:hereby\s+|now\s+)?(?:is|are))")
BASE_ADV = (r"(?:hereby|now|expressly|specifically|therefore|accordingly|herewith|formally|explicitly|today|thus|"
            r"necessarily|in\s+all\s+respects|pro\s+tanto|to\s+that\s+extent|to\s+this\s+extent|insofar|partially|"
            r"in\s+part|also|likewise|similarly|(?:modified|disapproved|questioned|criticized|limited|overruled|"
            r"overturned|receded\s+from)\s+and)")
PASSIVE2 = re.compile(r"\b(?:is|are|be|stands?|remains?)\s+((?:(?:" + EXTRA_ADV + r"|" + BASE_ADV +
                      r")\s+){0,4})(overruled|disapproved|receded\s+from|abrogated)\b", re.I)
WE2 = re.compile(r"\b(?:we|this\s+court|the\s+court)\b\s+((?:(?:now|therefore|accordingly|hereby|thus|expressly|"
                 + EXTRA_ADV + r")\s+){1,4})(overrules?|disapproves?|recedes?\s+from|abrogates?)\b", re.I)
INF = re.compile(r"\b(?:it\s+is\s+(?:our|the)\s+duty\s+(?:of\s+this\s+court\s+)?to|(?:we|this\s+court)\s+(?:have|has|feel|"
                 r"are|is|deem\s+it|think\s+it|now)?\s*(?:no\s+hesitation\s+in|constrained\s+to|compelled\s+to|bound\s+to|"
                 r"obliged\s+to|proceed\s+to|(?:our|its)\s+duty\s+to|proper\s+to|best\s+to|necessary\s+to|"
                 r"(?:it\s+)?(?:our|its)\s+duty\s+to))\s+(overrul(?:e|ing)|disapprov(?:e|ing)|reced(?:e|ing)\s+from|"
                 r"abrogat(?:e|ing))\b", re.I)
NEG_NEAR = re.compile(r"\b(?:not|never|nor|no\s+need|unnecessary|decline|refuse|whether|if|unless|would|should\s+we|"
                      r"ask|asks|asked|urge|urges|urged|contend|argue)\b", re.I)


def de_comma(s):
    """Read the commas of a short inserted clause as spaces (length kept, so offsets hold)."""
    out = s
    for _ in range(4):
        # keep the closing comma for a following clause; the stray one is removed below
        new = COMMA_CLAUSE.sub(lambda m: " " + m.group(1) + ",", out)
        if new == out:
            break
        out = new
    out = re.sub(r"\b(is|are|be|we|court|hereby|now|therefore|accordingly|thus|review|thereof|consideration|"
                 r"extent|tanto|also|likewise)\s*,", lambda m: m.group(1) + " ", out, flags=re.I)
    # "We, therefore, disapprove": a comma pair right after the subject
    out = re.sub(r"\b(we|this\s+court)\s*,\s*((?:therefore|accordingly|thus|now|then|hereby|also|likewise)"
                 r"(?:\s+\w+ly)?)\s*,", lambda m: m.group(1) + " " + m.group(2) + " ", out, flags=re.I)
    return out


def is_report2(s, a):
    if LIMIT_AFTER.match(s, re.match(r"\w+", s[a:]).end() + a if re.match(r"\w+", s[a:]) else a):
        # the verb is followed by a limiting phrase: only a citator form before it makes it a report
        return bool(R.CITATOR_BEFORE.search(s, max(0, a - 40), a) or R.PAST.search(s[max(0, a - 50):a + 25]))
    return R.is_report(s, a)


def noise_before2(s, pos):
    lo = max(0, pos - 90)
    for m in NOISE_WORD.finditer(s, lo, pos):
        if pos - m.end() > 60 or re.search(r"\.\s+[A-Z][a-z]", s[m.end():pos]):
            continue  # as rules.NOISE_BEFORE: at most 60 characters, no sentence-like break between
        w = m.group(1).lower()
        if w in ("ruling", "error", "ground", "point", "finding", "application") or m.group(0).lower() in ("rulings",):
            if PARTY_ERR.search(s[max(0, m.start() - 25):m.start()]):
                continue
            if w in ("ruling",) and SUBJ_DECISION.match(s, m.end()):
                continue
        return True
    return False


def shapes2(s, fams):
    """Own-act shapes of the repaired rules: [(fam, how)]."""
    s2 = de_comma(s)
    out = []
    fam_of = {"overruled": "overrule", "disapproved": "disapprove", "abrogated": "abrogate"}
    for f in fams:
        for pos, how in R.act_shaped(s2, f):
            out.append((f, pos, how))
    for m in PASSIVE2.finditer(s2):
        v = m.group(2).lower()
        f = "recede" if v.startswith("reced") else fam_of.get(v)
        after = s2[m.end():m.end() + 40]
        if re.match(r"\s*(?:,\s*)?(?:by|in)\s", after, re.I) and not LIMIT_AFTER.match(after):
            continue
        pre = s2[max(0, m.start() - 30):m.start()]
        if re.search(r"\bnot\s*$", pre, re.I):
            continue
        if re.search(r"\b(?:should|must|ought\s+to|shall|will|would|could|might|may|can|cannot|to)\s*$", pre, re.I):
            # modal passive (as rules.act_shaped): an act only without argument / negation words before it
            if R.NEG_BEFORE.search(s2[max(0, m.start() - 160):m.start()]):
                continue
        elif re.search(r"\b(?:whether|if|unless|not|when|whenever)\b", s2[max(0, m.start() - 60):m.start()], re.I):
            continue
        if R.PAST.search(s2[max(0, m.start() - 30):m.end()]):
            continue
        out.append((f, m.start(2), "passive2"))
    for m in WE2.finditer(s2):
        v = m.group(2).lower()
        f = "recede" if v.startswith("reced") else ("overrule" if v.startswith("overrul") else
                                                    "disapprove" if v.startswith("disapprov") else "abrogate")
        if NEG_NEAR.search(m.group(1) or ""):
            continue
        out.append((f, m.start(2), "we2"))
    for m in INF.finditer(s2):
        if NEG_NEAR.search(s2[max(0, m.start() - 50):m.start()]):
            continue
        v = m.group(1).lower()
        f = "recede" if v.startswith("reced") else ("overrule" if v.startswith("overrul") else
                                                    "disapprove" if v.startswith("disapprov") else "abrogate")
        out.append((f, m.start(1), "inf"))
    keep = []
    for f, pos, how in out:
        if f in ("overrule", "disapprove") and (noise_before2(s2, pos) or R.NOISE_AFTER.match(s2, pos)):
            continue
        if is_report2(s2, pos):
            continue
        keep.append((f, how))
    return keep


def rescue(sent, fams, part, reject_reason, part_fixed=False):
    """None, or the rescue tag ("PF", "REP", "NOI", "COM", "INF" + how) for a sentence the reader rejected."""
    if reject_reason == "separate-opinion":
        if not part_fixed:
            return None
        v, why = R.classify(sent, fams, "majority")
        if v == "llm":
            return "PF:" + why
        sh = shapes2(sent, fams + [f for f in ("overrule", "disapprove") if f not in fams])
        return ("PF+" + sh[0][1]) if sh else None
    if reject_reason in ("headmatter", "opinion-substitution"):
        return None
    sh = shapes2(sent, fams + [f for f in ("overrule", "disapprove") if f not in fams])
    if not sh:
        return None
    return reject_reason + ">" + sh[0][1]
