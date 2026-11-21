import TaxKernel.World

/-!
# Fiji: Income Tax on individuals, Income Tax Act 2015, tax year 2025 (calendar year)

Sources (all official; files in `fj/law/`):
* Global law, Laws of Fiji consolidation (laws.gov.fj, record to 2026-10-28; current text only): Income Tax Act 2015
  (No 32 of 2015) ss 6, 8, 13, 14, 15, 21, 22, 23, 125 (`gl_ita_core.txt`, `gl_ita_s8_s23_title.txt`); Income Tax
  (Rates of Tax and Levies) Regulations 2016 (LN 5 of 2016) reg 3 and Schedule (`gl_rates_regs.txt`); Income Tax
  (Exempt Income) Regulations 2016 Schedule Parts 4-6 (`gl_exempt_sch.txt`); Fiji National Provident Fund Act 2011
  ss 37, 39 (`gl_fnpf.txt`).
* laws.gov.fj "Laws as published" (API `/api/show_pdf_lawsaspublished/<id>`, gazette PDFs with a text layer), read to
  date the consolidated text for 2025: Income Tax (Budget Amendment) Act 2023 (No 5 of 2023: s 8 rewritten and the
  Social Responsibility Tax abolished from 1 January 2024), LN 55 of 2023 (Schedule reg 3(a) effective 1 January
  2024), Income Tax (Budget Amendment) Act 2024 (No 5 of 2024, from 1 August 2024: ss 28A and 125A deleted), LN 12 of
  2025 (Exempt Income, deemed from 1 August 2024), Act 9 of 2025 and LN 36 of 2025 (both from 1 August 2025: neither
  touches the individual rates; LN 36 changes only para (5)(d), insurance premiums); FNPF (Budget Amendment) Act 2024
  (No 11 of 2024) and FNPF (Amendment) Act 2025 (No 23 of 2025): neither changes s 37(4) or s 39.

Schedule para (1), as amended by LN 55 of 2023 reg 3(a) (in force 1 January 2024, unchanged in 2025):
"Resident Individuals ... 0-30,000 | Nil | 30,001-50,000 | 18% of excess over $30,000 | 50,001-270,000 | $3,600 + 20%
of excess over $50,000 | 270,001-300,000 | $47,600 + 33% ... | 300,001-350,000 | $57,500 + 34% ... | 350,001-400,000 |
$74,500 + 35% ... | 400,001-450,000 | $92,000 + 36% ... | 450,001-500,000 | $110,000 + 37% ... | 500,001-1,000,000 |
$128,500 + 38% ... | 1,000,001 + | $318,500 + 39% of excess over $1,000,000".
-/

namespace FjTax
open TaxKernel

/-- Schedule para (1), resident individuals (bands; the printed column is proved equal below). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (30000, 1800), (50000, 2000), (270000, 3300), (300000, 3400), (350000, 3500),
    (400000, 3600), (450000, 3700), (500000, 3800), (1000000, 3900)]
/-- Schedule para (1), non-resident individuals: "0-30,000 | 20% of excess over $0 | 30,001-50,000 | $6,000 + 20% ...". -/
def schedNonRes : Schedule :=
  Schedule.ofList [(0, 2000), (270000, 3300), (300000, 3400), (350000, 3500), (400000, 3600), (450000, 3700),
    (500000, 3800), (1000000, 3900)]
/-- Schedule para (5A)(a): resident withholding tax on interest 10 % (final for interest paid by a financial
    institution to a resident individual: s 125(1)(b), (2)). -/
def rwtInterest : Int := 1000
/-- Schedule para (7): Capital Gains Tax 10 %. -/
def cgtRate : Int := 1000
/-- Exempt Income Schedule Part 4 para (9)(c): "the interest derived from a licenced Bank, by an individual taxpayer
    gross income $30,000 or less in a year"; para (9)(a): a senior citizen (55 or above) whose only income is bank
    interest not exceeding $30,000. -/
def interestExemptLimit : Int := 30000
def seniorAge : Nat := 55
/-- FNPF Act 2011 s 37(4): "18% of the total wages payable"; s 39(1): the employer "may recover from the employee an
    amount equal to eight-eighteenths or 44.4% (whichever is the greater) of the amount paid as mandated
    contributions ... rounded up to the nearest cent": the employee's share is 8/18 x 18 % = 8 % of wages. Not
    deductible: ITA s 23 allows only the employer's contribution; s 22(1)(b) bars an employee's expenditure. -/
def fnpfTotal : Int := 1800
def fnpfEmployeeNum : Int := 8
def fnpfEmployeeDen : Int := 18

/-- Employee FNPF for one month in cents (s 37(4) total rounded up to the cent, then s 39(1) share rounded up). -/
def fnpfMonthCents (mCents : Int) : Int :=
  let total := divR .up (fnpfTotal * mCents) BP
  divR .up (total * fnpfEmployeeNum) fnpfEmployeeDen
/-- Employee FNPF for the year in dollars (wages paid evenly over 12 months). -/
def fnpfYear (w : Int) : Int :=
  if w ≤ 0 then 0 else divR .up (perPeriod 12 fnpfMonthCents (w * 100)) 100

structure Person where
  chargeable : Int
  tax : Int
  interestTax : Int
  interestExempt : Bool
  cgt : Int
  fnpf : Int

/-- One individual (s 8: individual assessment; the Act has no joint return). Chargeable income = gross income
    (s 14: employment, business and property income) less deductions (s 21; none for employees, s 22(1)(b)). Wage PAYE
    is a final tax for a single employment (s 125(1)(a)) and s 8(6) taxes other chargeable income at
    T(other + wages) - T(wages): together the tax on the sum, as computed here. Dividends are exempt (Exempt Income
    Schedule Part 5(1)); FNPF/approved-fund pensions are exempt (Part 6(3)). -/
