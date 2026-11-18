# France: catalogue of income-tax optimisations (income 2025), triaged and recreated

18 November 2026. Builds on [`FrTax/reports/LOOPHOLES.md`](../../../FrTax/reports/LOOPHOLES.md) (17 November: 18 findings, 14 known optimisations recreated), which
is cited here, not redone. Model: [`lean-proofs/FrTax`](../../../FrTax), unchanged (the Lake project in `lean/` reads it from there); the statute-faithful
additions are in `lean/FrLoop/Extra.lean` (exe `frloop`; with no additions it gives the same results as `frtax`:
0 differences on the 82 returns of `harness/known2.py`). Figures: `runs/known2.json` (`harness/known2.py`).
"Saving" is the household's burden without the optimisation minus with it: income tax + CEHR + CDHR + levies
assessed on the return ("tax3" rows leave out the levies, which are equal both ways or are not carried by the
emulation). Single = box 0AC, couple = 0AM. Statutory options are choices the law offers; anything resting on a
false declaration is fraud; abus de droit (LPF L64, L64 A) is noted where relevant.

Triage: **(a)** expressible with the existing boxes; **(b)** a small statute-faithful addition in `FrLoop/Extra.lean`
(cited); **(c)** out of scope, with the reason. Sources: CGI articles (as in force for 2025, from Légifrance) and the BOFiP; the earlier report's sources for E1–E17.

## Already recreated in `FrTax/reports/LOOPHOLES.md` (cited, not rerun)

| # | Optimisation | Law | Result there | Triage |
|---|---|---|---|---|
| E1 | Adult child: attach or deduct alimony | 6, 3; 156, II, 2°; 196 B | alimony wins above ~44–50 k€ (≤ 1 004 €), attachment wins for a 3rd child (≤ 1 557 €). New here: the CDHR reverses it (NOVEL N4) | a |
| E2 | Scale option (2OP) vs flat tax (PFU) | 200 A, 1 and 2; 158, 3, 2° | ≤ 5 120 € for the non-taxable; 2OP wins for CDHR payers (≤ 8 033 €) | a |
| E3 | Actual expenses vs 10 % | 83, 3°; 199 quater C | trap: union members lose ≤ 375 € | a |
| E4 | Marriage/PACS vs two singles; pension allowance cap | 6, 1; 194; 158, 5, a | bonus ≤ 12 492 €; penalties ≤ 310 € (décote), ≤ 1 819 € (pensioners) | a |
| E5 | Separate returns in the year of marriage | 6, 5 | median 308 €, ≤ 2 600 € | a |
| E6 | Separation with shared residence + box T | 194, I, II; 197, I, 2 | ≤ 4 910 € | a |
| E7 | Cases T and L | 194, II; 195 | T ≤ 2 455 €; L ≤ 1 198 € | a |
| E8 | QF cap and special half parts | 197, I, 2 | caps reached from ~73–94 k€ | a |
| E9 | Décote zone | 197, I, 4 | 15.98 % slope, no anomaly | a |
| E10 | Over-65 / disabled allowance cliff | 157 bis | +1 € → +226 € | a |
| E11 | Tax under 61 € not collected | 1657, 1 bis | notches; gift that pays for itself (≤ 60 €) | a |
| E12 | CEHR / CDHR thresholds and smoothing | 223 sexies; 224 | CDHR takes back unlisted credits; 101.1 % band | a |
| E13 | Micro income under the flat levy and art. 197 C | 151-0; 197 C | 157 bis via the effective rate; double rounding | a |
| E14 | Gifts 66 % / 75 % | 200 | 75 % band; limit 20 % of RNI | a |
| E15 | Home-help credit | 199 sexdecies | refundable; worth 0 to CDHR payers | a |
| E16 | Micro-entrepreneur flat levy vs ordinary micro | 151-0; 50-0; 102 ter | VL saves ≤ 11 251 € | a |
| E17 | Childcare credit, school-fee reductions | 200 quater B; 199 quater F | refundable / small; neutral for CDHR payers | a |

## New items recreated here

