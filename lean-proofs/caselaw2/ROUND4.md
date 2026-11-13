# caselaw-lean-2: round 4 (12 Nov 2026, 23:15–23:45)

The last round. Mostly code and the installation of work that rounds 2 and 3 had already read. All model reading
and auditing was done by Claude subagents (two blind audit readers; four forks of the coordinator for the sweep
triage, the queue install and the panel audit). No Azure or other external model was called. Nothing was committed
to git. Part-way through, the scope was cut to what could land in one pass: items 1, 2, 3, 6 and 7 were done, 10
(docs) was done, 4 and 5 are deferred, 8 and 9 were dropped (9 was partly met by item 1). Logs: `round4/*.md`.
Work files: `work/round4/`. Backups of every edited source: `work/round4/pre/`; of live data: `data/*.pre_round4.tsv`.

## Across rounds

Lean output scored by `score.py` at the end of each round. Round 1 is the first full pass.

| Measure | Round 1 | Round 2 | Round 3 | Round 4 |
|---|---|---|---|---|
| Treatment rows / admitted | 31,841 / 21,527 | 32,458 / 23,015 | 35,021 / 24,966 | 35,365 / 25,035 |
| Supreme Court Database: flagged decisions found | 82/278 = 29.5% | 113/278 = 40.6% | 141/278 = 50.7% | 141/278 = 50.7% |
| Supreme Court Database: precision | 82/85 = 96.5% | 113/125 = 90.4% | 141/152 = 92.8% | 141/152 = 92.8% |
| Constitution Annotated, current table | 85/292 = 29.1% | 126/292 = 43.2% | 162/292 = 55.5% | 162/292 = 55.5% |
| Constitution Annotated 2016, express | 70/243 = 28.8% | 108/243 = 44.4% | 135/243 = 55.6% | 135/243 = 55.6% |
| Constitution Annotated 2016, all | 72/311 = 23.2% | 112/311 = 36.0% | 139/311 = 44.7% | 139/311 = 44.7% |
| 42 literature overrulings: negative from the right date | 21 | 25 | 29 | 29 |
| 42 literature overrulings: still good, no finding | 15 | 11 | 3 | 0 |
| Split recall, section level | 109/714 = 15.3% | 164/714 = 23.0% | 171/714 = 23.9% | 171/714 = 23.9% |
| Theorems / mutants killed | 114 / 22 | 137 / 26 | 137 / 26 | 141 / 27 |
| Generated universes that disagree (500-round sweep) | 0 of 1,000 (older generator) | 8 (17 keys) | 3 (10 keys) | 0 |
| Real data: keys on which Lean and the reference differ | 11 | 0 | 0 | 0 |

Round 4 did not aim at recall: it installed the implicit tier (which never changes a status), made the two checkers
and the reader share one cue table, closed the sweep residue and cut a finding that had lost its precision.

## Final integration (23:25–23:34)

| Check | Result |
|---|---|
| `lake build` + native runner (WSL, Lean 4.35.0) | green on the first build |
| `audit.py lock`, then `check` | 141 theorems (137 before), 4 with no axioms, 0 statement changes, 0 problems; no sorry, axiom or native_decide |
| Mutation matrix | 27 × 27 (26 × 26 before): property "checkWitness_sound / witness_row_no_effect", mutant M27 |
| Regression set, 118 universes (`r4_regress2`) | 0 disagreements |
| Sweep, seeds 63000–63499, 500 universes, all layers (`r4_drt2`) | **0 universes disagree**: status 0/75,396, findings 0/35,295, certs 0/89,464, splits 0/10,602, conflicts 0/4,603, per-line rows 0/7,228, Horty 0/1,377 |
| Real data, snapshot of 23:25 (`real20`), Lean and reference side by side | **0 disagreements**: status 0/398,482, findings 0/168,276, certs 0/350,651, splits 0/360, conflicts 0/92, per-line rows 0/309, Horty 0/44 |
| `score.py` → `eval/score_final.txt` | done; round 3 kept as `eval/score_round3.txt`, `eval/results_round3.json` |
| Figure, heatmaps, report (`report/refresh_all.sh`) | done; `~/Documents/html-reports/caselaw-lean-2.html` |

