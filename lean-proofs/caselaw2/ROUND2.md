# caselaw-lean-2: round 2 (12 Nov 2026, 21:45–22:45)

All model reading and auditing in this round was done by Claude subagents. No Azure or other external model was
called. Nothing was committed to git. Each stream was time-boxed to about 40 minutes; what did not fit is listed
under "Next round" in each section. The full logs are in `round2/` (`recall.md`, `lean.md`, `courts.md`,
`enbanc.md`, `splits.md`).

## Final integration (run once, at the end)

| Check | Result |
|---|---|
| `lake build` + native runner (WSL, Lean 4.35.0) | green |
| `audit.py check` | 137 theorems (114 before), 4 with no axioms, 0 statement changes, 0 problems; no sorry, axiom or native_decide |
| Mutation matrix | 26 properties × 26 mutants (22 × 22 before), complete |
| Regression set, 111 universes (`regress13`) | 0 disagreements |
| Sweep, seeds 57000–57499, 500 universes, all generator layers (`drt9`) | 8 universes disagree, all conflict rows: 17 of 4,977 keys. Status 0/75,511, findings 0/35,566, certs 0/89,748, splits 0/10,939, per-line rows 0/7,332, Horty 0/1,450 |
| Real data, snapshot of 22:31 (`real18`) | **0 disagreements**: status 0/396,606, findings 0/144,218, certs 0/347,744, splits 0/359, conflicts 0/101, per-line rows 0/301, Horty 0/44 |

- The real-data residual was 11 keys (`real17`: 5 status and 6 finding `firm` flags). It is now 0.
- An earlier sweep in this round (`drt8`, seeds 56000–56499) had 15 disagreeing universes. Eleven had one root, a
  reference bug (the firm run left a decision of a court ended by a split with no holder). It was fixed in the
  reference; the Lean did not change. DIFFTEST.md §9.4 has the triage table.
- Outputs copied to `out/` (new files: `status_lines.tsv`, `horty.tsv`). `eval/score_final.txt` and the report were
  regenerated. The round-1 score is kept as `eval/score_round1.txt`.

## 1. Recall of overrulings

| Measure (Lean output, `score.py`) | Before | After |
|---|---|---|
| Hunt's 42 literature overrulings: negative from the right date | 21 | 25 |
| Hunt's 42: partly negative / atRisk only / still good | 3 / 3 / 15 | 4 / 2 / 11 |
| CRS current table | 85/292 = 29.1% | 126/292 = 43.2% |
| CRS 2016, express | 70/243 = 28.8% | 108/243 = 44.4% |
| CRS 2016, all | 72/311 = 23.2% | 112/311 = 36.0% |
| SCDB recall | 82/278 = 29.5% | 113/278 = 40.6% |
| SCDB precision | 82/85 = 96.5% | 113/125 = 90.4% |
| Treatment rows / admitted | 31,841 / 21,527 | 32,458 / 23,015 |
| Later-court notes naming an overruling: agreement | 29.8% | 31.6% |
| Admitted overrulings confirmed, among noted | 82.3% | 82.1% |

- The hunt row "atRisk only / still good" differs by measure: the recall agent's own count on the reference
  output was 6 / 7; `known.py` on the Lean output gives 2 / 11. The two were not reconciled.
- **Diagnosis of the 496 misses** (`round2/recall_misses.tsv`): reader rule 260 (no scan pattern 126, not
  act-shaped 70, wrong part map 22, report 18, procedural 15, other 9); implicit, no words 169; target unresolved
  30; other 26 (mostly gold targets that are a different case on the same page); treating decision not in the
  corpus 6; certificate `noCue` 3; scope partial 2.
- **Fixed:** a part map for slip opinions, a rescan with 8 new wording families and 14 new act shapes, wider target
  resolution (name phrases, anaphora). Claude subagents read 1,224 items (all Supreme Court items, 960 from courts
  of last resort) and produced 596 new certified rows. 880 existing rows were repaired (646 "no longer follow"
  rows relabelled overruled, 172 name evidences rewritten, 62 quotes re-cut). The cue lists for overruled and
  declinedToFollow were widened in `Certificate.lean` and in the reference.
- **Implicit tier:** 21 rows with `explicit = 0`, reader `claude-subagent:implicit`. They never change status and
  show as atRisk only. The row's by-decision is the later court that states the overruling, because both checkers
  need the quote in the by-decision's text. `score.py` reports them on a separate line and keeps them out of every
  recall and precision figure.
- **Blind audits (Wilson 95%):** new explicit rows 30/30 right act and target (89–100%), 28/30 right kind;
  relabelled rows 22/25 (70–96%); implicit rows 21/21 (85–100%).
- **Cost in precision:** SCDB precision fell from 96.5% to 90.4%. Twelve Supreme Court decisions now carry an
  admitted overruling that SCDB does not flag. They were not audited one by one.

