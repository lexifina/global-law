import TaxKernel.World

/-!
# Pakistan: income tax of a resident individual, tax year 2026 (1 July 2025 - 30 June 2026)

Access tier A. Statute: Income Tax Ordinance, 2001 (XLIX of 2001) as amended by the Finance Act, 2025 (in force
1 July 2025). Read and saved in `pk/law/` with sha256:
* FBR, "Income Tax Ordinance, 2001 Amended upto 31.07.2025" (download1.fbr.gov.pk, linked from
  fbr.gov.pk/Categ/Income-Tax-Ordinance/326; `ito_fbr_20250731.pdf`, sha256 3eb83def...): the text that governs tax
  year 2026.
* Pakistan Code consolidated text of 2026-10-28 (the official link Global law gives; `ito_pakistancode.pdf`, sha256
  1b611d31...): after the Finance Act, 2026; its footnotes print the tax-year-2026 wording that the Finance Act, 2026
  replaced ("Table substituted by the Finance Act, 2026. The substituted Table read as follows: ... 1% ... 11% ... 23%
  ... 30% ... 35%") and agree with the FBR text.
* Global law `pakistan/national/acts/acts/1976/employees-old-age-benefits-act` ss. 2(p), 9B (Pakistan Code 2026-10-28).

s. 74 (1): "the tax year shall be the period of twelve months ending on the 30th day of June"; tax year 2026 = the
year beginning 1 July 2025 (CONTRACTWORLD: the year beginning in 2025).
-/

namespace PkTax
open TaxKernel

/-- s. 219: "fractions of a rupee less than fifty paisa shall be disregarded and fractions ... equal to or exceeding
fifty paisa shall be treated as one rupee". -/
def r219 : Rule := { mode := .halfUp }

/-- First Schedule Part I Division I clause (2) as substituted by the Finance Act, 2025 (salaried individual, "where
the income of an individual chargeable under the head "salary" exceeds seventy-five per cent of his taxable income"):
0 to 600,000; "1% of the amount exceeding Rs. 600,000"; "Rs. 6,000 + 11% ... exceeding Rs. 1,200,000";
"Rs. 116,000 + 23% ... exceeding Rs. 2,200,000"; "Rs. 346,000 + 30% ... exceeding Rs. 3,200,000";
"Rs. 616,000 + 35% ... exceeding Rs. 4,100,000". -/
def salaried : Schedule :=
  Schedule.ofList [(0, 0), (600000, 100), (1200000, 1100), (2200000, 2300), (3200000, 3000), (4100000, 3500)]

/-- Division I clause (1) Table as substituted by the Finance Act, 2024 (unchanged by the Finance Act, 2025; "every
individual and association of persons except a salaried individual"): 0 to 600,000; "15% of the amount exceeding
Rs. 600,000"; "Rs. 90,000 + 20% ... exceeding Rs. 1,200,000"; "Rs. 170,000 + 30% ... exceeding Rs. 1,600,000";
"Rs. 650,000 + 40% ... exceeding Rs. 3,200,000"; "Rs. 1,610,000 + 45% ... exceeding Rs. 5,600,000". -/
def general : Schedule :=
  Schedule.ofList [(0, 0), (600000, 1500), (1200000, 2000), (1600000, 3000), (3200000, 4000), (5600000, 4500)]

/-- Division I clause (2), proviso inserted by the Finance Act, 2025 (with the omission of Second Schedule Part I
clause (8), the old pension exemption): "pension received by an individual from a former employer in a tax year":
"0% of the amount" up to "rupees ten million", "5% of the amount exceeding rupees ten million". -/
def pensionSched : Schedule := Schedule.ofList [(0, 0), (10000000, 500)]

/- The printed fixed amounts of both tables are the band sums (cumulative column checked). -/
def cum (s : Schedule) (x : Int) : Int := s.ticks x / BP
#guard cum salaried 1200000 = 6000 ∧ cum salaried 2200000 = 116000 ∧ cum salaried 3200000 = 346000 ∧
  cum salaried 4100000 = 616000
#guard cum general 1200000 = 90000 ∧ cum general 1600000 = 170000 ∧ cum general 3200000 = 650000 ∧
  cum general 5600000 = 1610000

/-- s. 4AB (Finance Act 2024; proviso Finance Act 2025): surcharge "at the rate of ten percent of the income tax
imposed under Division I of Part I of the First Schedule where the taxable income exceeds rupees ten million";
"in case of an individual deriving income chargeable under the head "Salary", ... nine percent". No marginal relief. -/
def surchargeThreshold : Int := 10000000
def surchargeRate (derivesSalary : Bool) : Int := if derivesSalary then 900 else 1000

/-- First Schedule Part I Division IIB (s. 4C super tax), column "For tax year 2026 and onwards" of the Table
substituted by the Finance Act, 2025: a rate "of the income" (the whole income, not the excess) chosen by its size:
<= 150m 0 %; 150-200m 1 %; 200-250m 1.5 %; 250-300m 2.5 %; 300-350m 3.5 %; 350-400m 5.5 %; 400-500m 7.5 %;
> 500m 10 %. -/
def superTaxRate (inc : Int) : Int :=
  if inc ≤ 150000000 then 0 else if inc ≤ 200000000 then 100 else if inc ≤ 250000000 then 150
  else if inc ≤ 300000000 then 250 else if inc ≤ 350000000 then 350 else if inc ≤ 400000000 then 550
  else if inc ≤ 500000000 then 750 else 1000
def superTax (inc : Int) : Int := divR .halfUp (superTaxRate inc * pos inc) BP

/-- Division III clause (b) as substituted by the Finance Act, 2025: "15% in the case of Real Estate Investment Trust
and cases other than those mentioned in clauses (a), (ba), (c) and (d)" (s. 5: on "the gross amount of the dividend"). -/
def dividendRate : Int := 1500
/-- Division IIIA as substituted by the Finance Act, 2025, clause (a): "20% of the yield or profit paid by a banking
company or financial institution on an account or deposit". s. 7B (3)(b): s. 7B "shall not apply to a profit on debt
that ... exceeds five million Rupees" (it is then taxable income under the normal tables). -/
def profitOnDebtRate : Int := 2000
def s7BLimit : Int := 5000000

/-- s. 15A (1)(a): "an allowance equal to one-fifth of the rent chargeable to tax". -/
def repairsAllowance (rent : Int) : Int := rent / 5

/-- s. 61 (2) and s. 63 (2): credit = (A/B) x C, A the tax before credits, B the taxable income; C capped at 30 %
(donations, individual) or 20 % (approved pension fund) of taxable income. -/
def avgRateCredit (a b c : Int) : Int := if b ≤ 0 then 0 else divR .halfUp (a * pos c) b
def donationCap : Int := 3000
def pensionFundCap : Int := 2000

/-- EOBI Act 1976 s. 9B: "contribution shall be payable every month by an insured person at the rate of one per cent
of the wages"; s. 2 (p): "wages" means "the rates of wages as declared under the Minimum Wages for Unskilled Worker
Ordinance, 1969", i.e. the notified minimum wage (amount not reached: optional input `pkMinWageMonthly`); s. 9 (1)
proviso: none due at "the age of sixty years". -/
def eobiRate : Int := 100

structure PersonIn where
  age : Nat
  salary : Int     -- head "Salary" other than pension
  pension : Int    -- pension from a former employer (Division I (2) proviso)
  business : Int
  rent : Int
  pod : Int        -- profit on debt (bank deposit)
  div : Int
  zakat : Int
  donation : Int
  vps : Int

structure PersonOut where
  ti : Int          -- taxable income (s. 9), incl. pension
  salariedTable : Bool
  divI : Int        -- Division I tax before credits
  credits : Int
  surcharge : Int
  superTax : Int
  s7B : Int
  s5 : Int
  eobi : Int

def person (minWage : Option Int) (p : PersonIn) : PersonOut :=
  let podInTI := if p.pod > s7BLimit then p.pod else 0
  let prop := pos (p.rent - repairsAllowance p.rent)
  let tiRest := pos (p.salary + p.business + prop + podInTI - p.zakat)
  let ti := tiRest + p.pension
  -- Division I (2): salary income (incl. pension) "exceeds seventy-five per cent of his taxable income"
  let salariedT := 4 * (p.salary + p.pension) > 3 * ti && ti > 0
  let main := (if salariedT then salaried else general).tax r219 tiRest
  let pen := pensionSched.tax r219 p.pension
  let divI := main + pen
  let derivesSalary := p.salary + p.pension > 0
  let sur := if ti > surchargeThreshold then divR .halfUp (surchargeRate derivesSalary * divI) BP else 0
  let cDon := avgRateCredit divI ti (min p.donation (divR .down (donationCap * ti) BP))
  let cVps := if p.salary + p.business > 0 then avgRateCredit divI ti (min p.vps (divR .down (pensionFundCap * ti) BP)) else 0
  let cred := min divI (cDon + cVps)
  let s7B := if p.pod > s7BLimit then 0 else divR .halfUp (profitOnDebtRate * pos p.pod) BP
  let s5 := divR .halfUp (dividendRate * pos p.div) BP
  let stInc := ti + pos p.pod - podInTI + pos p.div
  let eobi := match minWage with
    | some w => if p.salary > 0 && p.age < 60 then 12 * divR .halfUp (eobiRate * w) BP else 0
    | none => 0
  { ti, salariedTable := salariedT, divI, credits := cred, surcharge := sur, superTax := superTax stInc, s7B, s5, eobi }

def compute (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let minWage := c.int? "pkMinWageMonthly"
  let zak := (c.int? "zakat").getD 0
  let ps := (c.adults.zip (List.range n)).map fun (a, i) =>
    ({ age := a.age, salary := a.wages, pension := a.pension, business := a.selfEmployment,
       rent := share c.rentalIncome i, pod := share c.interest i, div := share c.dividends i,
       zakat := if i = 0 then zak else 0, donation := if i = 0 then c.charitable else 0,
       vps := if i = 0 then c.pensionContributions else 0 } : PersonIn)
  let rs := ps.map (person minWage)
  let s (f : PersonOut → Int) := sumInts (rs.map f)
  Out.make c "PK" "PKR" (s fun r => r.divI - r.credits)
    (surtaxes := [("surcharge4AB", s (·.surcharge)), ("superTax4C", s (·.superTax)),
                  ("profitOnDebt7B", s (·.s7B)), ("dividend5", s (·.s5))])
    (employeeSocial := s (·.eobi))
    (detail := [Out.d "taxableIncome" (s (·.ti)), Out.d "taxBeforeCredits" (s (·.divI)),
      Out.d "credits61_63" (s (·.credits)),
      Out.dStr "table" (String.intercalate "," (rs.map fun r => if r.salariedTable then "salaried(Div I (2))" else "general(Div I (1))"))])
    (unsupported := (if c.capitalGains ≠ 0 then ["capital gains (s. 37/37A rates by holding period and acquisition date) not modelled; capitalGains ignored"] else []) ++
      (if minWage.isNone && c.adults.any (·.wages > 0) then ["EOBI employee contribution (EOBI Act s. 9B: 1 % of the notified minimum wage) needs pkMinWageMonthly; employeeSocial 0"] else []) ++
      (if c.interest ≠ 0 then ["profit on debt read as bank-deposit profit (Division IIIA (a), 20 %)"] else []) ++
      ["provincial social security and workers' funds are employer-side; Workers' Welfare/Participation Funds not modelled"])

def country : Country :=
  { code := "PK", name := "Pakistan (tax year 2026: July 2025 - June 2026)", currency := "PKR", year := "2026 (2025-26)",
    compute := compute }

theorem sched_progressive : salaried.progressive = true := by decide
theorem general_progressive : general.progressive = true := by decide

/-- The tax-year-2026 salaried table as a kernel `sched` (for the generic theorems). -/
abbrev sched : Schedule := salaried

/- s. 4AB surcharge notch: at 10,000,000 of salaried taxable income the surcharge is nothing; one rupee more costs 9 %
of the whole Division I tax (241,290 rupees). -/
def salariedTotal (ti : Int) : Int :=
  let t := salaried.tax r219 ti
  t + (if ti > surchargeThreshold then divR .halfUp (surchargeRate true * t) BP else 0)
#guard salariedTotal 10000001 - salariedTotal 10000000 = 241290

/- s. 7B (3)(b) cliff: a single salaried earner of 2,400,000 whose bank profit rises from 5,000,000 to 5,000,001:
the profit leaves the 20 % separate tax and joins taxable income; salary is then below 75 % of taxable income, so the
general table (45 % top rate) applies to everything. -/
def podCase (pod : Int) : Int :=
  let r := person none { age := 40, salary := 2400000, pension := 0, business := 0, rent := 0, pod := pod, div := 0,
                         zakat := 0, donation := 0, vps := 0 }
  r.divI - r.credits + r.surcharge + r.superTax + r.s7B + r.s5
#guard podCase 5000000 = 1162000 ∧ podCase 5000001 = 2420000

/- Division I clause (2) 75 % test: a salaried individual (3,000,000 salary) with business income; when the business
income passes one third of the salary the whole income moves to the general table. -/
def mixCase (bus : Int) : Int :=
  let r := person none { age := 40, salary := 3000000, pension := 0, business := bus, rent := 0, pod := 0, div := 0,
                         zakat := 0, donation := 0, vps := 0 }
  r.divI - r.credits + r.surcharge
#guard mixCase 999999 = 586000 ∧ mixCase 1000000 = 970000

/- s. 4C super tax is a rate of the whole income: 1 % of 150,000,001 at the first rupee over 150 million. -/
#guard superTax 150000001 - superTax 150000000 = 1500000

end PkTax
