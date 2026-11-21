# Slovakia (SK), 2025: what this work is useful for

Each item names its evidence (FINDINGS.md, Lean theorem, run). Amounts in euros, tax year 2025.

## Taxpayer
1. **Let the lower-earning parent claim the daňový bonus.** The 2025 withdrawal (1/10 of the base above 25 740 € per child)
   is computed on the claimant's own base; a couple with 60 000 € and 12 000 € of wages and two children gets 2 400 € via
   the lower earner and 0 € via the higher one (F5, `Findings.f5_claimant`).
2. **Expect to repay monthly bonus in the annual settlement** if your annual base ends above 25 740 €: from 2025 the excess
   paid by the employer must be returned (Finančná správa 272586, "UPOZORNENIE" and príklad 8: 61 €).
3. **Families with children face 51–55 % marginal rates between about 29 700 € and 43 600 € of gross wages** (two
   children; 10 % more per extra child); moving income across years out of that band saves up to 2 384 € over two years
   (F6, F7; `results/search/metr.md`, `timing.md`).
4. **SZČO thresholds are cliffs:** 1 € of receipts above 8 580 € brings 2 844 € of social contributions (from 1 July of the
   next year), and above 100 000 € the whole business base moves from 15 % to 19 % (2 555 € at a 54 600 € base) (F8, F9).

## Adviser
1. **Owner-managers:** at 50 000 € of profit, dividends leave 81–83 % with the owner and salary 53 % (CIT 10 %, 7 %
   withholding, no contributions on dividends from taxed profits) (F10, `results/owner_sk.md`). Dividends paid out of
   2024 profits are still taxed at 10 % (§ 52zzzb ods. 5).
2. **A small salary beats the self-payer health minimum** (1 201,20 € a year) for an owner without other insured activity
   (F14, lead: confirm with the health insurer).
3. **Two bases, two 19 % bands:** employment income and business income above 100 000 € of receipts each get their own
   48 441,43 € threshold, worth up to 2 906,49 € a year against the same income in one base (F11,
   `Theorems.two_bases_le_one`).
4. **2025 returns:** pooling the other parent's base (§ 33 ods. 8) no longer escapes the withdrawal; the amendment of
   15. 3. 2025 applies to the whole year (§ 52zzzd) (F3).
5. Every Finančná správa 2025 bonus example (18) and the OECD's eight 2025 households (56 lines) are reproduced by the
   model: it can be used to check a client's figures (`lean/SkTax/Tests.lean`, `results/oecd_check_SK.md`).

## Government (Ministerstvo financií SR, Finančná správa)
1. **The bonus withdrawal misses its target:** it is avoided by any couple whose lower earner has a base of 4 138–25 740 €
   (F5), and it stacks with the § 11 withdrawal to push marginal rates of one-earner families above 50 % (and above 100 %
   with eight children) (F6). A household-level test, or a smaller rate per child, would fix both.
2. **Repeal § 32a (zamestnanecká prémia):** it cannot be positive for any income while the minimum wage is ≥ 554 € (it is
   816 €) (F12, `Theorems.premia_dead`).
3. **Tidy the bonus transitional law:** § 52zzp ods. 6 still schedules the 2023 text of § 33 ods. 1 (50 € for every child
   over 15, students included) for January 2025, in conflict with § 52zzzb ods. 6, and § 33 ods. 1 still points to the
   expired § 52zzp ods. 3–5 (F4).
4. **Replace the notches with glides:** the 100 000 € revenue test (15 % PIT, 10 % CIT) and the 8 580 € social-insurance
   test make one euro cost 2 555–9 974 € and 2 600 € (F8, F9).
5. **Write the proration in § 33 ods. 11** that Finančná správa applies to part-year children (426 × 2/12) (F13).
