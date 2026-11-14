# Round 7 log (real clock times from `date`)

- 22:37 start. Read ROUND5, DESIGN5, ROUND6, DESIGN6, LEAN6, PROGRESS6, STAGE_NOTES, improvement_plan,
  ROUND7_REQUEST. Machine: 24 cores, 62 GB in WSL; C: 45 GB free (variants cost ~300 MB each: watch it).
- 22:39 round7/ created; WSL keep-alive started (`wsl.exe -d Ubuntu -- sleep 36000`).
- 22:41 DESIGN7.md written (contract for joined certificates, history claims, linker rows, scoring, audits).
- 22:42-22:45 launched Phase A agents: lean, ref, infra (incl. A1(iii) orderHead rows), antecedent (A1 i),
  doctrine (A1 ii), opwords (A2 prep; readers by the lead, opus), audit (tooling); and Phase B preparation that
  touches no Phase A file (D7-5): queue (B1 inventory/packs), b3 (date-view scorer), heldout (new clean key).
- 22:46 live page: Round 7 row in processes.json (backup round7/pre/report/), section 95_round7.html; page rebuilt.
- 22:56 coordinator message: a separate `benchmarks/` agent owns new answer keys (FJC, Shadow Docket, SCDB
  disposition, pre-1930 state tables) and will re-score our frozen output from `round7/out/<name>` once FREEZE.md
  names it. Agent `heldout` redirected to a time split (or a thin adapter to a finished `benchmarks/` key). Final
  report must end with a ranked list of next highest-value, lowest-effort moves.
- 23:00 b3 done: `round7/score_fresh7.py`. final2 dev: model view strict 50/165 = 30.3% [23.8, 37.7], lenient
  108/165; attributed view strict 80/165 = 48.5% [41.0, 56.1], lenient unchanged (exactly 30 a_date → a). Holdout
  strict (precedent, Y named) 745 → 832 of 12,354 under the attributed view.
- 23:02 queue done: 12,466 certifiable feed statements = 1,859 read + 6,671 pattern-certified + 3,936 queued;
  plus 2,283 T1F items only pre-screened by the smaller model. Queue 6,219 items, 131 packs, 33 shards (P1 2,761
  items: no admitted row for the pair). Leak check 0/6,219. The "246 unread packs" are the round-3 own-act queue
  (work/round3/queue/packs 142-397, 20,443 items; different brief/certifier writing into data/): needs a port.
- 23:03 opwords done: round-5 failures 47 = intervening statute/rule 32, another decision 11, no loss of authority 4;
  43 of 47 are the bare state form "X is no longer the law"; own-act verbs were right 58/60. New brief
  READER_BRIEF_OPWORDS7.md (four tests; state form only with an own-act marker and no outside cause; whole only
  with listed phrases). 4,624 items in 103 packs (2,145 read in round 5 under the old brief, 2,479 never read).
  Pilot pack_001: 7 positives, all part. Certifier requires cause == own.
- 23:04 launched 13 opus readers on opwords packs 001-052 (4 packs each).
- 23:10 audit tooling done (make_packs7/score_audit7/AUDITOR_BRIEF7, decoy pools A 71 wrong/377 right, B 292/974;
  self-test pass). Launched b4sc (B4 a: Supreme Court opinions not linked; e: re-point multi-decision pages).
- 23:12-23:16 opwords readers 001-052 done (13 readers; ~7 min each); launched readers for 053-103 (13 more).
  Readers flag duplicate item ids in a few packs (answered once per listing) — the certifier must dedupe.
- 23:17 coordinator forwarded the antecedent agent's anaphor-list proposal: accepted (D7-8), passed to `lean`.
  antecedent: 49,595 candidates; 5,973 items queued in 150 packs; it runs 6 opus readers itself.
