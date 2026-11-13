"""Passage-classification tasks for llm_run.py. Each task: system, schema, user(row) -> str, key(row) -> str."""


def _obj(props, req=None):
    return {"type": "object", "additionalProperties": False, "properties": props,
            "required": req or list(props)}


def _win(r, n=2, cut=1300):
    ws = r.get("windows") or []
    out = []
    for i, w in enumerate(ws[:n]):
        if len(w) > 2 * cut:
            mid = len(w) // 2
            w = w[mid - cut:mid + cut]
        out.append("--- passage %d ---\n%s" % (i + 1, w))
    return "\n".join(out) if out else "(no passage found)"


# ---- pattern 1: zombie precedent ---------------------------------------------------------------------------------

ZOMBIE_SYS = """You check how a court opinion uses an earlier decision that had already been overruled, abrogated, \
disapproved, reversed or vacated before the opinion was written. You are given the earlier decision, the later event \
that negated it (with the negating court's own words when we have them), and passages of the citing opinion around \
each place it cites the earlier decision. Answer from the passages only.

Definitions:
- same_case: the citing opinion is part of the same litigation as the earlier decision (e.g. on remand, a later appeal \
in the same case, or the court reviewing that very decision).
- acknowledges: the passage itself says, near the citation, that the earlier decision was overruled / abrogated / \
reversed / vacated / disapproved / superseded / questioned, or cites it with that subsequent history, or cites the \
negating decision for the same point.
- use: "relies" = the citing court uses the earlier decision as authority for a legal proposition it applies; \
"other" = mentioned only for facts, procedural history, background, a party's argument, a dissent's view, or to \
reject or distinguish it; "not_found" = the passages do not show the citation.
- negated_point: compare the proposition the citing court takes from the earlier decision with the NEGATING WORDS. \
"yes" only if the negating words show that this proposition (or the whole decision, without limitation) is what was \
overruled, abrogated or disapproved; "no" if the negating words are about a different point or holding, or are \
limited ("to the extent", "insofar as", "on this point") to something else; "unclear" if the negating words are \
missing, generic ("any holding to the contrary") or do not let you tell. Do not guess from the case name or from \
your own knowledge. For a reversal or vacatur of the whole decision, any proposition counts as "yes" unless the \
negating words show it was on other grounds or only in part.
- zombie: true only if use = "relies", acknowledges = false, same_case = false and negated_point = "yes"."""

ZOMBIE_SCHEMA = _obj({
    "same_case": {"type": "boolean"},
    "acknowledges": {"type": "boolean"},
    "use": {"type": "string", "enum": ["relies", "other", "not_found"]},
    "negated_point": {"type": "string", "enum": ["yes", "no", "unclear"]},
    "zombie": {"type": "boolean"},
    "proposition": {"type": "string", "description": "the proposition the citing court takes from it, <= 25 words"},
    "reason": {"type": "string", "description": "<= 30 words"},
})


def zombie_user(r):
    neg = r.get("wkind", "?")
    return ("EARLIER DECISION: %s, %s (%s, decided %s)\n"
            "NEGATING EVENT: %s on %s by %s, %s\n"
            "NEGATING WORDS: %s\n"
            "CITING OPINION: %s, %s (%s, decided %s)\n\n%s"
            % (r.get("cited_name"), r.get("cited_cite"), r.get("cited_court_name"), r.get("cited_date"),
               neg, r.get("neg_from"), r.get("actor_name"), r.get("actor_cite"), r.get("wquote", "-")[:400],
               r.get("citing_name"), r.get("citing_cite"), r.get("citing_court_name"), r.get("citing_date"),
               _win(r)))


# ---- pattern 2: unpublished treated as binding ---------------------------------------------------------------------

UNPUB_SYS = """You check how a court opinion uses an earlier decision that was unpublished (not designated for \
publication, a table or summary decision, or a memorandum opinion) and so, under the rules of the court that issued \
it, is not binding precedent (and may not be citable at all). You are given the earlier decision, the rule status we \
computed, and passages of the citing opinion around the citation. Answer from the passages only.

- treats_as_binding: the citing court says or plainly treats the unpublished decision as binding or controlling \
precedent it must follow (e.g. "we are bound by X", "X controls", "under our precedent in X", "X forecloses", follows \
it as the law of the circuit/state) rather than as persuasive, illustrative or consistent authority.
- notes_unpublished: the passage itself marks the decision as unpublished / non-precedential / table / memorandum \
(e.g. "(unpublished)", "nonprecedential", "not binding but persuasive").
- same_case: the citing opinion is part of the same litigation (law of the case, earlier appeal in the same case).
- violation: treats_as_binding = true and same_case = false."""

UNPUB_SCHEMA = _obj({
    "treats_as_binding": {"type": "boolean"},
    "notes_unpublished": {"type": "boolean"},
    "same_case": {"type": "boolean"},
    "violation": {"type": "boolean"},
    "quote": {"type": "string", "description": "the words that show how it is used, <= 30 words"},
    "reason": {"type": "string", "description": "<= 30 words"},
})


