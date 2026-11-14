# scdb8 notes (round 8)

- 00:18 started; read DESIGN8, COMMON, BRIEF. bench_h0/READY, INFRA_READY, audit/READY absent. Studying round-6 below_sc and round-7 b4sc.
- 00:25 studied below_sc (round 6) + b4sc (round 7); tools peek8/tail8/cites8/corpus_miss/form_scan; sc8.py D1 (abbreviation periods in judgment sentences) run: decisions with row 8,871 -> 8,934.
- 00:40 bench_h0 READY (00:29). v3 SCDB h0: recall 1681/2407 = 69.8%, precision 97.5%, clean 97.6%.
  Misses (NEG not NEG_HIST): 726 = 638 GOOD with no row by the SC opinion on the below + 62 UNK_HIST (partial) + rest.
  Anatomy (anatomy8.py over round-7 diag; work/anatomy_r7diag.tsv), first stage that applies:
    no_anchor (below cited, no accepted anchor) 149 (+11 below not cand); anchor_no_cue (anchor lacks a cue-table cue)
    78; no_disposition 79 + disp_not_strong 52 (judgment line not read); sc_row_other_target 64 (SC row on another
    decision: 41 same court, later = mostly the order denying rehearing en banc); partial 62; trial_not_direct 41;
    row_not_in_v3 77 (r7 nozone 38, fn 9, round-6 weak/A1 rows not certified or not installed 30); later_marker 18;
    several_courts 15; outside_history 13; sc_row_other_kind 25 (affirmed 13); name guard 10; other 23.
  Round-7 R3 path reasons on these: L_no_shared_caption ~90, L_anchor_no_cue ~110, L_trial_not_direct ~60.
  Stratified sample of 41 (work/sample40.tsv, dump work/sample40_dump.txt, read by me): judgment line not read 12
  (modal "must be\nReversed." 3, "we grant ... and reverse" 2, long subject 1, part-map/slip chunking 3, hyphen "re- versed" 1),
  anchor / cue 6 (CA5-style parentheticals, fact citations, footnote cites), caption/name guard 5 (official-name
  changes, STOPW-only captions), wrong decision of the litigation 6 (rehearing-denial order 3), trial court on direct
  appeal 3, below not cited 2, later_marker false 1, source/partial/multi-docket 4.
- rules so far in sc8.py: D1 abbreviation periods; D2 widened modal + D2b printed "must be\nReversed."; D3 "we grant ...
  and reverse"/"Per Curiam: Reversed"; D5 long subject before "It is so ordered"; R4 rehearing-denial orders are not the
  judgment under review (+ later-marker exception). select8.py: new rows vs rules-off run, R3 test for weak types,
  round-7 guards, R4 replace list.
- 00:43 variant scdb8_c staged (delta_c_all 246 rows: disp 219, r4 11, r5 16; remove 11 v3 rows). Lean run.
- 00:55 scdb8_c (D1-D5 + R4 + R5, 246 rows, remove 11): Lean 246/246 ok. SCDB h0 recall 1681 -> 1723/2407
  (71.6% [69.7, 73.3]); clean 2002 -> 1993/2052; precision 97.5 -> 97.4%; FJC/Shadow/state unchanged.
  Losses read (lost8.py): 6 docket-numbered multi-kind judgments (scope unknown on the affirmed docket), 1 index
  collision (Chatwin: 146 F.2d 730 indexed to Cleveland, no shared party token), 2 SCDB coding errors (Lowe v. Dickson
  "108 Okla. 241, reversed."; Bakery Drivers v. Wohl "Reversed.").
  Fixes: K1 docket rule (target docket from its anchor; else no round-8 row); G1 round-8 rows need a shared party
  token. New rules: A5 head-matter block anchor, S6 own-case "See <cite>" sentence, T1 trial court on direct review
  (sc8sel.py = generated copy of sc7.strict/loose with the T1 gate).
- 00:56 lead: LEAN_REQUEST accepted as D8-5, claim-gated (anchorWide; DESIGN8 section 5). sc8 flag aw (--on aw);
  certify8w.py simulates the claim (certify8 with anchor + anchor_wide, writes the claim lines).
- 00:55 scdb8_d staged (cycle8.sh): select kept 562 new (disp-path 536, r4 4, r4rep 22) + R5 recert.
  Leave-one-out runs for class attribution running.
- 01:06 scdb8_d scored: SCDB h0 recall 1788/2407 = 74.3% [72.5, 76.0], precision 1788/1833 = 97.5%, clean
  1996/2052 = 97.3%; FJC recall +1 (1419), Shadow recall 158/1059, precision 158/192 (one CLEAN->NEG = Conkright v.
  Frommert 535 F.3d 111, a correct merits reversal), state tables unchanged. Remaining SCDB losses: docket-numbered
  multi-kind judgments (K1 now reads the whole judgment cluster), 2 SCDB coding errors, 1 partial ("vacated in part").
  Cycle scdb8_e running (K1 cluster window, wide W class, leave-one-out attribution).
