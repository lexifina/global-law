# Differential test results (tax year 2025)

The Lean model (`TaxCode/Individual/Form1040.lean`) compared, household by household, with PolicyEngine-US 2.116.9,
Tax-Calculator 6.8.5 and UsTaxes (commit 49cd0f2, 7 Nov 2026). Tolerance $10. Data, outputs and reports live outside
git, in `tax-formalization-data/diff/`.

## Runs

| Set | Households | What varies |
|---|---|---|
| common | 2,000 (seed 7) | filing status, ages, dependents, wages, SE income, interest, dividends, gains, pensions, Social Security, unemployment, property tax, mortgage interest, charity, medical, child care |
| hard | 3,000 (seed 11) | the above plus separate returns, surviving spouses, blindness, student and adult dependents, tips, overtime, car-loan interest, IRA, HSA, student-loan and educator adjustments, tax-exempt interest, the saver's credit, the American opportunity credit, and high incomes with large gains (AMT, NIIT) |

Agreement with Lean (quantities within $10):

| Quantity | PolicyEngine (5,000) | Tax-Calculator (common / hard, comparable) | UsTaxes (common) |
|---|---|---|---|
| AGI | 5,000 / 5,000 | 2,000 / 2,000 · 2,667 / 2,667 | 1,951 / 2,000 |
| Taxable income | 5,000 | 1,998 · 2,663 / 2,667 | 1,953 |
| Tax before credits | 5,000 | 2,000 · 2,663 / 2,667 | 1,955 |
| EITC | 4,993 | 1,999 · 2,893 / 2,976 | 1,792 |
| Refundable CTC | 5,000 | 2,000 · 2,164 / 2,165 | 1,972 |
| Nonrefundable credits | 5,000 | 2,000 · 2,152 / 2,165 | — |
| Income tax after credits | 4,996 | 1,999 · 2,092 / 2,165 | 1,661 |

## Every remaining disagreement, by cause

**Lean vs PolicyEngine (7 households).** All are the EIC table. §32(f) has the Secretary publish tables whose $50 bands
use the midpoint, and the IRS EIC table does that. The Lean model reads the table; PolicyEngine and Tax-Calculator apply
the formula. The gap is up to $11 per household.

**Tax-Calculator (Lean and PolicyEngine agree with each other):**
- **Married filing separately, EITC and dependent-care credit:** it allows both. §32(d)(2) allows the EITC on a separate
  return only with a qualifying child and only if the spouses lived apart for the last six months (or were legally
  separated). §21(e)(2) has the same rule for the dependent-care credit. This covers 77 of the 83 EITC disagreements and
  most of the income-tax ones.
  - `calcfunctions.py:3293` checks `EITC_sep_filers_elig` only.
- **AMT on a separate return with large gains:** it computes none; Lean and PolicyEngine compute $14,881 (household 27).
- **Itemizing ties:** when itemizing gives a lower taxable income but the same tax (the gain is taxed at 0%, or credits
  absorb it), it takes the standard deduction. The tax is the same either way (common households 474 and 1804).
- **Settings, not errors:**
  - Without `exact_calculations` it phases the CTC and dependent-care credit out continuously instead of by "$1,000 (or
    fraction thereof)".
  - Its default records draw EITC/ACTC non-take-up at random.
  - It takes the student-loan, saver's and American opportunity amounts as inputs, so those households are not
    compared.

**UsTaxes:** 12 bugs, each confirmed by recomputing a household by hand. Paths are under `src/forms/Y2025/irsForms/`.
1. `F1040.ts` (constructor, around line 139) never attaches Schedule C, so self-employment income is dropped. The runner
   works around this by default.
2. `F1040.ts:226` takes QBI only from K-1s, so Schedule C profit is never QBI. The runner works around this by default.
3. `Schedule3.ts:50` `isNeeded` ignores Form 2441, so the dependent-care credit never reaches the return (about 104 of
   2,000 households).
4. `Schedule8812.ts:122`: Credit Limit Worksheet A is not floored at 0.
5. `ScheduleEIC.ts:142`: the age test (25–64 for childless filers) is a stub returning true.
6. `ScheduleEIC.ts:291`: the investment-income limit is skipped when there is no Form 4797.
7. `ScheduleEIC.ts:221`: the $50 band uses round, not floor.
8. `ScheduleEIC.ts:44`: a qualifying child is capped at the CTC age (under 17) instead of under 19.
9. `ScheduleEIC.ts:197`: earned income leaves out self-employment earnings.
10. `ScheduleSE.ts:90`: Social Security wages on line 8a sum both spouses' W-2s.
11. `worksheets/SocialSecurityBenefits.ts:47`: line 6 subtracts Schedule 1 line 10 (an income total in 2025).
12. `ScheduleA.ts:104`: no 60%-of-AGI limit on cash gifts.
13. `F8960.ts:100`: line 9b allocates real-estate tax, which is not a state income tax.
14. `worksheets/QualifyingDependents.ts:31`: the student and non-student age limits are swapped.

## Model fixes the differential test forced

- Schedule C profit is now QBI (less the deductible half of SE tax; Reg. §1.199A-3(b)(1)(vi)).
- §63(e): the return is computed both ways and the cheaper kept. Itemizing can win when it is smaller, because it lowers
  the AMT. Household 1085 owed $2,070 less this way.
- Before that, harness mappings were fixed: PolicyEngine's medical-premium imputation, its sales-tax imputation, the
  filing status, the CTC liability limit, and IRA contributions counting for the saver's credit.

## Not covered by any reference tool here

- The premium tax credit, because PolicyEngine derives benchmark premiums from location.
- The surviving-spouse status on Tax-Calculator.
- Everything outside the household fields (see `TaxCode/Individual/*/FINDINGS.md`, "Not modelled").
- TAXSIM-35 stops at tax year 2023.
- OpenTaxSolver 2025 is only distributed through a SourceForge page that refuses automated downloads.
