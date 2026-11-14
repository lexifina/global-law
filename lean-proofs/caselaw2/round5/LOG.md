# Round 5 log (each iteration: what changed, every score before/after, what was learned)

All reading by Claude sub-agents. No external model. Nothing committed. Times are local, 13 Nov 2026.

## 0. Baseline (round-4 output, `out/`, unchanged)

| Test | Figure |
|---|---|
| Fresh lists, dev (165 pairs): strict / lenient | 50/165 = 30.3% [23.8, 37.7] / 86/165 = 52.1% [44.5, 59.6] |
| dev outcomes a / a_date / a_kind / b / c / d / e | 50 / 0 / 0 / 2 / 34 / 12 / 67 |
| Fresh lists, sealed test (127 pairs), run by the key's builder, not by us | 32/127 = 25.2% [18.4, 33.4] / 59/127 = 46.5% [38.0, 55.1] |
| Holdout notes, testable pool (9,374 pairs): negative by Y / negative or partly | 0.3% / 3.1% |
| pool, also stated by a feed speaker (2,640) | 0.1% / 1.4% |
| pool, holdout speakers only (6,734) | 0.3% / 3.8% |
| Reverse confirmation of the model's own negative rows (precedent) | 598/641 = 93.3% (91.1-95.0) |
| Behaviour, bound courts, 10 years: explicit / partly / implicit DiD | 0.609 (0.544-0.685) / 0.587 (0.472-0.687) / 0.894 (0.641-1.300), n = 1,676 / 6,087 / 88 |
| check_no_leak on round-4 inputs | 0 leaks, 16 warnings |
| SCDB (burned): found / precision | 141/278 / 141/152 |
| Lean: theorems / mutants | 141 / 27 x 27 |

Sources: `gold_fresh/GOLD_FRESH.md`, `tests/TESTS.md`, `ROUND4.md`.

## 0a. Diagnostic of the 66 wordless SCDB misses (burned list; diagnosis only; `diag/scdb66.tsv`)

Four readers, every opinion of the Court read. Labels per decision (several can apply): A (own operative verb on
the named case) 4; A~ (states the contrary of named X, no verb on its authority) 19; B (doctrine / line of cases)
18; C (field-limited) 13; D (a later opinion of the Court says with "overrul..." that Y overruled X) 10, weak D 6;
E (none) 35, of which 25 have no words about X at all. Primary label (A > B/C > D > E): A 4, B/C 22, D 5, E 35.

Ceilings on the 66: recognised 10 (7 with X and Y in one sentence); operative words 4 (none of the four uses a
phrase of the provisional cue list); doctrine/field only 19; nothing 35. In 17 of the 66 the list's entry itself
looks doubtful (same case on rehearing, a later Court credits another decision, nothing overruled).

Learned:
- The typed later-court notes catch "X, overruled by Y" but not "Y, overruling X" or "(overruling X)", which is how
  the Supreme Court writes it. The recognised candidates therefore also need a scan of Supreme Court opinions.
- The operative-words step has a low ceiling on this list. The common own-words form is a contrary statement with
  no verb on X's authority ("notwithstanding what is said in X"); that is an inference from a holding and stays out.
- Two installed round-4 witness rows quote the wrong list item (`tw:6043664:5986747:3720:6110802`,
  `tw:6123197:5951175:44727:6129139`); neither names X or Y in the quote, so the round-5 in-quote test rejects both.

## 1. Build 1 (12:00-12:15): Lean extension, baseline identity

- Lean: `Recog` on `TEvent`, `Unk.recognisedLater`, `recogEffects`, `demote`, `Spec/Recognised.lean` (theorems),
  `Cert.Mode`, `checkRecognised`, `checkOperative`, `classOf`, `Findings.citedRecognisedLater`, `Data.ClassRow`,
  runner wiring, `classes.tsv`, `oclass` columns. No sorry, no axiom, no native_decide.
- `audit.py check`: 175 theorems (141 + 34 new), 0 existing statements changed, 0 problems.
- Mutants: 34 (27 + M28-M34), properties 35 (27 + 8); every property holds of the spec, fails on a mutant; every
  mutant is caught.
