# Hunt2: circular rules and state interactions — findings (2026-11-16)

Lean files: `Circular.lean`,
`StateLoop.lean`, `Community.lean` (each `import Std`, kernel-checked, no `native_decide`). Scratch and outputs:
`tools/hunt/out/Hunt2/` (incl. `conformity.json`, `conformity.md`). Counts: 10 plans judged, 22 theorems.

## CANDIDATE: two lawful answers at the poverty-line floor (2025 and 2026)

Self-employed person on a Marketplace plan, no advance credit, household income before the §162(l) deduction between
the poverty line (100% FPL) and 100% FPL + premium. The statute admits two consistent answers:
full §162(l) deduction and no PTC, or the PTC with the deduction reduced by it (§36B(c)(1)(A), §162(l), §280C(g)).

- Pub. 974's iterative and simplified methods both say "Cannot take the PTC… stop here", which reaches only the
  no-credit answer; Pub. 974 and Rev. Proc. 2014-41 §3 also accept any method that satisfies the rules.
- Size: single, 2026, $14,000 benchmark plan: the credit answer is worth $11,800–$13,600 more; $7,500 plan: about
  $6,800–$7,100. In 2025 the credit covers the whole premium. Open earlier years can be amended.
- Limits: not for anyone Medicaid-eligible; any advance credit removes the choice (Reg. §1.36B-2(b)(6)).
- Red team: T1 partial and T8 partial (Reg. §1.162(l)-1 and the 2026 Pub. 974 not read); T2, T3, T5, T6, T7 pass;
  T6: every claim is a kernel-checked theorem. Nothing published found; a forum hint suggests some software may
  already reach the credit answer.

## Structural result: 2026 band with no lawful answer

Near 400% FPL there is an income band where no fixed point exists: from $68,840 to premium + $62,599, single
($7,760 wide for a $14,000 plan). The IRS iteration cycles between two values. The fallback method claims no credit and
a deduction about $7,800 below an admissible one (deduction = income − $62,601, no credit). That the iteration fails
near the cliff is known; the exact band is new. A similar smaller gap sits at 133% FPL. Anyone using an IRA, SEP or
HSA contribution to get under the cliff needs about $7,765 more than the simple calculation suggests.

## VARIANTs (small)

- §163(h)(4) car-loan interest: in community-property states a couple deducts $20,000 on separate returns instead of
  $10,000 joint; separate filing costs nothing in rates there (proved for the 2026 rate schedule). Sources disagree on
  whether separate filers qualify at all.
- Separate-return SALT reading (NewDeductions plan 1) extends to unequal earners in community-property states.

## KNOWN / nothing new

- Federal–state deduction loop (AL, MO, OR): unique answer, settles in 2–4 rounds; only lever is paying state tax in
  December (known).
- Community property and §1411: kills the known "split wages and investment income across separate returns" plan,
  except for separate-property income in CA/AZ/NV/NM/WA.
- State choices: DC/GA forcing the federal itemizing choice, and employer dependent-care plan vs credit: known.
- PTET: not modelled; each $1 restores $0.30 of SALT cap between $500k and $600k MAGI; classed known.

## PolicyEngine-US 2.138.1 bugs

- `self_employed_health_insurance_ald_person.py` ignores §280C(g): deducts the full premium and gives the credit on top.
- In a batched Simulation, setting `tax_unit_itemizes` on some tax units sets every other unit to `False`
  (a $400k Virginia filer shows $104,035 instead of $101,763).

## Gaps

The 51-row conformity table exists, but only Iowa's starting point is verified from an official page; the rest are
marked unverified, the rolling/static conformity column is blank, and the tips/overtime/HSA columns reflect
PolicyEngine behaviour, not checked law. The conformity-driven PolicyEngine search therefore did not produce verified
state plans.

## Sources checked

Kitces (PTC/SEHI), Iowa DOR conformity page, Intuit ProConnect community note, Spidell, Drake KB 18926, RSM on PTET,
Cornell LII 26 CFR 1.162(l)-1.
