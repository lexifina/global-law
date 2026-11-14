"""fjc8 rule S1 (scope): a dismissal that is the consequence of the reversal / vacatur ("Reversed; the petition is
dismissed", "vacate ... and remand with instructions to dismiss the complaint") does not make a whole-judgment
reversal partial.

Round 6's `kind_of` reads any "dismissed" next to a reversal as a second act (scope unknown). Here "dismiss" counts
as a second act only when it is not one of these consequence forms:
  - "<petition | complaint | action | suit | case | cause | claim(s) | indictment | charge(s) | bill | libel |
    proceeding(s) | count(s) ...> is / are / be dismissed" (the pleading, not the appeal), and no "appeal" in the
    same clause;
  - "(with) instructions / directions (to the district court) to dismiss ...", "remand(ed) ... to / for dismiss(al)",
    "direct(ing) (the district court) to dismiss", "order(ing) ... dismissed", "that ... be dismissed".
A partial word (round 6 IN_PART) still makes scope unknown; "counts" / "as to" in the consequence clause is read
only when it is outside the consequence clause (the dismissed clause is cut out before IN_PART is tested).
`patch()` swaps round 6's `kind_of` for this one in the imported below_other module.
"""
import re

CONSEQ = re.compile(
    r"\b(?:the\s+|his\s+|her\s+|their\s+|its\s+|this\s+|that\s+|said\s+|plaintiffs?['’]?s?\s+|defendants?['’]?s?\s+|"
    r"petitioners?['’]?s?\s+|appellants?['’]?s?\s+|habeas\s+|amended\s+|entire\s+|remaining\s+|federal\s+|state\s+)*"
    r"(?:petitions?|complaints?|actions?|suits?|case|cause|claims?|indictments?|charges?|bills?|libels?|proceedings?|"
    r"counts?|informations?|counterclaims?|writs?)\b[^.;:]{0,60}?\b(?:is|are|be|being|will\s+be|shall\s+be|must\s+be)\s+"
    r"(?:hereby\s+|therefore\s+|accordingly\s+)?dismissed\b[^.;]*"
    r"|\b(?:with\s+)?(?:instructions?|directions?)\s+(?:\w+\s+){0,6}?(?:to\s+)(?:\w+\s+){0,3}?dismiss\w*\b[^.;]*"
    r"|\bremand\w*\s+(?:\w+\s+){0,8}?(?:to|for)\s+(?:the\s+)?(?:\w+\s+){0,2}?dismiss\w*\b[^.;]*"
    r"|\bdirect(?:ing|ed)?\s+(?:\w+\s+){0,6}?to\s+dismiss\w*\b[^.;]*"
    r"|\border(?:ing|ed)?\s+(?:\w+\s+){0,6}?dismissed\b[^.;]*"
    r"|\bthat\s+(?:\w+\s+){0,8}?be\s+dismissed\b[^.;]*", re.I)
APPEAL_WORD = re.compile(r"\bappeals?\b|\bcross[- ]appeals?\b|\bcertiorari\b|\bwrit\s+of\s+error\b", re.I)


def make_kind_of(BO):
    orig = BO.kind_of

    def kind_of(kinds, sent):
        ks = set(kinds)
        if "dismissed" in ks and ({"reversed", "vacated"} & ks):
            cut = sent
            hit = False
            for m in CONSEQ.finditer(sent):
                if APPEAL_WORD.search(m.group(0)):
                    continue
                hit = True
                cut = cut.replace(m.group(0), " ")
            if hit and not re.search(r"\bdismiss", cut, re.I):
                ks.discard("dismissed")
                return orig(ks, cut)
        return orig(kinds, sent)
    kind_of.orig = orig
    return kind_of


def patch(BO):
    if not hasattr(BO.kind_of, "orig"):
        BO.kind_of = make_kind_of(BO)
    return BO
