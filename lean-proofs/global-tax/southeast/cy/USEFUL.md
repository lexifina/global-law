# Cyprus 2025: what is most useful to know (evidence in FINDINGS.md and lean/CYTax)

## For a taxpayer
1. **Family income just above 49.000 € (one child, or any lone parent) or 59.000 € (two children) costs you the whole
   child benefit at once.** A lone parent of two at 49.000,01 € loses 4.708 € a year of child and single-parent
   benefit for one cent of extra income; a couple with two children loses 870 € at 59.000,01 €, four children 5.721 € at
   69.000,01 €. The test uses the previous year's gross family income, so a bonus or a dividend that lands in the wrong
   year can cost more than it brings (F4; Lean `cb_cliff_*`, `sp_cliff_one_child`; METR peak 6.862 %).
2. **Interest: 12.000 € of total income is a hard line.** Below it the SDC on deposit interest is 3 %, above it 17 % on
   all the interest (F5, `sdc_interest_notch`).
3. **Moving to Cyprus for a job over 55.000 €:** the 50 % exemption (art. 8(23Α)) switches on at 55.000,01 €
   (+6.996 € net for one cent at the threshold), but the one-fifth cap on contributions means about 800 € of your SI and
   GESY is not deductible (F2, F3).

## For an adviser
1. **Owner-managers:** a salary of about 22.000-24.500 € and the rest as dividends is optimal for a domiciled owner in
   2025 (71-76 % of profit kept); a non-domiciled owner keeps 85 % by taking no salary at all (F6).
2. **The 2026 reform rewards waiting, but only for pay, and for dividends only after 2031.** A 12.000 € bonus moved from
   December 2025 to January 2026 saves 600 € at 60.000 €; dividends out of 2025 profits pay 17 % SDC whenever paid until
   31.12.2031 and 5 % after, while 70 % of 2024-2025 profits are deemed distributed at 17 % anyway (F8, F10).
3. **Spouses are taxed separately:** rent or deposits in the lower-income spouse's name cut income tax and SDC (F7).

## For the government
1. **Write the applied social insurance rates into the law.** SIL art. 5(1)(στ) prints 8,9 % (16,8 % self-employed)
   but 8,8 % (16,6 %) is charged; a reader of the statute gets every payslip wrong by 0,1 % (F1).
2. **Replace the benefit cliffs with tapers** (child benefit, single-parent benefit, SDC interest at 12.000 €, the
   23Α 55.000 € test): each is a 100 %+ marginal rate on a one-cent band (F2, F4, F5).
3. **Close the drafting gaps the 2026 reform left:** the 2008 scale still says "and thereafter" next to the 2026
   scale (F11); child-benefit column (2) moves with the 22.000 € tax-free band but column (3) and Table B do not, so
   incomes of 39.000-44.000 € fall in two columns from 2026 incomes on (F12); decide whether pre-2026 reserves paid
   after 2031 should really fall to 5 % (F10). EUROMOD's report should correct the GESY deduction ceiling (4.770 €,
   not 3.060 €) and date the 2 %/10 % limits to 2026 (F9).
