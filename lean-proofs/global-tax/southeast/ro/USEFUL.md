# RO Romania 2025: USEFUL (the 3-5 things each reader most needs)

## A taxpayer
1. **Near the minimum wage, check the net before accepting a raise.** Between 4.050 and 6.050 lei gross a month every
   50-lei step costs more than the leu that crosses it (F1); a raise of the base salary from the minimum wage loses the
   300 untaxed lei of 2025 and costs 125 lei a month until the base reaches 4.279 lei (F3). Evidence: `F1_step_metr_over_100`,
   `F3_notch_base`, `F3_break_even`.
2. **Parents and under-26s face a cliff at 6.051 lei gross a month** (minimum wage + 2.001): up to 161 lei a month
   lost for one leu (F2). A small pay cut or salary sacrifice back to 6.050 lei pays. Evidence: `F2_cliff`.
3. **Investment and rental income: the 24.300-lei line (6 minimum wages, net of withheld tax) is worth 2.430 lei of
   CASS.** 27.000 lei of dividends pay 2.430 lei CASS, 26.999 pay none; spouses each have their own line (F5, F6).
4. **Pensioners above 3.000 lei a month pay 10 % CASS on the excess since August 2025** (and tax on what is left):
   2025 is a mixed year (F9).

## An adviser
1. **Owner-managers (2025): micro + minimum salary + dividends ~80 % of profit up to ~760.000 lei; above that a PFA in
   sistem real keeps more** (caps on CAS and CASS), and with the 2026 16 % dividend rate the crossover falls to
   ~300.000 lei (F10, `F10_crossover`, `results/search/owner_ro.json`).
2. **Dividends: 2025 interim dividends stay at 10 % (Legea 141/2025 art. VII alin. (2))**; the consolidated Code shows
   16 % from August 2025, but it applies to dividends distributed from 1 January 2026 (F7, F16).
3. **Split investment income with a spouse only below the cap**: under 6 minimum wages each it removes CASS, above 24
   it doubles it (F6).
4. **The dependent-spouse test counts all income**: a spouse earning 811 instead of 810 lei a month can cost 240 lei
   a year (F4).

## The government (and the EU modellers)
1. **Replace the 50-lei step table of art. 77 alin. (4) by a continuous taper ending at 0 for every column** (or
   index the lei steps): 40 points of METR > 100 % and cliffs of up to 161 lei a month (F1, F2, F18); the steps'
   bite rises with every minimum-wage increase.
2. **Phase out the 300/200-lei minimum-wage facility instead of switching it off at one leu** (F3): the rule taxes
   raises of the base salary.
3. **Repeal annulled texts promptly**: provisions found unconstitutional by CCR 650/2022 stayed in the Code until
   August 2025 (F15); commencement rules that differ from the in-force date (Legea 141/2025 art. VII) should be shown
   in the consolidated text (F16).
4. **Eurostat/EC: the 100-lei deduction is per child, not per earning parent; the basic deduction is stepped, not
   linear** (F12, F13); EUROMOD's 2025 report should describe the 300-lei facility (F14).
