# Poland (PL) 2025: what is useful

Evidence: FINDINGS.md (F-numbers), Lean names in `lean/PlTax/Findings.lean` and `Theorems.lean`.

## For a taxpayer
1. **One child and income near 112 000 zł (couple or single parent) or 56 000 zł (other unmarried parent): one złoty
   over the limit costs the whole 1 112 zł relief.** The limit counts the year's scale, liniowy and share-gain income
   less social contributions (art. 27f ust. 2a). Between 133 272 and 134 903 zł of salary you are worse off than at
   133 271 zł (F3, `oneChild_band`). Ask for a December bonus to be paid in January.
2. **Married with a low- or non-earning spouse: file jointly.** It never costs more (`joint_le_separate`, all incomes)
   and saves up to 27 600 zł (`joint_gain_max`). But if either of you runs a business on liniowy or ryczałt, neither can
   file jointly (art. 6 ust. 8): a 40 000 zł side business moved to liniowy cost a 300 000 zł earner’s family 24 449 zł
   (F5).
3. **Low pay with children: the child relief pays back your contributions.** A single parent of three earning up to
   about 19 600 zł gets every złoty of social and health contributions back in the return (F9); claim the payout in
   part J of PIT-37.
4. **Under 26 on more than 85 528 zł: expect a refund.** Your employer withholds up to about 2 600 zł more than you owe
   because the monthly 300 zł reduction is lost in the exempt months; with the 30 000 zł tax-free amount you owe no PIT
   up to a salary of about 120 000 zł (F8, `young_120k_no_tax`).
5. **Pay above about 260 000 zł in one year stops pension contributions**; if you can choose the year of a large bonus,
   one year above the ceiling and one below beats two years just under it by up to 7 020 zł (F16).

## For an adviser
1. **Regime choice for a sole trader (no costs, standard ZUS)**: scale to about 145 000 zł, then ryczałt (12 % from
   150 000; 8,5 % from 125 000) or, where ryczałt is unavailable or costs are high, liniowy from 175 000 zł (F14). Count
   health: 9 % non-deductible on the scale, 4,9 % deductible up to 12 900 zł on liniowy, flat bands on ryczałt.
2. **Ryczałt health bands are notches on revenue after social contributions**: just over 60 000 zł (≈ 79 758 zł gross
   revenue with standard ZUS) costs 3 472 zł net; just over 300 000 zł costs 6 942 zł (F4). Watch December invoices.
3. **B2B vs employment**: at the same amount, ryczałt 12 % nets 18 022 zł more at 200 000 zł and 106 414 zł more at
   500 000 zł; below about 150 000 zł the fixed ZUS (21 287 zł with Fundusz Pracy) makes B2B worse (F7). The art. 5b
   test and PIP reclassification remain the risk.
4. **A client on ryczałt keeps the one-child relief whatever the revenue** if the spouse’s scale income is under the
   limit (art. 27f ust. 2a does not count ryczałt, F10). Liniowy does not have this.
5. **Rent between spouses**: keep the default split (art. 12 ust. 6): two 100 000 zł bands at 8,5 % save 4 % of the rent
   above 100 000 zł (F15).

## For the Polish government (Ministerstwo Finansów)
1. **Index or taper the one-child limits (112 000 / 56 000 zł, unchanged since 2013, Dz.U. 2012 poz. 1278).** They are
   now 1,06 average wages for a couple, and the cliff gives a 1 632 zł band with an effective marginal rate above 100 %
   (F3, F12). A taper (e.g. withdraw the 1 112 zł over the next 5 000 zł) removes the notch at no cost to families
   below the limit.
2. **Count ryczałt revenue (or income) in art. 27f ust. 2a**: the list (art. 27, 30b, 30c) was not updated when ryczałt
   was opened to most professions, so a 300 000 zł ryczałt earner’s family keeps a relief denied to a 113 000 zł
   employee family (F10).
3. **Turn the ryczałt health bands into a continuous schedule** (e.g. 9 % of revenue above 60 000 zł, capped): the
   present steps (3 694 and 7 386 zł) create bands of 3 946 and 7 889 zł of revenue in which earning more lowers net
   income (F4).
4. **Withholding for the under-26 (art. 32)**: let the payer apply the unused monthly 300 zł reductions once pay becomes
   taxable, as the annual return does; today up to 2 641 zł per young employee is over-withheld (F8). The 85 528 zł
   limit is a deliberate figure (same act as the 120 000 zł threshold, F11) but has not been indexed since 2019.
5. **The 30× ceiling makes contributions regressive** (combined rate 49,1-49,8 % from 142 534 to 260 326 zł, then 42,3 %
   above) and rewards bunching pay into one year (F16). All 2025 figures published by MF/MRPiPS/GUS/ZUS that the model
   uses re-derive exactly from their statutory formulas (F13).
