import TaxKernel.World

/-!
# Myanmar: income tax on salary, fiscal year 2025-26 (1 April 2025 - 31 March 2026)

Access tier B. Global law's Myanmar corpus holds the Constitution and three other acts, not the Income Tax Law (1974)
nor the yearly Union Tax Law; mlis.gov.mm did not answer. The amounts below are the Internal Revenue Department's own
page "တစ်ဦးချင်းပုဂ္ဂိုလ်" (individuals, https://www.ird.gov.mm/tax-knowledge/taxes/individual, saved as
`mm/law/ird_ind.html` 2026-11-20; official secondary), which cites the provisions:
* Union Tax Law 2025 s. 19 (က): salary income up to 4,800,000 kyat a year ("လစာဝင်ငွေ (၄၈) သိန်းထိ") is exempt.
* s. 19 (ဂ): above that, the total income less the Income Tax Law s. 6 reliefs is taxed by bands: 1-2,000,000 0 %;
  2,000,001-10,000,000 5 %; 10,000,001-30,000,000 10 %; 30,000,001-50,000,000 15 %; 50,000,001-70,000,000 20 %;
  70,000,001 and above 25 %.
* Income Tax Law s. 6 reliefs: basic relief 20 % of total income, at most 10,000,000 ("စုစုပေါင်းဝင်ငွေ၏ ၂၀ ရာခိုင်နှုန်း၊
  ကျပ်သိန်း ၁၀၀ ထက်မပိုစေရ"); a parent living with the taxpayer 1,000,000 each; one spouse 1,000,000; each child
  500,000; life insurance premiums; social security contributions (taxpayer only). Non-resident foreigners get none
  (Union Tax Law 2025 s. 24).
* Rent: commercial tax 5 % above 50,000,000 a year (s. 14 (င), exempt to 50,000,000, s. 15 (ခ)) and income tax 10 % on
  rent less the s. 6 reliefs; capital gains 10 % (s. 27 (ခ)), exempt if total sales in the year do not exceed
  10,000,000 (s. 28).
Not reached: the Social Security Law contribution rate and ceiling (employee contributions `unsupported`).
Unit: individual. Year: fiscal 2025-26 (the Union Tax Law 2025 year).
-/

namespace MmTax
open TaxKernel

def sched : Schedule := Schedule.ofList [(0, 0), (2000000, 500), (10000000, 1000), (30000000, 1500),
  (50000000, 2000), (70000000, 2500)]

def salaryExempt : Int := 4800000
def basicRelief (total : Int) : Int := min (divR .down (2000 * pos total) BP) 10000000
def spouseRelief : Int := 1000000
def childRelief : Int := 500000

/-- Salary tax of one resident (s. 19): nothing up to 4,800,000 of salary; above, bands on salary less reliefs. -/
def salaryTax (salary : Int) (spouse : Bool) (kids : Nat) : Int × Int :=
  if salary ≤ salaryExempt then (0, 0) else
  let ti := pos (salary - basicRelief salary - (if spouse then spouseRelief else 0) - childRelief * kids)
  (sched.tax Rule.unitDown ti, ti)

def out (c : Canon) : Out :=
  let idx := List.range c.adults.length
  let sal (a : Adult) : Int := pos a.wages
  let top : Nat := match c.adults with
    | [a0, a1] => if sal a1 > sal a0 then 1 else 0
    | _ => 0
  let rs := (c.adults.zip idx).map fun (a, i) =>
    let others : List (Adult × Nat) := (c.adults.zip idx).filter (fun p => p.2 ≠ i)
    let sp := c.isCouple ∧ i = top ∧ others.all (fun p => sal p.1 ≤ 0)
    salaryTax (sal a) sp (if i = top then c.childrenUnder 18 else 0)
  Out.make c "MM" "MMK" (sumInts (rs.map (·.1)))
    (detail := [Out.d "taxableIncome" (sumInts (rs.map (·.2))),
      Out.dStr "note" "child and spouse reliefs claimed by the higher earner; children under 18 counted (reading)"])
    (unsupported := (if c.adults.any (fun a => a.wages > 0) then ["employee social security contributions and their s. 6 relief: Social Security Law rates not reached"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rent: separate 10 % income tax after reliefs and 5 % commercial tax above 50,000,000 not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains 10 % (s. 27) with the 10,000,000 sales exemption (s. 28): needs sale proceeds"] else []) ++
      (if c.interest ≠ 0 ∨ c.dividends ≠ 0 then ["interest and dividends: treatment not on the IRD page"] else []) ++
      (if c.adults.any (fun a => a.selfEmployment ≠ 0) then ["self-employment (profession/business) income not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions not modelled"] else []))

def country : Country := { code := "MM", name := "Myanmar (FY 2025-26)", currency := "MMK", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- The s. 19 (က) exemption is all-or-nothing: one kyat of salary above 4,800,000 brings tax on everything above the
   reliefs and the zero band (a notch of 92,000 kyat for a single person). -/
#guard (salaryTax 4800000 false 0).1 = 0
#guard (salaryTax 4800001 false 0).1 = 92000

end MmTax
