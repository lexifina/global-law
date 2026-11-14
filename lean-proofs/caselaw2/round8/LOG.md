# Round 8 log (clock times from `date`, GMT)

- 00:11 Round 8 started. Read ROUND7, DESIGN7, PROGRESS7, FREEZE7, ROUND6, improvement plan, benchmarks CONTRACT and
  the four new keys' SOURCE/MAPPING/DISAGREEMENTS. Round-6 h0 figures (benchmarks/*/results/round6.h0.json, both
  builds already public): FJC recall 1,418/2,832 = 50.1%; SCDB disposition recall 1,488/2,407 = 61.8%; Shadow Docket
  recall 154/1,059 = 14.5%; state tables recall 11/132 = 8.3%.
- 00:13 DESIGN8.md (binding rules, D8-1, D8-2), PROGRESS.md. Phase A agents launched (10).
- 00:18 Launched 11 agents (briefs in agents/<name>/BRIEF.md, common rules agents/COMMON.md): infra, audit8, ownact,
  orderdock, rehear8, multicase, state8, contradict, fjc8, scdb8 (added: FJC and SCDB h0 diagnosis — the two new
  keys with the largest n), doctrine8 (opportunity first). Lean8/ref8 start when a LEAN_REQUEST arrives. Move 8
  (covered-pair statements) held until reader capacity frees up. WSL kept attached (sleep 21600).
- 00:22 doctrine8 done: dominance adds ≤ ~15 rows at the loosest threshold (3 ties, 2× runner-up; ~5 new
  pairs after base overlap) — under the 25-row bar; not built, no Lean change. Open alternative (not built): resolve
  the label by the court's own strict tie (605 sentences, 69 accepted, ~57 est. rows, ~half look real in 12 read);
  breaks corpus-wide label uniqueness — decision for a later round.
- 00:27 audit8 done: round8/audit/ tools (make_packs8 incl. two-quote pair form, score_audit8, decoy pools treat
  150 wrong / 794 right, history 332 / 1,570), selftest PASS, dry run r8x01 19/20 (decoys 3/3, matched round-7
  readers). HOWTO.md; READY 00:27. Contradict uses run name r8c01 (folder names are shown to auditors).
- 00:31 contradict done: 476 pairs still live in v3 (449 Lean-admitted new rows); rule "final judgment line decides"
  selects 245 replacements. Blind pair audit r8c01 (40 + 6 decoys, two opus readers, agreement 46/46, decoys 12/12):
  new row right 27/40 = 0.675 [0.520, 0.799]; base right 7/40; where only one is right new wins 27/34 = 0.794.
  Failures: mixed judgments (final line is the "affirmed" half), nested dispositions. NOT INSTALLED (no sub-rule
  reaches 0.90). bench_h0/READY 00:29.
- 00:29 v3 h0 baseline: FJC recall 1,418/2,832 = 50.1% (= round 6), precision 90.0%, clean 97.7%; Shadow Docket 156/1,059 = 14.7%, precision 82.5%; SCDB disposition 1,681/2,407 = 69.8%, precision 97.5%, clean 97.6%; state tables 13/132 = 9.8% (any 15/132).
- 00:33 INFRA_READY (certify8, stage8, r8_run.sh, base reproduction).
- 00:37 infra done: base reproduction byte-identical (7 output tables; summary differs only in timing lines);
  frozen v3 checker ~/caselaw2/r8_bin/caselaw2_r7v3 sha1 3270d7f3…; h0 shadow verified against round6/round4 h0
  results (Shadow Docket: node-level half, 509 placeholder rows, 562 h1-half items kept inside h0 nodes as the scorer
  pools by node); score8.sh base = round-7 v3 dev summary line for line; sealed tooling written, not run; live page
  row + section 96_round8.html. Incident: processes.json empty < 1 min during its edit, restored from pre copy.
