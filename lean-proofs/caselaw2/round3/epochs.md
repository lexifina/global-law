# Round 3, item 8 (agent `epochs`, resumed 23:03 on 12 Nov 2026): stray decisions re-routed, cluster epochs dropped

## State found (23:03)
- Nothing installed: `data/decisions2.tsv` (22:26) and `data/courts2.tsv` (22:17, identical in size to
  `work/round3/epochs/courts2.round2.tsv`) untouched; no `*.pre_round3.tsv` for either; no install lock.
- Predecessor's files in `work/round3/epochs/`: `strays.tsv` (839), `heads.json`, `build_delta.py` ->
  `court_delta.tsv` (804 re-routed) + `exceptions.tsv` (35 kept), `apply.py`, three finished reference runs.
- Variants (from `apply.py`): **a1** = `apply.py` without `--circuits`: court column of the 804 delta ids changed,
  all 88 `data:decision-cluster` rows dropped, exception rows written back for the 35 kept decisions.
  **a2** = a1 plus `--circuits`: federal rows with circuit 11 get circuit 5 before 19811001, circuit 10 rows get
  circuit 8 before 19290228.
- Runs (frozen engine `ref_frozen/`, same data snapshot): out_b 71,846 status / 151,570 findings; out_a1 71,862 /
  151,579; out_a2 71,942 / 151,928. Splits 491, conflicts 101, horty 44 in all three.

## Delta (804 rows, `court_delta.tsv`: node, old court, new court, rule, source)
Court of Claims 654 -> Claims Court 656: 486. Hawaii ICA 866 -> Supreme Court 867 (docket SC**): 88. "Kansas Court
of Appeals" 10002 -> Kansas City Court of Appeals 10107: 79 (+1 -> Kentucky 913). Alabama Court of Appeals 1 ->
Civil Appeals 2: 20, -> Criminal Appeals 3: 1. NJ Court of Chancery 1206 -> Superior Court, Chancery Division 1222:
17. 517 -> D.C. Circuit 514: 10. NY 1769 -> Appellate Division 1287: 8. U.S. circuit courts -> district court of
the same district: 80 (37 courts). Others: 608 -> 2905 (2), 664 -> 679 (2), 1047 -> 1050 (3), three by text
(312 -> 2998, 491 -> 326, 414 -> 157).
Exceptions (35, `exceptions.tsv`): 24 date errors (158 Tenn. reprints 20, Texas Commission 2, V.I. 1, NY 1) and 11
kept (NY 1769 x10, "District of California" 1960 x1: court not determinable from the text).

## Blind check (predecessor's three batches, `blind/`; scored 23:05)
30 delta rows, opinion text only, three Claude subagents (`claude-subagent`), answers in `blind/answers0-2.tsv`,
key `blind/key.tsv`. The auditor's court equals the delta's new court in 30 of 30 (Wilson 95%: 0.886-1.000). One
(B0-8, node 4087571, 1206 -> 1222) names the Superior Court but the Law Division, confidence medium; id 1222 is the
Chancery Division row, so strictly 29 of 30 (0.833-0.994). The corpus has that decision under "Court of Chancery",
so 1222 is kept. Sample by rule: 654->656 22, 10002->10107 3, 866->867 2, 1206->1222 1, circuit->district 2. Not
sampled: Alabama 1->2/3, 517->514, NY 1769->1287, the single-row rules.

## Diff of a1 against the baseline: every row explained (`classify_a1.py` -> `classify_a1.tsv`)
Status, 16 new rows, 0 gone, 0 changed: nodes 2573567, 2573693, 2574400 (Hawaii Supreme Court 1980, 1981, 1991)
are `negative overruled` from 20190628 by 2570041. 2570041 is a 2019 SCWC decision of the Hawaii Supreme Court that
the corpus labels as the ICA (866 -> 867). As an ICA decision it could not overrule the Supreme Court.
Findings, 19 gone and 28 new:
- 16 `citesLaterNegated` gone. Citing court is the Court of Claims (654, 1965-1982); the cited decisions (1965058,
  1965476, 1969350) were negated on 19920423 and 19850802. Those dates fell inside two cluster rows of 654
  (19900628-19920428, 19850222-19851011), so in the baseline the Court of Claims "existed" on them. Without the
  cluster rows it has no epoch there and both engines drop the finding (the round 2 rule; open question 1 of
  `round2/courts.md` "For the Lean owner" still applies).
