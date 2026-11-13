"""Round 2 act shapes: wordings of a court's own overruling that rules.act_shaped (v1) does not accept.

    shapes(sentence) -> [(position, shape name)]

v1 accepted "we overrule X", "X is (hereby|now|expressly ...) overruled", "to the extent ... overruled", "no longer
follow". The recall diagnosis (caselaw-lean-2/round2/recall.md) found the court's own words rejected as
"not act-shaped" or "procedural" in these general forms, which are added here. Every shape still needs the model
reading and a resolved target; the shapes only decide what is read.

  passive-adv      "that case is definitely overruled", "is, therefore, overruled", "is in effect overruled"
  be-and-is        "should be, and now are, overruled", "must be and is hereby overruled"
  regarded-as      "must be regarded as overruled", "is to be considered as overruled", "may be deemed overruled"
  decision-subj    "our decision today overrules X", "this holding necessarily overrules X"
  compelled        "we are constrained to overrule X", "we feel compelled to overrule", "we do not hesitate to overrule",
                   "we find it necessary to overrule", "it becomes necessary to overrule"
  conclude-modal   "we are convinced / persuaded / of opinion / conclude / think / hold that X should be overruled"
  no-longer-law    "X is no longer the law / good law / authority / controlling", "can no longer be regarded as
                   authority", "should no longer be followed / relied upon"
  other-verb       "we overturn / disavow / jettison / discard X", "X is hereby overturned / disavowed / discarded",
                   "we depart from X" (scan2 families)
  we-and-verb      "we agree and overrule Parratt to the extent that ..."
  in-gerund        "in disapproving that doctrine we do not hold ..." (the act is presupposed; target named in sentence)
  reject-rule      "we now reject the rule of Spector", "it is wiser to abandon the two-pronged test established by X"
                   (target named in the sentence)
  survive          "to the extent ... inconsistent with X, the latter cannot survive" (target named in the sentence)
  wrongly          "X was wrongly decided" said in the present by the court ("we hold / conclude / now believe that X
                   was wrongly decided")
  procedural-named a v1 act shape rejected only for a procedural word nearby ("despite those objections ... we think
                   the Friedlander case should be overruled"); kept when no procedural object follows the verb and a
                   case is named in the sentence (checked by the caller: a target named in the sentence)
"""
import re
import rules

V_PART = r"(?:overruled|disapproved|abrogated|receded\s+from|repudiated|abandoned|overturned|disavowed|discarded)"
V_PRES = r"(?:overrule|disapprove|abrogate|repudiate|abandon|overturn|disavow|discard|jettison)"
ADVW = (r"(?:now|hereby|therefore|thus|accordingly|consequently|necessarily|definitely|expressly|explicitly|specifically|"
        r"formally|squarely|plainly|clearly|distinctly|directly|substantially|practically|virtually|effectively|"
        r"completely|entirely|wholly|flatly|finally|also|likewise|too|in\s+effect|in\s+terms|in\s+substance|"
        r"in\s+principle|pro\s+tanto|to\s+that\s+extent|to\s+this\s+extent|for\s+that\s+reason|of\s+course|"
        r"in\s+all\s+respects|once\s+and\s+for\s+all|today|herewith|henceforth|hereafter|no\s+longer\s+authority\s+and)")
NEG_NEAR = re.compile(r"\b(?:not|never|nor|neither|whether|if|unless|until|hardly|scarcely|without|cannot|"
                      r"declin\w+|refus\w+|ask\w*|urg\w+|invit\w+|request\w*|argu\w+|contend\w*|insist\w*|suggest\w*|"
                      r"claim\w*|seek\w*|sought|would|could|might|dissent\w*|plurality)\b", re.I)
ARG_NEAR = re.compile(r"\b(?:whether|if|unless|until|ask\w*|urg\w+|invit\w+|request\w*|argu\w+|contend\w*|insist\w*|"
                      r"suggest\w*|claim\w*|assert\w*|maintain\w*|submit\w*|seek\w*|sought|would|could|might|"
                      r"dissent\w*|not\s+(?:say|hold|mean|suggest|conclude|agree|believe|think))\b", re.I)
BY_IN = re.compile(r"\s*,?\s*(?:by|in)\s+(?!(?:this|the\s+present|today|our)\b)", re.I)
MODAL = r"(?:should|must|ought\s+to|shall|will|may|can|is\s+to|are\s+to)"

