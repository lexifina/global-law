# orderdock (round 8, move 2): SC orders linked by docket; Shadow Docket h0 weak spots

Brief: `BRIEF.md`. Times are from `date`.

## Log
- 00:18 started; read DESIGN8, COMMON, BRIEF; round-7 orderhead NOTES, r7a10/r7a12 errors (audit outputs only).
- 00:20 Findings so far: SC orders carry only the SC docket ("No. 15-1052."), never the lower docket. Lower-court
  decisions carry their own docket in the cache meta (`round6/history/cache/*.meta.tsv.gz`, column 6). So a docket
  link needs a bridge text. Candidate bridges (all general rules, corpus-wide):
  R (remand docket): a later decision of the court below that cites the order (graph/edges.bin) and has docket D;
    target = the unique earlier decision of that court with docket D (window before the order).
  S (target's own text): the target's head matter cites the order ("Certiorari Denied ... See 103 S.Ct. 355").
  H (history string): a later text's "<below cite>, cert. denied, <order cite>".
- 00:22-00:30 `dock.py meta|edges|probe`: lower-court docket index (3,781,217 nodes with a docket; cache meta col 6);
  orders cited in graph/edges.bin: 35,814 of 305,237. Graph-only bridges are thin: S (target's own text cites the
  order) 118 unique, R (later decision of the court below citing the order, same docket) 514 unique; validated on
  orders whose own "Reported below" resolves: R 9/28, S 2/3 -> not used as is.
- 00:24-00:30 `hscan.py list|scan` (738,887 decisions dated >= 2013, 10 procs, 52,264 history strings) +
  `dres.py`: "<decision below cite / lower docket>, cert. denied / vacated / ..., <SC page cite or No. 15-375>".
  SC docket numbers appear rarely (about 200 links use them); the usable bridge is the subsequent-history citation.
- 00:31 dres tightened (all page refs of the clause must be the order's own pages in its reporters; window <= 1095
  days; caption tie-check always: order caption and target title share a party-name token): 11,455 orders linked
  (certDenied 10,925, vacated 424, reviewDismissed 91, affirmed 14, reversed 1; 3,862 dated >= 2013).
  Validation against the order's own "Reported below" (listcite rows): 196/199 right (3 wrong: 2 sister decisions
  of the same case, 1 ...). Against round-7 orderHead v2 caption rows: agree 1,225 / disagree 24 (cap-2t 22): read
  10 disagreements, the caption row was wrong in at least 6 (first-name / official-name matches).