- **Baseline identity**: the new runner on the round-4 tables (no `treatment_class.tsv`) gives status, findings,
  certs, splits, status_lines and horty byte-identical to the round-4 final output (`difftest/real20/lean`), and the
  same summary counters (`wsl/r5_base.sh`).

## 2. Iteration 1 (variant `it1`, scored 13:48): recognised overrulings

What `it1` is: the round-4 data, plus rows of the new class "recognised" (a later court with power says in its
opinion that X was overruled by Y), from three sources:
- **Read rows (1,432).** Claude readers read 59 packs (2,838 passages): the 179 witness rows of round 4 again, 52
  later-court notes about Supreme Court cases, 528 passages found by our own scan of Supreme Court opinions for
  "Y, overruling X" / "X, overruled by Y", and 1,807 notes by state and federal courts with power over the case.
  1,842 were judged to be statements; after removing duplicates of a pair and quotes the checker would refuse, 1,432
  rows were certified.
- **Pattern rows (4,685).** Notes of the fixed form "X-citation, overruled on other grounds by Y-citation", certified
  without a reader. These can only make a case *partly* negative, never overruled.
- The 179 round-4 witness rows, each now claiming the new class; the checker decides.
The Lean checker recognised 6,152 rows in all (it refuses a row when the later court has no power over the case,
when either case is not named inside the quoted sentence, or when the sentence is a negation, question or argument).

Before / after (dev half of the fresh lists, 165 pairs):

| | Round 4 | it1 |
|---|---|---|
| Overruled by the listed case from its own date (strict) | 50 = 30.3% [23.8, 37.7] | 50 = 30.3% [23.8, 37.7] |
| Overruled by the listed case, from the date a later court said so | 0 | 28 |
| By another case / partly negative / at risk only / nothing | 2 / 34 / 12 / 67 | 4 / 21 / 0 / 62 |
| Lenient | 86 = 52.1% [44.5, 59.6] | 103 = 62.4% [54.8, 69.5] |
| Pairs a list calls implied (20): lenient | 1 | 4 |
| Model's Supreme Court overrulings in this half that are on a fresh list | 50 of 53 | 78 of 91 (12 on no list, 1 under another overruler) |

Strict cannot move by design: a recognised overruling is negative only from the later court's date, and strict
asks for the overruling decision's own date.

Held-out later-court notes (statements by courts WITHOUT power; none of them can enter the model):

| | Round 4 | it1 |
|---|---|---|
| Testable pool (9,374 pairs): negative or partly negative by the named case | 3.1% | 1,294 = 13.8% (13.1-14.5) |
| of which pairs a court with power also states (2,640) | 1.4% | 932 = 35.3% (33.5-37.1) |
| of which pairs only held-out courts state (6,734) | 3.8% | 362 = 5.4% (4.9-5.9) |
| The model's own negative rows confirmed by a held-out note naming the same overruler: explicit rows | 598/641 = 93.3% | 598/641 = 93.3% (91.1-95.0) |
| the same for the new recognised rows | 13/17 (round-4 witness rows) | 164/176 = 93.2% (88.5-96.1) |
| Leak check | 0 leaks | 0 leaks (exit 0) |

Behaviour (citations from bound courts, 10 years either side, against matched controls; 1.00 = no change):
recognised, whole case, event dated at Y: 0.81 (0.62-0.96), n = 205; without citations that themselves report the
overruling 0.73 (0.56-0.86). Recognised, part of the case: 0.83 (0.73-0.93), n = 961. Explicit rows (calibration)
about 0.61. Placebo for the partly-recognised class 1.09 (0.98-1.21).

Old lists (burned, not blind): SCDB 141 -> 170 of 278 when recognised rows count; Constitution Annotated current
table 162 -> 187 of 292.

Learned:
- The recognised rows confirm at the same rate as the explicit rows (93%), and courts bound by a recognised-overruled
  case do cite it less after the overruling decision, by about half the drop seen for explicit overrulings.
