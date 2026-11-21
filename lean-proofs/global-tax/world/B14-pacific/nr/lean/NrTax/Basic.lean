import TaxKernel.World

/-!
# Nauru: employment tax, Employment and Services Tax Act 2014, 2025 (pay periods in calendar 2025)

Sources (official; files in `nr/law/`):
* Global law, Laws of the Republic of Nauru (RONLAW consolidation, record to 2026-10-08; `gl_esta2014.txt`):
  Employment and Services Tax Act 2014 s 2(2) ("applies to employment income ... paid on or after 1 October 2014"),
  s 5 (employment income), s 7 (resident individual: a citizen without a permanent home abroad, a resettled refugee or
  asylum seeker, or the spouse of a resident citizen), s 11(1) "a tax to be known as 'employment tax' is imposed for
  each pay period at the rate or rates specified in the Schedule", (3) computed on "the gross amount of employment
  income of the employee for the period", (4) discharged by correct withholding; s 14 "(a) the tax is a final tax ...
  (b) ... no deduction is allowed"; s 17. Schedule "[Sch subst SL 3 of 2021 reg 4, opn 24 Mar 2021; am SL 3 of 2023
  reg 4, opn 1 July 2022]": "(1) ... resident individual ... (a) for a monthly pay period: ... $0 - $9,240 0% Above
  $9,240 20% (b) for a fortnightly pay period: ... $0 - $4,257 0% Above $4,257 20% (c) for a weekly pay period: ...
  $0 - $2,129 0% Above $2,129 20%"; "(2) ... (a) ... Regional Processing Centre is 30%; (b) ... expatriate employees
  [of the Republic or a State-owned enterprise] ... 0 - $20,000 - rate is 0% ... above $20,000 - rate is 20%; (c) for
  any other non-resident is 20%". The only later notes on the Act are Act 21 of 2026 (opn 12 May 2026: preamble and
  s 7): the 2025 Schedule is the one printed.
* Naoero (Nauru) Superannuation Act 2018 (Global law, `gl_nsa2018.txt`): Schedule 1 "[... am Act 49 of 2025 s 6, opn
  1 Feb 2026; am Act 21 of 2026 s 5]": employer 10 %, employee 5 %; s 23 non-residents exempt; s 26 "The employer
  shall deduct from the member's basic salary or wages the members mandatory contribution at the contribution rate";
  (4) "rounded up to the nearest cent". Nauru Superannuation (Amendment) Act 2025 (No. 49 of 2025, ronlaw.gov.nr,
  `nsa_amend_2025.pdf`) s 2 "commences on 1 Febuary 2026" and s 6 "Schedule 1 is amended in item (a) by deleting '5%'
  and substituting with '10%'": in 2025 the employer rate was 5 % and the employee rate 5 % (item (b), unchanged).
-/

namespace NrTax
open TaxKernel

/-- Schedule (1): pay periods per year and the 0 % band per period (dollars). -/
def periods (p : String) : Nat := if p == "weekly" then 52 else if p == "fortnightly" then 26 else 12
def zeroBand (p : String) : Int := if p == "weekly" then 2129 else if p == "fortnightly" then 4257 else 9240
def rate : Int := 2000
/-- Schedule (2)(b): expatriate employees of the Republic or a State-owned enterprise: 0 % to $20,000 a year. -/
def expatBand : Int := 20000
def rpcRate : Int := 3000
/-- Naoero Superannuation Act 2018 Schedule 1 item (b) (employee 5 %). -/
def superRate : Int := 500

/-- Employment tax in cents for one pay period of `mCents` (resident): 20 % above the period's band. -/
def periodTaxCents (p : String) (mCents : Int) : Int := divR .down (rate * pos (mCents - zeroBand p * 100)) BP

/-- Annual employment tax (dollars) for wages paid evenly over the year's pay periods; the tax is final for each
    period (s 14), so there is no annual reconciliation. -/
def residentTax (p : String) (w : Int) : Int :=
  if w ≤ 0 then 0 else divR .down (perPeriod (periods p) (periodTaxCents p) (w * 100)) 100

def nonResidentTax (cat : String) (w : Int) : Int :=
  if cat == "rpc" then divR .down (rpcRate * pos w) BP
  else if cat == "government" then divR .down (rate * pos (w - expatBand)) BP
  else divR .down (rate * pos w) BP

def superYear (p : String) (w : Int) : Int :=
  if w ≤ 0 then 0 else divR .up (perPeriod (periods p) (fun m => divR .up (superRate * m) BP) (w * 100)) 100

structure Person where
  wages : Int
  tax : Int
  super : Int

def person (resident : Bool) (p cat : String) (a : Adult) : Person :=
  let w := pos a.wages
  { wages := w, tax := if resident then residentTax p w else nonResidentTax cat w,
    super := if resident then superYear p w else 0 }

def out (c : Canon) : Out :=
  let resident := (c.bool? "resident").getD true
  let p := (c.str? "payPeriod").getD "monthly"
  let cat := (c.str? "nrCategory").getD "other"
  let ps := c.adults.map (person resident p cat)
  let unsup :=
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["self-employment: services tax (s 12, same per-period scale for residents) and Business Tax Act 2016 not modelled"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then ["investment income: outside the Employment and Services Tax Act (employment income and services fees only); no other income tax act read"] else [])
  Out.make c "NR" "AUD" (sumInts (ps.map (·.tax)))
    (employeeSocial := sumInts (ps.map (·.super)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.wages))), Out.d "superannuationEmployee" (sumInts (ps.map (·.super))),
      Out.dStr "payPeriod" p,
      Out.dStr "note" "employment tax per pay period, final (ESTA s 11, 14): 20 % above $9,240 a month ($4,257 a fortnight, $2,129 a week); superannuation 5 % (2025)"])
    (unsupported := unsup ++ ["wages paid evenly in equal pay periods (input payPeriod: monthly | fortnightly | weekly; default monthly)"])

def country : Country := { code := "NR", name := "Nauru (Employment and Services Tax Act 2014)", currency := "AUD", year := "2025", compute := out }

/- A monthly salary of $10,000: 20 % of 760 = 152 a month, 1,824 a year. -/
#guard residentTax "monthly" 120000 = 1824
/- The three printed period bands are not the same annual amount: 9,240 x 12 = 110,880; 4,257 x 26 = 110,682;
   2,129 x 52 = 110,708. At $120,000 a year the fortnightly-paid employee pays $39.60 more than the monthly-paid. -/
#guard 9240 * 12 = 110880 ∧ 4257 * 26 = 110682 ∧ 2129 * 52 = 110708
#guard residentTax "fortnightly" 120000 - residentTax "monthly" 120000 = 39
/- No annual reconciliation: $120,000 paid in one month costs (120,000 - 9,240) x 20 % = 22,152 instead of 1,824. -/
#guard divR .down (periodTaxCents "monthly" 12000000) 100 = 22152
#guard superYear "monthly" 12000 = 600

end NrTax
