# Ireland 2025: what this work is useful for

## For a taxpayer
1. **Married or in a civil partnership? Joint assessment is never worse than being taxed as two single people** (a
   Lean theorem for the bands, `joint_gross_le_single`, and 0 exceptions in 3,966 couples, F13). A one-earner couple
   pays €3,800 less than the same couple unmarried.
2. **Watch the cliffs where earning more leaves you poorer**: €13,000 (USC on the whole income, €79.82, F10); €352 a
   week of pay (PRSI, €2.43 a week, rising to €4.54 by 2028, F9); €5,000 of self-employed or rental income (PRSI
   €650 minimum, F19); €60,000 at 70+ (USC, €326, F16); the end of the working family payment (€1,035 a year lost
   at once; a lone parent with 2 children needs about €1,970 more gross pay to get back to where they were, F17).
3. **Working family payment is fixed for 52 weeks on your income when you claim**: claim when income is lowest (F18).

## For an adviser
1. **Put investment income in the lower earner's name**: the married band rises by the lower spouse's income from
   any source (Revenue's own Example 5); €50,000 of dividends or rent moved to a non-earning spouse saves €9,954 a year
   (F12). Transfers between spouses are free of CGT.
2. **Owner-managers**: salary as a 50 %+ director (Class S, no employer PRSI) beats dividends after 12.5 % CT by
   €4,744 at €30,000 of profit to €20,523 at €250,000 (F15).
3. **PRSI on a rate change**: Class S for 2025 is charged at the blended 4.125 % (4.025 % for 2024), a reading the Act
   does not state (F3).

## For the government
1. **Index the PRSI credit to the rate**: the €12 credit was set in 2016 for a 4 % rate; five enacted rises take the
   notch at €352.01 from €2.08 to €4.54 a week. Making the maximum credit "the rate × €352" removes it at any rate
   (F9, theorems `prsi_notch_400/410/420/470`).
2. **Fix three published errors**: Revenue's Employers' Guide to PAYE USC example (€26.00 printed, €21.01 correct,
   F5); the Law Reform Commission's revised SWCA showing the employer PRSI threshold as €527 from 1 October 2026
   though Act 19/2025 made it €552 (F6); the notes for guidance quoting a €1,650 basic credit (F7). Draft texts are
   in FINDINGS.md.
3. **Publish a consolidated Taxes Consolidation Act**: the TCA is not among the Law Reform Commission's revised acts;
   a model of 2025 income tax has to be assembled from Finance Act 2024 amendments and Revenue's notes for guidance.
   Publishing the Revenue PAYE/USC cut-off rounding rules (F8) and the WFP €20 prescribed amount as text would also
   help anyone who checks a payslip.

## For a researcher
- An executable, cited model of Irish income tax, USC, PRSI (Class A1 weekly, Class S), child benefit and the working
  family payment for 2025 (`lean/IeTax`, exe `ietax`, contract in/out), agreeing with the OECD's Taxing Wages on 31 of
  32 lines to €1 under the OECD's conventions and on all 32 within 1 % (the gaps are the OECD's: F1, F2, F4), and with
  15 Revenue worked examples to the cent.
- Ireland is a credit system (allowances as tax credits at 20 %), with a separate individual levy (USC) and weekly
  social insurance: three different units of account (couple / individual / pay week) in one wage.
