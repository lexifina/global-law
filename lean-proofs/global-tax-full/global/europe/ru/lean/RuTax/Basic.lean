import TaxKernel.World

/-!
# Russia: налог на доходы физических лиц (Tax Code part two, chapter 23), tax resident, 2025

Statutes read (files in `ru/law/`):
* Federal Law of 12.07.2024 No. 176-FZ (kremlin.ru/acts/bank/50837, pages 1-12, the official text as published), art. 2
  item 36: new art. 224 (1) "13 процентов - если сумма налоговых баз, указанных в пункте 21 статьи 210 … равна 2,4
  миллиона рублей или менее; 312 тысяч рублей и 15 процентов … превышающей 2,4 миллиона рублей … не более 5 миллионов;
  702 тысячи рублей и 18 процентов … не более 20 миллионов; 3402 тысячи рублей и 20 процентов … не более 50 миллионов;
  9402 тысячи рублей и 22 процента … превышающей 50 миллионов рублей"; art. 224 (1.1) for the art. 210 (6) base
  (dividends, securities): "13 процентов … не более 2,4 миллиона рублей; 312 тысяч рублей и 15 процентов". Item 28:
  art. 218 (1) 4 child deductions "1 400" → "2800" (second child), "3 000" → "6000" (third and later), limit
  "350 000" → "450 000". Art. 8 (2): these items "вступают в силу с 1 января 2025 года" (wording of 362-FZ).
* Federal Law of 21.11.2011 No. 330-FZ (Global law `russia/national/acts/fz/2011/330`, official text
  actual.pravo.gov.ru t=69196): art. 218 (1) 4 "1 400 рублей - на первого ребенка"; "Налоговый вычет производится на
  каждого ребенка в возрасте до 18 лет"; "Налоговый вычет действует до месяца, в котором доход налогоплательщика,
  исчисленный нарастающим итогом с начала налогового периода … превысил" the limit.
The consolidated chapter 23 was not read (pravo.gov.ru timed out); provisions outside these two laws are flagged.
Unit: individual (each parent claims the child deduction). Employees pay no social insurance contributions in Russia
(insurance contributions are the insurer's, Tax Code ch. 34): not read here, so employeeSocial = 0 is flagged.
-/

namespace RuTax
open TaxKernel

/-- art. 224 (1) (176-FZ): the scale for the art. 210 (2.1) bases (wages and other main income). -/
def sched : Schedule :=
  Schedule.ofList [(0, 1300), (2400000, 1500), (5000000, 1800), (20000000, 2000), (50000000, 2200)]
/-- art. 224 (1.1): the scale for the art. 210 (6) bases (dividends, securities). -/
def schedInv : Schedule := Schedule.ofList [(0, 1300), (2400000, 1500)]

/- The fixed sums printed in art. 224 (1) ("312 тысяч", "702 тысячи", "3402 тысячи", "9402 тысячи") are the band sums. -/
#guard sched.ticks 2400000 = 312000 * BP ∧ sched.ticks 5000000 = 702000 * BP ∧
  sched.ticks 20000000 = 3402000 * BP ∧ sched.ticks 50000000 = 9402000 * BP
#guard schedInv.ticks 2400000 = 312000 * BP

/-- art. 218 (1) 4: monthly deduction per child by rank (1 400 / 2 800 / 6 000). -/
def childMonthly (rank : Nat) : Int := if rank = 0 then 1400 else if rank = 1 then 2800 else 6000
def childLimit : Int := 450000

/-- The year's child deduction of one parent with annual main income `inc` paid evenly over 12 months: months whose
cumulative income has not exceeded 450 000 (from the month it exceeds, none). -/
def childDeduction (inc : Int) (nKids : Nat) : Int :=
  let perMonth := sumInts ((List.range nKids).map childMonthly)
  let months := (List.range 12).filter (fun (m : Nat) => decide (divR .down (inc * ((m : Int) + 1)) 12 ≤ childLimit))
  perMonth * (months.length : Int)

def taxOn (s : Schedule) (x : Int) : Int := s.tax Rule.unitHalfUp (pos x)

def out (c : Canon) : Out :=
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let kids := c.childrenUnder 18
  let rows := (c.adults.zip (List.range n)).map fun (a, i) =>
    let main := a.wages + a.selfEmployment + share c.rentalIncome i
    let ded := min main (childDeduction main kids)
    let inv := share (c.dividends + c.capitalGains) i
    (main - ded, ded, inv)
  let mainTax := sumInts (rows.map fun r => taxOn sched r.1)
  let invTax := sumInts (rows.map fun r => taxOn schedInv r.2.2)
  Out.make c "RU" "RUB" (mainTax + invTax)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map (·.1))), Out.d "childDeductions" (sumInts (rows.map (·.2.1))),
      Out.d "investmentBaseTax" invTax])
    (unsupported := (if c.interest ≠ 0 then ["interest (deposit interest exemption art. 214.2) not modelled; interest ignored"] else []) ++
      (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions (art. 217 exemptions) not read; pensions ignored"] else []) ++
      ["employee social contributions: none modelled (insurance contributions are paid by the employer, Tax Code ch. 34, not read)",
       "rounding to whole rubles half up (art. 52 (6) not read)",
       "self-employment taxed in the main base (special regimes such as НПД not modelled)"])

def country : Country := { code := "RU", name := "Russia (НДФЛ, tax resident)", currency := "RUB", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

end RuTax
