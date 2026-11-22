import TaxKernel.World

/-!
# Armenia: income tax (Tax Code 2016, HO-165-N, Section 7), the funded-pension social payment and the stamp duty, 2025

Statutes read (Global law `armenia/national/acts`, official text arlis.am; files in `am/law/`), as in force on 2025-07-01:
* Tax Code art. 150 (official https://www.arlis.am/hy/acts/153403; no change to its words in 2025, compare_dates
  2025-01-01..2025-12-31): (1) table "2023 թվականի հունվարի 1-ից | 20 տոկոս"; (5.1) bank-deposit interest "10 տոկոս";
  (7) rent "տասը տոկոս", and a further 10 % on rent above 60 million dram a year; (8) dividends "հինգ տոկոս";
  (9) income from alienation of property 10 %.
* art. 143(1)(1): the base is gross income less the art. 147 reductions; art. 147(1)(2): "բոլոր տեսակի կենսաթոշակները"
  (all pensions) are reductions (exempt). The social payment is not a reduction.
* Law on Funded Pensions HO-244-N (in force text 2025-01-01, last changed by HO-287-N): art. 5(1)(1) payers are
  employees "1974 թվականի հունվարի 1-ին և դրանից հետո ծնված"; art. 6(2)(1) salary: "5 տոկոսի չափով, եթե աշխատավարձի
  ամսական չափը չի գերազանցում 500 000 դրամը" and "10 տոկոսի և 25 000 դրամի տարբերության չափով" above; (2)(2)
  entrepreneurial income 5 % up to 6 000 000 a year, else 10 % less 300 000; art. 6(6) no payment on the part of monthly
  gross income above 15 times the minimum monthly wage (annual: 180 times).
* Law on the Minimum Monthly Wage HO-66-N art. 1 (last changed by HO-501-N, 2022-12-23): "նվազագույն ամսական
  աշխատավարձը սահմանել 75000 դրամ".
* Law HO-245-N on compensation of damage to servicemen, art. 11 (payers: employees) and art. 12(1)(1) (as of 2023-04-03):
  monthly stamp duty 1 500 (base up to 100 000), 3 000 (to 200 000), 5 500 (to 500 000), 8 500 (to 1 000 000),
  15 000 (above); art. 12(1)(2) individual entrepreneurs 18 000 / 24 000 / 48 000 / 120 000 by annual base
  (2.4 m / 6 m / 12 m).
-/

namespace AmTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

/-- art. 150(1): 20 % from 2023. -/
def rate : Int := 2000
def sched : Schedule := Schedule.flat rate
def depositRate : Int := 1000   -- art. 150(5.1)
def divRate : Int := 500        -- art. 150(8)
def rentRate : Int := 1000      -- art. 150(7)
def rentExtraFrom : Int := 60000000
def propRate : Int := 1000      -- art. 150(9)

/-- HO-66-N art. 1. -/
def minWage : Int := 75000
/-- HO-244-N art. 6(6): monthly ceiling 15 x minimum wage; annual ceiling 180 x the 1 January amount. -/
def capMonth : Int := 15 * minWage
def capYear : Int := 180 * minWage

/-- art. 6(2)(1) as bands: 5 % to 500 000, then 10 % (so 10 % less 25 000), nothing above the ceiling. -/
def socWage : Schedule := Schedule.ofList [(0, 500), (500000, 1000), (capMonth, 0)]
/-- art. 6(2)(2): entrepreneurial income, annual. -/
def socSelf : Schedule := Schedule.ofList [(0, 500), (6000000, 1000), (capYear, 0)]

/- The statute's "10 % less 25 000" (and "less 300 000") are the band sums. -/
#guard socWage.ticks 500000 = 25000 * BP
#guard socWage.ticks 800000 = (80000 - 25000) * BP
#guard socWage.ticks capMonth = (112500 - 25000) * BP ∧ socWage.ticks (capMonth + 100000) = socWage.ticks capMonth
#guard socSelf.ticks 8000000 = (800000 - 300000) * BP

