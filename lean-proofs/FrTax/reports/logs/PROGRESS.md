# French income tax in Lean vs Mlang (goal set 2026-11-17)

Status file for the French Lean work on the build server. Update at each milestone.

## Plan (one owner, steps in order)
1. [x] Sources: Mlang (adullact, 2026-10-26), ir-calcul M sources 2010–2025 (sources2025m_3_11, published 2026-11-09), OpenFisca-France, combine-calculators, Catala examples, papers (CC21, Étude formelle, Catala ICFP21) in ~/fr/refs, ~/fr/papers
2. [ ] Build Mlang (opam local switch) and reproduce its test pass rates (2024, 2025 fuzzing; 2018 randomized)
3. [ ] Lean model of the CGI income tax (income 2024, taxed 2025), from the statute: ~/fr/lean
4. [ ] Benchmarks + harness: DGFiP tests, OpenFisca YAML, BOFiP/brochure worked examples, random realistic households (Lean vs Mlang differential), properties
5. [ ] Investigate every disagreement: Lean bug, M bug, or reading of CGI
6. [ ] Write-up (HTML report)

## Log
- 2026-11-17T00:22:16Z sources cloned; Mlang build started (build_mlang.log)
- 2026-11-17T00:25:21Z Mlang built; DGFiP 2024 suite: 2809/2809 pass (88 s wall, 42.6 CPU-min interpreter)
- 2026-11-17T00:52:39Z Mlang C backend built for 2024 and 2025 (~/fr/bin/cal2024, cal2025): 2024 suite 2809/2809, 2025 suite 3091/3091 (C backend, 0 incorrect). Harness ~/fr/harness (gen.py, run.py, probe.sh). Lean model v1 ~/fr/lean (FrTax).
- 2026-11-17T00:52:39Z Differential r4 (5000 random households, 4710 accepted by M): all compared fields equal 91.23%. Fixes so far: REGCO=1 needed in inputs; frais réels = max(10%, real) as M; art. 157 bis amounts indexed per its own rule (text lags a year; décret each June); complement of 197 I 2 al.4 not for case L (capped under 3rd para); RFR overtime net of 10% allowance.
- 2026-11-17T01:04:53Z r9 (18790 accepted): 100.00%; r10 fresh (18819): 99.99%. Fixes: T alternée 0.25/0.5 (194 II), QF caps rounded (1657), décote difference rounded, 7UD/7UQ split for 2025 (LF2026 art 28)
- 2026-11-17T01:26:38Z Added social levies (CSS L136-6/8, CRDS, 235 ter; 2025 rates; 61 € rule), 2CH, 5ND (2024), rentes PS, one micro allowance per category. r16: 29643/29643 (100.00%) on 10 fields incl. PSNET.
- 2026-11-17T01:33:51Z BENCHMARK brochure thresholds (Tableaux 4, 6, 7), both editions:
  ed 2025 T4: 42 printed cells; Lean=printed 15; Lean=M 42
  ed 2025 T6: 12 printed cells; Lean=printed 12; Lean=M 12
  ed 2025 T7: 12 printed cells; Lean=printed 0; Lean=M 12
  ed 2026 T4: 42 printed cells; Lean=printed 12; Lean=M 42
  ed 2026 T6: 12 printed cells; Lean=printed 12; Lean=M 12
  ed 2026 T7: 12 printed cells; Lean=printed 7; Lean=M 12
- BENCHMARK brochure barème tables: 2025 ed 3647 cells, 2026 ed 3672: Lean tableTax 100%; household cells 2446 + 2463: Lean 100%, Mlang 100%.
- 2026-11-17T02:13:22Z Coverage added: PER (163 quatervicies + ceilings + 6QR), CEHR, CDHR (2025, NOTA-correct), real-regime profits, micro flat levy with effective rate (197 C), gifts 7UJ/7UO/7VC/7UH, 3VZ/2EE in RFR, taxable overtime > 7 500. r24 (29636 accepted): 99.97% all 12 fields; the 8 others are F2 (CEHR scaling with flat-levy income). FINDINGS.md: F1 (union credit LIM5000, income 2022-2024), F2 (open).
- 2026-11-17T02:43:11Z Life insurance (2DH/2UU/2VV/2WW/2ZZ/2YY, art. 125-0 A, 200 A) added; r26 99.99% (only F1/F2). Benchmarks done: worked examples 18/18 Lean and M; OpenFisca-France 177 vs M 73.7% (2024) / 71.8% (2025) on 3000 each (causes: RFR without overtime, rounding < 2 €, 157 bis not doubled = numpy bool add, age on 1 Jan); speed Lean 14 us, cal 0.32 ms compute, OpenFisca 0.6 ms. Theorems.lean (monotone scale and décote, indexation, cliffs) + Brochure67.lean (80 theorems: every T6/T7 cell; 29 printed T7 cells wrong). Coverage: 107 tested boxes = 93.2% of 2024 box entries. Draft post saas-webpage app/blog/formalizing-the-french-tax-code (unfinished). Final 100k run in progress (final_run.sh).
- 2026-11-17T02:50:47Z FINAL: 100k households (98,868 accepted by M): Lean = M on all 12 figures for 98,849; 19 others all F2. OpenFisca vs M: 73.5% (2024), 70.8% (2025) of 5,000 each. 5ND/5KP levy share fixed. Draft post filled. DONE.
