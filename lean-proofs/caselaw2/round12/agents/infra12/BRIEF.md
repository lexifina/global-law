# Agent `infra12` (round 12): infrastructure on base v11d (order nodes included), audit exclusion fixed from the start, freeze / sealed / live page

Read `round12/DESIGN12.md` (§0 binding, §1–4, §9) and `round12/agents/COMMON.md` first. Folder
`round12/agents/infra12/` (NOTES.md, a line at least every 10 minutes). Model: round 11's infrastructure by `infra11`
(`round11/agents/infra11/BRIEF.md`, `NOTES.md`, its generator / patch scripts, and the outputs
`round11/{certify11,certify11_claims,certify_recog11,certify_opwords11,stage11,zones11,nodes11,freeze11,old_by_class11,sealed_lines11,shep_sealed11,summary11}.py`,
`round11/score11.sh`, `round11/score_sealed11.sh`, `round11/clean11.sh`, `wsl/r11_run.sh`, `wsl/r11_clean.sh`,
`round11/audit/`, `round11/lead/live11.py`). Port it to round 12 on base **v11d**; never change round-11 files (the
lead's round-11 patches are in those files already: port the files as they are now).

**DISK (binding):** C: has ~20 GB free and is shared; WSL's disk lives on C: too. `df -h /c` before anything big. The
base must NOT be copied: stage12 uses `round11/stage/v11d` in place, read-only (hard links), and writes only changed
tables; the WSL base mirror for v11d (`base_r12_v11d`) is built by hard links from what `wsl/r11_run.sh` left for v11d
in WSL (data dir `data_r11_v11d`; see `round11/out/v11d/RUN.txt`) — never copy unchanged tables. Report sizes added.

## Part A (marker `round12/INFRA_READY` when 1–6 are done and self-tested; write it in NOTES.md too) — target 07:40
1. `round12/certify12.py` (+ `certify12_claims.py` incl. anchorTribunal, `certify_recog12.py`,
   `certify_opwords12.py`): certify11 with ids `t12:` / `h12:`, base `round11/stage/v11d`, node overlay
   `round12/nodes12.py` (env `R12_NODES`, default: the nodes v11d holds = `round11/data_orders`; `--nodes DIR`).
2. `round12/stage12.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE] [--table NAME=FILE]
   [--nodes DIR]`: base `round11/stage/v11d` (keep every extra table and the 1,045 order nodes, `nodes.count`,
   `nodes_map.tsv`). Without `--nodes`: decisions2 / nodes files hard-linked from v11d. With `--nodes DIR`: decisions2
   = the corpus rows + DIR's nodes in file order from N = 6,892,454 (the round-11 nodes are the first 1,045 rows of
   `round12/data_orders/nodes.tsv` with the same local ids, so they keep their ids — check it and refuse otherwise),
   never the v11d nodes twice. `--drop FILE` must be able to drop base (v11d) rows by id (e.g. h11 olist rows whose
   node text changed). Self-test: staging with no delta reproduces v11d's tables byte for byte (identical sha1).
3. `wsl/r12_run.sh <name> [ref]`: as r11_run.sh; base mirror `base_r12_v11d`; NOBUILD = the frozen round-11 binary
   (`~/caselaw2/r11_bin/caselaw2_lean11_s51`, sha1 a1cc4296…; hard-link or copy to
   `~/caselaw2/r12_bin/caselaw2_r11v11d` and check the sha1 before each run); without NOBUILD it refuses unless
   `round12/LEAN_READY`; two run slots machine-wide (lock names r12_slot*; respect r11 slots if any are held);
   `R12BIN=` override; prints `df -h /mnt/c` and refuses under 8 GB free. **Self-test:** `NOBUILD=1 r12_run.sh
   v11d_check` on a stage with no delta reproduces `round11/out/v11d` byte for byte (every table; timing lines
   excepted), then clean it.
4. `round12/clean12.sh <name>` (+ `wsl/r12_clean.sh`): deletes `round12/stage/<name>`, `round12/out/<name>`, its WSL
   data/difftest dirs; keeps results; refuses names in `round12/KEEP.txt` (create it with `v11d`, `v12_frozen`).
