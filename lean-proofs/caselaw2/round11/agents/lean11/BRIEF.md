# Agent `lean11` (round 11): the Lean checker for round-11 rules (single writer of the Lean tree)

Read `round11/DESIGN11.md` (all of it; §5 holds your sections) and `round11/agents/COMMON.md` (disk rule!). Folder
`round11/agents/lean11/` (NOTES.md, a line every 10 minutes). You are the ONLY writer of
`global-law-lean/lean-proofs/LegalProofs/CaseLaw2/**`, `tools/caselaw2/cues/` (cue_table.json, gen_cues.py),
`CueTable.lean`, `audit/statements.lock`, `STATEMENTS.log`, the runner sources and Lean-side run scripts (new ones as
`wsl/r11_*.sh`; `wsl/r11_run.sh` itself is `infra11`'s). Never edit the Python reference (`tools/caselaw2/ref/`, agent
`ref11`). Do not touch other sessions' Lean files (`LegalProofs/USTax/**` incl. `Entity*`, `USTax/Hunt/`,
`tools/hunt/`, `tools/taxcode/**`).
Model your work on round 10: `round10/LEAN10.md` (format: §0 readings, §1 definitions + theorems stated BEFORE
proving, mutants, §2 tables/loader/runner, §3 results), `round10/agents/lean10/NOTES.md` (backup list, build, lock,
audit, regression commands, how v9c / v8e were reproduced; the `wsl/r10_*.sh` scripts).

**Round 10 had a slip: a patch script meant for a scratch copy wrote into the real Lean tree while gates ran. Rule:
never patch the real tree while any gate (build, lock, audit, regressions, reproduction) is running; patch scratch
copies only by explicit absolute scratch paths; check `git -C <tree> status` / sha1s before and after each gate.**

Do:
1. Backup to `round11/pre/` (round 10's backup list, SHA1SUMS.txt) before any edit.
2. `round11/LEAN11.md` §0 (readings) and §1 (definitions, **theorem statements written into LEAN11.md and appended
   to STATEMENTS.log BEFORE any proof or runner code**, mutants) for each DESIGN11 §5 section; log the time the
   statements were fixed.
3. Implement, round-11 mode by presence (absent table / claim ⇒ round-10 output byte for byte). Prove the theorems
   as stated; existing statements unchanged; no `sorry`, no new axiom, no `native_decide`; one mutant per new rule,
   each killed by a stated property (diagonal guarded); `#guard` replays; a fixture under `round11/fixtures/`.
4. Lock + `audit.py check` green (0 changed, only additions); regressions a/a2/b/c (+ joined, bridge, zone, remand,
   tbridge fixtures) byte-identical; build the runner; **reproduce `round10/out/v10d`** with the new binary on
   `round10/stage/v10d` (via `wsl/r11_run.sh` with `R11BIN=` once `round11/INFRA_READY` exists), **`round9/out/v9c`**
   and **`round8/out/v8e`**: cmp every output table (summary timing lines excepted). Then write
   `round11/LEAN_READY` (date, binary sha1, theorem/mutant counts); keep the binary at
   `~/caselaw2/r11_bin/caselaw2_lean11`. `df -h /c` before every regression run (stop under 8 GB; delete your
   regression outputs once compared).
5. Further sections arrive in `round11/agents/lean11/INBOX.md` (check every ~10 minutes). For each: remove
   LEAN_READY while editing, state before prove, same gates, write LEAN_READY again.
Final report: theorems before → after, mutants, audit check, regressions, v10d/v9c/v8e reproduction, LEAN_READY
times, readings, any slip.
