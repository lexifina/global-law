# Agent `fjc9` (round 9): FJC appeals, citation sentence without the court + guard misfires (move 1)

Read `round9/DESIGN9.md` and `round9/agents/COMMON.md` first. Folder `round9/agents/fjc9/` (NOTES.md). You may read
`benchmarks/fjc_idb_appeals/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files
(`round8/results/v8e/bench/fjc_idb_appeals.h0.cases.tsv`, `round9/results/*/bench/`) only.

## Background
v8e FJC h0: recall 1,536/2,832 = 54.2%, precision 90.3%, clean 97.6%, part 41.0%. Round 8 (`round8/agents/fjc8/`:
NOTES.md, `diag.py`, `fjc_link.py`, `gfeat8.py`, `guard8.py`, `funnel.py`, `read1/`) traced 1,414 v3 misses:
**no_court_phrase 405** (the citation sentence does not name the district court; the court is named 1–3 sentences
earlier, after a quote, in a footnote; the sentence splitter cuts at abbreviations so "previous sentence" is often a
fragment), named_other_case 282, linker row exists 139, later_events 92 + earlier_proceeding 63 + interlocutory 55
(the round-6 earlier/later/interlocutory word guards; 8 of 33 read misses were these guards firing on the decision
under review's OWN procedural-history narrative), signal 67, … F1 (installed; r8f05 73/80) covers part of
no_court_phrase via an extended anchor; F2 (one-side captions, 62/80) was not installed.

## Do
1. Re-trace the v8e h0 misses (`diag.py trace` copied, against v8e) and count by stage; read a fresh stratified
   sample of ~40 of the no-court-phrase and guard-fired misses with opus readers to see the forms.
2. Rules (general, corpus-wide over all 546,328 CoA opinions):
   (a) **anchor widening**: the district court identified by a sentence-aware window (a real sentence splitter that
   does not cut at legal abbreviations; the court named in the same paragraph before the citation, or in the
   citation's own footnote), with the opinion's own judgment line reversing/vacating "the district court's
   judgment/order", the unique district decision of the circuit cited with the caption, etc. — check the anchor
   is expressible with the round-8 Lean (`anchor` / `anchorWide` claim lists, ≤ the anchor quote rules); if not,
   LEAN_REQUEST.
   (b) **guard exception**: the earlier/later/interlocutory guards should not fire when the guard word describes
   the decision under review's own procedural history (e.g. "the district court later granted summary judgment …
   We reverse") — define the exception by sentence structure (the guard word's ruling is the one the judgment line
   disposes of / the cited decision's date equals the reviewed ruling's date), never by key case.
3. Certify (`round9/certify9.py`), stage, run (NOBUILD), score; check precision/clean/Shepardized dev don't drop.
   Blind audit each status-changing class (≥ 80, two auditors, decoys; link + effect); install at ≥ ~90%.
Report: miss anatomy (counts), rules, counts, audits with intervals, delta folders, h0/dev effect.
