# Norway 2025: what this work is useful for

Evidence: `FINDINGS.md` (F-numbers), `CATALOGUE.md` (K-numbers), theorems in `lean/NOTax/Theorems.lean`.

## For a taxpayer
1. **Your withholding is set to over-collect by about 2 430 NOK a year** if you earn more than 200 000 on an
   ordinary table: the tables deduct only 88 % of the minstefradrag (F1; `table_minst_gap`). The refund in June is
   that money coming back, not a mistake in your favour.
2. **Sole traders earning 108 550-176 684 NOK keep only 53 øre of each extra krone** (47 % marginal rate, F10,
   `soleTrader_band`): higher than at 700 000. An employee at the same pay faces 25 % up to 144 003 and 7.5 % above it.
3. **Couples: the 22 % is flat, so who owns savings matters only when one spouse earns little**: deposits in the
   name of a spouse with no income save up to 23 883 NOK a year (F12, `capital_shift_neutral`); give charitable
   gifts from one spouse (each gift deduction needs 500 NOK per giver, F18); put the foreldrefradrag on the spouse
   who pays tax (F14).
4. **A single parent who moves in with a partner loses 30 192 NOK a year of utvidet barnetrygd** (F16).
5. **Pensioners under 67 outside the pension credit can face 55 %** on pension between about 230 600 and
   318 000 (F4, sktl. § 17-1), above the 47.8 % Skatteetaten publishes as the maximum for pensions.

## For an adviser
1. **Owner-managers: wages to 942 400 (trinn 4), dividends above** is the cash optimum in 2025 (F11; theorems
   `wage_route_trinn3`, `wage_route_trinn4`): 50.4 % against 51.5 % below the threshold, 53.0-53.9 % above it.
   Pension and sickness rights (not modelled) push towards wages.
2. **The model reproduces the OECD's 2025 Norwegian rows within rounding (48/48 lines, max 6.3 NOK) and
   Skatteetaten's published withholding tables row for row (909 996 rows)**: it can be used as a checked
   calculator for wages, pensions, business and capital income (validation table in FINDINGS).
3. **Statute traps worth knowing**: § 10-12 (1) cites a § 10-11 paragraph that exempts nothing since 2015 (F5);
   § 17-1 (6) and § 16-21 forget the § 5-22 oppjustering (F6); the 2025 low-income limits were raised only in
   December 2025 (F9).

## For the Norwegian government
1. **Fix the cross-references**: § 10-12 (1) "§ 10-11 syvende ledd" (F5), § 17-1 (6) and § 16-21 lists missing
   § 5-22 (F6), the særfradrag ranges in §§ 6-3 and 6-90 (F7). Each is a one-line amendment; evidence: the
   amending laws' own renumbering clauses (Lov 18. des 2015 nr. 115 III, Lov 21. des 2020 nr. 164).
2. **Publish the reason for the 88 % minstefradrag in the tables, and complete the open withholding code** (F1, F2;
   draft issue `drafts/ISSUE_trekktabell_2025.md`): 36 published tables are not in the 2025 code.
3. **Correct the maximum-marginal-rate page**: 11.1 % should read 10.9 % (F3), and the § 17-1 55 % band belongs
   next to the pension credit's 47.8 % (F4).
4. **The sole-trader phase-in overlap (F10)** is a design side effect: the trygdeavgift phase-in was built for
   employees, whose minstefradrag keeps them out of the 22 % tax while it runs; sole traders get no minstefradrag.