def person (resident : Bool) (a : Adult) (interest gains rent : Int) : Person :=
  let earn := pos a.wages + a.selfEmployment
  let ci := pos (earn + rent)
  let s := if resident then sched else schedNonRes
  let t := s.tax Rule.unitDown ci
  let gross := ci + pos interest
  let senior := decide (a.age ≥ seniorAge) && earn == 0 && rent == 0 && decide (interest ≤ interestExemptLimit)
  let exempt := resident && (decide (gross ≤ interestExemptLimit) || senior)
  let it := if exempt then 0 else divR .down (rwtInterest * pos interest) BP
  { chargeable := ci, tax := t, interestTax := it, interestExempt := exempt,
    cgt := divR .down (cgtRate * pos gains) BP, fnpf := fnpfYear a.wages }

def persons (c : Canon) : List Person :=
  let resident := (c.bool? "resident").getD true
  match c.adults with
  | [a] => [person resident a c.interest c.capitalGains c.rentalIncome]
  | a :: b :: _ =>
    [person resident a (half1 c.interest) (half1 c.capitalGains) (half1 c.rentalIncome),
     person resident b (half2 c.interest) (half2 c.capitalGains) (half2 c.rentalIncome)]
  | [] => []

def out (c : Canon) : Out :=
  let ps := persons c
  let resident := (c.bool? "resident").getD true
  let unsup :=
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions: FNPF and approved-fund pensions are exempt (Exempt Income Schedule Part 6(3)); other pensions not modelled (input ignored)"] else []) ++
    (if (c.adults.map (·.selfEmployment)).any (· ≠ 0) then ["business income taxed in chargeable income; Presumptive Income Tax (s 9) and business deductions not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capital gains: CGT 10 % on the whole gain; exemptions of s 67 (first home, family home, etc.) not modelled"] else []) ++
    (if c.interest ≠ 0 then ["interest assumed paid by a licensed bank (final 10 % resident withholding tax, s 125(1)(b))"] else [])
  Out.make c "FJ" "FJD" (sumInts (ps.map (·.tax)) + sumInts (ps.map (·.interestTax)))
    (surtaxes := [("CapitalGainsTax", sumInts (ps.map (·.cgt)))])
    (employeeSocial := sumInts (ps.map (·.fnpf)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.chargeable))),
      Out.d "incomeTaxOnChargeableIncome" (sumInts (ps.map (·.tax))),
      Out.d "interestWithholdingTax" (sumInts (ps.map (·.interestTax))),
      Out.d "fnpfEmployee" (sumInts (ps.map (·.fnpf))),
      Out.dStr "note" (if resident then "individual assessment; resident scale (Rates Regs Schedule para (1)); FNPF 8 % employee share not deductible; dividends exempt"
        else "non-resident scale (20 % from the first dollar; Schedule para (1)); FNPF computed (non-citizens join only by election, FNPF Act s 36(2))")])
    (unsupported := unsup ++ ["wages paid evenly over 12 months (FNPF rounded per month)"])

def country : Country := { code := "FJ", name := "Fiji (Income Tax Act 2015)", currency := "FJD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide
theorem schedNonRes_progressive : schedNonRes.progressive = true := by decide

/- The Schedule's printed cumulative column ("$3,600 + 20% ...", "$47,600 + 33% ...", ...) equals the bands. -/
#guard sched.tax Rule.unitDown 30000 = 0
#guard sched.tax Rule.unitDown 50000 = 3600
#guard sched.tax Rule.unitDown 270000 = 47600
#guard sched.tax Rule.unitDown 300000 = 57500
#guard sched.tax Rule.unitDown 350000 = 74500
#guard sched.tax Rule.unitDown 400000 = 92000
#guard sched.tax Rule.unitDown 450000 = 110000
#guard sched.tax Rule.unitDown 500000 = 128500
#guard sched.tax Rule.unitDown 1000000 = 318500
/- Non-resident column: $6,000 at 30,000; $10,000 at 50,000; $54,000 at 270,000; ...; $324,900 at 1,000,000. -/
#guard schedNonRes.tax Rule.unitDown 30000 = 6000
#guard schedNonRes.tax Rule.unitDown 50000 = 10000
#guard schedNonRes.tax Rule.unitDown 270000 = 54000
#guard schedNonRes.tax Rule.unitDown 300000 = 63900
#guard schedNonRes.tax Rule.unitDown 500000 = 134900
#guard schedNonRes.tax Rule.unitDown 1000000 = 324900
/- From 270,000 up the two columns differ by exactly 6,400 (the resident zero band and 18 % band). -/
#guard schedNonRes.tax Rule.unitDown 777777 - sched.tax Rule.unitDown 777777 = 6400
/- FNPF s 39(1): "eight-eighteenths or 44.4% (whichever is the greater)": 8/18 = 44.44 % always wins. -/
#guard fnpfEmployeeNum * 1000 > 444 * fnpfEmployeeDen
#guard fnpfYear 12000 = 960
/- Exempt Income Part 4(9)(c): bank interest of 1,000 exempt at gross income 30,000, taxed 100 at 30,001. -/
#guard (person true { age := 40, wages := 29000, selfEmployment := 0, pension := 0 } 1000 0 0).interestTax = 0
#guard (person true { age := 40, wages := 29001, selfEmployment := 0, pension := 0 } 1000 0 0).interestTax = 100

end FjTax
