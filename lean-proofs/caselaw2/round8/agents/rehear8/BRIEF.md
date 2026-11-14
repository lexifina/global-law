# Agent `rehear8` (round 8, move 3): rehearing grant orders → the panel opinion they vacate; no-date docket rows

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/rehear8/` (NOTES.md).

## Background
`round7/agents/b4rehear/` (NOTES.md, `RULES7.md`, `r7rehear.py`, `work/dropped.tsv`, `counts7.json`): round 7
installed en banc act + grant orders (748), en banc silent (55), docket + date linked rehearing (240), set aside (97).
Left: **154 rehearing grant order rows dropped** (see NOTES/dropped.tsv: why — e.g. the link went to the grant order
itself or the panel opinion could not be told apart) and **589 non-en-banc docket rows whose act sentence names no
date** (+ 30 that name the date of another decision) — R7-D1. Round 6: `round6/history/rules/rehear`.

## Do
1. Grant orders: a general rule that links an order granting rehearing (en banc or panel) and vacating "the panel
   opinion" / "the opinion filed …" to the panel opinion it vacates: same court, same docket number (docket index of
   r7rehear), the latest opinion of that docket before the order (or the one whose date / reporter citation the order
   names), not itself an order; unique only. Re-derive the 154 and any new candidates corpus-wide; certify8.
2. No-date docket rows: when the act sentence ("we withdraw our opinion", "the opinion is vacated") names no date,
   link to the unique earlier opinion of the same docket and court (no other published opinion of that docket in
   between; a stated window); 30 naming another decision's date: refuse or re-point by the stated date. Certify8.
3. Measure (stage/run/score): Shepardized dev subclasses `enbanc_different`, `panel_withdrawn`, CLEAN kept clean;
   FJC h0 (`round8/results/<v>/bench/fjc_idb_appeals.h0.cases.tsv`) where relevant. Blind audit per class (≥ 80 or
   all; link + same status effect, and link + kind reported separately as in round 7). Installed only at ≥ ~90%.

Final report: rules, counts, audits (k/n, Wilson), delta folders, dev/h0 effect.
