# Agent `lean9` (round 9): the Lean checker for round-9 rules (single writer of the Lean tree)

Read `round9/DESIGN9.md` (all of it; §4 is your first rule) and `round9/agents/COMMON.md`. Folder
`round9/agents/lean9/` (NOTES.md). You are the ONLY writer of `global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`,
`tools/caselaw2/cues/` (cue_table.json, gen_cues.py), `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`, the
runner sources and the Lean-side run scripts (new ones as `wsl/r9_*.sh`). Never edit the Python reference
(`tools/caselaw2/ref/`, agent `ref9`). Model your work on round 8: `round8/LEAN8.md` (format: §0 readings, §1
definitions + theorems stated BEFORE proving, mutants, §2 tables/loader/runner, §3 results), `round8/agents/lean8/NOTES.md`
(backup list, build, lock, audit, regression commands: `wsl/r8_lean.sh`, `wsl/r8_final.sh`, `wsl/r7_lean_base.sh`).

Do:
1. Backup to `round9/pre/` (the round-8 backup file list, SHA1SUMS.txt) before any edit.
2. `round9/LEAN9.md` §0 (readings of anything DESIGN9 §4 leaves open: e.g. what "the row's part" is for each table and
   row kind; how offsets of a row relate to the node's text; witness rows; operative/recognised rows; part name
   spellings) and §1 (definitions, theorem statements, mutants) BEFORE code. Ask the lead (NOTES.md line + your
   message is not possible: write `round9/agents/lean9/QUESTIONS.md` and continue on your stated reading) only if a
   reading changes an effect.
3. Implement DESIGN9 §4 (`part_zone.tsv`, `checkPartZone`), round-9 mode by presence. Prove the theorems as stated;
   existing statements unchanged; no `sorry`, no new axiom, no `native_decide`; one mutant per new rule, each killed by
   a stated property (diagonal guarded); `#guard` replays; a small fixture `round9/fixtures/partzone`.
4. Lock + `audit.py check` green (0 changed, only additions); round-4…8 regressions (a/a2/b/c, joined fixture, bridge
   fixture) byte-identical; build the runner; **reproduce `round8/out/v8e`** with the new binary on stage
   `round9/stage/base` (made by `infra9`; or `round8/stage/v8e` through r9_run with `R9BIN=`): cmp every output table
   (summary.tsv timing lines excepted). Then write `round9/LEAN_READY` (date, binary sha1, theorem/mutant counts) and
   keep the binary at `~/caselaw2/r9_bin/caselaw2_lean9`.
5. Further rules arrive as new sections of DESIGN9 (§5 joined gap, §6 New Jersey successor authority, §7 …) — the
   lead tells you by appending to `round9/agents/lean9/INBOX.md`; check it every ~15 minutes. For each: remove
   LEAN_READY while editing, state before prove, same gates, write LEAN_READY again. Do not start a rule the lead has
   not sent.
Final report: theorems before → after, mutants, audit check, regressions, v8e reproduction, LEAN_READY times, readings.
