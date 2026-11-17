# French income tax at the scale of France: the Lean model and the DGFiP's M code on a calibrated population (17 November 2026)

Question: every earlier benchmark tests households one by one, on generated households that are "plausible, not a
sample". Here the DGFiP's published national statistics are used (a) to see whether a statute model reproduces
France's actual income-tax totals and (b) to put a number of households and of euros on each finding (FINDINGS.md
F1–F8, PAS.md W1–W6).

Files on the build server: raw data `~/fr/data/pop/raw/`, parsed targets `data/pop/targets_{2023,2024}.json`, the boxes Lean reads
`data/pop/lean_boxes_{2023,2024}.json`, coverage `data/pop/coverage_{2023,2024}.json`, published-count arithmetic
`data/pop/scale.json`, pools and results `runs/pop/{2023,2024}/` (cases, lean, m, m_rejected, weights, fit.tsv,
report.json), scripts `harness/pop_*.py` (+ `pop_all.sh`), progress `PROGRESS_pop.md`.

## 1. Data

All files were fetched on 2026-11-17 from the build server with plain HTTP requests (no challenge page met, nothing bypassed).
economie.gouv.fr web pages were not used; data.economie.gouv.fr's API, data.gouv.fr and impots.gouv.fr served normally.

| File (data/pop/raw/…) | URL | Date | Covers |
|---|---|---|---|
| `ir-declarations-2042-nat.csv` (= `docs/data/boxes.csv` already in the project, byte-identical) | `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/ir-declarations-2042-nat/exports/csv` ("L'impôt sur le revenu : les déclarations nationales") | dataset modified 2026-04-07 | Every box of forms 2042, 2042-C and 2042-IOM: number of declarations filling it and amount declared, income 2006–2024 (1 213 boxes for 2024, 1 222 for 2023) |
| `ircom-2025-revenus-2024/…/national/national.xls` | `https://static.data.gouv.fr/resources/limpot-sur-le-revenu-par-collectivite-territoriale-ircom/20260526-131537/ircom-2025-revenus-2024.zip` (data.gouv.fr dataset 536998cba3a729239d20505e, "IRCOM") | resource 2026-05-26 | Income 2024, France: households, RFR, net tax ("impôt net (total)"), taxed households and their RFR, salaries and pensions (households, amounts) for 25 RFR brackets; non-residents line |
| `ircom-2024-revenus-2023/…/national/national.xls` | `https://static.data.gouv.fr/resources/limpot-sur-le-revenu-par-collectivite-territoriale-ircom/20250919-135242/ircom-2024-revenus-2023.zip` | resource 2025-09-19 | Same for income 2023 |
| `dgfip_stat/dgfip_stat_41.{pdf,xlsx}` | `https://www.impots.gouv.fr/sites/default/files/media/9_statistiques/0_etudes_et_stats/0_publications/dgfip_statistiques/2025/num41_11/dgfip_stat_41.xlsx` (and `.pdf`) | November 2025 | DGFiP Statistiques n° 41, "L'impôt sur le revenu 2024 a été plus dynamique que les revenus": income 2024 from the 3rd emission (provisional): net tax 92 Md€, tax at the scale 98.84 Md€, flat-rate tax 10.32 Md€, CEHR 1.98 Md€, RICI 19.53 Md€ (credits 9.77, reductions 9.75), 41.5 M households, 19.6 M taxed, main credits and reductions with beneficiaries |
| `dgfip_stat/dgfip_stat_32_2025.{pdf,xlsx}` | `…/dgfip_statistiques/2025/num32_04/dgfip_stat_32_2025.xlsx` | April 2025 | n° 32, income 2023 (data at February 2025): net tax 83.5 Md€, scale 91.77, flat 7.60, CEHR 1.40, by marginal rate; RICI 17.8 Md€ |
| `dgfip_stat/dgfip_stat_53_ir_2025.{pdf,xlsx}` | `…/dgfip_statistiques/2026/num53_11/dgfip_stat_53_ir_2025.xlsx` | November 2026 | n° 53, income 2025 (provisional). Recorded, not used: there are no 2042 box statistics for income 2025 yet |
| `tables/nid_25518_ir_deciles_rfr_par_part.xlsx` | `https://www.impots.gouv.fr/sites/default/files/media/9_statistiques/0_etudes_et_stats/1_statistiques/1_impots_particuliers/ir/nid_25518_ir_deciles_rfr_par_part.xlsx` | fetched 2026-11-17 | Deciles of RFR per part 2003–2024: bounds; for 2024 (6th emission) mean parts, RFR per part, tax at the scale, flat tax, CEHR, RICI per part |
| `tables/nid_25519_ir_taux_marginal.xlsx` | `…/ir/nid_25519_ir_taux_marginal.xlsx` | fetched 2026-11-17 | Households and net tax by marginal rate (quotient familial), income 2019–2024 |
| `tables/nid_25520_ir_revenus_categoriels.xlsx` | `…/ir/nid_25520_ir_revenus_categoriels.xlsx` | fetched 2026-11-17 | Declared income by category, taxed / non-taxed households, 2019–2024; defines "imposé" (impôt sur rôle, corrected for the PFO credit, > 0) |
| `tables/nid_25535_ir_ci_deciles_rfr_par_part.xlsx` | `…/ir/nid_25535_ir_ci_deciles_rfr_par_part.xlsx` | fetched 2026-11-17 | Every tax credit: beneficiaries and amounts by decile of RFR per part, 2017–2024 |
| `tables/nid_25536_ir_ri_deciles_rfr_par_part.xlsx` | `…/ir/nid_25536_ir_ri_deciles_rfr_par_part.xlsx` | fetched 2026-11-17 | Every tax reduction, same, 2021–2024 |
| `vmt/Voies_et_moyens_Tome_2_2026.pdf` | `https://www.assemblee-nationale.fr/dyn/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf` | PLF 2026, October 2025 | Cost of each tax expenditure (overtime exemption 120146: 2 144 M€ in 2024; union-dues credit 110202: 156 M€) |

