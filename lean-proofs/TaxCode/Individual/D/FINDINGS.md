# Group D: credits, tax year 2025: findings

Files (namespace `TaxCode.Individual.D`):
- `Basic`
- `ChildTaxCredit` (§24)
- `EarnedIncome` + `EICTableData` (§32)
- `DependentCare` (§21, 2025 and 2026)
- `Education` (§25A)
- `Saver` (§25B)
- `PremiumTaxCredit` (§36B: the 2025 statute, Form 8962, the 2025 repayment cap, 2026)
- `Ordering` (§26(a), `applyCredits`, `credits2025`)
- `Axioms`: `#print axioms` for all 71 theorems; each uses only propext, Classical.choice and Quot.sound, or none.

Build with `lake build TaxCode.Individual.D.Ordering`.

Sources: `usc26.xml` (OLRC 119-138) with its amendment and effective-date notes, and the 2025 IRS documents:
- Rev. Proc. 2024-40;
- Schedule 8812, Form 8962, Form 8863 and Form 2441 instructions;
- Pub. 596;
- Notice 2024-80;
- Rev. Proc. 2025-25, for 2026.

Confidence: **high** means proved in Lean on a clear reading of the statute; **medium** means it depends on a reading
that could be disputed.

## §24 child tax credit

1. **The statute and Schedule 8812 disagree on the refundable cap when there are other dependents.**
   - §24(h)(5) caps the refundable part at the qualifying-child credit after the phase-out. Schedule 8812 caps the
     unused combined CTC+ODC at n × $1,700.
   - The form is never below the statute (`form_ge_statute`) and can be above it (`form_exceeds_statute`).
   - Example: single, one child and one other dependent, MAGI $240,000, no tax left after a foreign tax credit. The
     statute gives $200 and the form $700.
   - Confidence: medium-high.
2. **"Or fraction thereof" notch.** The first $1 over $200,000 / $400,000 costs $50 (`ctc_notch_at_threshold`), and no
   single dollar costs more (`ctc_step_le_50`). The credit never rises with income and is never negative (`ctc_bounds`,
   `ctc_antitone`). High.
3. **The split stays within the maximum.** Nonrefundable plus ACTC is at most the credit after the phase-out, which is
   at most $2,200 per child plus $500 per other dependent. ACTC is at most $1,700 per child, under both statute and form
   (`ctc_split_le`, `actc_le_cap`, `actc_le_child_credit`). High.
4. **Taxpayer SSN (§24(h)(7)(A)(i), in force for 2025 under §70104(f)).** Without it, every child counts as a $500
   dependent, so two children go from $4,400 to $1,000 (`taxpayer_ssn_cost`). High.
5. **Surviving spouses.** A qualifying surviving spouse gets the $200,000 threshold, because §24(h)(3) says "joint
   return". This is not an inconsistency.

## §32 earned income credit

6. **The IRS table rule, reconstructed.** Each cell is the formula at the band midpoint, with the maximum rounded and
   the result rounded to the nearest dollar. A band containing a kink shows the maximum. This reproduces all 1,374 × 8
   cells, the footnoted partial bands and the worked example (`tableCheck`). High.
7. **Proved tight bounds, table minus exact statute:**

   | Children | Table minus statute |
   |---|---|
   | 0 | −$2.89 to +$2.575 |
   | 1 | −$7.66 to +$10.00 |
   | 2 | −$9.60 to +$12.00 |
   | 3+ | −$11.05 to +$13.50 |

   (`table_vs_statute_0..3`, `table_vs_statute_tight`). High.
8. **The table adds notches the statute lacks.** One dollar can cost $12: married filing jointly, 3+ children,
   $30,499 → $30,500 (`table_notch`, `table_step_le_12`).
9. **Worksheet A equals the statute's "AGI, or if greater earned income" rule** exactly, for every column
   (`worksheet_rule_exact`).
10. **Rounding the maximum.** Rev. Proc. 2024-40 rounds the 0-child maximum to $649, but the statute gives $649.485 and
    §32(j)(2) authorises no such rounding (`zero_child_tail`, `completed_phaseout_consistent`). High; the effect is
    cents.
11. **§32(i) cliff.** Going from $11,950 to $11,951 of investment income removes the whole credit, up to $8,046
    (`investment_income_cliff`, `table_le_max`). High.

## §21 dependent care credit

12. **The OLRC text is the 2026 text.** For 2025 the earlier text applies: 35%, less 1 point per $2,000 (or fraction)
    over $15,000, down to 20%. The model reproduces the Form 2441 decimal table. High.
13. **Notches in both years.** $60 for $1 at $15,001 (`cdcc2025_notch`, `cdcc2026_notch`, `cdcc2025_step_le_60`). The
    2026 rate is at least the 2025 rate everywhere (`cdcc2026_ge_2025`).

## §25A education credits

14. **No MAGI cliff.** One dollar of MAGI costs at most $1 (`eduPhase_step`, `eduPhase_bounds`).
15. **Form 8863's three-decimal ratio** is within $2 of the statute for a $2,500 AOTC (`form_vs_statute_aotc`).
16. **The §25A(i) kiddie-tax cliff** removes the $1,000 refundable part (`kiddie_cliff`).
17. **Timing.** The 2025 Act's SSN rule applies only after 2025.

