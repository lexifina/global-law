# scdb8 LEAN_REQUEST: anchor cues for the court forms the Supreme Court uses for the decision below

Agent scdb8 (round 8). For the lead, to pass to `lean8` if accepted. Cue-table data only; no checker code changes.

## The rule
Add these entries to `cue_table.json` key `anchor` (substring test on the ASCII-lower-cased, normalised anchor quote,
exactly as the existing entries):

| cue | form it admits (examples from Supreme Court opinions) |
|---|---|
| `circuit` | "The Fifth Circuit defended its requirement ...", "the Seventh Circuit rejected ... and affirmed. 101 F. 3d 1183" |
| `(ca` | "Iqbal v. Hasty, 490 F. 3d 143, 147-148 (CA2 2007)", "Alford v. Haner, 333 F. 3d 972, 974 (CA9 2003)" |
| `c.a.` | "662 F.3d 387, 392 (C.A.5 2011)", "670 F.3d 1160, 1162 (C.A.11 2012)" (the table has only `c. a.`) |
| `judicial court` | "the Maine Supreme Judicial Court reversed. 655 A. 2d 876 (1995)" (`supreme court` does not match it) |
| `court of errors` | "Upon appeal to the state court of errors and appeals, the judgment was affirmed. 103 N. J. L. 708" |
| `case below` | "Compare 662 F.3d 387 (C.A.5 2011) (case below), ..." |

## The check (unchanged)
`check_hist` anchored path: the anchor quote must contain one `anchor` cue, no `disqualify_anchor` entry, and the
row's evidence (`cite:` key resolved through the citation index, or `name:` tokens). Only the cue list grows. Every
other step (disqualifiers, evidence, part, target-before-acting, conflict) is as now.

## Effect (measured; no key row is input to any rule)
- On the 726 SCDB-disposition h0 misses of v3 (`work/try_cues.py`, linker run only, before selection/guard): the five
  cues `circuit`, `(ca`, `c.a.`, `judicial court`, `court of errors` let the existing anchor rules link 36 more misses
  to their decision below (0 lost); all 36 were `anchor_no_cue` (the anchor sentence names the court only in these
  forms).
- Base rows: a cue list that grows can only admit more rows (no current verdict changes from ok to refused). With the
  round-8 mode by presence, nothing changes unless rows that need the new cues are staged.

## Theorem it needs
None new: the anchored-history soundness theorem quantifies over the cue table (membership of a cue in the anchor
quote); adding entries keeps it. The cue-table hash in `audit/statements.lock` changes (lean8 regenerates it).

## Risk
`circuit` also matches "circuit court" (already a cue) and "Circuit Justice"; `(ca` matches "(Cal." in state
citations. An anchor still has to hold the target's own citation key and pass the linker's court test (the citation's
governing court phrase must fit the target's court), so a wider cue does not by itself create a link.