The impots.gouv.fr table pages are `https://www.impots.gouv.fr/node/25518` etc. (each redirects to the xlsx); the
bulletins' pages are listed at `https://www.impots.gouv.fr/dgfip-statistiques-2025` and `-2026`.

Not found in any published table: the national **décote** (households, amount), the number of households whose tax is
**under the 61 € collection threshold**, and the number of **CEHR** payers. The décote is not a tax expenditure (VMT II
lists it among the mechanisms excluded), so it has no line in the Voies et moyens either. For these three the totals
below give Lean and M only.

Definitions that matter for the comparison:
- IRCOM "impôt net (total)": "Impôt sur le revenu émis par voie de rôle, hors prélèvement forfaitaire obligatoire sur
  les revenus de capitaux mobiliers et crédit d'impôt correspondant, hors prélèvements libératoires … et hors impôt sur
  les plus-values immobilières". CEHR included (bulletin n° 41: "la CEHR, incluse ici dans le périmètre de l'IR").
  So the comparable model figure is net tax + CEHR with no 2CK (the 12.8 % instalment and its credit): the pool never
  fills 2CK.
- "Foyer imposé": tax on the roll, corrected for the PFO credit, above zero (after the 61 € rule).
- IRCOM counts 41 635 259 households for 2024 including 298 023 non-residents (953 M€ of net tax). The pool is resident.
- The bulletin figures are provisional (3rd emission, September 2025); IRCOM and the decile table are later emissions
  (6th): net tax 91.72 Md€ (IRCOM) vs 92 Md€ (bulletin).

## 2. Population: pool, runs, calibration

**Which boxes Lean reads** (`harness/pop_boxprobe.py`): every box code of the 2042 dataset is added (value 1 for tick
boxes, 1 000 and 15 000 € for amounts) to five base households; a box is "read" if any Lean output changes. Union of
that probe and the box codes named in `lean/FrTax/*.lean`: 183 of the 1 213 codes published for 2024. Boxes that only act in combination
(ceilings with 6NS, 7GA with a child under 6) are caught by the source list.

