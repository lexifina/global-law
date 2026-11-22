import TaxKernel.World

/-!
# Lesotho: income tax on resident individuals, year of assessment 1 April 2025 - 31 March 2026

Access tier B. Structure from the Income Tax Act No. 9 of 1993 as updated to 1 April 2012 (official consolidation
served by the Revenue Services Lesotho, rsl.org.ls/sites/default/files/2026-09/Income Tax Act 1993 Updated up to 1
April 2012.pdf; sha256 in `ls/law/SHA256SUMS`); the 2025/26 amounts from the RSL's "Guide on Taxation of Employment
Income 25-26" (same site, official secondary: the regulations and Finance Acts that set them were not reached).
* s. 1 "year of assessment" means "the period of 12 months ending on 31 March".
* s. 4 (2): "The income tax payable is calculated by applying the relevant rates of tax to the chargeable income and
  subtracting any allowable tax credits."
* s. 9 (1): "The rates prescribed in the Second Schedule apply to the chargeable income of a resident individual."
  (2012 text: "First M40,368 22% / Over M40,368 35%", amended by Act 17 of 2008 and LN 61 of 2009.)
* s. 73 (1): "A resident individual ... is allowed a non refundable personal credit of M5,184" (2012 amount, "revised in
  terms of Income Tax (Amendment of Monetary Amounts) Regulations, 2010").
* RSL guide 25-26, s. 3.1: "progressive two-rate structure of 20% and 30% ... Any chargeable income from M 1.00 up to
  M 6, 170.00 per month is taxable at 20%; and Any excess of M 6, 170.00 per month is taxable at 30%"; s. 3.2:
  "Individuals are granted a non-refundable tax credit of M 970.00 per month"; s. 3.3: "Employees who earn a gross
  salary of M 4,850.00 and below per month, will not pay any tax" (checked below: 970 / 20 % = 4 850).
* s. 27 (1): "The first M500 of interest derived from one savings account by a resident individual who is not a minor
  is exempt from income tax."
Annual amounts = 12 x the guide's monthly amounts (band M74 040, credit M11 640). Unit: individual (s. 4 (1) "every
individual"). No employee social-security contribution statute was found (not modelled; not asserted absent).
-/

namespace LsTax
open TaxKernel

def band : Int := 12 * 6170          -- 74 040
def credit : Int := 12 * 970         -- 11 640
def sched : Schedule := Schedule.ofList [(0, 2000), (band, 3000)]
def interestExempt : Int := 500      -- s. 27 (1)

def personTax (ti : Int) : Int := pos (sched.tax Rule.unitDown (pos ti) - credit)

/- RSL guide s. 3.3: no tax at M4 850 a month (M58 200 a year), tax above. -/
#guard personTax (12 * 4850) = 0 ∧ personTax (12 * 4850 + 12) > 0

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let tis := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    pos (a.wages + a.selfEmployment + a.pension + share c.rentalIncome i + pos (share c.interest i - interestExempt)
      - share c.pensionContributions i)
  let it := sumInts (tis.map personTax)
  Out.make c "LS" "LSL" it (employeeSocial := 0)
    (detail := [Out.d "taxableIncome" (sumInts tis), Out.d "taxBeforeCredits" (sumInts (tis.map fun t => sched.tax Rule.unitDown t)),
      Out.dStr "note" "ITA 1993 s. 4, 9, 73; 2025/26 amounts from the RSL employment-income guide 25-26 (official secondary)"])
    (unsupported := (if c.dividends ≠ 0 then ["dividends: withholding / final tax rules not read"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: not modelled"] else []) ++
      (if c.pensionContributions ≠ 0 then ["approved pension contributions deducted in full: the statutory cap was not read"] else []) ++
      ["2025/26 band and credit from the RSL guide (official secondary): the regulation or Finance Act setting them was not reached"])

def country : Country := { code := "LS", name := "Lesotho (year of assessment 2025/26)", currency := "LSL", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end LsTax