- The small rise on held-out-only pairs (3.8% -> 5.4%) is expected leakage of *facts*, not of words: our own scan of
  Supreme Court opinions and the pattern rows reach pairs that the typed notes table never credited to a court
  with power.
- Plessy is still only "partly negative": the row that carries it quotes Justice Black's opinion in Oregon v.
  Mitchell (1970), which the part map calls the opinion of the court but which is his own. The Dobbs sentence
  ("the Court overruled the infamous decision in Plessy v. Ferguson") is in a pack that had not been read yet.

## 3. Blind audit of the recognised rows of `it1` (13:52)

Seven Claude auditors, one pack each, 278 passages. Each was shown about 2,000 characters of the speaking decision
and a neutral claim ("X lost authority through Y"), not the class, not the reader's quote, not why the row was
picked. "Right" = the court itself states it, X is right and Y is right. "Right and extent" also requires that a row
the model treats as overruling the whole case is read by the auditor as the whole case.

| Rows | Population | Sample | Right | Right and extent |
|---|---|---|---|---|
| Recognised, read, whole case (these make a case overruled) | 747 | 70 | 66 = 94.3% [86.2, 97.8] | 64 = 91.4% [82.5, 96.0] |
| Recognised, read, part of the case | 683 | 70 | 68 = 97.1% [90.2, 99.2] | 68 = 97.1% |
| Recognised, by pattern ("overruled on other grounds by") | 4,685 | 70 | 68 = 97.1% [90.2, 99.2] | 68 = 97.1% |
| Recognised, round-4 witness rows that pass the new check | 37 | 37 | 36 = 97.3% [86.2, 99.5] | 33 = 89.2% [75.3, 95.7] |
| Control: self-announced rows of earlier rounds | 30 | 30 | 29 = 96.7% [83.3, 99.4] | 27 = 90.0% [74.4, 96.5] |
| All, weighted by population | 6,182 | 277 | 96.8% [93.8, 99.8] | 96.4% [93.3, 99.4] |

Decision: every recognised stratum is at or above the 90% bar on its point estimate, and level with the control;
the class is installed as status-changing. The 14 recognised rows the auditors marked wrong were removed.
Weakness of this audit: the decoys failed to build (1 decoy instead of about 45; that one was accepted), so the
auditors' tendency to say yes is measured only through the control rows and the 17 rows they did reject.

## 4. Lean against the Python reference, first sweep (13:53)

Regression set (118 universes of earlier rounds): 0 disagreements. 300 new universes with witness rows and class
claims: status 0 of 55,638 keys; 73 universes differ on other files. Cause 1 (62 universes): Lean classed a row
"recognised" when the overruling decision Y had no power over X (the row had no effect either way; only the class
label and a counter were wrong). Lean fixed. Cause 2 (10 universes): a witness row Lean admits and the reference
refuses for want of standing; being triaged.

## 5. Iteration 2 (variant `it2`, scored 13:59): operative words added, one fix from the dev diagnosis

What `it2` is: `it1`, plus (a) 62 more recognised rows from the remaining Supreme Court passages (2,347 loose
passages pre-screened by a smaller Claude model, its 64 positives re-read by the main model: 62 kept), (b) 665
operative-words rows (the court's own "rejected", "repudiated", "no longer to be followed" on a named case; 44
packs, 2,179 passages read, 42 rows claim the whole case), minus (c) the 14 recognised rows the blind audit marked
wrong and one row found through the dev diagnosis: it quoted Justice Black's own opinion in Oregon v. Mitchell
(1970) as the Court's. The Dobbs sentence about Plessy is now in.

| Dev half, 165 pairs | Round 4 | it1 | it2 |
|---|---|---|---|
| Strict | 50 = 30.3% | 50 = 30.3% | 50 = 30.3% [23.8, 37.7] |
| Overruled by the listed case from a later court's date | 0 | 28 | 30 |
| By another case / partly / at risk / nothing | 2 / 34 / 12 / 67 | 4 / 21 / 0 / 62 | 6 / 24 / 0 / 55 |
| Lenient | 52.1% | 62.4% | 110 = 66.7% [59.2, 73.4] |

