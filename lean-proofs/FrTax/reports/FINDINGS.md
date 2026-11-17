# French income tax: Lean model vs Mlang (M code of the DGFiP) — findings

Each finding: what the statute says, what M (DGFiP source) does, who is affected, evidence.

## F1. Union-dues credit: M kept the old 5 000 € overtime limit for three years (income 2022–2024)
- CGI art. 199 quater C: credit = 66 % of union dues within 1 % "du montant du revenu brut désigné à l'article 83".
- CGI art. 81 quater, I: overtime pay exempt "dans une limite annuelle égale à 7 500 €" (loi n° 2022-1157 du 16 août 2022,
  from income 2022; it was 5 000 € for income 2021, 7 500 € for 2020 under loi n° 2020-473).
- M (ir-calcul, chap-3.m, SOMBCOSV): adds `max(0, COD1GH - LIM5000)` to the base in sources 2021, 2022, 2023 and
  2024; `LIM7500` in 2020; `COD1GHRET` (= overtime above 7 500 €) in 2025. So for income 2022–2024 M counts exempt
  overtime between 5 000 € and 7 500 € in the 1 % base.
- Effect: up to 66 % × 1 % × 2 500 € = 16.50 € too much credit per person (declarant with exempt overtime between
  5 000 € and 7 500 € and union dues above 1 % of salary). Probe (2024): 1AJ 10 908, 7AC 900: credit 72 € with
  1GH ≤ 5 000, 79 € at 6 000, 85 € at 7 000, 88 € at 7 500. Fixed in the 2025 code (82 € only at 9 000).