| # | Optimisation | Law (source) | Scenario (2025) | Saving | Triage |
|---|---|---|---|---|---|
| K17 | Exempt overtime | 81 quater, I (7 500 €); 1417, IV, 1° c (kept in RFR) | single, salary 40 000 €, overtime 7 500 € exempt vs taxable | 2 025 €; **0 € for a CDHR payer** (it stays in the CDHR base) | a |
| K18 | Value-sharing bonus (PPV) exempt | loi 2022-1158, art. 1, V–VI quater | 6 000 € with a profit-sharing scheme / 3 000 € without | 1 620 € / 810 € | a |
| K19 | Retirement savings (PER) deduction; pooling of the spouses' ceilings | 163 quatervicies, I (3, c: pooling, box 6QR) | 8 000 € at salary 80 000 €; couple 150 k/20 k, 20 000 € paid by declarant 1, ceilings 15 k/5 k | 2 400 €; pooling 1 500 €; **0 € in or above the CDHR band** (added back to the RFR) | a |
| K20 | Property deficit on global income (10 700 €; 21 400 € for energy renovation 2023–2025) | 156, I, 3° (BOI-RFPI-BASE-30) | single, salary 80 000 € | 3 210 € / 6 420 €; CDHR above the band 2 140 € (20 %); **in the band 8 827 € (82.5 %)** | a |
| K21 | Monuments historiques: deficit without cap | 156, I, 3°; 156 bis (BOI-RFPI-SPEC-30) | 100 000 € deficit, salary 400 000 € | 48 000 € (45 % + CEHR 3 %) | a |
| K22 | Micro-foncier (30 %) vs actual regime | 32; 28–31 | rents 14 000 €, expenses 20/30/40/60 % | −660 / 0 / 661 / 1 983 €: break-even at 30 % (levies included) | a |
| K23 | Micro-BNC (34 %) vs déclaration contrôlée | 102 ter; 93 (BOI-BNC-DECLA-10-40) | receipts 60 000 €, expenses 20/34/50 % | −2 520 / 0 / 2 880 €; same logic for 71 % / 50 % BIC (self-employed contributions not modelled) | a |
| K24 | Furnished letting (LMNP): actual regime with depreciation vs micro 50 % | 50-0; 39 C (BOI-BIC-CHAMP-40-20) | rents 15 000 €, depreciation bringing the profit to 0 | 2 250 € a year (in-year view; the depreciation schedule is multi-year; 5KP stands for the 2025 furnished boxes) | a (emulated) |
| K25 | Life insurance ≥ 8 years: 4 600 / 9 200 € allowance; 7.5 % rate | 125-0 A; 200 A, 2 bis (BOI-RPPM-RCM-20-10-20-50) | 4 600 € of proceeds vs interest; 20 000 € post-2017 proceeds | 589 €; 1 405 € (income tax only) | a |
| K26 | PEA exemption after 5 years | 157, 5° bis (BOI-RPPM-RCM-40-50) | 5 000 € of dividends | 640 € (12.8 %; levies equal) | a |
| K27 | Year of death: two returns, each on the couple's parts | 6, 8; 196 ter (BOI-IR-LIQ-10-10-10-20) | salaries 60 k/20 k, death on 30 June | 7 246 € (survivor run as a couple); 5 682 € lower bound (survivor on 1 part) | a (emulated) |
| K28 | Married adult child attached: 6 855 € allowance per person | 6, 3; 196 B | parents 120 000 €, child + spouse without income | 4 113 € | a |
| K29 | Hosting a person over 75 of low means: flat deduction | 156, II, 2° ter (BOI-IR-BASE-20-60-30 § 80: 4 075 €) | salary 60 000 € | 1 223 € | a |
| K30 | Prestation compensatoire: capital within 12 months (25 % reduction, ≤ 30 500 €) vs paid over more than 12 months (deductible) | 199 octodecies; 156, II, 2° (BOI-IR-RICI-160) | payer 120 000 €, 30 500 € | capital 7 625 €; spread 11 727 € to the payer, but the recipient (salary 25 000 €) then pays 7 244 €: jointly the capital wins (7 625 € vs 4 483 €) | b |
| K31 | Quotient for exceptional income | 163-0 A, I (BOI-IR-LIQ-20-30-20); CDHR: 224, II ninth para., IV | 40 000 € on 40 000 € / on 20 000 €; 200 000 € on a couple + 2 children at 60 000 €; 300 000 € with 150 000 € of dividends | 0 € (same band) / 5 400 € / 19 287 € / **49 108 €** (the CDHR counts exceptional income for a quarter) | b |
| K32 | Pinel / Denormandie reduction, inside the 10 000 € cap | 199 novovicies (BOI-IR-RICI-360, -365); 200-0 A, 1 | 5 000 € a year at 80 000 €; with 12 000 € of home help | 5 000 €; with home help only 4 000 € (cap); a CDHR payer keeps 5 000 € (listed, loi 2025-127 art. 10, II) but home help is worth 0 to them | b |
| K33 | Girardin industriel: cap 18 000 € counting the reduction for 44 % | 199 undecies B; 200-0 A (BOI-IR-LIQ-20-20-10-30) | 50 000 € asked at salary 300 000 € | 40 909 € of reduction in one year (`girardin_40909_2025`); for a CDHR payer 20 000 € of Girardin is worth 20 000 €, 20 000 € of gift reduction 0 € | b |
| K34 | IR-PME / FCPI / FIP (18 %) | 199 terdecies-0 A (BOI-IR-RICI-90) | 50 000 € subscribed at 100 000 € | 9 000 € | b |
| K35 | Malraux: outside the global cap | 199 tervicies; 200-0 A (BOI-IR-LIQ-20-20-10-10 § 95) | 100 000 € of works + Pinel 10 000 € at 300 000 € | 40 000 € in one year (30 000 € outside the cap) | b |
| K36 | Global cap of the niches (10 000 € / 18 000 €) and what sits outside it (gifts, Malraux, MH deficit, QF) | 200-0 A (BOI-IR-LIQ-20-20-10-10, -30) | see K32, K33, K35 and NOVEL N1 | home help eats the cap: −1 000 € (no CDHR), −5 000 € net for a CDHR payer | b |
| K37 | Pre-2018 shares: 2OP with the 50 % / 65 % holding allowance | 150-0 D, 1 ter; 200 A, 2 (BOI-RPPM-PVBMI-20-20) | gain 50 000 €, couple 60 000 € / 200 000 € | +2 130 € / −775 € (2OP loses at the 41 % rate) | a (emulated: net gain + allowance in the RFR) |
| K38 | Retiring company director: 500 000 € allowance | 150-0 D ter; CDHR base: 224, II, 1° | gain 700 000 €, pension 30 000 € | **101 656 €**: 64 000 € of flat tax and 37 656 € of CDHR (the allowance leaves the CDHR base, not the CEHR one). Production: 43 744 € vs 145 400 € | a (emulated) |
| K39 | Student job exemption (3 × monthly SMIC) | 81, 36° (BOI-RSA-CHAMP-20-30) | attached student earning 5 400 €, parents 90 000 € | 1 458 € | a |

