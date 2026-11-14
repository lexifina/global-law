# infra (round 8) notes

Clock times from `date` (GMT).

- 00:17 started; read DESIGN8, COMMON, BRIEF.
- 00:19 `round8/certify8.py` = round7/certify7.py with exactly: default --base round7/stage/v3 (was
  round6/history/stage/final2), new ids `t8:`/`h8:` (were `t7:`/`h7:`), docstring (title, usage line, the two id
  descriptions). `src`/reader columns still `r7:<rule>` (unchanged). Diff:
  - line 1-2 title; line 4 usage `round8/certify8.py`; lines 57/60 id docs t8/h8;
  - `BASE = os.path.join(C2, "round7", "stage", "v3")`; `hid = "h8:%d:%d:%s"`; `tid = "t8:%d:%d:%d"`.
  Self-test: round-7 antecedent rows (1,747) with `--base round6/history/stage/final2` -> all 12 output tsv files
  identical to round7/agents/antecedent/cert after t7/h7 -> t8/h8; with the v3 base: 1,506 skipped as in base, 241
  admitted = the round-7 antecedent rows dropped by stage_drop_v3 (242 dropped ids; one shares a key).
- 00:21 `round8/certify_recog8.py`, `round8/certify_opwords8.py` (paths-only copies of the round-7 copies; base
  v3 / round7/out/v3; ids t8 for opwords; answers/items/index/out required args) + `round8/CERTIFIERS.md`.
  Self-tests: queue answers -> 317 class lines all live-identical, 0 rows; opwords7 answers -> 48 rows.
- 00:22 `round8/stage8.py` (built by `agents/infra/mk_stage8.py` from stage7.py by exact replacements): base v3,
  out round8/stage/<name>, EXTRA_TABLES constant (+ `--extra-table` for trials), TABLES.txt per stage.
  Self-test: `stage8.py base` -> 31/31 tsv files are the same files (hard links) as round7/stage/v3;
  `--force-write` -> all 31 cmp-identical; toy extra table staged + listed in TABLES.txt, empty extra not written,
  unknown delta file reported. Test stages removed.
- 00:24-00:29 h0 benchmark shadow round8/bench_h0/ (README.md): build_keys.py (h0 keys by script; KEYS.json),
  scorer copies via agents/infra/mk_bench_h0.py (diff in agents/infra/bench_h0_scorer.diff), score_h0.py,
  verify_h0.py, diff_h0.py. First verify: Shadow Docket differed (my filter let an h0 item linked to an h1 node open
  that node as a unit with a half computed from h0 items only); fixed with synthetic h1 stub items (509 nodes).
  Then VERIFY OK for round6 and round4 (every metrics / extra_metrics / link dict identical, incl. SCDB federal/state
  h0). Filtered key rows: FJC units 16,743, items 120,585; Shadow 105,703 (incl. 562 h1-half items of h0 units, 509
  stubs); SCDB 14,712; state 290 (132 units; no other-half rows needed).
- 00:29 v3 h0 baseline scored (round8/results/v3/bench/); every cases table holds only h0 units. 2026-11-14 00:29:17 GMTST: wrote
  round8/bench_h0/READY.
- 00:22 `wsl/r8_run.sh` (new file). Frozen binary: `~/caselaw2/r8_bin/caselaw2_r7v3` = copy of
  `~/caselaw2/r7_bin/caselaw2_v3` (the v3 run's binary; same as runner/.lake/build/bin/caselaw2 at 00:18), sha1
  3270d7f3443fee00121ea55358b951eca8df9fea; NOBUILD runs it and checks the sha1 first; `R8BIN=` override is copied
  aside. Always `run_direct` (no lake call) with the chosen binary, asOf 20261112, 8 shards. Data dir: tables listed in
  stage TABLES.txt whose sha1 equals the base mirror's are symlinked, others copied; empty optional tables left out.
  Base mirror base_r8_v3 from data_r7_v3 (hard links / symlinks), cmp-checked against round7/stage/v3: built 00:31
  (WSL had restarted at 00:18, cold cache: ~8 min). Lean base run started 00:29:40.
- 00:30 round8/score8.sh, summary8.py, old_by_class8.py (via agents/infra/mk_score8.py), freeze8.py,
  shep_sealed8.py, score_sealed8.sh (written, NOT run). Note: score8.sh calls round5 score_fresh.py, which writes
  into round5/gold_fresh/dev/results/ and the files are moved out at once (as round 7's score7.sh did).
- 00:33 live page: round8/pre/processes.pre_round8.json (copy, 00:09 file); round5/report/processes.json + Round 8
  row (state Running; json indent=2 as the file was). INCIDENT: a first edit attempt opened processes.json for
  writing before a NameError, leaving it empty for <1 min; restored from round8/pre/processes.pre_round8.json at once
  (8 entries, identical), then the row added. round5/report/sections/96_round8.html written (what round 8 does, v3
  h0 baseline on the four keys, dev baseline, "running"). Rebuilt with `python -X utf8
  round5/report/make_overturned.py` -> ~/Documents/html-reports/overturned.html: section id round8
  present, process row present.
  How to update: edit the Round 8 entry's "state"/"note" in round5/report/processes.json (JSON, indent 2) and
  sections/96_round8.html (plain HTML, embedded verbatim), then rerun make_overturned.py.
- 00:34 base reproduction OK (7 output tables cmp-identical to round7/out/v3; summary.tsv differs only in load_ms/run_ms timing lines). 2026-11-14 00:33:42 GMTST: wrote round8/INFRA_READY.
- 00:33-00:34 `bash round8/score8.sh base` (56 s): the dev block of round8/results/base/summary.txt (fresh lists,
  both views, no-leak, holdout notes, old lists, Shepardized dev) is line-for-line identical to
  round7/results/v3/summary.txt; new-keys h0 block = the v3 baseline in bench_h0/READY. No r8_ files left in
  round5/gold_fresh/dev/results.
- 00:34 sealed tooling checked without running a sealed scorer: `freeze8.py --check` -> "no round8/FREEZE.md" (exit 1);
  `score_sealed8.sh base` -> "refused: round8/FREEZE.md missing" (exit 3). All round-8 .py/.sh are LF.

## State: done (all 7 steps). Markers: round8/bench_h0/READY (00:29), round8/INFRA_READY (00:33).
Open points: none blocking. (1) certify8 keeps the reader/src text `r7:<rule>` (only ids changed, as briefed).
(2) The Shadow Docket h0 key holds 562 rows whose own half is h1 (items of h0 units, needed for pooling) and 509
synthetic stubs; FJC/SCDB/state h0 keys hold h0 rows only. (3) WSL data dirs data_r8_<name> and base_r8_v3 live in
~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/.
