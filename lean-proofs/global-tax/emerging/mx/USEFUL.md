# Mexico 2025: what this work is useful for

Evidence: FINDINGS.md (F-numbers), CATALOGUE.md (K-numbers), Lean theorems in `lean/MxTax/Theorems.lean`.

## For a taxpayer
1. **Earning just above 10,171 a month (1.2 minimum wages) can leave you with less.** The subsidio para el empleo
   (474.65 a month) stops entirely one centavo above 10,171.00 of taxable pay; a raise to anything below 10,703.59
   a month leaves you worse off after ISR (F6, `subsidy_cliff`, `subsidy_dead_zone_month`). Over a year: 128,390
   of pay nets 5,213 less than 128,380 (F7).
2. **Your aguinaldo can cost you December’s subsidy.** From about 112,750 a year (100,000 with a 30-day aguinaldo)
   the taxable aguinaldo pushes December over the cut-off (F8). Asking for part of it in November avoids that.
3. **At the minimum wage your employer pays your IMSS quotas; one peso more and you pay all of them** (about 2,417 a
   year, LSS art. 36; F9).
4. **Self-employed? RESICO taxes revenue at 1-2.5 %**, far below the general regime (e.g. 600,000 of fees: 6,600 vs
   113,604; K3). Watch its edges: 300,000.01 of revenue costs 300 more than 300,000.00 (F10), and above 3,818,181.81
   earned evenly a month of profit falls into the general regime (F11).
5. Deductions are capped (min of 5 UMA = 206,367.60 or 15 % of income; retirement contributions separately up to 10 %
   / 206,367.60) and investment income is taxed to its legal owner, so ownership between spouses matters (F15, K8, K9).

## For an adviser
1. The OECD’s Mexican household numbers are reproducible to the centavo once you know its assumptions: aguinaldo
   15 days and prima vacacional 25 % of 12 days inside the AW, a day = W/365, cesantía y vejez left out of SSC, and
   the annual 2025 UMA for the whole year (F1-F3).
2. Paying part of salary as exempt previsión social still works within art. 93’s 7-UMA rule: 20 % of a 200,000 wage
   saves 7,476 (K1); asimilados save the IMSS quotas but lose the subsidy and the exempt aguinaldo (K4).
3. For an owner-manager the own-company route (30 % CIT + 10 % dividend tax, credit not refunded) costs more than the
   general regime at every profit level if profits are paid out (K6); RESICO is the cheapest legal route up to
   3.5 M of revenue, but socios and related parties are excluded (art. 113-E fr. I).
4. Timing pays around the subsidy cliff: bunching two years’ pay gains up to 7,112 (F16).
5. Leaving RESICO mid-year keeps earlier months definitive only if the previous year was also RESICO (RMF 3.13.5
   fr. I); the art. 113-F annual table has no rate for a year that crosses 3.5 M only in December (F11).

## For the Mexican government (SHCP / SAT / Congress)
1. **Replace the subsidy cut-off by a phase-out.** ~6.1 million beneficiaries (SHCP DRR 2025) sit below a cliff
   where 10 pesos more annual pay costs 5,213 and the dead zone is 5 % of pay (F6, F7); December’s aguinaldo trips
   it early (F8).
2. **Finish the salario mínimo -> UMA conversion in the LISR.** DOF 12-11-2021 converted art. 151’s overall cap but
   not fr. V, I, II of the same article, nor art. 93 or 96 (which still cite geographic areas and the Distrito
   Federal); LSS art. 106 still prints a 2 % quota cut to 0.40 % in 2007 (F5).
3. **Give art. 113-F a rate for revenue above 3.5 M** in the year of exit, and consider smoothing the month-count
   notches of the in-year exit (F11); consider an IMSS phase-in above the minimum wage (F9).
4. **Say whether the minimum wage is taxed**: art. 96 forbids withholding but the annual calculation gives 1,110
   for a 2025 minimum-wage worker (F13).
5. Index or review the nominal 400,000 / 3,500,000 / 10,171 thresholds alongside the tarifas (updated 2023 and 2026),
   and derive each cuota fija from the row below so the tarifa cannot fall when income rises (F4, F14).
