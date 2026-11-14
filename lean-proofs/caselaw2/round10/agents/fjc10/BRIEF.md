# Agent `fjc10` (round 10): FJC appeals — "named other case", one-side captions, which ruling is under review (move 3)

Read `round10/DESIGN10.md` and `round10/agents/COMMON.md` first. Folder `round10/agents/fjc10/` (NOTES.md). Audit
letter `f`. You may read `benchmarks/fjc_idb_appeals/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files
(`round9/results/v9c/bench/fjc_idb_appeals.h0.cases.tsv`, `round10/results/*/bench/`) only. Never anything about
`songer_treat` or `brace_hall_state` (closed, DESIGN10 §0.3).

## Background
v9c FJC h0: recall 1,564/2,832 = 55.2%, precision 90.4%, clean 97.6%. Round 9 (`round9/agents/fjc9/`: NOTES.md,
`fjc9_link.py`, `diag.py`, `f1why.py`, `funnel.py`, `gpeek.py`, `read1/`; round 8 `round8/agents/fjc8/`) installed W
(anchor widened, 0.900) and J (judge-form anchors, 0.900); G / G2 (guard exceptions) failed at 0.81 / 0.84 because
word-level exemptions do not identify **which ruling is under review** (errors: injunction appeal vs a later final
judgment / contempt order; own-remand into a separate suit; unappealed parts; affirmed). Remaining v8e-traced miss
stages: no_court_phrase (partly fixed), **named_other_case 282** (the citation sentence names a different case than
the one under review — e.g. the decision below is cited as authority in another case's name, or the caption under
review differs from the district caption), **one_side 29–64** (one-side captions; round 8's F2 failed at 62/80),
row exists 139, later/earlier/interlocutory guards ~200, signal 67.

## Do
1. Re-trace the v9c h0 misses by stage (fjc9's `diag.py` against v9c). Read a stratified sample (~40) of the
   named_other_case and one_side misses with opus readers (corpus text only) to see the forms.
2. Rules (general, corpus-wide over all CoA opinions):
   (a) **citation-level identity of the ruling under review**: the district decision under review is the one whose
   docket / caption / date matches the appeal (the CoA opinion's own caption and docket line, "appeal from the
   United States District Court for … No. …", the district judge named in head matter), not the one named in the
   citation sentence's case name; a decision cited inside another case's name is not the decision under review unless
   the docket/date ties it. Use this test both to admit named-other-case misses and to give G/G2's exemptions the
   ruling identity they lacked (a re-run of a G-like class needs a fresh audit sample, excluding r9f01/r9f03's).
   (b) **one-side captions**: admit only with a second tie (docket or district judge or date of the ruling below).
   Keep rows checkable by the round-9 Lean (anchor / anchorWide claims); else `LEAN_REQUEST.md`.
3. Certify (`round10/certify10.py`), stage, run (NOBUILD), score (`noold`): precision / clean / Shepardized dev must
   not drop.
4. Blind audit each status-changing class (≥ 80, two auditors, decoys; link + effect). Install at ≥ ~90%.
Report: miss anatomy on v9c (counts), rules, rows per class, audits with intervals, delta folders, h0/dev effect.
Time box ~100 minutes.
