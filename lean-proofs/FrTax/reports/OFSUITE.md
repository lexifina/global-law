# The OpenFisca-France test suite through Lean and Mlang (17 November 2026)

OpenFisca-France `refs/openfisca-france`, master at 0fb80f6 (12 November 2026; `git fetch` showed nothing newer, so
no pull), package 177.0.0. Harness: `harness/ofsuite_*.py`; outputs: `runs/ofsuite/` on the build server. Production simulator
answers: `runs/ofsuite/sim.jsonl` (+ `.html/` pages), ids in `runs/ofsuite/sim_idmap.json`.

| Step | Script | Output |
|---|---|---|
| 1. Inventory | `ofsuite_inventory.py` (+ `ofsuite_load.py`) | `inventory.json`, `inventory.txt` |
| 2. Conversion | `ofsuite_convert.py 2019-2025` | `cases.jsonl`, `skipped.json`, `convert.txt` |
| 3. Run and score | `ofsuite_run.py` | `results.jsonl`, `scoreboard.txt` |
| 4. One test in detail | `ofsuite_show.py results.jsonl ID [M vars]` | — |
| 5. Lean regression | `ofsuite_regress.sh before / after` | `regress/{before,after}/` |

## 1. Inventory

843 YAML files, 2,630 tests. A test counts as income tax (IR) when one of its outputs is defined in an income-tax
module of openfisca_france or carries a box (`cerfa_field`): **890 IR tests**, by income year:

| Income years | IR tests | Note |
|---|---|---|
| 2005–2018 | 628 | no M binary; `formulas/irpp.yaml` (119) and `irpp_niches_fiscales.yaml` (104) are all 2010–2014 |
| 2019 | 86 | `cal2019` exists, Lean does not cover 2019: run as a supplement (M only) |
| **2020–2025** | **159** | 84 LexImpact 2024 households, 35 calculator, 22 `formulas/` (16 CSG), 6 micro-entreprise 2025, 2 `impot_revenu/` |
| 2026–2027 | 17 | no M binary |

So the hand-written IR tests the brief expected in 2020–2025 are mostly not there: the hundreds of hand-written ones
are for 2010–2014. In 2020–2025 the bulk is LexImpact's 2024 household cases (gross pay in, IR figures out).

IR output variables in 2020–2025 (tests): rfr 108 (2024: 81), nbptr 100, rni 88, ir_plaf_qf 63, iaidrdi 50,
ip_net 50, impots_directs 50, decote_gain_fiscal 38, impot_revenu_restant_a_payer 33, rbg 21, reductions 19, iai 18,
protection_patrimoine_naturel 11, retraite_imposable 9, ci_investissement_forestier 8, chomage_imposable 7,
microsocial 6, prelevement_forfaitaire_unique_ir 6, salaire_imposable 5, others ≤ 4 (full table:
`runs/ofsuite/inventory.txt`).

## 2. Conversion to boxes

Each test is loaded into an OpenFisca simulation exactly as OpenFisca's test runner does (input, default period,
`max_spiral_loops`, then every expected output computed in the YAML's order), and the boxes are read back from it:
every variable with a `cerfa_field` for the income year (summed over months), the situation flags
(`maries_ou_pacses`, `celibataire_ou_divorce`, `veuf`), the case boxes, the dependant counts OpenFisca derives
(`nbF`, `nbG`, `nbH`, `nbI`, `nbJ`, `nbR`, `nbN`) and birth years. Every box is checked against the aliases of that
year's M source. A test with several tax households becomes one return per household. Tests written with bare boxes
give exactly those boxes ("box" tier); tests written with gross pay give the boxes OpenFisca derives ("derived"
tier: salaries 1AJ, pensions 1AS, exempt value-sharing bonus 1AD).

