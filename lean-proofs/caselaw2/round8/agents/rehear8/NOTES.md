# rehear8: round 8, move 3 (rehearing grant orders -> the panel opinion they vacate; no-date docket rows)

Agent `rehear8`. Folder `round8/agents/rehear8/`. Started Sat 14 Nov 2026 00:18 (clock of `date`).
No answer key opened. Nothing committed.

## Log
- 00:18 start; read DESIGN8 §0, COMMON, BRIEF, round-7 b4rehear NOTES / RULES7 / r7rehear.py.
- 00:20 `r8rehear.py window`: round-7 installed c-order rows (423): delay order - panel opinion median 134 d, p99 478,
  max 546 -> grant window G_WINDOW = 548 days (18 months).
- 00:21 `nrows` (no-date / other-date docket rows from round-7 `work/cands.jsonl` + `feats.json`): 585 no-date + 30
  other-date candidates. Read 15 a + 12 b + 12 e (seeds 801-803): 37/39 right; the two wrong -> N-7 (another court's
  judgment inside the act span, after a Supreme Court reversal recital) and N-8 (part of the opinion: "any
  expression in our former opinion ... is withdrawn"). N-7 first version too broad (dropped "our judgment affirming
  the district court is reinstated"): narrowed with ACTED_ON. Now 366 no-date rows + 2 re-dated.
- 00:23 `orders` (claims cache: 3,520 short records granting rehearing en banc, or granting rehearing + present act
  on this court's opinion; 106 of the 139 round-7 grant-order targets); docket index 3,664 keys; `ofeats` running.
- 00:24-00:33 `grows` (G rules) read in rounds: grant-latest 6/10 (seed 811) -> G-3b motion to withdraw the petition,
  G-3c another case, G-4b failed poll ("voted against"), G-7 adoption in the court's part; fresh 14 (seed 821):
  11/14 -> G-3d named-judge minority votes, DENY_EB "is also denied", failed-poll forms; fresh 14 (seed 831): 13/14
  -> G-2b short ORDER-headed targets (en banc remand order with a named bench); act rows 11/12 (seed 813: another
  court's decree in the act span -> N-7 applied to acts) and 14/14 (seed 841); grant-date (Virginia / D.C.
  orders naming the mandate / opinion date) 10/10 (seed 812). Orders without a caption line (state reporters,
  CourtListener): unanchored name evidence within the certifier window (400 characters), G-6.
- 00:33 final counts: G 311 rows (12 pairs also emitted by N removed -> 299 in `work/rows_grant_final.jsonl`); N 366
  no-date + 2 re-dated. certify8: `cert_grant` 299/299 admitted (rehearingEnBancGranted 185, vacated 103,
  withdrawn 11); `cert_nodate` 368/368 (vacated 127, reinstated 121, withdrawn 65, modified 51, substitutedBy 4).
- 00:34 staged `rehear8_a` (= v3 + cert_grant + cert_nodate; history 175,182 rows); Lean NOBUILD run started.
- 00:35 blind audits built (HOWTO, make_packs8 default seed, no hand selection): `r8h01` class rehear8/grant
  (population 299; 80 real + 9 decoys, 3 packs), `r8h02` class rehear8/nodate (368; 80 + 9, 3 packs). Two opus
  readers per pack spawned (r8h02 pack 1 reader b waits for a free agent slot: concurrent limit).
- 00:41 Lean (NOBUILD) `rehear8_a`: round-8 rows by verdict h8 ok 667 (all). Scored (`round8/results/rehear8_a/`).
- 00:43 audit r8h01 (rehear8/grant, 2 readers/pack, strict reading): right (link + kind) 76/80 = 0.950
  [0.878, 0.980]; link + effect 77/80 = 0.963 [0.895, 0.987]; right + extent 75/80 = 0.938 [0.862, 0.973];
  link 77/80; corpus-weighted right 0.957 [0.888, 0.984]; decoys 18/18. Errors: an en banc order only remanding
  to the panel (target already vacated earlier), a stay motion "heard en banc" (target an order on another stay
  motion), a Tex. CCA parallel report (1 reader), vacated vs withdrawn (kind only), one scope.
- 00:44 audit r8h02 (rehear8/nodate): right 72/80 = 0.900 [0.815, 0.949]; link + effect 74/80 = 0.925
  [0.846, 0.965]; right + extent 71/80 = 0.887 [0.800, 0.940]; link 79/80 = 0.988; corpus-weighted right 0.911
  [0.807, 0.962]; decoys 18/18. Errors: partial vacaturs read as whole ("vacated as to <party>", "regarding the
  seniority issue", "Part V ... vacated and the following language substituted", "the judgment only ... withdrawn")
  -> modified / in part; vacated vs withdrawn (kind only, 2); one Booker reinstatement of convictions only (scope);
  one link (memorandum disposition relied on, a companion opinion vacated).
- 00:45 variant `rehear8_b` (= a without the 121 reinstated no-date rows) building, to explain a -1 in Shepardized
  dev sc_reversed and sc_vacated in `rehear8_a`.
- 00:50 `rehear8_b` scored (nobench): h8 ok 546. Shepardized dev vs base v3: NEG strict 140 -> 143/254, lenient
  149 -> 152, precision 140/149 -> 143/152 (94.1%), CLEAN 9695/9704 unchanged, MOD 15/16 unchanged; enbanc_different
  14 -> 16/27, panel_withdrawn 9 -> 10/27, sc_reversed 87 and sc_vacated 30 unchanged. So the -1 / -1 of `rehear8_a`
  (sc_reversed 86, sc_vacated 29; NEG 141) comes from the reinstated no-date rows: after a Supreme Court vacatur the
  panel's own "we reinstate our judgment" makes the target live again in the model, while the dev key keeps it
  negative. The rows themselves are right (audit), so this is a semantics decision for the lead.

## Results (summary)

| class | delta folder | rows | audit | right (link + kind) | link + effect |
|---|---|---|---|---|---|
| rehear8/grant (G) | `cert_grant` | 299 (fed 156 / state 143; rehearingEnBancGranted 185, vacated 103, withdrawn 11) | r8h01 | 76/80 = 0.950 [0.878, 0.980] | 77/80 = 0.963 [0.895, 0.987] |
| rehear8/nodate (N) | `cert_nodate` | 368 (all federal; vacated 127, reinstated 121, withdrawn 65, modified 51, substitutedBy 4) | r8h02 | 72/80 = 0.900 [0.815, 0.949] | 74/80 = 0.925 [0.846, 0.965] |
| N without reinstated | `cert_nodate_noreinst` | 247 | (subset of r8h02 population) | - | - |

Variants: `rehear8_a` = v3 + cert_grant + cert_nodate; `rehear8_b` = v3 + cert_grant + cert_nodate_noreinst.
Dev / h0 (rehear8_a vs base v3): fresh dev unchanged (strict 51/165, lenient 111/165); holdout history 4746/5625 ->
4786/5708; Shepardized as above (a: NEG 141, enbanc_different 16, panel_withdrawn 10, sc_reversed 86, sc_vacated 29);
FJC h0 unchanged (recall 1418/2832, clean 6087/6229, precision 1418/1576); Shadow Docket h0 recall 156 -> 159/1059,
precision 156/189 -> 159/196, clean 43781 -> 43777/43811; SCDB disposition h0 recall 1681 -> 1683/2407, precision
1724 -> 1727 flagged (97.5%), clean 2002 -> 2001/2052; state tables unchanged (13/132).

## Open points
- Round-7 grant-order drops (139 orders): 52 already have a base row from the order to the panel opinion, 31 have no
  earlier opinion of the docket in the corpus (the panel opinion is not in the corpus), 9 give new rows; the rest
  fail the docket / caption / window / denial gates.
- N partial vacaturs whose limit is "as to <party>", "regarding <issue>", "the judgment only" are kept with scope
  `all` (audit errors); a partial-marker rule (scope `unknown` / kind modified) would need a fresh audit (exclude
  r8h02).
- G: an en banc order that only remands to the panel, and "motion for stay be heard en banc" (not a rehearing of an
  opinion) are the residual error kinds.
- No Lean change needed (all 667 rows h8 ok with the round-7 runner, NOBUILD).
