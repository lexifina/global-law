# Agent `multicase` (round 8, move 4): one act overruling several named cases

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/multicase/` (NOTES.md).
You may read `benchmarks/state_overruled_tables/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files
under `round8/results/*/bench/` only. Agent `state8` works on the other state-court gaps; you own sentences that
name two or more cases under one act.

## Background
State-table recall is low (round 6 h0: 11/132; round 7 overall 6.9%, all hits Georgia). The DISAGREEMENTS reading
found explicit overrulings the reader misses, chiefly lists: "The rulings in Overstreet v. Sullivan, Smith v.
McWhorter, and Seaboard A. L. Ry. v. Simmerville … are overruled in so far as they hold …" (148 Ga. 376). Round-7
reader/certifier rules: `round7/DESIGN7.md` §2 (joined), the plain certificate in `round7/certify7.py` (which
phrase checks, length and distance limits a quote meets; how the target evidence must resolve inside the quote).

## Do
1. Find the general form corpus-wide: sentences (or a sentence + its predecessor) in an opinion-of-the-court part
   with an overruling / disapproval act of the court itself and ≥ 2 case names or citations as its object (lists
   with commas / "and", "the cases of A and B", "A, B, C, and the cases following them", "so far as they conflict …",
   "and all cases holding otherwise" — only named ones become rows). Use the round-6 cache and existing treatments
   reader outputs to find candidates; count by court, decade, state/federal.
2. For each named case: resolve the name/citation to one corpus decision (same rules as the treatments reader:
   citation key → node, else name tokens unique in the citing decision's citation list); one row per case with the
   same main quote; scope partial when the sentence limits ("in so far as", "to the extent") — DESIGN7 §6. Check
   with certify8 which of these rows the round-7 checker admits; if a structural limit refuses correct rows (quote
   length, evidence must be the only/nearest name, cue distance), write `LEAN_REQUEST.md` with the narrowest change.
   Where the rule is unclear on a sentence form, read with opus reader sub-agents (brief in your folder).
3. Diagnose on h0 only (after `round8/bench_h0/READY`: `round8/results/v3/bench/state_overruled_tables.h0.cases.tsv`):
   which h0 misses are list sentences, and does your rule reach them (report counts, not rows; never use a key row as
   input). Measure the effect on state-tables h0, fresh dev, holdout notes.
4. Blind audit (≥ 80, stratified by state/federal and decade, decoys) via `round8/audit/HOWTO.md`; install at ≥ ~90%.

Final report: the rule, counts, audit, delta folder, h0/dev effect, any LEAN_REQUEST.