## F2. CEHR scaled down when micro-entrepreneur flat-levy income is present (no statutory basis found)
- CGI art. 223 sexies, I, 1: the CEHR is computed on the revenu fiscal de référence of art. 1417, IV, 1°, which
  includes income under the flat levy of art. 151-0 (1417, IV, 1°, c, "retenus pour leur montant diminué ... de
  l'abattement"). No rule scales it.
- M (chap-thr.m, CHRAPRES): when the effective-rate indicator INDTEFF is set (which flat-levy income triggers),
  CHRAPRES = CHRTEFF, the CEHR on the whole RFR times (RFR without the flat-levy income ÷ RFR). Probe 2024: 1AJ
  900 000, 5TB 25 455: RFR 898 301, CEHR by art. 223 sexies 23 432 €, M 23 100 € (= 23 432 × 885 574 / 898 301).
- BOFiP describes an effective-rate CEHR for income exempted by a tax treaty; we found none for flat-levy income,
  which is French income taxed by a levy that discharges the income tax only.
- Effect: high earners (RFR above 250 000 € / 500 000 €) who are also micro-entrepreneurs under the flat levy pay
  CEHR (and so, in 2025, CDHR) on less than the statute's base; in random returns, 8 of 29 636.
- Status: open reading question, not asserted as an error.

## R. Readings where the statute is silent and the Lean model follows M (not findings)
- Actual expenses smaller than the 10 % allowance: M keeps the allowance (art. 83, 3°: an option).
- RFR overtime: net of its share of the 10 % allowance, cut to the cent then rounded (art. 1417, IV "montant net").
- CSG and CRDS rounded together; investment and property CSG rounded apart in 2025 (art. 1657, 1).
- QF cap rounded per amount (half parts and quarter parts: 895.50 € -> 896 €); décote rounded on the difference.
- Effective rate (art. 197 C): décote applied after the scaling; art. 157 bis tested on the total income.
- 61 € threshold on income tax and CEHR together; credits imputed on a tax under 61 € before refunding the excess.

## F3. DGFiP brochure pratique: printed thresholds that neither the statute nor the M code gives
- Tableau 7 ("Seuils de mise en recouvrement", the taxable income below which the tax is under 61 €): edition 2025
  (income 2024) all 20 cells 9 € too high; edition 2026 (income 2025) the couples' row (9 cells) 9 € too high and
  4.5 parts printed 62 869 € for 61 860 €. The single-person row of 2026 is right. Every cell is a theorem in
  lean/FrTax/Brochure67.lean (first income reaching 61 €, and the euro before it).
- Tableau 6 ("Seuils d'imposition"): all 40 cells right.
- Tableau 4 ("Premier revenu imposable plafonné"): 57 of 84 cells 1–9 € from what Lean and Mlang both give
  (harness/thresholds.py, runs/thresholds.json); rows with an invalidity/veteran half part or a widow(er)'s part
  print the income where the tax first exceeds the uncapped tax after the complementary reduction (hence 170 604 €).
- Mayotte (cyclone Chido) gifts: the brochure states both "du 14.12 au 31.12.2024 ... (maximum 2 000 €)" and
  "du 17.12 ... (maximum 1 000 €)"; M applies 2 000 €.

## F4. OpenFisca-France 177.0.0 (commit 0fb80f6)
- abat_spe (ir.py:3661): `foyers_eligibles = (declarant eligible) + (spouse eligible)` adds two numpy boolean arrays,
  which is a logical OR: a couple who both qualify get one art. 157 bis allowance, not two (minimal case: both 87,
  pension 7 226 €: abat_spe 2 796 € vs 5 592 €).
- rfr: exempt overtime (art. 81 quater) not added (art. 1417, IV, 1°, c).
- Age taken on 1 January (period.first_month) rather than "au 31 décembre de l'année d'imposition".
- Amounts not rounded to the euro (art. 193, 1657).
- Like for like on 5 fields (parts, RNG, RNI, RFR, net income tax without CEHR/CDHR): 73.7 % (2024), 71.8 % (2025)
  of 3 000 households each match M; Lean 100 %.
- Production verdict on abat_spe (OFSUITE.md): three LexImpact 2024 tests whose stated values follow OpenFisca
  (taxable income 14 068.96 / 23 077.82 / 26 024.31); production gives 11 273 / 21 680 / 24 626, which are M and Lean.
  The suite's expected values carry the bug.

## F8. OpenFisca-France: the 2024 young-innovative-company reduction is left out (OFSUITE.md)
- `cappme_jei_jeir` is counted in `reductions_deplafonnees` only from 2025. In `reduc_cappme.yaml#5` (income 2024)
  OpenFisca and the test state 6 662 € of reductions; M gives 7 213 €; production 7 213 € (net tax 59 520 €).
  OpenFisca charges 551 € too much, and the test, said to be read off the DGFiP calculator, has the wrong value.
- 2019 forestry credit (`calculateur_impots`): production gives 5 864 €, M's value, not the stated 5 857 €.
- 2019 half-parts W/S given without a birth date: the tests state 1.5 / 2.5 / 1.5 parts; M and production 1 / 2 / 1
  (art. 195, 1, f and 6 require "plus de 74 ans").

## F5. M rounds amounts ending in .49995–.49999 up (a floating-point safety margin)
- CGI art. 193 and 1657, 1: amounts are rounded "à l'euro le plus proche ; la fraction d'euro égale à 0,50 est
  comptée pour 1" — so 0.49996 goes down.
- Mlang's C backend (src/mlang/backend_compilers/dgfip_gen_files.ml:629): `my_arr(a) = floor(a + 0.5 + EPSILON*50)`
  with EPSILON = 0.000001 (the build's comparison_error_margin): any fraction in [0.49995, 0.5) is rounded up.
  The interpreter's my_arr (validator.ml) rounds to 5 decimals first, with the same effect.
- Where it bites: any rounded ratio, e.g. the effective rate of art. 197 C (tax on all income × taxable income ÷
  all income). harness/eps_search.py finds such returns directly: 24 found (12 per year), all of them single
  salaried people with flat-levy services income (5TB); on every one M's gross tax is 1 € higher than exact rounding
  and the net tax 1–2 € higher (the décote shrinks too). Lean, with exact rational arithmetic, rounds them down.

## F6. Mlang's driver for income 2020 and 2021 caps refundable credits as if they were tax advantages
- Arbiter: the DGFiP's production simulator, still served for earlier years (calc-2021.cgi = income 2020 …
  calc-2026.cgi = income 2025).
- Household: single, salary 17 174 €, dividends 212 152 €, interest 147 €, 12.8 % withheld at source (2CK 27 174 €).
  Production: net income tax 79 € (2020), 47 € (2021). Lean: 79 €, 47 €. Mlang: 628 € in both years.
- Cause: the plafonnement global des niches (art. 200-0 A) needs a first, "theoretical" pass of the calculation
  without advantages (V_INDTEO = 1) to set V_IRETEO, V_IAD11TEO, V_INETEO. Mlang's hand-written driver for the 2020
  and 2021 M code (m_ext/2020/cibles.m, calcule_avfiscal) runs that pass only when a box with the avfisc attribute
  is present; otherwise V_IRETEO stays 0, AVFISCO = IARTEO − IARAF counts the refundable 2CK credit as a 27 095 €
  "advantage", and the cap (LIMIT9 26 546 €) claws back 549 €. The 2022+ driver adds `est_code_supp_avfisc` and
  always runs the pass. The M rules are the same in both eras; the bug is in the reconstruction of the driver.
- In 20 000 random households for 2020–2023, these are the only 7 where Lean and Mlang still differ.

## F7. What M (as run by Mlang) accepts or refuses differs from production
- Actual expenses above salary (1AK > 1AJ): production nets the excess against other income in every year
  (2020–2024 tested: 1AJ 21 036, 1AK 21 175, interest 449 → taxable income 279). Mlang 2020/2021 does the same;
  Mlang 2022+ refuses the return (anomaly IM2001). The Lean model capped the expenses at the salary: fixed.
- 3VG (net gains) with 3VH (net losses): production refuses ("incompatibilité entre 3VH et 3VG"); Mlang 2022+
  refuses (A320); Mlang 2020/2021 computes, ignoring 3VH. The generator no longer emits both.
- 7UJ for income 2020 (the box was created for income 2021): production ignores it; Mlang 2020 returns an empty
  result (no parts, no KO line). The Lean model had put it in the 66 % pool: fixed.
- Earlier M versions need the income year as an input (ANREV) to compute ages; without it 2020–2021 returns lost the
  art. 157 bis allowance and the 0AW/0AS half-parts. Harness fixed.
- OpenFisca suite: Mlang 2022 refuses one test return (anomaly DD27) that production computes (reductions 2 500 €,
  as stated).

## W. Withholding-tax rates (prélèvement à la source, art. 204 H and 204 M) — PAS.md
Lean models the household rate (204 H I/II), the couples' individualised rates (204 M) and the 18 default grids
(204 H III, rate years 2021–2026, 3 zones) in lean/FrTax/Withholding.lean. Production (calc-2021 … 2026 prints the
household rate and its detail; individualised rates for income 2024–2025 only) = M on 318/318 household rates and
53/53 individualised rates. Lean = production on 251/323. Every Lean/M difference is in one class below, and in each
class production can judge it sides with M.
- W1, tax under 61 €: M and production give a nil rate when the tax after décote is under 61 €. Art. 204 H has no
  such rule; the 61 € threshold is art. 1657 (collection). E.g. income 2020, single, salary 16 695 €, tax 11 €:
  statute 0.1 %, M and production 0.0 %. The commonest class in random households (105 of 19 748; 633 of 98 868).
- W2, rounding margin (income 2020–2024): F5 again. 29 296 / 115 112 = 25.44996 %: art. 204 H, I, 3 gives 25.4 %,
  M and production 25.5 % (30/30). The income-2025 code truncates first; the effect is gone.
- W3, the 204 H, II zero-rate threshold: **Lean error, fixed** (AUTHORITY.md). The statute indexes the threshold
  every year; the codified figure is updated a year late by decree. M, production and every BOFiP version
  (BOI-IR-PAS-20-20-10, 2020–2026) use the indexed figures 25 705 / 26 065 / 27 473 / 28 792 / 29 310 / 29 574 €.
  Lean now does too: production 251 → 269/323 household rates (threshold family 30/30); regressions identical.
- W4, décote in the couple rates: M and production apply the single-person décote; art. 197, I, 4 as referred to by
  204 M points to the couples' décote. 9 360 of 36 779 random couples differ; production sides with the single-person
  reading on the 17 couples where only this reading differs (the other 7 of 24 are W1/W5 cases).
- W5, quarter-part cap in couple rates (2.5 parts): M rounds that cap together with the tax in the 2020–2024 code and
  on its own in 2025; production follows each year's program (5/5, income 2024). Lean rounds it on its own.
- W6, a wrong bound in M's grid: M's income-2025 default grid for dependants has 8 739 € where loi n° 2026-103 has
  8 789 € (chap-taux.m 627–628); a monthly base of 8 746 € is charged 24 % (2 099 €) instead of 20 % (1 749 €).
  Production does not print dependants' acomptes: no arbiter, a departure from the printed statute.
- Grids: Lean 720/720 probes = statute; M 701/702 cells (W6); BOFiP BOI-BAREME-000037 (2025) = statute 57/57.
- Lean keeps the statute's reading in W1–W5; variants TXFOYER61 and TXDEC1S/TXDEC2S reproduce production.
- Theorems (kernel-checked, standard axioms only): every grid has 19 strictly increasing bounds; the default rate is
  monotone, ≤ 43 %, nil below the first bound; the computed rate is ≥ 0, monotone in the tax, and bounded by the share.
- OpenFisca-France has no withholding-rate variable (commit 0fb80f6).

## P. The production simulator as arbiter (DGFiP, calc-2021 … calc-2026 = income 2020 … 2025)
Runs: runs/sim_targets_v2.jsonl (371 targeted returns), runs/sim_fam.jsonl (126 family structures); scored by
harness/sim_compare2.py (reports runs/sim_targets_report.txt, runs/sim_fam_report.txt; raw pages saved since the
label fix in <run>.html/).
- F1 (union-dues credit, 5 000 € overtime limit, income 2022–2024): production = M. The deviation from the statute is
  in what taxpayers are charged (here in their favour: refunds of 79–88 € where the statute gives 72 €).
- F2 (CEHR with flat-levy income): production = M on all 22 returns. M prorates the CEHR by
  (RFR − flat-levy base + taxable income) / RFR whenever the effective-rate rule applies (CHRTEFF, chap-thr.m:82);
  art. 223 sexies taxes the RFR, flat-levy income included, with no such proration. Production charges 1.4–2.3 % less
  CEHR than the statute (e.g. 23 100 € for 23 432 €). Lean keeps the statute.
- F5 (rounding margin .49995–.49999): production = M on all 24: production rounds up where art. 193/1657 round down
  (1–2 € more tax). Lean keeps the statute.
- F6 (Mlang's 2020/2021 driver): production = Lean on all 7 (e.g. 79 €, not 628 €).
- Returns M refuses (anomalies DD22, I00101, IM15, IM2001, IM2102, IM3001, IM3002, and I011/I012 = S or W under 74):
  production computes them; Lean equals production on every one (three show a global deficit, which production prints
  and Lean does not model; the tax is equal). A01007 and A320 are refused by both.
- Family structures: of 126 returns, production refused 87; Mlang 2020/2021 computed 60 of those (that driver runs
  no input controls: 0 of 30 000 random family returns refused, against ~40 % for 2022+).

## L. Lean corrections made because of these tests (each now equal to production)
- Actual expenses above the salary: a deficit set against other income (art. 156, I); no cap at the salary.
- 7UJ for income 2020: ignored (the box did not exist).
- Box T (art. 194, II) only for "célibataires ou divorcés": not for a widow(er).
- Boxes S (art. 195, 6) and W (art. 195, 1, f) need a person over 74 (born in year − 74 or before, as M).
- Box L (art. 195, 1, a, b, e: "vivent seuls") is cancelled by box N.
- Reporting only: gross tax under art. 197 C reported after the effective-rate scaling.
- Extension (not a correction): the exempt value-sharing bonus, boxes 1AD…1FD and the 1AV… ticks, from income 2022
  (loi n° 2022-1158, art. 1, V, VI, VI bis, VI quater). Regressions identical before and after (OFSUITE.md).

## A. What the authorities say (AUTHORITY.md: BOFiP in force + archives, 1.75 M administrative decisions, AN 2017–2026 and Sénat 1978–2026 written questions)
- F1 union dues: unaddressed by any authority; the DGFiP's 2025 code switched to 7 500 € (a three-year lag, earlier years not corrected).
- F2 CEHR proration: CE 10 juillet 2019 n° 412624 and TA Paris 29 janvier 2026 n° 2316179 uphold proration only for
  treaty-exempt income ("lorsque la convention le permet"); BOI-IR-CHR § 40, 50, 280 put flat-levy income in the base.
  Supports Lean, more firmly than before: a treaty device applied where no treaty applies.
- F5, W2 rounding: BOI-IR-LIQ-20-20-40 § 50 and BOI-IR-PAS-20-20-10 § 20 state the plain rule: a technical margin in M.
- W1 61 € in the rate: BOI-IR-PAS-20-20-10 uses 1657 only in the 204 H II test (§ 150); BOI-IR-LIQ-20-20-40 § 90 "ne
  constitue pas une exonération"; AN 15e n° 4893 (JO 13/11/2018). Supports Lean.
- W4 couples' décote: BOI-IR-PAS-20-20-20 § 140 examples and AN n° 17510 (JO 31/12/2019), AN 16e n° 13 (JO 17/01/2023)
  use the single-person décote. For M; only the literal words of art. 197 I 4 a support the couples' décote. Disputed
  reading, no court. Lean keeps both outputs (default: literal; decision pending with the user).
- W5: BOFiP example 3 rounds the cap on its own (= Lean, = M 2025). W6: BOI-BAREME-000037-20260706 prints 8 789 € (= statute).
- W3: against Lean (see W above, fixed).
- All W points: the rate only sets advance payments; the tax due is unchanged (TA Poitiers 7/11/2023 n° 2200177).

## H. The DGFiP's correction history (HISTORY.md)
- Public releases: one per income year 2010–2025 (Adullact ir-calcul, 31 commits; mirrors add nothing), except 2018
  (6.3 and 6.7). No within-year pair for 2020–2025, so "would Lean have caught their fixes" cannot be tested there.
- 2018 6.3 → 6.7: real fixes, e.g. 8ZZ income left out of the CIMR base (salary 30 000 + 8ZZ 5 000: tax 0 → 594 €);
  production calc-2019 still gives the 6.3 answer. A loss carry-forward double count (art. 156 I 8°) also fixed.
- Across years: the 2025 code moves F1, W2, W5 in Lean's direction; earlier years not corrected; F2 still prorated in 2025.

## Q. Loopholes (LOOPHOLES.md; 121 M Lean evaluations, 24 production returns, 18 theorems in lean/FrTax/Loopholes.lean)
- Novel in the sources checked: 101.1 % marginal rate in the 2025 CDHR smoothing band (single ~298–330 k€ dividends,
  couple ~615–660 k€; production 97 050 → 98 061 € for +1 000 €); a 75 % gift smaller than a 61–239 € tax makes it
  uncollected (proved for every case); +1 € flat-levy turnover → −62 € tax (curiosity).
- Known, recreated: CDHR neutralises unlisted reductions/credits in 2025 (`cdhr_neutral`, general); attach vs alimony
  (≤ 1 004 € / ≤ 1 557 €); flat tax vs 2OP; separation bonus with shared residence (≤ 4 910 €; sham = fraud); 61 €
  notches; 157 bis cliff (≤ 226 € for 1 €); 14 known items in all.
- Proof strength: 5 kernel-only (decide/omega), 13 with native_decide (HashMap/String.hash opaque to the kernel).

## N. National population (POPULATION.md; 250 k households per year calibrated to 360 published margins)
- Lean and M give the same national net tax within 0.03 % (2024: 112.92 vs 112.95 Md€); both exceed the published
  91.72 Md€ by 23 %, almost all in the top decile (flat-tax vs scale split not published) plus ~6.7 Md€ of reductions in
  unmodelled boxes. Deciles 6–9 within 2 %.
- Scale (estimates): F1 10–50 k households, 0.1–0.9 M€/yr; F2 4–13 k, 0.2–1 M€; W1 0.36–0.38 M, ~14 M€ timing; W4 2.14 M
  couples, ~0.83 Md€ moved between partners; OpenFisca RFR w/o overtime 11.8 M households, 21.8 Md€ of RFR; F8 ≤ 12.4 k,
  ≤ 34 M€; F4 52 k taxed couples, ≤ 9 M€.
- Two Lean errors found and fixed (FIX_2AB_6GP.md; statute, BOFiP, M and production agree): 2AB credit refunded by Lean, offset only by M (art. 199 ter; 177 k, 29 M€);
  6GP (and 6GI/6GJ) alimony counted at 125 % (art. 158, 7, 3°) (6.5–11.5 k, 1–2.5 M€). After the fix Lean − M = +0.57 M€ (2024), differing households 200 k → 16 k.

## I. Other implementations (CATALA.md, IMPLEMENTATIONS.md)
- Catala (DGFiP + Inria PoC, parts and income categories 2022–23): own tests 54/54; vs production parts 191/209 (Lean
  195/195, M 180/180), RBG 83/86. Errors confirmed by production: pension allowance per kind not per pensioner (art. 158,
  5, a), 0CR, widow with shared-residence children, G without invalidity, P/F with S no-cumulation never fires; scope gaps
  (no ages: W/S; no box N); 0DJ attached adults: literal 196 B vs production (disputed). No Lean error found.
- Publicodes modele-social 11.1.0: widow + QF cap gives no benefit to the extra part (93 100 € 2024: 20 325 vs 14 750 €;
  2 839 brochure cells); no rounding; no 157 bis. Random in scope 89.4 % exact.
- INES 2024.1 (R): 85 % exact on random; RFR 72 %; production-confirmed errors: widow with all children in shared
  custody, W with T, invalidity complementary reduction +760 €, 2020 overtime cap 5 000 €, 157 bis band at 17 510 €,
  actual expenses capped at salary, three RFR errors.
- EUROMOD FR: tax stage only; décote from the wrong base (i_tingt1), single parent's first-child cap doubled.
- Not run: LexImpact, TAXIPP (OpenFisca), 2016 Python translations (income 2014), PolicyEngine (no France).

## C. Court decisions as test cases (COURTS.md)
- 1,748,519 administrative decisions → 5,361 IR computation disputes with a figure → 1,020 read → 76 usable (1 complete
  return: TA Poitiers 7/11/2023 n° 2200177, income 2021, all 6 figures reproduced by Lean, M and production).
- Scores on 86 figures: Lean 72/73, M 82/85, production 22/23; parts 53/53 for Lean and M. No Lean error.
- Court readings differing from programs: TA Nantes n° 2004003 (gift 20 % limit base); TA Lyon n° 2304314 (same child
  attached and alimony — the form cannot express it); courts in conflict on art. 195 1 f (TA Besançon n° 2200884 vs TA
  Nantes n° 2103500); several court capital-gain arithmetic slips (CAA Versailles 23VE00322, CAA Lyon 23LY01245, 23LY03190).

## X. Penalties and interest (PENALTIES.md; lean/FrTax/Penalties.lean, 17 kernel-checked theorems)
- M computes penalties in correctif mode; OpenFisca none (only the 2025 CDHR instalment penalty).
- Lean: BOFiP/official examples 22/23 (the miss: a 2013 BOFiP example vs art. 1758 A); vs M 59/70 (M ignores some
  codes on salaries; layer order where statute silent; M drops the 1758 A 10 % within the 1/20 interest tolerance);
  court figures 33/47 exact, 38 within 2 €; courts keep the administration's figure when lower than the statute's.
