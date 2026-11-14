# round5/recog: candidates and tooling for "recognised overruling" rows (agent `recog`)

Contract: `../DESIGN5.md` sections 2 and 7. Nothing outside `round5/recog/` was written. No row is installed: the
lead spawns the readers, audits, and installs.

State (13 Nov, 12:25): DONE for this agent. Candidates, packs (119), brief, certifier, verifier, pattern tier
(4,685 rows staged and verified), claims for the 179 existing rows. `cert/` is empty until readers answer.
Added 12:40: tier T1f (section 3a), 2,347 items in 47 packs; cue-table change taken up.

## 1. Tier sizes

Source for T1, T2, T3: `round5/tests/split/feed_ids.tsv` only (89,542 statements), joined by statement id to
`gold/reports_typed.tsv` for the note's position, and W's text from git (`build_candidates.py`, `stats.json`).

| step | statements |
|---|---|
| feed, family precedent, named by-decision, kind overruled/abrogated/disapproved/recededFrom | 28,062 |
| W, X, Y in corpus and distinct; date(X) <= date(Y) <= date(W), none 0; **W has power over X** (`can_change(W, X)` = yes); Y not shown to lack power | 14,286 |
| note stands in an opinion-of-the-court part of W (`part_map2`) | 12,739 |
| one per (W, X, Y, scope group of the note) | 12,466 |
| 3 earliest W per (Y, X, scope group) = **candidates** | **10,567** |

| tier | candidates | (Y, X) pairs | note scope all / partial / other grounds | reader packs |
|---|---|---|---|---|
| T0 (the 179 round-4 witness rows, to re-read) | 179 | | | 4 |
| T1 (X = US Supreme Court, from the feed notes) | 52 | 43 | 36 / 6 / 10 | 2 |
| T1, pair already explicit-all-ok in the model | 14 | 9 | | |
| T1, pair not yet explicit | 38 | 34 | | |
| T1s (own scan of the Supreme Court's opinions, section 3) | 3,727 | 3,375 | | 76 |
| T1s, strict form | 528 (452 not explicit + 76 explicit) | 452 | | packs 001-012 |
| T1s, loose | 3,199 | | | packs 013-076 |
| T2 (other X, pair not explicit-all-ok) | 10,004 | 6,760 | 1,213 / 594 / 8,197 | 37 (the 1,807 all + partial) |
| T2p (the 8,197 T2 other-grounds notes, by pattern, section 4) | 4,685 rows staged | 4,685 | | none |
| T3 (other X, pair already explicit-all-ok) | 511 | 380 | 132 / 23 / 356 | none |

Packs: 119 files, 5,765 items (`packs/summary.json`, `packs/index.tsv`).

The largest drop is power: 12,715 statements are by a panel under a strong horizontal rule
(`F7.panelCannotOverrulePanel`), 678 Florida sister-district, 145 trial courts, 46 unknown bench. Of the 179 T0
rows, those whose W is such a panel can never be recognised (the certifier answers `w-no-power`).

Deviation from the task text, on purpose: the reduction keeps the 3 earliest W per (Y, X) **and scope group of the
note**, because four notes in five are "overruled on other grounds by" and the earliest plain "overruled by"
statement is the one that fixes the negative date.

## 2. Files

| file | what |
|---|---|
| `recog_common.py` | paths, streaming lookups, git text, the recognised text checks (DESIGN5 2.2), evidence choice |
| `build_candidates.py` | feed -> `candidates.tsv`, `items.jsonl.gz` (T0, T1, T2, T3), `stats.json` (2.5 min) |
| `scan_scotus.py` | Supreme Court scan -> `candidates_t1s.tsv`, `items_t1s.jsonl.gz`, `stats_t1s.json` (10 min) |
| `build_packs.py` | -> `packs/pack_<tier>_<nnn>.md`, `packs/index.tsv`, `packs/summary.json`. DO NOT re-run while readers work: it rewrites every pack except T1f |
| `build_t1f.py` | loose T1s items -> `packs/pack_T1f_<nnn>.md`, `packs/index_T1f.tsv`, `packs/T1f_dropped.tsv` (section 3a) |
| `READER_BRIEF_RECOG.md` | the reader brief (answers: `ans/ans_<pack name>.jsonl`) |
| `certify_recog.py` | answers -> deltas in `cert/` |
| `certify_pattern.py` | T2p: pattern answers (`pattern/ans/`) -> deltas in `cert_pattern/` (75 s) |
| `verify_recog.py` | mechanical re-check of a delta folder from the corpus -> `verify_failures.tsv` |
| `claims_existing.py`, `claims_existing.tsv` | a `recognised` claim line (5 columns) for each of the 179 live witness rows |
| `test/` | hand-made answers (`test/ans`), their deltas (`test/cert`), a tampered copy (`test/cert_bad`) |
| `packs_unused/` | the other-grounds packs of the first build (not for readers; no INTRO field) |

An item (one JSON line): ids, tier, W / X / Y (node, name, citations, date, court), W's `sha`, the note offset,
the part (and the part boundaries around it), `text` = W's text from `s0` (the shown window `d0..d1` is the note
+-700 characters; 450 more are stored on each side for the certificate window), `intro` / `para` (start of the
paragraph), the note's kind and scope (hints only), `w_power`, `pair_explicit`.

