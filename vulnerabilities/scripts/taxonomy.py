"""The vulnerability taxonomy (draft 3): the single source for TAXONOMY.md, the release labels, tests/test_taxonomy.py
and bench/taxonomy_bench.py.

Every flag carries two labels:
  category  what kind of defect the flag alleges (A1 ... E4). Decided from the text, before anyone knows if it is real.
  verdict   whether it holds: flagged (unreviewed), candidate, confirmed, not_a_defect, corpus_error, detector_error.
Draft 1 had one label and a category for corpus errors; the agreement test showed that most disagreements were verdicts
filed as categories ('no category fits: this is lawful'), so the two are now separate.

Design rules
1. A category names a kind of legal defect, never a detector or a country. Detectors map to categories (DETECTORS); a
   detector can feed several categories through conditional rules (classify()).
2. Families A-D are defects in the law as published; family E holds kinds of anomaly that are usually corpus artefacts.
   An E flag that is confirmed real is re-filed under A-D (its exclusions say where).
3. Categories are mutually exclusive: each lists boundary rules naming the neighbour and which one wins.
4. Every category states the legal rule it breaches, the effect if real, what confirming it needs, and an example.
"""
from __future__ import annotations
import re

FAMILIES = {
    "A": ("Broken references", "The text points at something that does not exist: a repealed, deleted or never-enacted "
          "provision of the same act, or a provision of another act that no longer exists. The rule that relies on the "
          "reference loses its trigger, its condition or its content."),
    "B": ("Timing", "The text is fine but its dates are not: it applies before it was made or published, or a time-limited "
          "rule lapses before its renewal starts, or is renewed to a date already past."),
    "C": ("Competence and procedure", "The instrument was made without the power, majority, procedure or time the constitution "
          "requires, so it may be void as a whole or in part."),
    "D": ("Amounts", "A figure in the text no longer means what it was meant to: it was changed in one place only, or it is "
          "stated in a currency that no longer exists."),
    "E": ("Anomalies", "Kinds of irregularity in the record that are usually how a corpus was built (dates, numbering, leftover "
          "text). Reported to corpus builders; re-filed under A-D when review shows a real defect."),
}

EFFECTS = {  # strongest to weakest
    "void": "the instrument or provision is invalid (a court can set it aside)",
    "unenforceable": "a penalty, charge or duty cannot be enforced against anyone",
    "gap": "for a period, or for a set of cases, no rule applies",
    "inapplicable": "the provision cannot be applied as written; a court must read it down or fill it",
    "ambiguous": "two readings are open; the outcome depends on interpretation",
    "cosmetic": "the text is wrong but nothing turns on it",
}

VERDICTS = {
    "flagged": "found by a detector, not yet reviewed",
    "candidate": "a model review found a possible defect (and, where run, it survived a second model arguing against it)",
    "confirmed": "checked by hand against official sources",
    "not_a_defect": "real text, but lawful, cured (e.g. by a substitution or conversion clause), favourable, or harmless",
    "corpus_error": "the corpus is wrong (date, attribution, missing text); reported to the corpus builder",
    "detector_error": "the corpus is right but the detector misread it (another act's section, a sub-unit, a heading)",
}

C = {}


def cat(code, name, definition, rule, include, exclude, effect, confirm, example, detectors, severity, status):
    C[code] = dict(code=code, family=code[0], name=name, definition=definition, rule=rule, include=include, exclude=exclude,
                   effect=effect, confirm=confirm, example=example, detectors=detectors, severity=severity, status=status)


# ---------------------------------------------------------------- A. Broken references
cat("A1", "Reference to a repealed or deleted provision of the same act",
    "A provision in force relies on another provision of the same act that has been repealed, deleted or renumbered away, "
    "including a paragraph or sub-unit the cited provision no longer has.",
    "Legal certainty: a rule must be determinable from the text; for duties and charges, the legality principle.",
    ["the cited provision is now only a repeal placeholder ('(weggefallen)', 'Revogado', 'Repealed')",
     "the cited provision's file was deleted and nothing replaced its number",
     "the cited paragraph (Abs., subsection, alinéa) does not exist in the cited provision"],
    ["the citing provision attaches a sanction (punishment or coercion, not cost recovery) to the cited provision -> A2",
     "the cited number never existed in the act -> A3",
     "the cited provision belongs to another act -> A4",
     "the text deliberately refers to the old version ('in der bis ... geltenden Fassung') or is a note, index entry or "
     "saving clause -> not a defect (verdict not_a_defect)"],
    "inapplicable", "the repeal (instrument, date) and the current official text of both provisions; whether a general "
    "clause redirects references to the successor",
    "Brazil CLT art. 413: the notice duty for minors' overtime points at four repealed articles",
    ["placeholder_ref", "dangling_ref", "missing_paragraph"], 2, "tested (placeholder, deleted); missing_paragraph untested")

