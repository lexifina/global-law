# Round 9 log (clock times from `date`, GMT)

- 02:04 Lead started. Read ROUND8, DESIGN8, LEAN8 (skim), PROGRESS8, FREEZE8, LOG8, SEALED_LOG8, infra notes, research
  sources. WSL up (24 cores, 62 GB); round-8 binary ~/caselaw2/r8_bin/caselaw2_lean8 sha1 3b8d3e4d. Keep-alive sleep attached.
- 02:09 DESIGN9.md (§0–4, D9-1..3), agents/COMMON.md and 11 briefs written; launching agents infra9, fjc9, scdb9,
  calpart9, shadow9, state9, nj9, lean9, ref9 and the dataset agents bench_bh (Brace & Hall, CC0) and bench_songer
  (Songer TREAT) for the new fresh held-out key(s).
- 02:15 D9-4: ref9's Q9-1..10 answered (text-owner zones); lean9/ref9 INBOX.
- 02:18 calpart9 early zone table: 582,968 zones / 208,557 text-owner nodes; zone check would refuse 223 of 220,955 admitted v8e rows (200 straddle headmatter+majority/perCuriam in short 1920s-30s federal texts; 14 majority vs perCuriam; 9 syllabus quotes labelled majority). lean9 Q1/Q2 answered (= D9-4).
- 02:21 audit/READY. lean9 Q3 (all admitted verdicts are zone-checked) / Q4 (uniqueness without zones) answered, to lean9+ref9.
- 02:25 D9-5: state9 R-A implicitReject (§7) and R-B joinedFar (§5) accepted for the Lean (claim-gated); R-C withdrawn (3 new pairs). lean9/ref9 INBOX.
- 02:29 Fresh keys READY (dataset agents done; no model build scored): benchmarks/songer_treat (Songer 1925-96 +
  Kuersten-Haire 1997-2002, PRIORPUB-linked district decisions; 4,400 items, 2,391 linked; FJC-key overlaps excluded
  (910); units 1,544: h0 756 / h1 788; primary reversed/vacated 228) and benchmarks/brace_hall_state (Brace & Hall
  1995-98, CC0; 7,781 intermediate-appellate items, 3,685 linked; main units 3,322: h0 1,703 / h1 1,619; reversed/
  vacated 1,670). Both scored once after the freeze (v8e + frozen r9). round9/FRESH_KEYS.txt written. Songer: 2,383
  appellate decisions are Shepardized units (that key tested their own later history, not their treatment of the
  decision below) — kept; flagged for the user. REPORT.md not written by either (harness refused .md report files).