## 3. T1s: scan of the Supreme Court's own opinions (`scan_scotus.py`)

Corpus text only (no notes table, no gold list). 384,140 Supreme Court texts (opinions and orders) read at HEAD;
9,237 overruling words (overrul-, abrogat-, disapprov-, reced- from) stand in an opinion-of-the-court part of an
opinion that cites two or more Supreme Court decisions; 2,540 of them have two such decisions mentioned within a
400-character span (by citation, or by a caption word of a decision the opinion cites elsewhere). Pairs among the
three nearest mentions, X = the older, Y = the newer: 3,899 (W, X, Y) triples, 3,395 pairs; 3 earliest W per pair
(plus the earliest strict-form W); 36 triples already in T1 left out: **3,727 candidates, 3,375 pairs**.

- strict form (528): "X ... overruled [in part ...] by|in Y", "Y (overruling X)" / "Y, overruling X",
  "overruled X in Y", "Y overruled X". These are the likely statements. 76 of them are pairs already explicit.
- loose (3,199): two decisions near an overruling word in any other order. Mostly not statements (W's own act, a
  third case, a demurrer); they are packed last so reading can stop at pack 012.
- "X did not survive Y" is NOT scanned: the cue list `recognised` has no such phrase, the row could not pass.
- 78 candidates are of pairs that already have a round-4 witness row.

### 3a. T1f: the loose T1s items, cut to those that can be certified (`build_t1f.py`, 12:40)

Input: the 3,199 loose items minus the 200 of the sample packs 013, 029, 045, 061 = 2,999. Existing packs,
`packs/index.tsv` and `ans/` are not touched.

