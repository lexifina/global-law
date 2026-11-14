# Agent `scdb11` (round 11): SCDB — the decision under review is the rehearing / en banc decision, not the panel (move 5)

Read `round11/DESIGN11.md` and `round11/agents/COMMON.md` first. Folder `round11/agents/scdb11/` (NOTES.md, a line
every 10 minutes). Audit letter `b`. You may read `benchmarks/scdb_disposition/SOURCE.md`, `MAPPING.md`,
`DISAGREEMENTS.md` and the h0 files (`round10/results/v10d/bench/scdb_disposition.h0.cases.tsv`,
`round11/results/*/bench/`) only. Never the closed keys.

## Background
v10d SCDB h0: recall 1,826/2,407 = 75.9%, precision 97.5%, clean 97.4%. Round 10 `scdb10` (`round10/agents/scdb10/`:
NOTES.md, `anatomy10.py`, `sc10.py`, `scope10.py`, `select10.py`, `deltas10.py`, `work/anatomy_a.tsv`) found among 583
h0 misses: `sc_row_other_target` 59 — 25+ where the Supreme Court's row hits another decision of the same court
below: the panel opinion when the judgment under review is the en banc / rehearing decision (or the reverse), or an
earlier panel decision. Others: row_not_in_base 125, no_anchor 113, partial 63, no_disposition 50.

## Do
1. Re-run the anatomy on v10d and list the other-target misses. On the corpus: for each Supreme Court history row
   whose target T has a later decision T' of the same court in the same case before the Supreme Court decision
   (rehearing en banc, panel rehearing, opinion on remand, amended opinion, "opinion withdrawn and superseded"), find
   which one the Supreme Court reviewed — its own text ("judgment of the Court of Appeals sitting en banc", "the en
   banc court", the decision's date or citation in the syllabus-free opinion text, "on rehearing"), T' citing T as
   vacated/superseded. Read ~40 such pairs with opus readers (corpus text only).
2. Rule R: link the row to (or add a row on) the decision actually under review, by the Court's own words naming
   the en banc / rehearing court or by the citation / date of T'; when the en banc decision vacated the panel
   decision, the panel decision is not the target. Decide per case whether the change is a new row on T' (keep or
   drop the row on T — a `--remove` of a wrong-target row is a status change and must be audited as such), keeping
   rows checkable by the round-10 Lean.
3. Certify, stage, run (NOBUILD), score (`noold`): SCDB h0 precision / clean, Shepardized dev must not drop.
4. Blind corpus-wide audit (≥ 80 or the whole class, two opus auditors, decoys; item type B). Install bar ~0.90.
5. If time remains: one more general rule on another SCDB miss block (no_anchor / partial / no_disposition) not
   designed on round-10 audits' errors.
Report: anatomy counts on v10d, rules, rows, audits with intervals, delta / remove folders, h0/dev effect vs v10d,
headroom left (misses by reason, SCDB coding errors).
