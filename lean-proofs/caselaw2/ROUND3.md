# caselaw-lean-2: round 3 (12 Nov 2026, 22:39–22:55, resumed 23:00)

The first round-3 coordinator and all of its agents were cut off by a usage limit at about 22:55, 25 minutes in.
This file is written by the resumed coordinator and is updated as each item lands. All model reading and auditing
was done by Claude subagents. No Azure or other external model was called. Nothing was committed to git. After
the resume the user chose the faster scope: items 2, 5, 6 and 7 are deferred with their partial files kept.
Logs: `round3/*.md`. Work files: `work/round3/<item>/`.

## State at the resume (23:00)

| Item | State found | Decision |
|---|---|---|
| Build | `lake build LegalProofs.CaseLaw2` + Run + native runner: green as found (the pending fix "bind the force first" was already in `Run.lean` of 22:50; the mirror's last build at 22:51 was green). Rebuilt at 23:02: green. No revert. | keep |
| Data files | No `.tmp` / `.part`, no stale lock. All live TSVs end in a newline with a constant column count. | keep |
| 1 splitter | Splitter and scan done; gold packs partly read; nothing installed | finish |
| 2 queue | Packs built; part read, part installed (rows already in live `treatments.tsv`) | deferred; installed rows stay |
| 3 SCDB audit | Done and installed at 22:47 (`round3/scdbaudit.md`) | done |
| 4 sweep class | Lean and reference changed and verified at 22:52; docs missing | docs written |
| 5 implicit | Format fixed; all 23 packs read; nothing installed; no checker support | deferred |
| 6 splits | 45 reader batches built; none read; nothing installed | deferred |
| 7 bench | Scan and features done; no rule step; nothing installed | deferred |
| 8 epochs | Deltas, three reference runs and blind answers done; nothing installed | finish |
| 9 artefacts | Driver `report/refresh_all.sh` written and dry-run at 22:55 | run at the end |

## Final integration (run once, 23:02–23:13)

| Check | Result |
|---|---|
| `lake build` + native runner (WSL, Lean 4.35.0) | green |
| `audit.py check` | 137 theorems (137 before), 4 with no axioms, 0 statement changes, 0 problems; no sorry, axiom or native_decide |
| Mutation matrix | 26 × 26, unchanged |
| Regression set, 114 universes (`r3_regress2`) | 0 disagreements |
| Sweep, seeds 62000–62499, 500 universes, all layers (`r3_drt2`) | 3 universes disagree, all conflict rows: 10 of 4,668 keys (round 2: 8 universes, 17 of 4,977). Status 0/75,045, findings 0/34,862, certs 0/89,479, splits 0/11,053, per-line rows 0/7,149, Horty 0/1,396 |
| Real data, fresh snapshot of 23:09 (`real19`), Lean and reference side by side | **0 disagreements**: status 0/398,334, findings 0/168,153, certs 0/350,307, splits 0/360, conflicts 0/92, per-line rows 0/309, Horty 0/44 |
| `score.py` → `eval/score_final.txt` | done; round 2 kept as `eval/score_round2.txt`, `eval/results_round2.json` |
| Figure, heatmaps, report (`report/refresh_all.sh`) | done; `~/Documents/html-reports/caselaw-lean-2.html` |

## Before and after (Lean output, `score.py`; "before" = round 2 final)

| Measure | Before | After |
|---|---|---|
| Treatment rows / admitted | 32,458 / 23,015 | 35,021 / 24,966 |
| Hunt's 42 literature overrulings: negative from the right date | 25 | 29 |
| Hunt's 42: negative by another decision / partly negative / atRisk only / still good | 2 / 4 / 2 / 11 (round 2 reported 4 / 2 / 11 without the first) | 2 / 6 / 2 / 3 |
| CRS current table | 126/292 = 43.2% | 162/292 = 55.5% |
| CRS 2016, express | 108/243 = 44.4% | 135/243 = 55.6% |
| CRS 2016, all | 112/311 = 36.0% | 139/311 = 44.7% |
| SCDB recall | 113/278 = 40.6% | 141/278 = 50.7% |
| SCDB precision | 113/125 = 90.4% | 141/152 = 92.8% |
| Later-court notes naming an overruling: agreement | 6,594/25,485 = 25.9% | 7,143/25,485 = 28.0% |
| Admitted `overruled` rows confirmed, among noted | 82.1% | 81.6% |
| Certificates: treatments ok / noAuthority / noCue | 31,008 / 1,394 / 12 | 33,118 / 1,816 / 41 |
| Split recall, section level (Lean as-of) | 164/714 = 23.0% | 171/714 = 23.9% (no split work installed; a side effect of new overrulings) |
| Split rows as of today / conflicts | 460 / 101 | 452 / 92 |
| Findings: atRisk | 65,533 | 85,827 |
| Findings: citesOverruled | 46,857 | 50,600 |
| Findings: panelDepartsWithoutEnBanc | 664 | 998 |
| `courts2.tsv` rows / cluster epoch rows | 3,106 / 88 | 3,025 / 0 |
| Sweep residue (500 universes) | 8 universes, 17 conflict keys | 3 universes, 10 conflict keys |
| Real-data residue | 0 | 0 |
| Theorems / mutants | 137 / 26 × 26 | 137 / 26 × 26 |
| Figure: v2 declarations / theorems drawn / modules | 895 / 138 / 21 (stale, before `Spec/Lines`) | 955 / 161 / 22 |
| Heatmaps: bad-law citations 1990–2019 / precedent-broken events | 44,618 / 12,178 (stale) | 49,444 / 12,594 |

- The first row of the Hunt line differs from ROUND2.md by 2: `known.py` counts 2 targets negative from a decision
  other than the listed overruler (*Grady*, *Apodaca*) in both rounds.
- Most of the recall gain comes from the reader queue rows that were installed before the cut-off (2,527 rows) and
  from the 37 gold-directed rows of item 1. The gold-directed rows were picked using the gold list of pairs, so the
  CRS and SCDB recall figures are no longer a held-out measure for those 37 rows.
- `panelDepartsWithoutEnBanc` rose by 334 and `atRisk` by 20,294 with the new rows. Neither was audited.
- 29 new rows fail the Lean certificate with `noCue` although `certify2.py` passed them. They assert nothing; the
  two cue lists differ and were not reconciled.

## Items

### 1. Hard-wrap splitter and the gold-pair re-read (installed 23:08; `round3/splitter.md`)

- The splitter for hard-wrapped slip opinions and a rescan of 21 repos were finished before the cut-off. At the
  resume, 5 subagents re-read the 5 gold packs (150 items from 183 gold decisions, 245 pairs) and a sixth read 4
  more *Loper Bright* items. A heading rule that took "The dissent ends by quoting…" as the start of a dissent was
  fixed (`reader/common.py`).
- Installed: 37 certified rows, reader `claude-subagent:gold-directed`. No blind audit (two packs are prepared).

| Target | Before | After |
|---|---|---|
| *Roe*, *Casey* (Dobbs) | good | overruled from 24 Jun 2022 |
| *Quill* (Wayfair) | good | overruled from 21 Jun 2018 |
| *Chevron* (Loper Bright) | good | overruled from 28 Jun 2024 |
| *Logan Valley* (Hudgens) | good | overruled from 3 Mar 1976 |
| *Halper* (Hudson) | good | partly negative from 10 Dec 1997 |
| *Swift* (Erie) | good | negative (`disapproved`) from 25 Apr 1938; Erie has no "overruled" sentence |
| *Lochner* | atRisk only | atRisk only: *Skrupa*'s one sentence is a report about *Adkins* |
| *Wolf* | good | good: *Mapp*'s candidate sentences report counsel's argument |
| *Ohio v. Roberts* | good | good: *Crawford* has no candidate sentence |
| *Plessy* | good | good: not attempted (the pair is not in the CRS current table) |

- *Wolf*, *Roberts* and *Lochner* need the implicit tier keyed on the overruling decision (item 5).

### 3. The 12 Supreme Court overrulings SCDB does not flag (done 22:47; `round3/scdbaudit.md`)

Twelve subagents, one per decision, read the full opinion blind.

| | Decisions | Rows |
|---|---|---|
| Row correct, SCDB does not flag it (kept) | 9 | 14 |
| Kept, scope corrected `all` → `partialUnknown` (*Ex parte Flippin*; *Atherton v. FDIC*) | 2 | 2 |
| Removed: a report of earlier decisions (*Aberdeen & Rockfish v. SCRAP* on *Griffin*) | 1 | 1 |

- The other 11 are real acts of the Court that SCDB does not code: 6 disavow or recede from dicta, 3 are partial
  "insofar as / to the extent" overrulings, 1 is supersession by a rule of evidence, 1 a conditional disapproval of
  1876. The remaining gap is one of definition (DEVIATIONS 81).
- Not done: 36 admitted rows label a disavowal of dicta `overruled`; `disapproved` fits but its cue list lacks
  "disavow". Counted, not changed.

### 4. The open sweep class: conflict rows at an adopter of a ceased court (code done 22:50; docs 23:10)

- Root, on both sides: the displacement test among conflict candidates read the force on the deciding court on asOf;
  a ceased court has no epoch then, so nothing displaced its decisions. Both engines now ask a ceased deciding court
  as it last sat (DEVIATIONS 80; `Exec.lastEpoch`, `Exec.forceOnAs`; reference R3-80). DIFFTEST.md §10.
- No theorem added, no statement changed.

| | Before (`drt9`) | After |
|---|---|---|
| The 8 disagreeing universes of `drt9` | 17 conflict keys | 0 (`r3_fail8`) |
| Sweep of 240 (seeds 61000-61239) | | 0 disagreements |
| Sweep of 500 | 8 universes, 17/4,977 conflict keys | 3 universes, 10/4,668 conflict keys (`r3_drt2`, seeds 62000-62499) |

- The 3 remaining universes are a different shape (state issue `tx.a`, at the adopter court; a candidate's deciding
  court has no epoch on asOf and none before). Open, not triaged.

### 8. Decisions dated after their court's end (installed 23:05; `round3/epochs.md`)

| | Before | After |
|---|---|---|
| Stray decisions re-routed (court column of `decisions2.tsv`) | 0 | 804 of 839 |
| Cluster epoch rows in `courts2.tsv` | 88 (47 courts) | 0 |
| `courts2.tsv` rows | 3,106 | 3,025 |
| Ended courts with an epoch after their end | 47 | 5 (the 35 exceptions, 7 rows) |
| Decisions dated outside their court's epoch | 0 | 0 |

- Court of Claims → Claims Court 486; Hawaii ICA → Supreme Court 88; "Kansas Court of Appeals" → Kansas City Court
  of Appeals 79; US circuit courts → the district court 80; Alabama 21; New Jersey Chancery 17; others 33.
- Blind review: 30/30 name the delta's court (Wilson 89–100%); strictly 29/30. 22 of the 30 were Claims Court rows.
- Effect on the reference run, every row explained: 16 new status rows (three Hawaii decisions overruled by a 2019
  Hawaii Supreme Court decision the corpus had labelled as the intermediate court), 19 findings gone, 28 new.
- Not installed: the circuit-parent epochs (Eleventh Circuit districts under the Fifth before 1981, Tenth under the
  Eighth before 1929). The trial run changes 112 status rows and 497 findings and was not classified.

### Deferred to the next round (partial files kept)

- **2. Reader queue** (`round3/queue.md`). 398 packs, 31,803 items. 141 packs (11,280 items) were read and
  installed: 2,528 treatment rows (2,363 before the cut-off, 165 at the resume), less one row removed after the
  audit. 11 more packs are answered but not certified; 246 packs (about 19,600 items) are unread. Blind audit of 30
  installed rows: own act 29/30 (83–99%), target 30/30 (89–100%), kind 20/30 (49–81%): 9 rows say `overruled` where
  the auditor says `disapproved`. The row the audit found wrong was removed (`t:6865583:6852906:48056`).
- **5. Implicit tier** (`round3/implicit.md`). All 23 packs (978 items) read. 189 candidate rows, 185 pass the
  work-folder verifier; 171 need the witness format (`round3/implicit_schema.md`), which neither checker
  implements; 18 are in the old format. Nothing installed; live data keeps the 21 round-2 rows.
- **6. Split sections** (`round3/splits.md`). All 45 reader batches now have answer files. No clustering, staging,
  validation, audit or install. `score.py` gained `honest_*` keys (additive).
- **7. Bench bulk pass** (`round3/bench.md`). 2,433,434 decisions re-read, features complete. No rule step, no
  delta, nothing installed. 338,428 rows would pass the round-2 size rule (302,839 a stricter one).

## What remains

- The three sweep universes (62003, 62350, 62391): conflict rows only in the reference at an adopter court on a
  state issue. Not triaged.
- Blind audits not run: the 37 gold-directed rows, the 165 queue rows installed at the resume. The queue audit's
  kind agreement is 20/30: about a third of the new `overruled` rows may be `disapproved` (both change status).
- The witness checker for implicit rows (Lean `Certificate.lean`, the reference, the generator); then 171 rows.
- Queue: 11 answered packs to certify, 246 unread. Splits: cluster, validate, audit, install. Bench: the rule step.
- Epochs: the circuit-parent epochs; 24 date errors among the 35 exceptions; `data/COURTS.md` rule 7 is out of
  date (replacement text in `round3/epochs.md`); `epochs_fix.py` would recreate the cluster rows if re-run.
- `report/heatmaps/HEATMAPS.md` is hand-written and still shows the old totals.
- `Exec.lastEpoch` and `Exec.forceOnAs` have no theorem.