/-- art. 5(1)(1): born 1 January 1974 or later; at the end of 2025 that is age 51 or less. -/
def participant (age : Nat) : Bool := age ≤ 51

/-- HO-245-N art. 12(1)(1): monthly stamp duty by the monthly base. -/
def stampMonth (w : Int) : Int :=
  if w ≤ 0 then 0 else if w ≤ 100000 then 1500 else if w ≤ 200000 then 3000 else if w ≤ 500000 then 5500
  else if w ≤ 1000000 then 8500 else 15000
/-- art. 12(1)(2): entrepreneurs, by the annual base. -/
def stampSelf (y : Int) : Int :=
  if y ≤ 0 then 0 else if y ≤ 2400000 then 18000 else if y ≤ 6000000 then 24000 else if y ≤ 12000000 then 48000 else 120000

def taxOn (x : Int) : Int := sched.tax Rule.unitHalfUp (pos x)

def out (c : Canon) : Out :=
  let rows := c.adults.map fun a =>
    let m := divR .halfUp (pos a.wages) 12
    let socW := if participant a.age then 12 * socWage.tax Rule.unitHalfUp m else 0
    let socS := if participant a.age then socSelf.tax Rule.unitHalfUp (pos a.selfEmployment) else 0
    let stamp := 12 * stampMonth m + stampSelf (pos a.selfEmployment)
    (taxOn (pos a.wages + pos a.selfEmployment), socW + socS, stamp)
  let earnTax := sumInts (rows.map (·.1))
  let soc := sumInts (rows.map (·.2.1))
  let stamp := sumInts (rows.map (·.2.2))
  let rent := pos c.rentalIncome
  let rentTax := pct rentRate rent + pct rentRate (pos (rent - rentExtraFrom))
  let intTax := pct depositRate (pos c.interest)
  let divTax := pct divRate (pos c.dividends)
  let cgTax := pct propRate (pos c.capitalGains)
  Out.make c "AM" "AMD" (earnTax + rentTax + intTax + divTax + cgTax)
    (surtaxes := [("stampDuty", stamp)]) (employeeSocial := soc)
    (detail := [Out.d "taxableIncome" (sumInts (c.adults.map fun a => pos a.wages + pos a.selfEmployment)),
      Out.d "earningsTax" earnTax, Out.d "socialPayment" soc, Out.d "stampDuty" stamp,
      Out.d "interestTax" intTax, Out.d "dividendTax" divTax, Out.d "rentTax" rentTax, Out.d "propertyGainTax" cgTax,
      Out.dStr "note" "20 % (TC art. 150(1)); funded-pension social payment HO-244-N art. 6 for those born 1974+; stamp duty HO-245-N art. 12"])
    (unsupported := (if c.adults.any (fun a => a.age == 51 || a.age == 52) then ["social payment: ages 51-52 straddle the 1 January 1974 birth date (HO-244-N art. 5(1)); age 51 treated as born 1974"] else []) ++
      ["voluntary social payment of those born before 1974 (art. 5(1)(2)) not modelled",
       "wages assumed paid evenly over 12 months (social payment and stamp duty are monthly)",
       "turnover-tax and micro-enterprise regimes for entrepreneurs not modelled (general regime, 20 %)",
       "interest assumed bank-deposit interest (art. 150(5.1), 10 %)",
       "art. 6(7) combined cap across salary and entrepreneurial income not modelled"])

def country : Country := { code := "AM", name := "Armenia (income tax + social payment + stamp duty)", currency := "AMD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- 400 000 a month (4.8 m a year), born 1990: tax 960 000, social payment 12 x 20 000, stamp duty 12 x 5 500. -/
#guard (out { id := "a", adults := [{ age := 35, wages := 4800000 }] }).incomeTax = 960000
#guard (out { id := "a", adults := [{ age := 35, wages := 4800000 }] }).employeeSocial = 240000

end AmTax
