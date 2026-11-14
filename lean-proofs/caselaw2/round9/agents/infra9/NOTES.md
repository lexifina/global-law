# infra9 (round 9) notes

Clock times from `date` (GMT).

- 02:10 started; read DESIGN9, COMMON, BRIEF, round-8 infra NOTES.
- 02:13 `round9/agents/infra9/mk_round9.py` derives every round-9 copy from the round-8 file by exact replacements
  (asserted counts): certify9.py, certify_recog9.py, certify_opwords9.py, stage9.py, old_by_class9.py, summary9.py,
  score9.sh. certify9 = certify8 with base round8/stage/v8e, ids t9:/h9: (docstring + BASE + hid/tid only).
  Self-tests (test/): multicase rows (2 files, 2,991 rows) with `--base round7/stage/v3` -> all 12 output tsv identical
  to round8/agents/multicase/cert after t8/h8 -> t9/h9; with the v8e base: 2,985 in_base_skipped, 6 admitted = exactly
  the 6 multicase t8 ids that v8e holds with another kind (same id staged first by another delta, so stage8 skipped
  them). certify_recog9 (round-7 queue answers): 317 class lines, all live-identical, 0 rows. certify_opwords9
  (round-7 opwords answers): 48 rows, identical to round 8's self-test after t8 -> t9.
- 02:14 `round9/stage9.py` (mk_round9.py): stage8 with base round8/stage/v8e, output round9/stage/<name>/,
  EXTRA_TABLES = [history_bridge, part_zone] (+ XCOL: part_zone delta lines without 5 columns are reported in the
  log, still staged). Self-test: `stage9.py base` -> 32/32 tsv the same files (hard links) as round8/stage/v8e,
  TABLES.txt name/rows/sha1 identical (only base|written differs), part_zone "empty: not written"; `--force-write`
  -> every tsv cmp-identical; toy part_zone delta (3 lines, 1 duplicate, 1 with 4 columns) -> 2 lines staged, listed
  in TABLES.txt, NOTE printed. Test stages removed.
- 02:15 `wsl/r9_run.sh` written; frozen binary ~/caselaw2/r9_bin/caselaw2_r8v8e = copy of
  ~/caselaw2/r8_bin/caselaw2_lean8 (sha1 3b8d3e4d..., = run_v8e). Two flock slots ~/caselaw2/r9_slot{1,2}.lock.
  Base run started 02:15 (base mirror base_r9_v8e being built from data_r8_v8e, cold cmp).