**Pool** (`harness/pop_gen.py`, a copy of gen.py extended): 250 000 households per income year, built from the boxes
Lean reads, in four income tiers (78 % ordinary, 14 % affluent, 6 % rich, 2 % very rich) so that the RFR tail up to
30 M€ is represented; family situation, children with birth years, half-part ticks, salaries and pensions per person,
overtime, actual expenses, unemployment pay, alimony, annuities by age band, investment income and life insurance,
gains, property income, micro and real-regime business income, flat-levy micro income, CSG deductible, retirement
savings with ceilings, donations, home help, childcare, schooling, dependency, union dues. The 12.8 % instalment (2CK)
is never filled (see the net-tax definition above). Generation rules avoid the M input controls met in a first draft
(4BA with 4BB/4BC, 1AF without 8TK, case G with situation D, ceilings above 35 194 €, union dues with actual
expenses, and the N-1 CSG discordance DD22, which M is told to ignore by setting `V_BTCSGDED` = 6DE in the IRJ only).

**Runs** (`harness/pop_run.py`): Lean (`frtax`) on all 250 000; M (`cal2023`, `cal2024`, IRJ with `REGCO/1`,
`ANREV/<year>`, completion mode) in chunks of 400 on /dev/shm, 12 jobs. Returns M refuses with only IM15 (net tax ≥
1 M€: "validez avec une habilitation") are run again with `V_NOTRAIT/23`, the processing number for which that check
is skipped; `harness/pop_check_notrait.py` reran 2 000 accepted returns with `V_NOTRAIT/23` and found no M variable
changed. What M still refuses is IM2102 only ("RICI > 80 % du RFR et âge < 65 ans", an informative anomaly that
production computes; FINDINGS P: Lean = production on every such return). For those, M's totals below use Lean's
values; their weight is given with each total.

**Calibration** (`harness/pop_calib.py`): weights w = d · g, where the design weights d post-stratify the pool on
13 IRCOM RFR groups (this undoes the deliberate oversampling of the tail) and g comes from the bounded logit distance
of Deville and Särndal (1992), g ∈ [0.05, 20], solved in the dual by L-BFGS with soft constraints (each constraint
scaled to its target; residual = −c·λ, c from 1e-5 for the household total to 1e-2 for the softest). Margins
(inputs only; no tax figure is a margin):
- IRCOM, 13 RFR groups: households, RFR amount, households with salaries and with pensions, salary and pension
  amounts (IRCOM's own aggregation scaled to the 2042 boxes' national totals: salaries ×0.935, pensions ×0.993 in 2024; 0.938 and 0.996 in 2023);
- deciles of RFR per part (table nid_25518): households per decile (10 %); for 2024 also parts and RFR per decile;
- beneficiaries of the home-help, childcare and union-dues credits per decile (table nid_25535), as box presence;
- family situation (0AC 0AD 0AV 0AM 0AO) and every box the pool fills that at least 20 000 declarations fill
  nationally: declarations filling it and amount (114 boxes in 2024, 113 in 2023).
Outcomes compared, never calibrated: net tax, taxed households, tax at the scale, flat-rate tax, CEHR, reductions,
credits, households with a RICI, décote, the 61 € threshold, households and tax by marginal rate, tax by RFR bracket.
(RFR and parts, used to place households in groups and deciles, are computed by Lean; M gives the same on all but
a handful of returns.)

**Fit** (`runs/pop/<year>/fit.tsv`, `calib.log`). 2024: 360 margins, 357 within 5 %, all within 10 %; 2023: 339, 334
within 5 %, all within 10 %. L-BFGS stopped at its 30 000-iteration limit in both years; the residuals below are
what that leaves.