- The stages ran concurrently in one WSL call (`wsl/r4_final.sh`). The first pass showed two things. On real data,
  170 certificate keys and 145 findings differed: one bug in the new reference code (fixed; reference wrong). In the
  sweep, 1 universe (63322, 3 conflict keys) differed: the mirror of item 3's fix, in the reference (fixed;
  DEVIATIONS 86). `wsl/r4_recheck.sh` then re-ran the regression set, the whole sweep and the real-data reference:
  all zero. The Lean real-data output is that of the first pass; no Lean source changed after it.

## Before and after (Lean output, `score.py`; "before" = round 3 final)

| Measure | Before | After |
|---|---|---|
| Treatment rows / admitted | 35,021 / 24,966 | 35,365 / 25,035 |
| Witness rows (`treatment_witness.tsv`) | 0 | 179 |
| Implicit rows (`explicit = 0`) / with a passing certificate | 21 / – | 204 / 167 ok, 9 `witnessNoStanding`, rest no power or dates |
| `atRisk … inferredRejection` findings | not counted | 168 |
| *Wolf v. Colorado* | good, no finding | atRisk, naming *Mapp v. Ohio* |
| *Ohio v. Roberts* | good, no finding | atRisk, naming *Crawford v. Washington* |
| *Plessy v. Ferguson* | good, no finding | atRisk, naming *Brown v. Board of Education* |
| *Lochner v. New York* | atRisk only | atRisk only; the new row names *Moore v. East Cleveland* (the court that says Lochner was repudiated), not an abrogating decision |
| Hunt's 42: negative from the right date / by another decision / partly negative | 29 / 2 / 6 | 29 / 2 / 6 |
| Hunt's 42: atRisk only / still good | 2 / 3 | 5 / 0 |
| CRS current table | 162/292 = 55.5% | 162/292 = 55.5% |
| CRS 2016, express / all | 135/243 = 55.6% / 139/311 = 44.7% | the same |
| CRS pairs (any edition) covered by the implicit tier | 10 | 14 |
| SCDB recall / precision | 141/278 = 50.7% / 141/152 = 92.8% | the same |
| Later-court notes naming an overruling: agreement | 7,143/25,485 = 28.0% | 7,161/25,485 = 28.1% |
| Admitted `overruled` rows confirmed, among noted | 81.6% | 81.6% |
| Certificates: treatments ok / noAuthority / noCue | 33,118 / 1,816 / 41 | 33,382 / 1,934 / 0 |
| Split recall, section level | 171/714 = 23.9% | 171/714 = 23.9% (splits not installed) |
| Split recall, "honest" keys: any / opposite answers | 9/464 = 1.9% / 0 | the same |
| Split rows as of today / conflicts | 452 / 92 | 452 / 92 |
| Findings: atRisk | 85,827 | 86,228 |
| Findings: citesOverruled | 50,600 | 50,742 |
| Findings: panelDepartsWithoutEnBanc | 998 | 573 |
| Sweep residue (500 universes) | 3 universes, 10 conflict keys | 0 |
| Real-data residue | 0 | 0 |
| Theorems / mutants | 137 / 26 × 26 | 141 / 27 × 27 |
| Figure: v2 declarations / theorems drawn / modules | 955 / 161 / 22 | 992 / 165 / 23 |
| Heatmaps: bad-law citations 1990–2019 / precedent-broken events | 49,444 / 12,594 | 49,541 / 12,597 |

- The Hunt line's last two cells are counted from `out/findings.tsv`. `hunt/known.py` still prints "good" for
  *Plessy*, *Wolf* and *Roberts*: it reads atRisk rows with the target in the cited column, and the
  `inferredRejection` row has the target first. Not changed (the script is not part of the report).
- Recall on the published lists did not move: the 161 queue rows contain no new Supreme Court pair, and the implicit
  tier never changes a status by design.

## Items

### 1. Implicit-overruling tier (installed 23:24; DEVIATIONS 83)

- **Format.** `round3/implicit_schema.md`, now in SCHEMA.md: a treatments row with a line in
  `data/treatment_witness.tsv` says "X was overruled by Y" in the words of a later decision W. Both checkers
  implement it: Lean `Cert.checkWitness` (`Certificate.lean`), wired in `Run.lean`; reference `check_witness`.
  Order of checks: `witnessBadRow`, the text checks on W's window, `byUnresolved`, `targetLater`,
  `witnessEarlier`, `witnessNoStanding`, then Y's power over X.
