# b3: two date views for the scorers (DESIGN7 section 6, B3)

Agent b3, round 7. Scoring code only. Started 22:45 (Fri 13 Nov 2026, `date`); finished 22:59.
Wrote: `round7/score_fresh7.py` and this folder. Nothing else changed (a `__pycache__` my first import left in
`round5/gold_fresh/` at 22:50 was removed at 22:58; the scorer now imports with `dont_write_bytecode`).
Never opened `round5/gold_fresh/sealed/`, never ran `--split test` on the real key.

## 1. What `round7/score_fresh7.py` does

Same arguments as `round5/gold_fresh/score_fresh.py` (imported, not edited) plus `--view model|attributed|both`
(default both), `--data DIR` (decisions2.tsv), `--out DIR` (dev only), `--write-status PATH`.

- **model view**: the R5-3 timeline, exactly score_fresh.py (same code path on the same rows, file order kept).
- **attributed view** ("as attributed today"): per group (node, issue, holding, actor Y) of path-`recognised` rows
  that has a `neg:overruled` / `neg:abrogated` row N (the earliest): every `unknown:recognisedLater` row of the
  group ending before N is read with N's status; the earliest of those rows and N then starts at date(Y)
  (decisions2.tsv of the variant's data folder) if it started later. Everything else unchanged.
  The group key leaves out the witness row on purpose: when several later courts W1, W2 recognise the same
  overruling, the status row names whichever effect is in force, so the `unknown:recognisedLater` row can come
  from W1's row and the negative row from W2's row (seen on final2, e.g. node 5943866). A first version keyed on the
  witness row too; it gave the same fresh numbers but redated 15 rows instead of 4.
- Outputs: `<out>/fresh7_dev.json` (both views' recall tables + precision side, attribution counts, moves),
  `fresh7_dev.<view>.pairs.tsv`, `fresh7_dev.<view>.unlisted_sample.tsv`, `fresh7_dev.moves.tsv` (dev only: the
  pairs whose outcome differs). Stdout: each view's table (as score_fresh.py), a side-by-side table (strict and
  lenient, k, rate, Wilson 95%, both views), the move counts and the attribution counts.
- `--split test`: results go to `round5/gold_fresh/sealed/results/<label>.fresh7.*` (no moves list), and ONE line per
  run is appended to `sealed/TEST_RUNS.log` (score_fresh.py's 5 fields + `scorer=round7/score_fresh7.py view=...`),
  for both views together. `--out` is refused on test.
- `--write-status P` writes the attributed reading of the whole status.tsv (same columns, same row order) for
  scorers that read status on a date (the holdout notes scorer, section 3).

## 2. Proof on the round-6 frozen build (final2, dev split)

Inputs: `--status round6/history/out/final2/status.tsv --treatments round6/history/stage/final2/treatments.tsv`
(decisions2.tsv from `round6/history/stage/final2/`).

Reference: score_fresh.py itself, copied to `check/score_fresh_r5_copy.py` with only two lines changed (HERE pinned
to the real gold_fresh folder; results folder = `ref_r5/`, dev asserted) so that nothing is written into round5;
`diff` shows just those two lines. `check/compare_model_view.py ref_r5 final2 results/final2`:
recall tables identical, precision side identical, inputs identical, `.pairs.tsv` and `.unlisted_sample.tsv`
byte-identical. **ALL IDENTICAL.** (Also identical with `--view model` alone.)

| final2, dev (165 pairs) | a | a_date | a_kind | b | c | d | e | strict | lenient |
|---|---|---|---|---|---|---|---|---|---|
| model view (= score_fresh.py) | 50 | 30 | 0 | 5 | 23 | 0 | 57 | 50/165 = 30.3% [23.8, 37.7] | 108/165 = 65.5% [57.9, 72.3] |
| attributed view | 80 | 0 | 0 | 5 | 23 | 0 | 57 | 80/165 = 48.5% [41.0, 56.1] | 108/165 = 65.5% [57.9, 72.3] |

Moves: `a_date -> a` 30, nothing else (list: `results/final2/fresh7_dev.moves.tsv`; every moved pair's new start
equals the overruling date in scotus_meta, e.g. Plessy: from 20220624 to 19540517). Lenient cannot move except
c -> a, which did not happen. Precision side identical in both views (80 listed, 12 unlisted, 1 other overruler of
93 in the dev half; 169 all halves).

Selected cells, strict model -> attributed: express 50 -> 78 /145; implied 0 -> 2 /20; partial 0 -> 2 /13;
not in CRS 1 -> 2 /19; era 1946-1991 16 -> 37 /78; payne_n1_1991 0 -> 12 /18; gerhardt 28 -> 49 /84;
wikipedia 31 -> 49 /80; blaustein 19 -> 27 /72. Full tables: `results_final2.txt`.

Attribution counts on final2 (whole status.tsv): 19,131 recognised rows in 9,227 groups; 1,582 groups with a
recognised negative (669 whole-decision, 913 issue); 1,787 `unknown:recognisedLater` rows read negative; 1,571
groups start at date(Y) through those rows; 7 had date(Y) = date(W); 4 rows (2 nodes) had no recognisedLater row
before the negative, because another actor's negative held the interval, and were moved to date(Y) (overlapping that
row; a reading, not a status); 0 negative rows start on a day other than date(W) or the day after; 0 actors without a
date. 50 groups have `unknown:recognisedLater` but no negative row of their own (31: another actor's explicit
overruling arrives before W; 10: Y lapses, status good; 6: another recognised actor; 3: X vacated) and stay unchanged,
as the brief says; none is a gold pair of the dev key.

## 3. Held-out notes scorer (`round5/tests/score_holdout.py`)

Date-sensitive: it reads X's status rows live on the note date of W, skips `unknown:recognisedLater` (not negative,
not partial) and has `strict` = negByY. So the two views apply. Done without changing the scorer: run it on the
model status and on the attributed status (`--write-status`), findings/certs/treatments given explicitly from
final2. `--data` was `caselaw-lean-2/data` (its decisions2.tsv is the same inode as final2's, and its meta cache
exists, so no new 100 MB cache file was written in `round5/tests/cache`); `--pool` the frozen
`round5/tests/results/testable_pool_baseline-round4.tsv`; `--out holdout/`.

