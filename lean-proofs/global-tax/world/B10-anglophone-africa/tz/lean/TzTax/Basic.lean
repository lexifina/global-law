import TaxKernel.World

/-!
# Tanzania (Mainland): income tax of a resident individual, Income Tax Act Cap. 332 R.E. 2023, year of income 2025

Sources (Tanzania Revenue Authority "Acts" page, tra.go.tz/resource-center/8; files in `tz/law/`):
* The Income Tax Act [CAP. 332 R.E. 2023] (`The_Income_Tax_Act.pdf`, 146 pages). s. 20(1): "the year of income for
  every person shall be the calendar year". First Schedule para. 1(1) (history notes end "7 of 2023 s. 31"): "1.
  Where the total income does not exceed 3,240,000 | NIL | 2. ... exceeds 3,240,000/= but does not exceed
  Tshs.6,240,000/= | 8% of the amount in excess of Tshs. 3,240,000/= | 3. ... exceeds 6,240,000/= but does not exceed
  9,120,000/= | Tshs.240,000/= plus 20% of the amount in excess of 6,240,000/= | 4. ... exceeds 9,120,000/= but does
  not exceed 12,000,000/= | Tshs. 816,000/= plus 25% ... | 5. Where the total income exceeds 12,000,000/= |
  Tshs.1,536,000/= plus 30% of the amount in excess of 12,000,000/=". Para. 1(7): the Zanzibar rate is set separately
  (the model is Mainland Tanzania). s. 61(1)-(2): an individual's income is reduced by "retirement contributions made
  during the year of income by (a) the individual" to an approved retirement fund, "the actual contribution or the
  statutory amount required whichever is lesser".
* Finance Act 2024 (No. 6 of 2024) s. 46 and Finance Act 2025 (No. 11 of 2025, in force "1st day of July, 2025") s. 60
  amend the First Schedule only in paras. 2 (presumptive tax for transport) and 4 (withholding rates): para. 1 is
  unchanged in 2025.
* National Social Security Fund Act [CAP. 50 R.E. 2023] (nssf.go.tz "Acts"; `nssf_cap50_re2023.pdf`) First Schedule
  "CONTRIBUTIONS FOR EMPLOYEES": one month: "Ten cents for every complete shilling of wages" deductible from wages,
  "Twenty cents for every complete shilling of wages" statutory contribution; "employee's share" means "that portion of
  a statutory contribution set out in the First Schedule to be the employee's share" (the column heading itself reads
  "Employer's share deductible from wages by Employer": FINDINGS). No ceiling.
-/

namespace TzTax
open TaxKernel

/-- First Schedule para. 1(1), annual. -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (3240000, 800), (6240000, 2000), (9120000, 2500), (12000000, 3000)]
/-- NSSF Act First Schedule: ten cents for every complete shilling of monthly wages. -/
def nssfMonth (m : Int) : Int := divR .down (10 * pos m) 100

structure Person where
  tax : Int
  total : Int
  nssf : Int

def person (a : Adult) : Person :=
  let w := pos a.wages
  let nssf := perPeriod 12 nssfMonth w
  let total := pos (w - nssf)      -- s. 61: retirement contributions to an approved fund (NSSF) reduce income
  { tax := sched.tax Rule.unitDown total, total := total, nssf := nssf }

def out (c : Canon) : Out :=
  let ps := c.adults.map person
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income (and presumptive tax, First Schedule para. 2) not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 then ["interest, dividends and rents: final withholding (First Schedule para. 4) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["gains (para. 1(2)-(3) 10 % rate on gains) not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "TZ" "TZS" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (·.nssf)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.total))), Out.d "nssf" (sumInts (ps.map (·.nssf))),
      Out.dStr "note" "Mainland Tanzania; individual taxation; First Schedule para. 1(1) on employment income less NSSF 10 % (s. 61)"])
    (unsupported := unsup ++ ["Zanzibar rates (para. 1(7)) not modelled", "PSSSF (public servants) not modelled: private-sector NSSF assumed",
      "wages paid evenly over 12 months (NSSF is monthly)"])

def country : Country := { code := "TZ", name := "Tanzania (Mainland, Income Tax Act Cap. 332)", currency := "TZS", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- The printed fixed amounts of First Schedule para. 1(1): 240,000 at 6,240,000; 816,000 at 9,120,000; 1,536,000 at
   12,000,000 (checked against the bands). -/
#guard sched.tax Rule.unitDown 6240000 = 240000
#guard sched.tax Rule.unitDown 9120000 = 816000
#guard sched.tax Rule.unitDown 12000000 = 1536000
/- NSSF: 10 % of complete shillings. -/
#guard nssfMonth 1000000 = 100000

end TzTax
