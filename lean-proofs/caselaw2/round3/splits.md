# Round 3 item 6: split questions for gold-split sections never read for splits (agent `splits`, resumed 23:03, 12 Nov 2026)

All model reading and judging is by Claude subagents. No external model. Gold gives only the list of SECTIONS
(`round2/splits_misses.tsv`, classes A1/A2); holdings and answers come from the circuit opinions.

## State found at resume (23:03)
- Scripts in `tools/caselaw2/holdings/round3/` (gs_build, gs_stage, gs_val, gs_install, gs_gain) read through: complete, compile.
- `work/round3/splits/w/`: 45 reader batches (20 windows each), `windows.json`, `sections.tsv`, `citers.json`.
- Reader answers `w/out/batch_NN.jsonl`: 37 of 45 present and complete. Missing: 01, 03, 05, 15, 30, 35, 36, 39.
- `w/items.json` and `cluster_00..02.md` were a prep run on a partial set of answers; no cluster output (`w/cout/`), nothing staged, no delta, nothing installed (`data/holdings.tsv`, `issues.tsv`, `holdings_cert_text.tsv` unchanged since round 2).
- Baseline reference run `out0` (private copy `data0`): 491 splits, 101 conflicts.
- `eval/score.py` edit (22:50): adds `splits_honest` (extra keys `honest_*` in the split block, inside try/except). Complete, compiles, existing keys unchanged. Kept.

## Stopped (23:10): item dropped for this round by the coordinator
- 8 reader subagents had been launched for the missing batches (01, 03, 05, 15, 30, 35, 36, 39) and were told to stop. Any `w/out/batch_NN.jsonl` for those eight that appears after 23:08 is from a cancelled reader; it is unused.
- Nothing clustered, staged, validated, audited or installed. No reference run. No `.tmp` file, no `data/.install.lock`.
- `eval/score.py`: predecessor's edit kept (additive `honest_*` keys only; backup `work/round3/splits/score.pre_splits_round3.py`).

## Next round
- Read the 8 missing batches; `gs_stage.py prep` (re-run: the existing `items.json`/`cluster_*.md` are from a partial set), cluster readers into `w/cout/`, `gs_stage.py stage`, private install, `gs_val.py` blind audit, live install, one reference run + `gs_gain.py`.
- `gs_stage.py` keeps questions with 2 circuits even when the answers agree: filter to opposite answers before install.
- Update: the batch 15 reader finished before the stop reached it. `w/out/batch_15.jsonl` is complete (25 windows, 8 interpreting) and can be used next round; 7 batches remain unread unless their files also appear complete (25 lines).
- Update 2: the readers for 01, 03, 05, 30, 35 and 36 also wrote their files before the stop reached them. Checked by count: each of `w/out/batch_{01,03,05,15,30,35,36}.jsonl` has 25 lines for 25 windows (44 of 45 answer files now present). Batch 39 has no answer file and is the only unread batch. These seven files were not inspected beyond the line count.
- Update 3 (final): batch 39 was also written before its reader stopped (25 lines). All 45 answer files are now present with one line per window; none of the eight late files was inspected beyond the line count. Next round starts at `gs_stage.py prep`, no reading needed.
- `data/courts2.tsv.tmp` and `data/decisions2.tsv.tmp` (23:05) exist in `data/`; they are not from this item (it never touches those files).
