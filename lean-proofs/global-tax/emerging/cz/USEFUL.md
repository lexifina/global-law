# Czechia 2025: what this work is useful for

Evidence: FINDINGS.md (F-numbers), CATALOGUE.md (L-numbers), Lean theorems in `lean/CzTax/` (names in backticks).
Amounts are for 2025 and the stated household; "burden" = income tax + contributions − přídavek na dítě.

## For a taxpayer
1. **124 800 Kč of wage or self-employment receipts unlocks the child bonus.** Below it a parent with no tax to
   offset gets nothing; at it, 15 204 Kč (one child) to 65 364 Kč (three) (F9, `bonus_notch_124800`). A short job or
   small business income in the year is worth checking.
2. **Who claims the children can be worth 20 000–51 000 Kč through the přídavek na dítě.** The benefit tests
   income after tax, and the refundable bonus is not counted: letting the lower earner claim (F6, `n2_allocation_gain`:
   51 240 Kč, three children) or not claiming one child (F5, `n1_forgo_credit_gain`: 20 076 Kč) can bring the family
   under 3,4 × životní minimum. The same income definition is in the new dávka státní sociální pomoci (zákon
   151/2025 § 4). Check the reading with the Úřad práce first (reading-dependent).
3. **The spouse credit (24 840 Kč) needs a child under 3 and the spouse's own income at most 68 000 Kč for the whole
   year** (F9, F11). One crown more loses all of it; it is never given in monthly payroll, only in the annual
   settlement or a return (F10).
4. **A DPP side job below 11 500 Kč a month carries no social or health insurance** (16 022 Kč a year at the limit,
   F9, `dpp_notch_year`); 15 % is withheld as final tax unless included in the return.
5. **Payroll over-withholds a little every year** (100–123 Kč on average, up to 684 Kč with children, never less than
   the annual tax: F10, `withholding_ge_annual`). Ask the employer for the roční zúčtování.

## For an adviser
1. **Regime choice dominates everything else for an owner-manager.** From the same 1 M Kč business result an
   employee keeps 579 426 Kč, an OSVČ with real costs 652 740, with the 60 % paušál 868 888, with the 80 % paušál or the
   paušální daň 905 190 / 895 408, an s.r.o. paying dividends 637 804 (CATALOGUE regime table; L01, L04). The
   s.r.o. beats an OSVČ with real costs only from about 3 M Kč.
2. **Paušální daň band edges are notches**: 1 Kč over 1 000 000 Kč of receipts in the 40 % class costs 96 348 Kč
   for the year (F8, `pausal_band_notch`); time invoices around the limit. A client in the paušální daň cannot use
   the child credit: let the other parent claim (blind search, 39 households).
3. **§ 13 spolupracující manžel**: giving up to 50 % (max 540 000 Kč of profit) to a spouse with no income saved up
   to 99 086 Kč in the grid (L10); it excludes the spouse credit (§ 13 odst. 4 písm. c)).
4. **Dividends are outside the přídavek income test** (ZSSP § 5 lists only ZDP §§ 6, 7, 9, 10 income): a family
   living on s.r.o. dividends of ~900 000 Kč still receives the přídavek (L16, 23 280 Kč net of other effects).
5. **The 40 M Kč cap on the share-sale exemption is per year** (§ 4 odst. 3): spreading an exit over two years kept
   2 135 076 Kč of tax at 50 M Kč (L08b).

## For the Czech government
1. **Delete the dead cap in § 35c odst. 7** ("; maximální výše daňového bonusu podle odstavce 3 zůstává
   zachována"): § 35c odst. 3 has had no maximum since zákon 609/2020 (F3; Global law phrase_history).
2. **The means test rewards paying more tax.** Because the přídavek (and the DSSP, zákon 151/2025 § 4 odst. 2) counts
   income after tax and ignores the refundable child bonus, families gain 20 076–51 240 Kč by allocating or forgoing
   child credits (F5, F6, proved in Lean). Counting income before the child credit (or adding the bonus back) closes it.
3. **Six all-or-nothing tests produce one-crown notches of 15 000–125 000 Kč** (F7–F9: bonus 124 800 Kč, spouse
   68 000 Kč, DPP 11 500 Kč/month, side OSVČ 111 736 Kč, přídavek 3,4 × ŽM, paušální daň bands). Each is proved or
   computed on a named household; a taper would remove each.
4. **The tax-relief report omits the self-employed reliefs** (F12): MF's 2023 quantification lists 27 PIT reliefs
   but not the výdaje paušálem or the paušální daň, which the model shows are worth 178 338 Kč and up to 108 510 Kč for
   single households (L02, L03).
5. **Un-indexed amounts drift**: the 68 000 Kč spouse limit has not changed since 2008 while the bonus and pension
   tests in the same act move with the minimum wage (F11).
