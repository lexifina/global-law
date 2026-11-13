# Round 2, agent `splits`: resolution links and split recall

Written 2026-11-12. Time-boxed by the coordinator; one audit round.
Private copy: `work/round2/splits/` (`data/` = the installed state, `out0` baseline run, `out3` final run).
Scripts: `tools/caselaw2/holdings/round2/` (copies of `work/round2/splits/tools/`).
All model reading was done by Claude subagents. No external model was called. Gold was read only by `diagnose.py`,
`gain.py` and the scorer.

## Numbers (reference engine + the split block of score.py, private copy)

| measure | before | after |
|---|---|---|
| gold statutory splits found, section level | 135/714 = 18.9% | 255/714 = 35.7% |
| – section only | 111 | 215 |
| – section + circuits | 19 | 23 |
| – subsection + circuits | 5 | 17 |
| missed | 579 | 459 |
| node level (a split question holding a gold conflict decision, split before the resolution) | 25/464 = 5.4% | 28/464 = 6.0% |
| `splits_detected_on_or_after_resolution` | 655 | 673 |
| split rows, ever (`splits.tsv`) | 393 | 491 |
| split rows as of 2026-11-12 (`splits_asof.tsv`) | 332 | 362 |
| conflict rows as of 2026-11-12 | 107 | 101 |
| split questions with a split row, ever | 190 | 301 |

- The published 15.3% / 485 / 436 in `eval/score_final.txt` come from Lean's `out/splits.tsv`, which holds only the
  rows that exist on the asOf date. The reference's `splits.tsv` holds every split with its first date, so its
  baseline is 18.9% / 655 / 393. Before and after above use the reference file.
- **Read the section-level gain with care.** 120 more gold rows are found, but 31 of them are on 42 U.S.C. § 1983 and
  34 more on 21:841, 28:1291, 28:1331 and 28:1332: one new split on a much-litigated section matches every gold row on
  it. The node-level measure moves by 3 rows. The new splits are real (audit below) but are mostly not the gold's
  splits.
- `splits_detected_on_or_after_resolution` is also a section-level count (any split on the section dated after any
  gold decision on it). It went up because 98 new split rows were added. It does not measure staleness.
- **Staleness, measured directly:** of the 332 baseline as-of split rows, **60 rows (26 questions) are now resolved**;
  19 baseline split rows no longer arise at all (the Supreme Court holding predates the second side); 6 conflict
  rows are removed. Of the 116 as-of rows of the new questions, 26 are resolved by the second linking pass.
- **Warning for the Lean-format score.** Lean's `out/splits.tsv` is the as-of table. A resolved split leaves it, so
  linking resolutions lowers "recall of resolved splits" measured on that file. Score recall on a first-date table.

## Task 1: miss classes (`round2/splits_misses.tsv`, written from the final run)

Missed gold rows, before → after:

| class | before | after |
|---|---|---|
| A1 section not read for splits; no circuit holdings name the section | 315 | 251 |
| A2 section not read; only decision-local circuit holdings (no question, answer `-`) | 58 | 42 |
| A3 section read, no court-of-appeals split holding before the resolution date | 18 | 14 |
| B only one circuit extracted on the section before resolution | 5 | 7 |
| C holdings of ≥ 2 circuits, no shared issue key (not clustered) | 61 | 50 |
| D shared issue key, answers not opposite as coded | 121 | 94 |
| E opposite answers on a shared key, no engine row | 1 | 1 |
| total | 579 | 459 |

- "Circuits' decisions not in corpus" was not found as a class: gold `conflict_nodes` are graph nodes by construction.
- Rows counted in `splits_detected_on_or_after_resolution` (gold row × later split row on the section), before → after:
  R1 resolving decision has no holdings row 3 → 3; R2 it has split holdings on the section under other keys
  281 → 307; R3 it has only decision-local holdings (answer `-`) 371 → 363. No row is "same key, wrong date".

## Task 2: Supreme Court holdings linked to split questions

