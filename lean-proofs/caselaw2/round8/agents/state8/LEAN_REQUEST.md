# state8 request (round 8): bench of a court that has at most three judges

Not a Lean code change: a data rule on `decisions2.tsv` (bench column), which `stage8.py` does not stage
("decisions2.tsv is never copied"). Sent to the lead to decide whether it is staged (and how) or left for a later round.

## Rule (BENCH-3)
A decision of an intermediate court (tier A) whose bench is `panel` or `unknown` only by default (decisions2 src
`b:default-tierA` / `b:-`) and whose court has at most 3 regular judges on its date (`court_size.tsv`, any tag) is
labelled `wholeCourt`: a court of three judges sitting in a panel of three sits as the whole court. This is the rule
`tools/caselaw2/bench_size_fix.py` already states ("value = wholeCourt ... for size <= 3"), applied without its
judge-names requirement (the old reporters print no judges line, so the round-2 rule never fired on them).

## Check (what Lean already does with it)
`Spec/Authority.lean` `benchRule`: a same-court overruling under a `strong` horizontal rule needs `enBancEquiv`,
which is true for `wholeCourt`. No theorem changes; the label is data (as every other bench label).

## Effect (counted on v3 + state8_v1, no key read)
- v3 treatments rows refused `noAuthority` whose acting court is the target's court with court size <= 3 at the
  acting date: 30 (Alabama Court of Appeals 1911-69 era: 20; a federal court of appeals with 3 judges: 10).
- state8_v1 (class R8S) rows refused `noAuthority`: 19, of which 1 has a 3-judge acting court (Ala. Ct. App. 1939).
- The other 18 R8S `noAuthority` rows are panels of larger intermediate courts (Florida DCA recede-from rows 8,
  Ga. Ct. App. 4, Ala. Ct. Civ. App. 2, La., Pa. Super., Tex.): correctly refused under the current rules; not part
  of this request. (One Ga. Ct. App. 1916 row says the ruling "is, on review, expressly overruled"; under the 1916
  Act review of a precedent was by the whole court, but a text cue for that is not proposed here.)
- State-table h0: none of the h0 misses reaches the certificate stage (miss anatomy in NOTES.md: (d) = 0), so this
  rule does not move state-table h0 recall; it is a correctness fix for small courts.

## Theorem needed
None new (`enBancEquiv` on `wholeCourt` is existing behaviour).
