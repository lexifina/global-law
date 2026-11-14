# Agent `infra` (round 8): build, run, score, h0 benchmark shadow, base reproduction, live page

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/infra/` (NOTES.md). You are the
only agent that reads `benchmarks/<key>/key*.tsv` (and the files a scorer needs), and only by script, keeping
half = h0; never print, copy or summarise an h1 row; never write anything under `benchmarks/`.

Do, in this order, writing each marker as soon as its part is verified (other agents wait on them):

1. `round8/certify8.py`: round-7 `round7/certify7.py` with base `round7/stage/v3` (live tables used for duplicate /
   cite-index checks) and round-8 row ids `t8:` / `h8:` (instead of `t7:` / `h7:`); nothing else changed (diff it and
   record the diff in NOTES). Also check how `round5/recog/certify_recog.py` and `round5/opwords/certify_opwords.py`
   are pointed at a live base (round 7 used them with final2) and write `round8/CERTIFIERS.md` saying exactly how to
   run each against v3.
2. `round8/stage8.py`: `round7/stage7.py` with base `round7/stage/v3`; same options. Self-test: `stage8.py base` (no
   deltas) gives every table as a hard link / byte-identical to v3. Make the staged-table list extensible: any extra
   table a round-8 Lean rule may add later is listed in one place (a constant + `EXTRA_TABLES`), so a future table
   (e.g. a docket index) is copied without editing the run script.
3. `wsl/r8_run.sh` (copy `wsl/r7_run.sh` to `round8/pre/` is not needed: it is a new file): base mirror
   `base_r8_v3` built from the round-7 mirror `data_r7_v3` checked with cmp against Windows `round7/stage/v3`;
   `round8/LEAN_READY` gate; `NOBUILD=1` runs the runner binary already built (that is the round-7 build = the v3
   checker; first copy it aside as `~/caselaw2/r8_bin/caselaw2_r7v3` and record its sha1, and make NOBUILD use that
   copy so later builds by `lean8` cannot change it mid-round; a `R8BIN=<path>` override selects another binary);
   output `round8/out/<name>/`, difftest `difftest/r8_<name>`; verdict counts printed for `t8:` / `h8:` rows; copies
   every staged table the stage folder has (the list from step 2). **Base reproduction:** `stage8.py base` +
   `NOBUILD=1 r8_run.sh base` → every `round8/out/base/*.tsv` byte-identical to `round7/out/v3/*.tsv` (cmp; record).
   Then write `round8/INFRA_READY` (with the sha1 of the binary and the date).
4. h0 benchmark shadow `round8/bench_h0/`: for each key (`fjc_idb_appeals`, `shadow_docket`, `scdb_disposition`,
   `state_overruled_tables`) copy its `score.py` and the helper modules it imports (`common/benchlib.py`,
   `shadow_docket/sdlib.py`, …) with only path changes, and write the key files filtered by script so that the
   scorer's h0 result is exactly what the full scorer gives for h0 (read how each scorer assigns the half — per item,
   per node, smallest docket among a node's items — and filter at the level that preserves it; also secondary files
   such as `secondary_pairs.tsv` or `key_nodes.tsv`). Results go to `round8/results/<label>/bench/` (`<key>.h0.json`
   and `<key>.h0.cases.tsv`; drop any empty h1/all output). One entry point:
   `python round8/bench_h0/score_h0.py --out <outdir> --data <stagedir> --label <x>` (all four keys; prints one line
   per key with the primary metric and its sub-metrics, k/n and Wilson). **Verify:** on the round-6 build
   (`round6/history/out/final2` + `round6/history/stage/final2`) and the round-4 build the shadow reproduces the metrics
   of `benchmarks/<key>/results/round6.h0.json` / `round4.h0.json` exactly (compare the metrics dicts by script;
   these two files are already public). Then score `round7/out/v3` + `round7/stage/v3` as label `v3` (the round-8
   baseline) and write `round8/bench_h0/READY` with the v3 h0 figures. Also `round8/bench_h0/diff_h0.py A B` → per-key
   metric changes and the h0 cases that flip (for diagnosis agents).
5. `round8/score8.sh <name>`: `round7/score7.sh` with round-8 paths (`round8/out`, `round8/stage`, `round8/results`),
   the fresh-list dev scorers, no-leak, holdout notes, old lists (burned), Shepardized dev, plus the h0 benchmark step;
   `round8/summary8.py` (one page, every line of `round7/summary7.py` plus the four h0 keys). Never the time split
   (`round7/heldout/`), never a sealed half, never h1. Run it on `base` and check the dev numbers equal round-7 v3's
   (`round7/results/v3/summary.txt`).
6. Sealed tooling, written but NOT run: `round8/freeze8.py` (as `round7/freeze7.py`: hashes of the frozen stage/out
   files and the scripts; `--check`), `round8/score_sealed8.sh <name>`: fresh lists sealed half (fourth use; same
   scorer as round 7), Shepardized sealed (as `round7/shep_sealed7.py`), and the four benchmark scorers in
   `benchmarks/<key>/score.py --out round8/out/<name> --data round8/stage/<name> --label round8` (they write their own
   results; that is the single sanctioned write into benchmarks/, done by the lead only), each refusing to run unless
   `round8/FREEZE.md` exists and `freeze8.py --check` passes; appends to `round8/SEALED_LOG.md`.
7. Live page: copy `round5/report/processes.json` to `round8/pre/processes.pre_round8.json`, add a row
   `{"work": "Round 8: own-act queue, docket links, rehearing, multi-case acts, state courts, new held-out keys",
   "state": "Running", "note": "..."}`; write `round5/report/sections/96_round8.html` in the style of
   `95_round7.html` (what round 8 does; the v3 baseline on the four h0 keys and the dev keys; "running"); rebuild
   with `python round5/report/make_overturned.py` and check the section appears. Record how to update both.

Keep NOTES.md current (clock times from `date`). Final report: markers written, base reproduction result, the v3 h0
baseline per key (k/n, Wilson), the v3 dev baseline, how to run everything.
