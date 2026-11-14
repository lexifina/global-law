# Agent `infra9` (round 9): staging, run, scoring, audit tooling, live page

Read `round9/DESIGN9.md` (§0–3) and `round9/agents/COMMON.md`. Folder `round9/agents/infra9/` (NOTES.md). Model the
work on round 8's `round8/agents/infra/NOTES.md` (same steps, round-9 paths). Copy, never edit, round-8 files.

1. `round9/certify9.py` (+ `certify_recog9.py`, `certify_opwords9.py` if trivial): round-8 copies with base
   `round8/stage/v8e`, ids `t9:` / `h9:`; self-test as round 8 did (a round-8 delta re-certified against v8e: all
   skipped as in base).
2. `round9/stage9.py`: stage8 with base `round8/stage/v8e`, output `round9/stage/<name>/`; EXTRA_TABLES must include
   `history_bridge` (in the base) and `part_zone` (new round-9 table, DESIGN9 §4; absent ⇒ not written); keep
   TABLES.txt. Self-test: `stage9.py base` → every table the same file as v8e (hard links).
3. `wsl/r9_run.sh` (new file; `wsl/r8_run.sh` untouched): base mirror `base_r9_v8e` from the mirror's `data_r8_v8e`
   (cmp-checked against Windows `round8/stage/v8e`, incl. history_bridge); NOBUILD = the frozen round-8 binary
   copied to `~/caselaw2/r9_bin/caselaw2_r8v8e` (sha1 3b8d3e4d45fb60a84c5cfb00c2f6729ebc2bfa6b, checked each run);
   `R9BIN=` override; build mode refuses unless `round9/LEAN_READY`; output `round9/out/<name>/`; optional `ref`.
   **Machine-wide limit: at most two runs at once** (two flock slots, e.g. `~/caselaw2/r9_slot{1,2}.lock`; a third
   run waits and prints that it waits). Verdict summaries for `t9:` / `h9:` rows. Reproduce `round8/out/v8e` from
   stage `base` (every output table cmp-identical; summary.tsv timing lines excepted).
4. `round9/score9.sh` + `summary9.py` (+ `old_by_class9.py`): score8 on round-9 paths, h0 bench via
   `round8/bench_h0/score_h0.py --results round9/results/<name>/bench`. Check `score9.sh base` equals
   `round8/results/v8e/summary.txt` line for line (dev block and h0 block).
5. `round9/freeze9.py` (hash list as freeze8 + round-9 files + `part_zone.tsv` and any extra table) and
   `round9/score_sealed9.sh` (LEAD ONLY; written, NOT run): fresh sealed (5th use), Shepardized sealed (4th use) via a
   `shep_sealed9.py` copy, the four round-8 keys' h1 halves (second use) with `--label round9` (refuse if
   `benchmarks/<key>/results/round9.h1.json` exists), and a hook for the round-9 fresh keys: for every folder name in
   `round9/FRESH_KEYS.txt` (one per line; written by the lead later) run `benchmarks/<k>/score.py` twice: on
   `round8/out/v8e` + `round8/stage/v8e` with `--label round8v8e` and on the frozen build with `--label round9`.
   FIX round 8's empty log lines: take the SEALED_LOG figures from the scorers' output files (json or the exact
   result lines), and test the extraction on round 8's existing `round8/results/v8e/sealed/` files (no new scoring).
6. `round9/audit/`: port of `round8/audit/` (make_packs9.py, score_audit9.py, more_text9.py, decoys9.py, HOWTO.md,
   AUDITOR_BRIEF9.md, decoy pools copied) with run names `r9<letter><nn>` and the letter table of COMMON.md; neutral
   run-name check kept; selftest; write `round9/audit/READY`.
7. Live page: back up `round5/report/processes.json` to `round9/pre/processes.pre_round9.json`; add a "Round 9" row
   (state Running) by writing a temp file and renaming it over (atomic; never truncate in place); write
   `round5/report/sections/97_round9.html` (what round 9 does; the v8e baseline: h0 on the four keys and the dev
   block); rebuild with `python -X utf8 round5/report/make_overturned.py`; note in NOTES.md how to update.
8. Write `round9/INFRA_READY` (date, binary sha1, self-test results) as soon as 1–4 work; the audit READY and the live
   page may follow. Report: the commands, self-tests, anything the lead must know.
