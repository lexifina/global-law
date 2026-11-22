import TaxKernel.World

/-!
# Samoa: salary and wage income tax and income tax, Income Tax Act 2012, tax year 2025 (calendar year)

Sources (official: Ministry of Justice and Courts Administration, Legislative Drafting Division, "official version
... as at 31 December 2024", the publisher Global law names for Samoa; files in `ws/law/`, fetched from the MJCA
storage listing `legislation/`):
* Income Tax Act 2012 (`Income_Tax_Act_2012.pdf`): s 2 "'tax year' means the calendar year"; s 9(2)-(3) income tax at
  the Schedule 1 rates on taxable income; s 9(6) "If, for a tax year, an individual has both taxable income, and
  salary and wage income, the tax payable on the taxable income is ... A-B" (A = tax on taxable income plus salary and
  wage income, B = tax on the salary and wage income); s 59(2) salary and wage income tax "on an employee who receives
  salary and wage income ... during the fortnight", (3) "applying the rate or rates ... to the gross amount of salary
  and wage income received by the employee during the fortnight", (5) "each fortnight commences on a Monday"; s 60
  "Salary and wage income tax is a final tax"; s 24 (deduction for an employer's contribution only). Schedule 1 "(1)
  The rates of income tax applicable to an individual ... 0 - 15,000 NIL | 15,001 - 25,000 20% | 25,001 + 27%";
  "(7) The rates of salary and wage income tax ... for fortnight($) 0 - 576 Nil | 577 - 962 20% | 963 + 27%" (clauses
  (1), (7) last amended by the Income Tax Amendment Act 2017, No. 11, per the revision notes); Schedule 2 Part A (1)(b)
  "a dividend paid by a resident company" is exempt.
* National Provident Fund Act 1972 (official version as at 31 December 2024): s 22(1) "An employer shall pay to the
  Fund for each employee a contribution of 20 sene per tala of the amount of wages", (2) "is entitled to retain or
  recover from each employee's wages 10 sene per tala of the contribution", (6) no recovery where "the rate of wages
  is less than the minimum rate" (not modelled: hourly rates are not in the contract).
* Accident Compensation Act 1989 (official version as at 31 December 2024) s 52(1)(b): "by way of contribution by the
  employee a levy of 1 sene out of every complete tala of wages".
Amendments in 2025, if any, are not in these versions (access A with that caveat).
-/

namespace WsTax
open TaxKernel

/-- Schedule 1 clause (1): annual rates for an individual's taxable income. -/
def sched : Schedule := Schedule.ofList [(0, 0), (15000, 2000), (25000, 2700)]
/-- Schedule 1 clause (7): salary and wage income tax per fortnight (dollars). -/
def schedFortnight : Schedule := Schedule.ofList [(0, 0), (576, 2000), (962, 2700)]
def fortnights : Nat := 26
/-- NPF Act s 22(2) (employee 10 sene per tala) and ACC Act s 52(1)(b) (1 sene per complete tala). -/
def npfRate : Int := 1000
def accRate : Int := 100

/-- Salary and wage income tax for one fortnight, in cents (Schedule 1 clause (7) bands in dollars). -/
def fortnightTaxCents (fCents : Int) : Int := divR .down ((schedFortnight.mapLo (· * 100)).ticks (pos fCents)) BP

/-- Final salary and wage income tax for the year: wages paid evenly over 26 fortnights. -/
def wageTax (w : Int) : Int :=
  if w ≤ 0 then 0 else divR .down (perPeriod fortnights fortnightTaxCents (w * 100)) 100

structure Person where
  wages : Int
  taxable : Int
  wageTax : Int
  otherTax : Int
  npf : Int
  acc : Int

/-- s 9(6): tax on other taxable income = T(other + wages) - T(wages) at the annual rates; the wages themselves bear
    the final fortnightly tax (s 60). -/
def person (a : Adult) (rent : Int) : Person :=
  let w := pos a.wages
  let other := pos (a.selfEmployment + rent)
  let ot := if other == 0 then 0 else sched.tax Rule.unitDown (other + w) - sched.tax Rule.unitDown w
  { wages := w, taxable := other, wageTax := wageTax w, otherTax := ot,
    npf := divR .down (npfRate * w) BP, acc := divR .down (accRate * w) BP }

def persons (c : Canon) : List Person :=
  match c.adults with
  | [a] => [person a c.rentalIncome]
  | a :: b :: _ => [person a (half1 c.rentalIncome), person b (half2 c.rentalIncome)]
  | [] => []

def out (c : Canon) : Out :=
  let ps := persons c
  let unsup :=
    (if c.interest ≠ 0 then ["interest: withholding on interest (s 104 final withholding) not modelled; interest ignored"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains tax (Schedule 1 clause (8): 10 % within 12 months, 27 % after) not modelled: holding period not in the contract"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income taxed at the annual rates by s 9(6); deductions not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions through the NPF are exempt (Schedule 2 Part A (1)(d)); pension input ignored"] else [])
  Out.make c "WS" "WST" (sumInts (ps.map (·.wageTax)) + sumInts (ps.map (·.otherTax)))
    (employeeSocial := sumInts (ps.map (·.npf)) + sumInts (ps.map (·.acc)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "salaryWageIncome" (sumInts (ps.map (·.wages))),
      Out.d "salaryWageIncomeTax" (sumInts (ps.map (·.wageTax))), Out.d "incomeTaxOther" (sumInts (ps.map (·.otherTax))),
      Out.d "npfEmployee" (sumInts (ps.map (·.npf))), Out.d "accLevyEmployee" (sumInts (ps.map (·.acc))),
      Out.dStr "note" "fortnightly final salary and wage income tax (s 59-60, Schedule 1 (7)); other income at the annual rates by s 9(6); NPF 10 % and ACC 1 % not deductible"])
    (unsupported := unsup ++ ["wages paid evenly over 26 fortnights (a calendar year has 26 or 27 fortnights commencing on a Monday)"])

def country : Country := { code := "WS", name := "Samoa (Income Tax Act 2012)", currency := "WST", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide
theorem schedFortnight_progressive : schedFortnight.progressive = true := by decide

/- Annual scale: 20 % of 10,000 = 2,000 at 25,000. -/
#guard sched.tax Rule.unitDown 25000 = 2000
/- The fortnightly bands are not the annual bands over 26 fortnights: 576 x 26 = 14,976 (not 15,000) and
   962 x 26 = 25,012 (not 25,000). -/
#guard 576 * 26 = 14976 ∧ 962 * 26 = 25012
/- A wage of $26,000 a year (1,000 a fortnight): 20 % of 386 + 27 % of 38 = 77.20 + 10.26 = 87.46 a fortnight,
   2,273.96 a year; the annual scale would give 2,000 + 27 % of 1,000 = 2,270. -/
#guard fortnightTaxCents 100000 = 8746
#guard wageTax 26000 = 2273
#guard sched.tax Rule.unitDown 26000 = 2270

end WsTax
