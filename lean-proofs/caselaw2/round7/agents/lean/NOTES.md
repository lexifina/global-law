# Round 7, agent `lean`: notes

Times are from `date` (Git Bash; the clock prints "GMTST").

- 22:43 start. Read DESIGN7, LEAN6, DESIGN5, DESIGN6.
- 22:43 backup to `round7/pre/` (CaseLaw2/, CaseLaw2.lean, cues/{cue_table.json,gen_cues.py}, ref/cue_table.py,
  reader/cue_table.py, audit/statements.lock, STATEMENTS.log, run_lean.sh, run_lean_wsl.sh, wsl/, runner sources;
  `SHA1SUMS.txt`, 85 files).
- 22:59 LEAN7.md section 0 (readings L7-1..12) and section 1 (definitions, 22 theorem statements, 13 mutants) written before any code.
- 23:16 lead ruling D7-8 (message): anaphor list extended with round7/agents/antecedent/anaphor_proposal.json (39 -> 70 phrases; every proposal phrase in it); regenerated, earlier lists unchanged.
- 23:21 lead ruling D7-9: order_line entries 'a ... b' = hasInOrder (Cert.orderLineHit); 6 entries added (certDenied, reviewDismissed); regenerated. Full build (before D7-9) green incl. runner.
- 23:22 rebuild after D7-9 green; lead ruling D7-10: antecedent needs a plain kind cue also on operative rows (as implemented, L7-13).
- 23:28 fixture round7/fixtures/joined green (39 cert lines, counters, classes; without round-7 tables = round-6 checks, no counter). audit lock: 183 -> 220 theorems (22 stated + 15 helpers), 0 changed / 0 removed vs round7/pre lock; audit check after lock: 0 changes, 0 problems. Guards: Examples 223 -> 308, Mutants 8 -> 11; mutants 40 -> 53; properties 41 -> 54. Regressions (wsl/r7_lean_base.sh, log agents/lean/r7_lean_base.log) running.
- 23:34 regression (a) round-6 final2: all 8 files byte-identical (certs 68f6fb621957, status 96888c8b4381 = FREEZE hashes).
- 23:41 lead ruling D7-12: doctrine_reject 18->35, doctrine_tie 25->31 (append); regenerated on Windows; rebuild + reruns after the running regression.
- 23:43 regressions before D7-12 all byte-identical (a, a2, b, c; rc=0): log r7_lean_base_before_D7-12.log. Starting the D7-12 rebuild + audit + fixture + regressions (log r7_final.log).
- 00:00 final run after D7-12 green (build, audit check 220/0 changes/0 problems, fixture, regressions a a2 b c byte-identical; log r7_final.log). LEAN7.md sections 0-4 written. LEAN_READY created.
