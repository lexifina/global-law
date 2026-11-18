/-!
# tax-kalculator: the £100,000 taper for the 2020-21 default code

ITA 2007 s. 35 as in force for 2020-21 (legislation.gov.uk, point in time 6 April 2020):
(1) "a personal allowance of £12,500"; (2) "For an individual whose adjusted net income exceeds £100,000, the
allowance under subsection (1) is reduced by one-half of the excess"; (3) a remainder that is not a multiple of £1 is
rounded up. s. 10 (same date): "(5) The basic rate limit is £37,500. (5A) The higher rate limit is £150,000."

tax-kalculator 2.16.1 applies the taper only when the code ends with `TaxCode.getDefaultTaxCode()`, which defaults
to the *current* tax year's code (1257L), not the requested year's. For `taxYear = 2020` the default code is "1250L"
(`CalculatorUtils.defaultTaxCode(2020)`), so no taper is applied: £120,000, 1250L, `userSuppliedTaxCode = false`
returns tax £35,496.40 with tax-free amount £12,500.

Amounts in pence; proofs by kernel computation (`decide`). Lean 4 core only.
-/

namespace KalcDefaultCode

set_option maxRecDepth 100000

/-- s. 35(1)-(3), 2020-21 (pounds). -/
def personalAllowance2020 (ani : Nat) : Nat :=
  -- reduced by half the excess; the remainder rounded up to £1, i.e. 12,500 − ⌊excess / 2⌋, not below 0
  if ani ≤ 100000 then 12500 else 12500 - min 12500 ((ani - 100000) / 2)

/-- 2020-21 rates on taxable income (pence): 20 % to £37,500, 40 % to £150,000, 45 % above. -/
def tax2020 (t : Nat) : Nat :=
  20 * min t 37500 + 40 * (min t 150000 - min t 37500) + 45 * (t - min t 150000)

/-- The statute: £120,000 → allowance £2,500, tax £39,500.00. -/
theorem statute_120000 : personalAllowance2020 120000 = 2500 ∧ tax2020 (120000 - 2500) = 3950000 := by decide

/-- The library's own convention (PAYE Free Pay £12,509 for 1250L, taper unrounded) would give £39,496.40;
without the taper it gives £35,496.40, £4,003.60 less than the statute. -/
theorem kalculator_120000 :
    tax2020 (120000 - (12509 - 10000)) = 3949640 ∧ tax2020 (120000 - 12509) = 3549640 ∧
    3950000 - 3549640 = 400360 := by decide

/-- The general rule over £100,100 … £150,000 (step £100): without the taper the result is too low by the withdrawn
allowance at 40 % (half the excess over £100,000, up to £12,500; so up to £5,000 of tax). -/
theorem missing_taper :
    ∀ i, i < 500 →
      tax2020 (100100 + 100 * i - personalAllowance2020 (100100 + 100 * i)) - tax2020 (100100 + 100 * i - 12500)
        = 40 * (12500 - personalAllowance2020 (100100 + 100 * i)) := by
  decide

end KalcDefaultCode
