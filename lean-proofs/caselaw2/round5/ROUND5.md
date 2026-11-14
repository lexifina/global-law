# caselaw-lean-2: round 5 (13 Nov 2026, 11:35–14:20, with a crash 12:40–13:42)

Overrulings that are not self-announced (*Brown v. Board* / *Plessy v. Ferguson*). All reading and auditing by
Claude sub-agents (about 75 agents: readers on disjoint packs, blind auditors, the reference, diagnosis, triage;
the loose Supreme Court tier was pre-screened by a smaller Claude model and its positives re-read by the main
model). No external model was called. Nothing was committed or pushed. The live `data/` and `out/` were not
touched: the frozen build is `round5/stage/final` (data) and `round5/out/final` (Lean output). Design:
`round5/DESIGN5.md`. Log: `round5/LOG.md`. Freeze record: `round5/FREEZE.md`. Report:
`~/Documents/html-reports/overturned.html` (`round5/report/make_overturned.py`).

## What was built

- **Recognised overruling (class `recognised`), installed.** A later decision W of a court that itself has power to
  overrule X says, in a certified majority sentence naming both cases, that X was overruled by Y. Status of X: good
  before Y; `unknown:recognisedLater` from date(Y); negative from date(W), attributed to Y. A citation between Y and
  W is `atRisk … recognisedLater`; after W it is `citesOverruled`. A claim that fails (W has only standing, a name
  outside the quote, a negation, unknown dates) falls back to round 4's "at risk" tier.
- **Operative words (class `operativeWords`), built and measured, not installed.** The court's own "rejected /
  repudiated / no longer to be followed" on a named case. Checker, scope demotion ("partly negative unless the whole
  case is disposed of") and theorems are in Lean; the rows of this round failed the blind audit.
- **Field limits and doctrine labels:** display columns only (`treatment_class.tsv`, `classes.tsv`).
- **Classes on every output row** (`oclass` on status and findings; `classes.tsv`), in round-5 mode only. Without
  `treatment_class.tsv` the new program's output on the round-4 data is byte-identical to round 4's.
- Lean: 175 theorems (141 + 34), 0 earlier statements changed, locked and checked; 34 mutants (27 + 7), all killed;
  no `sorry`, no new axiom, no `native_decide`.

## Scores, before and after (before = round 4)

| Measure | Round 4 | Frozen build |
|---|---|---|
| Fresh lists, open half (165): strict | 50 = 30.3% [23.8, 37.7] | 50 = 30.3% [23.8, 37.7] |
| open half: overruled by the listed case from a later court's date | 0 | 30 |
| open half: lenient | 86 = 52.1% [44.5, 59.6] | 108 = 65.5% [57.9, 72.3] |
| **Sealed half (127), single run: strict** | 32 = 25.2% [18.4, 33.4] | 32 = 25.2% [18.4, 33.4] |
| sealed half: overruled by the listed case from a later court's date | 0 | 25 |
| **sealed half: lenient** | 59 = 46.5% [38.0, 55.1] | 77 = 60.6% [51.9, 68.7] |
| sealed half, implied pairs (21): lenient | 1 | 5 |
| Model's Supreme Court overrulings on a fresh list, open / sealed half | 50 of 53 / 32 of 43 | 80 of 93 / 57 of 76 |
| Held-out notes, pool 9,374: negative or partly by Y | 3.1% | 1,302 = 13.9% (13.2–14.6) |
| pool, also stated by a court with power (2,640) | 1.4% | 932 = 35.3% (33.5–37.1) |
| pool, held-out courts only (6,734) | 3.8% | 370 = 5.5% (5.0–6.1) |
| Reverse confirmation: self-announced rows / recognised rows | 93.3% / – | 598/641 = 93.3% / 170/181 = 93.9% (89.4–96.6) |
| Leak check | 0 leaks | 0 leaks (exit 0; 16 warnings, rows the checker refuses) |
| Behaviour, bound courts, 10 y: self-announced whole case | 0.61 (0.54–0.69), n = 1,676 | 0.64 (0.57–0.72), n = 1,474 |
| Behaviour: recognised, whole case | – | 0.78 (0.50–0.91), n = 207; without reporting citations 0.68 (0.45–0.79) |
| Behaviour: recognised, part of the case | – | 0.85 (0.75–0.95), n = 957 |
| Behaviour: at-risk witness tier | 0.89 (0.64–1.30), n = 88 | 1.09 (0.70–1.62), n = 45 |
| SCDB (burned, not blind) | 141/278 | 141/278 explicit; 175/278 with recognised rows |
| CRS current table (burned, not blind) | 162/292 | 162/292 explicit; 195/292 with recognised rows |
| Treatment rows / recognised by the checker | 35,365 / 0 | 41,476 / 6,161 |
| Theorems / mutants | 141 / 27 | 175 / 34 |
| Lean vs reference: regression set; new universes; real data | 0; –; 0 | 0 of 118; status 0 of 55,055 keys (13 of 300 universes differ on a verdict, old cause); 2 of 6,163 recognised rows |

