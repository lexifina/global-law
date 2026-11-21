# Croatia (Zagreb) 2025: what this work is useful for

Evidence: FINDINGS.md (F-numbers), CATALOGUE.md (L-numbers), Lean theorems in `lean/HrTax/` (names in backticks).
Amounts are for 2025, a Zagreb resident (23 %/33 %) and the stated household; "burden" = income tax + employee
contributions − doplatak za djecu.

## For a taxpayer
1. **Under 26 you pay no income tax on pay up to a base of 60.000 €; from 26 to 30, half** (ZPD čl. 46 st. 2), for the
   whole year in which you reach the age. A 30.000 € earner pays 0 at 25, 1.932 € at 26-30 and 3.864 € at 31
   (`Walls.young_steps`); a bonus paid in the year of the 30th rather than the 31st birthday saves 920 € (L06, F15). The
   relief comes in the annual assessment, not in the monthly payslip.
2. **Agree who claims the children.** The children's allowance can be split between parents in any proportion; the law's
   default is an equal split, which wastes the share of a parent with little income: 1.707 € a year for a couple with
   36.000 € + 9.000 € and three children (L04).
3. **One euro can cost hundreds.** A spouse whose own income passes 3.600 € a year stops being a dependant: the earner pays
   828 € more (F11, `Walls.dependant_cliff`). The doplatak za djecu falls in five steps of 159-742 € a year, each one euro
   wide: a one-earner family with two children loses 741 € of net income between 40.899 € and 40.900 € of pay (F10,
   `Walls.dzd_cliff`); the test uses last year's income, so the timing of a bonus decides it.
4. **Paušal obrt is far cheaper than a job at the same cost**: 4.230 € of tax and contributions on 60.000 € of receipts
   against 26.618 € for an employee costing the client 60.000 € (L01), but each class limit is a notch of 72-193 € (F12),
   the work must really be independent (RRiF on disguised employment), and the Government's bill of September 2026 cuts
   the deemed expenses of the top two classes.
5. **Zagreb withheld too much in January and February 2025** (old 23,6 %/35,4 % rates); the annual assessment refunds it
   (12 € at 24.612 €, 98 € at 96.000 €; F8).

## For an adviser
1. **Owner-managers of a d.o.o.: the minimum director's salary plus dividends** is the cheapest route (15.034 € on
   60.000 € of profit against 26.618 € all salary), but "no salary" is not free: a director not insured otherwise pays
   pension and health on 1.798 €/month himself, 7.875 € a year (ZD čl. 90-92; F16, `tools/owner_hr.py`). The generic
   scanner's company side (OECD placeholder) gets this wrong.
2. **Monthly rules, annual pay**: the 2024 pension-base reduction (300 € off the base up to 700 € of monthly pay,
   tapering to 1.300 €) and the monthly maximum base (10.788 €) are applied month by month with no annual settlement:
   24.000 € paid as 11 × 970 € + 13.330 € instead of 12 × 2.000 € saves 780,65 € of contributions, 601 € after tax, and
   the reduction does not lower pension rights (F13, `Walls.pay_timing`). Check labour-law limits first.
3. **Local rates differ by up to 8 points** (15-23 % lower rate, 25-33 % higher): 1.984 € a year on 40.000 € between
   Zagreb and a 15 % municipality (F14). The official calculator gives the wrong higher rate for općina Novigrad and a
   rate for Knin that the official table does not (F4): check the city's decision in Narodne novine.
4. **Pensioners' 50 % reduction is only for residents of group-I assisted areas and Vukovar** (ZPD čl. 46 st. 1,
   Pravilnik čl. 57); EUROMOD's country report gives it to every pensioner (F5).
5. **Capital income is taxed 12 % final, rent 8,4 % of the gross, gains after two years not at all** (L08-L10): 20.000 €
   as dividends instead of pay saves 5.280 € on top of a 30.000 € salary.

## For the government
1. **Correct Porezna uprava's "Primjeri izračuna za mlade"** (calculator PDF): the lowest column ignores the 2024
   pension-base reduction (tax due 44,55 €, not 0, at 9.000 € for a 26-30-year-old), the 9.000 € column's contributions
   (1.680 €) do not match its dohodak (7.200 €), and the 50 % relief at 24.000 € is 1.080 €, not 1.008 € (F3; checked by
   `Tests.pu_young30`, `Tests.pu_young_9000`).
2. **Fix the calculator's rate list and number parsing** (Novigrad 20 %/31 % for a 20 %/30 % općina; Knin 32 % vs the
   table's 30 %; amounts of 1.000.000 € and more give NaN) and **say in the law what rate applies when a unit keeps a
   decision above the new ceilings** (NN 152/24 čl. 14 is silent; F4, F9).
3. **Replace the doplatak's five all-or-nothing brackets with a glide** (F10): today one euro of income can cost a family
   742 € a year.
4. **Settle the pension-base reduction (ZD čl. 21.a) on the year's pay**, as čl. 206 already does for the maximum (F13).
5. **Clean up the wording**: čl. 24 st. 5 ZPD ("umirovljenicima ... ili poreznim obveznicima koji imaju prebivalište")
   invites the reading that every pensioner gets 50 % (F5); r.br. 11 of čl. 14 st. 3 still steps the 10th child by 1,1
   after the 2024 shift of the scale (F6). Validation note for statisticians: Eurostat's 2025 Croatian lines use a 22,4 %
   lower rate that no city applied in 2025 (F1).
