# Agent `doctrine8` (round 8, move 7, optional): doctrine dominance

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/doctrine8/` (NOTES.md).

## Background
Round 7 (`round7/agents/doctrine/` NOTES.md, `build_registry.py`, `dscan.py`, `work/cue_counts.json`; DESIGN7 §2.3–2.4,
D7-12): doctrine rows (a court rejects a doctrine D; the doctrine is tied to a case X by a tie cue in the same
opinion) — 19 certified, 17 admitted by Lean, audit 19/19. The ambiguity rule is strict: a label tied to two
decisions anywhere in the corpus gives no row (linker) and two admitted rows with the same label and different targets
both fail in Lean (`doctrineAmbiguous`, theorem `doctrine_unique`). Doctrine rows are always demoted (at most
`unknown:partialScope`).

## Do
1. Measure the opportunity first (timebox ~40 min): with the round-7 registry, how many rejected-doctrine
   sentences were refused only because the label is tied to several decisions, and of those, how many have one
   decision far more often than any other (e.g. ≥ 5 ties and ≥ 4× the runner-up; try a few thresholds, report the
   curve)? What would they add (rows, distinct targets, fresh dev / holdout effect estimated from pair overlap)?
2. If fewer than ~25 new rows would result, stop and report (not worth a Lean change this round).
3. Otherwise: design the rule so Lean can check it (the table-level check can only see the table: e.g. the linker
   writes the dominance counts as a data column that Lean cannot verify — say so — or the rule stays linker-only with
   the Lean table uniqueness kept per admitted row), write `LEAN_REQUEST.md` (rule, check, effect, theorems:
   `doctrine_never_neg` must still hold), produce rows with certify8, and run a blind audit (≥ 80 or all) via
   `round8/audit/HOWTO.md`.

Final report: opportunity curve, decision, and if built: rows, audit, LEAN_REQUEST.
