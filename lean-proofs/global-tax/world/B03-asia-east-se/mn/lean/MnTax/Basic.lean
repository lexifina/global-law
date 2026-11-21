import TaxKernel.World

/-!
# Mongolia: personal income tax on employment income, social and health insurance, 2025

Access tier A (statute and amounts as dated law). Sources (saved in `mn/law/`, sha256 in PROGRESS.md):
* Law on Personal Income Tax (Хувь хүний орлогын албан татварын тухай хууль, revised 2019-03-22, in force
  2020-01-01; Global law `mongolia/national/acts/law/2019/14410`, official https://legalinfo.mn/mn/detail?lawId=14410).
  Global law holds only the 2026-10-28 consolidated text, whose art. 21.1 and 23.1 were replaced/repealed by the law of
  2026-06-26 **from 2027-01-01**; the wording in force in 2025 is read from the archived official page
  (web.archive.org snapshot 2025-06-25 of legalinfo.mn/mn/detail/14410, `wb_14410_20250625081427.html`):
  - art. 21.1 (as reworded by the law of 2022-11-11): "0-120 000 000 хүртэлх төгрөгийн албан татвар ногдуулах орлого
    олсон тохиолдолд 10 хувиар, 120 000 001-180 000 000 хүртэлх ... 12 000 000 төгрөг дээр 120 000 000 төгрөгөөс дээш
    давсан орлогод 15 хувиар, 180 000 000 төгрөгөөс дээш ... 21 000 000 төгрөг дээр ... 20 хувиар".
  - art. 14.1: taxable employment income = income of art. 7.1 less "эрүүл мэндийн болон нийгмийн даатгалд төлсөн
    шимтгэл" (health and social insurance contributions paid).
  - art. 23.1: annual tax credit on art. 7.1.1-7.1.5, 7.1.7 income by annual taxable income: 0-6m 240,000;
    6-12m 216,000; 12-18m 192,000; 18-24m 168,000; 24-30m 144,000; 30-36m 120,000; 36m and over: none.
    art. 23.14: a credit is not granted beyond the tax; the 23.1 credit is not refunded.
  - art. 16.1.3/16.1.4 + 21.2.4: dividends and interest at 10 % of the gross amount; 16.1.1 rent net of documented
    costs at 10 %; art. 8 + 15.1 + 21.2.4 business income at 10 % of income less costs.
  - art. 22.1.1: pensions and benefits paid under the law are exempt.
* Social Insurance General Law (Нийгмийн даатгалын ерөнхий хууль, revised 2023-07-07; lawId 16760148379551), text in
  force 2025 from the archived official page (snapshot 2025-08-09): art. 18.1 employee rates pension 8.5 %, benefits
  0.8 %, unemployment 0.2 % ("Шимтгэлийн дүн ... 9.5"); art. 19.4 monthly ceiling "сарын хөдөлмөрийн хөлсний доод
  хэмжээг 10 дахин" (10 x the monthly minimum wage) for compulsory insured persons.
* Health Insurance Law (2015, lawId 10922) art. 8.1.1/8.2.1 and Government resolution No. 02 of 2025-01-02
  (lawId 17355469261271): employee 2 % of monthly wages ("ажилтан 2 хувь"); the law sets no ceiling.
* Minimum wage 792,000 MNT a month from 2025-04-01 (Tripartite National Committee resolution 03 of 2024-10-07), as
  published by the General Authority for Social Insurance (ndaatgal.mn, 2025-03-28 and 2025-04-21; official secondary).
  The January-March 2025 minimum wage was not reached: the model applies the 792,000-based ceiling to all 12 months
  and flags households whose monthly wage exceeds 3,960,000 (see `unsupported`).
Unit: individual (each adult files alone; investment income split equally between spouses, contract rule).
-/

namespace MnTax
open TaxKernel

/-- PIT Law art. 21.1 (2025 wording): 10 % to 120m, 15 % to 180m, 20 % above, on the year's taxable employment income. -/
def sched : Schedule := Schedule.ofList [(0, 1000), (120000000, 1500), (180000000, 2000)]

/- The statute's printed fixed sums: 12,000,000 at 120m and 21,000,000 at 180m. -/
#guard sched.ticks 120000000 = 12000000 * BP ∧ sched.ticks 180000000 = 21000000 * BP

/-- art. 23.1 credit table (annual taxable income; the printed rows overlap at each 6m boundary: "0-6 000 000
хүртэл", "6 000 000-12 000 000 хүртэл"; read here as upper bounds inclusive). -/
def credit (ti : Int) : Int :=
  if ti ≤ 6000000 then 240000 else if ti ≤ 12000000 then 216000 else if ti ≤ 18000000 then 192000
  else if ti ≤ 24000000 then 168000 else if ti ≤ 30000000 then 144000 else if ti ≤ 36000000 then 120000 else 0

def minWage : Int := 792000
/-- Social Insurance General Law art. 18.1 (employee 9.5 %) with the art. 19.4 monthly ceiling (10 x minimum wage). -/
def siMonthly (m : Int) : Int := divR .down (950 * min (pos m) (10 * minWage)) BP
/-- Health insurance: employee 2 % of monthly wages, no ceiling (Gov. res. 02/2025). -/
def hiMonthly (m : Int) : Int := divR .down (200 * pos m) BP

def employeeSocial (wages : Int) : Int := perPeriod 12 siMonthly wages + perPeriod 12 hiMonthly wages

def invRate : Int := 1000

/-- One adult: (income tax on employment income after the credit, tax before the credit, taxable income, contributions). -/
def person (a : Adult) : Int × Int × Int × Int :=
  let ss := employeeSocial a.wages
  let ti := pos (a.wages - ss)
  let t0 := sched.tax Rule.unitDown ti
  let t := pos (t0 - (if a.wages > 0 then credit ti else 0))
  (t, t0, ti, ss)

def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let ps := c.adults.map person
  let wageTax := sumInts (ps.map (·.1))
  let invBase (i : Nat) : Int := share c.interest i + share c.dividends i + pos (share c.rentalIncome i)
  let invTax := sumInts ((List.range c.adults.length).map fun i => divR .down (invRate * invBase i) BP)
  let seTax := sumInts (c.adults.map fun a => divR .down (invRate * pos a.selfEmployment) BP)
  let ss := sumInts (ps.map (·.2.2.2))
  let highQ1 := c.adults.any fun a => a.wages > 12 * 3960000
  Out.make c "MN" "MNT" wageTax (surtaxes := [("investmentIncomeTax", invTax), ("businessIncomeTax", seTax)])
    (employeeSocial := ss)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.2.2.1))),
      Out.d "taxBeforeCredits" (sumInts (ps.map (·.2.1))),
      Out.dStr "note" "pensions paid under the law are exempt (art. 22.1.1); self-employment taxed at 10 % of the given net income (art. 15.1, 21.2.4); its voluntary social insurance is not modelled"])
    (unsupported := (if c.capitalGains ≠ 0 then ["capital gains: art. 17 (2 % of the sale price of immovable property, 10 % of gains on shares) needs the asset type and price"] else []) ++
      (if highQ1 then ["Jan-Mar 2025 social-insurance ceiling: 10 x the minimum wage then in force (not reached); modelled with 792,000"] else []))

def country : Country := { code := "MN", name := "Mongolia", currency := "MNT", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Credit notches: at 6m, 12m, ... 30m the credit falls by 24,000 for one more tugrik; at 36m it falls by 120,000. -/
def netTaxAt (t : Int) : Int := pos (sched.tax Rule.unitDown t - credit t)
#guard netTaxAt 36000001 - netTaxAt 36000000 = 120000
#guard (List.range 5).all fun k =>
  let t : Int := 6000000 * (k + 1)
  (pos (sched.tax Rule.unitDown (t + 1) - credit (t + 1))) - (pos (sched.tax Rule.unitDown t - credit t)) = 24000

end MnTax