- 02:33 INFRA_READY (02:32; base reproduces v8e). D9-6 NJ option A (round9/nj/{adoption,succession}.tsv); D9-7 joinedFar without paragraph test; D9-8 part-zone data-side fixes, no Lean change. lean9/ref9 INBOX.
- 02:37 D9-9 fjc9 judge-form anchor cues accepted (§8, lowest priority); D9-10 shadow9 remandBridge evidence deferred.
- 02:37 fjc9: delta_W ready (rule W, wide anchor; 199 rows, 86 status-changing); r9f02 72/80 = 0.900 [0.815, 0.949],
  decoys 18/18 -> install (at the bar). Rule G (guard exception) r9f01 65/80 = 0.812 [0.713, 0.883] -> NOT installed
  (7 partial scope, 4 earlier ruling of the docket). (fjc9's message said "03:36"; the real time was 02:37.)
  scdb9: r9b01 judgment readings (census of 30 fresh rows) 26/30 = 0.867 [0.703, 0.947] — below the bar so far.
- 02:40 ref9 Q9-12..18 answered (lean9+ref9 INBOX).
- 02:43 shadow9 done: cert_remandtext_v2 (335 rows: 330 vacated, 5 reversed; rule: GVR order + unique caption-tied
  decision below 1-1,095 days before + remand decision on the same docket tied to the order). r9k01 79/80 = 0.988
  [0.932, 0.998] (corpus-weighted 0.964), r9k02 8/8; decoys 18/18, 4/4 -> INSTALL. shadow9_a: Shadow h0 412 -> 475/1,059
  = 44.9%, precision 91.5%; Shepardized dev 143 -> 145/254 (no new FP). Data gap: 281 h0 orders not in corpus (268 GVRs;
  2006-09 and 2020-25 order lists missing from the corpus).
- 02:47 infra9: stage9 --table done; nj_test (v8e + round9/nj tables, frozen binary) differs from v8e in exactly the 3 NJ rows (t8:4058244 noAuthority->ok; tw:3991335 witnessNoStanding->okRecognised; tw:4018149 disqualified->okRecognised), 9 status lines, findings -4 +20 (3 path-only). As predicted by nj9.
- 02:50 fjc9 r9f04 J class (judge-form anchors, §8; pop 176) 72/80 = 0.900 [0.815, 0.949], corpus-weighted 0.917
  (needs §8 in the Lean). calpart9 r9p03 PJR (rehear rows unlocked by PJ, whole class 14) 13/14, link+effect 14/14.
  state9: B joinedFar r9s01 whole class 52/52 [0.931, 1] but pack_1 decoys 2/6 (both auditors accepted the same 2
  known-wrong decoys) -> asked for a fresh auditor pair on pack_1 before install. A (implicitReject) r9s02 25/36 =
  0.694 [0.531, 0.820] -> not installed; v2 (no "no longer" family, intervening-cause filter) being read. A pool
  reaches 0 of the 147 h0 'nothing' pairs: the h0 implicit misses carry no rejection words naming X.
- 02:50 fjc9 done: delta_W (199 rows; r9f02 0.900) INSTALL; delta_J (444 rows, anchorWide claims; r9f04 72/80 =
  0.900, corpus-weighted 0.917) INSTALL once §8 is in the Lean; G r9f01 0.812 and G2 r9f03 67/80 = 0.838 NOT installed.
  fjc9_a (v8e + W): FJC h0 1,536 -> 1,549/2,832 = 54.7%, precision 90.4%, clean 6,079; dev unchanged. lean9 told: §8
  before §7.
- 02:53 scdb9 done: judgment readings (dfix 26 + j 19 + multi9 1) r9b01 whole class 26/30 = 0.867 [0.703, 0.947]; the
  post-hoc cut (C1-C3) scores 24/25 only on items already read -> NOT installed (D9-11: no fresh sample possible;
  the cut was designed on the audit's errors). Installed: a9 + r4w + wfix (4 rows, r9b02 4/4) + remove
  h6:6074206:1282434:reversed. Round-8 bug found: sc8sel.py NameError (WEAK) dropped 620 SC opinions' rows; fixed in
  scdb9's copy (2 rows survive selection). scdb9_b (all 50): SCDB h0 1,809 -> 1,819; the installed 4 rows add ~1-2.
- 02:53 state9 B: r9s01 pack_1 re-read by 2 fresh auditors: real 26/26 each; the same 2 contested decoys accepted
  again by all 4 pack-1 readers (labels contestable, not drift; pack_2 4/4 on other decoys). B joinedFar 52/52 =
  1.000 [0.931, 1.000] -> INSTALL with §5 (cert_far, 52 rows). A v2 (76 rows from 800 read) being audited.
- 02:56 lean9 Q5: parallel regressions allowed (≤ 3 runs, ≤ ~30 GB). §4 LEAN_READY ETA 03:08, batch 2 ETA ~03:25.
- 02:58 calpart9 done: PJ + PJ-V part-map rules (52,178 decisions' maps change; 40/40 changed decisions read right
  [0.912, 1]); final zone table 582,418 zones / 208,590 nodes (sha1 27465595), refuses 72 of 220,955 admitted v8e
  quotes after the re-cut (63 head-matter-only straddles + 9 syllabus quotes). PJT 23 rows r9p01 23/23 INSTALL; PJR 14
  rows r9p03 13/14, link+effect 14/14 INSTALL; PJH 36 rows r9p02 26/36 = 0.722 NOT installed; re-cut 137 rows (same
  conclusions as the replaced v8e rows, not separately audited) + 14 perCuriam relabels INSTALL. Frozen-binary effect:
  h0 keys unchanged; holdout negOrPartly 4,642 -> 4,653.
- 02:58 state9 A v2: fresh audit r9s03 whole class 72 rows (51 plain-cue + 21 needing §7): court itself rejects/departs
  from X 72/72 = 1.000 [0.949, 1.000]; 28 rows understate (auditors read overrule where the row says declinedToFollow:
  at-risk only, never overstates); decoys 12/16 (the same contested decoy again). INSTALL as at-risk only (D9-12);
  zero h0 effect by construction (the 147 h0 'nothing' pairs carry no such sentence).
- 02:58 v9a staged (v8e + shadow9 v2 + fjc9 W + scdb9 a9/r4w/wfix (+remove) + calpart9 PJT/PJR/recut (+remove, relabels) + state9 A plain + calpart9 zones + NJ tables). Rebuilding the zone table over every round-9 row (build_zones.py on v9a + delta_J + B + A claim -> round9/lead/zones_all) so new rows are zone-checked too.
- 03:05 §4 LEAN READY (03:05; lean9): theorems 245 -> 255 (0 changed), mutants 63 -> 66, audit check green,
  regressions a/a2/b/c byte-identical, round8/out/v8e reproduced byte for byte; binary 65bbc36d (~/caselaw2/r9_bin/
  caselaw2_lean9_s4). Real data v8e + zones: exactly calpart9's 223 rows ok -> partZone. LEAN_READY removed again for
  batch 2 (§5/§6/§7/§8). state9 done (A 51+21 rows installed per D9-12, B 52 rows with §5, C withdrawn).
- 03:09 v9a scored (frozen binary, zones ignored): FJC h0 1,536 -> 1,549/2,832 = 54.7%; Shadow 412 -> 475/1,059 =
  44.9% (precision 91.5%); SCDB 1,809 unchanged; state 17/132 unchanged; fresh dev 52/112 unchanged; Shepardized dev
  143 -> 145/254 (precision 93.5%, CLEAN 9,694 unchanged); holdout negOrPartly 4,642 -> 4,655; no-leak 0. v9a_s4 (round-9
  §4 binary + reference) running.
- 03:12 v9a_s4 (v9a with the §4 binary 65bbc36d + reference): zone_checked 221,076, zone_failed 72 (as
  calpart9 predicted), zone_missing 0, bad 0. Reference differential on real data: 0 disagreements in every table
  (status 525,876 keys, findings 320,805, certs 491,023, classes 37,396, ...) — the New Jersey class, open since
  round 5, is closed (D9-6 data rows). Scoring v9a_s4.
- 03:13 v9a_s4 scored: the zone check costs FJC h0 1,549 -> 1,547 and SCDB 1,809 -> 1,808 (rows whose only
  evidence is head matter / syllabus; refused as intended); everything else = v9a. v9b staged (v9a + fjc9 delta_J +
  state9 B/cert_far + A/cert2_claim), waiting for the batch-2 binary.
- 03:23 INCIDENT: C: full (67 MB free at 03:21; other sessions' writes plus round-9 stage/run copies), WSL Ubuntu root went read-only (lean9 Q6). Freed round-9 intermediates only: 8 finished agents' stage folders (MANIFEST/TABLES kept in round9/lead/deleted_stages/) and 9 intermediate out folders (RUN.txt/summary kept in lead/deleted_out/); results/ untouched.
- 03:25 WSL Ubuntu restarted: wsl --terminate Ubuntu (only idle sleeps / one wait loop were running; the root fs was read-only), first start failed (E_FAIL step 2), wsl --shutdown (docker-desktop was already stopped) then start: read-write. Removed finished variants' WSL data dirs/difftest dirs. Keep-alive re-attached. lean9/ref9 told to resume.
- 03:26 ref9: its v9a differential (as ref9_v9a, §4 binary) also 0 disagreements; NJ (frozen binary) 0. Caution: ref9's first attempt collided with my v9a run (shared difftest dir) at ~03:10 and may have copied §4-binary output into round9/out/v9a; v9a's figures are interim only (the reported attribution uses v9a_s4 and v9b).
- 03:27 Coordinator freed ~15 GB of non-frozen round-5..8 intermediates (list round9/lead/coordinator_cleanup_*.txt). Lead policy from now: delete each round-9 variant's stage/out once scored and superseded (keep base, final candidate, frozen); check df before each Lean run (stop under ~8 GB). v9a stage/out deleted (results kept).
- 03:31 v9b (batch-2 binary 22bab5cd + reference): 0 disagreements in every table (status 526,310 keys, certs
  491,540, findings 321,139, classes 37,448). h9 1,107 ok / 26 noAuthority; t9 98 ok / 48 joinedFarWindow / 1
  noAuthority: state9's B rows carry no window covering the gap (DESIGN9 §5) -> state9 asked to add gap windows.
  Scores: FJC h0 1,564/2,832 = 55.2% (J class +17), Shadow 475, SCDB 1,808, state 17; Shepardized dev 145/254
  (93.5%); fresh dev 52/112; holdout history 5,033/6,121. Burned old lists move DOWN: SCDB explicit 146 -> 144, with
  recognised 178 -> 177; CRS 167 -> 164 / 199 -> 198: the zone check refuses the 3 treatments rows that quote the
  Supreme Court syllabus (reporter's words, not the Court's), which these lists counted. v9a_s4 stage/out deleted.
- 03:32 batch-2 LEAN READY (03:32): binary 22bab5cd; theorems 245 -> 272 (0 changed), mutants 63 -> 74, audit green, regressions a/a2/b/c byte-identical, v8e reproduced. state9 B/cert_far2 (gap windows) ready; v9c staged (= v9b with cert_far2); running with 22bab5cd + reference.
- 03:34 D9-13: zone-failing non-ok rows feed no findings (Lean right; reference aligns; synthetic only).
- 03:36 v9c (final candidate; binary 22bab5cd + reference): h9 1,107 ok / 26 noAuthority; t9 144 ok / 3
  noAuthority (B: 49 of 52 admitted, 3 noAuthority); zone_failed 72; reference differential 0 in every table.
  Scores (h0): FJC 1,564/2,832 = 55.2%; Shadow 475/1,059 = 44.9%; SCDB 1,808/2,407 = 75.1%; state 18/132 = 13.6%
  (recall_any 20). Shepardized dev 145/254, precision 93.5%, CLEAN 9,694/9,704; fresh dev 52/112 (attributed 82);
  holdout alsoInFeed negOrPartly 1,068/2,640, holdoutOnly 660/6,734; no-leak 0. NJ exposure check: of 25 admitted
  rows touching a decision filed under the old Supreme Court with the Court of Errors and Appeals' vote roll, only
  tw:4018149 changed this round (the known one; its status is true either way). v9b stage/out deleted.
- 03:36 FREEZE.md for v9c (190 file hashes incl. the fresh keys' score.py/key/MAPPING/READY; freeze9 --check ok). Running score_sealed9.sh v9c once.
- 03:37 Sealed run REFUSED by its own freeze check (nothing scored): round9/agents/ref9/make_r9.py (ref9's universe generator, hashed as agent code) changed after the freeze while ref9 aligned the reference to D9-13. No build file changed. ref9 told to put further edits in new files; FREEZE.md will be re-written (old one kept as FREEZE_refused_0336.md).
- 03:37 FREEZE.md re-written (same 190 files; only make_r9.py's hash differs from the refused one); --check ok. Running the sealed pass.
- 03:39 SEALED (once, 03:37): round-8 keys h1, second use (v8e -> v9c): FJC 1,566 -> 1,601/2,864 = 55.9%; Shadow
  426 -> 508/1,093 = 46.5% (precision 92.7%); SCDB 1,810 -> 1,812/2,400 = 75.5%; state 11 -> 11/142. Fresh keys, first
  use (v8e -> v9c): Songer 82 -> 94/228 = 41.2% [35.0, 47.7] (h0 36 -> 43, h1 46 -> 51; precision 96.9%); Brace & Hall
  835/1,670 = 50.0% unchanged (precision 93.1%). Fresh sealed (5th use) 77/32/57 -> 76/31/56; Shepardized sealed (4th
  use) 123 -> 125/252, precision 92.6%. Nothing re-tuned. ROUND9.md written; live page section 97 (Done) and the
  Round 9 row (Done); make_overturned.py rebuilt.
- 03:44 ref9 final: synthetic differential (kept 9, sweep 20, probe 10, fuzz 10, 534 earlier universes) — every round-9 rule agrees; only the known round-5 W witness universes differ; 534 byte-identical to round-8 reference output without round-9 tables. Real data v9a/v9b/v9c 0. Round closed.
