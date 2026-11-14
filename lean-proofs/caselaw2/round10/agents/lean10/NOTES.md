# Round 10, agent `lean10`: notes

Times are from `date` (Git Bash; the clock prints "GMTST").

- 03:48 start. Read BRIEF, COMMON, DESIGN10 (all), round9/LEAN9.md, round9/agents/lean9/NOTES.md,
  round9/agents/shadow9/LEAN_REQUEST.md. `df -h /c`: 27 GB free.
- 03:48 backup to `round10/pre/` (round 9's file list: CaseLaw2/, CaseLaw2.lean, STATEMENTS.log,
  audit/statements.lock, fuzz/, ref/ copies, run_lean*.sh, runner/ sources, tools_caselaw2/ cue files, wsl/;
  `SHA1SUMS.txt`, 106 files). `round10/pre/CaseLaw2` = round-9 final state (LEAN_READY 03:32, binary 22bab5cd).
- 03:50 INBOX/lead: D10-5 (9-column history_remand.tsv, docket spans in B's and the target's text) and 03:52 D10-6
  (ref10's Q10-1..10 readings binding: two date forms, order court/date/docket/cue/tie, counters). The runner has no
  per-node docket (confirmed: decisions2 has none), so no QUESTIONS needed for the docket.
- 03:53 Read Certificate.lean (bridge section, round 9 sections), Run.lean (history loop, tables), Data.lean,
  Mutants.lean, gen_cues.py. Writing LEAN10.md §0/§1 before any code.
- 03:58 cue table + gen_cues.py round-10 keys (prefixes byte-identical); Certificate.lean round-10 section: definitions as LEAN10 §1.1, the 3 stated theorems + 5 helpers proved (no sorry), Certificate builds. Next: Data/Run loader + runner, Examples, Mutants.
- 04:03 Data.lean (RemandRow, optional history_remand.tsv, 9 fields; certNodes + B), Run.lean (remandTable, RemandTab.summary, history step: round-9 verdict then Cert.remandThen; zone counters on the round-9 verdict), Examples (60 new #guards, 441->501), Mutants (M75-M78, properties10, 4x4 diagonal, count guard (27,8,6,13,10,3,8,4,78)). Full build + runner green 04:03 (runner sha1 9bb60696). Next: audit check, lock, fixture, regressions.
- 04:05 audit check before lock: 280 theorems, 8 changes all new, 0 problems; locked 04:05 (reason
  agents/lean10/lock_reason_s4.txt -> wsl/lock_reason.txt; round 9's reason kept in round10/pre/wsl/); check after:
  280 / 0 changes / 0 problems.
- 04:07 fixture round10/fixtures/remand (make_remand_fixture.py, wsl/r10_remand_fixture.sh), 9-column version: green
  (15 rows; counters lines 14 / checked 13 / failed 9 / dup 1 / bad 2; without the table = round-9 verdicts, no
  counter; empty table = byte-identical to none).
- 04:07 INBOX/lead: D10-7 (§4 amendment 2: 12 columns, reason-case tie (c2) with an order span, tie (b) dropped) and
  D10-8 (§6 trialBridge, after §4). D10-7 changes the statement of my own round-10 theorem remandBridge_sound (locked
  04:05, before LEAN_READY): it will show as a changed round-10 statement in the next lock; against round 9's lock
  (round10/pre/audit/statements.lock) the round stays additions only. Writing LEAN10 §1b before code.
- 04:13 D10-7 built: cue keys remand_order_cue (renamed from my remand_reason_cue to ref10's Q10-11 name),
  remand_order_span_max 300, remand_tie_min 8; Remand +tie/oSha/oWindows/oStart/oStop; reasonTie (c2), tie (b)
  dropped; RemandRow 12 fields; M79 (tie string in B only) + property; 5x5 kill matrix = diagonal + (M78, reason-case
  property); count guard (27,8,6,13,10,3,8,5,79). Audit check: 281 theorems, 2 changes (new reasonTie_spec, changed
  remandBridge_sound); locked 04:12 (reason agents/lean10/lock_reason_s4b.txt); check after: 0 changes. Against
  round 9's lock (round10/pre): 0 removed, 0 changed, 9 added (axioms of the added: propext, Quot.sound,
  Classical.choice only). Full build green 04:12.
- 04:16 D10-9 read (ref10 Q10-11..17 binding for (c2) and §6). Fixture regenerated for 12 columns (18 rows; rows 16-18
  for (c2); row 7 docket-in-quote now remandTie). Scripts: wsl/r10_repro.sh (v9c / v8e reproduction from the verified
  base mirrors, run slot, deletes its output when identical), wsl/r10_r9zone_fixture.sh and
  wsl/r10_r9farimplicit_fixture.sh (copies that write nothing into round9/), wsl/r10_final.sh. Starting r10_final.
- 04:17 LEAN10 §6 (trialBridge) readings L10-20..27, definitions, 3 theorems, 4 mutants M80-M83 stated before code. r10_final running; §6 code goes into the tree only after r10_final ends (the regressions sync/build the tree).
- 04:22 r10_final: build OK, binary 43efb994 (~/caselaw2/r10_bin/caselaw2_lean10), audit check 281/0/0, all five fixtures green (remand 12-col, round-9 farimplicit + zone, round-8, round-7); regressions a a2 | b c and the v9c reproduction running since 04:17. §6 code drafted off-tree (scratchpad s6_cert.lean, s6_examples.lean, s6_apply.py), applied after the §4 gates.
- 04:22 SLIP (mine): s6_apply.py, meant for a staging copy, ran on the real Windows Lean tree at 04:22 (its LP override failed), while r10_final's regressions/reproduction run. Effect on the §4 gates: none — r7_lean_base.sh synced the WSL mirror only at its start (04:17) and run_lean.sh builds from the mirror; the reproductions use the copied binary 43efb994; no LEAN_READY exists, so no one else syncs/builds. The §4 state is kept in round10/agents/lean10/s6/lean-proofs (copied before the slip) and in the WSL mirror. The tree now holds the §6 code (it was going in next anyway); I do not sync the mirror until r10_final ends; §6 is iterated in a separate WSL copy ~/caselaw2/s6.
- 04:27 §6 built in the separate WSL copy ~/caselaw2/s6 (wsl/r10_s6build.sh): Certificate §6 (definitions as LEAN10 §6.1; trialBridge_no_claim, no_tbridge_table_no_change, trialBridge_sound + helpers checkByX_none, checkBy_cue_eq, checkByX_admitted, anchoredBy_admitted, tbridgeQuote_selfText, tbridgeQuote_some, trialFail_none, checkHistory8T_claimed) proved as stated; Examples 501->548 #guards, Mutants M80-M83 4x4 diagonal, count guard (27,8,6,13,10,3,8,5,4,83): full build green 04:25. v9c reproduced byte for byte with the §4 binary 43efb994 (04:24). Fixture round10/fixtures/tbridge (make_tbridge_fixture.py, wsl/r10_tbridge_fixture.sh) written; runs after r10_final.
- 04:31 r10_final FINAL rc=0 04:31: build, binary 43efb994, audit 281/0/0, 5 fixtures green, regressions a a2 (16 files) b c (15 files) byte-identical, v9c and v8e reproduced byte for byte. §4 ready: agents/lean10/LEAN_READY_s4, binary kept as ~/caselaw2/r10_bin/caselaw2_lean10_s4. round10/LEAN_READY not written yet (tree holds §6). Starting §6 gates (sync+build, lock, tbridge fixture, then r10_final again).
- 04:34 §6 gates: sync+build green 04:33 (binary in mirror), audit check 292 theorems / 11 changes all new / 0 problems; locked (reason agents/lean10/lock_reason_s6.txt); check after 292/0/0; vs round 9's lock: 0 removed, 0 changed, 20 added (axioms propext, Quot.sound, Classical.choice). Fixture round10/fixtures/tbridge green (16 rows each of data / data_noclaim / data_notable; counters lines 15 dup 1 bad 2; data_noclaim output = the frozen round-9 binary's). r10_final (with the tbridge fixture) started; the §4 log kept as r10_final_s4.log.
- 04:54 §6 r10_final FINAL rc=0 04:54 (binary e7e32592: audit 292/0/0, 6 fixtures green incl. tbridge, regressions a a2 b c byte-identical, v9c and v8e byte for byte). round10/LEAN_READY written 04:54 (copy agents/lean10/LEAN_READY_s6). Deleted my WSL side copy ~/caselaw2/s6; repro outputs were deleted by r10_repro.sh. Lean tree frozen; watching INBOX.