def unpub_user(r):
    return ("UNPUBLISHED DECISION: %s, %s (%s, decided %s; publication: %s; force on the citing court computed as: %s)\n"
            "CITING OPINION: %s, %s (%s, decided %s)\n\n%s"
            % (r.get("cited_name"), r.get("cited_cite"), r.get("cited_court_name"), r.get("cited_date"),
               r.get("cited_pub"), r.get("force", "?"), r.get("citing_name"), r.get("citing_cite"),
               r.get("citing_court_name"), r.get("citing_date"), _win(r)))


# ---- pattern 3: panel overrules panel ------------------------------------------------------------------------------

PANEL_SYS = """A US court of appeals follows the prior-panel rule: a three-judge panel is bound by an earlier published \
panel decision of the same court unless the earlier decision has been overruled by the court en banc or by the Supreme \
Court, or an intervening Supreme Court (or en banc, or for state law the state high court) decision is clearly \
irreconcilable with it. Some courts also let a panel overrule after circulating the opinion to all active judges \
(e.g. 7th Cir. Rule 40(e), D.C. Cir. "Irons footnote", 2d Cir. "mini en banc"), or an intervening statute changes the \
law. You are given a later decision of the same court and the words in which it treats the earlier decision. Answer \
from the text only.

- departs: the later court itself overrules, abrogates, recedes from, or refuses to follow the earlier decision's \
holding (not just distinguishes, limits, or notes that another court did so).
- bench: the deciding bench of the later decision as shown by the text ("panel", "en_banc", "unclear").
- justification: the reason given for being free to depart: "intervening_supreme_court" (or other intervening higher \
authority), "intervening_en_banc", "statute_change", "circulated_to_full_court", "earlier_case_conflicts_with_even_earlier" \
(prior panel rule: the earlier case itself was contrary to older binding precedent), "dicta_or_not_holding", \
"unpublished_or_nonbinding", "none" (no justification), "other".
- violation: departs = true, bench = "panel", and justification = "none" or "other" that is not a recognised exception."""

PANEL_SCHEMA = _obj({
    "departs": {"type": "boolean"},
    "bench": {"type": "string", "enum": ["panel", "en_banc", "unclear"]},
    "justification": {"type": "string", "enum": ["intervening_supreme_court", "intervening_en_banc", "statute_change",
                                                 "circulated_to_full_court", "earlier_case_conflicts_with_even_earlier",
                                                 "dicta_or_not_holding", "unpublished_or_nonbinding", "none",
                                                 "other"]},
    "violation": {"type": "boolean"},
    "reason": {"type": "string", "description": "<= 35 words"},
})


def panel_user(r):
    return ("COURT: %s\nEARLIER DECISION: %s, %s (decided %s)\nLATER DECISION: %s, %s (decided %s; bench in our data: %s)\n"
            "LATER DECISION'S WORDS (reader quote): %s\n\nHEAD OF THE LATER OPINION:\n%s\n\n%s"
            % (r.get("court_name"), r.get("cited_name"), r.get("cited_cite"), r.get("cited_date"), r.get("citing_name"),
               r.get("citing_cite"), r.get("citing_date"), r.get("bench"), r.get("quote", "-")[:500],
               (r.get("head") or "")[:1700], _win(r)))


# ---- pattern 4: superseded holding applied to post-effective conduct ----------------------------------------------

SUPER_SYS = """A statute superseded (overrode) a court decision's holding prospectively: conduct on or after the \
statute's effective date (or its stated retroactive date) is governed by the statute, not the old holding. You are \
given the old decision, the statute, and passages of a later opinion citing the old decision. Answer from the text.

- applies_old_rule: the citing court applies the old decision's superseded holding to decide the case before it (not \
merely describing history, the statute's origin, or a different, unaffected holding of the decision).
- notes_statute: the passage mentions that the holding was superseded / overridden / amended by the statute.
- conduct_year: the year of the relevant conduct or claim (e.g. the discriminatory pay decision, the filing) if the \
passages or head of the opinion state it, else 0.
- conduct_after_effective: "yes" if that conduct is on or after the effective (or retroactive) date, "no" if before, \
"unknown".
- error: applies_old_rule = true, notes_statute = false and conduct_after_effective = "yes"."""

SUPER_SCHEMA = _obj({
    "applies_old_rule": {"type": "boolean"},
    "notes_statute": {"type": "boolean"},
    "conduct_year": {"type": "integer"},
    "conduct_after_effective": {"type": "string", "enum": ["yes", "no", "unknown"]},
    "error": {"type": "boolean"},
    "proposition": {"type": "string", "description": "<= 25 words"},
    "reason": {"type": "string", "description": "<= 30 words"},
})


def super_user(r):
    return ("OLD DECISION: %s, %s (decided %s)\nSUPERSEDED HOLDING: %s\nSTATUTE: %s, effective %s, applies to conduct from %s\n"
            "CITING OPINION: %s, %s (%s, decided %s)\n\nHEAD OF THE CITING OPINION:\n%s\n\n%s"
            % (r.get("cited_name"), r.get("cited_cite"), r.get("cited_date"), r.get("holding", "-"), r.get("law"),
               r.get("effective"), r.get("conduct_from"), r.get("citing_name"), r.get("citing_cite"),
               r.get("citing_court_name"), r.get("citing_date"), (r.get("head") or "")[:1000], _win(r)))