- 00:27 `listcite.py` (sub-rule a): every "Reported below" entry of an order list, entry court, r6cite aliases
  (Fed. Appx. -> F. App'x): 2,707 rows, 301 not in the memo rows (memo read only the first entry and the reader key).
- 00:33 Shadow Docket h0 diagnosis (v3 cases file): NEG 1,059, misses 903, 624 with the order in the corpus. Of
  those: 225 orders the memo parser never sees (174 = 2005 Booker lists > 4,000 chars, decision_type opinion);
  ~90 short combined lists now hit by listcite; ~60 by bridges; 97 post-2013 head-matter GVRs with no "Reported
  below" and no bridge (36 have a round-7 orderHead caption row, not installed).
- 00:36 `listorder.py scan|rows` (sub-rule a2): long SC texts (>= 4,000 chars, 28,529) that are order lists: 9 lists
  (2005 Booker, 2012 Dorsey), 444 vacated rows (entry court + r6cite aliases; tail disposition reaches every entry).
- 00:38 `dock.py remand` (bridge R2, remand docket): 931 orders linked; vs own "Reported below" 21/26, vs history
  strings 96/110 -> too weak alone; used only where it agrees with the caption link (class remandcap).
- 00:40 `build_rows.py` -> rows_bridge (11,409), rows_remandcap (276), rows_lists (3,083: listcite + listorder,
  deduplicated). Evidence name: tokens the order caption shares with the target title, within 400 chars of the
  quote; scope unknown for vacated/reversed when the target carries more docket numbers than the order captions (124).
- 00:41 certify8 (base v3): cert_bridge 6,326 admitted (orderHead 2,874; other 3,452; certDenied 6,039, vacated 234,
  reviewDismissed 48, affirmed 4, reversed 1), 5,079 in base, 4 orderHeadNotAllowed; cert_remandcap 32 admitted
  (vacated 25, certDenied 7; 244 in base); cert_lists 640 admitted (vacated 565, certDenied 74, reviewDismissed 1;
  2,443 in base; 527 alias keys fedappx).
- 00:42 stage `orderdock_a` = cert_bridge + cert_lists + cert_remandcap; Lean NOBUILD run started.
- 00:44 audits built (round8/audit, make_packs8): r8k01 bridge vacated/reversed (235 -> 80 + 9 decoys, 3 packs),
  r8k02 lists vacated/reversed (565 -> 80 + 9 decoys), r8k04 remandcap whole class (32 + 4 decoys, 1 pack);
  two blind opus readers per pack (14 auditors) spawned.
- 00:46 base rows contradicted by a bridge row on a single-caption order: 43 (all certDenied; 40 r6:memo caption
  rows) -> work/base_conflicts_single.tsv (drop candidates, no status effect).
- 00:47 LEAN_REQUEST.md written (optional `bridge:` evidence; rows do not wait for it). Pointer: see LEAN_REQUEST.md.
- 00:47 orderdock_a scored (Lean NOBUILD 5 min): Shadow Docket h0 recall 156 -> 462/1059 (14.7% -> 43.6%),
  precision 156/189 -> 462/507 (82.5% -> 91.1%), clean 43781 -> 43780/43811, recall_gvr 125 -> 426/967;
  FJC / SCDB / state tables unchanged. Shepardized dev: NEG strict 140 -> 142/254 (sc_vacated 30 -> 32/71),
  precision 140/149 -> 142/152, clean 9695 -> 9694/9704 (new FP: Armstrong v. McAlpin 625 F.2d 433, panel/en banc
  share one citation; bridge row h8:6076508:537721:vacated). Fresh dev unchanged (51/165).
- 00:48 audits (two opus readers per pack, strict reading; decoys 100% in every run):
  r8k01 bridge vacated/reversed (pop 235): 79/80 = 0.988 [0.932, 0.998] -> passes
  r8k04 remandcap whole class (32): 32/32 = 1.000 [0.893, 1.000] -> passes (small class; interval reported)
  r8k02 lists vacated/reversed v1 (pop 565): 68/80 = 0.850 [0.756, 0.912] -> FAILS. Failures: 6 link (a page of
    Fed. Appx. holds several decisions; the index keys another one: civil case vs. criminal petitioner), 6 kind
    (target decided co-defendants' appeals; the GVR reaches its petitioner only).
  r8k03 bridge certDenied/dismissed/affirmed (pop 6,091): 79/80 = 0.988 [0.932, 0.998] -> passes.
- 00:50 lists v2 (build_rows.py; v1 kept as work/build_rows.v1.py): caption tie-check (target title shares a party
  token with the order's captions; 381 refused) + scope unknown for vacated/reversed when the target has more
  docket numbers than entries citing it (79). cert_lists_v2: 568 admitted (vacated 506, certDenied 61, dismissed 1).
  Fresh audit r8k05 (--exclude r8k02 sample; pop 506): 80/80 = 1.000 [0.954, 1.000] -> passes.
- 00:49-00:53 lead accepted LEAN_REQUEST as D8-3 (DESIGN8 section 4). certify_bridge8.py -> cert_bridge_lines/
  (strict section 4: 919 of 6,326 rows get a line; bridgeActor 5,340: shared SC reporter pages are keyed to one
  order in graph/cite_index) and cert_bridge_lines_ownpage/ (--own-page: 4,294 lines; keys shared in the delta
  dropped, 1,923 rows). stage8.py EXTRA_TABLES = ["history_bridge"] (pre copy round8/pre/stage8.pre_orderdock_bridge.py).
- 00:54 stage orderdock_b = cert_bridge + cert_bridge_lines + cert_lists_v2 + cert_remandcap; Lean + score running.
- 00:5x lead D8-7: bridge lines strict only (no --own-page). Lead added step 5b bridgeChain: certify_bridge8.py now
  refuses a citation between X's citation and the cue (staged-index key, or graph key of another node);
  cert_bridge_lines/ regenerated: 880 lines (bridgeChain -39), cite_index_delta 1,739, 0 keys with two nodes.
- orderdock_b (bridge + lines(919) + lists v2 + remandcap) scored: Shadow Docket h0 recall 156 -> 426/1059 (40.2%),
  precision 156/189 -> 426/465 (91.6%), clean 43781/43811 (= v3), recall_gvr 125 -> 390/967, lenient 164 -> 471;
  vs orderdock_a: lists v2 caption check / consolidated scope cost 36 h0 hits (39 lost, 1 gained). FJC, SCDB,
  state tables unchanged. Shepardized dev = orderdock_a (NEG 142/254, precision 142/152, clean 9694/9704).
  Fresh dev 51/165 unchanged.
- orderdock_c = cert_bridge + cert_bridge_lines (880, strict + chain) + cert_lists_v2 + cert_remandcap: THE VARIANT
  TO STAGE; Lean + score running.
- 01:1x orderdock_c scored: status.tsv byte-identical to orderdock_b (frozen checker ignores history_bridge).
- 01:1x lead: ref8 found 67 bridgeTarget + 1 bridgeActor fails in the 880 lines (printed forms "Wn.2d" /
  "Fed.Appx." with no index line; CITE_RX instead of index keys). certify_bridge8.py now simulates section 4 exactly
  (staged index = base + cert_bridge/cert_lists_v2/cert_remandcap deltas + proposed lines, iterated; longest key at
  a position; X's line = printed key when its canonical form maps to X alone) and keeps a stricter writer-side 5b
  (any graph/base-resolved citation between X and the cue). cert_bridge_lines/: 879 lines (bridgeChain 39,
  bridgeActor 5,341, bridgeCue 61, bridgeTarget 6); 66 printed-key index lines; 0 keys with two nodes.
  Re-checked on round8/stage/orderdock_d tables: 879/879 pass.
- FINAL VARIANT TO STAGE: orderdock_d = cert_bridge + cert_bridge_lines + cert_lists_v2 + cert_remandcap
  (history +6,926 rows: bridge 6,326, lists v2 568, remandcap 32; history_claim orderHead +2,901; history_bridge 879).
  Not for staging: cert_lists (v1, failed r8k02), cert_bridge_lines_ownpage (D8-7: circular).
- Open: 43 base rows contradicted by a bridge row on single-caption orders (work/base_conflicts_single.tsv, all
  certDenied, drop candidates); 5,400 bridge rows carry no bridge line (shared SC reporter pages) and are installed
  on the audits r8k01/r8k03 only; Shepardized dev FP Armstrong v. McAlpin (panel/en banc share 625 F.2d 433);
  remaining Shadow Docket h0 misses: post-2013 head-matter GVRs without "Reported below" or a history string
  (docket-only), orders not in the corpus (281 h0 NEG), 2005 lists whose entries carry no citation.
- 01:17 orderdock_d Lean (NOBUILD frozen): status.tsv byte-identical to orderdock_c/b, so d's h0/dev scores = orderdock_b's.