- 01:15 cycle scdb8_e done: certify8 580/580 admitted, guard drops 28 -> delta_c_all 552 rows by class (rule id
  below:sc8_<cls>_<anchor type>): disp 182 (D1-D5, K1), anchor 248 (A5 head-matter block, S6 own-case See), trial 65
  (T1), multi 20 (needs two rules), r4 22 (R4 incl. r4rep), r5 15; remove list 12 v3 rows (delta_c_remove_r4.txt).
  Wide class W (claim anchorWide, certify8w simulation): 114 admitted, guard drops 4 -> delta_w_all 110 (wide 109, r4w 1).
  Stage scdb8_e = delta_c_all + remove (no W; W needs LEAN_READY); Lean + score running.
- 01:15 blind audits built (make_packs8, status-changing kinds reversed|vacated|modified, pack-size 30):
  r8b01 disp (84 -> 80 + 9 decoys, 3 packs), r8b02 anchor (111 -> 80 + 9, 3 packs), r8b03 trial (all 34 + 4, 1 pack),
  r8b04 r4|r4rep|r5|multi (all 30 + 4, 1 pack), r8b05 wide (83 -> 80 + 9, 3 packs). Two opus readers per pack
  (20 launched; r8b05 packs 2-3 reader b pending).
- 01:23 AUDITS (two blind opus readers per pack, strict reading; measure = right: same case + acted on +
  disposition agrees with the kind; status-changing kinds reversed|vacated|modified; decoys all caught unless noted):
  | run | class (population) | right | link | decision |
  |---|---|---|---|---|
  | r8b01 | disp, judgment readings D1-D5 (84) | 67/80 = 0.838 [0.742, 0.902] | 71/80 | NOT installed as a whole |
  |  | ... D2/D2b modal-line sub-class (49; 48 read = census) | 44/48 = 0.917 [0.804, 0.967] | | install (census; no fresh sample possible: 1 row left) |
  |  | ... D1/D3/D5 sub-class (40 status rows; 32 read) | 23/32 = 0.719 [0.546, 0.844] | | not installed |
  | r8b02 | anchor: A5 head-matter block + S6 own-case See (111) | 72/80 = 0.900 [0.815, 0.949] | 76/80 | install (at the bar) |
  | r8b03 | trial: T1 direct review (34, all) | 32/34 = 0.941 [0.809, 0.984] | 33/34 | install |
  | r8b04 | r4 / r4rep / r5 / multi (30, all) | 29/30 = 0.967 [0.833, 0.994] | 29/30 | install |
  | r8b05 | wide, claim anchorWide (83) | 78/80 = 0.975 [0.913, 0.993] | 78/80 | install after LEAN_READY (decoys 16/18: both pack-3 readers missed one decoy) |
  r8b01 errors (13): 7 wrong decision (2 rehearing-denial orders cited inside a "Dissenting from the denial of rehearing
  en banc" sentence, 3 different cases cited, 2 one level below), 6 kind (partial reversal 2, docket pair 1,
  modified/vacated 2, stay order 1); 9 of 13 in D1/D3/D5 opinions.
- delta_ins/ (512 rows: anchor, trial, r4/r4rep/r5/multi, D2 modal sub-class; ids_disp_modal.txt) + delta_ins_remove_r4.txt
  (12 v3 rows on rehearing-denial orders) = variant scdb8_f: Lean 512/512 ok. SCDB h0 recall 1681 -> 1779/2407 = 73.9%
  [72.1, 75.6], precision 97.5% (1779/1824), clean 2002 -> 1999/2052; FJC unchanged; Shadow recall 156 -> 158/1059,
  precision 156/189 -> 158/192; state tables unchanged.
- delta_w_all/ (110 rows, claim lines anchorWide) + delta_w_remove_r4.txt (1): needs D8-5 Lean (LEAN_READY). Simulated on
  h0: +31 NEG misses fixed, 0 CLEAN cases touched (SCDB recall ~1810/2407 = 75.2% with W).
- 01:24 score8.sh scdb8_f (round8/results/scdb8_f/summary.txt): no-leak exit 0; fresh dev unchanged (51/165
  strict, 111/165 lenient); Shepardized dev unchanged (NEG 140/254, precision 140/149, CLEAN 9695/9704, SC reversed
  87/129, SC vacated 30/71: the new rows touch none of the dev cases); holdout notes +1 to +2 (history 4746/5625 ->
  4789/5670 = 84.5%; alsoInFeed negOrPartly 1038 -> 1039, holdoutOnly 574 -> 575); old lists (burned) unchanged.
## Open
- D1/D3/D5 judgment readings (abbreviation periods, "we grant ... and reverse", long subject) not installed (23/32
  in r8b01): the readings are right, the linking in those opinions is weaker (rehearing-denial order cited inside a
  "Dissenting from the denial of rehearing en banc" sentence; different cases cited; one level below). Next step: R4b
  (denial of rehearing anywhere in the citation's own sentence), the R3 sole/latest test for these rows, re-audit.
- W (anchorWide) waits for LEAN_READY (D8-5); then stage delta_ins + delta_w_all with both remove lists and run Lean
  without NOBUILD.
- Round-6 guard drops R4 rows ("a-same-later": the rehearing-denial order is a later decision of the same court):
  10 of 21 R4 rows lost to it; a guard exception for R4-recognised denial orders would recover them (not done).
- Remaining h0 misses not addressed: partial scope (62), source errors (SCDB legacy codes), slip-opinion part maps,
  hyphenated "re- versed" in hard-wrapped slip opinions (Lean noCue), below not cited.
