# Round 9, agent `lean9`: notes

Times are from `date` (Git Bash; the clock prints "GMTST").

- 02:10 start. Read BRIEF, COMMON, DESIGN9 (all), round8/LEAN8.md, round8/agents/lean8/NOTES.md.
- 02:12 backup to `round9/pre/` (round-8 file list: CaseLaw2/, CaseLaw2.lean, STATEMENTS.log, audit/statements.lock,
  fuzz/, ref/ copies, run_lean*.sh, runner/ sources, tools_caselaw2/ cue files, wsl/; `SHA1SUMS.txt`, 92 files).
  `round9/pre/CaseLaw2` = round-8 final state.
- 02:13 v8e history rows: all 184,798 quote the acting node's text (0 selfText), so L9-1's selfText reading has no
  v8e effect.
- 02:15 LEAN9.md §0 (readings L9-1..10) and §1 (definitions, 4 theorems + helpers, 3 mutants M64-M66, fixture plan)
  written before code. QUESTIONS.md Q1 (witness rows use W's zones; selfText rows unchecked), Q2 (zone gates text
  check / doctrine table / laterCourtSays evidence); continuing on these readings.
- 02:18 Certificate.lean round-9 section (Zone, nodeZones, zoneThen, zoneR, checkHistory9/Treatment9/Recognised9) built; all 4 stated theorems + 6 helpers proved as stated (no sorry). Next: Data/Run loader + runner.
- 02:19 INBOX read (D9-4, answers 02:18): L9-1 now text owner incl. target for selfText; L9-5 bad lines do not poison; L9-6 doctrine table without zones (D9-4 (2)); L9-9 counter names. Q3 (admitted = ok), Q4 (02:18 answer vs D9-4 on doctrine table) written; following D9-4.
- 02:27 Data.lean (ZoneRow, optional part_zone.tsv), Run.lean (ZoneTab, text owner zones, checkHistory9/checkTreatment9/checkRecognised9, zone-gated textOk/recOk/treatOkText, counters) built; Examples (round-9 #guards) + Mutants (M64-M66, properties9, diagonal guards) written; full build running. INBOX: calpart9 real zones at agents/calpart9/zone_delta/part_zone_delta.tsv.
- 02:29 fixture round9/fixtures/partzone (make_partzone_fixture.py: j/ from round-7 joined fixture, b/ from round-8 bridge fixture; data, data_nozone, data_emptyzone; 5 designed refusals) + wsl/r9_zone_fixture.sh written; stage round9/stage/lean9_z = v8e + calpart9 zone_delta (582,968 zone lines) staged; waiting on full build.
- 02:31 INBOX 02:21 (Q3 yes: every admitted verdict; Q4: D9-4 (2) stands) and 02:25 (D9-5: §5 joinedFar + §7 implicitReject after §4 gates) read.
- 02:34 full build green (Examples round-9 #guards, Mutants M64-M66 diagonal + count guard (27,8,6,13,10,3,66)). Zone fixture green (j: 4 refusals + counters; b: 1 refusal; without / with empty part_zone.tsv = the earlier fixtures' out/ byte for byte). Audit check before lock: 255 theorems, 10 changes all new, 0 problems. Real-data run lean9_z (v8e + calpart9 zones) running.
- 02:38 LEAN9.md §5 (batch 2: joinedFar §5, implicitReject §7): readings L9-11..20, definitions, 7 theorems, mutants M67-M71 stated before any batch-2 code. Real-data run lean9_z still running.
- 02:39 audit lock (02:39): 245 -> 255, 10 added, 0 changed/removed (reason wsl/lock_reason.txt). wsl/r9_final.sh started (log agents/lean9/r9_final.log): build, binary ~/caselaw2/r9_bin/caselaw2_lean9, audit check, zone fixture, round-8/7 fixtures (r9_r8fixture.sh / r9_r7fixture.sh: copies that write nothing back), regressions a a2 b c, v8e reproduction on stage lean9_base (hard links to round9/stage/base). Lean tree frozen until it ends (batch 2 waits).
- 02:43 r9_final so far: build OK, binary sha1 65bbc36d…, audit check 255 / 0 changes / 0 problems, zone fixture rc=0, round-8 fixture rc=0, round-7 fixture rc=0; regressions running since 02:41. Batch 2 prepared off-tree (scratch Lean text, agents/lean9/patch_batch2.py cue table + generator, patch_batch2_run.py runner), applied only after r9_final ends.
- 02:44 real-data run lean9_z (v8e + calpart9 zone_delta; pre-lock binary of the same source, runner sha1 65bbc36d): zone_nodes 208,557, zone_lines 582,968, bad nodes 0, bad rows 0, checked 220,452, failed 223, missing 0. certs: exactly 223 rows ok -> partZone (220 history, 3 treatments; both rule sets), every other verdict as v8e; the 223 ids = calpart9 refused.tsv exactly. rows_admitted 220,452 -> 220,229. Downstream: classes 3 lines, findings 528 diff lines, status 594 diff lines; status_lines, splits, horty identical. Output round9/out/lean9_z.
- 02:48 INBOX 02:33 (D9-6 §6 NJ: data-only, theorems + guards + mutants), 02:37 (D9-9 §8 judge-form anchorWide cues, lowest priority), 02:40 (ref9 Q9-12..18 rulings; D9-7 drops the paragraph test) read. LEAN9 §5 revised 02:46 before any batch-2 code (no joinedFarPara; far order gap/window/key/anaphor; mutants M67 key, M68 bound, M69 anaphor). r9_final still in regressions.
- 02:49 LEAN9 §6 (NJ, D9-6) stated before code: readings L9-21..24, theorems adoptedSameTier_power / adopted_lowerTier_noPower, 6 guards on njEnv, mutants M72 mutAdoptAnyTier, M73 mutNoAdoptPower. r9_final: regression (a) byte-identical so far.
- 02:51 batch-2 code (§5/§7/§6) fully drafted off-tree in the scratchpad; waiting for r9_final (regression a byte-identical; a2 running). The Windows Lean tree is not touched while the regressions run (run_lean.sh rebuilds the runner from the mirror).
- 02:55 INBOX 02:50: timeline (LEAN_READY §4 asap; batch by ~03:20; freeze 03:45) and priority §5, §6, §8, §7 last. Batch 2 (§5+§7+§6+§8) assembled in a staging tree round9/agents/lean9/b2/tree (assemble_batch2.py, patch_batch2*.py) and built in a separate WSL copy ~/caselaw2/b2/lean-proofs (wsl/r9_b2build.sh): Certificate (far/implicit/§8) + AuthorityThms (NJ) proved; full build running. §8 added: LEAN9 §8 to be written.
- 02:56 Q5 to the lead (QUESTIONS.md): batch-2 gates ETA ~03:40 sequential; asked whether 3 parallel runs are allowed.
- 02:57 batch 2 staging: full build green (Examples 441 #guards, Mutants 20 #guards incl. the 8x8 batch-2 diagonal and count guard (27,8,6,13,10,3,8,74)); staging runner (sha1 22bab5cd, wsl/r9_b2runner.sh) passes the batch-2 fixture round9/fixtures/farimplicit (11 rows: ok / joinedFarKey / joinedFarGap / joinedFarWindow / near ok / no-claim joinedRelation; implicit ok / implicitBadKind / questioned ok / partNotMajority / no-claim noCue; noclaim data = round-8 verdicts); soft target stays good, findings atRisk soft only. Stage lean9_nj (v8e + round9/nj adoption/succession) prepared.
- 02:59 INBOX 02:56 (Q5): parallel runs allowed (<= 3, PAR=4, < 30 GB). Started the §4 v8e reproduction now in parallel (stage lean9_base4 = hard links to round9/stage/base, PAR=4, log agents/lean9/v8e_s4.log) while r9_final runs regression c; wsl/r9_final2.sh (batch 2: regressions as two parallel pairs + v8e, PAR=4) prepared.
- 03:00 §4 regressions a, a2, b, c: every output file byte-identical (certs 68f6fb621957 / status 96888c8b4381 for a; c certs 0c9ef2f16764). v8e reproductions running (lean9_base4 PAR=4 started 02:59; r9_final's own lean9_base from 03:00).
- 03:02 LEAN9 §9/§10 (§4 as built, results) appended; LEAN_READY text drafted; apply_batch2.sh (copy staging -> tree) ready. Waiting for the v8e reproduction (lean9_base4).
- 03:04 v8e: all 110 anchorWide rows are ok in v8e, so §8's extended list cannot change v8e. §4 binary also kept as ~/caselaw2/r9_bin/caselaw2_lean9_s4 (65bbc36d).
- 03:05 r9_final.sh FINAL rc=0 03:04:47: v8e reproduced byte for byte (round9/out/lean9_base: certs 1a60f798de83 … summary timing aside). round9/LEAN_READY written 03:05 for §4 (copy agents/lean9/LEAN_READY_s4); binary 65bbc36d at ~/caselaw2/r9_bin/caselaw2_lean9 and caselaw2_lean9_s4.
- 03:05 round9/LEAN_READY removed for batch-2 editing (§5+§6+§7+§8 into the tree). The §4 ready text stays in agents/lean9/LEAN_READY_s4; the §4 binary stays at ~/caselaw2/r9_bin/caselaw2_lean9_s4 (use NOBUILD=1 R9BIN=…).
- 03:06 batch 2 applied to the tree (apply_batch2.sh: 6 Lean files, cue table, generator, reader cue_table.py; gen --check current), mirror build 03:05 (reusing the staging .lake; runner rebuilt), audit check 272 theorems, 17 changes all new, 0 problems; locked 03:06 (reason agents/lean9/lock_reason_b2.txt -> wsl/lock_reason.txt). r9_final2.sh starting.
- 03:06 r9_final2: build OK, binary sha1 22bab5cdc712… (= the staging runner, deterministic); audit check running; LEAN9 §11 (batch 2 as built) appended.
- 03:07 r9_final2: audit check after lock 272 theorems, 0 changes, 0 problems; fixtures running.
- 03:07 second §4 v8e reproduction (round9/out/lean9_base4, PAR=4, same binary 65bbc36d) also byte-identical. Batch-2 fixture green in r9_final2 (11 rows, no-claim = round 8, soft target good).
- 03:07 §6 real data (lead's round9/out/nj_test, v8e + NJ tables, frozen binary; the rule is data only): exactly nj9's 3 rows change (t8:4058244… noAuthority->ok; tw:3991335… witnessNoStanding->okRecognised; tw:4018149… disqualified->okRecognised).
- 03:08 r9_final2: all four fixtures green; parallel regressions (a a2 | b c, PAR=4) + v8e reproduction (lean9_base, PAR=4) started 03:08.
- 03:08 NOTE for lead/ref9: ~/caselaw2/r9_bin/caselaw2_lean9 is the batch-2 binary (sha1 22bab5cd…) since 03:06 (r9_final2 copies it there; LEAN_READY for batch 2 not yet written); the §4 binary is ~/caselaw2/r9_bin/caselaw2_lean9_s4 (65bbc36d…). Without joinedFar / implicitReject claims and with v8e's anchorWide rows the two binaries give the same output (claim-gated); r9_run.sh records the sha1 in RUN.txt.
- 03:09 staged round9/stage/lean9_far = v8e + state9 B/cert_far (52 joinedFar rows) + A/cert2_claim (21 implicitReject rows), to run with the batch-2 binary after r9_final2 (expected: all 73 admitted). r9_final2's v8e run waits for a slot (v9a / v9a_s4 runs of others active).
- 03:10 r9_final2 v8e reproduction got a run slot 03:10; regressions running.
- 03:11 wsl/r9_far_run.sh queued (runs lean9_far with the batch-2 binary once r9_final2's v8e run ends; at most 3 of my runs at once).
- 03:14 r9_final2 parallel stage still running (regressions a, b and the v8e run at PAR=4 on a loaded machine; load ~13).
- 03:17 batch 2: regressions a and b byte-identical; v8e reproduction with the batch-2 binary 22bab5cd: every file byte-identical (round9/out/lean9_base); a2 and c running; lean9_far starting.
- 03:21 regressions a2 and c running (machine load ~18); far run in progress. ETA batch-2 LEAN_READY ~03:25.
- 03:21 **ALERT: C: is full (0 MB free at 03:21; 67 MB after I deleted my duplicate output round9/out/lean9_base4) and the
  WSL root filesystem has gone READ-ONLY** (rm in ~/caselaw2 fails "Read-only file system"; r9_final2 can no longer write
  its logs). Every Lean run in WSL (mine, ref9's v9a, the lead's v9a_s4) is affected. I deleted only my own duplicate
  output; I have not touched anyone else's files and have not restarted WSL. Batch-2 gates done before the failure:
  build, audit 272/0/0, all four fixtures, regressions a and b byte-identical, v8e reproduction byte-identical with the
  batch-2 binary 22bab5cd (round9/out/lean9_base). Not finished: regressions a2 and c (the same code path as a / b with
  empty round-7 tables and round-4 tables). LEAN_READY for batch 2 NOT written.
- 03:21 stopped my own runs (r9_final2, r7_lean_base a a2 / b c, r9_far_run lean9_far): they cannot write on the read-only WSL filesystem. Waiting for the lead (Q6).
- 03:25 C: has 3.4 GB free again and WSL was restarted (up 0 min at 03:25; writable). Binaries intact (caselaw2_lean9 and the mirror runner 22bab5cd). Rerunning the two cut-off batch-2 regressions a2 and c in parallel (wsl/r9_final2_rest.sh, PAR=6, log agents/lean9/r9_final2_rest.log).
- 03:26 INBOX 03:26 (Q6 answer) read. Deleted my WSL scratch (~/caselaw2/b2, difftest/data_r9_lean9_{base4,z,far}, run_lean9_* copies); C: 5.1 GB free. a2/c rerun in progress.
- 03:26 lead 03:26: skip lean9_far (v9b with binary 22bab5cd holds the state9 claim rows, the judge-form rows and NJ tables; lead reports their verdicts).
- 03:30 a2 / c reruns in their second shard wave.
- 03:32 regressions a2 and c byte-identical with the batch-2 binary (REST rc=0 03:31:51). All batch-2 gates pass: round9/LEAN_READY written 03:32 (section 4 + batch 2; binary 22bab5cd at ~/caselaw2/r9_bin/caselaw2_lean9; §4's 65bbc36d at caselaw2_lean9_s4). LEAN9 §12 updated.