Dev and sealed halves moved alike (lenient +13.3 and +14.1 points). Nothing was re-tuned after the sealed run.

## Blind audits (Claude auditors; Wilson 95%)

| Rows | Sample | Right | Right and extent | Decision |
|---|---|---|---|---|
| Recognised, read, whole case (747) | 70 | 94.3% [86.2, 97.8] | 91.4% [82.5, 96.0] | installed |
| Recognised, read, part (683) | 70 | 97.1% [90.2, 99.2] | 97.1% | installed |
| Recognised, pattern, other grounds (4,685) | 70 | 97.1% [90.2, 99.2] | 97.1% | installed (partly negative only) |
| Recognised, round-4 witness rows (37) | 37 | 97.3% [86.2, 99.5] | 89.2% [75.3, 95.7] | installed |
| Control, self-announced | 30 | 96.7% | 90.0% | – |
| Operative words, part (614) | 80 | 78.8% [68.6, 86.3] | 78.8% | **not installed** |
| Operative words, whole (41) | 41 | 26.8% [15.7, 41.9] | 26.8% | **not installed** |

The 14 recognised rows marked wrong were removed, with one row found through the dev diagnosis (Oregon v. Mitchell,
a single Justice's opinion read as the Court's).

## Iterations (detail in LOG.md)

1. `it0_claims`: recognised claims on the 179 round-4 witness rows only: 38 pass. Lenient 52.1% → 55.1%.
2. `it1`: + 1,432 read rows and 4,685 pattern rows. Lenient 62.4%; held-out pool 13.8%; audit passed.
3. `it2`: + 62 verified Supreme Court rows, + 665 operative-words rows, − 15 wrong rows. Lenient 66.7%. The
   operative audit failed, so:
4. `final` = `it2` without the operative-words rows. Lenient 65.5%. Frozen; sealed half run once: 60.6%.

## Diagnosis (what the ceilings are)

- 66 old wordless SCDB misses: recognised by a later Court 10; own operative verb 4; doctrine/field only 19;
  nothing 35 (`diag/scdb66.tsv`).
- 113 open-half misses: fixable by recognition 34; list entry doubtful 18; operative 17; nothing 15; doctrine/field
  12; reader recall 12; scope label 5 (`diag2/dev_misses.tsv`).
- Open half, all 165 pairs: announced with a term of art 84 (51%); the court's own other words 30 (18%); never
  stated by the overruling court 33 (20%); doubtful entries 18 (11%).

## Residuals and what was cut

- **Cut for time:** the fuzzer extension (agent died in the crash, not restarted); the scope-label fix and the
  reader-recall fixes from the dev diagnosis (17 pairs); a decoy set for the audits (the builder produced 1 usable
  decoy); updates to LEAN.md / TRUST.md beyond a short note; installing the frozen build over `data/` and `out/`.
- **Open defect, older than this round, found by the new generator:** Lean reads an unknown date (0) as a real day in
  the power lookup (`powerAnyDomain`, `powerOn`, and the `citesLaterNegated` test); the reference says "unknown". 13
  of 300 universes; no status key. Patch text is in `round5/triage/`; it changes round-4 behaviour and needs its own
  baseline run.
- **Successor courts:** `canChangeStatus` gives a successor the power only between courts of last resort; 2 real
  recognised rows (New Jersey) are refused by Lean and admitted by the reference.
- The opinion-part map cannot separate an opinion announcing the judgment for one Justice from the Court's opinion.
- Strict recall cannot move under the agreed timeline (negative only from the later court's date).
- The earlier rounds' 2,315 rows with operative wording stay installed and were not re-audited; this round's audit of
  new rows of that kind suggests they deserve one.
- Payne v. Tennessee n.1 carries 12 of the 30 new open-half hits; entries it does not mark "in part" were read as
  whole although the sentence it hangs on says "in whole or in part".

## Decisions for the user

1. Install the frozen build over the live tables (`data/*.tsv` with `*.pre_round5.tsv` copies, `out/`)? Not done.
2. Keep "negative only from date(W)" (strict recall fixed at 30% / 25%), or let a recognised overruling count from
   date(Y) in reports while the model keeps the unknown interval?
3. Read the Payne footnote entries as whole (as now) or as partial (12 open-half hits become "partly negative")?
4. Re-audit the 2,315 earlier operative-wording rows, given 79% / 27% on this round's.
5. Fix the date-0 power lookup and the successor-court power (both change round-4 output)?
6. Blog wording: see the last section of the report. The post was not edited.
