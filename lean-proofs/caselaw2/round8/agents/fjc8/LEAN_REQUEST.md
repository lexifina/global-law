# fjc8 LEAN_REQUEST: the old Fifth Circuit's power over the district courts of the Eleventh (and the old Eighth over the Tenth)

## Rule
Before 1 October 1981 the district courts of Alabama, Florida and Georgia were in the Fifth
Circuit (Fifth Circuit Court of Appeals Reorganization Act of 1980, Pub. L. 96-452, effective 1 Oct 1981). Before
the Tenth Circuit was created (Act of 28 Feb 1929, 45 Stat. 1346), the district courts of Colorado, Kansas, New
Mexico, Oklahoma, Utah and Wyoming were in the Eighth Circuit. A decision of the Court of Appeals for the Fifth
(Eighth) Circuit dated before that day that reverses / vacates / affirms a decision of one of those district courts
acts with power over it.

## The check that refuses it today
`Spec/Authority.lean` `canChangeStatus`, `higherCourt` branch: `!B.federal || B.tier != .appellate || X.circuit ==
B.circuit || …`. `X.circuit` is the target court's epoch circuit from `courts2.tsv`, which gives those district
courts circuit 11 (10) for all dates. The round-6 linker already applies the rule (`below_other/link.py`
`circuit_ok`: "the old Fifth Circuit includes the Eleventh before 1 Oct 1981, the old Eighth the Tenth before 1929").

## Effect (round7/out/v3, base rows refused `noAuthority`)
- ca5 acting on ca11-district targets, acting date before 1981-10-01: 603 history rows (169 reversed / vacated, 434
  affirmed / other); ca8 on ca10-district before 1929: 10 rows. (Other cross-circuit `noAuthority` rows are wrong
  links and stay refused.)
- fjc8's own delta (`delta_b`): 48 rows refused `noAuthority`, the same pattern.
- FJC IDB h0: 14 h0 NEG misses carry a reversed/vacated `all` row of the right appellate opinion refused
  `noAuthority` for this reason (plus fjc8's refused rows).

## Two ways to implement (lead / lean8 decide)
1. Data only (no Lean change): split the epochs of those district courts in `courts2.tsv` at 1981-10-01 (1929-03-01
   for the Tenth), circuit 5 (8) before. This also changes vertical precedent for those dates (historically right:
   the old Fifth's decisions bound them), so it moves more than history rows.
2. Lean: in the `higherCourt` branch accept `X.circuit == 11 && B.circuit == 5 && b.date < 19811001` and
   `X.circuit == 10 && B.circuit == 8 && b.date < 19290301` (new RuleId, e.g. `.oldCircuit`), history only.
   Theorem: as `canChangeStatus_higherCourt`, with the date premise; round-7 mode by presence is kept if the clause is
   gated on a round-8 flag/table.