## §25B saver's credit

18. **The tiers are cliffs.** A couple each contributing $2,000 gets $2,000 at $47,500, $800 at $47,501, $400 at
    $51,001 and $0 at $79,001 (`saver_cliffs`). The worst one-dollar loss is $600 per person
    (`saverPerson_step_le_600`).
19. **Notice 2024-80's figures** are exactly 75% and 50% of the joint figures, as §25B(b)(2) directs.
20. **Timing.** In the OLRC text, "$2,100" and the change to which contributions count apply only after 2026.

## §36B premium tax credit

21. **2025 is continuous above 100% FPL, with no 400% cliff.** One more dollar of income lowers the credit by between 0
    and 18.5¢ (`ptc2025_continuous`, `ptc2025_step`, `ptc2025_no_400_cliff`). High.
22. **The 2025 cliff is at 100% FPL** (`ptc2025_cliff_at_100`). It is softened by Treas. Reg. §1.36B-2(b)(6), which is
    not modelled.
23. **Form 8962 departs from the statute.** Its whole-percent truncation creates notches ($64 for $1 at 300%,
    `form_notch_2025`) and gaps of +$63 / −$11 against the statute (`form_vs_statute_2025`). These are search maxima,
    not proved bounds.
24. **The 2025 repayment cap has a 400% cliff, though the credit does not.** A single filer repays $1,625 at 399% and
    $5,000 at 400% (`repayment_cliff_2025`).
25. **In 2026 the 400% cliff returns** (`ptc2026_zero_above_400`, `ptc2026_cliff_400`): $5,765 becomes $0 for $1.
26. **The 2026 table itself jumps at 133%:** $217 for $1 (`ptc2026_jump_133`). The poverty line used in the 2026
    examples is unverified.

## Ordering

27. **The CTC is applied last though it sits on line 19.**
    - §26(a) fixes only the total: the amount used is min(tax, Σ credits) in any order
      (`nonrefundable_eq_min`, `nonrefundable_same_either_order`).
    - The refund does depend on order. Putting the CTC last is never worse (`forms_order_dominates`) and sometimes
      $1,000 better (`forms_order_strictly_better`).

## Not modelled

- **Fields missing from `Household`** (passed as arguments or left out):
  - taxpayer SSN, §129 exclusions, separated-spouse rules;
  - an incapable or student spouse, per-spouse amounts;
  - §25B distributions, scholarships, kiddie-tax status;
  - foreign tax credit, advance PTC;
  - Alaska and Hawaii poverty lines, coverage months.
- **Simplified:**
  - §36B is annual only, with no affordability test.
  - §32(i) leaves out rents, royalties and passive income.
  - §32 eligibility checks age, dependency and married filing separately only.
  - Disallowance periods and possessions rules are out.
- **Rounding:** nearest dollar wherever the forms round.

## Independent review (step 4)

The reviewer had not written this group.
- **Fixed in `Ordering.lean`: §36B(c)(1)(C)/(D).** `credits2025` allowed the premium tax credit on separate returns and
  to people who can be claimed as a dependent. It now returns 0 in both cases; the abuse/abandonment relief is not
  modelled. Three new checks.
- **Test added:** the Pub. 596 footnote for joint filers with no children ($26,200–$26,213 gives $1).
- **Withdrawn — the finding that the refund depends on the order of credits.** §24(d)(1)(B) measures the increase in the
  *aggregate* subpart A credits. `forms_order_matches_statute` proves that putting the CTC last gives
  min(cap, earned-income amount, all unused credits). The $1,000 gap came from a model counting only the unused CTC.
- **Downgraded:**
  - **Finding 10:** §32(f)(1) makes the Secretary's tables the legal amount, so the $649 rounding is authorised.
  - **Findings 7–8:** the $50-band "notches" are table-versus-formula differences that §32(f) allows.
- **Confirmed:**
  - CTC: findings 1–5. Schedule 8812 line 16a is line 12 minus line 14, with no child-only cap, while §24(h)(5) reads
    "without regard to paragraph (4)". New theorems: `actc_statute_eq_form_no_others` (the two agree when there are no
    other dependents) and `actc_full`.
  - EIC: findings 6, 9 and 11.
  - §21: findings 12–13.
  - Education and saver's credits: findings 14–20.
  - §36B: findings 21–26.
- **Not fixed:**
  - The §25A(g)(3) and §25B(c)(2)(A) dependent bars are not modelled, because `Household` records only "can be
    claimed".
  - Excess advance PTC repayment (`excessAptcTax2025`) is not wired into the assembly.
  - The §21 tests cite the Form 2441 line 12 table (prior-year expenses), but the rates are the same.
- **Weak theorems noted:** `eicScaled_bounds`, `actc_le_cap`, `actc_le_child_credit`, `ptc2026_zero_above_400`,
  `repayment_le` and the `*_bounds` theorems. They hold for a function returning 0 and are backed only by the fixed
  tests.
- **Verified against IRS sources:** the 2025 instructions and form for Schedule 8812, Pub. 596, the Form 8962
  instructions (Tables 1-1, 2 and 5) and the Form 2441 instructions.
