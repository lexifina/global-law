# Agent `fedcir11` (round 11): a Federal Circuit review linker — the FJC linker ported to the Court of Appeals for the Federal Circuit (move 2)

Read `round11/DESIGN11.md` (§0 — rule 3: `benchmarks/fedcir_dataset/` (and `songer_treat/`, `brace_hall_state/`)
is CLOSED to you: never open, list or grep it, not even its docs; you diagnose on corpus text only) and
`round11/agents/COMMON.md`. Folder `round11/agents/fedcir11/` (NOTES.md, a line every 10 minutes). Audit letter `c`.
You may read `benchmarks/fjc_idb_appeals/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and its h0 per-case file
(`round10/results/v10d/bench/fjc_idb_appeals.h0.cases.tsv`) — only to check side effects.

## The relation
The Federal Circuit (and its predecessors, the Court of Customs and Patent Appeals and the Court of Claims'
appellate side, if the corpus has them — check) reviews decisions of the federal district courts (patent, Little
Tucker Act, …; any district in the country), the Court of Federal Claims (formerly U.S. Claims Court), the Court of
International Trade (formerly Customs Court), the Court of Appeals for Veterans Claims, and boards / agencies (PTAB /
BPAI / TTAB, ITC, MSPB, boards of contract appeals). When it reverses / vacates / modifies a decision **that is in
the corpus**, that decision should carry a `neg:*` history status at the as-of date; affirmed → nothing negative.
Agency / board decisions are rarely corpus nodes — measure it. The round-8–10 FJC linker targets regional circuits
reviewing district courts; nothing so far targets the Federal Circuit.

## Do
1. **Corpus-intrinsic diagnosis (no key).** From `graph/nodes.tsv` / `round10/stage/v10d/decisions2.tsv` /
   `courts2.tsv`: find the Federal Circuit repo(s) and the repos of its lower tribunals (district courts, Claims,
   CIT, CAVC, any board repos). Population: Federal Circuit opinions whose own judgment line (majority / per curiam /
   the "AFFIRMED", "REVERSED AND REMANDED", "VACATED AND REMANDED", "AFFIRMED-IN-PART, REVERSED-IN-PART" end lines
   and Rule 36 judgments) disposes of the decision below, and that cite or caption-match a corpus decision of the
   tribunal below dated before them (5-year window). Measure in v10d (`round10/out/v10d/status.tsv`, `certs.tsv`,
   `round10/stage/v10d/history.tsv`) what share is marked, and trace the unmarked through the round-6 history stages
   (`round6/history/`, `round8/agents/fjc8/diag.py`-style) to find why. Read a stratified sample (~40 pairs: tribunal ×
   decade × cited/uncited × marked/unmarked) with opus readers (corpus text only).
2. **Rules**, general and corpus-wide over Federal Circuit opinions: port the FJC linker — round 8 `fjc8`
   (`round8/agents/fjc8/`: `fjc_link.py`, `guard8.py`, `gfeat8.py`), round 9 `fjc9` (`round9/agents/fjc9/fjc9_link.py`:
   F1, W (anchor widened to the court named up to 4,000 chars back in the same part), J (judge-form anchors under
   claim `anchorWide`), round 10 `fjc10b` (`round10/agents/fjc10b/fjc10_link.py`: N form h (district caption tied by
   the appeal's head-matter caption) + rule P (partial scope)) — to the Federal Circuit: tribunal names as the anchor
   ("district court", "Court of Federal Claims", "Claims Court", "Court of International Trade", "Veterans Court",
   "the Board", "the Commission", "the trial court", "the court below"), the decision below identified by citation or
   by the appeal's head-matter caption ("Appeal from the United States District Court for the District of Delaware in
   No. 1:10-cv-…, Judge …") + date + docket against the tribunal's repo, the judgment line as disposition, the
   round-6 guards, and the latest decision below in the same case. Effects: reversed / vacated → neg history rows of
   the right scope (rule P: "affirmed-in-part" → unknown / partial); affirmed → no negative row.
   **Lean:** the Lean's anchor cue list (`global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json`, read only)
   holds "district court", "trial court", "court below", … but probably not "court of federal claims", "court of
   international trade", "board". Rows whose anchor needs a phrase the round-10 Lean lacks: write `LEAN_REQUEST.md`
   (a new claim value with its own presence-gated anchor list — existing lists must not change, since that would
   change round-10 verdicts) early, with the exact phrase list and counts, and continue with the rows that certify
   today.
3. Certify (`round11/certify11.py`), stage, run (NOBUILD), score (`noold`): FJC h0 precision / clean, Shepardized dev
   precision / CLEAN and holdout history must not drop.
4. Blind corpus-wide audit per status-changing class (≥ 80, two opus auditors, decoys; item type B). Install bar ~0.90
   on "right" (exact kind + scope).
Report: tribunals and their corpus presence (counts), population and miss anatomy, rules, rows per class, audits
with intervals, delta folders, side effects vs v10d, LEAN_REQUEST if any, headroom (what cannot be linked and why).
