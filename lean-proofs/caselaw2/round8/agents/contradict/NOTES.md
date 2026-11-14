# contradict (round 8, move 6): base rows contradicted by a newer two-quote row

Clock times from `date` (GMT).

## Log
- 00:18 started; read DESIGN8 §0, COMMON, BRIEF, round7/agents/b4sc/NOTES.md (section "Base rows contradicted").
- 00:19 sources: `round6/history/rules/{below_other,below_sc,rehear}/cert/rejects.tsv` (conflictBase: 466 / 9 / 7),
  rows in `rules/<x>/rows.jsonl` (reject column 1 = `rows.jsonl:<line>`), base id in the detail column.
  certify8 has `--keep-base-conflicts` (new row admitted although it clashes with a base row; the base row is then
  removed by the stage `--remove` list).
- 00:20 `pairs.py` -> `work/pairs.tsv` (482 pairs), `work/pairs.json` (counts), `work/rows_new.jsonl`.
- 00:22 certify8 of all 482 new rows with `--keep-base-conflicts` -> `cert_all/`: 482 admitted, 0 rejected,
  476 clash with a v3 row (6 base rows are gone from v3: those new rows no longer clash; not added here).
  Two new rows clash with two v3 rows each (c082: reversed + vacated; c199: affirmed + certDenied).
- 00:23 `rule.py` -> `work/rule_rows.jsonl`, `work/rule_pairs.tsv`, `remove_ids.txt` (245); certify8 of the 245
  -> `delta/` (245 admitted, 0 rejected; base_conflicts = exactly remove_ids.txt).

- 00:27 audit READY. 00:28 first audit `round8/audit/r8c01/` (pair form, type C):
  `make_packs8.py --class final_line --pairs round8/agents/contradict/pairs_rule.tsv --cert .../contradict/delta
  --cert round7/stage/v3 --n 40 --pack-size 30` -> 46 items (40 real, 6 decoys) in 2 packs; 4 blind opus auditors
  (packs 1, 2; readers a, b) spawned 00:28.

## Pair counts against v3 (482 conflictBase rejects of round 6)
- base row in v3: 476 (6 absent); Lean verdict of the base row: ok 449, noCue 18, noAuthority 7, targetUnresolved 2.
- admitted base (449): position of the new quote vs the base quote: after 318, overlap 101 (mostly the same
  sentence read as two kinds, e.g. "affirmed in part and reversed in part"), before 30.
- admitted base: final own disposition (cache `h` sentences of the opinion of the court after the new quote):
  final 331, later ones of the same polarity 25, a later one of the other polarity 93.
- admitted base: scopes new/base: unknown/all 392, all/all 51, all/unknown 6.
- new quote is an own disposition sentence (cache `h`, court part): 425 of 449; base quote: 446 of 449.
- kinds new<-base: reversed<-affirmed 226, affirmed<-reversed 93, vacated<-affirmed 80, affirmed<-vacated 28,
  vacated<-certDenied 5, reviewDismissed<-reversed 5, reversed<-certDenied 4, vacated<-reinstated 4, ...

## Rule (rule.py): "the final judgment line decides"
N replaces B when (i) N passes certify8; (ii) N's quote is an own disposition sentence (cache `h`, majority /
perCuriam), same text as B, N starts at/after B's end, no later own disposition sentence of another polarity;
(iii) scopes equal or N `unknown`; every clashing v3 row meets (ii)-(iii). Result: 245 replace, kept base:
overlap 96, later_opp 53, base not admitted 33, before 27, new not own disposition 24, scope 3, other clash 1.

## Audit r8c01 (00:30, `score_audit8.py round8/audit/r8c01` -> score.md, errors.tsv)
- 4 readers (2 per pack), strict reading; decoys 12/12 = 1.000 [0.757, 1.000]; readers agree on 46/46 items.
- new row (row 1) right: 27/40 = 0.675 [0.520, 0.799] (right + extent the same; corpus-weighted 0.582
  [0.403, 0.741]). Base row (row 2) right: 7/40 = 0.175 [0.087, 0.319]. Only new right 27, only base right 7,
  neither 6 -> new row right where exactly one is right: 27/34 = 0.794 [0.632, 0.897].
- by kinds: reversed/unknown vs affirmed/all 11/14; affirmed/unknown vs reversed/all 7/14; new NEG overall 17/22
  = 0.773 [0.566, 0.899]; federal 16/20, state 11/20.
- failure types: (a) mixed judgments whose final line is the "affirmed" half ("In all other respects ... is
  affirmed", "We affirm the district court." after "reversed in part") -> neither row right (6); (b) nested
  dispositions: "we affirm the judgment of the appellate court reversing ..." read as reversed, or a final
  "conviction affirmed" after "the decision of the court of appeals is vacated" (base right, 7); (c) a consolidated
  case whose final "We reverse" concerns another circuit; (d) a former appeal (no link, 1).
- Diagnostic (not a new rule): a "single-polarity, no partial phrase" filter on the new quote leaves 137 of 245 but
  scores 18/27 on the audited items: no general sub-rule reaches 0.90. The certDenied-base subset (8 rows) is mixed
  (partial cert denials) and too small.

## Decision (00:31)
NOT installed: the new row is right in 0.675 (0.794 of pairs where only one row is right), below the 0.90 bar.
Per the brief: report and stop. No second audit, no stage / Lean run / scoring. The base rows stay (current
behaviour). Files kept for the record: `delta/` (245 certify8 rows, `--keep-base-conflicts`), `remove_ids.txt`
(245 base ids) -- NOT for staging.

## Open
- 6 round-6 conflictBase rows whose base row is gone from v3 no longer clash (in `cert_all/`, not added).
- A mixed judgment (an own "reversed/vacated in part" line plus an "affirmed" line) is the main cause of both
  rows being wrong; the fitting row would be the negative kind with a partial scope, a reader/scope rule, not this
  replacement.
