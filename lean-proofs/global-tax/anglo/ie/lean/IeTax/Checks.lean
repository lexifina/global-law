import IeTax.Model

/-!
# Official worked examples, checked at compile time (`#guard`)

Revenue's examples ignore USC and PRSI where they say so; each check computes only the line the example shows.

* TDM Part 44-01-01 "Income tax treatment of married persons and civil partners" (last updated December 2025),
  https://www.revenue.ie/en/tax-professionals/tdm/income-tax-capital-gains-tax-corporation-tax/part-44/44-01-01.pdf
  (`refs/tdm/44-01-01.txt`): Example 3 (year of marriage 2025), Examples 5 and 7 (2025).
* TDM Part 18D-00-01 "Universal Social Charge" (last reviewed January 2026, examples for 2026),
  https://www.revenue.ie/en/tax-professionals/tdm/income-tax-capital-gains-tax-corporation-tax/part-18d/18D-00-01.pdf
  (`refs/tdm/18D-00-01.txt`): para. 4.1 Examples A and B and para. 4.3 (Sinead). The 2026 bands (first €12,012,
  next €16,688, next €41,344, para. 4.1) are given to the same code.
-/

namespace IeTax
open TaxKernel

/-- A PAYE employee with `w` euro of wages. -/
def emp (w : Int) (age : Nat := 40) : Person := { age, wages := eur w }

/-! ## TDM 44-01-01 Example 3: married 10 July 2025; spouse 1 €48,000, spouse 2 €24,000 (PAYE) -/
-- "Tax payable (€10,400 - €4,000) €6,400" and "(€4,800 - €4,000) €800"
#guard (singleIT (emp 48000) false 0).tax = eur 6400
#guard (singleIT (emp 24000) false 0).tax = eur 800
-- joint: "€72,000 x 20% €14,400 ... Total Credits €8,000 ... Tax payable €6,400"
#guard (jointIT (emp 48000) (emp 24000) 0).grossTax = eur 14400
#guard (jointIT (emp 48000) (emp 24000) 0).tax = eur 6400

/-! ## TDM 44-01-01 Examples 5 and 7: Philip €45,000 employment, Mark €27,000 investment income (2025) -/
def mark : Person := { dividends := eur 27000 }
-- Example 5, joint: "Tax payable (€14,400-€6,000) €8,400"
#guard (jointIT (emp 45000) mark 0).tax = eur 8400
-- Example 7, separate treatment: "Combined Tax Payable (€5,200 + €3,400) €8,600"
#guard (singleIT (emp 45000) false 0).tax = eur 5200
#guard (singleIT mark false 0).tax = eur 3400
-- and the household function picks joint assessment (best of the two)
#guard (hhCalc { persons := [emp 45000, mark], married := true, kids := 0 }).it = eur 8400

/-! ## TDM 18D-00-01 (2026 bands) -/
def usc2026 : Schedule :=
  Schedule.ofList [(0, 50), (usc1, 200), (usc1 + eur 16688, 300), (usc1 + eur 16688 + eur 41344, 800)]
-- Example A: "Emma has annual gross income of €65,000 ... USC liability for 2026 is therefore €1,482.82"
#guard uscWith usc2026 uscReducedSchedule (emp 65000) = 148282
-- Example B (full medical card, €55,000: the Part 2 rates, as for 70+): "€919.82"
#guard uscWith usc2026 uscReducedSchedule (emp 55000 70) = 91982
-- para. 4.3: Sinead, €40,000 PAYE + €110,000 non-PAYE investment income: "€8,330.62"
#guard uscWith usc2026 uscReducedSchedule { wages := eur 40000, dividends := eur 110000 } = 833062
-- para. 1: "Gross income of €12,500 ... no USC applies"
#guard uscWith usc2026 uscReducedSchedule (emp 12500) = 0

/-! ## OECD Taxing Wages 2025, Ireland, single at 100 % AW (GEBT €60,257.78): CGITLETC €15,303.11, USC
(CGITFP − CGITLETC + TC) €1,353.73 — at the whole-euro wage €60,258 the model gives the same to the cent after the
€0.22 of wage rounding (harness/oecd_ie.py has every line). -/
#guard grossTax bandSingle (eur 60258) = 1530320
#guard usc (emp 60258) = 135374

/-! ## Table vs statute: Revenue's Employers' Guide to PAYE (TDM Part 42-04-35A, last reviewed September 2026,
https://www.revenue.ie/en/tax-professionals/tdm/income-tax-capital-gains-tax-corporation-tax/part-42/42-04-35A.pdf,
`refs/tdm/42-04-35A.txt`, para. 9.3). Weekly cut-off point and credit are the annual amounts / 52 rounded **up** to
the cent ("€44,000 (per year), €846.16 (per week)", "€4,000 (per year), €76.93 (per week)"). -/
def weeklyOf (annual : Int) : Int := ceilDiv annual 52
#guard weeklyOf (eur 44000) = 84616
#guard weeklyOf (eur 4000) = 7693
/-- One week's PAYE income tax (week 1, non-cumulative), each band rounded half up to the cent as the guide does. -/
def payeWeek (cut cred pay : Int) : Int :=
  divR .halfUp (standardRate * min pay cut) BP + divR .halfUp (higherRate * pos (pay - cut)) BP - cred
-- "Pay for income tax purposes: €950 ... Net tax due this pay period = €133.84"
#guard payeWeek (weeklyOf (eur 44000)) (weeklyOf (eur 4000)) (eur 950) = 13384
-- over 52 weeks the rounded-up figures give €0.32 more band and €0.36 more credit than the statute's annual amounts
#guard 52 * weeklyOf (eur 44000) - eur 44000 = 32
#guard 52 * weeklyOf (eur 4000) - eur 4000 = 36

/-- One week's USC with weekly cut-off points (cents) and rates 0.5 / 2 / 3 / 8 %. -/
def uscWeek (c1 c2 c3 pay : Int) : Int :=
  (Schedule.ofList [(0, 50), (c1, 200), (c2, 300), (c3, 800)]).ticks pay / BP
-- The guide's own 2026 weekly cut-off points (€231.00, €551.92, €1,347.00) on Mary's €1,000: €21.01, which is
-- 1/52 of the annual 2026 USC on €52,000 (€1,092.82). The guide prints "Total USC due this pay period = € 26.00",
-- computed with the 2025 cut-off €526.58 and a 4 % third rate (the 2024 rate): FINDINGS F5.
#guard uscWeek 23100 55192 134700 (eur 1000) = 2101
#guard uscWith usc2026 uscReducedSchedule (emp 52000) = 109282
-- the guide's lines: "€295.58 (€526.58 - €231) @ 2% = € 5.91", "€473.42 @ 3% = €18.94": €18.94 is 4 % of €473.42;
-- 3 % is €14.20
#guard divR .halfUp ((52658 - 23100) * 200) BP = 591
#guard divR .halfUp ((eur 1000 - 52658) * 400) BP = 1894
#guard divR .halfUp ((eur 1000 - 52658) * 300) BP = 1420

end IeTax
