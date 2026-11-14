# Agent `infra11` (round 11): infrastructure on base v10d, plus the order-list node overlay (DESIGN11 §4)

Read `round11/DESIGN11.md` (§0 binding, §1, §2, §4, §9) and `round11/agents/COMMON.md` first. Folder
`round11/agents/infra11/` (NOTES.md, a line at least every 10 minutes). Model: round 10's infrastructure by agent
`infra10` (`round10/agents/infra10/BRIEF.md`, `NOTES.md`, its generator scripts `mk_round10.py`, `mk_r10run.py`,
`mk_audit10.py`, `mk_sealed10.py`, `mk_howto10.py`; the outputs `round10/{certify10,certify10_claims,
certify_recog10,certify_opwords10,stage10,zones10,freeze10,old_by_class10,sealed_lines10,shep_sealed10,summary10}.py`,
`round10/score10.sh`, `round10/score_sealed10.sh`, `round10/clean10.sh`, `wsl/r10_run.sh`, `wsl/r10_clean.sh`,
`round10/audit/`, `round10/lead/live10.py`). Port it to round 11 on base **v10d**; never change round-10 files.
Note: `round10/stage10.py` was patched by the round-10 lead after infra10 (history_remand 12 columns,
history_tbridge extra table; backup `round10/pre/stage10.py.pre_lead_0436`) — port the patched version.

**DISK (binding):** C: has ~24 GB free and is shared; WSL's disk lives on C: too. `df -h /c` before anything big.
The base must NOT be copied: stage11 uses `round10/stage/v10d` in place, read-only (hard links), and writes only
changed tables; the WSL base mirror for v10d (`base_r11_v10d`) must be built by hard links from what `wsl/r10_run.sh`
left for v10d in WSL (`~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/…`; find the v10d data dir) — never copy
unchanged table files. Report the sizes you add. Do not delete anything of round 10.

## Part A (marker `round11/INFRA_READY` when 1–6 are done and self-tested; write it in NOTES.md too)
1. `round11/certify11.py` (+ `certify11_claims.py`, `certify_recog11.py`, `certify_opwords11.py`): certify10 with
   ids `t11:` / `h11:` and base `round10/stage/v10d` (check the round-10 claims port is carried: anchorWide,
   joinedFar, implicitReject, trialBridge if certify10_claims had it).
2. `round11/stage11.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE] [--table NAME=FILE]`:
   base `round10/stage/v10d` (keep every round-10 extra table: history_bridge, part_zone, history_remand,
   history_tbridge, adoption, succession, …). Part zones for the acting nodes of new rows (as stage10 / zones10).
   Self-test: staging with no delta reproduces v10d's tables byte for byte (hard links / identical sha1).
3. `wsl/r11_run.sh <name> [ref]`: as r10_run.sh, base mirror `base_r11_v10d`, NOBUILD = the frozen round-10 binary
   (`~/caselaw2/r10_bin/run_v10d`, sha1 e7e32592…; copy or hard-link to `~/caselaw2/r11_bin/caselaw2_r10v10d` and
   check the sha1 before each run); without NOBUILD it refuses unless `round11/LEAN_READY`; two run slots machine-wide
   (lock names r11_slot*); `R11BIN=` override; `ref` hook as r10's (separate difftest folder per variant name);
   prints `df -h /mnt/c` and refuses under 8 GB free. **Self-test:** `NOBUILD=1 r11_run.sh v10d_check` on a stage
   with no delta must reproduce `round10/out/v10d` byte for byte (every table; summary timing lines excepted), then
   clean it.
4. `round11/clean11.sh <name>` (+ `wsl/r11_clean.sh`): deletes `round11/stage/<name>`, `round11/out/<name>` and its
   WSL data/difftest dirs; keeps results; refuses names in `round11/KEEP.txt` (the lead writes it).
5. `round11/score11.sh <name> [beh] [noold] [nobench]` (+ `summary11.py`, `old_by_class11.py`): as score10.sh on
   round-11 paths; h0 only for the four round-8 keys; never h1, never a sealed half, never songer_treat,
   brace_hall_state, fedcir_dataset or any round-11 fresh key. Self-test: score v10d_check before deleting it and
   compare to `round10/results/v10d/summary.txt`.
6. `round11/audit/` (HOWTO.md, READY): port of `round10/audit/` — base stage v10d, ids t11:/h11:, run names
   `r11<letter><nn>` (letters in DESIGN11 §3), decoy pools extended with the round-10 audits' known answers (as
   infra10 did for round 9), telling-word guard extended with: uncited, docket, fedcir, federal, circuit, claims,
   order, list, rehearing, banc, tie, caption. The packs must be able to show text of §4 order nodes (Part B).

