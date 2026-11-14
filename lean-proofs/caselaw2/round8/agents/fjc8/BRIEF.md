# Agent `fjc8` (round 8): courts of appeals reversing district decisions (FJC IDB appeals, h0 diagnosis)

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/fjc8/` (NOTES.md).
You may read `benchmarks/fjc_idb_appeals/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files under
`round8/results/*/bench/` only (never its `key.tsv`, `key_nodes.tsv`, `work/`, `raw/`, `results/`).

## Background
FJC IDB appeals (round 6, h0): recall 1,418/2,832 = 50.1% (district decision reversed/vacated → model NEG_HIST),
precision 90.0%, clean 97.7%. DISAGREEMENTS (round 6, both halves, 30 read): of the misses, 11/18 model missing —
the appellate opinion plainly reverses or vacates the district ruling and cites it ("Its judgment must be reversed
… REVERSED AND REMANDED", "We REVERSE the district court's grant of summary judgment and REMAND", "we will vacate
its order, remand"), yet **2,389 of 2,830 misses have no history row of any kind targeting the district
decision** although the appellate opinion cites it; 3/18 had the right row but scope unknown (UNK_HIST) for a
whole reversal ("VACATED and Appellant's appeal is DISMISSED"). False positives: wrong-ruling attachment (a docket
with several published rulings), reversal of a later ruling credited to an earlier one, panel vacatur itself
vacated en banc. Linkers: `round6/history/rules/below_other` (decision below in a reviewing court's opinion:
procedural-history sentence, judgment line), `rules/guard` (wrong decision of a litigation), round-7
`round7/agents/b4sc/` (B4 a/e for the Supreme Court).

## Do
1. After `round8/bench_h0/READY`: from `round8/results/v3/bench/fjc_idb_appeals.h0.cases.tsv`, find the h0 misses;
   for a stratified random sample of ~40 (by decade, civil/criminal), read the appellate opinion (corpus) and record
   where the pipeline loses each: no candidate (the below_other linker never proposes the district decision: why —
   the opinion names the district ruling only as "the district court" and cites it in the procedural history?
   the citation is in a footnote? an F. Supp. cite the reader does not key?), candidate but no cue match, cue but
   certificate refused (verdict in `round7/out/v3/certs.tsv`), scope unknown on a whole judgment. Counts in NOTES.
2. Write general rules for the largest causes (e.g. "the decision below = the unique district decision of the same
   litigation that the appellate opinion cites, when the opinion's own judgment line reverses/vacates 'the district
   court's judgment/order'"; whole scope when the judgment line has no partial marker), run them corpus-wide over
   every court of appeals opinion (not only key cases), guard them (the round-6 guard: later/earlier rulings of the
   same docket), certify8 (anchored history rows as round 6/7). Read with opus sub-agents where the rule needs
   judgment.
3. Measure (stage/run/score): FJC h0 recall / precision / clean / part, Shepardized dev (CLEAN kept clean), SCDB h0.
   Blind audit each status-changing class (≥ 80, stratified, decoys; link + effect) via `round8/audit/HOWTO.md`;
   install at ≥ ~90%.

Final report: miss anatomy (counts), rules, counts, audits, delta folders, h0/dev effect.
