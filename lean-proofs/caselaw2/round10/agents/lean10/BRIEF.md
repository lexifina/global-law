# Agent `lean10` (round 10): the Lean checker for round-10 rules (single writer of the Lean tree)

Read `round10/DESIGN10.md` (all of it; §4 is your first rule) and `round10/agents/COMMON.md` (disk rule!). Folder
`round10/agents/lean10/` (NOTES.md). You are the ONLY writer of `global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`,
`tools/caselaw2/cues/` (cue_table.json, gen_cues.py), `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`, the
runner sources and the Lean-side run scripts (new ones as `wsl/r10_*.sh`; `wsl/r10_run.sh` itself is `infra10`'s).
Never edit the Python reference (`tools/caselaw2/ref/`, agent `ref10`). Do not touch other sessions' Lean files
(`LegalProofs/USTax/**` incl. `Entity*`, `USTax/Hunt/`, `tools/hunt/`, `tools/taxcode/**`).
Model your work on round 9: `round9/LEAN9.md` (format: §0 readings, §1 definitions + theorems stated BEFORE proving,
mutants, §2 tables/loader/runner, §3 results), `round9/agents/lean9/NOTES.md` (backup list, build, lock, audit,
regression commands; `wsl/r9_*.sh`; how v8e was reproduced).

Do:
1. Backup to `round10/pre/` (round 9's backup file list, SHA1SUMS.txt) before any edit.
2. `round10/LEAN10.md` §0 (readings of anything DESIGN10 §4 leaves open: the docket field — does the runner load a
   docket per node? if not, how it should come in (a column of `history_remand.tsv` checked against a new
   `node_docket.tsv`? the lead decides; write `round10/agents/lean10/QUESTIONS.md` and continue on your stated
   reading); B's text hash / window; the order's date forms; the order's compact citation key) and §1 (definitions,
   theorem statements, mutants) BEFORE code.
3. Implement DESIGN10 §4 (`history_remand.tsv`, `remandBridge`), round-10 mode by presence. Prove the theorems as
   stated; existing statements unchanged; no `sorry`, no new axiom, no `native_decide`; one mutant per new rule (DESIGN10
   names four), each killed by a stated property (diagonal guarded); `#guard` replays; a small fixture
   `round10/fixtures/remand`.
4. Lock + `audit.py check` green (0 changed, only additions); regressions a/a2/b/c (and the joined, bridge, zone
   fixtures) byte-identical; build the runner; **reproduce `round9/out/v9c`** with the new binary on stage
   `round9/stage/v9c` (through `wsl/r10_run.sh` with `R10BIN=` once infra10's INFRA_READY exists, or your own script)
   and **`round8/out/v8e`** on `round8/stage/v8e`: cmp every output table (summary.tsv timing lines excepted). Then
   write `round10/LEAN_READY` (date, binary sha1, theorem/mutant counts) and keep the binary at
   `~/caselaw2/r10_bin/caselaw2_lean10`. `df -h /c` before every regression run (stop under 8 GB; delete your own
   regression outputs once compared).
5. Further rules arrive as new sections of DESIGN10 (§5 …) — the lead appends to `round10/agents/lean10/INBOX.md`;
   check it every ~15 minutes. For each: remove LEAN_READY while editing, state before prove, same gates, write
   LEAN_READY again. Do not start a rule the lead has not sent.
Final report: theorems before → after, mutants, audit check, regressions, v9c/v8e reproduction, LEAN_READY times,
readings.