cat("A2", "Sanction pointing at a repealed or deleted provision (dead sanction)",
    "A provision that attaches a sanction (an offence, a fine, an administrative infraction, seizure, forfeiture, a licence "
    "suspension, a duty to prosecute) defines the conduct it sanctions by reference to a provision of the same act that has "
    "been repealed or deleted.",
    "No penalty without a law (nulla poena sine lege; e.g. Basic Law art. 103(2), OWiG § 3, ECHR art. 7); a blanket sanction "
    "may not be filled by analogy.",
    ["catalogue items 'contrary to § 12' where § 12 is a placeholder or deleted",
     "'a person who contravenes section 47 commits an offence' where s 47 is repealed",
     "seizure, suspension or prosecution 'for breach of article 190' where art. 190 is repealed",
     "partly dead items (one of several references is dead) count, marked partial"],
    ["the consequence is cost recovery, a fee or compensation, not punishment or coercion -> A1",
     "the sanctioned duty lives on under the same number -> not a defect",
     "the sanction refers to another act's provision -> A4",
     "a sanction clause that mentions a repealed article only as history -> not a defect"],
    "unenforceable", "as A1, plus whether any other provision attaches a sanction to the same conduct",
    "Germany AWaffV § 34 no. 11: the fine for using a shut-down shooting range points at deleted § 12",
    ["dead_fine", "owi_de"], 1, "tested (unit tests, live check 9/9, penalty recognition 94% / 74%)")

cat("A3", "Reference to a provision never enacted",
    "A provision in force relies on a provision that never existed: it was in a bill that failed, an amendment that could "
    "not be carried out, or a numbering slip.",
    "Legality and legal certainty: a power, duty or recipient defined only by a non-existent provision has no content.",
    ["the publisher notes that an amendment could not be carried out because its target does not exist, and other "
     "provisions in force rely on that target",
     "the cited number is absent from every version of the act in the record"],
    ["the number existed once and was repealed -> A1 (or A2)",
     "two amendments to the same provision on the same day, one of which failed -> E2",
     "a publisher note about a typo ('sic'), truncated or omitted text -> E5",
     "a publisher note about a table of contents or other editorial matter -> not a defect"],
    "inapplicable", "the amending instrument and its explanatory memorandum; the failed bill; the current official text",
    "Germany AO § 31b(3a): tax data is to go to a body defined in GwG § 50c, which was never enacted",
    ["publisher_flag", "cross_act_missing"], 1, "partly detected (publisher notes); never-existed check not built")

cat("A4", "Broken reference to another act",
    "A provision in force relies on another act, or on a provision of another act, that is no longer in force, and no "
    "general clause redirects the reference to a successor.",
    "Legal certainty; for burdens and exemptions, legality.",
    ["'artículo 108 de la Ley 24/1988' where Ley 24/1988 has been repealed",
     "'section 63 of the Tax Act' where the Tax Act is in force but its s 63 was repealed"],
    ["a general substitution clause covers it -> not a defect (cured)",
     "the cited act is a different act with the same number (a regional law) -> detector error",
     "the citation is descriptive or historical -> not a defect",
     "the cited provision is in the same act -> A1"],
    "inapplicable", "the repeal of the cited act or provision and the absence of a substitution clause",
    "Spain Ley 27/2014 art. 29: the 1% rate for mortgage-market regulation funds points at a provision of Ley 2/1981, "
    "repealed in 2022 (candidate)",
    ["dead_act_ref"], 3, "act-level citations in Spain only; provision-level cross-act check not built")

