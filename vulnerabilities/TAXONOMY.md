# Vulnerability taxonomy (draft 3)

This document defines the kinds of defect the vulnerability list reports. It is generated from `scripts/taxonomy.py`, which is also what the tests and the release use, so the definitions here and the labels in the data cannot drift apart.

## Two labels for every flag

- **Category**: what kind of defect the flag alleges, decided from the text before anyone knows whether it is real. It never names a detector or a country.
- **Verdict**: whether it holds. The verdicts are:

  - `flagged`: found by a detector, not yet reviewed
  - `candidate`: a model review found a possible defect (and, where run, it survived a second model arguing against it)
  - `confirmed`: checked by hand against official sources
  - `not_a_defect`: real text, but lawful, cured (e.g. by a substitution or conversion clause), favourable, or harmless
  - `corpus_error`: the corpus is wrong (date, attribution, missing text); reported to the corpus builder
  - `detector_error`: the corpus is right but the detector misread it (another act's section, a sub-unit, a heading)

Draft 1 had a single label, with 'corpus error' as one of the categories. The agreement test showed that most disagreements were verdicts filed as categories ('no category fits: this one is lawful'), so the two are now separate. A flag about a lapsed currency that a conversion law cures is category D2, verdict not_a_defect, not 'no category'.

## Design rules

1. A category names a kind of legal defect. Detectors map to categories; one detector can feed several through conditional rules, and several detectors can feed one category.
2. Families A-D are defects in the law as published. Family E holds kinds of irregularity that are usually how a corpus was built; an E flag that review shows is real is re-filed under A-D, as its exclusions say.
3. Categories are mutually exclusive: each lists boundary rules naming the neighbour and which one wins.
4. Every category states the legal rule it breaches, its effect if real, what confirming it needs, and an example.

## Effects, strongest first

- **void**: the instrument or provision is invalid (a court can set it aside)
- **unenforceable**: a penalty, charge or duty cannot be enforced against anyone
- **gap**: for a period, or for a set of cases, no rule applies
- **inapplicable**: the provision cannot be applied as written; a court must read it down or fill it
- **ambiguous**: two readings are open; the outcome depends on interpretation
- **cosmetic**: the text is wrong but nothing turns on it

## Families and categories

| Code | Category | Effect | Severity (1 = worst) | Flags | Candidates | Confirmed | Not a defect | Corpus or detector error |
|---|---|---|---|---|---|---|---|---|
| A1 | Reference to a repealed or deleted provision of the same act | inapplicable | 2 | 6,856 | 30 | 4 | 163 | 945 |
| A2 | Sanction pointing at a repealed or deleted provision (dead sanction) | unenforceable | 1 | 645 | 11 | 10 | 36 | 121 |
| A3 | Reference to a provision never enacted | inapplicable | 1 | 79 | 0 | 1 | 0 | 0 |
| A4 | Broken reference to another act | inapplicable | 3 | 2,925 | 2 | 0 | 273 | 16 |
| B1 | Applies before it was made or published | inapplicable | 2 | 5,769 | 106 | 1 | 595 | 561 |
| B2 | Empty period | gap | 2 | 1,760 | 375 | 8 | 210 | 305 |
| B3 | End date set in the past | gap | 3 | 0 | 0 | 1 | 0 | 0 |
| C1 | Missing or wrong enabling power | void | 2 | 197 | 0 | 0 | 0 | 197 |
| C2 | Reserved-law breach | void | 3 | 158 | 3 | 0 | 111 | 44 |
| C3 | Decree-law not converted in time | void | 3 | 0 | 0 | 0 | 0 | 0 |
| C4 | Delegated legislation outside its delegation | void | 3 | 0 | 0 | 0 | 0 | 0 |
| D1 | Amount changed in one place only | ambiguous | 3 | 2,361 | 0 | 0 | 68 | 137 |
| D2 | Amount in a replaced currency | cosmetic | 4 | 8,394 | 0 | 0 | 0 | 0 |
| E1 | Repeal before replacement | gap | 4 | 15,876 | 4 | 0 | 181 | 871 |
| E2 | Same-day conflicting amendments | ambiguous | 4 | 6,161 | 1 | 0 | 225 | 524 |
| E3 | Duplicate numbering | ambiguous | 4 | 1,905 | 0 | 0 | 0 | 0 |
| E4 | Spent provision still in the text | cosmetic | 5 | 20,770 | 0 | 0 | 145 | 50 |
| E5 | Incomplete or garbled text | cosmetic | 5 | 445 | 0 | 0 | 0 | 0 |

Flags, candidates, not-a-defect and errors are the released list (74,301 flags) re-filed by `classify()`; confirmed are the 25 cases checked against official sources. Unreviewed flags are the remainder of each row.

### A. Broken references

The text points at something that does not exist: a repealed, deleted or never-enacted provision of the same act, or a provision of another act that no longer exists. The rule that relies on the reference loses its trigger, its condition or its content.

#### A1 · Reference to a repealed or deleted provision of the same act

A provision in force relies on another provision of the same act that has been repealed, deleted or renumbered away, including a paragraph or sub-unit the cited provision no longer has.

- **Rule breached:** Legal certainty: a rule must be determinable from the text; for duties and charges, the legality principle.
- **Effect if real:** inapplicable (the provision cannot be applied as written; a court must read it down or fill it); severity 2 of 5
- **Includes:** the cited provision is now only a repeal placeholder ('(weggefallen)', 'Revogado', 'Repealed'); the cited provision's file was deleted and nothing replaced its number; the cited paragraph (Abs., subsection, alinéa) does not exist in the cited provision
- **Excludes:** the citing provision attaches a sanction (punishment or coercion, not cost recovery) to the cited provision -> A2; the cited number never existed in the act -> A3; the cited provision belongs to another act -> A4; the text deliberately refers to the old version ('in der bis ... geltenden Fassung') or is a note, index entry or saving clause -> not a defect (verdict not_a_defect)
- **To confirm, check:** the repeal (instrument, date) and the current official text of both provisions; whether a general clause redirects references to the successor
- **Example:** Brazil CLT art. 413: the notice duty for minors' overtime points at four repealed articles
- **Fed by:** `placeholder_ref`, `dangling_ref`, `missing_paragraph`
- **Status:** tested (placeholder, deleted); missing_paragraph untested

#### A2 · Sanction pointing at a repealed or deleted provision (dead sanction)

A provision that attaches a sanction (an offence, a fine, an administrative infraction, seizure, forfeiture, a licence suspension, a duty to prosecute) defines the conduct it sanctions by reference to a provision of the same act that has been repealed or deleted.

- **Rule breached:** No penalty without a law (nulla poena sine lege; e.g. Basic Law art. 103(2), OWiG § 3, ECHR art. 7); a blanket sanction may not be filled by analogy.
- **Effect if real:** unenforceable (a penalty, charge or duty cannot be enforced against anyone); severity 1 of 5
- **Includes:** catalogue items 'contrary to § 12' where § 12 is a placeholder or deleted; 'a person who contravenes section 47 commits an offence' where s 47 is repealed; seizure, suspension or prosecution 'for breach of article 190' where art. 190 is repealed; partly dead items (one of several references is dead) count, marked partial
- **Excludes:** the consequence is cost recovery, a fee or compensation, not punishment or coercion -> A1; the sanctioned duty lives on under the same number -> not a defect; the sanction refers to another act's provision -> A4; a sanction clause that mentions a repealed article only as history -> not a defect
- **To confirm, check:** as A1, plus whether any other provision attaches a sanction to the same conduct
- **Example:** Germany AWaffV § 34 no. 11: the fine for using a shut-down shooting range points at deleted § 12
- **Fed by:** `dead_fine`, `owi_de`
- **Status:** tested (unit tests, live check 9/9, penalty recognition 94% / 74%)

#### A3 · Reference to a provision never enacted

A provision in force relies on a provision that never existed: it was in a bill that failed, an amendment that could not be carried out, or a numbering slip.

- **Rule breached:** Legality and legal certainty: a power, duty or recipient defined only by a non-existent provision has no content.
- **Effect if real:** inapplicable (the provision cannot be applied as written; a court must read it down or fill it); severity 1 of 5
- **Includes:** the publisher notes that an amendment could not be carried out because its target does not exist, and other provisions in force rely on that target; the cited number is absent from every version of the act in the record
- **Excludes:** the number existed once and was repealed -> A1 (or A2); two amendments to the same provision on the same day, one of which failed -> E2; a publisher note about a typo ('sic'), truncated or omitted text -> E5; a publisher note about a table of contents or other editorial matter -> not a defect
- **To confirm, check:** the amending instrument and its explanatory memorandum; the failed bill; the current official text
- **Example:** Germany AO § 31b(3a): tax data is to go to a body defined in GwG § 50c, which was never enacted
- **Fed by:** `publisher_flag`, `cross_act_missing`
- **Status:** partly detected (publisher notes); never-existed check not built

#### A4 · Broken reference to another act

A provision in force relies on another act, or on a provision of another act, that is no longer in force, and no general clause redirects the reference to a successor.

- **Rule breached:** Legal certainty; for burdens and exemptions, legality.
- **Effect if real:** inapplicable (the provision cannot be applied as written; a court must read it down or fill it); severity 3 of 5
- **Includes:** 'artículo 108 de la Ley 24/1988' where Ley 24/1988 has been repealed; 'section 63 of the Tax Act' where the Tax Act is in force but its s 63 was repealed
- **Excludes:** a general substitution clause covers it -> not a defect (cured); the cited act is a different act with the same number (a regional law) -> detector error; the citation is descriptive or historical -> not a defect; the cited provision is in the same act -> A1
- **To confirm, check:** the repeal of the cited act or provision and the absence of a substitution clause
- **Example:** Spain Ley 27/2014 art. 29: the 1% rate for mortgage-market regulation funds points at a provision of Ley 2/1981, repealed in 2022 (candidate)
- **Fed by:** `dead_act_ref`
- **Status:** act-level citations in Spain only; provision-level cross-act check not built

### B. Timing

The text is fine but its dates are not: it applies before it was made or published, or a time-limited rule lapses before its renewal starts, or is renewed to a date already past.

#### B1 · Applies before it was made or published

The instrument's own commencement date is earlier than the date it was made or published. Whether this is a defect depends on the effect: a burden (higher fine, new duty, charge) cannot apply before publication; a favourable backdating (pay rise, status) usually can.

- **Rule breached:** A rule binds only once published (e.g. Netherlands Constitution art. 88); no heavier penalty than at the time of the act (ECHR art. 7); burdensome regulations may not be retroactive without statutory authority (e.g. French Civil Code art. 2).
- **Effect if real:** inapplicable (the provision cannot be applied as written; a court must read it down or fill it); severity 2 of 5
- **Includes:** 'treedt in werking met ingang van 1 januari' in an instrument issued on 5 January; a décret signed in March that raises a charge from the previous January
- **Excludes:** the backdating is favourable -> not a defect; the corpus records a wrong date -> corpus error; a time-limited rule renewed after it had run out -> B2
- **To confirm, check:** the gazette issue (publication date), the commencement clause, and whether the effect is burdensome
- **Example:** Netherlands Stb. 2022, 7: higher fine ceilings in force on 1 January, published on 5 January
- **Fed by:** `retroactive_date`
- **Status:** detected; review must separate burdens from favourable backdating

#### B2 · Empty period

A rule written to last 'until' a date was renewed by an instrument that took effect after that date, without retroactivity, so for the days or months between the rule did not exist.

- **Rule breached:** A rule applies only while in force; extensions do not reach back unless they say so.
- **Effect if real:** gap (for a period, or for a set of cases, no rule applies); severity 2 of 5
- **Includes:** moratorium 'until 31 December 2025', extended by an act in force 1 August 2026; a provision repealed before its replacement took effect, confirmed in the official sources
- **Excludes:** the renewal is expressly retroactive -> not a defect; the amendment sets an end date already past -> B3; the lapsed text simply was not cleaned up and nothing renewed it -> E4; only the corpus shows the gap -> E1 with verdict corpus error
- **To confirm, check:** the original end date, the renewing instrument's commencement and any retroactivity clause
- **Example:** Switzerland GTG art. 37a: no GMO moratorium from 1 January to 31 July 2026
- **Fed by:** `late_extension`
- **Status:** detected; end-date recall 42%

#### B3 · End date set in the past

An amendment sets or changes a rule's end date to a date already past when the amendment takes effect, so the rule is dead on arrival or expires at once.

- **Rule breached:** Legal certainty; the legislator's evident intent fails.
- **Effect if real:** gap (for a period, or for a set of cases, no rule applies); severity 3 of 5
- **Includes:** an order of February 2022 changing 'until 31 December 2022' to 'until 31 December 2021'
- **Excludes:** the renewal starts later than the old end date but sets a future end date -> B2
- **To confirm, check:** the amending instrument's text and commencement
- **Example:** France, arrêté of 8 June 2015 (discard cap) as amended on 1 February 2022
- **Fed by:** `backdated_end`
- **Status:** found by hand; no dedicated detector

### C. Competence and procedure

The instrument was made without the power, majority, procedure or time the constitution requires, so it may be void as a whole or in part.

#### C1 · Missing or wrong enabling power

A delegated instrument cites as its legal basis a provision that did not exist, or did not confer that power, when the instrument was made, or omits a power it needed.

- **Rule breached:** Delegated legislation must rest on, and in some systems cite, an existing enabling power (e.g. Basic Law art. 80(1) sentence 3).
- **Effect if real:** void (the instrument or provision is invalid (a court can set it aside)); severity 2 of 5
- **Includes:** a regulation of 2019 citing § 9(1a) of an act that inserted § 9(1a) in 2021
- **Excludes:** the citation was only rewritten in a later consolidation -> corpus error; the enabling act was repealed later but the instrument was valid when made -> not a defect in most systems; the instrument is a legislative decree made under a time-limited delegation -> C4
- **To confirm, check:** the instrument's preamble as originally published, and the enabling act as it stood that day
- **Example:** the legal zero-day model case (an amending regulation citing the wrong power); none confirmed in this record
- **Fed by:** `authority_gap`
- **Status:** method pending: consolidated preambles are rewritten; 197/197 reviewed flags were artefacts

#### C2 · Reserved-law breach

A matter the constitution reserves to a special kind of law (organic law, complementary law, absolute majority) was changed by an ordinary law, decree-law or regulation.

- **Rule breached:** e.g. Spanish Constitution art. 81, French Constitution art. 46, Brazilian Constitution art. 69.
- **Effect if real:** void (the instrument or provision is invalid (a court can set it aside)); severity 3 of 5
- **Includes:** an ordinary budget law amending a provision of an organic law that the organic law did not declare ordinary
- **Excludes:** the amended provision is declared ordinary by the organic law itself -> not a defect
- **To confirm, check:** the organic law's 'carácter' clause, the amending instrument's rank, constitutional case law
- **Example:** Spain: the 2017 and 2018 budget laws amended transitional provision 8 of LO 7/2015 (candidate)
- **Fed by:** `organic_reserve`
- **Status:** Spain only

#### C3 · Decree-law not converted in time

An emergency decree-law lapses unless parliament converts or validates it within a fixed period; its text survives in the record after the period passed without conversion.

- **Rule breached:** e.g. Spanish Constitution art. 86 (30 days), Italian art. 77 (60 days), Brazilian art. 62 (60+60 days).
- **Effect if real:** void (the instrument or provision is invalid (a court can set it aside)); severity 3 of 5
- **Includes:** a Real Decreto-ley that Congress refused to validate, still shown as in force
- **Excludes:** the decree-law was converted -> not a defect; the lapse left a period with no rule that a later instrument restored -> B2 for that period
- **To confirm, check:** the parliamentary record of conversion or refusal and its publication
- **Example:** Spain RDL 9/2024 and RDL 16/2025 (eviction suspension) were derogated by refusal; the resulting gaps are B2 cases
- **Fed by:** no detector yet
- **Status:** no detector

#### C4 · Delegated legislation outside its delegation

A legislative decree made under a delegation of law-making power was signed after the delegation expired or covers matters outside it.

- **Rule breached:** e.g. Spanish Constitution art. 82, Italian art. 76, Peruvian art. 104, Colombian art. 150(10).
- **Effect if real:** void (the instrument or provision is invalid (a court can set it aside)); severity 3 of 5
- **Includes:** a texto refundido signed after the deadline in the delegating law
- **Excludes:** an ordinary regulation under a standing enabling power -> C1
- **To confirm, check:** the delegating provision's deadline and scope, and the decree's signature date
- **Example:** none found: all 40 Spanish textos refundidos were on time
- **Fed by:** `delegation_deadline`
- **Status:** Spain only, clean

### D. Amounts

A figure in the text no longer means what it was meant to: it was changed in one place only, or it is stated in a currency that no longer exists.

#### D1 · Amount changed in one place only

The same amount appears in several provisions; an amendment changed it in one and left the others.

- **Rule breached:** Legal certainty; equal treatment where the amounts must match.
- **Effect if real:** ambiguous (two readings are open; the outcome depends on interpretation); severity 3 of 5
- **Includes:** a threshold raised in the main rule but not in the exemption that repeats it
- **Excludes:** the amounts are meant to differ -> not a defect; a currency was replaced -> D2
- **To confirm, check:** the amending instrument and whether the provisions were meant to stay aligned
- **Example:** none confirmed
- **Fed by:** `stale_amount`
- **Status:** detected; mostly artefacts

#### D2 · Amount in a replaced currency

A provision in force states an amount in a currency that has been replaced. It is a defect only where no conversion rule covers it; where one does, the verdict is not_a_defect (cured).

- **Rule breached:** Legal certainty; for fines, legality.
- **Effect if real:** cosmetic (the text is wrong but nothing turns on it); severity 4 of 5
- **Includes:** a fine of '200 cruzeiros a 5.000 cruzeiros' still in the text
- **Excludes:** the amount was changed in one place only -> D1
- **To confirm, check:** the conversion law and whether it reaches this provision
- **Example:** Brazil CLT art. 347: fine still stated in cruzeiros
- **Fed by:** `dead_currency`
- **Status:** detected; almost always cured

### E. Anomalies

Kinds of irregularity in the record that are usually how a corpus was built (dates, numbering, leftover text). Reported to corpus builders; re-filed under A-D when review shows a real defect.

#### E1 · Repeal before replacement

In the record, a provision is repealed before the provision replacing it takes effect.

- **Rule breached:** If real, a gap.
- **Effect if real:** gap (for a period, or for a set of cases, no rule applies); severity 4 of 5
- **Includes:** a provision deleted on 1 January and its successor dated 1 March
- **Excludes:** confirmed in the official sources -> B2
- **To confirm, check:** the official commencement dates of both instruments
- **Example:** none confirmed
- **Fed by:** `repeal_gap`
- **Status:** 82% of reviewed flags are corpus errors (three quarters French)

#### E2 · Same-day conflicting amendments

Two instruments amend the same provision on the same day, so the order of execution decides the text.

- **Rule breached:** If real, the second amendment may fail ('ins Leere') or override the first.
- **Effect if real:** ambiguous (two readings are open; the outcome depends on interpretation); severity 4 of 5
- **Includes:** two amending acts in force on 1 January both rewriting § 5
- **Excludes:** the failed amendment leaves another provision relying on a target that never existed -> A3
- **To confirm, check:** both amending instruments and the publisher's consolidation notes
- **Example:** none confirmed
- **Fed by:** `same_day_conflict`
- **Status:** 70% of reviewed flags are corpus errors

#### E3 · Duplicate numbering

Two units in force carry the same number in the same provision or act.

- **Rule breached:** If real, references to that number are ambiguous.
- **Effect if real:** ambiguous (two readings are open; the outcome depends on interpretation); severity 4 of 5
- **Includes:** two paragraphs numbered § 3 in one section, both in force
- **Excludes:** one of the two is repealed or is a heading -> not a defect
- **To confirm, check:** the official text
- **Example:** none confirmed
- **Fed by:** `dup_label`
- **Status:** unreviewed; mostly noise

#### E4 · Spent provision still in the text

A provision whose effect is exhausted is still printed as if in force: it applied a rule 'until' a date that has passed and was not renewed, or it is marked moot or spent ('gegenstandslos', 'spent', 'sans objet').

- **Rule breached:** Usually none: an expired rule stops applying.
- **Effect if real:** cosmetic (the text is wrong but nothing turns on it); severity 5 of 5
- **Includes:** a transitional rule 'until 31 December 2019' still printed; a provision or index entry marked 'gegenstandslos'
- **Excludes:** the rule was renewed late -> B2; another provision in force still relies on it -> A1
- **To confirm, check:** nothing, unless another provision relies on it
- **Example:** none
- **Fed by:** `lapsed_limit`
- **Status:** large and mostly harmless

#### E5 · Incomplete or garbled text

The text in the record is truncated, has passages omitted, carries a '[sic]' or similar editorial marker, or differs from the published edition in wording.

- **Rule breached:** If real in the official text, legal certainty; usually a reproduction problem in the record.
- **Effect if real:** cosmetic (the text is wrong but nothing turns on it); severity 5 of 5
- **Includes:** a provision that stops mid-sentence; '[sic]' marking an error in the official text; a publisher note that passages were omitted or could not be reproduced
- **Excludes:** the publisher says an amendment could not be carried out because its target does not exist -> A3; two units carry the same number -> E3
- **To confirm, check:** the official edition
- **Example:** none
- **Fed by:** `publisher_flag`
- **Status:** fed by publisher notes; unreviewed

## From the released categories to this taxonomy

| Released category (detector) | Now filed under | Flags |
|---|---|---|
| Lapsed time limits (`lapsed_limit`) | E4 Spent provision still in the text | 20,770 |
| Repeal gaps (`repeal_gap`) | E1 Repeal before replacement | 15,876 |
| Dead currencies (`dead_currency`) | D2 Amount in a replaced currency | 8,394 |
| Same-day conflicts (`same_day_conflict`) | E2 Same-day conflicting amendments | 6,161 |
| Retroactive or pre-publication dates (`retroactive_date`) | B1 Applies before it was made or published | 5,769 |
| References to repealed placeholders (`placeholder_ref`) | A1 Reference to a repealed or deleted provision of the same act | 5,651 |
| Citations of repealed acts (Spain) (`dead_act_ref`) | A4 Broken reference to another act | 2,925 |
| Stale amounts (`stale_amount`) | D1 Amount changed in one place only | 2,361 |
| Duplicate numbering (`dup_label`) | E3 Duplicate numbering | 1,905 |
| Empty periods (`late_extension`) | B2 Empty period | 1,760 |
| Missing paragraphs (Germany) (`missing_paragraph`) | A1 Reference to a repealed or deleted provision of the same act | 754 |
| References to repealed placeholders (`placeholder_ref`) | A2 Sanction pointing at a repealed or deleted provision (dead sanction) | 574 |
| References to deleted provisions (`dangling_ref`) | A1 Reference to a repealed or deleted provision of the same act | 451 |
| Failed amendments (`publisher_flag`) | E5 Incomplete or garbled text | 445 |
| Missing enabling power (`authority_gap`) | C1 Missing or wrong enabling power | 197 |
| Organic-law reserve (Spain) (`organic_reserve`) | C2 Reserved-law breach | 158 |
| Failed amendments (`publisher_flag`) | A3 Reference to a provision never enacted | 79 |
| Dead fines (Germany) (`dead_fine`) | A2 Sanction pointing at a repealed or deleted provision (dead sanction) | 65 |
| Missing paragraphs (Germany) (`missing_paragraph`) | A2 Sanction pointing at a repealed or deleted provision (dead sanction) | 6 |

## How the taxonomy was tested

Two kinds of test, both rerun after every change (`python -m unittest discover -s tests`, `python bench/taxonomy_bench.py`).

**Structural tests** (`tests/test_taxonomy.py`) check the definitions on paper: every category has every field; codes are unique and family-prefixed; every released detector maps to a category; every exclusion either names another category or says the case is not a defect; the ten boundaries most likely to blur (A1/A2, A1/A3, A1/A4, A2/A4, A3/E5, B1/B2, B2/B3, B2/E4, E1/B2, E2/A3, C1/C4) are stated from both sides; the conditional rules in `classify()` behave as written; every older review verdict maps to a verdict here; every confirmed case sits in a defect family. On draft 1 they caught two real mistakes: B1 sent corpus date errors to the wrong category, and B1 never said where it stopped and B2 began.

**Agreement test** (`bench/taxonomy_bench.py`). A language model is given only the written definitions and files 331 items: up to 20 real flags per detector (two thirds already reviewed, one third not) and all 25 confirmed cases. It returns a category, a verdict, a second-best category, whether the definitions failed to decide between the two, and, if nothing fits, what category is missing. Its answers are compared with the mechanical mapping (`classify()`) and, for confirmed cases, with the category intended for each.

| Draft | What changed | Category agreement | Confirmed cases | Verdict agreement | 'No category fits' |
|---|---|---|---|---|---|
| 1 | one label per flag; 'corpus error' as a category | 53% | 24/25 | – | 110 |
| 2 | category and verdict separated; B1+B2 merged; A2 widened to all sanctions; A4 widened to any other act | 84% | 24/25 | 60% | 13 |
| 3 | cost recovery is not a sanction (A2 → A1); new E5 for garbled text; publisher notes split between A3 and E5; older 'artefact' reviews may be corpus or detector errors | 87% | 25/25 | 95% | 8 |
| 3 (final) | E4 widened to moot or spent provisions | 85% | 25/25 | 95% | 3 |

Labelling noise: the same items filed twice with near-identical definitions got the same category 317 times out of 331 (96%), so differences of 2-3 points between runs are noise. Two limits: the model, not a lawyer, applies the definitions; and the sample has at most 20 items per detector, so rare boundaries (B3, C3, C4) are barely exercised.

What remains of the disagreements is understood:
- 16 flags from the earlier Germany-only fine detector point at another act's section ('§ 60 LFGB'). The model files them as A4, which is what they allege; they are detector errors that the new `dead_fine.py` no longer produces.
- 5 references to repealed provisions sit inside sanction provisions that the mechanical rule's keyword list misses; `classify()` should use `dead_fine.is_penal()` (94% precision, 74% recall) instead of a keyword list.
- 3 items allege nothing at all (an index entry, a quoted rule with no problem in it). That is correct: a pure detector error has a verdict and no category.