**Next round.** About 17,000 unread candidate items and 25 repos not resolved. Hard-wrapped slip opinions break
sentence splitting, so *Dobbs*, *Wayfair* and *Loper Bright* are unread. *Plessy*, *Lochner*, *Swift*, *Wolf*,
*Ohio v. Roberts*, *Halper*, *Quill*, *Roe*, *Casey*, *Chevron* and *Logan Valley* are still good law in the
model. The reach step has not run on the 392 new `partialUnknown` rows. The 169 implicit misses need a larger
implicit tier; keying it on the overruling decision needs a small checker change (a witness text hash).

## 2. Per-heir status everywhere

- **Before:** per-heir status applied to the citation findings only (DEVIATIONS 69).
- **After:** a new module `Spec/Lines.lean` and DEVIATIONS 74–79. Per-heir rows are written to a new file
  `out/status_lines.tsv` (the `status.tsv` columns plus `line`: `orig` or the heir's court id), only where a
  line-limited effect exists. `status.tsv` keeps the union status and its old format, because several tools read it
  by position. Splits and conflicts are judged with each holding's status in the line of the court asked about.
  Horty binding bases hold a precedent only if it is good law in that court's line (`out/horty.tsv`).
- **Theorems:** 114 → 137, all 23 new ones locked. Among them `lineStatus_heir_agrees`,
  `heldIn_ignores_unreaching`, `conflict_in_line_ignores_unreaching`, `mem_lineBase_iff`, and the reductions to the
  union definitions when no heir exists (`lineStatus_all`, `heldIn_all`, `lineBase_all`, `statusFor_le_status`).
- **Mutants:** M23–M26 added; the matrix is 26 × 26 and complete. 35 new `#guard`s (*Bonner*, *Salinas*–*Adamson*,
  *M.A.P.*, CCPA).
- **Reference:** implemented by a separate subagent from the written reading only. It now also computes Horty
  binding bases, so Horty is compared for the first time. `diff.py` compares two more files (`lines`, `horty`).
  The generator has a new `lines` layer.
- **Real data:** 622 per-line rows; 301 keys compared, 0 disagreements. 44 Horty bases compared, 0 disagreements.

**Next round.** One open sweep class: conflict rows that only the reference reports, at an adopter of a ceased
court or a trial court below it (17 of 4,977 conflict keys in 500 universes; generator layer only, none on real
data). Three readings the reference chose where DEVIATIONS 74–78 are silent agree with the Lean on every compared
key but are not yet written into DEVIATIONS. The self bases and the Horty finding rows are still Lean only.

## 3. Court epochs

| `courts2.tsv` | Before | After |
|---|---|---|
| Rows | 3,019 | 3,106 |
| Court ids with a non-zero start | 86 | 2,671 |
| Court ids with an end | 7 | 168 |
| Decisions dated outside their court's epoch | 0 | 0 |

- Starts: 11 from `succession.tsv`, 5 from known dates, 2,576 from the first decision. Ends: 14 from
  `succession.tsv`, 135 known (133 are the US circuit courts abolished in 1912), 17 from the last decision.
- 839 decisions are dated after their court's firm end (Court of Claims 486, Alabama Court of Appeals 21). They
  get 88 short epoch rows of their own, so the court is gone on every other date.
- Federal Circuit succession and adoption rows went from L to S (*South Corp.*, read in the corpus). The Alabama
  row `1 → 3` is now a `rename`.
- Effect on the reference run: status and splits unchanged; 113 `citesLaterNegated` findings gone (102 because the
  citing court had ended before the negating date), 3 new findings, 48 conflict rows now point at a living court.

**Next round.** Re-route the 839 stray decisions and drop the cluster rows. Give Eleventh Circuit district courts
a Fifth Circuit epoch before 1981, and Tenth Circuit districts an Eighth Circuit epoch before 1929. Both engines
drop a `citesLaterNegated` finding when the citing court has no epoch on the negating date; whether that is right
was not decided. Dates still from memory: Tenth Circuit 1929, New Jersey 1948.

## 4. En banc by court size

- New table `data/court_size.tsv`: 23,399 rows, 218 courts, 17,474 court-years, from 939,751 decisions re-read
  from git. Tags: U 22,485, S 818, L 96.
- 3,817 overruling decisions relabelled in `decisions2.tsv`: unknown → wholeCourt 3,605, panel → wholeCourt 172,
  panel → enBanc 40. Scope: the treating decisions of `treatments.tsv` only.
- **Blind review:** relabels 29/30 right (83–99%). Courts whose units are divisions (AZ, WA, OK Civ. App., IN, TN)
  were then excluded after the one error. Full-court decisions still labelled panel: 31% → 17% estimated, on 18
  scored decisions (interval 4–49%).
- `panelDepartsWithoutEnBanc`: 696 → 664 in the Lean output (the reference alone, on this change alone:
  677 → 543; the new overruling rows of item 1 add findings).
- Of the 161 decisions the hunt's second reader called en banc, 123 → 135 are now labelled en banc or whole court.

**Next round.** Decisions that name only the author. The bulk pass over small and always-full intermediate courts
(written, not run). Bench is still unknown for 3.18M decisions. Louisiana five-judge panels stay panel. A larger
left-as-panel sample to narrow the 17% estimate.

## 5. Split recall

| Measure | Before | After |
|---|---|---|
| Section-level recall, Lean as-of table (`score.py`) | 109/714 = 15.3% | 164/714 = 23.0% |
| Section-level recall, reference first-date table | 135/714 = 18.9% | 255/714 = 35.7% |
| Splits detected on or after resolution (Lean as-of) | 485 | 436 |
| Split rows as of today (Lean) | 436 | 460 |

- 62 Supreme Court holdings were linked to existing split questions, under the same issue keys, with certificates.
  60 of the 332 split rows of the baseline (26 questions) are now resolved. Both named examples are resolved
  (*Burlington Northern v. White*; *Niz-Chavez*).
- 115 new split questions with 233 circuit holdings, from cross-circuit declined-to-follow pairs with a US Code
  citation nearby (327 pairs read, 118 accepted).
- **Blind review:** resolution links 36/37 (86–99.5%; the failure was dropped); new split pairs 42/42 (92–100%,
  with easy decoys, so probably overstated). The 26 links on the new questions were not audited.
- Most of the recall gain is coincidental: 65 of the 120 newly found gold rows sit on five much-litigated
  sections (31 on 42 U.S.C. § 1983). Counting only gold rows whose own conflict decisions appear in a split
  question, recall moved 25/464 → 28/464.
- The as-of measure understates recall once resolutions are linked, because resolved splits leave that table.

**Next round.** 293 gold splits on sections never read for splits; 308 cross-circuit pairs unread. The clustering
and answer-polarity classes (50 and 94 misses). 449 candidate pairs skipped because the Supreme Court decision has
no recorded holdings. The syllabus of slip opinions can cut the opinion short in `core.court_parts`. One likely
duplicate question (`usc:18:1546(a):x0` and `:q35`).

## 6. Doctrine check of the three dates

Four of the eight searches were used; decisions were read in the corpus.

| Rule | Before | After |
|---|---|---|
| Ohio prior-panel rule | from 1 July 2010, tag L | from 2 Oct 2008, tag S (*McFadden v. Cleveland State Univ.*, 2008-Ohio-4914). App.R. 26(A)(2) of 2010 is only the procedure |
| Louisiana within-circuit rule | from 1997, tag L | date kept, tag U. No source gives 1997; statements go back to 1985. A 1985 start was tried and not installed |
| Federal en banc date | 1 Sept 1948, tag L | confirmed, tag S (28 U.S.C. § 46(c); *Ex parte Collett*, 337 U.S. 55; *Western Pacific*, 345 U.S. 247) |

**Next round.** Louisiana: recover the units before moving the date. Check the Ohio value `withinUnitOnly` after
2008.

## 7. Split successors without a firm adoption row

- **Before:** 11 residual `firm` flags on real data (DEVIATIONS 73, open).
- **Reading (both sides):** a `split` succession row alone transfers no precedent; only an adoption row does
  (*Bonner v. City of Prichard*; *Estate of McMorris*).
- **Alabama:** the Court of Criminal Appeals is the old Court of Appeals continued (*Coalite v. Aldridge*, 1969;
  Act No. 987), so its adoption row went from U to S. No adoption was found for the Court of Civil Appeals; its
  row stays U.
- **After:** 0 residual on real data. DEVIATIONS 73 is closed.

## 8. Housekeeping

- `hunt/HUNT.md`: the Hunt module is imported by `Core.lean` and its 14 theorems are registered; the 77,575
  figure is corrected (7,342 were really mislabelled); the "What to fix" list marks what is done.
  `hunt/summary.json` and `hunt_summary_top.py` carry the corrected figure.
- New `LIMITS.md` records limits 5, 6, 7 and 12. The report's limits table reads it: 6 (Horty) and 12 (commission
  opinions) are fixed; 7 (Windows Application Control) is the user's to set.
- `report/make_report.py`: certificate rows admitted and rejected are no longer summed over the 8 shards (77,326
  and 9,455 on the round-1 output, not 618,608 and 75,640). The headline declarations tile uses the
  compiled-environment count from `report/caselaw-v1-v2.json`, as the figure does; the regex count is labelled.
- Not done: `report/caselaw-v1-v2.json` and the figure were not regenerated (their generator was not found), so
  the declaration count and the figure predate `Spec/Lines.lean`.