Held-out notes, `it2`: pairs a court with power also states 942/2,640 = 35.7% (33.9-37.5); held-out-only pairs
427/6,734 = 6.3% (5.8-6.9); reverse confirmation of recognised rows 170/181 = 93.9% (89.4-96.6), of the five
whole-case operative rows that a held-out note speaks of 3/5. Leak check: 0. Behaviour (bound courts, 10 years):
recognised 0.79 (0.49-0.92), n = 204; partly recognised 0.85 (0.75-0.96), n = 962; operative words incl. the
earlier rounds' rows 0.51 (0.35-0.75), n = 202; explicit 0.62 (0.54-0.71). Old lists (not blind): SCDB 176/278,
Constitution Annotated 197/292.

## 6. Blind audit of the operative-words rows (14:03): the class fails the bar and is NOT installed

Four auditors, 141 passages (121 operative rows and 20 control rows; scored on the 106 answered when the decision
was taken, final figures in the round report). Operative words on part of a case: 45/60 = 75.0% [62.8, 84.2].
Operative words said to dispose of the whole case: 8/31 = 25.8% [13.7, 43.2]. Control (self-announced rows):
15/15. The usual error: the sentence says the earlier case "is no longer the law" because of a statute, a rule
change or ANOTHER decision; it is a report, not the speaking court's own act. Both strata are below the 90% bar
for rows that change a status, so the class is measured but not installed. The final build has no operative-words
row of this round (the earlier rounds' rows with such wording stay, classed `operativeWords`). Brown's own sentence
("Any language in Plessy v. Ferguson contrary to this finding is rejected") was certified and admitted by the
checker in `it2`; it is not in the final build.

## 7. Lean against the reference: triage (14:02)

- Regression set (118 universes): 0 disagreements.
- 300 new universes: status 0 of 55,638 keys. After the class fix, the remaining differences (12 universes) have one
  cause, and it predates this round: Lean reads an unknown date (0) as a real day when it looks up a court's epoch,
  so an undated decision can be given or refused power; the reference says "unknown". Not fixed in this round (a fix
  changes round-4 behaviour and needs its own baseline run); recorded as an open defect.
- Real data (`it2`): status, findings, certificates agree except for 2 of 6,163 recognised rows. Both are New
  Jersey: the later court sits in a successor of the earlier court (not a court of last resort), the reference
  gives a successor the power, Lean does not, so Lean refuses the two rows. Lean is the stricter side; recorded.

## 8. Frozen build and the sealed half (14:05-14:07)

`final` = `it2` without the operative-words rows. Open half: strict 50 = 30.3%; overruled from a later court's date
30; lenient 108 = 65.5% [57.9, 72.3] (it2 was 66.7%: the two points were operative rows). Held-out notes: pool
13.9%, also-in-feed 35.3%, held-out-only 5.5%; recognised rows confirmed 170/181 = 93.9%. Leak check 0. Behaviour:
recognised whole case 0.78 (0.50-0.91), n = 207; part 0.85 (0.75-0.95), n = 957.

Theorem lock: 175 theorems, `audit.py check` 0 problems (exit 0), full build with the lock's guards green.
Second sweep on the frozen code (seeds 74000-74299): status 0 of 55,055 keys; 13 universes differ on one
certificate verdict each (the date-0 cause). Real data: 2 of 6,163 recognised rows differ (successor courts).

`FREEZE.md` written 14:05 (hashes of Lean sources, cue table, reference, readers, data, output). Then the sealed
half, once: 127 pairs; strict 32 = 25.2% [18.4, 33.4] (unchanged, by design); overruled from a later court's date
25; lenient 77 = 60.6% [51.9, 68.7] (round 4: 46.5% [38.0, 55.1]); implied pairs 5 of 21 (1 before); outside the
Constitution Annotated 3 of 8 (2 before). The open half had moved by 13.3 points, the sealed half by 14.1. Nothing
was changed after the run.

Final operative-words audit (all four auditors): part 63/80 = 78.8% [68.6, 86.3]; whole 11/41 = 26.8% [15.7, 41.9];
control 20/20.
