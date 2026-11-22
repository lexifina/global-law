import TaxKernel.World

/-!
# Grenada: income tax of a resident individual and the employee's National Insurance contribution, 2025

Sources (Laws of Grenada, laws.gov.gd, answered only from a second machine; files in `gd/law/`):
* Income Tax Act Cap. 149, 2010 Continuous Revised Edition (PDF of 2016-01-13, amended to Act 2 of 2010):
  s. 13: "Any income accrued to a married woman ... shall be charged to tax in her own name"; s. 42A(1): "there shall
  be allowed as a deduction the amount of assessable income accruing to that individual from all sources not exceeding
  sixty thousand dollars"; s. 56 and the Fifth Schedule (rates); s. 128 (rates and Schedules varied by order).
* S.R.O. 1 of 2014 (Income Tax (Amendment) Order 2014, gazetted 7 January 2014) para. 3: s. 42A "sixty thousand
  dollars" -> "thirty six thousand dollars"; para. 5: Fifth Schedule "(a) Individual: The first $24,000.00 or less of
  chargeable income ... 15%; Any amount in excess of the first $24,000.00 of chargeable income 30%".
* S.R.O. 2 of 2017 (in force 1 January 2017): Fifth Schedule para. (a) "15%" -> "10%".
* S.R.O. 25 of 2018 (in force 1 January 2019): Fifth Schedule "30%" -> "28%" "wherever it appears".
* Income Tax (Amendment) Acts 15/2012, 41/2013, 22/2014, 12/2015, 27/2015, 43/2015, 8/2016, 1/2017 read: none changes
  s. 42A or the individual rates. No later income-tax Act or Order is listed for 2018-2025 on laws.gov.gd.
* National Insurance (Collection of Contributions) Regulations (Cap. 205) Schedule, as amended by S.R.O. 43 of 2023
  (in force 1 January 2024): Part II (the employee's rows: "Employees who have attained the age of 60 years | Nil")
  "January 1, 2025 | 6% of employees' earnings not exceeding the maximum insurable earnings under Part III"; Part III
  "January 1, 2024 | $1,200 per week or $5,200 per month". (Part I, 7 % from 2025, read as the employer's rows.)
-/

namespace GdTax
open TaxKernel

/-- Fifth Schedule para. (a) as amended by S.R.O. 1/2014, 2/2017, 25/2018: 10 % on the first 24,000, 28 % above. -/
def sched : Schedule := Schedule.ofList [(0, 1000), (24000, 2800)]

def allowance : Int := 36000

/-- Employee's NI contribution for one month: 6 % to 5,200 (Part II, Part III). -/
def niMonth (m : Int) : Int := divR .down (600 * min (pos m) 5200) 10000

structure Person where
  ni : Int
  chargeable : Int
  tax : Int

def person (a : Adult) : Person :=
  let w := pos a.wages
  let ni := if a.age < 60 then perPeriod 12 niMonth w else 0
  let assessable := w + pos a.selfEmployment + pos a.pension
  let chargeable := pos (assessable - allowance)
  { ni := ni, chargeable := chargeable, tax := sched.tax Rule.unitDown chargeable }

def out (c : Canon) : Out :=
  let ps := c.adults.map person
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest, dividends, rents and gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["approved pension income exempt (s. 25(1)(gg),(hh), Act 1/2017): model taxes it"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed NI not modelled"] else [])
  Out.make c "GD" "XCD" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (·.ni)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.chargeable))), Out.d "ni" (sumInts (ps.map (·.ni))),
      Out.dStr "note" "individual taxation (s. 13); s. 42A deduction 36,000 (SRO 1/2014); 10 % to 24,000, 28 % above (SROs 1/2014, 2/2017, 25/2018); NI employee 6 % to 5,200/month (SRO 43/2023)"])
    (unsupported := unsup ++ ["NI Part I/II read as employer/employee rows from their content (principal Regulations' headings not read)",
      "wages assumed paid evenly over 12 months (NI ceiling is monthly)"])

def country : Country := { code := "GD", name := "Grenada (Income Tax Act Cap. 149 as varied by order)", currency := "XCD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard sched.tax Rule.unitDown 24000 = 2400
#guard sched.tax Rule.unitDown 34000 = 5200
#guard niMonth 5200 = 312
#guard niMonth 9000 = 312

end GdTax