## Part B — DESIGN11 §4 node overlay (marker `round11/NODES_READY`; start right after INFRA_READY)
`orders11` writes `round11/data_orders/nodes.tsv` + `text/<local id>.txt` (format in DESIGN11 §4; agree the exact
columns with orders11 through files: write your expected format to `round11/data_orders/FORMAT.md` early, orders11
reads it). Build:
- `stage11.py --nodes round11/data_orders` (also accepts a small synthetic test folder): appends decisions2 rows for
  the new nodes with ids N, N+1, … (N = the corpus node count used by the runner, `graph/nodes.count`), in the
  corpus's own row shape (find how the corpus's S. Ct. memorandum orders look in `decisions2.tsv`: court id of the
  Supreme Court, unit, bench, publication, kind, text sha — **find how `text_sha` is computed** for corpus nodes and
  compute it the same way for the new text, so `cert_text.tsv` / `window_sha.tsv` windows key on it) and writes
  `nodes.count` + `nodes_map.tsv` (local id → node id) in the stage. decisions2.tsv is ~915 MB: the staged copy is a
  new file (base hard-linked otherwise) — only when `--nodes` is given; say how big. If the Lean runner or the
  scorers cannot take extra node ids (check `LegalProofs/CaseLaw2/Run.lean` `main` / `Data.lean` `loadDecisions`
  read-only, the edges dir `lean-in-v3`, `benchmarks/common/benchlib.py`, `round8/bench_h0/score_h0.py` and the
  four round-8 keys' `score.py` — never the closed keys' folders), write `round11/agents/infra11/LEAN_REQUEST.md`
  instead and tell the lead at once.
- `r11_run.sh` uses the stage's `nodes.count` when present (else `../graph/nodes.count`).
- `round11/nodes11.py`: `is_extra(node)`, `meta(node)` (court, date, name/caption, docket), `text(node)`, and a
  `patch()` that makes `round6/history/r6lib.py`'s text/window accessors (and whatever certify11, zones11, the audit
  pack builder and more_text use) return the overlay text for extra ids — in memory, without editing r6lib. Wire it
  into certify11 / zones11 / audit packs, active only when a nodes folder is given (`--nodes` / env
  `R11_NODES=round11/data_orders`). Part zones for an order node: the same builder over its text; if that yields no
  zone, find what the Lean does with a node without zone lines and pick the reading that makes the order's
  disposition sentence a per-curiam zone only if the round-9 zone builder would do so for a corpus S. Ct. memorandum
  order of the same shape (check on a few corpus orders); state it in NOTES.md.
- Self-test on a synthetic nodes folder (3 fake orders + 1 fake history row by one of them on a real corpus
  decision): stage, NOBUILD run, the row reaches the Lean and is admitted (or rejected for a stated reason you
  understand); with no `--nodes` the output is v10d byte for byte; scorers ignore the extra ids. Then clean.

## Part C (after A; LEAD ONLY scripts, never run by you except `--help` / dry self-tests that score nothing)
7. `round11/freeze11.py` (+ `--check`) and `round11/score_sealed11.sh <frozen name>` (+ `sealed_lines11.py`,
   `shep_sealed11.py`), as round 10's, steps: 1. fresh lists sealed (burned); 2. Shepardized sealed (burned);
   3. the four round-8 keys, h1 halves, **fourth use**, `--label round11` (refused if `results/round11.h1.json`
   exists); 4. `songer_treat`, `brace_hall_state` (**third use**) and `fedcir_dataset` (**second use**), frozen
   build `--label round11` (h0/h1/all; refused if `results/round11.*` exists; v10d figures exist as `round10`, not
   re-run) — run their `score.py` by the CLI in `benchmarks/CONTRACT.md` without opening their folders; 5. fresh keys
   listed in `round11/FRESH_KEYS.txt` (first use; you never read that file — the script reads it at run time): v10d
   (`round10/out/v10d` + `round10/stage/v10d`) as `--label round10v10d` and the frozen build as `--label round11`;
   skipped and logged when the file is absent. Every run appended to `round11/SEALED_LOG.md` from the scorers' own
   files. freeze11 hashes the frozen stage tables (incl. any `--nodes` files and `round11/data_orders/nodes.tsv` +
   text if staged), out tables, the binary, every round-11 agent script and the scorers (exclude NOTES.md and logs).
8. Live page: `round5/report/sections/99_round11.html` ("Round 11 — in progress", short plan list from DESIGN11
   title) and a "Round 11" row in `round5/report/processes.json` (atomic edit: temp file then rename; every other row
   byte for byte; backup to `round11/pre/`), `round11/lead/live11.py` (as live10.py: --state/--note/--progress/
   --section), run `python -X utf8 round5/report/make_overturned.py` and check it builds.

Time box: INFRA_READY within ~40 minutes; NODES_READY within ~80; Part C meanwhile. Report: what exists, self-test
results, sizes added, the §4 decisions (node ids, text sha, zones), open points.