| test | passes | dropped |
|---|---|---|
| 1. one span of <= 400 characters of the window holds a cue, an evidence for X and one for Y (the certifier's own functions) | 2,997 | 2 (X or Y not named in the window) |
| 2. for some choice of occurrences, the SMALLEST span covering the cue, X and Y has no `disqualify_recognised` phrase and lies in one opinion-of-the-court part | **2,347** | 650 (641 a disqualifier in every such span, 9 crosses parts) |

Test 1 alone is what was asked for; it drops almost nothing because `scan_scotus.py` built its candidates under
the same condition. Test 2 is the rest of the same precondition: every certifiable quote contains the smallest
span, so an item that fails it cannot be certified whatever the reader answers (`--three-only` switches it off).

**T1f = 2,347 items in 47 packs** (`packs/pack_T1f_001..047.md`, same item format and ids, so `certify_recog.py`
takes the answers unchanged; `packs/index_T1f.tsv`; `packs/T1f_dropped.tsv` lists the 652 dropped ids with the
reason; `packs/summary_T1f.json`). Order: as in the T1s packs (by X's date). Ordering by the length of the shortest
span was tried and dropped: the shortest spans are "asks us to overrule X and Y", not statements. No ranking of the
kept items is claimed; the share of statements should be near the sample's (about 3%), a little higher.

Plessy / Brown among the loose items: `s01500` (W = Dobbs, 2022) is kept (pack_T1f_012); `s01499` (W = Patterson v.
McLean Credit Union, 1989) is dropped, rightly: its only overruling word is "We decline to overrule". (The 1970
statement of Plessy / Brown is the T1 item `r174714`.)

Cue table change of 12:35 (lead): `recognised` / `self_announced` now hold " reced"; the recognised disqualifiers
hold argues / argued / arguing / argument and urges / urged / urging instead of argu / urge. The certifier, the
verifier and `build_t1f.py` read the lists from `tools/caselaw2/reader/cue_table.py` at run time (no copy); the
brief quotes the new list. `cert_pattern/` was built under the old lists: every row still passes (the new
disqualifiers are a subset, and no T2p row is a "receded" row); a re-run of `certify_pattern.py` would admit a few
of the 99 quotes that the old `argu` / `urge` substrings refused.

## 4. T2p: other-grounds notes certified by pattern (`certify_pattern.py`, `cert_pattern/`)

Strict citator form at the note's own position: X's citation (the last one before the phrase, resolving to X),
then at most 250 characters with no other decision (no citation of another node, no " v. ", no history word, no
semicolon or sentence end outside parentheses), then "overruled | abrogated | disapproved [of] [in part] on other |
another | different ground[s] by | in", then within 200 characters Y's citation (the first one, no ";" before
it). Quote = from X's citation to Y's citation, at most 400 characters. Each match then passes through
`certify_recog.py --cite-only` (same cue, disqualifier, part, quotation, date and in-quote resolution checks).

| step | n |
|---|---|
| T2 items with an other-grounds note | 8,197 |
| strict pattern matched | 6,788 (no strict phrase 1,050; X's citation too far 108; another decision between 101; sentence/semicolon 91; ";" before Y 39; history word 17; other 3) |
| admitted by the certifier | 6,671 (refused: 99 disqualifier word in the quote, 18 inside a quotation) |
| **rows staged** (earliest W per pair) | **4,685** (overruled 2,962, disapproved 1,031, abrogated 692; all scope otherGrounds) |
| spare (later W of the same pair, `rows_spare.tsv`) | 1,986 |
| `cite_index_delta.tsv` | 7,037 keys |
| `verify_recog.py --cert cert_pattern` | 4,685 checked, **0 failing** (with the engine's power check) |

Rows: reader column `pattern-r5`, witness and class src `pattern:otherGrounds`, confidence 0.90.

## 5. How to run

    cd round5/recog
    python -X utf8 build_candidates.py          # only to rebuild; items.jsonl.gz is in place
    python -X utf8 scan_scotus.py               # only to rebuild; items_t1s.jsonl.gz is in place
    python -X utf8 build_packs.py
    # readers: brief READER_BRIEF_RECOG.md, one pack each, answers to ans/ans_<pack name>.jsonl
    python -X utf8 certify_recog.py --answers ans --out cert
    python -X utf8 verify_recog.py --cert cert
    python -X utf8 certify_pattern.py           # T2p -> cert_pattern/
    python -X utf8 verify_recog.py --cert cert_pattern

`certify_recog.py` options: `--tiers T0,T1,T1s,T2` (subset), `--skip-explicit` (leave out pairs that already have
an explicit scope-all ok row; they go to `rows_explicit_pairs.tsv`), `--all-witnesses` (stage every admitted W, not
only the earliest per pair and the earliest scope-all one), `--allow-quoted`, `--reader`, `--src`, `--cite-only`.

Delta files (same set in `cert/` and `cert_pattern/`): `treatments_delta.tsv` (16 columns, ids
`tw:<Y>:<X>:<start>:<W>`), `treatment_witness_delta.tsv`, `treatment_class_delta.tsv` (5 columns, claim
`recognised`), `treatments_items_delta.tsv`, `cert_text_delta.tsv`, `window_sha_delta.tsv`,
`cite_index_delta.tsv`, `remove_ids.txt`; reports: `rows_info.tsv`, `rows_spare.tsv`, `rows_explicit_pairs.tsv`,
`t0_map.tsv`, `live_same_triple.tsv`, `rejects.tsv`, `stats.json`, `verify_failures.tsv`, `verify_summary.json`.

Install order (lead): remove the ids of `remove_ids.txt` from `data/treatments.tsv` and
`data/treatment_witness.tsv`; append the deltas; `treatment_class.tsv` = class deltas (+ `claims_existing.tsv` if
wanted; a class line for an id that a T0 re-reading replaced is already in the delta). When both `cert/` and
`cert_pattern/` are installed, concatenate the two `cite_index_delta.tsv` without duplicates and run
`verify_recog.py` once more on each folder after the first is installed (each delta is computed against the live
index only; a key naming two nodes would resolve to nothing). Then `round5/tests/check_no_leak.py` (not run by me:
it reads the holdout).

## 6. What the certifier and the verifier enforce

Certifier (refusals in `rejects.tsv`): quote found in the item's window (exact; whitespace runs and quote-mark
styles tolerated; the window's own text is certified); at most 400 characters; a cue of the list `recognised` at a
word start; no phrase of `disqualify_recognised`; inside one opinion-of-the-court part; not inside a quotation;
date(X) <= date(Y) <= date(W), none 0; W's power = yes; X and Y both resolve INSIDE the quote (`cite:` through
`data/cite_index.tsv`, or uniquely through `graph/cite_index.tsv` with a delta row; else `name:` caption words
that stand capitalised in the quote and are not words of the other caption); the two evidences differ. Scope: the
reader's, only ever made narrower ("other grounds" in the quote; "in part / to the extent / insofar"; a field
limit or doctrine label; a list introduction saying "in whole or in part").

Verifier (independent of items and answers; reads the deltas, the live tables and git HEAD): row shape and id;
W's bytes hash to the row's sha and to decisions2; quote equals the text at the offsets; a covering window that
equals the corpus cut with a matching hash; cue; no disqualifier; both evidences resolve in the quote through the
index as it will be after install; evidences differ; dates; part recomputed with `part_map2`; the reference's
`can_change(W, X)` = yes and `can_change(Y, X)` != no; provenance (a feed pair, a round-4 witness triple, or a
T1s candidate). Test: `test/cert` 9 rows, 0 failing; `test/cert_bad` (6 tampered fields) 6 rows failing, each
change caught.

Hand test (15 + 2 answers): 9 admitted (5 T1 incl. Plessy/Brown with doctrine label -> partialUnknown, 3 T2, 1
T1s by name evidence `name:Malloy`); refusals as intended: negation, quote not in window, X not in quote, Y not in
quote, `dissent` in the quote, the two T0 rows whose W is a Fifth Circuit panel (`w-no-power`), unknown id.
Two of the T1 answers are already live witness rows that pass as they are (`live-identical`), one more passes with
its live quote (`live-kept`): they get a class line only.

## 7. Problems and things to decide

1. Cue table: fixed by the lead at 12:35 for `reced` (now " reced") and `argu` / `urge` (now whole word forms).
   Still substrings of ordinary words: `question`, `refus`, `declin`, `dissent`, `contend`, `doubt` ("the question
   presented", "(Holmes, J., dissenting)"); readers are told to cut around them.
2. A quote must hold both names: statements whose X or Y is named only by "supra" / "that case", or with a long
   parenthetical between X's citation and the overruling word, are lost (`notInOneSpan`).
3. T1 from the feed is thin (52) because the Supreme Court seldom writes in citator form; T1s is the real source.
4. The feed scope column was used to split T2; it is a hint. The readers set the scope of every T2 row.
5. `name:` evidence is weaker than `cite:` (a caption word); rows_info.tsv lists the by-evidence, and the target
   evidence is in the row, so name-only rows can be audited separately.
6. Leak note: when first looking at the format of `gold/reports_typed.tsv` I printed its header and first two
   rows (ids 1 and 2, which are not feed ids). They were not used for anything; every later read of that file goes
   through `recog_common.typed_rows`, which skips non-feed rows on their id.
7. No commit, no install, no edit of `data/`, the Lean tree or the tools folder.
