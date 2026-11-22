import TaxKernel.World

/-!
# Belarus: income tax of individuals (Tax Code, Special Part, ch. 16), tax year 2025

Statute read: Tax Code of the Republic of Belarus (Special Part), 29.12.2009 No. 71-З, the official consolidated text
on pravo.by (National Legal Internet Portal) as archived by the Internet Archive on 2025-06-14 (it lists Law 47-З of
13.12.2024 among the amendments and not Law 127-З of 30.12.2025; the live page now shows the 2026 text). Global law
holds no Belarusian text (empty corpus). Files in `by/law/`.
* art. 214(1): "Ставка ... устанавливается в размере тринадцать (13) процентов"; 214(8): "двадцати пяти (25) процентов
  в отношении совокупности начисленных доходов ... в виде дивидендов, в рамках трудовых отношений, а также по
  гражданско-правовым договорам ... в размере, превысившем за налоговый период 220 000 белорусских рублей", computed
  by the tax authority (art. 219); 214(3): individual entrepreneurs 20 %.
* art. 209(1)(1.1): "192 белорусских рублей в месяц при получении дохода ... в сумме, не превышающей 1164 белорусских
  рублей в месяц"; (1.2) "56 белорусских рублей в месяц на ребенка до восемнадцати лет", 107 a child for parents of two
  or more children, granted "обоим родителям".
* art. 208(3) pensions and 208(36) bank-deposit interest (with conditions) are exempt.
Not reached: the employee's 1 % pension contribution (Law 138-XIII "Об обязательных страховых взносах ..."): pravo.by
and etalonline.by serve the title but not the text, and no archived copy holds it; employeeSocial = 0 is flagged.
-/

namespace ByTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

def rate : Int := 1300           -- art. 214(1)
def highRate : Int := 2500       -- art. 214(8)
def highFrom : Int := 220000
def ipRate : Int := 2000         -- art. 214(3)
/-- The rate schedule of art. 214(1),(8) on the aggregate of wages and dividends. -/
def sched : Schedule := Schedule.ofList [(0, rate), (highFrom, highRate)]
def stdMonth : Int := 192        -- art. 209(1)(1.1)
def stdLimit : Int := 1164
def childMonth : Int := 56       -- art. 209(1)(1.2)
def childMonth2 : Int := 107     -- two or more children

/-- Standard and child deductions for a year of evenly paid wages `w` (monthly test of 209(1)(1.1)). -/
def deductions (w : Int) (kids : Nat) : Int :=
  let m := divR .halfUp w 12
  let std := if w > 0 && m ≤ stdLimit then stdMonth else 0
  let ch := if kids ≥ 2 then childMonth2 * kids else childMonth * kids
  12 * (std + (if w > 0 then ch else 0))

def out (c : Canon) : Out :=
  let kids := c.childrenUnder 18
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let rows := (c.adults.zip (List.range n)).map fun (a, i) =>
    let w := pos a.wages
    let ded := min w (deductions w kids)
    let dv := share (pos c.dividends) i
    -- art. 214(8): the excess of wages + dividends over 220 000 is taxed at 25 % (deductions taken from the 13 % part)
    let agg := w + dv
    let excess := pos (agg - highFrom)
    let tax := pct rate (pos (agg - excess - ded)) + pct highRate excess + pct ipRate (pos a.selfEmployment)
    (tax, ded)
  let earnTax := sumInts (rows.map (·.1))
  let cgTax := pct rate (pos c.capitalGains)
  Out.make c "BY" "BYN" (earnTax + cgTax) (employeeSocial := 0)
    (detail := [Out.d "deductions" (sumInts (rows.map (·.2))), Out.d "earningsAndDividendTax" earnTax,
      Out.d "capitalGainsTax" cgTax,
      Out.dStr "note" "13 % (TC SP art. 214(1)); 25 % on wages + dividends above 220 000 (214(8)); 192 a month if the month's income <= 1 164, 56/107 a child (209)"])
    (unsupported := ["employee pension contribution to the FSZN (Law 138-XIII, 1 %): text not reached; employeeSocial 0",
       "wages assumed paid evenly over 12 months at the main employer",
       "rent of dwellings is taxed in fixed sums set by regional councils (art. 214(2)): not modelled (rent ignored)",
       "dividends at 13 %; the 6 % and 0 % rates for retained profits (214(5)-(6)) not modelled",
       "interest assumed exempt bank-deposit interest (art. 208(36))",
       "pensions assumed exempt (art. 208(3))",
       "capital gains taxed at 13 %; exemptions for one dwelling every five years etc. not modelled"])

def country : Country := { code := "BY", name := "Belarus (income tax)", currency := "BYN", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- 1 100 a month: 192 a month off, 13 % of 12 x 908 = 1 416.48 -> 1 416. 1 200 a month: no deduction, 1 872. -/
#guard (out { id := "b", adults := [{ wages := 13200 }] }).incomeTax = 1416
#guard (out { id := "b", adults := [{ wages := 14400 }] }).incomeTax = 1872

end ByTax