| 2020–2025 | Tests | Returns |
|---|---|---|
| IR tests | 159 | |
| with an output M or Lean computes | 131 | |
| converted | 126 | **155** (box 42, derived 113; 8 tests hold 37 households) |
| skipped: sets the intermediate `rfr` (taxe d'habitation tests) | 3 | |
| skipped: overseas residence (`depcom_foyer` in Guadeloupe; no box) | 1 | |
| skipped: 7VM/7VN, which the income-2020 form does not have | 1 | |
| no output M or Lean computes (retraite_imposable 9, chomage_imposable 7, ci_investissement_forestier 6 [also in other tests], salaire_imposable 3, dfppce 2, PFU on life insurance 1) | 28 | |

2019 supplement: 86 tests, 82 returns converted (4 set `rfr`).

**Unmapped inputs.** Within 2020–2025 no unmapped input brings in more than one test (depcom_foyer overseas 1;
7VM/7VN 1; rfr set as input 3). The levers are elsewhere: building `cal2015`–`cal2018` (M sources and Mlang drivers
exist) would bring in 278 IR tests; mapping specific credit/reduction outputs (ci_investissement_forestier,
protection_patrimoine_naturel, dfppce: M has the amounts) would score 28 more figures.

**Mapping errors of ours found and fixed during the run** (each changed results):
- OpenFisca's taxable pension depends on the order in which variables are computed: the CSG rate on pensions
  depends on the RFR, a cycle that `max_spiral_loops: 1` cuts. Asking `rfr` first gives 1AS 25,444 for
  `leximpact/2024/celibataire_retraite_1.2_SMIC_d4`; the runner's order (outputs as listed) gives 24,375 and the
  stated RFR. The first pass used the first; boxes are now read after the runner's order (13 retiree tests changed,
  1AS 4–6 % lower, and all 13 now agree). Every converted test now passes in OpenFisca itself (155/155), as
  `openfisca test` also reports.
- `ppe_du_sa` (hours paid, a remnant of the employment bonus ended in 2015) carries `cerfa_field` 1AV, since 2022 the
  tick box of the value-sharing bonus: excluded.
- `hsup` carries 1AU (an old box): mapped to 1GH… (exempt overtime).
- The exempt value-sharing bonus (`prime_partage_valeur_exoneree_exceptionnelle`) has no `cerfa_field`: mapped to
  1AD…, with 1AV… ticked above 3,000 € when the employer has a profit-sharing agreement.
- Output definitions (production pages decide them, §4): reductions compared net of the global-cap clawback
  (M `ITRED − AVFISCOPTER`); `iai` with recaptured reductions (8TF, `IPREP`) added to M's `IAN`; the amount payable
  with CEHR (and CDHR) added to M's `IRN`; OpenFisca's `prelevement_forfaitaire_unique_ir` not compared (M's `IPROP`
  includes every proportional tax: micro-BA/BIC capital gains at 12.8 %, 3PI at 50 %, early PEA closure).

## 3. Scoreboard

A test is "equal" when every comparable stated figure is reproduced within max(test margin, 1 €) (M and Lean round
to the euro; OpenFisca does not); parts to 0.01. M runs with `REGCO/1`, `ANREV/<year>`.

