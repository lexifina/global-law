import TaxKernel.World

/-!
# South Africa: normal tax on individuals, 2026 year of assessment (1 March 2025 - 28 February 2026), and UIF

Access tier B. The Income Tax Act 58 of 1962 is not in Global law and SARS serves it only through a LexisNexis portal;
the rates for each year are fixed by Parliament (s. 5 (2)) in the annual Rates and Monetary Amounts Act, which was not
found for 2026 on gov.za's act list (the 2024-2025 acts there amend customs/excise and retirement rules). Every amount
below is therefore taken from SARS's own published tables, cited as official secondary (pages saved in `za/law/`,
2026-11-20); the facts are restated here, not quoted:
* SARS, Rates of Tax for Individuals (sars_ind.html): the 2026 year of assessment (March 2025 to February 2026) and
  the 2025 year both keep the 2024 table. Bands: 18 % up to R237 100; 26 % to R370 500 (R42 678 due at the band's
  start); ... 45 % from R1 817 001 (R644 489 due at the band's start). Rebates (s. 6) for 2026: primary R17 235,
  secondary (age 65 and over) R9 444, tertiary (age 75 and over) R3 145. Thresholds 2026: R95 750 / R148 217 /
  R165 689 (checked by `#guard`).
* SARS, Interest and Dividends (sars_intdiv.html): the s. 10 (1) (i) interest exemption for 2026 is R23 800 below
  age 65 and R34 500 from age 65; South African company dividends paid to an individual are not part of income for
  normal tax, and the 20 % dividends tax is withheld at source.
* SARS, UIF page (sars_uif.html; Unemployment Insurance Contributions Act 4 of 2002): the employee pays 1 % of
  remuneration, on earnings capped since 1 June 2021 at R17 712 a month (R212 544 a year).
Unit: individual (spouses taxed separately; investment income split equally between spouses, contract rule).
-/

namespace ZaTax
open TaxKernel

/-- s. 5 rate table for the 2026 year (= 2024 table, SARS). -/
def sched : Schedule :=
  Schedule.ofList [(0, 1800), (237100, 2600), (370500, 3100), (512800, 3600), (673000, 3900), (857900, 4100), (1817000, 4500)]

/- SARS's cumulative amount at each band start (R42 678 at R237 100, …) equals the band sum. -/
#guard [(237100, 42678), (370500, 77362), (512800, 121475), (673000, 179147), (857900, 251258), (1817000, 644489)].all
  fun (t, base) => sched.ticks t = base * BP

def primary : Int := 17235
def secondary : Int := 9444
def tertiary : Int := 3145
def interestExempt (age : Nat) : Int := if age ≥ 65 then 34500 else 23800
def dividendsTaxRate : Int := 2000
def uif : Contribution := Contribution.flatCapped "UIF" 100 212544

def rebate (age : Nat) : Int := primary + (if age ≥ 65 then secondary else 0) + (if age ≥ 75 then tertiary else 0)

/-- Tax of one person on taxable income `ti` (rand, rounded down to the rand). -/
def personTax (age : Nat) (ti : Int) : Int := pos (sched.tax Rule.unitDown (pos ti) - rebate age)

/- SARS printed thresholds: the income at which tax before rebates equals the rebates (tax 0 at or below). -/
#guard personTax 40 95750 = 0 ∧ personTax 40 95756 > 0
#guard personTax 65 148217 = 0 ∧ personTax 65 148223 > 0
#guard personTax 75 165689 = 0 ∧ personTax 75 165695 > 0

def personTI (a : Adult) (interest rental : Int) : Int :=
  a.wages + a.selfEmployment + a.pension + pos (interest - interestExempt a.age) + rental

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let tis := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    (a.age, personTI a (share c.interest i) (share c.rentalIncome i))
  let it := sumInts (tis.map fun (age, ti) => personTax age ti)
  let dt := divR .down (dividendsTaxRate * c.dividends) BP
  let ss := sumInts (c.adults.map fun a => uif.amount a.wages)
  Out.make c "ZA" "ZAR" it (surtaxes := [("dividendsTax", dt)]) (employeeSocial := ss)
    (detail := [Out.d "taxableIncome" (sumInts (tis.map (·.2))),
      Out.d "taxBeforeCredits" (sumInts (tis.map fun (_, ti) => sched.tax Rule.unitDown (pos ti)))])
    (unsupported := (if c.capitalGains ≠ 0 then ["capital gains (Eighth Schedule inclusion and annual exclusion) not modelled"] else []) ++
      (if c.pensionContributions ≠ 0 then ["retirement-fund contribution deduction (s. 11F) not modelled"] else []) ++
      ["medical scheme fees tax credit (s. 6A/6B): no contract input",
       "amounts from SARS's published tables (official secondary): the 2026 Rates and Monetary Amounts Act text was not reached"])

def country : Country := { code := "ZA", name := "South Africa (2026 year of assessment)", currency := "ZAR", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end ZaTax
