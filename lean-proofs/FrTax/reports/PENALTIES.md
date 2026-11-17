# Penalties and late-payment interest on the income tax: Lean, M, OpenFisca, the BOFiP and the courts (17 November 2026)

Question: what the DGFiP charges when a return is late, wrong or unpaid, why, and how much; which implementations
compute it; whether they agree with the statute, the DGFiP's own worked examples and the figures stated in court
decisions. Work on the build server in `~/fr`; files listed at the end. The production simulator has no penalties and was not used.

## 1. Summary

| Benchmark | Result |
|---|---|
| Lean `lean/FrTax/Penalties.lean`: interest (art. 1727, both rates, reliefs of 1727 V and L62, tolerance of a twentieth), majorations (1728, 1729, 1729 A strata and late-return rule, 1728 4 split, 1732, 1758 A), 1730, 1729 G | builds; 17 theorems, axioms `propext`, `Quot.sound` (one also `Classical.choice`); no `native_decide`; 6 worked examples checked by `decide` |
| BOFiP and official worked examples (23 stated figures) | **22/23**; the 1 is the statute reading (art. 1758 A) of a good-faith layer the BOFiP example shows at 0 % |
| Lean vs M correctif mode (70 constructed cases, income 2022–2024) | **59/70** equal on months, interest and majorations; 5 codes M does not apply to a salary box; 3 cases where M puts a no-interest layer under the penalised one; 3 cases where M drops the 1758 A 10 % inside the tolerance of a twentieth |
| Court decisions stating base and figure (47 figures from 20 decisions, read by hand from 177 candidates) | **33/47** exact, **38/47** within 2 €; the 9 others all state *less* than the statute's arithmetic on the stated base (part of the rights not bearing interest, facts not in the decision) |
| Penalty outcomes in 20 000 income-tax decisions | 676 operative parts discharge or reduce a penalty on its own; reasons found: burden of proof not met 213, substitution of a lower rate 114, remise/dégrèvement 62, motivation 46 (heuristic, see §6) |
| OpenFisca-France | no interest or majoration at all; one penalty parameter, the 20 % on an underpaid CDHR instalment (2025) |

## 2. The rules (CGI as in force 2018–2026; france-law record, `refs/france-law`; LPF L62 from the global-law record)

| Rule | Text | Lean |
|---|---|---|
| Interest, rate | art. 1727 III: 0,40 %/month, **0,20 %/month for interest running from 1 Jan 2018** (loi 2017-1775 art. 55; made permanent by loi 2020-1721 art. 68, BOI-DAE-20-10 § 90) | `rateSum`: 40 or 20 hundredths of a % per month |
| Interest, period | 1727 IV 1: income tax from **1 July N+1**; cessation cases first day of the 4th month after the deadline; IV 3 (with 1728): stops at the month of filing or of the proposition; IV 4 (with 1729): month of the proposition de rectification; IV 2: stops when 1730 applies | `irStart`, `cessationStart`, `months` (both ends inclusive) |
| Tolerance | 1727 II 4: none, except deliberate failure, when the insufficiency ≤ 1/20 of the base (income tax) | `tolerance` |
| Mention expresse | 1727 II 1 and 2: no interest on items explained on the return | layer flag `n` in the runner |
| Droit à l'erreur | 1727 V (ESSOC, loi 2018-727 art. 5; rectifying returns filed from 11 Aug 2018): interest **halved** for a spontaneous rectifying return paid with it; LPF L62: during a control, **70 %** of the interest | `Relief.spontaneous`, `Relief.l62` |
| Late or missing return | 1728 1: 10 % (no notice, or filed within 30 days of a formal notice), **40 %** (not within 30 days), **80 %** (occult activity); for the income tax **1758 A replaces 1728 1 a**: 10 %, **20 %** if filed within 30 days of a notice | `rate1728`, `lateFailure`, `Failure` |
| Insufficiencies | 1758 A: **10 % on a good-faith insufficiency** not corrected spontaneously or within 30 days of a request; 1729: **40 %** manquement délibéré, **80 %** abus de droit (40 % if not main initiator/beneficiary), **80 %** manœuvres frauduleuses; 1732: **100 %** opposition to a control | `Failure.rate` |
| Several rates | 1729 A 1: layers added "en suivant l'ordre décroissant des différents taux"; 1729 A 2: late return + reassessments: late rate on all, a higher 1729 rate replaces it on the reassessment rights; 1728 4: categorical late returns split pro rata | `strata`, `majoByRate`, `lateWithReassessment`, `lateSplit` |
| Late payment | 1730: 10 % of sums in a roll unpaid 45 days after collection, never before 15 September for the current year's tax | `latePayment` |
| Withholding | 1729 G (income 2019 on): 10 % for late instalments and for a downward modulation more than 10 % short; when more than 30 % short, half the shortfall in % | `modulationRate`, `modulationMajo` |
| Others relevant to income tax | 1729-0 A (80 %, undeclared foreign accounts, assets, crypto), 1758 (40 %/80 % for foreign transfers and illicit income), 1736 and 1766 amendes, 1731 bis (no deficit or reduction against rights carrying ≥ 40 %) | rates only, in the `Failure` comments; not modelled further |
| Rounding | 1657 1: "Il en est de même du montant des majorations": half up to the euro | `majo`, `interest` use `rnd` |