| Income 2020–2025 (155 returns) | Run | Equal to stated value | Differ | Refused | Out of scope | No comparable figure |
|---|---|---|---|---|---|---|
| OpenFisca (current code, on the test's own input) | 155 | 155 | 0 | — | — | — |
| Mlang (`cal<year>`) | 155 | 148 | 6 | 1 | — | — |
| Lean (`frtax`) | 134 | 126 | 5 | 0 | 21 | 3 |

| Income 2019 supplement (82 returns) | Run | Equal | Differ |
|---|---|---|---|
| OpenFisca | 82 | 82 | 0 |
| Mlang (`cal2019`) | 82 | 77 | 5 |
| Lean | — (2019 not modelled) | | |

By figure, 2020–2025 (equal/compared): rfr OpenFisca 127/127, M 121/126, Lean 104/109; rni 87/87, 81/86, 72/77;
nbptr 96/96, 96/96, 90/90; amount payable 60/60, 60/60, 47/47; ip_net and iaidrdi 49/49 for all three;
ir_plaf_qf 63/63, 61/63, 61/63; décote 37/37, 35/37, 35/37; reductions 19/19, M 17/18, Lean 4/4; iai 18/18,
18/18, 8/8; rbg 20/20, M 19/19; CEHR 2/2 each; marginal rate 3/3, M 3/3.

## 4. Disagreements and the production simulator

Asked: 16 requests (14 returns, then 2 of them again with the corrected pension boxes; the 3 answers on the
mis-derived pensions — of04, of06, of07 — are superseded, though there too production = M = Lean), strictly sequential, 1.2 s apart,
under `flock ~/fr/.sim.lock`.

### A. OpenFisca errors that its own tests encode (production = M; Lean = M where in scope)

**A1. JEI/JEIR subscriptions left out for income 2024** (new). `calculateur_impots/yaml/reduc_cappme.yaml#5`
(2024): 5KC 200,000 (BIC), PME/ESUS/SFS subscriptions and carry-forwards, and 7CR 1,000 (JEI, 30 %), 7DZ 500 (JEIR,
50 %). Stated reductions 6,662 (OpenFisca 6,662.5); M 7,213; Lean out of scope; **production: total reductions
7,213, net tax 59,520** (OpenFisca's tax: 60,071, 551 € too much). Cause in OpenFisca: `cappme_jei_jeir`
(art. 199 terdecies-0 A bis and ter, "hors plafonnement global", formula from 2024) is listed in
`reductions_deplafonnees` only in its `formula_2025_01_01`; the 2013 formula used for income 2024 omits it, so the
reduction (550 €: 1,000 × 30 % + 500 × 50 %) is lost for 2024. M computes it in `RPMEJEI` (chap-4.m). The test,
whose values are said to be read off the DGFiP calculator, is wrong for 2024.

**A2. Art. 157 bis for a couple counted once** (F4; first production verdicts). OpenFisca gives a couple in which
both spouses are over 65 one allowance, not two.
- `leximpact/2024/aspa_02_couple_retraites_1pension_moyenne_1_sans_pension` (2024): 1AS 18,739, 0AM, born 1946 and
  1944. Stated RFR/RNI 14,068.96 = OpenFisca; M 11,273; Lean 11,273; **production RFR and RNI 11,273**
  (16,865 − 2 × 2,796).
- `leximpact/2024/02_couple_retraites_pension_1.33_SMIC_d2` (2024): 1AS 13,598, 1BS 13,598, born 1946 and 1944.
  Stated RNI 23,077.82 (gross tax 9.22, décote 9) = OpenFisca; M 21,680; Lean 21,680; **production RNI 21,680, gross tax 0** (24,476 − 2 × 1,398).
- `leximpact/2024/Z_couple_retraites_pension_1.5_SMIC_d3` (2024): 1AS 15,234 each. Stated RNI 26,024.31, gross tax
  333.33, décote 333 = OpenFisca; M and Lean RNI 24,626, gross tax and décote 180; **production RNI 24,626, gross tax 180, décote 180**.

**A3. Forestry credit, income 2019.** `calculateur_impots/yaml/credit_invest_forestier.yaml#4`: 1AJ 50,000 and 24
forestry boxes. Stated amount payable 5,857 = OpenFisca; M 5,864; **production 5,864**. RESULTS row 14 counts this
as M's one failure ("40/41"): production says M is right and the calculator-read test value is not.

**A4. Half-parts W and S without the age condition, income 2019.** `impot_revenu/nombre_de_parts/`
`celibataire_ou_divorce.yaml#2` and `veufs.yaml#2` (0AV, 0AW, born 1970: stated 1.5 parts),
`maries_ou_pacses.yaml#3` (0AO, 0AS, both born 1970: stated 2.5). M 1, 2, 1; **production 1, 2, 1**. Art. 195, 1, f
and 195, 6 require the person to be over 74 (FINDINGS L); the tests give no birth date, so OpenFisca's default
1970 applies and OpenFisca ignores the age.

### B. M (as run by Mlang) refuses a return production computes

`calculateur_impots/yaml/reduc_cappme.yaml#3` (2022): 5KC 200,000 and 17 PME/ESUS/SFS boxes (7BS, 7BT, 7CA, 7CH,
7CI, 7CR, 7CS, 7CT, 7CV, 7CX, 7CY, 7DC, 7DY, 7EY, 7FY, 7GW, 7GY). Mlang 2022: anomaly DD27. **Production
computes it: reductions 2,500 = stated = OpenFisca, net tax 65,691.** Same family as the M refusals in FINDINGS F7
and P; Lean out of scope (7xx subscription boxes).

### C. Lean differences

None. On all 134 returns in Lean's scope that M computes, Lean equals M on every figure compared (parts, RNI, RFR,
tax after décote, décote, reductions, net tax, CEHR), so Lean's 5 "differ" are A2 (3) and D (2). The deliberate
statute readings F1, F2 and F5 are not exercised by any converted test (the returns hold no union dues with overtime
between 5,000 and 7,500 €, no flat-levy income above the CEHR threshold, and no M/Lean difference of the F5 kind
appeared).

### D. Rounding: not a disagreement of substance

`leximpact/2024/Z_couple_marie_salaries_secteur_prive_1.3_smic_chacun_2_enfants_d4` (2024): OpenFisca derives 1AJ
22,605.49 each; the return holds whole euros (22,605). Stated RFR 40,689.95 = OpenFisca (no rounding); M and Lean
40,688; **production 40,688** on the same boxes. Same with `..._3.2_smic_2_enfants_d5` (50,079.23 vs 50,078). The
2 € are the box rounding plus the rounding of each 10 % allowance (art. 193 and 1657, F4).

### E. Definitions, not disagreements (production pages show which line is which)

- `reduc_locmeu_plafonnee.yaml#5` (2020): stated reductions 10,000 (after the art. 200-0 A cap); production prints
  "Total des réductions d'impôt" 10,632 and the same net tax as M (32,232). Scored on M's `ITRED − AVFISCOPTER`.
- `reduc_credit_2042pro.yaml#5` (2020) and `#4` (2019): stated `iai` 45,369 / 45,397 = production's "Droits simples";
  production's "Impôt avant crédits" 46,069 / 46,097 adds the recaptures (8TF, 8TP …); M's `IAN` (44,869 / 44,397)
  is after non-refundable credits. The net tax is the same everywhere (41,169 / 40,397). For 2020 `IAN + IPREP`
  equals the stated figure; for 2019 it stays 500 € off (a second recapture box): counted as a mapping residue, not
  as a disagreement.
- 2019 PFU: OpenFisca's `prelevement_forfaitaire_unique_ir` (12.8 % only) against M's `IPROP` (all proportional
  taxes) — the totals agree; no longer compared.
- `pfu_bareme.yaml#4/#5` (2019): the amount payable includes the CEHR (4,200 €) in OpenFisca, not in M's `IRN`.

## 5. Lean's scope and the change made

**Out of scope before the change (2020–2025): 26 returns** (after the mapping fixes): 19 calculator tests that
each fill 10–60 reduction/credit boxes (PME/ESUS/SFS subscriptions 7BS–7GY and carry-forwards 7CY–7GY: 4 tests
each; the 8xx business credits; overseas investment HAA–HZZ; furnished rentals 7OU–7PZ; 7NA/7NB …), the 2 PFU tests
of 2020 (2GO, 2TQ, 2TT, 2TZ), and the 6 value-sharing-bonus households (1AD, 1AV). One box that would bring the
most in: 1AD (6 returns); next, the 2GO/2TQ/2TT/2TZ group (2); everything else needs a whole family of reductions
with the art. 200-0 A cap (the PME/ESUS family would bring 4).

Already in the model (checked first): micro-foncier 4BE, rental income and deficits 4BA–4BD, micro-BIC/BNC
5KO/5KP/5HQ…, pension allowance 1AS…, exempt and taxable overtime.

**Change: the exempt value-sharing bonus (1AD…1FD, 1AV…1FV), income 2022 onward.** `lean/FrTax/Income.lean`
(`ppvBox`, `ppvTick`, `ppvLimit`, `ppvExempt`, `taxablePpv`, `exemptShare`, `ppvForRfr`; `grossSalary` adds the
taxable excess; `overtimeForRfr` now shares `exemptShare`, whose 10 % allowance base also includes the exempt bonus)
and `lean/FrTax/Liquidation.lean` (`rfr` adds `ppvForRfr`); scope: `harness/of_calc_tests.py` `LEAN_BOXES` + 1AD…1FD,
1AV…1FV. Statute (not codified in the CGI; text read via global-law, france/national/acts, as in force on
31 December 2023; official text JORFTEXT000048480565): loi n° 2022-1158 du 16 août 2022, art. 1, V (limit
"3 000 € par bénéficiaire et par année civile", "portée à 6 000 €" with a profit-sharing scheme), VI (exempt from
income tax when paid 1 July 2022 – 31 December 2023 to employees under three SMIC), VI bis (2024–2026, employers
under 50 employees), VI quater ("incluses dans le montant du revenu fiscal de référence défini au 1° du IV de
l'article 1417 du code général des impôts"). Reading, as for exempt overtime and as M (XPRIMV, chap-87.m): the RFR
takes the exempt bonus net of its share of the 10 % allowance; the amount above the limit is taxable salary
(COD1ADRET).

Effect on the suite: the 6 bonus households come into scope and Lean equals the stated value on all 6 (e.g.
1AJ 19,682, 1AD 3,000, 2023: RNI 17,714, RFR 20,414 = OpenFisca 20,414.16 = M; net tax 152 for a stated 153, inside the
1 € tolerance, M also 152); out of scope 26 → 21 (the 21 also
reflect the 1AV mapping fix).

**Regression, before → after** (`ofsuite_regress.sh`; binary 12:22:53 → 12:31:45; the other agent's Withholding
changes were in the build both times):

| Benchmark | Before | After |
|---|---|---|
| 100,000 random households 2024–2025 (gen.py seed 2026; 98,885 accepted by M) | 98,866 all 12 figures equal | 98,866 (Lean outputs byte-identical) |
| 20,000 random households 2020–2023 (gen.py seed 2027; 19,719 accepted) | 19,709 | 19,709 |
| Official worked examples | Lean 43/47, M 44/57 | 43/47, 44/57 |
| OpenFisca calculator tests (of_calc_tests.py) | Lean 8/8 pass, M as before | same |
| Production verdicts, targeted returns (371, saved pages) | Lean 301/353, M 285/292 | 301/353, 285/292 |
| Production verdicts, family structures (126) | Lean 39/39, M 30/30 | 39/39, 30/30 |

The 100k sample differs from the one in RESULTS row 7 (98,885 accepted, not 98,868: gen.py has changed since), so
the absolute numbers are not RESULTS's; before and after use the same inputs. The 19 and 10 remaining differences
were not reclassified here.

## Not done

- Income years before 2019 (628 IR tests): no M binary; `cal2015`–`cal2018` could be built (sources and drivers
  exist) — not attempted.
- 2019 returns were not re-dated to 2020 for Lean.
- No Lean coverage of the PME/ESUS/SFS reduction family or the 8xx business credits (the 19 calculator tests).
