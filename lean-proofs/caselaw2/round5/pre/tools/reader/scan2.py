"""Round 2 candidate pass: scan.py with (a) the round-2 part map (common.part_map2: slip-opinion running heads,
stricter separate-opinion lines) and (b) wording families that v1 had no pattern for. No history candidates.

    python -X utf8 scan2.py <repo>        -> data/reader_work/cand2/<repo>.jsonl.gz   (same record format as scan.py)

New families (round2/recall.md, diagnosis class b "scan"):
  nolonger   "can no longer be regarded as the law", "is no longer controlling / authority / tenable / viable"
  overturn   "we overturn", "is overturned", "overthrown"
  disavow    "we disavow", "jettison", "discard(ed)"
  reject     "we (now) reject the rule / holding / doctrine / distinction / proposition ... of X"
  abandon    "abandon the rule / test / doctrine ..." (v1 only had "we abandon the rule")
  survive    "cannot survive", "did not survive"
  wrongly    "wrongly / erroneously / incorrectly decided"
  depart     "we depart from"
The v1 families are kept, so that a sentence whose opinion part changes under the new part map is seen again.
Candidate ids (node:sentence start) are the same as v1's for the same sentence.
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import scan  # noqa: E402

OBJ = (r"(?:rule|holding|holdings|doctrine|reasoning|test|approach|view|analysis|dictum|dicta|standard|language|"
       r"distinction|proposition|rationale|principle|conclusion|statement|statements|suggestion|interpretation|"
       r"construction|decision|decisions|case|cases)")
scan.FAM.update({
    "nolonger": re.compile(r"\bno\s+longer\b[^.;\n]{0,70}?\b(?:law|authority|authoritative|controlling|binding|precedent|"
                           r"tenable|viable|vitality|followed|adhered|relied|regarded|considered|sound|valid)\b", re.I),
    "overturn": re.compile(r"\boverturn(?:s|ed|ing)?\b|\boverthrown\b", re.I),
    "disavow": re.compile(r"\bdisavow(?:s|ed|ing)?\b|\bjettison(?:s|ed|ing)?\b|\bdiscard(?:s|ed|ing)?\b", re.I),
    "reject": re.compile(r"\b(?:we|court)\s+(?:\w+\s+){0,3}?rejects?\s+(?:the|that|this|any|its|our|those|these)\s+"
                         r"(?:[\w“”\"’'\-]+\s+){0,5}?" + OBJ + r"\b", re.I),
    "abandon": re.compile(r"\babandon(?:s|ed|ing)?\s+(?:the|that|this|its|our|any|those|these)\s+(?:[\w“”\"’'\-]+\s+){0,5}?"
                          + OBJ + r"\b", re.I),
    "survive": re.compile(r"\b(?:cannot|can\s+no\s+longer|does\s+not|did\s+not|do\s+not|could\s+not|no\s+longer)\s+"
                          r"survive\b", re.I),
    "wrongly": re.compile(r"\b(?:wrongly|erroneously|incorrectly|improvidently)\s+decided\b", re.I),
    "depart": re.compile(r"\b(?:we|court)\s+(?:\w+\s+){0,3}?departs?\s+from\b", re.I),
})
scan.ANCH.update({
    "nolonger": (("no longer",), 5, 110), "overturn": (("overturn", "overthrown"), 5, 20),
    "disavow": (("disavow", "jettison", "discard"), 5, 20), "reject": (("reject",), 60, 130),
    "abandon": (("abandon",), 5, 130), "survive": (("survive",), 30, 10),
    "wrongly": (("wrongly decided", "erroneously decided", "incorrectly decided", "improvidently decided"), 5, 30),
    "depart": (("depart from", "departs from"), 60, 20),
})
scan.part_map = common.part_map2
scan.HIST_ANCH = ((), 0, 0)          # no same-case history candidates in this pass
scan.CAND_DIR = os.path.join(common.WORK, "cand2")

if __name__ == "__main__":
    scan.main(sys.argv[1])
