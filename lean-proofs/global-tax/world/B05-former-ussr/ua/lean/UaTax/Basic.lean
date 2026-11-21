import TaxKernel.World

/-!
# Ukraine: personal income tax (Tax Code 2755-VI, Section IV), military levy (Section XX subsection 10 item 16-1) and
the single social contribution (Law 2464-VI), tax year 2025

zakon.rada.gov.ua did not answer from lean1 or the laptop (time-outs, not a refusal); the texts were read from the
Internet Archive's copies of the official pages (files in `ua/law/`):
* Tax Code, edition of 15.06.2025 (basis 4474-IX), archived 2025-06-20: art. 167.1 "Ставка податку становить 18
  відсотків бази оподаткування" for wages; 167.5.1 passive income 18 %; 167.5.2 "5 відсотків - для доходів у вигляді
  дивідендів" from resident profit-tax payers; art. 169.1.1 tax social benefit "50 відсоткам розміру прожиткового
  мінімуму для працездатної особи ... встановленому законом на 1 січня звітного податкового року"; 169.1.2 "100
  відсоткам" of it per child for a taxpayer keeping two or more children under 18; 169.3.1 only the largest benefit;
  169.4.1: the benefit applies to a month's wage not above that subsistence minimum "помноженого на 1,4 та округленого
  до найближчих 10 гривень", times the number of children for 169.1.2, for "одному з батьків".
* Section XX subsection 10 item 16-1 (as restated by Law 4015-IX of 10.10.2024): 1.2 object = art. 163 income; 1.3(1)
  "5 відсотків від об'єкта оподаткування" during martial law; 1.7 income not in the taxable income is exempt.
* Law 4059-IX on the State Budget 2025 (archived 2025-04-10), art. 7: subsistence minimum from 1 January 2025 for
  "працездатних осіб - 3028 гривень"; art. 8: minimum wage 8 000 a month.
* Law 2464-VI on the single contribution (archived 2025-03-14): art. 4(1)(1) payers are the employers; art. 8(5) "22
  відсотки" of the art. 7 base: the employee pays nothing on wages. Self-employed persons (art. 4 payers) pay 22 % on
  their net income (base and minimum not modelled).
-/

namespace UaTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

def rate : Int := 1800          -- art. 167.1
def sched : Schedule := Schedule.flat rate
def divRate : Int := 500        -- art. 167.5.2
def levyRate : Int := 500       -- XX/10/16-1 item 1.3(1)
def esvRate : Int := 2200       -- Law 2464-VI art. 8(5)
/-- Budget law 2025 art. 7. -/
def pmAble : Int := 3028
/-- art. 169.1.1: 50 % of the subsistence minimum (monthly). -/
def pspBase : Int := divR .halfUp pmAble 2
/-- art. 169.4.1: subsistence minimum x 1.4 rounded to the nearest 10 hryvnias. -/
def pspLimit : Int := 10 * divR .halfUp (pmAble * 14) 100
#guard pspBase = 1514 ∧ pspLimit = 4240

/-- The monthly benefit of a parent with `kids` children under 18 on a monthly wage `m`, or of anyone with
`kids = 0`/1 (art. 169.1.1, 169.1.2, 169.3.1, 169.4.1). -/
def psp (m : Int) (kids : Nat) : Int :=
  let general := if m ≤ pspLimit then pspBase else 0
  let child := if kids ≥ 2 && m ≤ pspLimit * kids then pspBase * kids else 0
  max general child

/-- Income tax on one person's wages for the year (wages paid evenly over 12 months). The benefit is granted "за
його заявою" (art. 169.2.1: on the employee's application to the employer): claimed by default; the optional input
`uaPsp` = false models an employee who has not applied (round W5 review). -/
def wageTax (claim : Bool) (w : Int) (kids : Nat) : Int × Int :=
  let m := divR .halfUp w 12
  let b := if w > 0 && claim then 12 * min m (psp m kids) else 0
  (sched.tax Rule.unitHalfUp (pos (w - b)), b)

def out (c : Canon) : Out :=
  let claim := (c.bool? "uaPsp").getD true
  let wageTax := wageTax claim
  let kids := c.childrenUnder 18
  let ws := c.adults.map (fun a => pos a.wages)
  -- art. 169.4.1: the child benefit goes to one of the parents: the one for whom it saves more (an election)
  let opt (j : Nat) : List (Int × Int) := (ws.zip (List.range ws.length)).map fun (w, i) => wageTax w (if i = j then kids else 0)
  let rowsA := opt 0
  let rowsB := opt 1
  let taxA := sumInts (rowsA.map (·.1))
  let taxB := sumInts (rowsB.map (·.1))
  let rows := if c.adults.length = 2 && taxB < taxA then rowsB else rowsA
  let wTax := sumInts (rows.map (·.1))
  let psps := sumInts (rows.map (·.2))
  let se := sumInts (c.adults.map fun a => pos a.selfEmployment)
  let seTax := pct rate se
  let passive := pos c.interest + pos c.rentalIncome + pos c.capitalGains
  let pTax := pct rate passive
  let divTax := pct divRate (pos c.dividends)
  let levyBase := sumInts ws + se + passive + pos c.dividends
  let levy := pct levyRate levyBase
  let esv := pct esvRate se
  Out.make c "UA" "UAH" (wTax + seTax + pTax + divTax) (surtaxes := [("militaryLevy", levy)]) (employeeSocial := esv)
    (detail := [Out.d "taxBenefitPSP" psps, Out.d "wageTax" wTax, Out.d "passiveTax" pTax, Out.d "dividendTax" divTax,
      Out.d "militaryLevyBase" levyBase,
      Out.dStr "note" "PIT 18 % (art. 167.1), dividends 5 %; tax social benefit 1 514 a month if the month's wage <= 4 240 (art. 169); military levy 5 % (XX/10/16-1); no employee ESV on wages (Law 2464-VI art. 4, 8)"])
    (unsupported := (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled: art. 167.4 taxes the excess over an amount 'defined in 164.2.19', a subparagraph deleted by Law 466-IX (see FINDINGS)"] else []) ++
      ["wages assumed paid evenly over 12 months at the employer where the benefit is claimed",
       "self-employment taxed on the general system (18 % + 5 % levy, ESV 22 % of the given net income without the minimum); single-tax groups not modelled",
       "interest, rent and capital gains taxed as passive/other income at 18 % + 5 %; deposit-interest and once-a-year property-sale rules (art. 172, 173) not modelled",
       "special 150 %/200 % benefits (art. 169.1.3-169.1.4) not modelled"])

def country : Country := { code := "UA", name := "Ukraine (PIT + military levy)", currency := "UAH", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- 4 000 a month: benefit 1 514, PIT 18 % of 12 x 2 486 = 5 370, levy 5 % of 48 000 = 2 400. -/
#guard (out { id := "u", adults := [{ wages := 48000 }] }).incomeTax = 5370
/- One hryvnia more than the limit each month loses the whole benefit: 4 241 a month -> PIT 9 160. -/
#guard (out { id := "u", adults := [{ wages := 50892 }] }).incomeTax = 9161

end UaTax
