# New Zealand: what this work is most useful for

Evidence: FINDINGS.md (F-numbers), CATALOGUE.md (K-numbers), Lean theorems in `lean/NzTax/`.

## For a taxpayer
1. **Low-income working families: extra pay can leave you worse off.** In the minimum family tax credit band (salary up
   to $41,483 a year in 2025-26) every extra dollar is fully offset by a lower MFTC, and the 1.67 % ACC levy then
   makes you 1.67 c poorer per dollar (13.67 c with a student loan). Extra hours pay off only once income clears the
   MFTC band. (F10, `mftc_acc_over_100`, `mftc_sl_over_100`)
2. **Couples near the end of Working for Families: check the IETC.** While the family is entitled to any WFF, neither
   partner gets the $520 independent earner tax credit. Where WFF has abated to a few dollars a year, the credit is
   worth more: up to $1,040 for a couple. (F9, `wff_ietc_notch`)
3. **The IETC is not only for wage earners.** A partner with $24,000-$70,000 of investment income can get it, and it
   starts with a $520 jump at $24,000. (F12, K05)
4. **Help from family above $5,000 counts in full.** Payments by others towards household bills count as family income
   only above $5,000, and then entirely: $1 over the line can cost $1,350 of WFF. (F11, `help_notch`)

## For an adviser
1. **The 11-point gap between 28 % and 39 %** (company rate, maximum PIR, against the top personal rate) is the
   largest lever: PIE investment saves 11 % of investment income for a top-rate taxpayer; retained company profit
   defers 11 %; trust income above $10,000 is now taxed at 39 %, but distribution to adult beneficiaries on low rates
   still saves most of it. (K01, K02, K09, K10)
2. **Dividends instead of shareholder salary save the ACC earners' levy** (up to $2,551.59 in 2025-26), but below
   roughly a 28 % average personal rate the excess imputation credits are lost to a loss carry-forward: run the
   numbers both ways. (F16, K03, K03b)
3. **Investment assets in the lower-income spouse's name** save tax at the rate gap and can add an IETC; New Zealand
   has no attribution of investment income between spouses. (K04, `spouse_split`)
4. **The personal-services attribution rule still starts at $70,000** although the 33 % band now starts at $78,100.
   (F8)

## For the government
1. **Define MFTC "income after tax" net of the ACC earners' levy (and student loan repayment)**, or taper the MFTC at
   less than 100 %: as written, the band has an effective marginal rate of 101.67 % for every working family in it.
   (F10)
2. **Make the WFF/IETC boundary continuous.** Abating the IETC against remaining WFF (instead of barring it while any
   WFF is due) removes a $1,040 notch, and settles whether "entitled", "eligible" or "receive" is the test (IRD's web
   page and its special report use different words). (F9)
3. **Fix the published guidance**: the July 2025 IR271 chart divides the FTC by 365/7 weeks while IRD's rule and its own
   example divide by 52 (185 of 318 cells $1-$2 a week low); the 2025-26 MFTC and IWTC examples kept pre-Budget figures
   ($7,111, $5,330); the special report's IETC example has an arithmetic error ($477.66 for $476.67) and its composite
   formula as printed goes negative. (F3-F7)
4. **Review thresholds that track the rate scale but were not moved in 2024**: the $70,000 attribution threshold, and
   the all-or-nothing $5,000 household-help rule in family scheme income. (F8, F11)
5. **What is right and worth keeping**: IRD's PAYE tables equal its published payroll formulas on all 69,228 cells,
   and the formulas equal the statute for every income (proved); the OECD's model reproduces the 2025-26 tax and WFF
   exactly. The OECD omits the ACC earners' levy from New Zealand's wedge (F1) and day-weights 2024-25 instead of
   using the Act's composite rates (F2). The public OpenFisca-Aotearoa model is stale (2010 tax rates; F14).

## For a researcher
A Lean model of New Zealand's 2025-26 (and 2024-25 composite) personal income tax, IETC, ACC earners' levy, Working
for Families and student loan repayments on the shared kernel, exact against the OECD's 2025 lines and IRD's PAYE
specification; 30 theorems (incl. table = statute for every income, composite rates ≤ day-weighted, the WFF
two-credit abatement equals one abatement of the sum) and 19 checks of official examples.