RX = {
    "passive-adv": re.compile(r"\b(?:is|are|stands?)\s*,?\s*((?:" + ADVW + r"\s*,?\s*){1,3})(" + V_PART + r")\b", re.I),
    "be-and-is": re.compile(r"\b" + MODAL + r"\s+be\s*,?\s*(?:and\s+)?(?:(?:it|they|the\s+same)\s+)?(?:" + ADVW +
                            r"\s+)?(?:is|are)\s*,?\s*(?:" + ADVW + r"\s*,?\s*){0,2}(" + V_PART + r")\b", re.I),
    "regarded-as": re.compile(r"\b(?:is|are|be|stands?)\s+(?:\w+\s+){0,2}?(?:regarded|considered|deemed|treated|taken|"
                              r"held|viewed)\s+(?:as\s+|to\s+be\s+|to\s+have\s+been\s+|as\s+having\s+been\s+)?"
                              r"(?:" + ADVW + r"\s+){0,2}(" + V_PART + r")\b", re.I),
    "decision-subj": re.compile(r"\b(?:our|this|today['’]s|the\s+present)\s+(?:decision|holding|opinion|ruling|conclusion|"
                                r"judgment|case)\s+(?:today\s+|here\s+|now\s+|necessarily\s+|therefore\s+|thus\s+|also\s+|"
                                r"expressly\s+|in\s+effect\s+){0,2}(" + V_PRES + r"s)\b", re.I),
    "compelled": re.compile(r"\b(?:we|this\s+court)\s+(?:(?:now|therefore|thus|accordingly|also)\s+)?(?:are|is|feel|feels|"
                            r"find\s+ourselves|deem\s+it|find\s+it|think\s+it|consider\s+it|have\s+no\s+(?:hesitation|"
                            r"hesitancy)\s+in|do\s+not\s+hesitate\s+to|have\s+concluded\s+to|have\s+determined\s+to|"
                            r"have\s+decided\s+to|take\s+this\s+(?:occasion|opportunity)\s+to|deem\s+it\s+(?:proper|best|"
                            r"necessary)\s+to)\s+(?:(?:constrained|compelled|obliged|forced|bound|impelled|required|"
                            r"necessary|proper|appropriate|our\s+duty|best)\s+(?:to\s+)?)?(" + V_PRES + r"|overruling|"
                            r"disapproving)\b|\bit\s+(?:is|becomes|has\s+become)\s+(?:now\s+)?(?:necessary|our\s+duty|"
                            r"proper)\s+to\s+(" + V_PRES + r")\b", re.I),
    "conclude-modal": re.compile(r"\b(?:we|this\s+court)\s+(?:(?:now|therefore|thus|accordingly|also|are|is|have|has)\s+){0,2}"
                                 r"(?:convinced|persuaded|satisfied|of\s+(?:the\s+)?opinion|conclude[sd]?|think|thinks|"
                                 r"hold|holds|believe|believes|agree|agrees|determine[sd]?|decide[sd]?)\s+"
                                 r"(?:,?\s*(?:however|therefore|accordingly)\s*,?\s*)?(?:that\s+)?[^.;]{0,220}?\b"
                                 + MODAL + r"\s+(?:now\s+|therefore\s+|accordingly\s+)?be\s+(?:" + ADVW + r"\s+)?("
                                 + V_PART + r")\b", re.I),
    "no-longer-law": re.compile(
        r"\b(?:is|are|can|may|should|will|must|shall|ought\s+to|it)\s+(?:therefore\s+|thus\s+|accordingly\s+)?no\s+longer\s+"
        r"(?:to\s+)?(?:be\s+)?(?:(regarded|considered|deemed|treated|viewed|accepted|recognized|followed|adhered\s+to|"
        r"relied\s+(?:up)?on|applied)\b|(?:a\s+|an\s+|the\s+|of\s+|any\s+|good\s+|sound\s+|valid\s+|binding\s+|"
        r"controlling\s+|correct\s+){0,3}(law|authority|authoritative|controlling|binding|precedent|sound|valid|viable|"
        r"tenable|force|vitality)\b)", re.I),
    "other-verb": re.compile(r"\b" + rules.SUBJ + r"((?:\s+" + rules.ADV + r"){0,4})\s+(overturn|disavow|jettison|discard|"
                             r"depart\s+from|withdraw\s+from|abandon|repudiate)s?\b|\b(?:is|are|be|stands?)\s+(?:" + ADVW +
                             r"\s+){0,2}(overturned|disavowed|discarded|abandoned|repudiated)\b", re.I),
    "we-and-verb": re.compile(r"\b" + rules.SUBJ + r"\s+(?:\w+\s+){1,3}?and\s+(?:now\s+|hereby\s+|therefore\s+|"
                              r"accordingly\s+|expressly\s+)?(" + V_PRES + r")\b", re.I),
    "in-gerund": re.compile(r"\b(?:in|by)\s+(?:thus\s+|now\s+|so\s+|expressly\s+)?(overruling|disapproving|abandoning|"
                            r"repudiating|rejecting|overturning)\b[^.;]{0,160}?\b(?:we|this\s+court)\b", re.I),
    "reject-rule": re.compile(r"\b" + rules.SUBJ + r"((?:\s+" + rules.ADV + r"){0,4})\s+(reject|abandon|discard)s?\s+"
                              r"(?:the|that|this|any|its|our|those|these)\s+(?:[\w“”\"’'\-]+\s+){0,5}?(?:rule|holding|holdings|doctrine|reasoning|test|approach|view|analysis|dictum|dicta|standard|language|distinction|proposition|rationale|principle|conclusion|statement|statements|suggestion|interpretation|construction|decision|decisions|case|cases)\b|"
                              r"\b(?:wiser|better|necessary|appropriate|time)\s+to\s+(abandon|reject|discard|overrule)\s+"
                              r"(?:the|that|this|those|these)\s+(?:[\w“”\"’'\-]+\s+){0,5}?(?:rule|holding|holdings|doctrine|reasoning|test|approach|view|analysis|dictum|dicta|standard|language|distinction|proposition|rationale|principle|conclusion|statement|statements|suggestion|interpretation|construction|decision|decisions|case|cases)\b", re.I),
    "survive": re.compile(r"\b(?:cannot|can\s+no\s+longer|does\s+not|did\s+not|do\s+not|could\s+not|no\s+longer)\s+"
                          r"(survive)\b", re.I),
    "wrongly": re.compile(r"\b(?:we|this\s+court)\s+(?:(?:now|therefore|thus|accordingly|also|are|is|have|has)\s+){0,2}"
                          r"(?:convinced|persuaded|satisfied|of\s+(?:the\s+)?opinion|conclude[sd]?|think|thinks|hold|"
                          r"holds|believe|believes|agree|agrees)\s+(?:that\s+)?[^.;]{0,200}?\b(?:was|were)\s+"
                          r"(?:wrongly|erroneously|incorrectly|improvidently)\s+decided\b|\b(?:was|were)\s+(?:wrongly|"
                          r"erroneously|incorrectly)\s+decided\s*,?\s+and\s+(?:is|are|should|must|we)\b", re.I),
}
NEED_NAMED = {"other-verb", "reject-rule", "survive", "in-gerund"}
MODALPRE = re.compile(r"\b(?:should|must|ought\s+to|shall|will|would|could|might|may|can|cannot|to)\s*$", re.I)


