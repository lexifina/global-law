import TaxKernel.World

/-!
# Kazakhstan: individual income tax (Tax Code K1700000120, in force until 2025-12-31) with the mandatory pension
contribution (OPV) and the employee's medical-insurance contribution (VOSMS), tax year 2025

adilet.zan.kz serves a script page and its API needs credentials (not used); the texts were read from the Internet
Archive's copies of the official adilet pages (files in `kz/law/`, sha256 in PROGRESS):
* Tax Code, adilet K1700000120 as archived 2025-06-11: art. 320(1) "Доходы налогоплательщика облагаются налогом по
  ставке 10 процентов"; art. 342(1) deductions in this order: OPV, VOSMS contributions, standard deductions, the
  large-family deduction; art. 342(3) cap 564 MRP for the large-family and other deductions; note to art. 342: the MRP
  is that of the budget law in force on 1 January; art. 346(1)(1) "14-кратный размер месячного расчетного показателя
  ... за каждый календарный месяц", at most 168 MRP a year; art. 347(1)(1) large family (4+ minors on 1 January):
  "23-кратном размере ... за каждый месяц" for one parent, at most 282 MRP; art. 341(1)(2) bank-deposit interest,
  (1)(8) dividends from a resident within 30 000 MRP a year, (1)(27) age pensions excluded from income.
* Law Z2400000141 on the republican budget 2025-2027 (archived 2025-04-19), art. 9: "минимальный размер заработной
  платы – 85 000 тенге"; "месячный расчетный показатель – 3 932 тенге".
* Social Code K2300000224 (archived 2025-04-30), art. 249(1)(1): OPV "в размере 10 процентов от ежемесячного дохода",
  monthly income taken "не должен превышать 50-кратный минимальный размер заработной платы".
* Law Z1500000405 on mandatory social medical insurance (archived 2025-07-04), art. 28(1): employee contributions "с
  1 января 2021 года – 2 процентов"; art. 28(3) monthly income for contributions at most "10-кратный минимальный размер
  заработной платы".
Unit: individual.
-/

namespace KzTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

def mrp : Int := 3932         -- budget law Z2400000141 art. 9(4)
def mzp : Int := 85000        -- art. 9(1)
def rate : Int := 1000        -- Tax Code art. 320(1)
def sched : Schedule := Schedule.flat rate
def opvRate : Int := 1000     -- Social Code art. 249(1)(1)
def opvCapYear : Int := 12 * 50 * mzp
def vosmsRate : Int := 200    -- Law on OSMS art. 28(1)
def vosmsCapYear : Int := 12 * 10 * mzp
/-- art. 346(1)(1): 14 MRP a month, at most 168 MRP a year. -/
def stdYear : Int := min (12 * 14 * mrp) (168 * mrp)
#guard stdYear = 660576
/-- art. 347(1)(1): 23 MRP a month to one parent, at most 282 MRP; art. 342(3) overall cap 564 MRP. -/
def largeFamilyYear : Int := min (12 * 23 * mrp) (282 * mrp)
/-- art. 341(1)(8): dividends from a resident within 30 000 MRP a year are excluded. -/
def divExempt : Int := 30000 * mrp

def adultRow (a : Adult) (large : Bool) : Int × Int × Int :=
  let w := pos a.wages
  let opv := pct opvRate (min w opvCapYear)
  let vosms := pct vosmsRate (min w vosmsCapYear)
  let lf := if large then largeFamilyYear else 0
  let base := pos (w + pos a.selfEmployment - opv - vosms - (if w > 0 then stdYear else 0) - lf)
  (sched.tax Rule.unitHalfUp base, opv + vosms, base)

def out (c : Canon) : Out :=
  let large := c.childrenUnder 18 ≥ 4
  let rows := (c.adults.zip (List.range c.adults.length)).map fun (a, i) => adultRow a (large && i = 0)
  let earnTax := sumInts (rows.map (·.1))
  let soc := sumInts (rows.map (·.2.1))
  let divTax := pct rate (pos (c.dividends - divExempt))
  let rentTax := pct rate (pos c.rentalIncome)
  let cgTax := pct rate (pos c.capitalGains)
  Out.make c "KZ" "KZT" (earnTax + divTax + rentTax + cgTax) (employeeSocial := soc)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map (·.2.2))), Out.d "earningsTax" earnTax,
      Out.d "opvAndVosms" soc, Out.d "dividendTax" divTax, Out.d "rentTax" rentTax, Out.d "capitalGainsTax" cgTax,
      Out.dStr "note" "10 % (TC art. 320); base less OPV 10 % and VOSMS 2 % and 14 MRP a month (art. 342, 346); MRP 3 932, MZP 85 000 (budget law 2025 art. 9)"])
    (unsupported := (if large then ["large-family deduction (art. 347) given to the first adult; the parents may split it 12+12 MRP"] else []) ++
      ["OPV for people of pension age and the standard deduction at a second employer not modelled (one employer, under pension age)",
       "self-employment taxed at 10 % on the given profit; special regimes (patent, simplified declaration) and IP contributions not modelled",
       "interest assumed bank-deposit interest: excluded (art. 341(1)(2))",
       "pensions assumed age pensions: excluded (art. 341(1)(27))",
       "texts read from Internet Archive copies of adilet.zan.kz (the site serves scripts only)"])

def country : Country := { code := "KZ", name := "Kazakhstan (IIT + OPV + VOSMS)", currency := "KZT", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- 300 000 a month: OPV 360 000, VOSMS 72 000, base 3 600 000 - 432 000 - 660 576 = 2 507 424, tax 250 742. -/
#guard (out { id := "k", adults := [{ wages := 3600000 }] }).incomeTax = 250742

end KzTax