- **Effect.** Never a status. One finding, `atRisk X Y inferredRejection`, while X is not already negative. No
  panel, unit or claim finding from a witness row.
- **Theorems (4, locked).** `Cert.witnessTail_sound`, `Cert.checkWitness_sound`, `Cert.checkWitness_inferred`, and
  `Examples.witness_row_no_effect`: the event built from an admitted witness row has no status effect (a corollary
  of `Spec.inferred_treatment_no_effect`). Mutant M27 (a checker that takes a row marked explicit, or a court with
  no standing) is killed by the new property. 12 new `#guard`s.
- **Rows.** 185 of the 189 round-3 candidates (the 4 that fail the work-folder verifier left out), plus 14 of the
  21 round-2 rows converted from "by = the stating court" to "by = Y" (13 where W cites Y in the window, and
  *Roberts* by name). 199 staged.
- **Blind audit, 24 rows, two readers** (the four landmark rows and 20 at random; passage and claim only). The court
  states it: 24/24. X right: 24/24. Y right: 21/24 (Wilson 95%: 69%–96%). The two witness rows with an unclear Y
  were removed before install. The third is the *Lochner* row, an old-format row whose by-decision is the stating
  court; it is kept and described as such.
- **Installed:** 197 treatment rows added and 14 removed (the converted originals); `treatment_witness.tsv` 179
  rows; `cert_text` +174, `window_sha` +174, `cite_index` +288. In the final run 167 of the 204 implicit rows are
  `ok`; 9 fail `witnessNoStanding`; the rest fail power or date order and assert nothing.
- Files: `work/round4/implicit_stage.py`, `work/round4/implicit/` (staged deltas, audit sheets, key, answers).

### 2. One cue table (DEVIATIONS 85)

- `tools/caselaw2/cues/cue_table.json` is the only table. `gen_cues.py` writes `LegalProofs/CaseLaw2/CueTable.lean`,
  `ref/cue_table.py` and `reader/cue_table.py`; `gen_cues.py --check` fails on a stale copy. `Cert.cues`,
  `Cert.disqualifiers`, the reference's `VERBS`/`DISQUALIFY_*`, `rules2.CUES2`/`DISQUAL2` and the implicit
  generator's table all read it.
- The difference was two cues the reader had and the checkers lacked: "abrogat" for `supersededByEnactment`,
  "no longer" for `questioned`. The shared table has both. `noCue` on treatments: 41 → 0 (the 29 of round 3 and
  12 older rows). Neither kind changes a status.

### 3. Sweep residue (DEVIATIONS 82 and 86; `round4/sweep.md`)

- The three universes of round 3 (62003, 62350, 62391; 10 keys): **Lean was wrong.** `candFor` ranked a Texas
  decision promoted by "writ refused" at its own tier, although `forceOn` already treated it as the Supreme Court
  of Texas's. Fixed in `Exec/Verdicts.lean`. Round 3's note that the court had no earlier epoch was incorrect.
- The final sweep then found the mirror case (63322, 3 keys): **the reference was wrong** (no precedence step
  between a writ-refused decision and an unpromoted one of the same court). Fixed in `_resolve`.
- All four universes are in `fixtures/regress/r4-*`. Final sweep: 0 of 500.

### 6. Reader queue: the 11 answered packs (`round4/queue.md`)

- Certified and installed: 161 treatment rows (`treatments` 35,021 → 35,182 before the implicit install).
  `ans_142.jsonl` (partial) was set aside as `ans_142.partial`.
- Blind read of 20 new rows by the fork itself (it could not spawn readers): own act 18/20 (70%–97%), target 20/20,
  kind 13/20. The two rows shown wrong were removed. `t:6865583:6852906:48056`, which round 3 left installed, was
  removed again.
- `install.py` re-adds rows removed after an audit on every run. Not fixed: the three ids must be removed again
  after any later run.
- 246 packs (about 19,600 items) remain unread.

### 7. The rise of `panelDepartsWithoutEnBanc` (DEVIATIONS 84; `round4/panel.md`)

