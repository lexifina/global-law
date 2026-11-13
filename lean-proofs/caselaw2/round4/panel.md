# Round 4 item 7: the rise of `panelDepartsWithoutEnBanc` (664 -> 998)

Fork `panel`, 23:17-23:27, 12 Nov 2026. Read-only: no Lean, reference or live-data change. The fork could not spawn
subagents, so the 20 sheets were read by the fork itself (blind to gold and to the reader's reasoning; sheet = window,
courts, bench labels, kind). Files: `work/round4/panel/` (`sheets.txt`, `key.tsv`, `answers.tsv`, `new_findings.json`).

## New findings
- No round-2 findings file is kept, so "new" = findings whose treatment row is not in `data/treatments.pre_round3.tsv`.
  That gives exactly 334 new and 664 old.
- All 334 new rows have reader `claude-subagent`; kinds: 332 `overruled`, 2 `abrogated`.

## Sample of 20 (seed 4007)
- Own act of the treating court: 20/20. Treating bench a panel of the target's court (or its successor): 20/20.
- Sound as "a panel departed from its own court's binding precedent without en banc": 1/20 (Wilson 95%: 0.9%-23.6%);
  with the borderline item 19 (NLRB policy change): 2/20 (2.8%-30.1%).
- Cause of the 18 false ones: one cause. The panel states that circuit precedent "is no longer good law / the law of
  this circuit / controlling" because of an intervening Supreme Court decision (17) or state high court decision on
  state law (1). That is the recognised exception to the prior-panel rule; no en banc court is needed.
- Not the cause: overruled-vs-disapproved kind confusion (0/20), bench mislabel (0/20), court or epoch mislabel (0/20).
- The rows themselves are right as status rows (the target is no longer law in that circuit). Only the finding is wrong.

## Where it comes from
- The round-2 cue additions for `overruled` ("no longer", "disavow", "abandon", ...) admit these sentences.
- Of the 998 findings, 427 have a quote with no express-act word (318 of the 334 new, 109 of the 664 old); 360 of
  those carry the cue "no longer".

## Proposed fix (not applied)
Emit `panelDepartsWithoutEnBanc` only when the row's certified quote (lower-cased, normalised) contains one of
`overrul`, `disapprov`, `recede from`, `receded from`, `recedes from`, `receding from`. (Not the bare stem `recede`:
it matches "precedent".) Same test in `Run.lean` (the `treatInfo` loop) and in the reference `_panel_departs`.
- Effect computed from `out/findings.tsv` and `data/treatments.tsv`: 998 -> 571 (removes 427: 318 new, 109 old; by
  kind: 411 `overruled`, 16 `abrogated`; all 102 `disapproved` and 114 `recededFrom` stay).
- In the sample it removes all 20, including the one sound item (4) and the borderline one (19).
- Status rows and every other finding are unchanged. No theorem statement is touched if the test is added at the emit
  site in the runner rather than inside `panelDepartsWithoutEnBanc`.
- Not measured: precision of the 571 that stay (the 16 new ones that stay were not in the sample).
- Alternative, more work: relabel these rows `abrogated` with by-decision = the intervening decision (the witness
  format of item 1); the sentences are witness statements by the target's own court.
