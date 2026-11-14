# Agent `state9` (round 9): state overruled tables — implicit overruling, far joined quotes, doctrine own-tie (move 5)

Read `round9/DESIGN9.md` and `round9/agents/COMMON.md` first. Folder `round9/agents/state9/` (NOTES.md). You may read
`benchmarks/state_overruled_tables/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files
(`round8/results/v8e/bench/state_overruled_tables.h0.cases.tsv`, `round9/results/*/bench/`) only.

## Background
v8e state tables h0 recall 17/132 = 12.9% (h1 did not replicate the round-8 gain: 11/142). Round 8: `state8`
(NOTES.md, reader repairs R8S), `multicase` (MC-OWN), `notarget` (43,312 no-target sentences; 3,914 "far" items with
the target more than 300 chars from the act sentence — beyond the joined-quote gap bound `joined_gap_max` = 300 of
DESIGN7 §2.1–2.2), `doctrine8` (own-tie rule ~57 rows, conflicts with the Lean `doctrine_unique` corpus-wide label
uniqueness). Of 154 h0 pairs, 97 have no act sentence near X: **implicit overruling** (the later court decides
contrary to X without saying "overruled").

## Do (three parts; report each separately; start with A)
A. **At-risk implicit class.** Find how the Lean/model represents a non-status-changing negative signal today (read
   `round7/DESIGN7.md`, the cue table `tools/caselaw2/cues/cue_table.json`, `round5/` designs: is there a kind or
   class that yields `atRisk` without changing status — e.g. questioned / criticized / limited / doctrine rows,
   `doctrine_never_neg`?). Design an "implicit overruling, at-risk only" class: the later court's own words reject X's
   holding or rule (e.g. "we decline to follow X", "X's reasoning … is no longer sound", "to the extent X holds …, we
   disagree", "contrary to X", "X … has been undermined") — never status-changing beyond at-risk unless a court with
   power later says so. Corpus-wide candidates, opus readers, certify, its own blind audit (≥ 80, two auditors,
   decoys; measure: does the acting court itself reject / depart from X's rule?). If the class needs a Lean change
   (a kind / class value that can only reach atRisk), LEAN_REQUEST with theorem (`<class>_never_neg`).
B. **Joined gap > 300.** From notarget's 3,914 far items (`round8/agents/notarget/`): the distribution of gaps where
   a reader says the act names X; propose a bound (or a structural relation: same paragraph, no other index key
   between, an anaphor in the act sentence) as a LEAN_REQUEST with a stated theorem (the round-7 `joined` relation
   with the new bound, claim-gated so v8e is unchanged); read + audit the rows it would admit.
C. **Doctrine own-tie** (doctrine8's ~57 rows): per-court (or per-system) label uniqueness in place of corpus-wide
   uniqueness — LEAN_REQUEST if the measured yield justifies it (≥ 25 rows after reading), else stop and say why.
Measure on h0 (state tables) + holdout notes (holdoutOnly negOrPartly) + Shepardized dev clean.
Report: per part: design, counts, audits with intervals, delta folders, LEAN_REQUESTs, h0/dev effect.