# ---- pattern 5: losing side of a resolved split ----------------------------------------------------------------------

SPLIT_SYS = """The US Supreme Court resolved a conflict among the courts of appeals. You are given the Supreme Court's \
statement of the question and its answer, and passages of a lower-court decision (decided after the Supreme Court) \
around its citation of a court of appeals decision that was on one side of the conflict. Answer from the text.

- side: whether that court of appeals decision answered the question the way the Supreme Court did ("winning"), the \
other way ("losing"), or cannot tell ("unclear"), judging by the Supreme Court statement and the passages.
- relies_on_point: the lower court relies on the cited decision for its answer to the resolved question.
- notes_scotus: the passage mentions the Supreme Court decision or that the point was resolved/abrogated.
- zombie: side = "losing", relies_on_point = true, notes_scotus = false."""

SPLIT_SCHEMA = _obj({
    "side": {"type": "string", "enum": ["winning", "losing", "unclear"]},
    "relies_on_point": {"type": "boolean"},
    "notes_scotus": {"type": "boolean"},
    "zombie": {"type": "boolean"},
    "reason": {"type": "string", "description": "<= 30 words"},
})


def split_user(r):
    return ("SUPREME COURT: %s, %s (decided %s)\nQUESTION AND ANSWER: %s\n"
            "CITED COURT OF APPEALS DECISION: %s, %s (decided %s)\n"
            "CITING LOWER-COURT DECISION: %s, %s (%s, decided %s)\n\n%s"
            % (r.get("scotus_name"), r.get("scotus_cite"), r.get("scotus_date"), r.get("qa", "-")[:900],
               r.get("cited_name"), r.get("cited_cite"), r.get("cited_date"), r.get("citing_name"),
               r.get("citing_cite"), r.get("citing_court_name"), r.get("citing_date"), _win(r)))


SIDE_SYS = """The US Supreme Court granted certiorari to resolve a conflict among the courts of appeals. From the \
Supreme Court's own words, state the question, the Court's answer, and for each listed court of appeals decision \
whether it answered the question the way the Supreme Court did."""

SIDE_SCHEMA = _obj({
    "question": {"type": "string", "description": "<= 30 words"},
    "answer": {"type": "string", "description": "<= 30 words"},
    "sides": {"type": "array", "items": _obj({"cite": {"type": "string"},
                                               "side": {"type": "string", "enum": ["winning", "losing", "unclear"]}})},
})


def side_user(r):
    return ("SUPREME COURT: %s, %s (decided %s)\nCOURT OF APPEALS DECISIONS NAMED NEAR THE CONFLICT STATEMENT: %s\n\n"
            "OPENING OF THE OPINION AND THE CONFLICT STATEMENT:\n%s\n\nCLOSING OF THE OPINION:\n%s"
            % (r.get("name"), r.get("cite"), r.get("date"), "; ".join(r.get("conflict_cites", [])),
               r.get("opening", "")[:5000], r.get("closing", "")[:1500]))


# ---- known-instance extraction (later courts' call-outs) -----------------------------------------------------------

CALLOUT_SYS = """A later court's opinion says that some earlier court decision relied on authority that had been \
overruled, abrogated, or disapproved. From the passage, identify who relied on it."""

CALLOUT_SCHEMA = _obj({
    "relier_kind": {"type": "string", "enum": ["named_court_decision", "lower_court_in_this_case",
                                               "party_or_counsel", "other"]},
    "relier_name": {"type": "string", "description": "case name of the relying decision, or -"},
    "relier_cite": {"type": "string", "description": "its reporter citation as written, or -"},
    "relied_on_name": {"type": "string"},
    "relied_on_cite": {"type": "string", "description": "as written, or -"},
    "relied_after_overruling": {"type": "string", "enum": ["yes", "no", "unclear"]},
})


def callout_user(r):
    return "PASSAGE (from %s, decided %s):\n%s" % (r.get("note_name"), r.get("note_date"), r.get("window"))


TASKS = {
    "zombie": dict(system=ZOMBIE_SYS, schema=ZOMBIE_SCHEMA, user=zombie_user, key=lambda r: r["hkey"]),
    "unpub": dict(system=UNPUB_SYS, schema=UNPUB_SCHEMA, user=unpub_user, key=lambda r: r["hkey"]),
    "panel": dict(system=PANEL_SYS, schema=PANEL_SCHEMA, user=panel_user, key=lambda r: r["hkey"]),
    "super": dict(system=SUPER_SYS, schema=SUPER_SCHEMA, user=super_user, key=lambda r: r["hkey"]),
    "split": dict(system=SPLIT_SYS, schema=SPLIT_SCHEMA, user=split_user, key=lambda r: r["hkey"]),
    "side": dict(system=SIDE_SYS, schema=SIDE_SCHEMA, user=side_user, key=lambda r: r["hkey"]),
    "callout": dict(system=CALLOUT_SYS, schema=CALLOUT_SCHEMA, user=callout_user, key=lambda r: r["hkey"]),
}
