# ownact NOTES (round 8, move 1)

- 00:18 started; read DESIGN8, COMMON, BRIEF.
- 00:26 port done (`port8.py`, log `port8.log`, `port_stats.json`): round-3 unread 19,584 items (res minus
  12,168 answered ids); all re-anchored to git HEAD (19,576 same offsets, 8 moved). Power (reference can_change on
  v3; same court = power) and v3 admitted negative pairs (37,740): low_nopower 9,787 (district/bankruptcy/
  intermediate courts over higher courts; `low_nopower.tsv`), low_admitted 122 (`low_admitted.tsv`), queued
  9,675 (P1 9,666, P2 power-unknown 9). 121 packs `packs8/pack_000..120.md` (80 items), `items8.jsonl.gz`,
  `index.tsv`. Order: round-3 certified rate of the pattern (`yield_r3.py` -> `yield_r3.json`).
- 00:27 `READER_BRIEF_OWNACT8.md` (round-3 brief + round-7 opwords/antecedent lessons), `answers_to_rows8.py`
  (answers -> DESIGN7 rows; evidence must be in the act quote or a joined antecedent line; non-overrule-family
  verbs -> disapproved/operativeWords/partialUnknown).
- 00:27 smoke test (scratchpad): one fake answer -> answers_to_rows8 -> certify8: 1 admitted. Pilot readers
  (opus) launched on packs 000 and 001 -> `ans/ans_000.jsonl`, `ans/ans_001.jsonl`.
- 00:31 pilot: packs 000+001, 160 items, 52 yes (overruled 39, disapproved 8, recededFrom 4, rejected 1);
  77 (item, target) pairs -> 64 rows (9 base_has_pair, 4 window_only/naming unusable); certify8: 61 admitted +
  3 in_base_skipped, 0 rejected => 73/77 = 95% of yes targets certify (bar 90%). Hand look at all 52 yes quotes:
  all are present own acts ("we overrule", "is hereby overruled", "we recede from", "to the extent ... disapprove").
  Brief fixed once: optional `kinds` per target (mixed verbs), naming must hold the TARGETS naming (no bare Id.).
  Packs per reader: 2 (one pack ~140k tokens of reader context).
- 00:32 wave 1: 20 opus readers, packs 002-041 (2 packs each). Next: packs 042-120 as readers finish.

## Pack tracker
| packs | state |
|---|---|
| 000-001 | done (pilot) |
| 002-041 | wave 1 running |
| 042-120 | queued |
- 00:38 batch 1 certified (packs 000-041 + 050-055 as answered): 3,428 answers, 288 yes -> 298 rows ->
  certify8 268 admitted, 7 rejected (disqualified), 23 in v3 already. Strata (cert/strata.json): federal 41 / state
  227; verb family 180 / strong (disavow etc., operativeWords) 88; scope all 33 / partial 235. Readers say no to
  bare "no longer good law" (verb class "state" = 0 rows). Concurrent-subagent cap of the session is 40 (shared):
  refilling as slots free. Interim variant `ownact_v0` staged + Lean (NOBUILD) running.
- 00:42 yield by pattern (answers so far): part-fix 47%, wrongly 38%, compelled 35%, be-and-is 36%,
  decision-subj 28%, we-and-verb 23%, passive-adv 18%, other-verb 8%, no-target 9%, regarded-as 7%,
  procedural-named 5%, no-longer-law 2% (yes are NY App Div "no longer to be followed" with a conflict phrase),
  survive 0/160 (packs 104-105). Stop rule: the survive packs 106-120 (1,173 items; round-3 rate 1.2%, here 0/160)
  are NOT read. All other packs 000-105 launched (2 packs per reader); readers on 084-103 still running.
  Packs 044-046 ("wrongly" pattern) give many "X was wrongly decided" = kind rejected -> operativeWords rows; verb
  class "state" in strata.py (no reject/repudiat/... word) so the audit can separate it.
