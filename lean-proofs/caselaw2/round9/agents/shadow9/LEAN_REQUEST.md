# shadow9 LEAN_REQUEST (optional; the rows do not wait for it)

Rows of class `shadow9:remandtext-K9-v2` (`cert_remandtext_v2/`, 335 history rows) are checked by the round-8 Lean as
any order row is: the order's own disposition quote, part (orderHead claim for head-matter orders >= 2013: court,
date, kind, order_line, length), name evidence (party tokens the order caption shares with the target title, within
the window). What the round-8 Lean cannot check is WHY the target is the decision below: the remand decision B.
Installed on the blind audits r9k01 (79/80) + r9k02 (8/8), like round 8's remandcap class.

## Rule (proposed optional evidence table `history_remand.tsv`)

One line per row: `id`, `b_node`, `b_start`, `b_end` (a quote of B's own text), `docket` (a docket token).
Check `remandBridge` (after the row's own checks pass):
1. B's court = the target's court; date(order) <= date(B) <= date(order) + 1,826 days; date(target) < date(order).
2. `docket` is a docket number of both B and the target (decisions2 / meta docket field, normalised tokens).
3. B's quote holds a `remand_cue` phrase ("Supreme Court" with vacat- / remand- / "in light of" /
   "further consideration") and is <= 600 characters.
4. B's quote (or its window) ties to the order: a citation key of the order's page, or the order's docket number,
   or the order's date as printed.
Failure reasons `remandCourt`, `remandDate`, `remandDocket`, `remandCue`, `remandTie`.

## Effect
Moves the link evidence of these 335 rows (and round 8's 32 remandcap rows) from "audit only" to checked.
No change of status counts (the rows are admitted now).

## Theorems
`no_remand_line_no_change` (absent table => round-8 step byte-identical); `remandBridge_sound` (admitted line =>
B and target share a docket token and court, B after the order, cue in B's quote); mutants: B before the order,
B of another court, a docket token of B only.