# ---------------------------------------------------------------- B. Timing
cat("B1", "Applies before it was made or published",
    "The instrument's own commencement date is earlier than the date it was made or published. Whether this is a defect "
    "depends on the effect: a burden (higher fine, new duty, charge) cannot apply before publication; a favourable "
    "backdating (pay rise, status) usually can.",
    "A rule binds only once published (e.g. Netherlands Constitution art. 88); no heavier penalty than at the time of the "
    "act (ECHR art. 7); burdensome regulations may not be retroactive without statutory authority (e.g. French Civil "
    "Code art. 2).",
    ["'treedt in werking met ingang van 1 januari' in an instrument issued on 5 January",
     "a décret signed in March that raises a charge from the previous January"],
    ["the backdating is favourable -> not a defect", "the corpus records a wrong date -> corpus error",
     "a time-limited rule renewed after it had run out -> B2"],
    "inapplicable", "the gazette issue (publication date), the commencement clause, and whether the effect is burdensome",
    "Netherlands Stb. 2022, 7: higher fine ceilings in force on 1 January, published on 5 January",
    ["retroactive_date"], 2, "detected; review must separate burdens from favourable backdating")

cat("B2", "Empty period",
    "A rule written to last 'until' a date was renewed by an instrument that took effect after that date, without "
    "retroactivity, so for the days or months between the rule did not exist.",
    "A rule applies only while in force; extensions do not reach back unless they say so.",
    ["moratorium 'until 31 December 2025', extended by an act in force 1 August 2026",
     "a provision repealed before its replacement took effect, confirmed in the official sources"],
    ["the renewal is expressly retroactive -> not a defect",
     "the amendment sets an end date already past -> B3",
     "the lapsed text simply was not cleaned up and nothing renewed it -> E4",
     "only the corpus shows the gap -> E1 with verdict corpus error"],
    "gap", "the original end date, the renewing instrument's commencement and any retroactivity clause",
    "Switzerland GTG art. 37a: no GMO moratorium from 1 January to 31 July 2026",
    ["late_extension"], 2, "detected; end-date recall 42%")

cat("B3", "End date set in the past",
    "An amendment sets or changes a rule's end date to a date already past when the amendment takes effect, so the rule "
    "is dead on arrival or expires at once.",
    "Legal certainty; the legislator's evident intent fails.",
    ["an order of February 2022 changing 'until 31 December 2022' to 'until 31 December 2021'"],
    ["the renewal starts later than the old end date but sets a future end date -> B2"],
    "gap", "the amending instrument's text and commencement",
    "France, arrêté of 8 June 2015 (discard cap) as amended on 1 February 2022",
    ["backdated_end"], 3, "found by hand; no dedicated detector")

# ---------------------------------------------------------------- C. Competence and procedure
cat("C1", "Missing or wrong enabling power",
    "A delegated instrument cites as its legal basis a provision that did not exist, or did not confer that power, when the "
    "instrument was made, or omits a power it needed.",
    "Delegated legislation must rest on, and in some systems cite, an existing enabling power (e.g. Basic Law art. 80(1) "
    "sentence 3).",
    ["a regulation of 2019 citing § 9(1a) of an act that inserted § 9(1a) in 2021"],
    ["the citation was only rewritten in a later consolidation -> corpus error",
     "the enabling act was repealed later but the instrument was valid when made -> not a defect in most systems",
     "the instrument is a legislative decree made under a time-limited delegation -> C4"],
    "void", "the instrument's preamble as originally published, and the enabling act as it stood that day",
    "the legal zero-day model case (an amending regulation citing the wrong power); none confirmed in this record",
    ["authority_gap"], 2, "method pending: consolidated preambles are rewritten; 197/197 reviewed flags were artefacts")

cat("C2", "Reserved-law breach",
    "A matter the constitution reserves to a special kind of law (organic law, complementary law, absolute majority) was "
    "changed by an ordinary law, decree-law or regulation.",
    "e.g. Spanish Constitution art. 81, French Constitution art. 46, Brazilian Constitution art. 69.",
    ["an ordinary budget law amending a provision of an organic law that the organic law did not declare ordinary"],
    ["the amended provision is declared ordinary by the organic law itself -> not a defect"],
    "void", "the organic law's 'carácter' clause, the amending instrument's rank, constitutional case law",
    "Spain: the 2017 and 2018 budget laws amended transitional provision 8 of LO 7/2015 (candidate)",
    ["organic_reserve"], 3, "Spain only")

cat("C3", "Decree-law not converted in time",
    "An emergency decree-law lapses unless parliament converts or validates it within a fixed period; its text survives in "
    "the record after the period passed without conversion.",
    "e.g. Spanish Constitution art. 86 (30 days), Italian art. 77 (60 days), Brazilian art. 62 (60+60 days).",
    ["a Real Decreto-ley that Congress refused to validate, still shown as in force"],
    ["the decree-law was converted -> not a defect",
     "the lapse left a period with no rule that a later instrument restored -> B2 for that period"],
    "void", "the parliamentary record of conversion or refusal and its publication",
    "Spain RDL 9/2024 and RDL 16/2025 (eviction suspension) were derogated by refusal; the resulting gaps are B2 cases",
    [], 3, "no detector")