- 00:45 reading done for packs 000-105 (8,445 answers, 732 yes). Certified all (`run_batch.sh` -> `cert/`):
  744 rows -> 677 admitted by certify8, 41 rejected (28 noCue operative e.g. "incorrectly decided", 13
  disqualified), 26 in v3 already; converter dropped base_has_pair 67, window_only 35, duplicate_pair 20.
  Strata: federal 184 / state 493; verb family 197, strong 355, follow 51, state 74 (mostly "wrongly decided");
  kind overruled 158, disapproved 510 (operativeWords 522 rows incl. rejected ones), recededFrom 9.
  Interim ownact_v0 (268 rows) Lean: 135 ok, 133 noAuthority.
- 00:45 audit r8o01 built: `make_packs8.py --class o1 --cert round8/agents/ownact/cert --n 80
  --pack-size 30 --out round8/audit/r8o01/` -> 89 items (80 real, 9 decoys) in 3 packs; 6 blind opus auditors
  (2 per pack) running. Staging ownact_v1 (= full cert) + Lean NOBUILD.
- 00:48 audit r8o01 scored (`score_audit8.py`): right 76/80 = 0.950 [0.878, 0.980]; corpus-weighted 0.854
  [0.687, 0.940] (n_eff 30); federal 40/40, state 36/40; decoys 18/18; two readers agree 88/89. Errors: 3 of 4 are
  "X was wrongly decided" with no act verb (auditors: limit, not overrule) = the round-7 weak-verb lesson again; 1 is
  a shared-page citation (Norman v. Daniels cite resolving to another decision on the same page).
  Cut by two stated rules in answers_to_rows8.py: (1) operativeWords rows need an act verb in the main quote
  (reject|repudiat|disavow|abandon|overturn|discard|follow), state words alone are not written (rej_state_verb 114);
  (2) cite: evidence must pass the round-7 caption check (cite_consistent: no other caption right before the cite).
  Old cert kept as `cert_r8o01/` (+ rows_r8o01.jsonl). New `cert/`: 630 rows -> 591 admitted, 13 rejected.
  Re-audit on a FRESH sample r8o02 (--exclude r8o01/sample.tsv).
- 00:51 re-audit r8o02 (fresh sample, --exclude r8o01/sample.tsv, class = cut cert, 591 rows): right 77/80 =
  0.963 [0.895, 0.987]; corpus-weighted 0.975 [0.884, 0.995] (n_eff 48); link 80/80; federal 38/40, state 39/40;
  decoys 16/18 (one known-wrong decoy missed by ans_1 and one by ans_2_b). 3 errors, no common sub-rule (target is
  the lower-court decision under review in the same litigation; reasoning rejected is the district court's; act
  words inside a quotation of another opinion). Class passes the bar (point >= 0.90).
- 00:58 measured. ownact_v1 (old cert, 677 rows; superseded) and **ownact_v2 = stage8 --delta cert/** (591
  rows), NOBUILD Lean: t8 ok 278, noAuthority 313 (federal ok 78 / 94; state ok 200 / 219; overruled ok 82,
  disapproved ok 195, recededFrom ok 1; verb family 95 ok, strong 171, follow 12). In the r8o02 sample the Lean-ok
  rows are 42/42 right; all 3 errors are noAuthority rows. score8.sh ownact_v2 vs base: fresh lists dev (both views),
  Shepardized dev, old lists, new keys h0 (fjc, shadow, scdb, state tables): unchanged; holdout notes precedent
  Y-named strict 771 -> 774, byAnyone 900 -> 903, negOrPartly 4542 -> 4556, anySignal 5197 -> 5223; holdoutOnly
  strict 85 -> 87, anySignal 1000 -> 1018; no-leak exit 0. Findings: atRisk +367, citesOverruled +60,
  panelDepartsWithoutEnBanc +79 (from noAuthority panel rows).

## State: DONE (reading, certify, audit, measure)
- Delta ready to stage: `round8/agents/ownact/cert/` (591 rows; variant ownact_v2). Superseded: `cert_r8o01/`.
- Not read: packs 106-120 (1,173 "survive" items; 0/160 yes in packs 104-105), low_nopower.tsv (9,787 items: no
  candidate the acting court has power over), low_admitted.tsv (122: every powered pair already admitted in v3).
- Resume: answers in ans/ (106 files, 8,445 answers); `bash run_batch.sh` rebuilds rows + cert + strata.
