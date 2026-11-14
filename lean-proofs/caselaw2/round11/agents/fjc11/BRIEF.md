# Agent `fjc11` (round 11): FJC appeals — docket / judge / date ties combined with a caption tie (move 4)

Read `round11/DESIGN11.md` and `round11/agents/COMMON.md` first. Folder `round11/agents/fjc11/` (NOTES.md, a line
every 10 minutes). Audit letter `f`. You may read `benchmarks/fjc_idb_appeals/SOURCE.md`, `MAPPING.md`,
`DISAGREEMENTS.md` and the h0 files (`round10/results/v10d/bench/fjc_idb_appeals.h0.cases.tsv`,
`round11/results/*/bench/`) only. Never the closed keys.

## Background
v10d FJC h0: recall 1,595/2,832 = 56.3%, precision 90.5%, clean 97.5%. Round 10 `fjc10b`
(`round10/agents/fjc10b/`: NOTES.md, `fjc10_link.py`, `cycle10.sh`, `deltas.py`, `rows_n1.jsonl`, `link_stats_n1.json`,
`work/`) installed rule N form h + rule P (district caption tied by the appeal's head-matter caption; 1,317 rows,
0.912). **Not installed: forms x + s** (single or several district candidates tied by docket K, district judge U or
date T, with or without the head caption H; 1,486 rows; r10f12 57/80 = 0.713: "judge U / date T / docket K ties
without caption tie are unreliable: no-H 14/48 wrong, H+ 9/32"; errors: different case / earlier ruling 15, partial 4,
other kind 4). Also open in r10f13's errors: partial scope read as whole (3), consolidated / multi-defendant
affirmed-vs-reversed (2).

## Do
1. Re-run the N linker's x / s forms on v10d (copy `fjc10_link.py` into your folder) and split them by tie
   combination: H+K, H+U, H+T, K+U, K+T, H+K+U … Measure on the corpus (no key): agreement of ties, how often the tied
   candidate is the latest district decision of that docket before the appeal, sibling decisions of the same
   docket (an earlier interlocutory ruling, a later final judgment) and whether the appeal names WHICH ruling it
   reviews ("appeals from the order granting summary judgment", "from the judgment entered …", the date of the
   ruling below in the opinion). Read ~40 pairs per promising combination with opus readers (corpus text only).
2. Rule X2: a caption tie (H: the appeal's head-matter caption against the district caption, both sides) PLUS at
   least one of docket K / judge U / date T, with the ruling-under-review test (the latest district decision of that
   docket before the appeal unless the opinion names an earlier ruling; consolidated / multi-defendant appeals →
   scope unknown unless the judgment line names every party), and rule P. Keep rows checkable by the round-10 Lean.
3. Certify (`round11/certify11.py`), stage, run (NOBUILD), score (`noold`): FJC h0 precision / clean, Shepardized
   dev must not drop.
4. Blind corpus-wide audit (≥ 80, fresh sample excluding r10f11–13, two opus auditors, decoys; item type B). Install
   bar ~0.90 on "right". A cut designed on an audit's errors needs a fresh sample (D9-11).
Report: tie-combination counts and agreement, rules, rows, audits with intervals, delta folders, h0/dev effect vs
v10d, headroom left (FJC misses by reason).