cat("C4", "Delegated legislation outside its delegation",
    "A legislative decree made under a delegation of law-making power was signed after the delegation expired or covers "
    "matters outside it.",
    "e.g. Spanish Constitution art. 82, Italian art. 76, Peruvian art. 104, Colombian art. 150(10).",
    ["a texto refundido signed after the deadline in the delegating law"],
    ["an ordinary regulation under a standing enabling power -> C1"],
    "void", "the delegating provision's deadline and scope, and the decree's signature date",
    "none found: all 40 Spanish textos refundidos were on time",
    ["delegation_deadline"], 3, "Spain only, clean")

# ---------------------------------------------------------------- D. Amounts
cat("D1", "Amount changed in one place only",
    "The same amount appears in several provisions; an amendment changed it in one and left the others.",
    "Legal certainty; equal treatment where the amounts must match.",
    ["a threshold raised in the main rule but not in the exemption that repeats it"],
    ["the amounts are meant to differ -> not a defect", "a currency was replaced -> D2"],
    "ambiguous", "the amending instrument and whether the provisions were meant to stay aligned",
    "none confirmed", ["stale_amount"], 3, "detected; mostly artefacts")

cat("D2", "Amount in a replaced currency",
    "A provision in force states an amount in a currency that has been replaced. It is a defect only where no conversion "
    "rule covers it; where one does, the verdict is not_a_defect (cured).",
    "Legal certainty; for fines, legality.",
    ["a fine of '200 cruzeiros a 5.000 cruzeiros' still in the text"],
    ["the amount was changed in one place only -> D1"],
    "cosmetic", "the conversion law and whether it reaches this provision",
    "Brazil CLT art. 347: fine still stated in cruzeiros", ["dead_currency"], 4, "detected; almost always cured")

# ---------------------------------------------------------------- E. Anomalies
cat("E1", "Repeal before replacement",
    "In the record, a provision is repealed before the provision replacing it takes effect.",
    "If real, a gap.", ["a provision deleted on 1 January and its successor dated 1 March"],
    ["confirmed in the official sources -> B2"],
    "gap", "the official commencement dates of both instruments", "none confirmed",
    ["repeal_gap"], 4, "82% of reviewed flags are corpus errors (three quarters French)")

cat("E2", "Same-day conflicting amendments",
    "Two instruments amend the same provision on the same day, so the order of execution decides the text.",
    "If real, the second amendment may fail ('ins Leere') or override the first.",
    ["two amending acts in force on 1 January both rewriting § 5"],
    ["the failed amendment leaves another provision relying on a target that never existed -> A3"],
    "ambiguous", "both amending instruments and the publisher's consolidation notes", "none confirmed",
    ["same_day_conflict"], 4, "70% of reviewed flags are corpus errors")

cat("E3", "Duplicate numbering",
    "Two units in force carry the same number in the same provision or act.",
    "If real, references to that number are ambiguous.",
    ["two paragraphs numbered § 3 in one section, both in force"],
    ["one of the two is repealed or is a heading -> not a defect"],
    "ambiguous", "the official text", "none confirmed", ["dup_label"], 4, "unreviewed; mostly noise")

cat("E4", "Spent provision still in the text",
    "A provision whose effect is exhausted is still printed as if in force: it applied a rule 'until' a date that has "
    "passed and was not renewed, or it is marked moot or spent ('gegenstandslos', 'spent', 'sans objet').",
    "Usually none: an expired rule stops applying.",
    ["a transitional rule 'until 31 December 2019' still printed", "a provision or index entry marked 'gegenstandslos'"],
    ["the rule was renewed late -> B2", "another provision in force still relies on it -> A1"],
    "cosmetic", "nothing, unless another provision relies on it", "none", ["lapsed_limit"], 5, "large and mostly harmless")