5. `round12/score12.sh <name> [beh] [noold] [nobench]` (+ `summary12.py`, `old_by_class12.py`): score11 on round-12
   paths; h0 only for the four round-8 keys; never h1, never a sealed half, never songer_treat, brace_hall_state,
   fedcir_dataset, bhk_enbanc or any round-12 fresh key. Self-test: score v11d_check and compare with
   `round11/results/v11d/summary.txt`.
6. `round12/audit/` (HOWTO.md, READY): port of `round11/audit/` — base stage v11d, ids t12:/h12:, run names
   `r12<letter><nn>`, decoy pools extended with the round-11 audits' known answers (as infra11 did for round 10),
   telling-word guard extended with: banc, panel, rehearing, superseded, judge, county, district, journal, ligature.
   **The `--exclude` fix from the start:** `make_packs12 --exclude FILE` (repeatable; any round's `sample.tsv`)
   excludes every item matching by (table, by, target, kind) — and by (by, target) when the earlier file lacks kind —
   whatever the row id prefix (t10/h10/t11/h11/t12/h12); it prints how many items each file excluded. Self-test:
   (a) a pack drawn from a class that contains r11 sample pairs excludes all of them; (b) a synthetic sample with
   h10/h11 ids of the same pairs is excluded too. Packs show text of order nodes through the overlay.

## Part B — node plumbing for `round12/data_orders` (marker `round12/NODES_READY` when tested; agent `orders12` writes the data, same FORMAT as `round11/data_orders/FORMAT.md`; it lists text changes in `CHANGED.tsv`)
- `round12/nodes12.py` (as nodes11: `is_extra`, `meta`, `text`, `patch()`), reading the folder given by `--nodes` /
  `R12_NODES`. Self-test with a copy-free check: pointing it at `round11/data_orders` gives the v11d node table byte
  for byte (stage12 `--nodes round11/data_orders` → decisions2 sha1 = v11d's) — then delete that test stage.
- Report the size of one `--nodes` variant (C: and WSL).

## Part C (after A; LEAD ONLY scripts — you only run `--help` / dry self-tests that score nothing)
7. `round12/freeze12.py` (+ `--check`) and `round12/score_sealed12.sh <frozen name>` (+ `sealed_lines12.py`,
   `shep_sealed12.py`), steps: 1. fresh lists sealed (burned); 2. Shepardized sealed (burned); 3. the four round-8
   keys, h1 halves, **fifth use**, `--label round12` (refused if `results/round12.h1.json` exists); 4. `songer_treat`,
   `brace_hall_state` (**fourth use**), `fedcir_dataset` (**third use**), `bhk_enbanc` (**second use**) on the frozen
   build `--label round12` (h0/h1/all; refused if `results/round12.*` exists; v11d figures exist as `round11`, not
   re-run) — run their `score.py` by the CLI in `benchmarks/CONTRACT.md` without opening their folders (the CLI is the
   same for every key; copy the invocation from `round11/score_sealed11.sh`); 5. keys listed in
   `round12/FRESH_KEYS.txt` (first use; you never read that file — the script reads it at run time): v11d
   (`round11/out/v11d` + `round11/stage/v11d`) as `--label round11v11d` and the frozen build as `--label round12`;
   skipped and logged when the file is absent. Every run appended to `round12/SEALED_LOG.md` from the scorers' own
   files with the use count of each key on its line. freeze12 hashes the frozen stage tables (incl. `--nodes` files and
   `round12/data_orders/nodes.tsv` + text if staged), out tables, the binary, every round-12 agent script and the
   scorers (exclude NOTES.md and logs).
8. Live page: `round5/report/sections/99b_round12.html` ("Round 12 — in progress", the plan as a short list from the
   DESIGN12 title) and a "Round 12" row in `round5/report/processes.json` (atomic edit: temp file then rename; every
   other row byte for byte; backup to `round12/pre/`), `round12/lead/live12.py` (as live11.py: --state/--note/
   --progress/--section), run `python -X utf8 round5/report/make_overturned.py` and check the section shows.

Time box: INFRA_READY by ~07:40, NODES_READY by ~08:00, Part C meanwhile. Report: what exists, self-test results
(byte-for-byte), sizes added, the exclusion self-test output, open points.
