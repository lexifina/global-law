# Round 8, agent `lean8`: notes

Times are from `date` (Git Bash; the clock prints "GMTST").

- 00:47 start. Read DESIGN8 (all), COMMON, BRIEF, LEAN7, round-7 lean NOTES, orderdock LEAN_REQUEST (DESIGN8 §4 is
  the contract where they differ).
- 00:48 backup to `round8/pre/` (CaseLaw2/, CaseLaw2.lean, cues/{cue_table.json,gen_cues.py}, ref/ files,
  reader/cue_table.py, fuzz/, audit/statements.lock, STATEMENTS.log, run_lean.sh, runner sources, wsl/;
  `SHA1SUMS.txt`, 90 files). `round8/pre/CaseLaw2` = round-7 final state (differs from `round7/pre` only by round 7's edits).
- 00:57-01:02 LEAN8.md §0 (readings L8-1..16) and §1 (definitions, 6 theorems, mutants) before code; D8-5 (§5
  anchorWide) received 00:56 and bundled; D8-9 (step 5b bridgeChain) received 01:01 and stated (01:02) before code.
- 01:00 cue table: bridge_cue, bridge_max_len, anchor_wide appended (later old_circuit); gen_cues.py gets R8 lists and
  `--skip-ref` (ref/ is ref8's; ref/cue_table.py left untouched); CueTable.lean / reader/cue_table.py prefixes
  byte-identical to round8/pre.
- 01:07 Certificate.lean round-8 section built: all §4/§5 theorems proved (no sorry).
- 01:12 Examples (bridge + anchorWide #guards) and Mutants (M54-M61, properties8, diagonal) green.
- 01:13 D8-12 (§6 oldCircuit) received; LEAN8 §1.5 stated 01:13 before code; Exec/Verdicts.lean histPower8,
  oldCircuit_no_claim / oldCircuit_sound / histPower8_keeps proved; M62/M63.
- 01:18 full build (`wsl/r8_lean.sh all`: LegalProofs.CaseLaw2, Run, runner) green. M63's property tests the rule id
  (M15 "no power check" subsumes M63 on the truth value).
- 01:19 fixture round8/fixtures/bridge (make_bridge_fixture.py; 20 history rows, 17 bridge lines, 7 claim lines) green
  with and without the round-8 tables (wsl/r8_bridge_fixture.sh).
- 01:20 audit check before lock: 245 theorems, 25 statement changes all `new`, 0 problems. Locked (reason in
  wsl/lock_reason.txt). vs round8/pre lock: 220 -> 245, removed 0, changed 0, added 25.
- 01:21 wsl/r8_final.sh started (log agents/lean8/r8_final.log): build OK, runner sha1 3b8d3e4d45fb…, audit check
  after lock 245 / 0 changes / 0 problems, round-8 fixture rc=0, round-7 fixture rc=0; regressions a a2 b c running
  from 01:21:59, then the v3 reproduction (stage lean8_v3 = hard-linked copy of round8/stage/base, R8BIN).
- 01:38 r8_final.sh FINAL rc=0: regressions a a2 b c byte-identical; round7/out/v3 reproduced byte for byte
  (round8/out/lean8_v3, summary timing lines aside). LEAN8.md §1.6, §2-4 written. round8/LEAN_READY written 01:38.
  Scratch left: round8/stage/lean8_v3 (hard links to stage/base), round8/out/lean8_v3.
