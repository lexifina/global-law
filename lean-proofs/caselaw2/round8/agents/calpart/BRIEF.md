# Agent `calpart` (round 8): opinions mislabelled as concurrences by the part map

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/calpart/` (NOTES.md).

## Finding (agent state8, `round8/agents/state8/NOTES.md`)
The part map labels old California opinions `concurrence~` when the opening line reads "…, J., delivered the opinion
of the Court. …, C. J., concurring." (the concurrence note of the other judges is taken as the start of a separate
opinion). A corpus count found this cut in 607 decisions that have candidate overruling sentences; there will be
more decisions overall, and other states/reporters may print the same header form.

## Do
1. Find where parts are assigned (round-6 cache zones / the reader's part map used by rounds 5–7 and the `part`
   field of rows; check what the Lean checker reads as the part and how it is verified). Write a general rule: a
   "concurring" (or "concurred") note inside the opening header block that names judges joining the opinion of the
   court — before any opinion text — does not open a separate opinion. Count the decisions it relabels corpus-wide,
   by state/court/decade; read 20 random relabelled decisions yourself to check the rule (opening lines only).
2. Re-run the existing overruling and history readers' candidate generation on the relabelled decisions only
   (sentences that were refused because their part was not the court's), with the round-7/8 rules (the state8 R8S
   repairs included: `round8/agents/state8/`), read where needed with opus reader sub-agents, certify8 into `cert/`.
   If the rows need the part map change to be visible to Lean (a staged table or a row field), do it the way the
   existing tables carry parts; if it needs a Lean change, write `LEAN_REQUEST.md` and tell the lead at once.
3. Blind audit (≥ 80 or all, decoys) via `round8/audit/HOWTO.md`; measure (stage/run/score): state-tables h0, fresh
   dev, holdout notes, no-leak.

Final report: rule, decisions relabelled, rows, audit, delta folder, effect.
