import TaxKernel.World

/-!
# Turkmenistan: tax on the income of individuals (Tax Code, new edition, Section on income tax) 2025 (access B)

Statutes read (official site of the Mejlis, mejlis.gov.tm > Codes > Tax Code, Russian text, consolidated with the
amending laws up to 12 April 2025 (Ведомости 2025 № 1 ст. 4); file `tm/law/mejlis_code10_taxcode_20261120.*`; Global
law's Turkmenistan corpus does not hold the Tax Code):
* art. 192(1) (as worded by the Law of 3 June 2023): "Налоговая ставка устанавливается в размере 10 процентов".
* art. 188(1)(а): a monthly deduction for any individual "в размере однократной величины установленной законодательством
  Туркменистана базовой величины для исчисления налогов и сборов"; (г) one base value per dependant a month.
* art. 187(1)(б) pensions and (т) interest on bank deposits are not included in the base.
* art. 172(2): dividends "в размере 15 процентов"; art. 193(1) applies it to the art. 185(6) base of individuals.
* art. 193(4): "Сумма налога менее 50 тенге - не учитывается, а 50 тенге и более – округляются до целого маната".
* Social protection: the Code of Turkmenistan on social protection (mejlis.gov.tm, code 17): the pension system
  "основывается на обязательных пенсионных взносах ... уплачиваемых страхователями" (employers), and the funded system
  rests on "добровольном пенсионном страховании": no compulsory employee contribution (employeeSocial = 0).
Not reached (access B): the value of the "базовая величина для исчисления налогов и сборов" (set by a decree outside
the Code; law.minjust.gov.tm needs a login). The deduction is therefore not applied unless an input field `"baseValue"`
(manat a month) is given, and the omission is listed in `unsupported`.
-/

namespace TmTax
open TaxKernel

/-- art. 193(4): whole manat, 50 tenge and more up. -/
def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

def rate : Int := 1000       -- art. 192(1)
def sched : Schedule := Schedule.flat rate
def divRate : Int := 1500    -- art. 172(2) via art. 193(1)

def out (c : Canon) : Out :=
  let bv? := c.int? "baseValue"
  let rows := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    let deps : Int := if i = 0 then (c.childrenUnder 18 : Int) else 0
    let ded := match bv? with | some bv => 12 * bv * (1 + deps) | none => 0
    let base := pos (pos a.wages + pos a.selfEmployment - ded)
    (sched.tax Rule.unitHalfUp base, base)
  let earnTax := sumInts (rows.map (·.1))
  let divTax := pct divRate (pos c.dividends)
  let rentTax := pct rate (pos c.rentalIncome)
  let cgTax := pct rate (pos c.capitalGains)
  Out.make c "TM" "TMT" (earnTax + divTax + rentTax + cgTax) (employeeSocial := 0)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map (·.2))), Out.d "earningsTax" earnTax,
      Out.d "dividendTax" divTax, Out.d "rentTax" rentTax, Out.d "capitalGainsTax" cgTax,
      Out.dStr "note" "10 % (TC art. 192(1)); dividends 15 % (art. 172(2)); deposit interest and pensions excluded (art. 187); no compulsory employee pension contribution (Social Protection Code)"])
    (unsupported := (if bv?.isNone then ["monthly deduction of one base value per person and per dependant (TC art. 188(1)(a),(g)) not applied: the 2025 base value was not reached"] else []) ++
      ["dependants: children under 18 given to the first adult (art. 188(1)(g) allows either spouse)",
       "self-employment taxed at 10 % on the given profit; the simplified regime for entrepreneurs (art. 200) not modelled",
       "capital gains and rent taxed at 10 %",
       "text read from mejlis.gov.tm's consolidated version (amendments to 12 April 2025); dates of entry into force of that law not read"])

def country : Country := { code := "TM", name := "Turkmenistan (income tax)", currency := "TMT", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard (out { id := "m", adults := [{ wages := 36000 }] }).incomeTax = 3600

end TmTax