- 02:16 step 5 written: round9/freeze9.py, score_sealed9.sh, shep_sealed9.py, sealed_lines9.py (extractor).
  Extraction tested on round8/results/v8e/sealed/ (test/sealed_extract/round8_v8e.txt): fresh -> strict model
  32/127, strict attributed 57/127, lenient 77/127 (= the lead's hand line); Shepardized -> NEG strict 123/252 ...
  (= the lead's hand line); round-8 key h1 lines from each scorer's stdout. `freeze9.py --check` -> "no
  round9/FREEZE.md" (exit 1); `score_sealed9.sh base` -> "refused: round9/FREEZE.md missing" (exit 3).
- 02:18 step 6: round9/audit/ via mk_audit9.py (textual port, names/paths/base v8e/t9 ids/r9a01 + telling words),
  decoy pools copied; selftest9 PASS; decoys9.py rebuild into selftest9/pools byte-identical to the copied pools;
  name guard refuses `zone01`. HOWTO.md written; round9/audit/READY 02:19.
- 02:20 step 7 live page: round9/pre/processes.pre_round9.json (copy of the 9-entry file); Round 9 row (state
  Running) appended through a temp file + os.replace (json indent 2, ensure_ascii, trailing LF: the file's own
  format; the first 9 entries are identical to the backup). round5/report/sections/97_round9.html (what round 9
  does; v8e h0 on the four keys; v8e dev block). Rebuilt `python -X utf8 round5/report/make_overturned.py` ->
  ~/Documents/html-reports/overturned.html (id round9 present, process row present).
  How to update: edit the Round 9 entry's "state"/"note" in round5/report/processes.json (write a temp file and
  os.replace it over; never truncate in place) and sections/97_round9.html (plain HTML, embedded verbatim), then
  rerun make_overturned.py.
- 02:20 base mirror built and cmp-checked (32 tables, ~5 min cold); base run's Lean step running.
- 02:29 base run done (Lean ~9 min under load: shard loads 250-400 s while scdb9 also ran). `cmp_out.sh round9/out/base`
  (test/cmp_base_v8e.txt): certs, classes, findings, horty, splits, status, status_lines cmp-identical to
  round8/out/v8e; summary.tsv identical except load_ms/run_ms. ALL SAME.
- 02:30-02:32 `bash round9/score9.sh base` (~2 min): summary.txt vs round8/results/v8e/summary.txt: only the 5 header
  lines differ (+ "round-9 rows by verdict: none"); dev block and h0 block line-for-line identical. No r9_ files left in
  round5/gold_fresh/dev/results.
- 02:32:40 wrote round9/INFRA_READY.
- 02:31 lead message: FRESH_KEYS.txt exists; freeze9.py now hashes, per listed key, benchmarks/<k>/score.py, key.tsv,
  key_nodes.tsv (if present), MAPPING.md, READY (bytes only; I did not open them). score_sealed9.sh step 4 logs
  h0/h1/all from results/<label>.{h0,h1,all}.json via `sealed_lines9.py json` (generic k/n flattener, tested on
  round8/results/v8e/bench/state_overruled_tables.h0.json), stdout lines as fallback. Not run.
- 02:32 slot test: both slot locks held by two `flock -n ... sleep 20`; `r9_run.sh base` printed "two round-9 runs are
  active: base waits for a run slot" and did nothing until stopped by `timeout 12` (data dir / out untouched).

## State: done (steps 1-8). Markers: round9/audit/READY (02:19), round9/INFRA_READY (02:32).
Open points: (1) certify9 keeps the reader/src text `r7:<rule>` (ids only changed, as round 8). (2) WSL dirs
base_r9_v8e (hard links to data_r8_v8e files), data_r9_<name>, difftest/r9_<name> in ~/caselaw2/us-caselaw-lean-work/
caselaw-lean-2/. (3) RUN.txt line 1 now ends with ", slot N". (4) audit decoy pools = round 8's (no round-8 audited
rows added).
- 02:34 lead request: `stage9.py --table NAME=FILE` (hand edit of round9/stage9.py after mk_round9.py; do not rerun
  mk_round9.py over it). Replaces the base non-row table NAME.tsv by a copy of FILE (temp file + os.replace, so the
  hard link to the base is never written through), listed in TABLES.txt as `NAME rows sha1 table` (r9_run.sh copies
  it since its sha1 differs from the base mirror's; freeze9.py hashes every TABLES.txt table). Refused: the ten row
  tables, decisions2, the extra tables; FILE empty / with CR / without final LF. Checked: history, decisions2,
  part_zone refused. `stage9.py nj_test --table adoption=round9/nj/adoption.tsv --table succession=round9/nj/succession.tsv`
  -> adoption 43 rows (base 41; +2 lines 1099->1095, 1222->1206 and 1096->1094 last column L -> S), succession 63 rows
  (1095->1099 U -> S, 1206->1222 L -> S); both copies cmp-identical to the files; other tables hard links.
  NOBUILD r9_run nj_test started 02:35.
- 02:44 nj_test waited for a slot 02:34:54-02:40:35 (two other runs active), Lean running since 02:40.
- 02:46 nj_test run done (NOBUILD frozen binary; adoption + succession copied into data_r9_nj_test, all else base
  mirror). Diff vs round8/out/v8e (agents/infra9/diff_out.py -> test/diff_nj_test_v8e.txt):
  * certs/classes: exactly 3 rows change verdict: t8:4058244:4016514:17127 noAuthority -> ok (operativeWords);
    tw:3991335:4086271:4616:4089451 witnessNoStanding -> okRecognised (class atRiskWitness -> recognised);
    tw:4018149:4006682:13821:4061823 disqualified -> okRecognised (atRiskWitness -> recognised).
  * status: +9 lines, only for the 3 targets: 4086271 neg:overruled from 19490623; 4006682 neg:overruled
    19770929-19790506 (recognisedLater around it); 4016514 unknown:partialScope from 19620618.
  * findings -4 +20: the consequences of those 3 (12 new citesOverruled on 4086271/4006682 citers, 5 atRisk
    recognisedLater on 4006682, the atRisk 4058244->4016514 gone), plus 3 path-only changes from the new succession
    lines: atRisk 4058519->4016236 path sisterCourt>noPower -> sisterCourt>sameCourtSoft; citesVacated 4090117 and
    4090966 -> 4087060 path S44 -> adopted>S44 (same finding, same firm).
  * splits, horty, status_lines identical; summary counters move by the same 3 rows (rows_admitted 220452 -> 220455,
    recognised_rows +2, operative_rows +1, findings/status_rows per shard).
  Reported to the lead.