| final2, pair level | model view | attributed view |
|---|---|---|
| precedent, Y named: strict | 745/12354 = 6.0% (5.6-6.5) | 832/12354 = 6.7% (6.3-7.2) |
| precedent, Y named: negOrPartly | 4295 = 34.8% (33.9-35.6) | 4390 = 35.5% (34.7-36.4) |
| precedent, Y named: laterOnly | 128 | 58 |
| history, Y named: strict | 4367/20843 = 21.0% | 4375/20843 = 21.0% |
| precedent, explicitly admitted: strict | 631/2980 = 21.2% | 669/2980 = 22.4% |
| precedent, not explicit now: strict | 114/9374 = 1.2% (1.0-1.5) | 163/9374 = 1.7% (1.5-2.0) |
| frozen pool all: strict | 114/9374 = 1.2% | 163/9374 = 1.7% |
| frozen pool alsoInFeed: strict | 42/2640 = 1.6% (1.2-2.1) | 82/2640 = 3.1% (2.5-3.8) |
| frozen pool holdoutOnly: strict | 72/6734 = 1.1% (0.8-1.3) | 81/6734 = 1.2% (1.0-1.5) |
| kind overruled: strict | 655/7920 = 8.3% | 724/7920 = 9.1% |
| kind abrogated: strict | 35/3362 = 1.0% | 50/3362 = 1.5% |

Caveat for the report: on this test the attributed view credits the model on a note's date with a negative that the
model only knows from a later recognising court W' (date(W') may be after the note). That is what "as attributed
today" means, but it measures attribution, not what the model could know on that date; the model view stays the
one that answers "what did the law look like then". Full text: `holdout/holdout_final2.{model,attributed}.txt`.

