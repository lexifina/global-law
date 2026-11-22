import UkTax.Params

/-!
# Primary Class 1 contributions per pay period (SSCBA 1992 s. 8; S.I. 2001/1004 regs. 10, 11, 131)

The household model uses the annual earnings period. Employees are in fact charged per pay period with
"prescribed equivalents" of the thresholds (SSCBA 1992 s. 5(4)–(5)):

* weekly: the figures of reg. 10 (primary threshold £242, upper earnings limit £967);
* monthly: reg. 11(3)(a), (2A)(a): £1,048 and £4,189;
* a multiple of a week (2-weekly, 4-weekly): reg. 11(3)(c), (2A)(c): the annual figure ÷ 52 × the multiple,
  rounded up to the next whole pound (reg. 11(4)): £484 / £1,934 and £967 / £3,867;
* a year: reg. 11(3)(b), (2A)(b): £12,570 and £50,270.

Categories (the employee's side): A, H, M, V and the employer-relief letters pay 8 % / 2 % (s. 8(2)); B, a married
woman's reduced rate, 1.85 % (reg. 131) / 2 %; C, over pensionable age, nothing (s. 6(3)); J and Z (deferment) 2 % on
everything above the primary threshold.

Rounding. The Act and regulations give none. HMRC's employer guide CWG2 (2025-26, "Exact percentage method"): "round
the resulting National Insurance contributions figures to the nearest penny, rounding down exact amounts of £0.005".
HMRC's own 2025-26 NIC test data (v1.1) instead cut each band's amount to three decimal places and then round half
down: 0.32 × 8 % = £0.0256 is £0.02 in the test data and £0.03 by CWG2. Both rules are here; `NITestData.lean` checks
the test data row by row.
-/

namespace UkTax

inductive PayFreq where
  | weekly | twoWeekly | fourWeekly | monthly | annual
  deriving Repr, DecidableEq

/-- Prescribed equivalents of the primary threshold and upper earnings limit (pence). -/
def periodLimits (p : Params) : PayFreq → Int × Int
  | .weekly => (24200, 96700)                                         -- reg. 10(c), (b)
  | .twoWeekly => (100 * ceilDiv (p.niPrimaryThreshold * 2) 52, 100 * ceilDiv (p.niUpperEarningsLimit * 2) 52)
  | .fourWeekly => (100 * ceilDiv (p.niPrimaryThreshold * 4) 52, 100 * ceilDiv (p.niUpperEarningsLimit * 4) 52)
  | .monthly => (gbp p.niPrimaryThresholdMonthly, gbp p.niUpperEarningsLimitMonthly)
  | .annual => (gbp p.niPrimaryThreshold, gbp p.niUpperEarningsLimit)

/-- Employee's rates by category letter (basis points): main band, above the upper earnings limit. -/
def categoryRates (cat : Char) : Int × Int :=
  if cat = 'C' then (0, 0)
  else if cat = 'B' then (185, 200)
  else if cat = 'J' || cat = 'Z' then (200, 200)
  else (800, 200)

/-- HMRC's test-data rounding: cut to three decimal places (tenths of a penny), then the nearest penny, an exact
half penny down. Ticks are 1/10 000 penny. -/
def roundTestData (t : Int) : Int := let m := t / 1000; m / 10 + (if m % 10 ≥ 6 then 1 else 0)

/-- CWG2's rule: the nearest penny, "rounding down exact amounts of £0.005". -/
def roundCWG2 (t : Int) : Int := t / 10000 + (if t % 10000 > 5000 then 1 else 0)

/-- The employee's (primary) Class 1 for one pay period, in pence, each band rounded on its own. -/
def class1Period (p : Params) (rnd : Int → Int) (f : PayFreq) (cat : Char) (pay : Int) : Int :=
  let (pt, uel) := periodLimits p f
  let (r1, r2) := categoryRates cat
  rnd (r1 * overlap 0 pay pt uel) + rnd (r2 * above 0 pay uel)

theorem period_limits_2025 :
    periodLimits p2025 .twoWeekly = (48400, 193400) ∧ periodLimits p2025 .fourWeekly = (96700, 386700) := by decide

end UkTax