def shapes(s):
    """Positions in s of a round-2 act shape: [(pos, name)]. Negated, conditional, requested and reported uses are
    dropped (the same guards as v1: no "by/in <case>" straight after the participle, no argument/negation words in the
    120 characters before the verb)."""
    out = []
    for name, rx in RX.items():
        for m in rx.finditer(s):
            g = [i for i in range(1, (m.lastindex or 0) + 1) if m.group(i) and m.start(i) >= 0]
            pos = m.start(g[-1]) if g else m.start()
            if name in ("passive-adv", "be-and-is", "regarded-as", "conclude-modal") or (name == "other-verb" and m.group(3)):
                if BY_IN.match(s, m.end()):
                    continue  # "is now overruled by Y": a report (or a statute acting), not this court's act
            pre = s[max(0, m.start() - 120):m.start()]
            # the clause the verb sits in: from the last ; or : or sentence-internal full stop
            clause = re.split(r"[;:]\s|\.\s+(?=[A-Z])", pre)[-1]
            if name in ("passive-adv", "regarded-as", "other-verb", "decision-subj", "we-and-verb", "reject-rule"):
                if NEG_NEAR.search(clause[-70:]):
                    continue
            if name in ("no-longer-law", "survive"):
                # the phrase carries its own negation; only a party's argument, a question or a condition is dropped
                if ARG_NEAR.search(clause[-90:]):
                    continue
            if name in ("compelled", "conclude-modal", "wrongly", "be-and-is"):
                if re.search(r"\b(?:not|never|nor|whether|if|unless|ask\w*|urg\w+|argu\w+|contend\w*|would|dissent\w*)\b",
                             clause[-50:] + " " + m.group(0)[:25], re.I) and not re.search(
                                 r"do(?:es)?\s+not\s+hesitate|no\s+hesita", m.group(0), re.I):
                    continue
            if name == "passive-adv" and MODALPRE.search(s[max(0, m.start() - 12):m.start()]):
                continue
            out.append((pos, name))
    return out