`round5/old_by_class.py` (SCDB / CRS by class) is not date-sensitive (admitted pairs only); one view.
Behaviour (`behaviour.py`) and Shepardized compare were not in the brief; not looked at.

## 4. How `round7/score7.sh` should call it (for the agent `infra` / the lead)

```bash
# OUT=round7/out/$N  DATA=round7/stage/$N  R=round7/results/$N   (run from caselaw-lean-2/)
echo "== fresh lists, dev (model and attributed date views)"
python -X utf8 round7/score_fresh7.py --split dev --status "$OUT/status.tsv" --treatments "$DATA/treatments.tsv" \
  --data "$DATA" --label "$N" --out "$R" --write-status "$R/status_attributed.tsv" > "$R/fresh_dev.txt" 2>&1
grep -A25 "^side by side" "$R/fresh_dev.txt"; grep "^moves" "$R/fresh_dev.txt"
echo "== holdout notes, both views"
HD="$DATA"; [ "$DATA/decisions2.tsv" -ef "$C2/data/decisions2.tsv" ] && HD="$C2/data"   # reuse the meta cache
cd round5/tests
python score_holdout.py --status "$OUT/status.tsv" --label "$N" --findings "$OUT/findings.tsv" --certs "$OUT/certs.tsv" \
  --treatments "$DATA/treatments.tsv" --data "$HD" --out "$R/holdout" \
  --pool "$C2/round5/tests/results/testable_pool_baseline-round4.tsv" > "$R/holdout.txt" 2>&1
python score_holdout.py --status "$R/status_attributed.tsv" --label "$N.attributed" --findings "$OUT/findings.tsv" \
  --certs "$OUT/certs.tsv" --treatments "$DATA/treatments.tsv" --data "$HD" --out "$R/holdout" \
  --pool "$C2/round5/tests/results/testable_pool_baseline-round4.tsv" > "$R/holdout_attributed.txt" 2>&1
cd "$C2"; rm -f "$R/status_attributed.tsv"     # 47 MB, regenerable
```

Notes: with `--status` pointing at the attributed copy, `--findings`, `--certs`, `--treatments` must be given (the
defaults look beside the status file). With `--out` other than round5/tests/results, pass `--pool` explicitly
(otherwise the frozen-pool section is silently missing), on both calls.
`--data "$DATA"` alone works but writes a ~100 MB meta cache into `round5/tests/cache` for each new stage path.
Sealed run (the lead, once, after FREEZE.md): `python round7/score_fresh7.py --split test --status ... --treatments
... --data ... --label <name>` gives both views and appends ONE line to `sealed/TEST_RUNS.log`; its model view is
score_fresh.py's number for number, so score_fresh.py need not be run on test as well (that would add a line).

## 5. Checks in `check/`

- `score_fresh_r5_copy.py`: round-5 scorer with results redirected (two-line diff), the reference.
- `compare_model_view.py`: model view vs the reference (tables, pairs, samples).
- `fake_test_path.py`: exercises the `--split test` code path with GOLD pointed at a throw-away fake folder whose
  "sealed/test.tsv" is a copy of the DEV key (the real sealed folder is not touched): 2 runs -> 2 log lines of 6
  fields, results named `<label>.fresh7.*`, no moves file, `--out` refused, tables equal to the dev run. Fake folder
  deleted afterwards.

To rerun: `python -X utf8 round7/score_fresh7.py --split dev --status round6/history/out/final2/status.tsv
--treatments round6/history/stage/final2/treatments.tsv --label final2 --out round7/agents/b3/results/final2`
(about 30 s; add `--write-status round7/agents/b3/check/final2_status_attributed.tsv` for the holdout runs).

## Open points

- The 50 recognised groups with no negative row of their own are left as the model has them (brief). If the lead
  wants "attributed" to also date Y's overruling from date(Y) where another actor's negative masks it, that is a
  one-line change in `attribute()`; it moves no dev-key pair on final2.
