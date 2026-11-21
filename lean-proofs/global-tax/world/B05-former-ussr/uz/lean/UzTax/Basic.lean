import TaxKernel.World

/-!
# Uzbekistan: personal income tax (Tax Code of 30.12.2019, Section XI), tax year 2025

Statute read: the official Russian text on lex.uz (Ministry of Justice), version in force on 01.01.2025
(`https://lex.uz/ru/docs/4674893?ONDATE=01.01.2025`, one of the dated versions the page itself lists; file
`uz/law/lex_tc_ru_on20250101.*`). The dated versions listed for 2025 (17.04, 22.04, 08.05, 17.05, 17.06, 26.06, 06.08,
22.08, 27.09, 20.10, 17.12, 25.12, 30.12) are to be checked for arts. 378 and 381 (see PROGRESS).
* art. 381 (residents): "Доходы физического лица — резидента Республики Узбекистан подлежат налогообложению по
  налоговой ставке 12 процентов"; "Доходы, в виде дивидендов и процентов облагаются налогом по налоговой ставке 5
  процентов".
* art. 378 item 13: "проценты и выигрыши по вкладам в банках" are not taxed.
* "государственные пенсии, пособия, установленные законодательством" are not taxed (see `uz/law` excerpt).
* "Исчисленная сумма налога уменьшается на сумму обязательных ежемесячных взносов на индивидуальные накопительные
  пенсионные счета физических лиц": the employee's funded-pension contribution is paid out of the 12 %, so the
  employee's total burden is the 12 % and `employeeSocial` is 0 (the contribution's own rate is not needed).
No personal allowance. Social tax is the employer's.
-/

namespace UzTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

def rate : Int := 1200        -- art. 381 part 1
def sched : Schedule := Schedule.flat rate
def divIntRate : Int := 500   -- art. 381 part 2

def out (c : Canon) : Out :=
  let rows := c.adults.map fun a => let b := pos a.wages + pos a.selfEmployment; (sched.tax Rule.unitHalfUp b, b)
  let earnTax := sumInts (rows.map (·.1))
  let otherInterest := (c.str? "interestSource") == some "other"
  let intTax := if otherInterest then pct divIntRate (pos c.interest) else 0
  let divTax := pct divIntRate (pos c.dividends)
  let rentTax := pct rate (pos c.rentalIncome)
  let cgTax := pct rate (pos c.capitalGains)
  Out.make c "UZ" "UZS" (earnTax + intTax + divTax + rentTax + cgTax) (employeeSocial := 0)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map (·.2))), Out.d "earningsTax" earnTax,
      Out.d "dividendTax" divTax, Out.d "interestTax" intTax, Out.d "rentTax" rentTax, Out.d "capitalGainsTax" cgTax,
      Out.dStr "note" "12 % (TC art. 381); dividends and interest 5 %; bank-deposit interest exempt (art. 378(13)); funded-pension contribution credited against the tax"])
    (unsupported := ["self-employment taxed at 12 % on the given profit; turnover-tax and fixed-tax regimes of entrepreneurs not modelled",
       "interest assumed bank-deposit interest: exempt (art. 378(13)); interestSource=other gives 5 %",
       "capital gains taxed at 12 %; exemptions for property held long term not modelled",
       "pensions assumed state pensions: exempt",
       "dated versions after 01.01.2025 not yet compared for arts. 378/381"])

def country : Country := { code := "UZ", name := "Uzbekistan (PIT)", currency := "UZS", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

#guard (out { id := "u", adults := [{ wages := 60000000 }] }).incomeTax = 7200000

end UzTax
