# Sweden 2025: what is most useful to know (with the evidence)

Everything below is computed by the Lean model of the 2025 statute (`lean/SETax`), which reproduces the OECD's
Swedish figures (56 of 56 lines), 22 of Skatteverket's own worked examples and all 26 936 cells of Skatteverket's
2025 withholding tables exactly. Amounts for a Stockholm resident outside Svenska kyrkan.

## For a taxpayer
1. **If you work after 66 on modest pay, the 7 % pensionsavgift is a real cost.** Up to 213 000 kr of pay you pay
   the whole fee (14 000 kr at 200 000 kr) even though your income tax is zero; the "skattereduktion för allmän
   pensionsavgift" only replaces jobbskatteavdrag you could not use (F2, `f2_old_worker_fee_is_a_cost`). It still
   earns pension rights. The same holds under 66 for pay of 25 000-53 000 kr.
2. **Very small jobs: 24 800 kr a year is free, 24 900 kr costs 1 700 kr** (F1, `f1_fee_notch`). Above that, each
   100-kr step of the fee can cost 100 kr for one krona more pay until about 85 000 kr (309 000 kr at 66+).
3. **Couples: put deductions and gifts where they count.** Interest deductions give 30 % only up to 100 000 kr
   per person and only against your own tax: 300 000 kr of interest on a low earner's return can be worth 72 000 kr
   less than on the earner's (F12). Gifts to approved charities: give at least 2 000 kr each, and up to 12 000 kr
   each, to get the 3 000 kr reduction twice (F13).
4. **Expect a refund: Stockholm's tables over-withhold about 3 300 kr a year at the average wage** (F5), by
   design (whole-percent tables that assume 1,16 % church and burial fees; Stockholm's burial fee is 0,07 %).

## For an adviser
1. **Owner-managers (3:12, 2025, förenklingsregel):** salary pays until 475 100 kr (8,08 pbb, where the
   jobbskatteavdrag stops rising); above that, dividends taxed as salary (20,6 % bolagsskatt, no
   arbetsgivaravgifter) leave about 2,3 % more of the profit than salary, before valuing pension and sickness
   rights (F14). From 2026 the 3:12 rules are recast (SFS 2025:1361): redo the comparison.
2. **Credit order matters for low earners with capital income**: whether the pensionsavgift credit is taken
   first against the municipal tax or the capital tax changes the result by up to 3 520 kr (F3); ask Skatteverket
   or check the beslut om slutlig skatt.
3. **Löneväxling and timing:** above the brytpunkt (643 100 kr) each 10 000 kr exchanged saves 5 067 kr now
   against about 2 500 kr later at 66+ (F15); bunching 800 000 kr in one year instead of two costs 72 458 kr (F11).

## For the Swedish government (Finansdepartementet, Skatteverket)
1. **Decide whether the pensionsavgift is meant to be fully tax-compensated.** The 67 kap. 2 § order makes the
   compensation disappear for working pensioners up to 213 000 kr and for under-66 earners up to 53 000 kr (F2);
   the fix is in how the fee credit and the jobbskatteavdrag share the municipal tax.
2. **Close the gap in 67 kap. 2 §:** say which tax a credit allowed against both municipal and state tax uses first
   (F3; draft question in FINDINGS).
3. **Make the formulas continuous at their joints** (coefficients rounded to 3-4 decimals): the förhöjt
   grundavdrag jumps by 233,64 kr at 1,965 pbb, giving pensioners a negative marginal rate (100 kr more pension,
   64 kr less tax), and the jobbskatteavdrag falls at 8,08 pbb (F4); the 2026 wording keeps both kinds.
4. **What checked out:** the 2025 withholding tables are exactly the statute applied to each band (F6), the
   skiktgräns and prisbasbelopp follow their indexation rules (F9), and the OECD's Swedish figures are exact (F7);
   an inconsistency between SFS 2025:539 and 2025:1361 was repaired before it took effect (F8).
