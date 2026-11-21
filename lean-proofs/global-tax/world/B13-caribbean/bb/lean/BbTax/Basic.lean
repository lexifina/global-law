import TaxKernel.World

/-!
# Barbados: income tax of a resident individual and National Insurance (employee), income year 2025

Sources (files in `bb/law/`; Global law's Barbados corpus has no Income Tax Act):
* Income Tax Act Cap. 73, L.R.O. 2007 consolidation (Barbados Revenue Authority, bra.gov.bb "Income Tax Act" page;
  the Supreme Court's copy `IncomeTaxCAP073.pdf` is the same edition) and the amending Acts listed on that page (text
  layers): 2009-6, 2010-11/13/15, 2011-11/26, 2012-26, 2013-17/18, 2014-15, 2015-16/22/23, 2016-19, 2018-4/37/54,
  2020-10/16, 2024-15, 2025-30.
  - s. 38B(1)(a)(iv): "the amount of $25 000 in respect of income year 2007 and subsequent income years"; (b) "60 years
    of age or over and in receipt of a pension, the amount of $40 000"; (c) "an individual whose spouse during the year
    had no income ... $3 000"; (d) child deduction "repealed" "With effect from 1st July, 2019" (Act 2020-10 s. 5).
  - s. 42(1) as amended by Act 2020-10 s. 6: "(j) with effect from 1st July, 2019 and the income years thereafter 12.5
    percent of every complete dollar of taxable income up to $50 000; (k) ... (ii) 1st January, 2020 and the income
    years thereafter, 28.5 per cent of every complete dollar of taxable income above $50 000"; s. 42(2): "where the tax
    ... is less than $1, no tax is payable".
  - s. 30(1)(a) (employee's NIS deduction) "Repealed by 1992-28": employee contributions are not deductible.
  - s. 65D reverse tax credit: (1)(e) (Act 2020-10 s. 10) "for income year 2018 and subsequent income years earns less
    than $25 000 annually but not more than $2083 monthly"; amount (2)(c) as replaced by Act 2015-16: "for the income
    year 2013 to the income year 2016, the amount of $650" - no amount is enacted for 2017 onwards in the Acts read
    (FINDINGS: credit 0 in the model, flagged).
  - s. 65G (Act 2020-10 s. 11) compensatory income credit for an employed individual who "earns more than $25 000
    annually but not more than $35 000 annually": "a credit in the amount of up to $1 250 calculated at the prescribed
    rate of their taxable income" (the prescribed rate was not found: input `bbCicRateBp`, default 0, flagged).
* National Insurance and Social Security Act Cap. 47: contribution rates and ceilings are set by regulations not in the
  L.R.O. 2007 copy. Official secondary: National Insurance and Social Security Service, "Contribution Rates & Earnings
  Ceilings" (nis.gov.bb, read 2026-11-20 from the laptop; lean1 gets 403): private-sector employees "R": employee 6.75 %
  national insurance + 2.00 % non-contributory + 0.75 % unemployment + 0.50 % training levy + 1.00 % health service
  contribution = 11.00 %; ceiling 2025 "1219.00" weekly, "5280.00" monthly; Catastrophe Fund 0.1 % of insurable
  earnings, replaced "from April 1, 2025" by the Resilience and Regeneration Fund at 0.25 % "calculated on gross
  earnings".
-/

namespace BbTax
open TaxKernel

/-- s. 42(1)(j),(k): 12.5 % to 50,000, 28.5 % above (every complete dollar). -/
def sched : Schedule := Schedule.ofList [(0, 1250), (50000, 2850)]

def taxOf (taxable : Int) : Int :=
  let t := sched.tax Rule.unitDown taxable
  if t < 1 then 0 else t

/-- NIS employee contribution for one month of pay `m` (index 0 = January): 11 % to the 5,280 ceiling, plus the
    Catastrophe Fund (0.1 % insurable, Jan-Mar) or Resilience Fund (0.25 % gross, Apr-Dec). In cents. -/
def nisMonthCents (i : Nat) (m : Int) : Int :=
  let ins := min (pos m) 5280
  1100 * ins + (if i < 3 then 10 * ins else 25 * pos m)

structure Person where
  nis : Int
  taxable : Int
  tax : Int

def person (a : Adult) (spouseNoIncome : Bool) (cicRate : Int) : Person :=
  let w := pos a.wages
  let nisC := if a.age ≥ 16 then perPeriodIdx 12 (fun i m => nisMonthCents i m) w else 0
  let assessable := w + pos a.selfEmployment + pos a.pension
  let allowance := (if a.age ≥ 60 && a.pension > 0 then 40000 else 25000) + (if spouseNoIncome then 3000 else 0)
  let taxable := pos (assessable - allowance)
  let tax := taxOf taxable
  let cic := if w > 25000 && w ≤ 35000 then min 1250 (divR .down (cicRate * taxable) 10000) else 0
  { nis := divR .halfUp nisC 10000, taxable := taxable, tax := pos (tax - cic) }

def out (c : Canon) : Out :=
  let cic := (c.int? "bbCicRateBp").getD 0
  let inc (a : Adult) : Int := a.wages + a.selfEmployment + a.pension
  let ps : List Person :=
    match c.adults with
    | [a, b] => [person a (c.married && inc b == 0) cic, person b (c.married && inc a == 0) cic]
    | l => l.map (fun a => person a false cic)
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest and dividends (withholding ss. 48B, 48C), rents and gains not modelled"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employed NIS (17.00 %) not modelled"] else []) ++
    (if c.adults.any (fun a => a.wages > 0 && a.wages < 25000) then ["s. 65D reverse tax credit: no amount enacted for 2017 onwards in the Acts read (model: 0)"] else []) ++
    (if c.adults.any (fun a => a.wages > 25000 && a.wages ≤ 35000) && cic == 0 then ["s. 65G compensatory income credit: prescribed rate not found (input bbCicRateBp; model: 0)"] else []) ++
    (if c.adults.any (fun a => a.age ≥ 65) then ["NIS at pensionable age (class E: 0.50 %) not modelled: the pensionable age was not read"] else [])
  Out.make c "BB" "BBD" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (·.nis)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "nis" (sumInts (ps.map (·.nis))),
      Out.dStr "note" "individual taxation; s. 38B allowance 25,000 (40,000 pensioners 60+, +3,000 spouse without income); s. 42 12.5 %/28.5 % at 50,000; NIS class R 11 % to 5,280/month + Catastrophe/Resilience Fund (official secondary)"])
    (unsupported := unsup ++ ["NIS rates and ceiling: official secondary (nis.gov.bb), regulations not reached",
      "wages assumed paid evenly over 12 months (NIS is monthly)"])

def country : Country := { code := "BB", name := "Barbados (Income Tax Act Cap. 73)", currency := "BBD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard taxOf 50000 = 6250
#guard taxOf 60000 = 9100
#guard taxOf 7 = 0
#guard nisMonthCents 0 5280 = 5808000 + 52800
#guard nisMonthCents 5 10000 = 5808000 + 250000

end BbTax
