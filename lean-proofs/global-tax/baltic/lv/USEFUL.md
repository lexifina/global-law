# Latvia 2025: what this work is useful for

Evidence: FINDINGS.md (F-numbers), CATALOGUE.md (K-numbers), Lean theorems in `lean/LvTax/` (names in backticks).
Amounts in euro for 2025 and the stated household; "burden" = income taxes + contributions − family benefit.

## For a taxpayer
1. **Earning more than 105 300 euro a year from one job: put about 10 % of the excess aside for the return.** The
   employer withholds 25,5 % all year; the 33 % band and the loss of most of the solidarity-tax deduction come with
   the annual return: 4 492 on a 150 000 wage, 22 567 on 300 000 with the 3 % (F7, `withholding_gap`).
2. **Self-employed near 740 euro a month: one euro over costs about 116 that month.** Below the minimum wage only
   10 % pension contributions are due, at it 31,07 % of 740 (F1, `f1_se_notch`: 1 393 a year at 8 880, and the loss
   is only made good at 10 960). The extra buys sickness and maternity cover; decide knowingly.
3. **Claim the children on the tax book of the parent who pays enough tax.** The relief is 250 a month per child and
   is lost if the claiming parent's income cannot absorb it: 2 258 a year for wages 7 000 + 30 000 with three
   children (F4, `f4_allocation`).
4. **A spouse at home with a child under 3 (or three children, one under 7) is worth 765 a year, but only if you are
   married and the spouse has no job at all** (F3, `f3_spouse_notch`, `f3_marriage_bonus`).
5. **Every deduction is worth 25,5 %, even if you pay 33 %:** 600 of donations or education costs return 153, 4 000 of
   private pension contributions return 1 020 (F9, `deduction_worth_255`; VID example `vid_ad_ex1`).

## For an adviser
1. **Owner-managers: dividends (20 % in total) beat salary at every profit level in 2025** (31 % to 48 % all
   salary; gains 1 216 to 60 757 a year: F6, generic owner scan). Watch the board member's minimum VSAOI object
   (VSAOI 14(12.1)) and the 2026 switch to UIN 4.2 (15 % + 6 % IIN).
2. **The author's royalty regime (25 % final, to the end of 2027) keeps 8 964 more than employment on a 50 000
   payment and 56 749 more on 250 000**, and it stays outside the 33 % band and the 3 % rate (F5, PN 163-171, 200).
3. **Micro-enterprise tax (25 % of turnover up to 50 000) beats the general self-employed regime only with low
   costs** (turnover 30 000 without costs: 2 218 a year; CATALOGUE K3). VID leaves micro income out of the 3 %
   additional rate, but the statute has no express exception (F13): a client above 200 000 carries that risk (≤ 1 500).
4. **The self-employed 31,07 % is charged per month with income ≥ 740:** the same profit received in fewer months
   costs up to 1 277 a year less (F2, `f2_se_months`; reading-dependent: the month in which income arises).
5. **Do not compute the 33 % band on taxable income** (as VID's 2025 information material words it): it applies to
   income above 105 300, with deductions taken at 25,5 % (F8, `lowband_cost`: 352,50 on income 110 000).

## For the government (VID, Finanšu ministrija, Saeima)
1. **Remove the self-employed notch at the minimum wage** (F1, F2): an all-or-nothing monthly test creates a
   2 080-euro band where more profit leaves less, and rewards bunching income into one month (1 277 a year). A
   phase-in (e.g. 31,07 % on the part of the object above a threshold) or an annual test would remove both.
2. **Correct the wording in "Izmaiņas iedzīvotāju ienākuma nodoklī no 2025. gada"** (F8: "apliekamajam ienākumam
   virs 105 300" vs the statute's "gada ienākuma daļai") and **state the legal basis for leaving micro income out of
   the 3 % base, or add it to PN 200** (F13).
3. **Fix the text of IIN 12(1)**, which says 570 euro a month in the 2025 and 2026 consolidated versions while the
   amounts in force are 510 and 550 (PN 197; F10), and the stale cross-reference lists in 13(6) (F12) and 15(2)/15(11)
   (F11).
4. **The non-working spouse relief is a 765-euro notch and marriage bonus** (F3): one euro of wages ends it; a
   phase-out by the spouse's income would remove the notch.
5. **The employee pays 10,5 % above 105 300 as solidarity tax with no refund and almost no deduction** while the
   employer is refunded (F14): the marginal rate on wages is 43,37 % from 105 300 and 46,37 % from 200 000, against
   20 % for an owner who takes dividends (F6) and 25 % for a royalty (F5).

Validation behind all of this: OECD Taxing Wages 2025 country table 56/56 lines exact; OECD decomposition 2025
(804 households × 4 lines) 3 200 exact, 3 216 within 1 %; 8 VID wage-tax examples (13 values) and 2 VID deduction examples exact.
