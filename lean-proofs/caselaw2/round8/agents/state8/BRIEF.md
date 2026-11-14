# Agent `state8` (round 8, move 5): state-court reading and coverage gaps

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/state8/` (NOTES.md).
You may read `benchmarks/state_overruled_tables/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files under
`round8/results/*/bench/` only (never `benchmarks/state_overruled_tables/key.tsv`, `links.tsv`, `work/`, `raw/`,
`results/`, `secondary_pairs.tsv`). Agent `multicase` owns sentences naming several cases under one act; you own the rest.

## Background
State-table recall: round 6 h0 11/132 (8.3%); round 7 6.9% overall, every hit Georgia. DISAGREEMENTS (round 6, 30
read): 16 real model misses (9 explicit: "is overruled by the case of Y" (a third case as overruler), "Any holding
in X … is, on review thereof, overruled", "distinctly disapproved", "hereby expressly overruled", overrulings in
rehearing sections; 7 implicit but plain), 10 table errors, 1 link error. Pre-1930 California, New York, Georgia
reporters: nominative reporters ("3 Kelly 17"), "Abb. N. Cas.", early "Cal." volumes, Ga. Court of Appeals vs Ga.
Supreme Court, NY Court of Appeals vs general term / Supreme Court.

## Do
1. On h0 only (after `round8/bench_h0/READY`), take the state-table misses from
   `round8/results/v3/bench/state_overruled_tables.h0.cases.tsv` and, for each, find where the pipeline loses it:
   (a) Y not in corpus / X not in corpus; (b) Y's text never cites X in a form the citation reader resolves
   (reporter alias, nominative reporter, page-cite); (c) the sentence is found but no reader cue matches; (d) a cue
   matches but the certificate fails (verdict in `round7/out/v3/certs.tsv`: which check — noAuthority means the
   court-hierarchy table lacks the edge); (e) admitted but the status rule drops it. Count per stage (counts, not
   rows, in NOTES).
2. Fix the largest causes with general rules: citation aliases for old state reporters (extend the round-6
   `citeforms/` approach; audited alias list), court hierarchy edges in the court tables (`courts2.tsv`,
   `court_alias.tsv`, `succession.tsv` — check what the Lean authority check reads; a data-table change is a staged
   table, and if a Lean change is needed write `LEAN_REQUEST.md`), reader cue forms that are explicit own acts
   ("is hereby (expressly) overruled", "distinctly disapproved", "is, on review, overruled", "any holding in X …
   is overruled"), and rehearing sections. Run each rule over the whole corpus (state and federal), count.
3. Certify (certify8) into delta folders per rule; measure (state-tables h0, fresh dev, holdout notes, no-leak). Blind
   audit each status-changing rule class (≥ 80, stratified, decoys) via `round8/audit/HOWTO.md`; install at ≥ ~90%.
   Citation aliases: audit the alias list itself (each alias read against a text where it occurs).

Final report: miss anatomy (counts per stage), rules, counts, audits, delta folders, h0/dev effect.