## 3. Implementations

**M (DGFiP).** M computes penalties, in the *correctif* (rectification) chain, not in the primitif runs every other
benchmark uses. `chap-inr.m` / `chap-cinr.m`: interest, `TXMOISRETARD` 0,40 and `TXMOISRETARD2` 0,20, months before and
from 2018 (`NBMOISI`, `NBMOISI2`), reductions `TXMOISRED` 0,70 (L62, penalty code 22) and `TXMOISRED2` 0,50 (1727 V,
code 24). `chap-majo.m` / `chap-cmajo.m`: majorations by stratum, `TX1758A` = 10 (doubled for code 17), 1728 and 1729
rates, 1732 100 %. The penalty code of each *rappel* selects the rate (Mlang's driver `m_ext/<year>/correctif.m`,
`taux_penalite`: 2, 7, 10, 17 → 10; 3, 8, 11, 30, 55 → 40; 4, 5, 9, 12, 31, 32 → 80; 6 → 100) and the stratum order
(`get_strate_pena`). M has no art. 1730 or 1729 G (they are charged at collection, outside the assessment program;
the variables `MAJO1732*` are described as "1730" but are 1732).
- The correctif chain runs in Mlang's interpreter (`harness/pen_mlang_corr.sh`, 18 s per case). The driver that orders
  events is Mlang's re-implementation (`m_ext`), not the DGFiP's. Mlang ships 3 correctif tests; 2 have no expected
  values and the third (`tests/2023/corr/david2`) expects values Mlang does not produce (37 errors). **There is no DGFiP
  reference output for penalties**; "M" below means DGFiP M code driven by Mlang's driver.

**OpenFisca-France** (177.0.0, `refs/openfisca-france`): no intérêt de retard and no majoration of art. 1727–1758 A.
The only penalty is `contribution_differentielle_hauts_revenus_penalite_acompte` (20 % of an underpaid CDHR instalment,
LF 2025 art. 10). Nothing to test against the cases here.

**Lean.** `lean/FrTax/Penalties.lean`, imported from `lean/FrTax.lean`; no existing model file changed. The runner
`harness/pen_eval.lean` (`lake env lean --run`) evaluates cases; its `X` case computes the declared tax and the tax
after each layer with the existing Lean model (`compute`), then the penalties.

## 4. Scoreboards

### 4a. BOFiP and official examples (`data/pen/bofip_cases.txt`, `runs/pen/bofip_score.json`): 22/23

Inputs are the stated rights; Lean computes the penalties. Sources found by extracting every numeric example from the
in-force BOFiP sanction series (`harness/pen_bofip_examples.py`, 51 numeric examples in 61 documents, most about the
withholding transition) plus the rates impots.gouv.fr and service-public.fr publish (no official page gives a
worked late-filing example with euro amounts; press examples were not used).