cat("E5", "Incomplete or garbled text",
    "The text in the record is truncated, has passages omitted, carries a '[sic]' or similar editorial marker, or differs "
    "from the published edition in wording.",
    "If real in the official text, legal certainty; usually a reproduction problem in the record.",
    ["a provision that stops mid-sentence", "'[sic]' marking an error in the official text",
     "a publisher note that passages were omitted or could not be reproduced"],
    ["the publisher says an amendment could not be carried out because its target does not exist -> A3",
     "two units carry the same number -> E3"],
    "cosmetic", "the official edition", "none", ["publisher_flag"], 5, "fed by publisher notes; unreviewed")

DETECTORS = {"placeholder_ref": "A1", "dangling_ref": "A1", "missing_paragraph": "A1", "dead_fine": "A2", "owi_de": "A2",
             "publisher_flag": "A3", "cross_act_missing": "A3", "dead_act_ref": "A4", "retroactive_date": "B1",
             "late_extension": "B2", "backdated_end": "B3", "authority_gap": "C1", "organic_reserve": "C2",
             "delegation_deadline": "C4", "stale_amount": "D1", "dead_currency": "D2", "repeal_gap": "E1",
             "same_day_conflict": "E2", "dup_label": "E3", "lapsed_limit": "E4"}

SANCTION = re.compile(r"(?i)bu(ss|ß)geld|ordnungswidrig|offen[cs]e|infracci|infraç|amende|multa|\bfine\b|penalt|bestraft|"
                      r"puni|seiz|sequestr|forfeit|suspend|prosecut|sanction")
FAILED = re.compile(r"(?i)nicht ausführbar|ging ins leere|could not be executed|not executed|could not be given effect|"
                    r"non exécutable|n'a pu être|niet uitvoerbaar|no (?:ha )?podido")


def _is_penal(text: str) -> bool:
    """the penalty recogniser tested in bench/penal_bench.py (held-out precision 94%, recall 74%)."""
    import sys
    from pathlib import Path
    d = str(Path(__file__).resolve().parent / "detectors"); i = str(Path(__file__).resolve().parent / "ingest")
    for p in (d, i):
        if p not in sys.path:
            sys.path.insert(0, p)
    from dead_fine import is_penal
    return is_penal(text)


def verdict(review: str) -> str:
    r = (review or "").lower()
    if not r:
        return "flagged"
    if r.startswith("artefact"):
        return "corpus_error"        # older reviews lumped corpus and detector errors; see ARTEFACT_EITHER
    if r.startswith(("lawful", "harmless", "cured", "no_gap")) or "not real" in r or "rebutted" in r:
        return "not_a_defect"
    if r.startswith("candidate"):
        return "candidate"
    return "flagged"


# verdicts an older 'artefact' review is compatible with (the review prompt did not ask which)
ARTEFACT_EITHER = {"corpus_error", "detector_error"}


def classify(detector: str, row: dict | None = None) -> tuple[str, str]:
    """(category, verdict) for one flag, by the conditional rules the definitions state."""
    row = row or {}
    code = DETECTORS.get(detector, "E4")
    text = " ".join(str(row.get(k) or "") for k in ("summary", "reference", "context"))
    if code == "A1" and (SANCTION.search(text) or _is_penal(text)):
        code = "A2"
    v = verdict(row.get("review", ""))
    if detector == "publisher_flag" and not FAILED.search(text):
        code = "E5"                  # '[sic]', truncated or omitted text; failed amendments stay A3
    return code, v


CONFIRMED = {
    "DE AWaffV § 34 no. 11": "A2", "DE AO § 31b(3a) / GwG § 50c": "A3", "BR CLT art. 413": "A1", "CH LwG art. 154(2)": "A1",
    "NL Stb. 2022, 7": "B1", "DE EIGV § 41(2) no. 5": "A2", "DE SchSiHafV § 42": "A2", "DE FuttMV § 40": "A2",
    "DE EnergieStV § 111": "A2", "BR CPP art. 571": "A1", "AR CP art. 23": "A2", "FR discard cap 2022": "B3",
    "CL Ley 17.798 art. 19 A": "A1", "FJ VAT Act s 71": "A2", "MT Cap. 31 arts. 43, 90, 119": "A2", "MT Cap. 10 art. 319": "A2",
    "CA-NT Boilers Act s 43": "A2", "CH GTG art. 37a": "B2", "FR loi 2023-380 art. 10": "B2", "ES Ley 16/1985 DT 5": "B2",
    "ES RDL 11/2020 evictions": "B2", "FR loi 2022-1158 art. 6": "B2", "US-CA Gov. Code § 51298.5": "B2",
    "US-IN IC 9-32-11-20": "B2", "FR discard cap 2021 lapse": "B2",
}