## Not run separately, same mechanism as above

| # | Optimisation | Law | Why not run |
|---|---|---|---|
| G1 | SOFICA, Censi-Bouvard, Loc'Avantages, forests (DEFI forêt), ESUS / foncières solidaires | 199 unvicies; 199 sexvicies; 199 tricies; 199 decies H; 199 terdecies-0 AA/AB | each is a reduction with a rate and ceiling inside the 10 000 € or 18 000 € cap: the K32–K34 machinery covers them; adding the rates is mechanical (b), no new interaction |

## Out of scope (c)

| # | Optimisation | Why |
|---|---|---|
| C1 | PER: deduction now vs taxation at exit (capital or annuity), unused ceilings over 3 years | multi-year |
| C2 | Gifts above 20 % of RNI carried forward 5 years; Girardin/PME carry-forward | multi-year (only the carried amounts as boxes) |
| C3 | CEHR smoothing (223 sexies, II) and the CDHR's three-year average test for exceptional income | needs the two/three previous RFRs; the CDHR quarter rule is applied when the income is entered as exceptional (K31) |
| C4 | IFI, démembrement, donations (Sarkozy, 15-year allowances), life insurance on death (990 I, 757 B), Pacte Dutreil | wealth and succession taxes |
| C5 | Holding contributions (apport-cession 150-0 B ter), SCI at corporate tax, management packages | entity level |
| C6 | LMNP/LMP depreciation schedules, carried-forward BIC deficits, LMP status | multi-year asset schedules (in-year effect in K24) |
| C7 | Micro flat-levy eligibility planning (RFR N−2) | multi-year |
| C8 | Exit tax, impatriate regime (155 B), treaty-exempt income | non-resident / treaty |
| C9 | Termination indemnities exemption (80 duodecies) | exempt income outside the return; arithmetic as K39 |
| C10 | Micro vs real regime including self-employed contributions (URSSAF) | contributions of the self-employed not modelled (income-tax part in K23) |

## Counts

Catalogued 51: recreated 40 (E1–E17 earlier, K17–K39 here: 12 with existing boxes, 4 emulated with existing
boxes, 7 through the additions K30–K36), 1 grouped (G1), 10 out of scope (C1–C10). Headline items proved in
`lean/FrLoop/Proofs.lean`; production simulator checks in `runs/sim.jsonl` (see NOVEL.md).