| Example | Stated | Lean |
|---|---|---|
| BOI-CF-INF-10-20-30-20 § 10 ex. 1: 40 % layer 6 770 → 2 708; good-faith layer 1 156 at 0 % | 2 708 | 2 708 |
| same, with art. 1758 A on the good-faith layer | (2 708) | **2 824** |
| ex. 2: 80 % layer 10 624 → 8 499; 40 % layer 3 884 → 1 554 | 10 053 | 10 053 |
| ex. 3 and 4: late 10 % on 2 379 / 2 181 → 238 / 218; 40 % on 3 141 / 2 755 → 1 256 / 1 102; penalty dégrèvements 20 and 154 | all | all |
| BOI-CF-INF-10-20-10 § 80: art. 1728 4 split, 9 830 × 16 000/51 000 at 40 % + rest at 10 % | 1 909 | 1 909 |
| BOI-CF-INF-10-20-30-10 § 30: late 10 % on 5 372 + 40 % on 6 770; good faith 10 % on 12 142 | 3 245; 1 214 | 3 245; 1 214 |
| BOI-CF-INF-10-20-30-20 § 30: deficit carried, strata N-1 and N | 2 721; 901 + 2 980 = 3 881 | same |
| BOI-CF-INF-10-30 § 180: 0,20 % × 3 months × 15 000; 10 % × 15 000 | 90; 1 500 | 90; 1 500 |
| BOI-CF-INF-10-10-10 § 250: tolerance, 13 000 vs 73 000 / 20 = 3 650 | not applicable | not applicable |
| BOI-DAE-20-10 § 90: halved rate 0,10 %/month from 2018, 0,20 % before | 10; 20 (per 10 000, 1 month) | 10; 20 |
| BOI-CF-INF-10-10-20 § 70: income N from 1 July N+1 (16 months to Oct N+2) | 16 months | 16 |
| impots.gouv.fr droit à l'erreur: 1,2 %/year halved; L62 "réduit de 30 %"; service-public A15723 2,4 %/year | 120; 168; 240 | same |

The one difference: BOI-CF-INF-10-20-30-20 (version of 15 April 2013, in force) adds a good-faith income-tax
reassessment at **0 %**. Art. 1758 A, in force since 2006, charges 10 % on a good-faith insufficiency unless it was
corrected within 30 days of a request; the DGFiP's own BOI-CF-INF-20-10-10 § 90 and BOI-ANNX-000277 say "Bonne foi:
majoration de 10 % (CGI, art. 1758 A)". The example is right only if the taxpayer corrected within 30 days, which it
does not say. Class: **doctrine example vs statute (the example predates or ignores 1758 A)**; Lean follows 1758 A.

### 4b. Lean vs M (`harness/pen_m_cases.py`, `runs/pen/m_compare.txt`): 59/70

A couple, 1AJ 30 000 / 1BJ 20 000 (income 2023 unless stated), declared on time; reassessments sent as M *rappels*
with a penalty code and a proposition month; Lean computes the same scenario from the statute with its own tax model.
Families: every penalty code (21), the stop month from July 2024 to December 2027 (9), two and three layers in both
orders (9), late returns by code (5), late return + reassessment (5), BOFiP examples 1–2 transposed to salaries (3),
small reassessments around the tolerance (10), reliefs over time (4), income 2022 and 2024 with their own M code (4).