| Margin family (2024) | margins | within 1 % | within 5 % | worst |
|---|---|---|---|---|
| total households | 1 | 1 | 1 | 0.0 % |
| IRCOM groups: households / with salaries / with pensions | 13 / 13 / 13 | 13 / 13 / 13 | all | ≤ 0.1 % |
| IRCOM groups: RFR amount | 13 | 12 | 13 | −1.1 % (50–100 k) |
| IRCOM groups: salary amount / pension amount | 13 / 13 | 9 / 10 | 12 / 13 | +5.1 % salaries 50–100 k; +2.2 % pensions 30–50 k |
| RFR-per-part deciles: households, parts, RFR | 29 | 29 | 29 | −0.9 % (D10 RFR) |
| credit beneficiaries per decile (7DB, 7GA…, 7AC/7AE) | 30 | 30 | 30 | 0.0 % |
| family situation and half-part ticks | 11 | 11 | 11 | 0.0 % |
| 2042 boxes: households | 108 | 104 | 108 | +4.1 % (2UU) |
| 2042 boxes: amounts | 103 | 98 | 101 | −5.2 % (0CR), −5.1 % (0CG), +4.0 % (1AJ) |

2023: the same, except that the 2023 decile table gives only the bounds (10 margins) and 1BA (pay from private
employers) misses by −5.9 % (households) / +8.8 % (amount). Weights: 2024 from 0.48 to 4 778 (median 62; Kish
effective size 60 530 of 250 000; 10.2 % of households at the lower bound, 0.19 % at the upper); 2023 from 0.13 to
5 247 (effective size 38 864).

## 3. Totals: published vs Lean vs M

