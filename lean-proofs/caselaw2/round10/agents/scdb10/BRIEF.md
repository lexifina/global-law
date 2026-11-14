# Agent `scdb10` (round 10): SCDB disposition — decisions below cited without an accepted anchor (move 4)

Read `round10/DESIGN10.md` and `round10/agents/COMMON.md` first. Folder `round10/agents/scdb10/` (NOTES.md). Audit
letter `b`. You may read `benchmarks/scdb_disposition/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files
(`round9/results/v9c/bench/scdb_disposition.h0.cases.tsv`, `round10/results/*/bench/`) only. Never anything about
`songer_treat` or `brace_hall_state` (closed, DESIGN10 §0.3).

## Background
v9c SCDB h0: recall 1,808/2,407 = 75.1%, precision 97.5%, clean 97.4%; the slowest-moving key (round 8 → 9: −1).
Round 9 (`round9/agents/scdb9/`: NOTES.md, `anatomy9.py`, `sc9.py`, `select9.py`, `deltas9.py`, `dump8.py`,
`work/`; round 8 `round8/agents/scdb8/`): anatomy of the h0 misses — **no_anchor:below_cand 129** (the Supreme Court
opinion cites the decision below, but no accepted anchor ties the citation to "the court below / the Court of
Appeals" in the history zone: bare citations, footnote-only citations, fact/quote support citations, the court named
too far away, court-pronoun subjects "It reversed … cite"), row_not_in_base 99, no_disposition ~50. Round 9
installed a9 / r4w / wfix (4 rows); its judgment readings (dfix / j / multi9, 46 rows) were NOT installed: whole-class
audit r9b01 26/30 = 0.867, and the cut that fixes it was designed on that audit's errors (D9-11) — a version of those
readings may be re-audited only on a fresh sample (exclude r9b01) or on new rows that the round-10 rule produces.
Round 9 also found `sc8sel.py` used an undefined `WEAK` (620 SC opinions produced no row): fixed in scdb9's copy —
check whether the fix reached v9c and what those 620 opinions yield now.

## Do
1. Re-run the anatomy on v9c (`anatomy9.py` copied). Read a stratified sample (~40) of no_anchor misses with opus
   readers (corpus text only): where is the decision below cited (syllabus / head matter "certiorari to …", opening
   paragraph, footnote 1, a "Reported below" line, the judgment line), and what ties it to the judgment.
2. Rules (general, all Supreme Court opinions): the decision below identified by the opinion's own text outside the
   history zone — (i) the opening paragraph's "We granted certiorari to review the judgment of the Court of Appeals …
   [cite]" / "the Court of Appeals … held … [cite]" sentence; (ii) footnote citations whose footnote is attached to a
   sentence naming the court below; (iii) the docket/caption of the case below matching the SC caption ("sub nom.",
   party tokens) and the circuit; combined with the opinion's own judgment line ("The judgment of the Court of
   Appeals is reversed"). Anchor quotes must be inside the opinion zones (round-9 part zones refuse syllabus/head
   matter as evidence: "Reported below" in head matter is the reporter's — check how the round-9 Lean treats an
   anchor quote there: anchors are not zone-checked, but the evidence rule DESIGN10 §0.6 still applies; ask the lead
   if unsure). Use the `anchor` / `anchorWide` / `bridge` mechanisms of the round-9 Lean; else `LEAN_REQUEST.md`.
3. Certify, stage, run (NOBUILD), score (`noold`): precision / clean / Shepardized dev (sc_reversed) must not drop.
4. Blind audit each status-changing class (≥ 80 or whole class, two auditors, decoys; link + effect). Install at ≥ ~90%.
Report: anatomy on v9c, rules, rows, audits with intervals, delta folders, h0/dev effect. Time box ~100 minutes.
