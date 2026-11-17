# French income tax in Lean vs Mlang — results (17 November 2026)

Lean model `lean/` (FrTax): income 2020 to 2025, written from the CGI as it applied to each year; Mlang (DGFiP M code,
C backend `cal2020` … `cal2025`) used as an oracle and as a competitor. Harness `harness/`. Run outputs `~/fr/runs` on
the build server. Findings F1–F7, the production verdicts (P) and the Lean corrections (L) are in `FINDINGS.md`.

## Benchmarks where both reach 100 %

| # | Benchmark | Decides | Lean | Mlang | OpenFisca-France |
|---|---|---|---|---|---|
| 1 | DGFiP test suites (Mlang `tests/2024` 2,809; `tests/2025` 3,091) | DGFiP reference program | n/a (tests set internal M variables) | 2,809/2,809; 3,091/3,091 | — |
| 2 | Brochure pratique scale tables, income 2020–2025 (20,489 printed cells; 2020–2023 from archived editions) | DGFiP printed table | 20,489/20,489 (`tableTax`); 13,722/13,722 household cells | 13,722/13,722 household cells | — |
| 3 | Brochure thresholds: Tableaux 4, 6, 7 (income 2024, 2025) | statute | equals printed: T4 27/84, T6 40/40, T7 11/40 (each cell a theorem) | equals Lean | — |
| 4 | Brochure worked examples (18 answers) | DGFiP | 18/18 | 18/18 | — |
| 5 | Official worked examples (parliamentary reports, BOFiP, brochure, service-public; 84 collected, 48 mappable to boxes) | the publisher | 43/47 stated figures (the 4 others: a patent-income box the example's facts do not map) | 44/57 (the 13 others: box guesses for expatriate and compensatory-allowance examples) | — |
| 6 | Statutory edges: 132 returns at each threshold and ±1 € | statute | 132/132 = M | 132/132 = Lean | 94–96 % (157 bis edges off by one) |
| 7 | Random households, 2024–2025: 98,868 accepted by M | each other | 98,849/98,868 identical on 12 figures (the 19 others: F2) | — | 3,677/5,000 (2024), 3,556/5,000 (2025) on 5 figures |
| 8 | Random households, 2020–2023: 19,748 accepted by M | each other | 19,741/19,748 (the 7 others: F6, where production sides with Lean) | — | — |
| 9 | Proofs | — | scale and décote monotone; indexation; cliffs; brochure counterexamples (kernel-checked) | — | — |

## Benchmarks that separate them

| # | Benchmark | Lean | Mlang | OpenFisca |
|---|---|---|---|---|
| 10 | **Production simulator, random households 2024–2025** (700) | 699/700 every figure (1: reported droits simples under art. 197 C) | 691/691 computed; refuses 9 that production computes | — |
| 11 | **Production simulator, targeted returns 2020–2025** (371: every disagreement family, M refusals, edges, rounding margin, random 2020–2023) | 301/353 every figure; the 52 others are deliberate statute readings: F5 rounding 24, F2 CEHR 22, F1 union credit 3, deficit not reported 3 | 285/292 computed (the 7: F6); refuses 61 that production computes | 51/222 exact; 200/222 within 2 € on net tax |
| 12 | **Production simulator, family structures** (126: half-part boxes, invalid combinations) | 39/39 computed by production | 30/30; refuses 9 production computes; computes 60 that production refuses (2020–2021 driver runs no input controls) | 5/12 (T for a widow(er): 1,592–1,759 € too little tax) |
| 13 | **Family-structure stress, Lean vs M** (30,000 generated; 20,159 accepted by M) | 91.3 % equal before corrections, 95.0 % after three statute fixes; the rest are returns production refuses | — | — |
| 14 | OpenFisca calculator tests (expected values read off the DGFiP calculator, 2019–2024) | 8/8 in scope | 40/41; the 1 (2019 forestry credit 5,864 vs stated 5,857) is production's value, so the test is wrong | its own suite |
| 15 | Speed (one core) | 14 µs / household | 0.32 ms compute (1.1 ms with I/O) | 0.6 ms (vectorised) |
| 16 | **OpenFisca-France test suite, income 2020–2025** (155 returns from 126 tests; OFSUITE.md) | 126/131 with a figure (21 out of scope; = M on every figure) | 148/155, refuses 1 (DD27) | 155/155 (its own suite); production finds 4 of its stated values wrong (F4 ×3, F8) |
| 17 | OpenFisca suite, income 2019 (82 returns, M only) | — | 77/82; the 5 are wrong stated values (forestry credit; W/S without age ×3; …) | — |
| 18 | **Withholding rates: default grids** (18 grids, 702 cells; PAS.md) | 720/720 probes = statute | 701/702 (W6: 8,739 for 8,789) | no PAS variable |
| 19 | **Withholding rates: random households** (household rate 118,616; couples' rates 36,779) | = M on all but W1 (738 households); couples: = M on 36,254 with the single-person décote (W4) | — | — |
| 20 | **Withholding rates: production simulator** (323 chosen returns, 53 couples; 131 saved typical) | household 269/323 after the W3 fix (251 before); couples 30/53 (43/53 with W4 variant); typical 130/131 | 318/318, refuses 5 production computes; couples 53/53; typical 128/128, refuses 3 (IM15) | — |

## What production says about each disagreement

| Disagreement | Statute | Production (DGFiP simulator) | Mlang | Lean |
|---|---|---|---|---|
| F1 union-dues credit, overtime limit 2022–2024 | 7,500 € | 5,000 € (refund 79–88 € instead of 72 €) | = production | = statute |
| F2 CEHR with flat-levy income | RFR, no proration | prorated: 1.4–2.3 % less CEHR | = production | = statute |
| F5 amounts ending .49995–.49999 | round down | round up (1–2 € more) | = production | = statute |
| F6 2CK credit with no tax advantage, 2020–2021 | credit refundable, not capped | 79 € / 47 € | 628 € (driver bug) | = production |
| F7 actual expenses above salary | deficit against other income | nets it (2020–2024) | refuses from 2022 | = production (after fix) |
| T for a widow(er) with children; S/W under 74; L with N | art. 194 II; art. 195, 1 f, 6; 195, 1 a, b, e | as statute | as statute (refuses S/W under 74 from 2022) | = production (after fixes) |
| Invalid boxes (F on a single return, T for a couple, 3VG with 3VH) | — | refuses | 2020–2021 computes anyway | computes (no input controls) |
| F4 art. 157 bis allowance for a couple both over 65 | two allowances | two | = production | = production (OpenFisca and three LexImpact tests: one) |
| F8 young-innovative-company reduction, income 2024 | counted | counted (7,213 €) | = production | out of scope (OpenFisca: left out, 551 € more tax) |
| W1 withholding rate when the tax is under 61 € | rate as computed | nil | = production | = statute |
| W2 withholding rate ending .x4995–.x4999 (2020–2024) | round down | round up | = production | = statute |
| W3 204 H II zero-rate threshold | codified figure | next year's figure | = production | = statute |
| W4 décote in couples' individualised rates | couples' décote (art. 197 I 4) | single-person décote | = production | = statute (variant = production) |
| W6 dependants' default grid, income 2025 | 8,789 € | not printed | 8,739 € (24 % instead of 20 % on 8,739–8,788 €/month) | = statute |

## Benchmarks added on 17 November (afternoon)

| # | Benchmark | Lean | Mlang | Other |
|---|---|---|---|---|
| 21 | **National population, 2023 and 2024** (250 k households each, calibrated to 360 published margins; POPULATION.md) | net tax 112.95 Md€ (2024; 112.92 before the 2AB/6GP fix) | 112.95 Md€ (Lean − M = +0.57 M€) | — ; published 91.72 Md€: both +23 %, top decile and unmodelled reductions |
| 22 | **Loophole search** (121 M Lean evaluations; LOOPHOLES.md) | 18 findings, 18 theorems (5 kernel-only) | every sampled comparison equal | 24 production returns equal to Lean |
