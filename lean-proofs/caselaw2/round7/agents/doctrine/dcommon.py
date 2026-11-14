"""Round 7, agent doctrine: shared lists and checks (proposals; the certified lists are the `lean` agent's
`doctrine_reject`, `doctrine_tie`, `disqualify_joined` in tools/caselaw2/cues/cue_table.json once they exist)."""
import json, os, re

CUE_JSON = os.path.expanduser("~/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json")

# proposed doctrine_reject (substring tests on the normalised lower-cased main quote)
PROP_REJECT = ["has no place", "have no place", "no proper place", "no longer", "is rejected", "are rejected",
               "be rejected", "we reject", "we now reject", "hereby reject", "accordingly reject", "therefore reject",
               "expressly reject", "repudiat", "abandon", "is overruled", "are overruled", "be overruled",
               "we overrule", "hereby overrule", "discard", "disapprove", "disavow", "abolish", "renounce",
               "jettison", "depart from", "departing from", "recede from", "decline to follow", "unsound",
               "not the law", "cannot stand", "cannot survive", "is abrogated", "are abrogated"]
# proposed doctrine_tie (substring tests on the normalised lower-cased joined quote)
PROP_TIE = ["doctrine of", "doctrine announced", "doctrine established", "rule of", "rule announced", "rule laid down",
            "announced in", "established in", "adopted in", "laid down in", "the rule in", "first announced",
            "originated in", "enunciated in", "formulated in", "set forth in", "articulated in", "test of",
            "test announced", "principle of", "principle announced", "standard of", "formula of", "exception of",
            "presumption of", "first stated", "made its appearance", "announced by", "established by", "adopted by",
            "laid down by", "first adopted", "first articulated", "first enunciated"]

_ASCII_LOWER = {c: c + 32 for c in range(65, 91)}


def lower(s):
    return s.translate(_ASCII_LOWER)


def nq(s):
    """Normalised lower-cased quote, as the checker reads it (tab/newline/CR -> space, ASCII lower case)."""
    return lower(s.replace("\t", " ").replace("\n", " ").replace("\r", " "))


def cue_table():
    with open(CUE_JSON, encoding="utf-8") as f:
        return json.load(f)


def lists(union=True):
    """(reject, tie, disq_main, disq_joined, reject_lean): the cue table's lists when present, else the proposals.
    With union=True the reject and tie lists are the cue table's plus the proposals (items are judged on the union;
    `reject_lean` is the cue table's own list, recorded per item)."""
    d = cue_table()
    rej_l = d.get("doctrine_reject") or []
    tie_l = d.get("doctrine_tie") or []
    rej = sorted(set(rej_l) | set(PROP_REJECT)) if union or not rej_l else rej_l
    tie = sorted(set(tie_l) | set(PROP_TIE)) if union or not tie_l else tie_l
    dq_main = list(d.get("disqualify_treat", [])) + list(d.get("disqualify_operative", []))
    dq_j = list(d.get("disqualify_treat", [])) + list(d.get("disqualify_joined") or [])
    return rej, tie, dq_main, dq_j, rej_l, tie_l


def label_ok(d):
    """DESIGN7 2.3: >= 2 words, >= 8 characters after normalising (we also require 2 space-separated words)."""
    d = nq(d).strip()
    return len(d.split()) >= 2 and len(d) >= 8


def compact_label(d):
    return re.sub(r"[^0-9a-z]", "", nq(d))