- **Questions:** every issue in the reference's `splits.tsv`, `splits_asof.tsv`, `conflicts_asof.tsv` (240 at
  baseline; 115 new ones in the second pass).
- **Candidates (`res_candidates2.py`), no gold:** Supreme Court opinions dated after the earliest side holding that
  cite the question's US Code section (`usc/cites/supreme-court.usc.tsv`) or cite a side decision (citation edges).
  4,265 pairs (pass 1), 2,291 (pass 2).
  - The brief's narrower rule (cites each side, or one side and the section) gives 47 pairs and misses both named
    examples: *Niz-Chavez* has no citation edges and *Burlington Northern* cites other circuit decisions.
  - US Code cites start in 1995. Earlier Supreme Court decisions are reached only through citation edges.
- **Cut (`res_screen_prep.py`, `res_stage1_build.py`):** IDF word overlap between the question and the Supreme Court
  decision's recorded holdings ≥ 0.2, or both sides cited, or one side cited and overlap ≥ 0.1. 543 + 226 pairs.
  Supreme Court decisions with no recorded holdings (350 + 99 pairs) are not scored and are left out unless they cite
  a side.
- **Stage 1 (Claude subagents, 8 batches):** screen on recorded holdings: 64 + 40 pairs kept (yes/maybe).
- **Stage 2 (Claude subagents, 13 batches):** the opinion of the Court is read from git, cut into sentences with
  offsets (`core.split_sentences`); the reader sees about 45 numbered sentences and returns decides yes/partly/no,
  the answer, and a sentence id. The reader never types a quote. 37 + 26 "yes".
- **Syllabus fix (`syl.py`).** CourtListener slip opinions carry the syllabus inside the "Combined" section, and
  `core.court_parts` cut four of them at the syllabus's "filed a dissenting opinion" line. Six picks were syllabus
  sentences. `syl.court_parts2` starts the part at "JUSTICE X delivered the opinion of the Court"; the six were
  re-read. The existing gpt rows for 2015+ Supreme Court texts may have the same fault (not checked).
- **Rows:** 62 holdings under the split question's existing issue key, role `majority` (59) or `perCuriam` (3),
  reader `claude-subagent`, ids `S<node>.<usc>.r[n]`. 36 are on baseline questions, 26 on the new questions.
  Plurality decisions (decisions2 form) are skipped: none arose.
- **Named examples.** *Burlington Northern v. White* (2006) answers `usc:42:2000e-3(a):q2` yes: the Wideman/Burger
  row is gone from the as-of table. *Niz-Chavez* (2021) answers `usc:8:1229(a):q4` yes (also `q0` and
  `usc:8:1229b(d):q18`): the Banuelos-Galviz/Garcia-Romo row is gone; 15 as-of rows in all.
- **List:** `round2/splits_resolved_links.tsv` (62 rows: issue, question, decision, answer, holding id, baseline rows
  resolved). 27 links resolve at least one baseline as-of row; the rest sit on splits that were already historical,
  on conflict rows, or on new questions.

## Task 3: detection recall (largest class: sections never read for splits)

- **Generator, no gold (`xc_pairs.py`, `xc_build.py`):** reader rows in `treatments.tsv` where a federal court of
  appeals declines to follow or disapproves a decision of another circuit: 720 pairs.
- **Cut:** by-date ≥ 1970, the quote is in the court's own part, and the disagreeing decision cites the US Code
  within ±3,000 characters of the quote: 327 pairs. 308 pairs with no US Code cite nearby were not read.
- **Reading (Claude subagents, 24 batches):** numbered sentences of both decisions; the reader returns the yes/no
  question, the US Code section, each court's answer and one sentence id per court. 118 accepted, 209 rejected
  (not statutory 55, not the same question 29, earlier holding not shown 18, earlier decision not contrary 17, …).
- **Rows:** 115 new questions `usc:<title>:<section>[(sub)]:x<n>` in `issues.tsv` (src `splits2:claude-subagent`) and
  233 holdings (ids `S<node>.<usc>.x<n>`). All 115 produce a split row in the reference; 90 rows are still open on
  the asOf date.
