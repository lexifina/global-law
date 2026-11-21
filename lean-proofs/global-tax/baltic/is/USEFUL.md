# Iceland 2025: what this work is useful for

Evidence: `FINDINGS.md` (F-numbers), `CATALOGUE.md` (K-numbers), theorems in `lean/IsTax/Theorems.lean`, scan tables in
`results/is_scans/is_scans.md` and `owner_is.md`.

## For a taxpayer
1. **Watch the 2.617.618 kr. line.** If your taxable income (after the 4 % pension) is between 2.617.618 and about
   2.671.000 kr., the two flat levies (22.200 + 14.614 kr., charged at the 2026 assessment) leave you poorer than if
   you had earned less. A 10.000 kr. gift to a registered charity or a small séreign contribution that takes you below
   the line saves 36.814 kr. plus tax (F3, `levies_cliff_2025`). Students with summer jobs and pensioners under 70 are
   the usual cases.
2. **Living in Reykjavík you owe a little at assessment.** Withholding uses the 14,94 % average útsvar; Reykjavík's is
   14,97 %: 0,03 % of taxable income, about 3.600 kr. at an average wage (F6).
3. **Couples: the second credit is fully usable, and in 2025 part of the top band too.** A one-earner couple saves
   824.288 kr. through the credit transfer and up to 424.855 kr. through the band transfer; cohabitants only get this
   if both ask for joint taxation (62. gr.); it never costs (`pair_le_separate`, `transfer_never_costs`; F11, K4-K6).
   Both band sharing and the 22/31 credit end with income year 2026.
4. **Families with young children face up to 54 % marginal rates** in the barnabætur withdrawal band: 4 % for all
   children plus 4 % for each child under 7, on top of the bands (F4). Barnabætur below 5.000 kr. per parent are not
   paid even if RSK's calculator shows them (F8).
5. **Retirees living on savings paid no tax on almost 3 M kr. of capital income in 2025** (5,9 M kr. for a couple)
   because 22/31 of the unused credit paid the capital income tax; this ends for 2026 (F10).

## For an adviser
1. **Owner-managers: salary to 5.900.065 kr., dividends above** (37,6 % on distributed profit vs up to 52,7 % on top
   salary). RSK's reiknað endurgjald minima bind first: with B(5) 10.392.000 kr. the saving at 2 AW of profit is still
   915.003 kr. (F16, `dividend_route_rate`). The dividend gets no 300.000 kr. exemption (unlisted).
2. **Timing income around barnabætur**: bunching a bonus or self-employed profit into one year saved a single parent
   up to 481.655 kr. over two years (F17).
3. **The second earner in a high-income couple pays 4,15 points more** on middle-band income in 2025 (each 2 kr. of
   her income removes 1 kr. of the partner's band transfer; F11, `shift_secondary`). From 2026 the transfer is gone.
4. **Separated parents with a registered shared residence** each receive half of a single parent's barnabætur:
   339.000-566.040 kr. a year more than a couple with the same incomes and two children (F12). Advice must stress
   that parents living together are a couple for barnabætur whether or not they register.
5. **Residential rent at 11 % in 2025 (16,5 % from 2026)** and listed-share income up to 300.000 kr. tax-free remain
   the cheapest forms of income (K7, K8).

## For the government
1. **Fix two stale cross-references**: lög 4/1995 23. gr. cites a children's minimum in "2. mgr. 67. gr." of lög
   90/2003 that is in 66. gr. 2. mgr. (F1); 67. gr. A still tests the credit against "1. tölul. 1. mgr. 66. gr.", the
   first band only since 2009 (harmless today, `firstBandTax_gt_credit`; F2).
2. **The levy floor is a cliff**: 36.814 kr. due in full from one króna (F3). A glide zone (like the kernel's
   `Surcharge.glide`) or a percentage would remove the 53.759 kr. band where earning more lowers net income.
3. **Barnabætur need an index rule**: the 2025 amounts and thresholds were frozen by changing a year in a temporary
   provision while tax bands rose 5,80 %, costing families 19.854-27.116 kr. (F15); the per-child withdrawal of the
   under-7 supplement stacks to 54 % marginal rates (F4); the shared-residence rule pays parents living apart up to
   566.040 kr. more than a couple (F12).
4. **Correct published figures**: the ministry's 2025 barnabætur table ("4 % með hverju barni", F13), RSK's
   barnabætur calculator (amounts under 5.000 kr., F8), Skatturinn's 2026 credit total 869.904 vs 869.898 and the
   2025 band left in the 2026 example, the 150.000 kr. exemption still stated as current (F14); publish the indexed
   band-transfer cap the statute asks for (F7).
5. **The OECD's ISL 2025 row uses the levies of income year 2024** (21.400 / 14.093 instead of 22.200 / 14.614, F5);
   worth telling the OECD so its series stays consistent.