- 3 `claim:overruled` gone: 2570041's three overrulings now take effect (the status rows above).
- 7 `citesLaterNegated` new: Hawaii ICA (869) decisions citing those three decisions.
- 18 `citesLaterNegated` new: citing decision is a re-routed Claims Court decision (654 -> 656, 1985-1992); the
  cited decision is of the Claims Court, the Federal Circuit or the Supreme Court and was negated later. Court 654
  had no epoch on the negating date; 656 has.
- 1 new: 3793239 (10002 -> 10107, Kansas City Court of Appeals 1922) cites a Missouri Supreme Court decision
  overruled later. 1 new: 94025 (1 -> 2, Alabama Court of Civil Appeals 2003) cites an overruled Alabama Supreme
  Court decision.
- 1 `panelDepartsWithoutEnBanc` new: 105432 (Court of Civil Appeals 2005) overrules 94021 (1 -> 2, 1999), now a
  decision of the same court.
Nothing unexplained. Splits, conflicts, horty unchanged.

## Decision: a1 installed; a2 not installed
a2's extra diff (112 status rows, 497 findings against a1) was not classified in the time allowed (coordinator's
scope change at about 23:04: 15 minutes, no new run, circuits to next round). Its files stay in
`work/round3/epochs/` (`data_a2/courts2.tsv`, `out_a2/`, `diff_out_a1_out_a2_*.tsv`).

## Install (23:05, `python -X utf8 apply.py --install`, no `--circuits`)
- Backups written first (copies): `data/decisions2.pre_round3.tsv` (915,171,131 bytes), `data/courts2.pre_round3.tsv`.
- `data/decisions2.tsv`: live file re-read under the lock, court column of the 804 delta ids changed (0 skipped),
  `.tmp` checked (6,892,454 rows, same columns, only column 2 differs), renamed.
- `data/courts2.tsv`: 3,106 -> 3,025 rows: 88 cluster rows dropped, 7 exception rows added.
- `apply.py` got a row/column check before the rename (the only script edit).
- Note: at the end `os.rmdir` of `.install.lock` failed because the directory was already gone. Someone else
  removed it during the 20 seconds of the install. No lock is left. The checks below were run after that.

## Verification after install (23:06)
- Live `decisions2.tsv` against `decisions2.pre_round3.tsv`: 6,892,454 rows, 9 columns in every row, 804 lines
  differ, all in the court column only and all equal to `court_delta.tsv`.
- Live `decisions2.tsv` and `courts2.tsv` are byte-identical to `data_a1/`, the inputs of run `out_a1`. So out_a1
  is the reference result of the installed state (as of the 22:48 snapshot of the other tables); no new run.
- Decisions dated outside their court's epoch: 0.
- Cluster rows: 88 (47 courts) -> 0. Ended courts with an epoch after their end: 47 -> 5, 7 rows, 35 decisions:
  481 (1 kept, 1960), 1769 (10 kept 1896; 1 date error 1898), 2907 (20 date errors, 1929), 2948 (2 date errors),
  3000 (1 date error). Src `data:kept-stray` / `data:date-error-exception`.

## Not done / next round
- Circuit-parent epochs (Eleventh Circuit districts under the Fifth before 19811001, Tenth Circuit districts under
  the Eighth before 19290228): implemented as `apply.py --circuits` and run (out_a2) but not classified, not
  installed. Finding recorded: it changes 112 status rows and 497 findings (+80 status rows, +349 findings net),
  far more than the 11 findings round 2 expected, so it needs a row-by-row triage before install.
- The 35 exceptions: 24 need a date fix in `decisions2.tsv` (not this item's column), 11 need a court that the
  text does not name.
- Blind audit of the strata not sampled (Alabama, 517->514, NY).
- COURTS.md rule 7 ("cluster rows") is now out of date: text to add: "Round 3: the 839 stray decisions were
  re-routed (804) or kept as dated exception rows (35); no `data:decision-cluster` row remains."
- `tools/caselaw2/epochs_fix.py` would recreate cluster rows if rerun from `courts2.pre_round2.tsv`; rerun
  `work/round3/epochs/apply.py` after it.