- **No issue key was renamed or merged. There is no `issue_key_alias.tsv`.** 33 new questions sit on a subsection
  that already has `q` questions; one is a likely duplicate (`usc:18:1546(a):x0` and `:q35`). Classes C and D
  (clustering, polarity) were not worked.

## Task 4: blind validation (one round)

Judges were separate Claude subagents. They saw the passage (±1,100–1,300 characters with the sentence marked) and
the claim. They did not see the reader, its confidence, or the key. Decoys were mixed in.

| set | result | Wilson 95% |
|---|---|---|
| Resolution links: decides the question and the answer is right (all 37 first-pass links) | 36/37 = 0.97 | 0.86–0.995 |
| – and the marked sentence states it | 36/37 = 0.97 | 0.86–0.995 |
| – decoys (answer flipped) rejected | 8/8 | 0.68–1.0 |
| New split questions: genuine split (42 of 118 pairs, stratified by confidence) | 42/42 = 1.00 | 0.92–1.0 |
| – confidence < 0.7 | 19/19 | 0.83–1.0 |
| – decoys (other pair's passage) rejected | 6/6 | 0.61–1.0 |

- Dropped: the *Tapia* link (judged not to decide the question as posed). No class failed.
- Limits. The judges are the same model family as the readers. The split decoys were easy (unrelated cases), so
  42/42 probably overstates. Five judged pairs are an en banc Eleventh Circuit overruling inherited Fifth Circuit
  precedent; they are opposite holdings, and the engine's adoption rule decides whether they are a split.
- **Not audited:** the 26 second-pass links (same reader and method as the audited 37).

## Installed (appended; `*.pre_round2.tsv` backups written)

| file | rows before | after |
|---|---|---|
| `data/holdings.tsv` | 260,054 | 260,349 (+295: 62 Supreme Court links, 233 split holdings) |
| `data/issues.tsv` | 255,981 | 256,096 (+115) |
| `data/holdings_cert_text.tsv` | 258,198 | 258,491 (+293 windows) |
| `data/window_sha.splits_round2.tsv` | new | 293 rows |

- `marks.tsv`, `holdings_reach.tsv`: unchanged.
- `check_certs.work` on the 264 decisions with first-pass rows: 537 rows, 0 failures. The reference admits all 295
  new rows (`certs.tsv`: ok) on the private copy.
- **Action for the coordinator: `window_sha.tsv`.** The reference and Lean reject a window with no hash row
  (`windowHash`). I do not own `data/window_sha.tsv`. Either rerun `tools/caselaw2/window_sha.py`, or append
  `data/window_sha.splits_round2.tsv` (same five columns) and sort. Without this the 295 rows are not admitted.

## Next round

1. Class A (293 misses): read more sections. A wider no-gold generator is the reader's candidate file
   (`reader_work/cand`, 2.6M sentences) filtered for court-of-appeals sentences naming another circuit ("we
   disagree with the Ninth Circuit", "circuits are divided") near a US Code cite; and the 308 unread pairs.
2. Class D (94) and C (50): second reading of polarity and a pairwise same-question pass on subsections with holdings
   of ≥ 2 circuits; merge through an alias file.
3. Audit the 26 second-pass links; add harder decoys (same section, different question).
4. Link Supreme Court decisions with no recorded holdings (449 candidate pairs skipped) and pre-1995 decisions
   through a US Code cite table that starts before 1995.
5. Apply `syl.court_parts2` in `core.court_parts` and re-read the 2015+ Supreme Court slip opinions.
6. Score split recall on a first-date table in Lean, not on the as-of table.

## Text for files I do not own

- DEVIATIONS (new item): "Round-2 split rows. 62 Supreme Court holdings were added under existing split-question
  keys and 115 questions (`:x<n>`) from cross-circuit declined-to-follow pairs, read by Claude subagents. Candidate
  generation uses US Code cites, citation edges and the reader's treatments; gold is not read. Section-level split
  recall is inflated by much-litigated sections; the node-level figure is 28/464."
