# Transfer (estate, gift, GST): findings

File: `LegalProofs/USTax/Hunt/Transfer.lean`. Outputs: `tools/hunt/out/Transfer/*.txt`.
Run: `lake env lean LegalProofs/USTax/Hunt/Transfer.lean` (scenario A, 49 s). Other scenarios:
`lake env lean --run LegalProofs/USTax/Hunt/Transfer.lean <short|Wfirst|Cfirst|farm|late|qtip|nomarry|notrusts|checks>`.

## Bottom line

One item I could not find written up (CANDIDATE, below): a surviving spouse who has remarried gives up her income
interest in the first spouse's QTIP trust (§2519) with the new spouse consenting to split gifts (§2513), so the new
spouse's exclusion and GST exemption shelter half of the first spouse's trust. Everything else the search returned
is a known technique, some re-priced under the 2025 Act's $15M exclusion. The candidate came out of a model
artifact (the search had the new spouse allocate GST exemption to the dead spouse's trust, which §2631(a) forbids);
after that was closed and §2519 was encoded with §2513, the search still returned it as the best plan in the QTIP
scenario.

## Family, objective, figures

- H owns $100M ($20M cash, $80M zero-basis appreciation); W and child C own nothing; two grandchildren.
- Objective: what the grandchildren hold at the end, after the 23.8% income tax built into it. This counts
  transfer tax, income tax on property sold to pay it, lost §1014 step-up, and the time value of paying early.
- 7% growth, 5-year periods. Scenario A: H dies year 5, W year 10, C year 25.
- 2026 figures: basic exclusion and GST exemption $15,000,000 (§2010(c)(3) as amended by Pub. L. 119-21), indexed
  at an assumed 2.5%; annual exclusion $19,000. §7520 rate assumed 5.0%. §2032A limit $1,420,000 is the 2025 figure.
- Simple will (all to spouse, then child, then grandchildren; no elections): **$216.71M**, transfer tax $200.12M
  nominal over the 25 years.

## Provisions encoded (each read in the local OLRC text)

§2001(b), (c); §2010(c)(2)–(5); §2502, §2505; §2503(b), (e); §2513; §2515; §2518 (as equivalence of bequest
choices); §2519, §2207A; §2523(a), (f); §2056(a), (b)(7); §2044; §2035(b); §2013; §2702(a)(2)(B), (b)(1) with
§7520; §2631, §2632(a), (b), (c), (e); §2641, §2642(a), (b)(3), (c), (d), (f); §2611(b)(1), §2612, §2613,
§2651(e), §2652(a)(1)–(3), §2603, §2621–2623, §2654(a)(2), (b)(1); §529(c)(2), (c)(4); §1014(a), (b)(1), (b)(9),
(b)(10), (e); §1015(a); §2032A(a) with §1014(a)(3).

Read but not modelled: §§2036–2038 (the only retained-interest vehicle is the GRAT, which the model lets end before
any death; a GRAT in the last year is not offered), §2053–2055, §6166 and §6601(j) (pure deferral at 2%; no
interaction found), §1014(f), §2041/§2514, §2040, §529(c)(5), §530A.

## Search size

Scenario A: 161,945 positions examined over 11 phases, 232 distinct end plans. Exhaustive to depth 2 in the first
planning phase and in each estate; elsewhere one move exhaustive plus two beam rounds. Beam: 350 positions kept per
phase, stratified by number of kinds of large move, scored by playing out with no further move. Consent to split
and remarriage are tried free in front of every move. Nine scenarios in all, roughly 1.1M positions.

**Limits of the search.** It is a beam, not exhaustive, beyond depth 2; a plan needing three unrewarded moves in
a row can be missed (the remarriage plans were missed until the two enabling moves were made free).

## Plans (scenario A unless stated; dollars are year-25, grandchildren's after-tax wealth vs the simple will)

| Plan (moves) | vs simple will | Provisions combined | Class | What could defeat it |
|---|---|---|---|---|
| W, widowed with H's property in a QTIP, marries again; both consent; W gives up the income interest. Scenario `qtip`: best plan $283.50M against $250.67M for the best plan without remarriage. Direct check: $256.57M against $226.13M for the same release unmarried | +$30M to +$33M per new spouse on a $100M trust | §2519, §2513(a), §2652(a)(2), §2632(c), §2207A(b) | **CANDIDATE** | See the next section |
| H's will: $15M to grandchildren, rest to W; W marries again, both consent, W gives $80M to a family trust and $18M to the child, paying gift tax; child regifts within his own exclusion. Best plan overall, $327.66M | +$110.94M; remarriage is worth $19.96M of that (best plan without it: $307.70M) | §2513, §2652(a)(2), §2056, §2502, §2035(b) | **VARIANT** (gift-splitting with a spouse who has no estate, done with a later spouse) | Same as the candidate except the §2519 points |
| Best plan without remarriage (`nomarry`): split gifts, $30M to grandchildren, $36M to child with gift tax paid, GRAT, remainder to W | +$93.47M | §2513, §2632(b), §2502, §2702 | KNOWN: tax-exclusive lifetime gifts, GST-exempt gifts, GRAT | Death within 3 years (§2035(b)); loses §1014 step-up ($63M built-in gain remains) |
| Gift to family trust, deemed GST allocation, alone | +$78.15M | §2632(c), §2642 | KNOWN: dynasty trust | — |
| Gift to grandchildren up to exclusion and exemption, alone | +$61.18M | §2632(b), §2642(c) | KNOWN | — |
| Zeroed-out GRAT, remainder to trust / to child | +$43.89M / +$26.24M | §2702(b)(1), §7520, §2642(f), §2632(c)(4) | KNOWN | §2036 if grantor dies in term; exemption needed at the end-of-term value |
| Will: exemption amount to grandchildren or trust | +$43.01M | §2010, §2631, §2632(e) | KNOWN: credit-shelter/GST bequest | — |
| Child gives to grandchildren during life (in every top plan) | +$11.77M alone | §2502 vs §2001 | KNOWN: gift tax is tax-exclusive | §2035(b) |
| QTIP by will / lifetime QTIP / with reverse election | +$16.00M / +$15.88M / +$16.53M | §2056(b)(7), §2523(f), §2652(a)(3), §2044, §1014(b)(10) | KNOWN | See traps: reverse election |
| Portability alone | +$14.33M | §2010(c)(4)–(5) | KNOWN | DSUE not indexed; no GST portability |
| `Wfirst`: W dying; H puts $15M in a lifetime QTIP for her in her last year, remainder to family trust | part of the $320.73M best plan | §2523(f), §2044, §1014(b)(10), §1014(e) | KNOWN: funding the poorer spouse's exclusion; §1014(e) does not reach property that does not return to the donor | A QTIP that benefits the donor afterwards invites §1014(e)(2)(B) |
| Trust distributes to child, who regifts within his exclusion | in top plans, +$0.4M alone | §2612(b), §2502 | KNOWN: moving non-exempt trust property into the child's transfer-tax base | Trustee discretion, fiduciary duty |
| Tuition paid directly; trust pays tuition; 529 with five-year election | +$1.46M; +$0.66M (by itself, at the start) | §2503(e), §2611(b)(1), §529(c)(2)(B), §2642(c) | KNOWN | — |
| `Cfirst`: after the child's death, W gives $104M outright to grandchildren with no GST tax | best plan +$39.16M | §2651(e) | KNOWN: predeceased-parent rule | — |
| `short` (child dies 5 years after W): GRATs and exemption gifts win, large taxable gifts do not | +$46.13M | §2013 | KNOWN: the §2013 credit makes two estate taxes in 5 years cheap | — |
| `farm`: §2032A election | +$1.17M by itself; absent from the best plan (best plan using it is $0.34M behind) | §2032A(a), §1014(a)(3) | KNOWN, and marginal here | See traps |

## The CANDIDATE, attacked

Text: §2519(a) treats the disposition as "a transfer of all interests in such property other than the qualifying
income interest" for chapter 12. §2513(a)(1) covers "a gift made by one spouse to any person other than his
spouse" and tests marriage "at the time of the gift". §2652(a)(2) carries the split into chapter 13. Nothing in
the three ties the consenting spouse to the spouse who created the QTIP.

Not a model artifact as far as the text goes. What could defeat or shrink it:

1. **Is a §2519 deemed transfer "a gift made by" W for §2513?** No authority found either way. The IRS could say
   the remainder was never hers to give. Reg. §25.2519-1(a) calls it a transfer by gift by the spouse, which helps.
2. **§2652(a)(3).** If H's estate made the reverse QTIP election, H stays transferor for GST; the new spouse's
   exemption cannot reach the trust. Only the gift-tax half survives.
3. **§2207A(b)** gives a right of recovery to the person "treated as transferred by such person under section
   2519". The new spouse is treated as transferor by §2513, not §2519: his half of the tax may have no statutory
   recovery right, and not recovering could be a further gift.
4. **W gives up the income for life.** Real cost, not priced by the model.
5. **Trust terms and state law.** Most QTIP trusts bar assignment; a court-approved termination raises the
   *McDougall* (163 T.C. No. 5, 2024) and *Anenberg* questions about who makes a gift to whom.
6. **The new spouse** uses up his own exclusion and exemption and is jointly liable for the year's gift tax
   (§2513(d)); the consent covers all gifts that year; he must not have an interest in the property.
7. **A marriage entered for this** risks being disregarded as a sham; §7701(o) does not obviously apply to a
   marriage. §2513(a)(1) already blocks more than one consenting spouse per calendar year.
8. Not modelled: a new spouse every year. The text has no lifetime cap on consenting spouses.

Sources checked (3 searches, standard mode): no result on §2519 with §2513 after remarriage. Found only the
general rules: Reg. §26.2652-1 (split gift, each spouse transferor of half); Bessemer Trust summaries of *Kite II*,
*Anenberg* and *McDougall*; Greenleaf Trust and Florida Bar Journal pieces on §2513; PLR 201811002 and related.
Three searches is thin; a treatise check (Bloomberg portfolio 843, Stephens Maxfield) is still owed.

## Traps found

- **Reverse QTIP election when the child dies between the spouses.** §2651(e) fixes generation "at the earliest
  such time" the transfer was taxed to the transferor; with the §2652(a)(3) election that is H's death. Check 5:
  $111.43M with the election, $173.36M without. The election costs $61.93M in that order of deaths.
- **Direct skip in the last year of life.** §2035(b) reaches only chapter 12 tax, so the GST tax on a deathbed
  direct skip leaves the estate. With appreciated property the lost §1014 step-up and the sale to pay tax outweigh
  it: check 3, $244.01M for the gift against $251.98M for the same outlay by will.
- **§529 five-year election in the last year:** §529(c)(4)(C) pulls back four-fifths. $217.18M against $217.37M
  when funded at the start. Tuition paid directly ($218.17M) beats both.
- **§2032A lowers basis** (§1014(a)(3)): 40% saved on at most $1.42M against 23.8% lost, before recapture risk.
- **No portability election on the death of a later spouse** wipes out the first spouse's DSUE: §2010(c)(4)
  speaks of the *last* deceased spouse.
- **§2632(c) deemed allocation** spends exemption on any trust gift unless elected out; electing out cost $22M
  on the single-move trust gift (+$55.77M against +$78.15M).

## Drafting gaps noticed (not modelled)

- **§2010(c)(4)(B)(ii)** subtracts the deceased spouse's adjusted taxable gifts even where gift tax was paid on
  them; only the regulations repair this.
- **DSUE stacking** across successive spouses exists only in the regulations. On the statute alone, §2505(a)(1)
  and §2001(b) give one last-deceased-spouse amount.
- **§529(c)(5)(B)** taxes a change to a lower-generation beneficiary without saying who the transferor is. A change
  to a same-generation family member is untaxed, so accounts for several cousins can be consolidated (IRS flagged
  this in its 2008 advance notice; no final rule).
- **§530A (Trump accounts, 2025 Act)** has no gift or GST rule, unlike §529(c)(2) and §530(d)(3). Whether a
  contribution is a present interest is left to §2503(b) and (c).
- **§2035(b)** says "tax paid … by the decedent": tax paid by a consenting spouse on a split gift is outside it.
- **§2611(b)(1)** has no dollar or relationship limit for tuition and medical payments out of a non-exempt trust.

## Model limits that affect the numbers

- Fixed lives, known in advance; one growth rate; the GRAT never fails.
- Lump gifts get no annual exclusion; no withdrawal-power trusts; no valuation discounts; no grantor-trust income
  tax effects (done in `USTax/Trusts`); no charity; no state tax.
- The later spouse is costless and has no estate of his own.
- Scenario labels after remarriage print the new spouse as "H" and his half of a trust as "trust(H)".