Income 2024 (pool 250 000; M refuses 1 910 returns, all IM2102, weight 112 453 households, filled with Lean's values):

| Figure | Published | Lean | M | Lean / published |
|---|---|---|---|---|
| Households | 41 635 259 (IRCOM) | 41 635 271 | = | calibrated |
| **Net income tax incl. CEHR** | **91.72 Md€** (IRCOM; bulletin n° 41: 92 Md€) | **112.92 Md€** | **112.95 Md€** | **1.23** |
| of which non-residents | 0.95 Md€, 298 023 households | not in the pool | | |
| Taxed households (net tax > 0) | 19 681 757 (bulletin 19.6 M) | 21.47 M | 21.47 M | 1.09 |
| Tax at the scale (after décote, before RICI) | 98.84 Md€ | 114.52 Md€ | 114.52 Md€ | 1.16 |
| Flat-rate tax ("hors barème": PFU 12.8 %, 7.5 %…) | 10.32 Md€ | 7.46 Md€ | 7.46 Md€ | 0.72 |
| CEHR | 1.98 Md€ | 2.57 Md€ | 2.57 Md€ | 1.30 |
| CEHR households | not published | 154 644 | 154 644 | |
| Reductions (hors PFU) | 9.75 Md€ | 2.01 Md€ | 2.01 Md€ | 0.21 |
| Credits (hors PFO) | 9.77 Md€ | 9.50 Md€ | 9.43 Md€ | 0.97 |
| Households with a reduction or credit | 12.83 M | 12.73 M | 12.42 M | 0.99 |
| Décote | not published | 8.16 Md€, 19.56 M households | same | |
| Households with tax before credits in (0, 61 €) | not published | 6.40 M | 6.29 M | |
| RFR | 1 375.1 Md€ | 1 365.8 Md€ | = | calibrated |

Income 2023 (M refuses 4 336: IM2102 3 703, A601 388 — the 2023 code's lower ceiling for APS/APT —, IM2101 246, IM15
with another code 42; weight 615 928, filled with Lean's values):

| Figure | Published | Lean | M | Lean / published |
|---|---|---|---|---|
| Net income tax incl. CEHR | 83.55 Md€ (IRCOM; bulletin n° 32: 83.5) | 108.47 Md€ | 108.50 Md€ | 1.30 |
| Taxed households | 18 674 378 | 20.28 M | 20.28 M | 1.09 |
| Tax at the scale | 91.77 Md€ | 111.24 Md€ | 111.24 Md€ | 1.21 |
| Flat-rate tax | 7.60 Md€ | 6.15 Md€ | 6.15 Md€ | 0.81 |
| CEHR | 1.40 Md€ | 1.92 Md€ | 1.92 Md€ | 1.37 |
| Reductions | 8.7 Md€ | 1.82 Md€ | 1.82 Md€ | 0.21 |
| Credits | 9.0 Md€ | 8.90 Md€ | 8.83 Md€ | 0.99 |
| Households with a RICI | 12.4 M | 12.11 M | 11.80 M | 0.98 |
| Décote; tax under 61 € | not published | 7.95 Md€, 19.29 M households; 6.42 M | same; 6.32 M | |

**Lean and M agree with each other on the population**: the totals differ by 0.03 % (2024: 112.92 vs 112.95 Md€).
200 439 weighted households (0.48 %) differ on net tax, for −27.7 M€ net (Lean lower), see §4. So the gap to the
published totals is not a Lean–M question: the DGFiP's own program, run on the same population, is as far off.

**Where the gap is** (2024, Lean − published, using the bulletin's components): +21.2 Md€ = scale +15.7, reductions
+7.7 (Lean 2.01 vs 9.75), CEHR +0.6, credits +0.3, flat-rate −2.9. By decile of RFR per part (table nid_25518, 6th
emission, published / Lean, Md€):

| Decile | Tax at the scale | Flat-rate tax | RICI | Net tax |
|---|---|---|---|---|
| D1–D5 | 0.56 / 0.34 | 0.21 / 0.59 | 2.50 / 3.09 | −1.71 / −2.28 |
| D6 | 1.99 / 1.95 | 0.07 / 0.16 | 0.93 / 0.99 | 1.19 / 1.11 |
| D7 | 4.58 / 4.58 | 0.13 / 0.17 | 1.16 / 1.12 | 3.48 / 3.63 |
| D8 | 8.32 / 8.43 | 0.13 / 0.24 | 1.68 / 1.38 | 6.84 / 7.29 |
| D9 | 16.20 / 16.46 | 0.32 / 0.28 | 2.71 / 1.66 | 13.81 / 15.08 |
| **D10** | **66.95 / 82.75** | **9.59 / 6.02** | **10.46 / 3.27** | **68.02 / 88.07** |

Deciles 1–9 are reproduced closely (scale tax within 2 % in D6–D9, where 31 Md€ of it is raised; net tax +1.2 Md€
over D1–D9). The top decile carries +20.1 of the +21.2 Md€. Three causes, in this order:
1. **Coverage: reductions the model does not have** (≈ 6.7 Md€, almost all in D10). Lean has the donations,
   schooling and dependency reductions (published 2.99 Md€; Lean reproduces 2.01, see 3 below); it has none of the
   credit for foreign income taxed in France (3.66 Md€, 488 861 households, box 8TK not modelled), Pinel/Scellier/
   Duflot/Denormandie (1.82 Md€), overseas investment (0.78 Md€), accounting fees (0.15), SMEs (0.10) and the rest.
2. **Calibration: the composition of the top decile's income.** IRCOM gives salaries and pensions by RFR bracket but
   no split of the rest; in the pool, the top decile's non-salary income sits too much in scale-taxed categories
   (business profits 5QC/5KC, property 4BA) and too little in flat-taxed dividends and gains. Signs: scale tax +15.8 Md€
   and flat-rate tax −3.6 Md€ in D10 alone; 135 000 households at the 45 % rate against 61 476 published, and
   297 000 at 41 % against 434 112. The 2042 box totals are matched nationally, so this is where they sit, not how
   much there is. This is a limit of a synthetic calibration, not a statement about Lean or M.
3. **Smaller coverage items**: flat-rate items not modelled (pensions in capital at 7.5 % 1AT 1.2 Md€ of base,
   gains in sursis/report 3WA/3UA, life-insurance 2XX); deductions and allowances not modelled (childminders' and
   journalists' allowance 1GA/1HA 4.3 Md€, global deficits of earlier years 6FL, furnished-letting deficits 5GA–5GJ,
   reinforced and fixed allowances on gains 3SL/3VA); micro agricultural profits 5XB/5YB (5.3 Md€); in all, 357 of the 468
   income boxes with amounts are not read, 6.1 % of the declared amounts; the global cap on tax advantages (art. 200-0 A), which Lean does
   not model. The modelled reductions come out at 2.01 against 2.99 Md€ published for the same devices: the pool's
   donors are placed by the generator, and their reduction is limited by their tax.

**Taxed households** (+1.8 M): almost all are households with RFR ≤ 20 000 € that pay only the 12.8 % flat tax on
investment income (1.8 M households, 0.3 Md€). In the pool the scale option (2OP) is drawn independently of income;
in reality households with a 0 % marginal rate take it (it is pre-ticked when favourable). Published: 1.82 M taxed
households below 20 000 € of RFR; Lean 3.17 M.

**What this shows and does not show.** (a) Coverage: on the boxes it reads, a statute model fed a population that
matches France's published margins reproduces the tax at the scale of deciles 6–9 (31 Md€) within 2 %, net tax over deciles 1–9 within 1.2 Md€ (5 %), and the credits within
3 %; the national total is 23 % too high, and the DGFiP's own M code on the same population is too high by the same
amount, so the excess comes from the population (top-decile composition) and from coverage (reductions, foreign
income), not from a reading of the statute. (b) It cannot show that Lean (or M) would reproduce 91.7 Md€ on the real
microdata (POTE), which would need the DGFiP's files; the joint distributions in the pool (who has dividends, who
gives to charity, who ticks 2OP) are generator assumptions, constrained only through one-dimensional margins.

## 4. Lean vs M on the population (all differences classified)

| Class | 2024 households (pool) | 2024 net, Lean − M | 2023 households (pool) | 2023 net | Status |
|---|---|---|---|---|---|
| **2AB credit refunded** (new) | 177 091 (971) | −29.3 M€ | 183 250 (927) | −34.5 M€ | Lean adds 2AB (credit for tax paid abroad on securities income, art. 199 ter) to the refundable credits (Liquidation.lean, `credits`); M imputes it up to the tax and refunds nothing (chap-3.m: `CIRCMAVFT = max(0, min(IRB + … , RCMAVFT))`). |
| **6GP without the 25 % increase** (new) | 6 543 (176) | +1.0 M€ | 11 492 (175) | +2.5 M€ | Alimony under a court decision before 2006: M deducts `arr(PAAV × MAJREV)` (×1.25, chap-7.m `TOTPA`; art. 156, II, 2°); Lean deducts the amount declared (Income.lean). Taxable income +13.6 M€ (2024) under Lean. |
| F2 CEHR with flat-levy micro income | 6 793 (183) | +0.46 M€ | 5 294 (296) | +0.47 M€ | known; production = M |
| F1 union dues, overtime 5 000–7 500 € | 9 486 (37) | +0.11 M€ | 17 895 (48) | +0.19 M€ | known; production = M |
| other | 59 (10) | 0 | 2 570 (41) | +1.0 M€ | 2024: 1 € rounding of a two-person union credit. 2023: the global cap on tax advantages (art. 200-0 A, not in Lean) and elderly households with flat-levy micro income where M's RFR is lower by exactly the art. 157 bis allowance (1 373 €); not investigated further. |

Neither new class could appear in the earlier random runs: their generator (gen.py) never fills 2AB or 6GP. Both are written up
here only; FINDINGS.md and the Lean sources were not changed. Production was not consulted for them.

## 5. Scale of each finding

"Population" = the calibrated pool (weighted households, euros a year); "published" = arithmetic on published counts
(`harness/pop_scale.py`, `data/pop/scale.json`). Euros are a year's effect; withholding (W) findings move cash
between months and are settled at the assessment (§1 of AUTHORITY.md), they do not change the tax due.

| Finding | Households a year | Euros a year | Basis and assumptions | Range |
|---|---|---|---|---|
| **F1** union-dues credit with exempt overtime 5 000–7 500 € (income 2022–2024; production = M) | published: 21–42 k (2022), 24–48 k (2023), 27–53 k (2024) people with overtime above 5 000 € and union dues; population: 9 900 (2024), 17 900 (2023) households whose credit actually changes | population: +0.11 M€ (2024), +0.19 M€ (2023) of credit M/production gives beyond the statute; published upper bound 0.70 / 0.80 / 0.87 M€ | overtime: 1GH 10.06 M filers, mean 1 788 €, 1HH 2.30 M, mean 1 598 € (2024); share above 5 000 € from a lognormal capped at 7 500 € with the published mean, σ 0.8–1.2: 4.9–9.3 % (D1); union dues 7AC/1AJ = 4.6 %, 7AE/1BJ = 5.9 %, assumed independent of overtime; ≤ 16.50 € each (66 % × 1 % × 2 500 €), paid only when the dues exceed 1 % of pay | 10–50 k households, 0.1–0.9 M€ a year; 2022–2024 together 0.3–2.4 M€ |
| **F2** CEHR prorated for flat-levy micro income (production = M) | population: 6 800 (2024), 5 600 (2023) of 155 k / 134 k CEHR payers; published arithmetic: 217 k households above 250 k€ of RFR × 2.0 % flat-levy filers = 4 400 (13 000 at 3× the share) | population: −0.46 M€ (2024), −0.47 M€ (2023) of CEHR (production charges less than the statute) | flat-levy filers 846 137 (5TA…5UE); 1.4–2.3 % of the household's CEHR on the 22 production returns; 250 k€ is the single threshold (couples 500 k€), so the published count is an upper bound | 4–13 k households, 0.2–1 M€ |
| **F5** rounding margin .49995–.49999 (production = M) | ≈ 45: (846 k flat-levy + 23 k 8TI effective-rate households) × 5·10⁻⁵ per rounded ratio; population: none found (0.2 expected in the pool) | 1–2 € each: under 300 € in all | uniform fractional parts; 1–3 rounded ratios per return | 20–130 households, < 300 € |
| **W2** rate rounding margin (rates from income 2020–2024) | ≈ 1 000: 20.2 M households with a rate × 5·10⁻⁵; population: 197 (2024, 3 pool cases), 1 695 (2023, 6) | 0.1 point more withheld: ≈ 40 € a year each, ≈ 0.04 M€; timing only | rate fraction uniform | 200–2 000 households, < 0.1 M€ of timing |
| **W1** nil rate when the tax is under 61 € (production = M) | population: 381 000 (2024), 362 000 (2023) households whose statutory rate is ≥ 0.1 % while production's is nil | 14.1 M€ (2024), 14.0 M€ (2023) a year that the statutory rate would withhold (mean rate 0.2 %), all refunded since the tax is not collected | Lean `TXFOYER` > 0 and `TXFOYER61` = 0; 6.4 M households have a tax before credits under 61 €, but for most the rate rounds to 0.0 % anyway | 0.3–0.5 M households, 10–20 M€ of timing |
| **W4** couples' individualised rates: couples' décote (statute) vs single-person décote (production = M) | population: 2.14 M of 13.05 M couples (income 2024 → rates from September 2025, when individualised rates became the default); 1.83 M (2023, when they were optional, take-up unknown) | the rates move withholding between the partners: Σ|Δ| = 1.67 Md€ a year (≈ 0.83 Md€ moved from one partner to the other); net −16 M€ | Lean `TXDEC1/2` vs `TXDEC1S/2S` × each partner's salaries, pensions and replacement income | 1.8–2.1 M couples, 0.7–0.9 Md€ moved |
| **W6** M's dependants' default grid 8 739 € for 8 789 € (income 2025 code, rate year 2026) | published arithmetic: 0–17 people (1CJ 911 k filers, mean 3 781 €; 1DJ 122 k, mean 3 443 €; lognormal σ 1.0–1.5; band 104 868–105 468 € a year) | ≤ 351 € a month each (24 % instead of 20 % on a base of 8 739–8 788 €) | income-2024 dependants' pay as a proxy for 2025 | effectively nobody |
| **F8** OpenFisca leaves out the 2024 JEI/JEIR reduction | ≤ 12 439 (7CR 5 840 households, 36.5 M€ subscribed; 7DZ 6 599, 47.0 M€) | ≤ 34.4 M€ of reductions (30 % of 7CR + 50 % of 7DZ, M's rates and caps) | only for users of OpenFisca (simulators, LexImpact) | up to 12 k households, up to 34 M€ |
| **F4** OpenFisca: one art. 157 bis allowance for a couple both 65+ | population: 332 000 (2024) / 489 000 (2023) couples both 65+ under the 27 670 € limit, of which 52 000 / 43 000 taxed | taxable income understated by 0.53 Md€ (2024); tax ≤ 7.0 M€ (marginal rate × missing allowance) | 3.6 M couples both 65+; allowance 2 796 / 1 398 € | 7–9 M€ |
| OpenFisca RFR without exempt overtime | 11.8 M households (published 1GH 10.06 M + 1HH 2.30 M, overlapping) | 21.8 Md€ of RFR missing (published 1GH+1HH+1IH+1JH 21.83 Md€) | affects RFR-based tests (CEHR, 204 H II zero rate, local taxes, benefits), not the income tax itself | |
| OpenFisca age on 1 January | 556 000 households with a 65th birthday in the year, 179 000 of them under the 157 bis limit | small (allowance × marginal rate for the few taxed) | | |
| new **2AB** refunded by Lean | population: 177 000 (2024), 183 000 (2023) | Lean refunds 29.3 M€ (2024), 34.5 M€ (2023) more than M | published 2AB: 470 195 filers, 70.1 M€ (upper bound); the pool draws 2AB independently of income, which overstates non-taxable filers | population 29–35 M€; at most 70 M€ |
| new **6GP** ×1.25 missing in Lean | 68 675 filers (379 M€); population: 23 000 whose taxable income differs, 6 500 (2024) / 11 500 (2023) whose tax differs | +1.0 M€ (2024), +2.5 M€ (2023) more tax under Lean; upper bound 25 % × 379 M€ = 95 M€ of deductions × 15–30 % ≈ 14–28 M€ | | 1–28 M€ |

## 6. Limits

- **A synthetic calibration is not microdata.** The pool is generated; only one-dimensional margins (box counts and
  amounts, RFR brackets, deciles, credit beneficiaries by decile) are matched. Joint distributions — who has
  overtime and union dues, who has flat-levy income and a high RFR, who opts for the scale — are assumptions. The
  finding sizes that depend on such joints (F1, F2, 2AB, W1, W4) are model estimates with ranges, not counts.
- **The national total is not reproduced** (Lean and M both +23 % in 2024, +30 % in 2023). The decomposition in §3
  rests on the published decile table; the split between "top-decile composition" and "unmodelled items" inside D10
  cannot be separated further with published data.
- **2023 is weaker**: its decile table gives no parts or RFR per decile, and 616 000 weighted households (M
  refusals) carry Lean's values in M's totals.
- **Published aggregates differ among themselves**: bulletin (3rd emission, provisional) vs IRCOM and the tables (6th
  emission); non-residents (298 000 households, 0.95 Md€) are in the published totals, not in the pool.
- **Not published**: décote, the 61 € count and the CEHR count; the pool's figures for them are unverified.
- **Rare events**: F5 and W2 occur at rates of ~5·10⁻⁵; a 250 000 pool sees a handful at most, so their sizes come
  from arithmetic, not from the population.
- **Year coverage**: 2042 box statistics exist up to income 2024. W6 (income 2025) and the 2025 CDHR are sized by
  arithmetic only; bulletin n° 53 (income 2025) is recorded but unused.
- **The Lean binary** (`frtax`, built 14:19, md5 471dab3c…) was not rebuilt during these runs: both pools ran on the
  same binary (one pass each, 14:57 and 15:17).
- **M inputs**: `V_BTCSGDED` (= 6DE) and, for IM15, `V_NOTRAIT/23` were added to M's input only; a check on
  2 000 returns showed `V_NOTRAIT/23` changes no result.