- 23:16 heldout redirected and done: time split = Supreme Court merits judgments dated 2021-01-01 or later, keyed
  from the Court's own docket JSON (public domain): 256 (SC node, lower node) pairs; scorer refuses to run before
  FREEZE.md; Shadow Docket raw files kept unlinked. `round7/heldout/` and `benchmarks/` added to DESIGN7 §0.2.
- 23:15 launched 6 opus readers on antecedent packs 091-120 (the antecedent agent reads 001-090 itself).
- 23:17 heldout incident (its NOTES.md): one recursive file-name grep and a first "seen nodes" scan walked
  round5/gold_fresh/sealed/ before the exclusion was added; nothing printed or kept, output overwritten. Recorded;
  the sealed fresh half's integrity is reported with this note. Heldout key: 256 pairs (reversed 83, vacated 47,
  mixed 3, affirmed 46, DIG 4, certDenied 73); 82 pairs touching any node builders had seen were dropped.
- 23:17 launched B1 readers S001-S003 (P1); S004+ refused: the harness caps 40 concurrent sub-agents (nested
  readers included). Pending launches, in order: B4 rehear agent, B2 scope agent, B1 S004-S015, antecedent 121-150.
- 23:18 infra done: certify7, stage7, r7_run.sh (NOBUILD mode), score7.sh; `base` reproduces final2 byte for byte
  (summary minus timing). orderHead: 9,812 candidates (not 11,065: v1 count), only 119 pass the order_line cue list
  because the order list reads "Petition for writ of certiorari to the <court> denied." → D7-9: `lean` asked for
  in-order (a ... b) order_line entries. B4(f): 204,371 of 305,237 Supreme Court orders (67.0%) have no unique match
  (no candidate 114,234; several 58,377).
- 23:18 ref done: reference implements DESIGN7 §1-3 + D7-6; 0 disagreements on the 267 round-6 universes; real
  final2 identical; 18 new universes + sweeps ready for the Lean differential (difftest7.sh) once LEAN_READY.
- 23:18 fixed certify7 KeyError on unjoined treatments rows (reported by antecedent; backup kept).
- 23:19 launched b4rehear (B4 b, d), scope (B2 rule), B1 readers S004-S006.
- 23:20 opwords: all 103 packs read (4,612 items; 872 own acts) → certified 936 rows (30 whole). Blind audits built:
  r7a01 = part, 80 + 10 decoys; r7a02 = whole, all 30 + 4 decoys; 3 auditors launched.
- 23:24 audit r7a02 (operative words, whole, all 30 + 4 decoys, 1 auditor): right 10/30 = 0.333 [0.192, 0.512];
  right + extent 7/30. Mostly "X was wrongly decided" read as criticism (`limit`), not a disposal. Whole sub-class
  NOT installed as whole. Decoys 3/4.
- 23:24 B1: S001 140/160 positive, S002 158/196; T1F S004/S005 0/400 (D7-11 hold confirmed).
- 23:23 audit r7a01 (operative words, part, 80 of 906 + 10 decoys, 2 auditors): right 79/80 = 0.988 [0.932, 0.998],
  right + extent the same; answers overrule 52, reject_doctrine 27, limit 1. Part sub-class INSTALLED (906 rows);
  the 30 whole rows are left out (r7a02).
- 23:24 B1 P1 (OG/CUT, 497 statements + T1F 650 items read): certify_recog → 317 new recognised rows, all
  "on other grounds" (partly negative): overruled 199, disapproved 68, abrogated 30, recededFrom 20. Audit r7a03
  (80 + 10 decoys) launched.
- 23:24 variant v1 = final2 + operative words part (906) + B1 recognised (317); whole operative rows dropped.
  Running with NOBUILD (round-6 checker is exact here: no round-7 table).
