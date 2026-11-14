# Agent `lean8` (round 8): the Lean checker for round-8 rules (single writer of the Lean tree)

Read `round8/DESIGN8.md` (all of it; §4 is your first rule) and `round8/agents/COMMON.md`. Folder:
`round8/agents/lean8/` (NOTES.md). You are the ONLY writer of `global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`,
`tools/caselaw2/cues/` (cue_table.json, gen_cues.py), `CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`, the
runner sources and the Lean-side run scripts. Never edit the Python reference (`tools/caselaw2/ref/`, agent `ref8`).
Model your work on round 7: `round7/LEAN7.md` (format: §0 readings, §1 definitions + theorems stated BEFORE proving,
§1.4 mutants, §2 tables/loader/runner, §3 results), `round7/agents/lean/NOTES.md` (backup list, build, lock, audit,
regression commands).

Do:
1. Backup to `round8/pre/` (same file list as round 7's `round7/pre/`, SHA1SUMS.txt) before any edit.
2. `round8/LEAN8.md` §0 (your readings of anything DESIGN8 §4 leaves open — write them down, ask the lead only if a
   reading changes an effect) and §1 (definitions, theorem statements, mutants) before code.
3. Implement DESIGN8 §4 (`history_bridge.tsv`, `checkBridge`, cue list `bridge_cue`, `bridge_max_len`), round-8 mode by
   presence. Prove the theorems as stated; existing statements unchanged; no `sorry`, no new axiom, no
   `native_decide`; one mutant per new rule, each killed by a stated property; `#guard` replays.
4. Lock + `audit.py check` green (0 changed, only additions); fixture(s) for bridge rows; the round-4/5/6/7 regressions
   (a/a2/b/c, `fixtures/joined`) byte-identical; build the runner; **reproduce `round7/out/v3`**: stage `base`
   exists (`round8/stage/base`); run `bash wsl/r8_run.sh base` WITH the new build (not NOBUILD; you may write
   LEAN_READY temporarily for that run or use R8BIN with your fresh binary) into a scratch name and cmp every output
   table with `round7/out/v3` (summary.tsv timing lines excepted). Then write `round8/LEAN_READY` (date, binary sha1,
   theorem/mutant counts). Tell `ref8`'s readers nothing about the Lean; the lead runs the differential.
5. Further rules may arrive from the lead by message while you work (other agents' LEAN_REQUESTs); add them to
   LEAN8.md the same way (state before prove). Do not start a rule the lead has not sent.

Final report: theorems before → after, mutants, audit check, regressions, v3 reproduction, LEAN_READY time, any
reading the lead must know.
