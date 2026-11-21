# CH Switzerland 2025: what is most useful to know

## For a taxpayer
1. **Without a pension fund, pay either nothing or at least about 1 400 (single) / 2 800 (couple) into Säule 3a.**
   Any 3a payment removes the half-again insurance deduction (900 federal + 1 450 Zürich single); one franc paid in
   costs 236 francs of tax at 60 000, 498 for a one-earner couple at 90 000. Evidence: FINDINGS F8, Lean
   `p3a_one_franc_costs`.
2. **Two earners pay more federal tax married than unmarried at most incomes**: +71 % at 2 × 100 000 (+2 496), +135 %
   with two children at 2 × 75 000; one-earner couples gain from marriage. The Zürich layer is milder. Evidence: F12,
   results/marriage.md (penalty > 10 % at about two thirds of two-earner grid points).
3. **Pension buy-ins pay**: a buy-in deducted at the marginal rate and withdrawn as capital at least three years later
   (BVG Art. 79b Abs. 3) keeps 18-25 % of the buy-in; staggering a 600 000 withdrawal over two years saves 12 785.
   Evidence: F14.

## For an adviser
4. **Owner-managers in Zürich keep 6-9 % more of the profit as qualifying dividends than as salary** (no AHV, 70 % /
   50 % taxation), within the limits of the AHV practice on excessive dividends. A generic scan that treats the
   dividend as a portfolio dividend gets the opposite answer. Evidence: F13, results/owner.md.
5. **Family allowances have no income test for employees**: a family with large capital income gets the full
   allowances (5 160 a year for two young children) once one spouse earns 7 560. Evidence: F10, Lean `famzg_notch`.

## For the government (and the OECD)
6. **All-or-nothing conditions create notches**: the insurance-deduction increase (DBG Art. 33 Abs. 1bis lit. a, StG ZH
   § 31 lit. g) turns the BVG threshold into a +84.63 notch and small 3a payments into a loss; tapering it, or
   writing "ohne Beiträge an die berufliche Vorsorge und die Säule 3a" and a minimum, would fix both and the
   literal-reading problem of lit. d (F7, F9). The two-earner deduction's "mindestens 8600" needs "höchstens das
   Erwerbseinkommen" (F11). FamZG Art. 13 Abs. 3 vs Art. 19 Abs. 2 gives a 5 160 notch (F10).
7. **Published numbers**: the ESTV calculator omits taxable family allowances (understates a family's tax by about
   970 at the average wage, F6); the OECD's 2025 chapter prints a federal tariff mixing 2023 and 2024 values (F4),
   uses 268 per child where Zürich pays 215 under age 12 (F3) and a 7.83 % pension-fund convention (F5). The model
   reproduces the ESTV calculator on 1 494 of 1 494 lines (166 households) and the OECD on 55 of 56 lines with its
   conventions.