- 23:27 v1 scored (dev). Fresh dev lenient 108 → 109/165 = 66.1% [58.5, 72.9]; strict 50/165 model view, 80/165
  attributed view; SCDB 175 → 176/278 and CRS 195 → 196/292 with recognised rows (burned). Shepardized dev
  unchanged (105/254, precision 105/111). No-leak exit 0. Fixed score7.sh: the holdout scorer was called without
  the frozen pool (no 2,640/6,734 lines); backups agents/infra/*.pre_pool.*.
- 23:30 v1 holdout, frozen pool: alsoInFeed negOrPartly 932 → 1,027/2,640 = 38.9% [37.1, 40.8]; holdoutOnly
  370 → 499/6,734 = 7.4% [6.8, 8.1]. The holdout-only rise (+129) needs explaining before it is accepted:
  ablation v1rcg (recognised rows only) running.
- 23:34 holdout explained. The right "before" is the round-6 frozen build final2 (not round 5's figures):
  alsoInFeed 940/2,640 = 35.6%, holdoutOnly 425/6,734 = 6.3% (round 6's history rows had already moved both).
  v1rcg (B1 recognised only): 1,019 / 431. v1 (+ operative words): 1,027 / 499. All 81 pool pairs that the new
  recognised rows touch are alsoInFeed (0 holdout-only). The holdout-only rise (+68) comes from the operative-words
  rows: Y's OWN words on X ("rejected", "disavowed", ...), which is what a holdout note "X overruled by Y" reports;
  no holdout statement enters the model (leak check exit 0). Recorded as a legitimate own-words gain, not a leak.
- 23:39 antecedent done: 49,595 candidates → 5,973 items read (150 packs; 3,048 acts) → 1,747 rows → 1,305
  certified (442 already in base). Sub-classes: A joined 489, B one-sentence 574, D window-plain 63, C weak verbs
  179. Blind audits r7a04 (A, 80), r7a05 (B, 80), r7a06 (D, all 63), r7a07 (C, 80), each + decoys; 8 auditors.
- 23:40 doctrine done: registry 7,184 unique labels (2,132 ambiguous); 255 items read; 29 rows → 12 certified
  (Brown → Plessy "separate but equal", field "public education"; Wayfair → Quill; Solorio → O'Callahan …); ~7 more
  need cue additions (D7-12, sent to lean). Only 5 pairs are new information vs the base.
- 23:41 scope (B2) done: the rule moves only 56 explicit rows partialUnknown → all (45) / issues → all (11); 9,591
  kept partial (7,530 limiting phrase, 2,061 part of the case acted on). Fewer than 80 changed rows exist: audit
  all 56 (r7a08) + a 40-row control of kept-partial rows (r7a09). Confirms the round-6 diagnosis: most "partly
  negative" fresh-list pairs are correct partial overrulings the lists record flatly.
- 23:43 orderHead: certify7 + build_orderhead now apply the D7-9 in-order entries (`order_line_hit`; backups
  *.pre_orderline.*): 8,166 rows certified (was 119). Audit r7a10 (80 + decoys) built. ref asked to implement D7-9.
- 23:42 audits: r7a04 antecedent A joined 79/80 = 0.988 [0.932, 0.998] (extent 76/80 = 0.950) → INSTALL;
  r7a05 B one-sentence 78/80 = 0.975 [0.913, 0.993] (extent 77/80) → INSTALL; r7a06 D window-plain 54/63 = 0.857
  [0.750, 0.923] → NOT installed; r7a08 scope → all, census 55/56 (extent 54/56 = 0.964 [0.879, 0.990]) →
  install pending the control r7a09 (decoys in r7a08 only 5/8: noted). Decoys r7a04 10/10, r7a05 8/10, r7a06 7/8.
- 23:44 audits: r7a07 antecedent C weak verbs 36/80 = 0.450 [0.346, 0.559] → NOT installed (answers: other 20,
  report_other 23: the "no longer good law" form again). r7a09 scope control (kept-partial rows) 38/40 = 0.950.
  Scope rule (56 rows → all) INSTALLED.
- 23:45 audit r7a10 orderHead (all kinds; 97% certDenied): 67/80 = 0.838 [0.742, 0.902]; every failure is a wrong
  caption link (cap-2t 11/59 wrong, cap-2g 2/21). Not installed as a whole. The status-changing part (110 GVR
  `vacated` rows) is audited separately: r7a12 (80 of 110). Doctrine: 19 rows certified after D7-12 (was 12);
  audit r7a11 (all 19) running.
- 23:50 audits: r7a11 doctrine, all 19 rows: 19/19 [0.832, 1.000] (overrule 13, reject_doctrine 6) → INSTALLED
  (small class; interval reported). r7a12 orderHead GVR (vacated) 67/80 = 0.838 [0.742, 0.902] (link 8, kind 5)
  → orderHead class NOT installed (Lean rule in place; the data linking, mostly caption-only, is the weak part).
- 23:50 b4sc done: (a) 1,394 rows (R3 sole-litigation-decision, weak types passing R3, R2 modal judgment line),
  (e) 58 SC + 345 other re-pointed shared-page rows; proxy dev NEG 106 → 128/254 with no new CLEAN/MOD negatives.
  Audits r7a13 (R3), r7a14 (weak/R2), r7a15 (re-pointed), 80 each, status-changing kinds only.
- 23:53 audits (B4): r7a13 R3 sole-litigation-decision 71/80 = 0.887 [0.800, 0.940] (link + effect 73/80) → not
  installed as a whole; by sub-rule the failures sit in nozone/fn (5/24). Fresh re-audit r7a16 of R3 without
  nozone/fn (253 rows, excluding the r7a13/r7a14 samples) launched — the cut is decided by this fresh sample, not
  r7a13. r7a14 weak types passing R3 + R2 modal 73/80 = 0.912 [0.830, 0.957] → INSTALLED. r7a15 re-pointed
  shared-page rows 72/80 = 0.900 [0.815, 0.949] → INSTALLED (at the bar; interval reported).
- 23:57 r7a16 fresh re-audit of R3 without nozone/fn/modal sub-rules (253 rows): 76/80 = 0.950 [0.878, 0.980]
  → INSTALLED (R3 zone/hm/body); nozone/fn/modal (288 rows) left out.
- 23:57 b4rehear done: en banc act 437, en banc grant orders 423, en banc silent 86, docket-linked 267, set aside
  97 rows (rules in agents/b4rehear/RULES7.md; failure analysis of round 6: 27/55 were links to the grant order).
  Audits: r7a17 en banc act+order pooled (80), r7a19 silent (all 55 fresh), r7a20 docket (80), r7a21 set aside
  (all 97). 9 auditors launched.
- 00:01 LEAN_READY (lean agent: 220 theorems, 53 mutants, audit check green, fixture + regressions a/a2/b/c
  byte-identical after D7-12).
- 00:02 rehear audits (measure as D6-13: link + same status effect): r7a17 en banc act + grant orders 79/80 = 0.988
  [0.932, 0.998] → INSTALLED; r7a19 en banc silent 54/55 = 0.982 [0.904, 0.997] → INSTALLED; r7a20 docket-linked
  79/80 = 0.988 → INSTALLED (link + kind 74/80 = 0.925); r7a21 set aside, all 97: link + effect 96/97 = 0.990
  [0.944, 0.998] → INSTALLED (link + kind 80/97: "vacated" vs "reversed" labels, same negative effect).
- 00:03 v3 staged = final2 + operative part (906) + B1 recognised (317) + antecedent A/B (1,063) + doctrine (19) +
  scope replace (56) + B4 a (R3 zone/hm/body + weak/R2; 1,091 after dropping 288) + B4 e (398) + rehear en banc
  act/order/silent + docket (1,213) + set aside (57 rows + 97 claims). Running on the round-7 Lean with the
  reference (`r7_run.sh v3 ref`).
- 00:03 v3 Lean run (round-7 binary) + reference: disagreements = the 2 New Jersey witness rows known since round 5
  only (status 2 keys, findings 17, certs 2); every round-7 row agrees. Lean verdicts on new rows: h7 ok 2,759;
  t7 ok 1,837, noAuthority 140, joinedRelation 2 (two doctrine rows certify7 admitted and Lean + reference refuse:
  certify7 is looser there — noted; the checker decides). Counters: joined 508 lines, 474 admitted; history claims
  97, 89 admitted; doctrine rows 17 admitted, 0 ambiguous.
- 00:04 v3 scored (dev): fresh strict 51/165 = 30.9% [24.4, 38.3] (attributed 81/165 = 49.1% [41.6, 56.6]),
  lenient 111/165 = 67.3% [59.8, 74.0]; holdout alsoInFeed 1,038/2,640 = 39.3% [37.5, 41.2], holdoutOnly
  574/6,734 = 8.5% [7.9, 9.2]; Shepardized dev NEG strict 140/254 = 55.1% [49.0, 61.1], precision 140/149 = 94.0%
  [88.9, 96.8], CLEAN 9,695/9,704, en banc 14/27, panel withdrawn 9/27, SC reversed 87/129, SC vacated 30/71;
  SCDB 178/278, CRS 198/292 (burned). No-leak exit 0.
- 00:04 holdout-only check: every new v3 row that touches a holdout-only pool pair is an explicit row of Y's own
  text (119 rows); 0 witness rows touch one (all 81 new witness rows hit alsoInFeed pairs). The holdout-only rise
  (6.3% → 8.5%) is the own-words classes (operative words, antecedent), not a leak.
- 00:08 FREEZE.md written for v3 (127 file hashes; freeze7.py --check ok). Sealed runs next, once.
- 00:08 SEALED (once each). Fresh lists, sealed half (third use): lenient 77/127 = 60.6% [51.9, 68.7] (round 6:
  77/127, unchanged); strict model 32/127 = 25.2%, attributed 57/127 = 44.9% [36.5, 53.6]. Dev moved +3 lenient
  (108 → 111), sealed +0: the lenient gain did not replicate on sealed (within noise; not re-tuned).
- 00:09 Shepardized sealed (second use; via shep_sealed7.py after compare.py refused on the round-6 freeze hashes):
  NEG strict 104 → 120/252 = 47.6% [41.5, 53.8]; lenient 129/252; precision 120/130 = 92.3%; CLEAN 9,577/9,586
  (was 9,579); en banc different 0 → 6/33; panel withdrawn 3 → 5/25; SC reversed 73 → 79/132; SC vacated 28 → 30/61.
  Dev moved +35 (41.3 → 55.1%), sealed +16 (41.3 → 47.6%): same direction, smaller on sealed.
- 00:10 Time split (new key, Supreme Court merits judgments 2021+, 256 pairs; first and only use), r6-final2 → r7-v3:
  reversed link/effect 14 → 21/83 (25.3% [17.2, 35.6]); vacated 9 → 13/47 (27.7% [16.9, 41.8]); affirmed effect
  44/46, certDenied 73/73 both builds; precision (row points to the key's lower decision) 39/42 → 60/65 = 92.3%;
  rows of a negative kind on affirmed/denied pairs 2 → 2; orders with no history row 214 → 191 of 256.
- 00:10 ref differential (Lean at LEAN_READY 00:00): 267 round-6 universes 0; fuzz 40 and no-round-5 20: 0; kept 18,
  main 60, probe 30: only class W (round-5 witness standing: reference witnessNoStanding vs Lean ok/noAuthority; it
  persists with every round-7 input stripped, so it predates round 7; same family as the New Jersey rows). Reference
  self-check 8,391 expectations, 0 differ.
- 00:11 ROUND7.md written; live page and processes.json updated (Round 7: Done). Round closed.
