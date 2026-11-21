import TaxKernel.World

/-!
# Kyrgyzstan: income tax (Tax Code of 18 January 2022 No. 3) and the employee's state social insurance contribution,
tax year 2025 (access B)

Statutes read (files in `kg/law/`): the official editions of the Tax Code from cbd.minjust.gov.kg (`GetEdition`) in
force during 2025: edition of 12.02.2025 (Law No. 37) and of 29.10.2025 (Laws 37, 137, 185, 243); the articles used
have the same words in both (and in Global law's current text `kyrgyzstan/national/acts/nalogovyy-kodeks-...`):
* art. 197(1): "Ставка подоходного налога устанавливается в размере 10 процентов".
* art. 187(1): base = annual gross income less exempt income and deductions; art. 187(2): if the monthly salary does
  not exceed the district average monthly wage (published by the National Statistical Committee), the base is that
  average wage (not for state-funded employers and the other art. 187(4) cases).
* art. 194: standard deductions: personal "6,5 расчетного показателя за каждый месяц", dependants "одного расчетного
  показателя на каждого иждивенца за каждый месяц", and the state social insurance contributions.
* art. 191: dividends of a resident citizen from a resident company (191 part 6 item 4), bank-deposit and account
  interest (part 7 item 1) and statutory pensions (part 3) are not taxed.
* Law No. 136 of 23.07.2024 art. 7 (Global law `kyrgyzstan/national/acts/zakon/2024/07-23-n136`, in force 1 August
  2024 by its art. 10(1)(2)), restating art. 2-2 of the Law on social insurance tariffs: employees "в размере 10
  процентов" (Pension Fund 8 % + State accumulative pension fund 2 %); working pensioners 8 %.
Not reached (access B): the value of the расчетный показатель (set outside the Code) and the 2025 district average
wages (National Statistical Committee; www.stat.kg did not answer from lean1 or the laptop). Without them the personal
and dependant deductions and the art. 187(2) minimum base cannot be applied: the model reports the tax without them
and lists both in `unsupported` (tax overstated by up to 10 % of 6.5 RP a month; understated for wages below the
district average). An input field `"rp"` (som) and `"avgMonthlyWage"` (som) switch them on for testing.
-/

namespace KgTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

def rate : Int := 1000             -- art. 197(1)
def sched : Schedule := Schedule.flat rate
def socRate : Int := 1000          -- tariff law art. 2-2(2)(a) as restated by Law 136
def socPensionerRate : Int := 800  -- art. 2-2(2)(b)
/-- Personal deduction in tenths of an RP a month (art. 194(1): 6.5). -/
def personalTenths : Int := 65

def out (c : Canon) : Out :=
  let rp? := c.int? "rp"
  let avg? := c.int? "avgMonthlyWage"
  let rows := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    let w := pos a.wages
    -- art. 187(2): monthly salary below the district average is taxed on the average
    let wBase := match avg? with
      | some avgW => if w > 0 then max w (12 * avgW) else 0
      | none => w
    let soc := pct (if a.age ≥ 63 then socPensionerRate else socRate) w
    let deps := if i = 0 then (c.childrenUnder 18 : Int) else 0
    let ded := match rp? with
      | some rp => divR .halfUp (12 * personalTenths * rp) 10 + 12 * deps * rp
      | none => 0
    let base := pos (wBase + pos a.selfEmployment - soc - ded)
    (sched.tax Rule.unitHalfUp base, soc, base)
  let earnTax := sumInts (rows.map (·.1))
  let soc := sumInts (rows.map (·.2.1))
  let rentTax := pct rate (pos c.rentalIncome)
  let cgTax := pct rate (pos c.capitalGains)
  Out.make c "KG" "KGS" (earnTax + rentTax + cgTax) (employeeSocial := soc)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map (·.2.2))), Out.d "earningsTax" earnTax,
      Out.d "socialContribution" soc, Out.d "rentTax" rentTax, Out.d "capitalGainsTax" cgTax,
      Out.dStr "note" "10 % (TC art. 197(1)); social contributions deducted (art. 194(3)); dividends, deposit interest, pensions exempt (art. 191)"])
    (unsupported := (if rp?.isNone then ["personal deduction 6.5 RP a month and dependant deduction 1 RP (art. 194(1)-(2)) not applied: the value of the расчетный показатель was not reached"] else []) ++
      (if avg?.isNone then ["art. 187(2) minimum base (district average monthly wage, National Statistical Committee) not applied: 2025 values not reached"] else []) ++
      ["dependants: children under 18 given to the first adult",
       "working pensioners assumed from age 63 (pension age not read) for the 8 % rate",
       "self-employment and rent at 10 % on the given amounts; patent and other special regimes not modelled",
       "capital gains at 10 %; listed securities exempt (art. 191) not modelled"])

def country : Country := { code := "KG", name := "Kyrgyzstan (income tax + social contribution)", currency := "KGS", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard (out { id := "k", adults := [{ wages := 360000 }] }).incomeTax = 32400

end KgTax