- The 334 findings added in round 3 all come from the queue rows. Blind read of 20 (by the fork itself): the finding
  is sound in 1 (Wilson 1%–24%). In 18 the panel says circuit precedent "is no longer good law" after an
  intervening Supreme Court or state high court decision: the recognised exception to the prior-panel rule.
  Overruled-versus-disapproved confusion, bench labels and court labels were each 0 of 20. The status rows are right.
- Fix, both engines: the finding needs the panel's own overruling words in the certified quote (`overrul`,
  `disapprov`, `recede(s/d/ing) from`). 998 → 573 (the count on the round-3 data was 571; 2 come from new rows).
  It removes 318 of the 334 new findings and 109 older ones.
- The rise of atRisk (65,533 → 85,827 in round 3) was not audited. It is mostly `citesLaterNegated` (62,792 rows),
  which follows mechanically from every new status row.

### 10. Docs

- `report/heatmaps/HEATMAPS.md`: the case-law table rows, totals and peaks are now written from `heatmaps.json` and
  `series.json` by `report/heatmaps/update_md.py`, which `refresh_all.sh` runs after `plot.py`.
- `data/COURTS.md` rule 7 rewritten (no cluster rows; the round-3 re-routing).
- DEVIATIONS 82–86, DIFFTEST §11, LEAN.md (counts and a round-4 section), SCHEMA.md (`treatment_witness.tsv`).
- Report: section 14 opens with the table across rounds and the remaining items, and embeds the film; the
  differential-testing tiles read DIFFTEST §11.1; the hand-written `report/sections/why_recall.html` is embedded
  in the evaluation section.

## Residuals

- Sweep and real data: none. The generator writes no witness rows, so the witness checker is compared between
  Lean and the reference on the 179 real rows and by `#guard`s only.
- Precision of the 573 remaining panel findings: not measured after the fix. The fix also removed the one sound
  finding in the sample.
- The implicit tier's Y is right in 21 of 24 audited rows; rows like the two removed ones remain at about that rate.
- *Lochner* has no row naming an abrogating decision: no later decision in the pack says which decision did it.
- 12 older model-read `supersededByEnactment` rows now pass the cue check with "abrogated"; they were not re-read.
- Kind labels on queue rows: the auditor's kind matched in 13 of 20 (most differences: `overruled` where a panel
  reports abrogation by a higher court). Both kinds change status the same way.
- `Exec.lastEpoch`, `Exec.forceOnAs` and `candFor` have no theorem.

## Remaining and deferred

Nothing further is planned; this is what a later pass would pick up.

- **Split sections (item 4), deferred.** All 45 reader batches are answered (`work/round3/splits`). Clustering,
  staging, validation, the 30-pair audit and the install were not started. Split recall is unchanged (23.9%;
  "honest" keys 9/464 and 0 opposite).
- **Bench bulk pass (item 5), deferred.** Features for 2.43M decisions are complete (`work/round3/bench`). The rule
  step is not written; 302,839 rows would pass the stricter rule. It changes the bench label that the panel
  finding reads, so it needs its own 40-row audit and a full run.
- **Reader queue.** 246 packs unread; `install.py` re-adds audit-removed rows.
- **Circuit-parent epochs (item 8), dropped.** The round-3 trial (112 status rows, 497 findings) was not classified.
- **Landmark pairs (item 9), dropped as a separate item.** *Brown*/*Plessy* is covered as an implicit row by
  item 1; other pairs in CRS 2016 only were not attempted.
- **Not audited:** the 37 gold-directed rows of round 3, the 165 queue rows installed at the round-3 resume, the
  rise in atRisk.
- 36 admitted rows label a disavowal of dicta `overruled` (round 3); 24 date errors among the 35 epoch exceptions.

## Report check (23:45)

`work/round4/check_report.py` (Playwright, 1440 and 390 px wide): no horizontal page overflow, no page error, no broken image, no "failed to render" box; section 14 shows the table across rounds (12 rows), "Remaining and deferred" and the film; the two `why_recall` headings are in the evaluation section and in the contents. The film loads in installed Chrome (100 s); the bundled test Chromium has no H.264 decoder. 3 pending boxes remain, all blind audits C/D/E of the first plan that were never run.