| Result | Cases |
|---|---|
| Equal on months, interest and majorations | **59**: all interest periods (1 to 42 months), both rates, 70 % and 50 % reliefs, every rate 10/20/40/80/100, 1729 A strata in either input order (C1 = C2), 1729 A 2 with late returns (interest on the late part stops at the filing month, on the reassessment at the proposition: 34 + 107 = 141), 1758 A at 20 % (code 17), the tolerance boundary for interest (G6, G7 none; G8 3 €), income 2022 and 2024 |
| M does not apply the rappel (codes 09, 12, 30, 31, 32 on a salary box: occult activity, foreign accounts) | 5: **input issue**, excluded |
| M puts a no-interest layer (codes 01, 99) **under** the penalised layer | 3 (C4, C9, F1): +152 € and −47 € of majoration, ±1–3 € of interest. **Reading where the statute is silent**: 1729 A orders layers "passibles de pénalités" by rate; a layer with neither interest nor majoration is outside it. M treats it as part of the declared items (`get_strate_pena` stratum 0/1); Lean (and the BOFiP's ex. 1, which adds its 0 % layer last) puts it last. The meaning of codes 01 and 99 is inferred from what M computes (no interest, no majoration) and from `traite_inr` (code 01 on situation boxes sets `MENTION_EXP`) |
| M drops the 1758 A 10 % when the insufficiency is within the twentieth | 3 (G2, G6, G7: 14, 35, 36 €). **M departure, no text found**: 1727 II 4 waives interest only; 1758 A II lists its exceptions (spontaneous correction, correction within 30 days, higher majorations) and the tolerance is not one; BOI-CF-INF-20-10-10 does not mention it. M switches at exactly the twentieth (G7 2 250 ≤ 2 362: no majoration; G8 2 430 > 2 371: 39 €) |

Batch 1 (before mapping fixes) gave 33/50; the differences then were all ours: code 17 (20 %, not 10 %), code 35
(80 %), codes 01/99 (no interest), interest of a late return stopping at the filing month, the tolerance and the
"late return" flag (no tolerance for a late return). They are recorded in `runs/pen/m_cases_m_batch1.json`.

### 4c. Courts (`data/pen/court_cases_curated.txt`, `runs/pen/court_score.json`): 33/47 exact, 38/47 within 2 €

Decisions stating a penalty amount *with* its base and period are rare. Pipeline: 1 748 519 decisions scanned
(`harness/pen_courts_filter.py`, JADE dump of 2026-11-08 + justice-administrative open data 2021–2026), 21 885 kept
(income tax or social levies, and a penalty term), 20 000 with "impôt sur le revenu" in the first 6 000 characters;
`pen_courts_score2.py` extracted 177 candidate statements (a labelled base and a labelled interest or majoration
amount); every candidate with a computable statute value was read by hand; 47 figures from 20 decisions kept.

| Decision | Figure | Stated | Lean | Class |
|---|---|---|---|---|
| CAA Versailles, 1 Dec 2016, 15VE03603 | 1758 A 10 % of 12 500; interest 2008 to Dec 2011 (30 × 0,40 %) | 1 250; 1 500 | same | match |
| CAA Versailles, 17 Mar 2022, 20VE01553 | 80 % of 120 912; 29 months × 0,40 % | 96 730; 14 026 | same | match |
| CAA Nantes, 31 Jan 2019, 17NT01442 | 10 months × 0,40 % of 88 277; penalties = 100 % | 3 531; 88 277 | same | match |
| CAA Paris, 28 Feb 2017, 15PA04185 | 8 months × 0,40 % of 63 039 | 2 017 | same | match |
| CAA Paris, 18 Nov 2020, 19PA00074 | 40 % of 256 094 | 102 438 | same | match |
| CAA Nantes, 15 Nov 2019, 18NT00682 | 22 months × 0,40 % of 995 | 88 | same | match |
| TA, 20 Feb 2025, 2220181 | 2016 income: 6 months at 0,40 % + 19 at 0,20 % = 6,2 % of 129 090; 40 % | 8 004; 51 636 | same | match (the 2018 rate change) |
| TA, 3 Apr 2025, 2207191 / 2207540 / 2216992 / 2300384 / 2307151 | 1758 A 10 % and 7,0–7,2 % interest (2016 income, Nov–Dec 2019) | 10 figures | same | match (1 455 = 10 % of 14 545 = 1 454,50 rounded half up) |
| TA, 18 Mar 2024, 2200248 | 10 % of 76 641; social levies 6,8 % of 28 780 | 7 664; 1 957 | same | match |
| TA, 5 Dec 2023, 2200330 | 10 % of 5 278; court's own 10 % of 3 316 | 528; 332 | same | match |
| TA, 14 Mar 2025, 2301416 | 1730 10 % of 71 316; the court's own 19 272 × 7,20 % | 7 132; 1 388 | same | match |
| TA, 10 Aug 2026, 2500240 | 40 % of 59 437 / 42 937 / 79 868; social levies 30 × 0,20 % | 4 figures | same | match |
| CAA Versailles, 1 Jun 2017, 16VE01745 | 80 % of 226 521 = 181 216,8 | 181 216 | 181 217 | ±1: rounding down (or a base in cents) |
| CAA Nantes, 14NT00058; TA 2500240 (IR 2020); CAA Lyon, 18LY04137 | interest | 2 196; 2 876; 1 057 | 2 195; 2 875; 1 056 | ±1: several levies rounded separately |
| CAA Versailles, 16 Oct 2018, 17VE00948 | 40 % and 15 × 0,40 % of 309 577 | 123 823; 18 573 | 123 831; 18 575 | extraction: both reproduce exactly on 309 557 (20 € of the rights carry neither) |
| CAA Paris, 19PA00074 | 24 × 0,40 % of 256 094 | 24 489 | 24 585 | extraction: exact on 255 094 (1 000 € without interest) |
| TA, 18 Mar 2024, 2200248 | IR interest 6,8 % of 76 641 | 5 162 | 5 212 | extraction: implies a base of 75 912 |
| TA, 3 Apr 2025, 2216416 / 2300726 | interest (same scheme as the 5 matching siblings) | 205; 204 | 254; 435 | unexplained in the decision |
| TA, 5 Dec 2023, 2200330 | interest, income 2017, proposition 7 Apr 2021 (34 months) | 306; court 192 | 359; 225 | the administration's and the court's figures both imply 29 months; the court cut the interest pro rata (306 × 3 316/5 278 = 192) instead of recomputing |
| TA, 10 Aug 2026, 2500240 | IR 2019 interest | 2 140 (3,6 %) | 3 566 (6,0 %, as the same year's social levies) | extraction: 3,6 % is the 2020 ratio; likely a transcription |
| CAA Marseille, 23 May 2014, 12MA01157 | 2005 income, 6 × 0,40 % of 15 721 | 285 | 377 | unexplained |

No decision found where a court computed a penalty by a method different from the statute. The nearest is
**TA, 14 Mar 2025, n° 2301416**: the court states the statute's figure itself ("1 388 euros (19 272 euros x 7,20 %)")
but keeps the 1 228 € the administration claimed, because the claim was lower; and TA n° 2200330, which scales the
claimed interest pro rata. Every unexplained difference is in the taxpayer's favour (stated < statute on the stated base).

## 5. Interesting disagreements

1. **M waives the 1758 A 10 % within the 1/20 tolerance** (G2, G6, G7). The statute waives only the interest.
2. **M puts mention-expresse / no-penalty layers (codes 01, 99) beneath the penalised layer**, which moves the 40 % or
   80 % onto a different slice of the scale (C4: 1 486 € where descending order gives 1 334 €; F1: 1 103 € vs 1 150 €).
3. **The BOFiP's good-faith layer at 0 %** (BOI-CF-INF-10-20-30-20, 2013) vs art. 1758 A's 10 %, which the DGFiP's own
   annex BOI-ANNX-000277 states.
4. **Courts accept the administration's lower figures** (TA 2301416, TA 2200330) rather than the statute's arithmetic.
5. M's pre-2018 branch: `TXINR` counts the 0,40 % months only when the notification year is 2015 or 2016
   (`positif(2017 - DATOCEANS12) * positif(DATOCEANS12 - 2014)`), and the halved and 70 % rates apply 0,20 % to the
   pre-2018 months too, where BOI-DAE-20-10 § 90 gives 0,20 % halved from 0,40 %. Dead code in the 2022–2025 programs
   (their interest always starts in or after July 2023), so not reachable in any case we can run.

## 6. Which penalties courts uphold or discharge (indicative)

`harness/pen_courts_outcomes.py`: of 17 023 income-tax decisions with an operative part, **676** discharge or reduce a
penalty on its own (not "droits et pénalités" following a cut in the base). Penalties named there: 40 % 218, manquement
délibéré 190, art. 1729 145, 80 % 70, 10 % 68, 1758 A 53, 1728 47, manœuvres frauduleuses 47, occult activity 11.
Reasons found in the penalty section: the administration does not establish the deliberate character (burden on it,
LPF L195 A) 213; a lower penalty substituted (80 % → 40 %, or interest instead of a majoration) 114; remise or
dégrèvement during the case 62; motivation (LPF L80 D) 46; procedure 18; none found 342. By year: 16–25 a year in
2017–2021, 43–72 in 2022–2026 (more TA decisions are published from 2022). A first, coarser classifier over all 9 129
decisions with a penalty section was checked on 10 samples and was wrong on 4 (it counted base reductions and
reversals as discharges), so only the operative-part count is reported.

## 7. Theorems (all in `lean/FrTax/Penalties.lean`; `#print axioms` in `harness/pen_axioms.lean`)

| Theorem | Statement | Axioms |
|---|---|---|
| `months_mono`, `rateSum_mono` | a later stop month never counts fewer months or less rate | propext, Quot.sound |
| `interest_mono_delay` | **interest is monotone in the delay** (base ≥ 0, any relief) | propext, Quot.sound |
| `interest_mono_base` | monotone in the base | propext, Quot.sound |
| `rateSum_from2018`, `ir_interest_rate` | **0,20 % a month**: from Jan 2018 the rate sum is 20 × months; for income ≥ 2017 always | propext, Quot.sound |
| `rateSum_before2018`, `months_split` | 0,40 % before 2018; the two periods add up | propext, Quot.sound |
| `relief_le` | the halved (1727 V) and 70 % (L62) interest never exceed the full interest | propext, Quot.sound |
| `rate1728_cases`, `rate1728_mem` | **art. 1728 rates are 10, 40 or 80 %** whenever due | propext (+ Quot.sound) |
| `rate_1728_1729_mem`, `rate_1729_mem` | 1728/1729 failures carry 10, 40 or 80 %; 1729 ones 40 or 80 % | propext |
| `rate_mem` | every income-tax rate is in {0, 10, 20, 40, 80, 100} | propext |
| `majo_mono_rate` | a higher rate never gives a smaller majoration | propext, Quot.sound |
| `strata_sum` | the 1729 A strata add up to the total extra tax, in any order | propext, Quot.sound |
| `modulationRate_le` | the 1729 G rate never exceeds 50 % | propext, Classical.choice, Quot.sound |

Plus 6 `example`s by `decide` (kernel-checked): the BOFiP figures 2 708, 10 053, 1 909, 3 245, 1 214 and one month of
interest on 10 000 € = 20 €.

## 8. What the DGFiP publishes about sanctions

Gathered from the web (20 searches; economie.gouv.fr refused every fetch with HTTP 403, so two official documents were
read from copies hosted elsewhere, marked below).

**Why.** impots.gouv.fr ("Le droit à l'erreur en matière fiscale", modified 7 Jan 2026): the interest "représente le prix
du temps, mais aucune majoration ni amende" for a good-faith error; a spontaneous correction gives "une réduction de
50 % du taux de l'intérêt de retard, soit 1,2 % l'an au lieu de 2,4 %"; during a control "réduit de 30 %"; the right
does not cover late filing, late payment or deliberate errors. The courts say the same: interest is not a sanction, "dès lors qu'ils ne visent qu'à réparer le
préjudice financier subi par le trésor du fait de l'encaissement tardif de sa créance" (TA, 22 June 2023, n° 1908163);
majorations are sanctions, so the administration bears the proof of bad faith (LPF L195 A) and must give reasons 30
days before collection (L80 D). The 2024 performance plan of programme 156 (PAP 2024, assemblee-nationale.fr) states
the droit à l'erreur as an incentive "à régulariser leur situation", and that withholding-instalment penalties "n'ont
pas été appliquées jusqu'en 2022" after the Covid crisis. service-public.gouv.fr (A15723, F34176, F34200, F31451)
restates 10/20/40/80 %, 0,20 %/month, the 45-day rule of 1730 and the penal sanctions (500 000 € and 5 years; 3 M€ and
7 years aggravated).

**How much.**
- Bilan du contrôle fiscal 2025 (ministry press kit, April 2026; read from a copy on ifrap.org): **17,1 Md€ of duties
  and penalties notified** in 2025 (13,4 / 14,6 / 15,2 / 16,7 Md€ in 2021–2024), 11,4 Md€ collected; external controls
  9,8 Md€, desk controls 7,3 Md€; "un peu plus de 34 % des dossiers [de contrôle externe] ont donné lieu à l'application
  de pénalités exclusives de bonne foi" (33,3 % in 2024, 31,1 % in 2023); 2 138 cases sent to prosecutors, 282 of them
  complaints for tax fraud; 50,9 % of controls closed with the taxpayer's acceptance (44,6 % in 2024).
- Cour des comptes, "La lutte contre la fraude fiscale" (December 2025; synthesis read from a copy on upe06.com), chart
  from the DGFiP's statistical annexes: **penalties and late interest 5,07 Md€ (2015), 4,17, 3,92, 3,23 (2018), 2,41,
  1,34 (2020), 2,38, 2,66, 2,56, 2,64 Md€ (2024)** against duties of 16,12 … 17,42 Md€ (from 2019 the series counts
  amounts put into collection, not notified). Penalties fell from ~31 % to ~15 % of duties. The Cour finds that
  administrative sanctions remain "mesurée et limitée aux faits les plus caractérisés" and that the DGFiP "gagnerait à
  mieux formaliser sa doctrine d'application des sanctions administratives". (Year pairing read from the extracted chart
  layout; check against the original.)
- No official source found gives penalty amounts for the income tax or for individuals separately, nor counts of
  rectifying returns or interest reductions under the droit à l'erreur.

## 9. Limits

- **No reference output for M's penalties.** The DGFiP publishes no correctif test with expected values; Mlang's driver
  (`m_ext/correctif.m`) is a re-implementation, so an "M departure" may be a driver departure. The two M findings (§5,
  1–2) are in the M rules (`chap-majo.m` tolerance coupling, `get_strate_pena` order) but were only observed through it.
- **Penalty codes are inferred.** Code meanings come from M's tables and from what M computes, not from a DGFiP code
  list (none is public). Codes 09, 12, 30–32 were not exercised on suitable boxes.
- **Constructed cases.** The 70 Lean-vs-M cases are simple salary households; credits, CEHR, social levies and
  multi-year cases were not combined with penalties. The 61 € and 12 € collection thresholds are not modelled.
- **Courts.** Only 20 decisions state usable figures; the extraction finds labelled statements and was then read by
  hand, so decisions stating figures in tables or annexes are missed; pre-2006 cases (0,75 %) are out of the Lean scope.
  The outcome statistics are regex-based and indicative.
- **Doctrine** used is the in-force BOFiP (2026-11-12 dataset); archived versions were not fetched.
- Not modelled in detail: 1729-0 A, 1758, 1736 amendes, 1731 bis, mention expresse conditions, 1729 G instalment
  rules beyond the rate, art. 1727 IV 7–8.

## 10. Files (the build server `~/fr`, mirrored under `~\Documents\the build server-work\fr\`)

- `lean/FrTax/Penalties.lean` (import added to `lean/FrTax.lean`); `harness/pen_eval.lean`, `harness/pen_axioms.lean`
- `harness/pen_courts_filter.py`, `pen_courts_extract.py`, `pen_courts_score.py`, `pen_courts_score2.py`,
  `pen_courts_outcomes.py`, `pen_bofip_examples.py`, `pen_m_cases.py`, `pen_m_run.py`, `pen_m_compare.py`,
  `pen_mlang_corr.sh`, `pen_score.py`, `pen_explore*.py`, `pen_fig_peek.py`
- `data/pen/`: `courts/*.jsonl.gz` (21 921 filtered decisions), `court_decisions.jsonl`, `court_figures.jsonl`,
  `court_candidates.jsonl`, `court_cases_curated.txt`, `court_penalty_discharges.jsonl`, `bofip_examples_raw.txt`,
  `bofip_cases.txt`, `m_cases*.json|txt`
- `runs/pen/`: `m/*.irj` (the correctif cases), `m_cases_m.json`, `m_cases_m_batch1.json`, `m_cases_lean.out`,
  `m_compare.txt|json`, `bofip_score.json`, `court_score.json`, `filter.log`
- `PROGRESS_pen.md`