- 00:48 orderdock LEAN_REQUEST (bridge evidence through a third text's subsequent-history clause) accepted as D8-3,
  spec DESIGN8 §4 (docket evidence dropped: SC orders carry only their own docket). lean8 + ref8 launched;
  orderdock asked for a bridge delta writer (certify_bridge8.py).
- 00:52 rehear8 done: G grant orders 299 rows (audit r8h01 link+kind 76/80 = 0.950 [0.878, 0.980], link+effect 77/80),
  N no-date docket 368 rows (r8h02 72/80 = 0.900 [0.815, 0.949], link+effect 74/80); decoys 18/18 each; all 667 Lean
  ok (NOBUILD). Shepardized dev NEG 140 → 141 (with reinstated) / 143 (without); D8-6 keeps reinstated (no key
  fitting). Shadow h0 156 → 159. INSTALL both (cert_grant, cert_nodate).
- 00:52 scdb8 LEAN_REQUEST (wider anchor cues) accepted claim-gated as D8-5 (DESIGN8 §5); sent to lean8, ref8, scdb8.
- 00:58 orderdock (interim message): bridge status rows r8k01 79/80 [0.932, 0.998]; bridge certDenied/other r8k03 79/80;
  remandcap r8k04 32/32 [0.893, 1]; lists v1 r8k02 68/80 FAIL → v2 (caption tie-check + consolidated scope) fresh
  r8k05 80/80 [0.954, 1]. orderdock_a h0 Shadow Docket recall 156 → 462/1,059, precision 82.5 → 91.1%. D8-7: bridge
  lines strict (§4 as written, 919 rows); no "own page" index lines (circular).
- 00:58 ownact done: 19,584 unread items re-anchored; 9,787 with no powered candidate and 122 already admitted set aside;
  9,675 in 121 packs; 106 packs (8,445 items) read by 54 opus readers; 732 yes → 630 rows → 591 certified (cut: operative
  rows need an act verb; citation evidence must pass the caption check) → Lean ok 278, noAuthority 313. Audit r8o01
  (pre-cut) 76/80 (corpus-weighted 0.854) → cut → fresh r8o02 77/80 = 0.963 [0.895, 0.987], link 80/80, decoys 16/18.
  INSTALL (cert/). Effect: holdout Y-named strict 771 → 774, anySignal 5,197 → 5,223; dev fresh / Shepardized / h0
  unchanged. Not read: 15 "survive" packs (0/160 yes). New findings: atRisk +367, panelDepartsWithoutEnBanc +79.
- 01:00 lean8: §4 + §5 bundled; LEAN8.md §0–1 stated (readings L8-1..15, 6 theorems, mutants M54–M60). Its observation
  that §4 admits "X, aff'd, Y, cert. denied, O" → step 5b bridgeChain (D8-9), sent to lean8, ref8, orderdock.
  state8 BENCH-3 (decisions2 data rule, ~30 rows, no benchmark effect) not staged (D8-10).
- 01:00 v8a staged (rehear8 G + N, ownact) and running (lead).
- 01:02 state8 done: h0 miss anatomy (154 pairs): Y never names X 9; implicit (no act sentence near X) 97; explicit
  sentence lost by reader rules 48 (11 real own acts: 4 multi-case, 1 ownact queue, rest reader bugs — "overruled in
  so far as" read as a report, procedural filter on "the ruling in X", comma clauses, infinitive acts, old-California
  part map labelling the opinion "concurrence~": 607 decisions); certificate stage 0. Rule R8S (5 repairs of the
  reader's rules over 2.51 M rejected sentences → 427 near-target candidates read by 5 opus readers → 169 rows → 151
  certified → Lean ok 132, noAuthority 19). Audit r8s01 77/80 = 0.963 [0.895, 0.987], link 80/80, decoys 16/18.
  INSTALL (cert/). state8_v1: state h0 13 → 15/132, fresh dev strict 51 → 52, lenient 111 → 112, holdoutOnly 574 →
  589. cert_multi (87 multi-target rows) passed to multicase. Not built: reporter aliases (no h0 miss needs one), BENCH-3.
- 01:02 orderdock: bridgeChain removes 39 lines (880 left); variant orderdock_c = bridge + bridge lines + lists v2 +
  remandcap. scdb8 interim: scdb8_d (557 rows, remove 11 v3 rows targeting rehearing denials): SCDB h0 1,681 →
  1,788/2,407 = 74.3%, precision 97.5%, clean 2,002 → 1,996; audits pending; wide-cue rows a separate class.
- 01:06 calpart launched (state8's finding: old-California header "…, J., delivered the opinion … C. J., concurring"
  labels the court's opinion "concurrence~"; 607 decisions with candidate sentences). ref8: §4 + 5b + §5 in the
  reference; 435 earlier universes byte-identical; 68 of orderdock's 880 bridge lines fail the spec (writer used
  r6cite keys, not compact index keys) → orderdock told to fix (a failing line rejects its row). Q8-13 ruled literal
  (X's own parallel cite before the cue fails bridgeChain).
- 01:12 fjc8 LEAN_REQUEST (old Fifth/Eighth circuit power over Eleventh/Tenth district courts before 1981/1929; 603 base history rows refused noAuthority) accepted claim-gated as D8-12 (DESIGN8 §6). orderdock_d: 879 bridge lines, ref8 879/879 ok.
- 01:16 ref8: §4 (5b, Q8-4 positions, ASCII-only), §5, §6 in the reference; 435/435 earlier universes byte-identical; real base v3 = known 2 witness rows only; differential waits for LEAN_READY. lean8: §4/§5 proved 01:12, §6 bundled.
- 01:19 orderdock done: no lower docket in SC orders → general links: bridge (52,264 subsequent-history strings ≥ 2013 →
  11,455 orders; 196/199 vs the orders' own "Reported below"), lists v2 (every "Reported below" entry, incl. 2005/2012
  long lists, Fed. Appx. alias, caption tie-check, consolidated scope), remandcap. Certified: bridge 6,326 (5,079 already
  in base), lists v2 568, remandcap 32. Audits: r8k01 bridge vacated/reversed 79/80 [0.932, 0.998]; r8k03 bridge
  certDenied etc. 79/80; r8k04 remandcap 32/32 [0.893, 1]; r8k02 lists v1 68/80 FAIL → r8k05 lists v2 fresh 80/80
  [0.954, 1]. INSTALL orderdock_d (bridge + 879 bridge lines + lists v2 + remandcap). Effect: Shadow Docket h0 recall
  156 → 426/1,059 (40.2%), precision 82.5 → 91.6%, clean unchanged; Shepardized dev 140 → 142 (one new FP: panel and
  en banc share 625 F.2d 433).
- 01:20 multicase done: rule MC-OWN (strong act verb + ≥ 2 cases named, or one + "those cases" in the sentence before;
  court's present act forms; exclusions) over 6.89 M decisions → 117,259 candidate sentences → 4,198 items → 2,705 read
  (69 packs) → 1,423 own acts → 2,904 rows (2,229 already v3) → 706 certified (incl. 47 of state8's multi rows) → Lean
  ok 651, noAuthority 55. Audit r8m01 76/80 = 0.950 [0.878, 0.980], link 80/80, decoys 16/18. INSTALL (cert/).
  multicase_v1: state h0 13 → 15/132; holdout explicitly admitted pairs 3,143 → 3,194; holdoutOnly negOrPartly 574 → 611.
  Of 119 state h0 misses, 100 have no list sentence by the overruling court: the remaining gap is not list sentences.
- 01:20 fjc8 (interim): oldCircuit base claims (614 lines; 183 status-changing) audited r8f04 63/80 = 0.787 [0.686,
  0.863]: failures in the old base rows themselves (old-reader quotes, earlier rulings) → base claims NOT installed;
  claims on fjc8's own F1 rows (26) covered by F1 audit r8f05 73/80 = 0.912 [0.830, 0.957].
- 01:21 fjc8 done: h0 miss anatomy (1,414 misses; 1,220 with no history row on the district decision; furthest stage:
  citation sentence does not name the court 405, caption one side only 231, guards 333, …; 33/40 read are true misses).
  F1 (unique district decision of the circuit cited with the opinion's own caption in a 6-year window; anchor from the
  nearest sentence naming the court; disposition sanity; ruling-type overlap; guards) over 546,328 CoA opinions →
  2,081 rows (reversed 535, vacated 203, modified 19, affirmed 1,317, dismissed 7). Audit r8f05 (status-changing,
  after fixes) 73/80 = 0.912 [0.830, 0.957], link+effect 75/80, corpus-weighted 0.903, decoys 16/18 → INSTALL
  (delta_c with LEAN_READY; delta_c_noclaim otherwise). Not installed: F2 one-side captions 62/80; S1 base scope
  rewrite 24/29; oldCircuit base claims 63/80. fjc8_c: FJC h0 recall 1,418 → 1,534/2,832 = 54.2% [52.3, 56.0],
  precision 90.3%, clean 6,087 → 6,081; Shepardized dev / SCDB / fresh unchanged. notarget launched (50-min timebox).
- 01:24 v8b (v8a + state8 + orderdock_d) scored: Shadow h0 403/1,059 (orderdock alone 426): 31 GVR'd nodes lost
  because rehear8's N rows record the court of appeals reinstating its judgment on the Booker remand (e.g. "nothing in
  … Booker … requires us to change our prior affirmance …; we reinstate our judgment"). Right as text; the MAPPING
  states this as a known mapping artefact (recall_at_order_plus_90d 434 → 435). D8-6 stands; both figures reported.
- 01:27 scdb8 done: h0 miss anatomy (726): cited below without accepted anchor 160, judgment line not read 131, anchor
  without cue 79, linker row not in v3 77, row on another decision of the litigation 64 (mostly rehearing-denial
  orders), partial 62, trial court refused 41, … Rules over all 110,654 SC decisions. Audits: r8b01 D1–D5 67/80 =
  0.838 (not installed as a whole); its D2/D2b modal sub-class 44/48 = 0.917 [0.804, 0.967] (near census of 49,
  post-hoc split; D8-14); D1/D3/D5 23/32 not installed; r8b02 A5+S6 anchors 72/80 = 0.900 [0.815, 0.949]; r8b03 T1
  trial court 32/34; r8b04 R4/R5 29/30; r8b05 W wide cues 78/80 = 0.975 (decoys 16/18). INSTALL delta_ins (512 rows,
  remove 12 v3 rows that point at rehearing-denial orders) + after LEAN_READY delta_w_all (110 rows, anchorWide
  claims, remove 1). scdb8_f: SCDB h0 1,681 → 1,779/2,407 = 73.9% [72.1, 75.6], precision 97.5%, clean 2,002 → 1,999.
- 01:30 v8c (v8b + multicase + fjc8 F1) scored: fresh dev strict 52, lenient 112/165; Shepardized dev 143/254, precision 93.5%; FJC h0 54.2%; Shadow 38.0%; state 17/132; holdoutOnly negOrPartly 647/6,734.
- 01:33 notarget done: 43,312 no-target sentences profiled (≈ 90% procedural "overruled"); 224 with a target within
  300 chars or in the act sentence → 223 read (6 opus) → 62 acts → 56 rows → 51 certified (Lean ok 39, noAuthority 12).
  Audit r8n01 (all 39 effective rows) 38/39 = 0.974 [0.868, 0.996], decoys 12/12 → INSTALL (small class). No h0
  effect; holdoutOnly negOrPartly +4. Caveat: one auditor reported that a search of the shared scratchpad showed
  other sessions' file names; it used none, and agreed 19/19 with the second reader. Far group (3,914, gap > 300) left.
- 01:34 v8d (v8c + scdb8 delta_ins) scored: SCDB h0 1,780/2,407 = 74.0%; Shadow 405/1,059 = 38.2% (precision 90.4%); FJC 54.2%; state 17/132; fresh dev 52/112; Shepardized dev 143/254, precision 93.5%. Live page updated.
- 01:38 LEAN_READY (lean8): theorems 220 → 245 (8 stated + 17 helpers, 0 changed), mutants 53 → 63, audit check green, fixtures green, regressions a/a2/b/c byte-identical, round7/out/v3 reproduced byte for byte; binary sha1 3b8d3e4d… . v8e staged (v8d + fjc8 claims + scdb8 W + notarget); running with the round-8 binary + reference.
- 01:40 lean8 done (see LEAN_READY 01:38; LEAN8.md readings: bridge decides over an anchor line on the same row, counted bridge_anchor_ignored; §6 target tiers trial/special). ref8: first differential found one disagreement (ambiguous key inside the chain window) — reference aligned (D8-15); 9 kept universes agree; sweeps running.
- 01:42 v8e Lean (round-8 binary) + reference: h8 10,296 ok; t8 1,090 ok / 392 noAuthority; bridge 879/879 admitted; anchorWide 110; oldCircuit 26 used. diff.py: only the 2 known New Jersey witness rows and their consequences (status 3, findings 18, certs 2) — every round-8 row agrees. Scoring v8e.
- 01:42 v8e scored: SCDB h0 1,809/2,407 = 75.2% [73.4, 76.8] (precision 97.5%); Shadow 412/1,059 = 38.9%, precision 90.3%; FJC 1,536/2,832 = 54.2%; state 17/132; fresh dev 52/112; Shepardized dev 143/254 (93.5%); holdoutOnly negOrPartly 655/6,734; no-leak 0. Candidate for the freeze; waiting for calpart (until ~02:05).
- 01:45 ref8 done: §4/§5/§6 in the reference (written from DESIGN8 only); differential vs the round-8 Lean: kept 9/0,
  main sweep 40 (3 = round-7 witness class W), probe 20/0, fuzz 30 (2 base-layer W, persist with round-8 inputs
  stripped), 435 earlier universes 7 = the known W universes; reference alone byte-identical to round 7 on them.
  Real v8e: the 2 known New Jersey witness rows + one ownact operative row of the same NJ successor class
  (t8:4058244:4016514:17127: Lean noAuthority, reference ok via the U-tagged succession) — Lean's verdict stands
  (the checker decides); no bridge/anchorWide/oldCircuit row differs. Open readings Q8-1..3, 7, 8, 11, 14 recorded.
- 01:59 FREEZE.md for v8e (176 file hashes; freeze8 --check ok). calpart left out: no file written since 01:11 and no report (TaskStop refused: not stoppable from here); its class is unaudited, nothing staged. Sealed run next, once.
- 02:00 SEALED (once): new keys h1 (round-7 → round-8, round-7 h1 from benchmarks/*/results/round7.h1.json): FJC
  1,448 → 1,566/2,864 = 54.7%; Shadow Docket 175 → 426/1,093 = 39.0% (precision 83.3 → 91.4%); SCDB 1,723 →
  1,810/2,400 = 75.4%; state tables 10 → 11/142. Fresh sealed (4th use) 77/32/57 unchanged; Shepardized sealed (3rd
  use) 120 → 123/252, precision 92.5%. Dev and h1 agree on FJC, Shadow, SCDB; the state-table h0 gain (+4) did not
  replicate (+1). Nothing re-tuned. ROUND8.md written.
- 02:01 live page: section 96_round8.html (Done, h0/h1 tables) and processes.json Round 8 row (Done); make_overturned.py rebuilt. Round closed.
- 02:27 calpart agent stopped (killed notification received after the round closed); nothing of it staged.