def classify2(s, fams, part, named_in_sentence):
    """v2 verdict for a candidate that v1 rejected: ('llm', 'v2:<shape>') or ('reject', reason).
    named_in_sentence: a resolvable earlier decision is cited or named in the sentence itself."""
    if part.startswith(("dissent", "concurrence")) or part == "headmatter":
        return "reject", "separate-or-head"
    sh = shapes(s)
    keep = []
    for pos, name in sh:
        if name in NEED_NAMED and not named_in_sentence:
            continue
        if rules.NOISE_AFTER.match(s, pos):
            continue  # "is therefore overruled ... the motion": a procedural object follows
        if rules.is_report(s, pos) and name not in ("decision-subj", "compelled", "conclude-modal"):
            continue
        if rules.NOISE_BEFORE.search(s[max(0, pos - 90):pos]) and not named_in_sentence:
            continue
        keep.append(name)
    if keep:
        return "llm", "v2:" + keep[0]
    # v1 shape lost only to a procedural word before the verb, with a case named in the sentence
    if named_in_sentence:
        for f in fams:
            if f not in ("overrule", "disapprove"):
                continue
            for pos, how in rules.act_shaped(s, f):
                if rules.NOISE_AFTER.match(s, pos) or (how != "law" and rules.is_report(s, pos)):
                    continue
                if rules.NOISE_BEFORE.search(s[max(0, pos - 90):pos]):
                    return "llm", "v2:procedural-named"
    return "reject", "v2-not-act-shaped"


# ---- round 2 cue table -----------------------------------------------------------------------------------------
# What a certificate quote must contain, per kind, for the rows written in round 2. It is the checker's table
# (Certificate.lean `cues`, ref VERBS) with the additions proposed in round2/recall.md; certify2.py refuses a row whose
# quote the checker would not pass. v1's reader table (rules.CUES) was wider than the checker's for overruled
# ("repudiat", "abandon", "no longer follow" ...) and declinedToFollow, which cost 1,043 rows at the checker.
CUES2 = {
    "overruled": ["overrul", "repudiat", "abandon", "no longer", "overturn", "disavow", "discard", "reject",
                  "not survive", "cannot survive", "wrongly decided"],
    "disapproved": ["disapprov"],
    "recededFrom": ["recede"],
    "abrogated": ["abrogat"],
    "supersededByEnactment": ["supersed", "legislatively overrul", "abrogated by statute", "congress responded",
                              "in response to", "abrogat"],
    "limited": ["limit"],
    "questioned": ["question", "doubt", "no longer"],
    "criticized": ["critici"],
    "distinguished": ["distinguish"],
    "followed": ["follow", "adhere", "bound by", "controlled by", "binding"],
    "declinedToFollow": ["declin", "not follow", "refuse", "disagree", "reject", "not persuaded", "no longer",
                         "not inclined", "unwilling", "not adhere", "not be followed"],
}
# the checker's disqualifier phrases for status-changing kinds (Certificate.lean `disqualifiers`, ref DISQUALIFY_TREAT)
DISQUAL2 = ("point of error", "points of error", "assignment of error", "assignments of error", "issue is overruled",
            "issues are overruled", "point is overruled", "points are overruled", "overrule appellant",
            "overrule appellee", "overrule his ", "overrule her ", "overrule their ", "complaint is overruled",
            "overruled by", "overruled on other grounds by", "overruled in part by", "abrogated by",
            "abrogated on other grounds by", "disapproved by", "disapproved of by", "disapproved on other grounds",
            "receded from by", "as stated in", "as recognized in", "recognized as abrogated", "decline to overrule",
            "declined to overrule", "declining to overrule", "refuse to overrule", "refused to overrule", "not overrule",
            "would overrule", "should not be overruled", "urges us to overrule", "asks us to overrule")


# round 4: one cue table for the reader and both checkers (tools/caselaw2/cues/cue_table.json -> cue_table.py)
from cue_table import VERBS as _VERBS, TREAT_KINDS as _TREAT_KINDS, DISQUALIFY_TREAT as _DQ  # noqa: E402
CUES2 = {k: list(_VERBS[k]) for k in _TREAT_KINDS}
DISQUAL2 = tuple(_DQ)


def cue_ok2(kind, quote):
    q = quote.lower()
    return any(c in q for c in CUES2.get(kind, []))
