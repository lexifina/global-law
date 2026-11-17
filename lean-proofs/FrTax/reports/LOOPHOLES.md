# French income tax: loopholes, cliffs and traps in the rules as written (17 November 2026)

What this is: a search, with the Lean model of the CGI (`lean/FrTax`, income 2020–2025), for legal outcomes of the
rules as written that are surprising, unintended or exploitable. Every figure was computed by Lean, checked against
Mlang (the DGFiP's M code), and on 24 returns against the DGFiP's production simulator. This is analysis of the
law, not advice. Statutory options (scale option, actual expenses, attachment, separate taxation in the year of
marriage, flat levy) are choices the law offers. Anything that rests on a false declaration is fraud, not a
loophole (for example a separation that did not happen, or a gift that was not made). The anti-abuse rules are
noted where they matter: abus de droit (LPF art. L64), which covers fictitious acts and acts whose only aim is
tax, and the "mini-abus de droit" (L64 A, acts from 2020 whose main aim is tax).

"Burden" below means everything the household pays on the return: net income tax (a refund counts as negative),
CEHR, CDHR, social levies assessed on the return, and the micro-entrepreneurs' flat levy. Amounts are in euros
per household per year.

Files: harness `harness/loop_lib.py` (runners), `loop_known.py` (step 1), `loop_scan.py` + `loop_scan_report.py`
(step 2a), `loop_inter.py` (steps 2b–2d), `loop_sim.py` (production simulator). Outputs: `runs/loop/` (`known_*.json`,
`scan_*.jsonl`, `scan_report.json`, `inter_*.json`, `sim.jsonl` and the saved pages `sim.jsonl.html/`).
Proofs: `lean/FrTax/Loopholes.lean`. Log: `PROGRESS_loopholes.md`.

## Ranked findings

The score is size × plausibility × reach, judged on 1–3 each. **Size** is the euros at stake per household.
**Plausibility** asks whether an ordinary household meets the conditions without artifice. **Reach** is how many
households could use it; the national box counts are DGFiP figures for income 2024 (`data/pop/targets_2024.json`).
Status: **known** means described before (sources in each entry); **variant** means a known mechanism in a new
combination or under 2025 law; **novel** means not found in the sources checked (listed at the end).

| # | Finding | Size | Who / how many | Status | Score | Lean / M / production | Proof |
|---|---|---|---|---|---|---|---|
| 1 | Adult child: alimony deduction beats attachment above ~44–50 k€ (couples, 1st/2nd child); attachment beats it by up to 1 557 € for a 3rd child and up to 1 126 € for single parents | ≤ 1 004 € (couples), ≤ 1 557 € the other way | 1.72 M households attach (0DJ), 0.82 M deduct (6EL) | known | 3×3×3 = 27 | ✓ / ✓ 600/600 / ✓ 3 returns | `attach_costs_more_*` (kernel over 24 000 incomes; full band native) |
| 2 | **CDHR (income 2025) takes back credits and reductions**: home help, gifts, care home, PER deduction… worth 0 to a CDHR payer | ≤ 6 000 € (home help), ≤ 6 600 € (gifts) | CDHR payers: 7 055 advance payers, 605 M€ (AN q. 16231) | known (gifts fixed for 2026; others remain) | 3×3×1 = 9 → **18** for its size | ✓ / ✓ 900/900 / ✓ 4 returns | `cdhr_neutral` (general, omega), `cdhr_payer_2025` |
| 3 | Separated parents with shared residence and box T: up to 4 910 € less than married | ≤ 4 910 € | 1.13 M households with 0CH; 1.97 M with T | known (sham separation = fraud) | 3×2×2 = 12 | ✓ / ✓ 14/14 / ✓ 3 returns | `separation_bonus_2025` |
| 4 | Scale option (2OP) vs flat tax (PFU): the default (PFU) costs the non-taxable and the 11 % band up to 12.8 % of their investment income | ≤ 5 120 € in the grid (40 k€ dividends) | 11.5 M declare dividends, 2.54 M tick 2OP | known | 2×3×3 = 18 | ✓ / ✓ 600/600 / — | — |
| 5 | **Marginal rate 101.1 % in the CDHR smoothing band** (income 2025): PFU-taxed investment income with levies on the return | 1.1 % above 100 % over a 32–45 k€ band (≈ 350–500 €) | CDHR band households; the 82.5 % applies to all of them | **novel** (not found) | 2×3×1 = 6 → **12** as a design defect | ✓ / ✓ / ✓ 2 returns | `emtr_over_100_single/couple_2025` |
| 6 | Scale option beats PFU for CDHR payers (the CDHR base leaves out the 40 % dividend allowance) | 1 333–8 033 € in the grid | CDHR payers living on dividends | known (advisers list CDHR as an exception) | 3×2×1 = 6 | ✓ / ✓ / ✓ 1 return | in `cdhr_payer_2025` |
| 7 | Micro-entrepreneur flat levy (VL) vs ordinary micro | VL saves ≤ 11 251 €; costs ≤ 510 € to low earners | ~660 k on VL; ~820 k ordinary micro; VL needs a low RFR two years earlier | known | 3×2×2 = 12 | ✓ / ✓ 500/500 / — | — |
| 8 | Separate returns in the year of marriage/PACS (art. 6, 5) | median 308 €, ≤ 2 600 € (17 % of random couples gain) | every couple in its first year | known | 2×3×2 = 12 | ✓ / — / — | — |
| 9 | Pensioner couples pay up to 1 819 € more married: the 10 % pension allowance is capped per household (4 439 €) | ≤ 1 819 € | pensioner couples above ~45 k€ each | known (AN q. 21770, 2019) | 2×3×2 = 12 | ✓ / ✓ / ✓ 2 returns | `pensioners_marriage_penalty_2025` |
| 10 | Actual expenses that exceed the 10 % allowance still cost more for union members (the 66 % dues credit is lost) | ≤ 375 € | 1.04 M claim union dues; 4.27 M claim actual expenses | known (trap) | 1×3×2 = 6 | ✓ / ✓ 206/206 (394 refused I00101) / ✓ 2 returns | `union_dues_trap_2025` |
| 11 | **A gift that pays for itself**: with tax 61–239 € after the décote, a gift of 4/3 × (tax − 60) at 75 % brings the tax under 61 €, which is not collected | ≤ 60 € net gain | every household with tax 61–239 € (several hundred thousand; not counted) | variant (rule documented; this use not found) | 1×3×3 = 9 | ✓ / ✓ / ✓ 2 returns | `gift_cheaper_than_tax` (kernel, every tax 61–239 €), `gift_pays_2025` |
| 12 | Refundable credits are first spent on an uncollected tax under 61 € | ≤ 60 € | home-help (5.19 M), childcare (1.9 M) users near the threshold | known (BOFiP § 90; press) | 1×3×2 = 6 | ✓ / ✓ / ✓ 2 returns | `credit_pays_uncollected_tax_2025` |
| 13 | 61 € notches: +1 € of income → +61 to +63 € (income tax; separately social levies) | 61–63 € | at the threshold | known | 1×3×2 = 6 | ✓ / ✓ / — | `notch_61` (Theorems.lean) |
| 14 | Art. 157 bis cliffs: +1 € → up to +226 € (2025); also triggered by untaxed flat-levy income counted for the effective rate (+108 €) | ≤ 226 € | over-65s and disabled near 17 670 € / 28 430 € | known; flat-levy route variant | 1×3×2 = 6 | ✓ / ✓ / ✓ 2 returns | `age_cliff` (Theorems.lean), `flat_levy_removes_157bis_2023` |
| 15 | Décote marriage penalty: two low earners pay up to 310 € more married | ≤ 310 € | couples with ~20–33 k€ each | known | 1×3×2 = 6 | ✓ / ✓ / — | — |
| 16 | F2: production prorates the CEHR when flat-levy micro income is present (statute: no proration) | ≤ 1 737 € (2 M€ salary + 77.7 k€ receipts) | high earners with VL micro income; VL needs a low RFR two years earlier, so rare | from FINDINGS F2 | 2×1×1 = 2 | M = production ≠ statute (22/22 earlier) | — |
| 17 | **One more euro, 62 € less tax**: the double rounding of art. 197 C pushes a 62 € tax to 60 €, which is not collected | ≤ 62 € | flat-levy micro-entrepreneurs at the threshold; 31 points in the scan | **novel** (curiosity) | 1×1×1 = 1 | ✓ / ✓ / ✓ 2 returns | `one_euro_less_tax_2020` |
| 18 | F1: union-dues credit on overtime between 5 000 € and 7 500 € (production, 2022–2024) | ≤ 16.50 € per person | overtime earners who pay union dues | from FINDINGS F1 | 1×2×1 = 2 | M = production ≠ statute | — |

Rows 2 and 5 are scored up for size or for design interest, not by the formula alone.

## The strongest findings in detail

### 1. Adult child: attach or deduct alimony (CGI art. 6, 3; 196 B; 156, II, 2°; 197, I, 2)
- **Law.** A child aged 18–24 (25 for students) may be attached to the parents' household (art. 6, 3). The child
  then brings a half part (a whole part from the third child), and the saving is capped at 1 807 € per half part
  in 2025 (art. 197, I, 2). Instead, the parents may deduct alimony paid to the child, up to 6 855 € in 2025
  (art. 156, II, 2°, by reference to the art. 196 B amount). The child is then taxed on it alone, after the 10 %
  allowance.
- **Mechanism.** Attachment is worth at most the cap. The deduction is worth 6 855 € × the marginal rate, and the
  student usually owes nothing on 6 169 € of taxable income.
- **Grid** (`known_k1.json`, 2020–2025, salaries 10–300 k€, 4 family types):

  | Family | Alimony first beats attachment at total salary | Largest gain |
  |---|---|---|
  | Couple, no other child (2025) | 44 000 € | alimony 1 004 € (196 k€ and above) |
  | Couple + 1 minor (2025) | 50 000 € | alimony 1 004 € |
  | Couple + 2 minors (the student is the 3rd child, a whole part) | never | attachment 1 557 € |
  | Single parent, box T (2025) | 34–36 k€ (≤ 169 €), then again above ~250 k€ (107 €) | attachment 1 126 € (T with a whole part, capped at 4 262 €; without the child the parent gets only box L) |

  Other years scale with indexation (2020: alimony up to 874 €; 2024: 995 €).
- **Concrete** (2025): married, salaries 120 000 € + 80 000 €, one minor and a student. Attached: 37 787 €.
  Alimony of 6 855 €: 36 783 €, and the student's own return gives 0 €. Saving 1 004 €.
  Production 37 787 € / 36 783 € / 0 €.
- **Proved.** `attach_costs_more_kernel_2025` (kernel `decide`, every taxable income from 176 002 € to 200 001 €)
  and `attach_costs_more_2025` (every integer from 176 002 € to 369 999 €, `native_decide`): on 2.5 parts after
  deducting 6 855 €, the tax is at least 1 003 € below the 3-part tax. `student_alone_owes_nothing_2025`.
- **Who.** Parents of 18–25-year-olds. The default is to attach; above roughly 45–50 k€ of salary (couples, first
  or second child) it costs up to 1 004 € a year. Anti-abuse: the alimony must be really paid and match the
  child's needs (art. 208 Code civil). The administration accepts a flat amount for board and lodging. Nothing
  artificial is involved.

### 2. The 2025 CDHR takes back reductions and credits (CGI art. 224, III, IV, A, 2°; loi n° 2025-127 art. 10)
- **Law.** The CDHR is 20 % of the reference revenue (smoothed between 250 000 € and 330 000 €, or 500 000 € and
  660 000 € for couples) minus the income tax, the CEHR and fixed amounts (12 500 € for a couple, 1 500 € per
  dependant). IV, A, 2° adds back to that income tax only the reductions and credits it lists. For income 2025
  the list did not include gifts (art. 200; the art. 200 entry was added by loi n° 2026-103 art. 2 from income
  2026), home help (art. 199 sexdecies), care-home costs, school fees and the like. A deduction such as PER
  contributions also lowers the income tax without lowering the RFR, which adds it back.
- **Mechanism.** The tax used in the CDHR falls by exactly the reduction or credit, so the CDHR rises by the same
  amount. **Proved in general** (`cdhr_neutral`, omega, standard axioms only): for income 2025, if a household
  pays CDHR with income tax `t` and with `t'`, then `t + CDHR(t) = t' + CDHR(t')`.
- **Grid** (`inter_cdhr.json`: singles and couples, salary 0/30/100 k€, dividends 200 k€–1.5 M€; M 900/900).
  Whenever the CDHR is positive, these are worth exactly 0: 10 000 € of gifts (nominal 6 600 €), a 2 000 € aid
  gift (1 500 €), 12 000 € of home help (6 000 €), 10 000 € of care-home costs (2 500 €) and a 10 000 € PER
  contribution. Childcare and school fees show a 1 500 € gain, but that is the dependant's 1 500 € in the CDHR,
  not the credit.
- **Concrete** (2025). Single, salary 30 000 €, dividends 300 000 € at the flat rate, levies withheld at source.
  Burden 63 525 €. With 10 000 € of home help it is 63 525 € (the CDHR line rises from 21 251 € to 26 251 €).
  With 10 000 € of gifts it is 63 525 € (CDHR 22 815 €). Production shows the same three totals and the same CDHR
  lines.
- **Who.** CDHR payers: 7 055 households paid the December 2025 advance, and 605 M€ had been charged by July 2026
  (AN question n° 16231, answer JO 27 October 2026). For income 2025 their gifts, home help and similar spending
  bring no tax relief. This is a trap rather than a loophole. For gifts the legislator called it an error and
  fixed it for 2026 (loi n° 2026-103; CFF note). The others still apply.
- **Status.** Known (Fortuny Conseil, CFF "Brève juridique LF 2026", BOFiP BOI-IR-CDHR-10-20260630 § 270–280).
  New here: the general theorem and the full list as the model computes it.

### 3. A marginal rate of 101.1 % (art. 224, V, with the social levies; income 2025)
- **Mechanism.** Inside the smoothing band (art. 224, V) the first amount of the CDHR is 82.5 % × (R − 250 000 €)
  (couples: − 500 000 €). While the CDHR is positive, income tax + CEHR + CDHR equals that amount less fixed
  items, so together they take **82.5 % of every extra euro** of reference revenue. On flat-tax investment income
  whose social levies are assessed on the return, add 18.6 % for income 2025: CSG 10.6 % (LFSS 2026), CRDS 0.5 %
  and the solidarity levy 7.5 %. The total is **101.1 %**. With levies withheld at source at 17.2 % it is 99.7 %.
  Above the band the rate falls back to 20 % + levies.
- **Scan** (`scan_report.json`): 156 rays, all income 2025, every family type, dividends, interest or gains under
  the flat tax. Sustained marginal rates of 101.1 % over 30–45 k€ bands: about 298 000–330 000 € for a single
  person and 615 000–660 000 € for a couple without children. The band moves with the other income and the
  children.
- **Proved.** `emtr_over_100_single_2025`: every 1 000 € step of dividends from 298 000 € to 330 000 € costs
  1 011 €. `emtr_over_100_couple_2025`: the same from 615 000 € to 660 000 €. Production: 97 050 € at 300 000 €
  and 98 061 € at 301 000 €.
- **Who and how it could be used.** Few households, about the size of the CDHR population. The 82.5 % applies to
  every income type, and the rate above 100 % to investment income taxed on the return. A taxpayer in the band
  gains by moving income out of it: deferring a sale, timing dividends from a company they control. Deliberate
  timing through a controlled company could be challenged under L64 A if tax is its main aim. Not found as a
  description in the sources checked. The press calls the 82.5 % a "décote" (lissage); none we found says the
  combined rate exceeds 100 %.

### 4. A gift that pays for itself (art. 200 with art. 1657, 1 bis)
- **Law.** A tax under 61 € is not collected. The test is on the tax after the décote and after the reductions,
  but before the credits (BOI-IR-LIQ-20-20-40 § 60).
- **Mechanism.** With tax T between 61 € and 239 €, a gift of G = ⌊4 (T − 60) / 3⌋ € to an aid organisation (75 %,
  art. 200, 1 ter) is enough to bring the tax under 61 €, and G < T. The household saves T and spends G, a net gain
  of up to 60 €. At 66 % (other gifts) it works for T < 176 €.
- **Proved.** `gift_cheaper_than_tax` (kernel `decide`, every T from 61 € to 239 €). `gift_pays_2025`: a single
  person with a 19 600 € salary owes 67 €; a 9 € gift gives a 7 € reduction, the tax is 60 € and nothing is
  collected. Production: "Impôt sur le revenu net 60 €", nothing to pay.
- **Who.** Every household whose tax after the décote is 61–239 €. That is the band just above the taxation
  threshold, several hundred thousand households (not counted). The gift must be real; then there is no artifice,
  and the law gives the result. The 61 € rule and the order of imputation are documented; we found this use of a
  reduction nowhere (classed as a variant).

### 5. Separation with shared residence (art. 194, I and II; 197, I, 2, second paragraph)
- **Mechanism.** A married couple's children each bring a half part capped at 1 807 € (2025). Separated parents
  living alone, each with the children in shared residence, each tick box T: each return gets the children's
  quarter parts plus T's, capped at 4 262 € for two children. That is 2 × 4 262 € against 2 × 1 807 €.
- **Grid** (`inter_divorce.json`, salaries 10–200 k€). Separation is cheaper for 607 of 858 income pairs (two
  children, 2025). The gain is up to 4 910 € with two or three children and up to 2 455 € with one.
- **Concrete** (2025), salaries 100 000 € and 50 000 €, two children. Married: 23 094 €. Separated: 16 439 € +
  2 398 €. Separation saves 4 257 €. Production gives the same three figures. `separation_bonus_2025`.
- **Status.** Known; it is how the law treats single parents. Ticking T while living as a couple is a false
  declaration (fraud), not a loophole. Unmarried cohabitants cannot tick T (the step 1 grid `known_k4` models that:
  their best split never beats marriage by more than the décote effect).

## Known optimisations recreated (step 1)

Grids in `runs/loop/known_*.json`. Mlang ran on a random sample of each grid: 4 204/4 204 comparable results
equal. M refused 394 returns with actual expenses (anomaly I00101) and 2 shared-residence returns (IM3002);
production computes them (`Lud1`).

| Item | Law | Result (2025 unless stated) | Status |
|---|---|---|---|
| Attach vs alimony | 6, 3; 196 B; 156, II, 2° | finding 1 | recreated |
| 2OP vs PFU | 200 A, 1 and 2; 158, 3, 2° (40 %); 154 quinquies (6.8 % CSG) | The scale wins for singles up to ~30 000 € of salary and couples up to ~65 000 €. Gain up to 12.8 % of the income when no tax is due (40 k€ of dividends: 4 470 € single, 5 120 € couple). With equal interest, singles above ~17 500 € lose. At 197 500 € of salary, 2OP costs 1 114 € on 10 k€ of dividends. 2OP covers all investment income and gains together (art. 200 A, 2), so one interest-heavy line can make it lose. | recreated |
| Actual expenses vs 10 % | 83, 3°; 199 quater C | Dues are deductible inside actual expenses, but claiming actual expenses loses the 66 % credit. Actual expenses 400 € above the allowance still cost more for 28 of 28 salaries (≤ 211 €). Costs up to 375 €. | recreated (trap) |
| Marriage/PACS vs two singles | 6, 1; 194; 197, I, 4 (décote); 158, 5, a | Bonus up to 12 492 € (one earner). Penalties: décote up to 310 € (low earners). Pensioners up to 1 819 € (household cap on the 10 % pension allowance). Pensioners also share one 157 bis income test. | recreated |
| Shared custody | 194, I; 197, I, 2 | Separated parents with 2 children (2025): shared residence is cheapest for 607 of 858 income pairs. Both children with the higher earner is cheapest for 230 (up to 1 807 € better). Exclusive custody with the lower earner plus 12 000 € of deductible child support (6GU/1AO) is cheapest for 21. | recreated |
| Cases T and L | 194, II; 195, 1, a, b, e; 197, I, 2 | T + first child: up to 2 455 €. Box L: up to 1 198 €, above its 1 079 € cap, because the décote amplifies the capped saving. | recreated |
| QF cap, where each half part stops paying | 197, I, 2 | A couple's 1st/2nd child reaches 1 807 € from a salary of ~73–80 k€. A 3rd child (a whole part) reaches 3 614 € from ~94 k€. A disabled single person: 3 608 € (cap + complement 1 801 €). Widow(er) + child: 3 170 €. Shared child + T: 2 131 €. | recreated |
| Décote zone | 197, I, 4, a | 11 % × 1.4525 = 15.98 % of taxable income (14.4 % of salary). No abnormal rate from the décote alone (`decote_slope` in Theorems.lean). | recreated |
| 157 bis cliff | 157 bis | +1 € → +197 € (2020) … +226 € (2025), singles over 65 or disabled at 28 430 €. Couples fall in the décote zone there and lose nothing. | recreated, `age_cliff` |
| 61 € threshold | 1657, 1 bis; CSS L136-6, III | +61 to +63 € for 1 € (income tax). The same on social levies (1 680 scan points), e.g. 505 € of micro-foncier rents. | recreated, `notch_61` |
| CEHR / CDHR thresholds | 223 sexies; 224 | The CEHR has no cliff (3 %/4 % marginal). The CDHR: finding 3 (82.5 % band) and finding 2. | recreated + new |
| 197 C with micro income | 197 C; 151-0 | The décote applies after scaling. 157 bis is tested on the total, so untaxed flat-levy income can remove it (+108 € for 1 €, production confirmed). Double rounding (finding 17). | recreated + new |
| Gifts 66 % vs 75 % | 200, 1 and 1 ter | The 75 % band (1 000 €; 2 000 € from 14 Oct 2025) beats 66 %. The 20 % RNI limit carries forward. Reductions are wasted when no tax is due. With the 61 € threshold: finding 4. | recreated + variant |
| Home-help credit | 199 sexdecies | Refundable: non-taxable households get 50 %. Spent first on an uncollected tax under 61 € (refund 946 € not 1 000 €). Worth 0 to CDHR payers (2025). | recreated |
| Micro regimes | 50-0; 102 ter; 151-0 | VL vs ordinary micro: VL wins from a salary of ~5–20 k€ depending on turnover. It saves up to 11 251 € (60 k€ BNC receipts, 150 k€ salary) and costs up to 510 € to a person with no other income. Eligibility (RFR N−2 limit) not modelled. | recreated |

## Novel search (step 2)

### 2a. Marginal rates, every year, family type and income mix
3 528 rays: 6 years × 14 families (singles, T with 1–2 children or shared residence, L, disabled, widow(er),
over 65, couples with 0–3 children, couples over 65, disabled couple with children). Each ray moves one income:
salary or pension under 7 backgrounds (home help, gifts, flat-levy micro income, dividends, rents, PER), or one of
8 investment and micro incomes on top of 0/25/60/150 k€ of earnings. Each runs from 0 to 800 000 € in 7 € steps
(50 € above 150 000 €), with steps above 60 % or below 0 refined euro by euro: 121 M Lean evaluations.
Results (`scan_report.json`):
- **Rates above 100 %, sustained:** only the 2025 CDHR band (finding 3, 101.1 %).
- **Abnormal (> 60 %) and sustained:** only the CDHR band, at 82.5 % (+ levies). Nothing else in 2020–2024.
- **One-euro notches:** the 61 € threshold (1 767 points, +61 to +63 €); the social-levies threshold (1 680, +61 to
  +63 €); 157 bis (187, up to +226 €); 157 bis through flat-levy income on the effective-rate total (26, +54 to +109 €).
- **Income up, tax down:** 31 points where +1 € of flat-levy turnover lowers the tax from 61–62 € to 0 (finding 17;
  every year). Also ±1–2 € rounding jitter in the art. 197 C formula (16 595 coarse steps), not a loophole.
- Outside the model: means-tested benefits (prime d'activité, housing benefit, bourses) and earned-income social
  contributions. In real life these produce most of the high marginal rates of low earners; see "Out of scope".

### 2b. Choice pairs on 60 000 random households (gen.py; plausible shapes, not a population sample)
`inter_choices.json`. For each legal toggle: the share of households for whom the non-default choice is better,
and by how much.

| Toggle | Applicable | Non-default better | Median gain if better | Max |
|---|---|---|---|---|
| Separate returns in the year of marriage (art. 6, 5) | 19 124 | 17.3 % | 308 € | 2 600 € |
| Adult child: alimony instead of attachment | 3 305 | 23.0 % | 200 € | 4 610 € |
| Ordinary micro → flat levy (eligibility not modelled) | 2 874 | 71.3 % | 529 € | 12 086 € |
| Flat levy → ordinary micro | 1 691 | 26.0 % | 160 € | 1 309 € |
| Drop actual expenses (declarant 1) | 3 669 | 1.2 % (union-dues credit) | 88 € | 293 € |
| Toggle 2OP (either way) | 32 766 | 46.5 % | 68 € | large (the generator ticks 2OP on some large-gain returns) |

"Default is worse": attachment above ~45 k€ (couples), PFU for low incomes, joint taxation in the year of marriage
for 1 in 6 couples, and actual expenses for union members.

### 2c. Interactions
- Reductions before the 61 € test, with gifts: finding 4.
- Credits imputed on an uncollected tax: finding 12 (`credit_pays_uncollected_tax_2025`).
- The CDHR against every unlisted reduction or credit, and against the PER deduction: finding 2. The CDHR against
  2OP (the 40 % allowance left out of its base): finding 6, where 2OP saves up to 8 033 € at 340 k€ of dividends.
- The CDHR smoothing with the social levies: finding 3.
- The 157 bis test on the effective-rate total with flat-levy income, and the art. 197 C double rounding with the
  61 € threshold: findings 14 and 17.
- The QF cap with special half parts: box L is worth up to 1 198 € against its 1 079 € cap, and a disabled
  person's half part up to 3 608 € (cap + complement). A single parent with one child in shared residence gets
  2 131 €; two such parents get 4 262 € for one child, against 1 807 € for a married couple's child (finding 5).
- The household-level pension cap with marriage (finding 9).

### 2d. Where DGFiP practice and the statute differ
- **F2 (CEHR proration with flat-levy income)** is the only gap worth money (`inter_f2.json`). Production charges
  less than art. 223 sexies: −396 € (300 k€ salary + 77.7 k€ services receipts), −1 433 € (1 M€ + 77.7 k€ BNC),
  −1 737 € (2 M€). Using it needs flat-levy eligibility: an RFR two years earlier of at most about 28–29 k€ per part (art.
  151-0, I, 4°). So it fits only a household whose income has just jumped, such as a micro-entrepreneur with a
  one-off large gain. For a CDHR payer the gap is neutral: a lower CEHR raises the CDHR by as much.
- **F1** is worth at most 16.50 € a person (2022–2024, already fixed in 2025).
- **F5 and W2** work against the taxpayer (1–2 €). **W1 and W4** move cash between months only (AUTHORITY.md: the
  rate governs advances, not the tax due). **W3** is a Lean error, not a gap. F6 is an Mlang driver bug.

## Proofs (`lean/FrTax/Loopholes.lean`, imported by `FrTax.lean`; `lake build FrTax.Loopholes`: 186 s, no `sorry`)

| Theorem | Statement | Method | Axioms |
|---|---|---|---|
| `gift_cheaper_than_tax` | for every tax 61–239 €, the 75 % gift that brings it under 61 € is smaller than the tax | `decide +kernel` | none |
| `gift_pays_2025_scale` | tableTax 17 640 € = 67 €; reduction on 9 € = 7 € | `decide` | none |
| `student_alone_owes_nothing_2025` | tax on 6 169 € = 0 | `decide` | none |
| `attach_costs_more_kernel_2025` | every integer income 176 002–200 001 €: 2.5-part tax after 6 855 € ≤ 3-part tax − 1 003 € | `decide +kernel` (24 000 cases) | none |
| `cdhr_neutral` (+ `cdhr_eq`) | income 2025: whenever the CDHR is positive, income tax + CDHR does not depend on the income tax | `omega` | propext, Classical.choice, Quot.sound |
| `attach_costs_more_2025` | the same as the kernel theorem over 176 002–369 999 € | `native_decide` | + native axiom |
| `gift_pays_2025`, `credit_pays_uncollected_tax_2025`, `cdhr_payer_2025`, `emtr_over_100_single_2025`, `emtr_over_100_couple_2025`, `emtr_example_2025`, `attach_example_2025`, `one_euro_less_tax_2020`, `flat_levy_removes_157bis_2023`, `pensioners_marriage_penalty_2025`, `separation_bonus_2025`, `union_dues_trap_2025` | whole-return statements on `compute` | `native_decide` | standard + one native axiom each |

Why `native_decide` for whole returns: a `Decl` keeps its boxes in a `Std.HashMap String Int`, and `String.hash` is
opaque to the kernel, so the kernel cannot evaluate `compute`. Statements about the pure scale and CDHR functions
are kernel-checked. Theorems.lean already holds `notch_61` and `age_cliff` (decide).

## Verification

- **Lean ↔ Mlang.** Step 1: 4 204/4 204 sampled comparable results equal. CDHR grid: 900/900. Divorce: 14/14.
  Every concrete return of the proofs agrees, except `Lud1`, which M refuses (I00101) and production computes.
  F2 rows differ by design (M = production).
- **Production simulator** (`runs/loop/sim.jsonl`, 24 requests, sequential, 1.2 s apart, under
  `flock ~/fr/.sim.lock`). Amount to pay or refund equal to Lean on 24/24: gift 67 → 0; home help refund 946;
  CDHR 63 525 ×3 with CDHR lines 21 251 / 26 251 / 22 815 and 2OP 62 192; dividends 97 050 → 98 061; flat-levy
  notch 62 → 0 (2020); 157 bis via flat levy 328 → 436 (2023); attach 37 787 vs 36 783 + 0; pensioners 39 581 vs
  18 881; union dues 3 640 vs 3 724; separation 23 094 vs 16 439 + 2 398.

## Out of scope (not modelled, so not searched)
- Means-tested benefits (prime d'activité, APL, RSA, bourses, CMI), earned-income social contributions, local
  taxes. In practice these drive most marginal rates above 100 % for low earners.
- The plafonnement global des niches (art. 200-0 A) and investment reductions (Pinel, Girardin, FCPI, monuments
  historiques), the IFI, property gains (only box 3VZ), the quotient for exceptional income (art. 163-0 A), the
  CEHR/CDHR smoothing for exceptional income, and deficits carried forward.
- Multi-year plans: PER deduction vs taxation at exit, gift carry-forward over five years, flat-levy eligibility
  (RFR N−2), income timing.
- Real-regime choices that need expense data the boxes do not hold (micro-foncier vs réel, micro-BIC vs réel,
  LMNP depreciation), and life-insurance planning beyond the allowance split.
- Events within the year (death, marriage dates within the year beyond the art. 6, 5 option), non-residents and
  treaty income, and withholding timing beyond the W points.

## Sources checked for "novel" and "known"
- The authority corpora on the build server (`data/authority/text/`): BOFiP in force (9 173 records), AN written questions
  2017–2026, Sénat questions 1978–2026, administrative case law (6 072 tax decisions). Pattern searches covered the
  61 € threshold with gifts and credits, the CDHR with credits / marginal rate / 2OP, 157 bis with flat levy or
  effective rate, the pension cap with marriage, union dues with actual expenses, and shared residence with the T
  cap. Hits: pension cap (AN q. 21770), 61 € and credits (BOFiP LIQ-20-20-40 § 90), CDHR list (BOI-IR-CDHR-10
  § 270–280), CDHR yield (AN q. 16231).
- Web (standard search, 4 queries). CDHR and credits/gifts: Fortuny Conseil, Centre français des fondations note on
  LF 2026 ("erreur légistique" on gifts), Deloitte, Rivière Avocats. CDHR and 2OP: Hagnère Patrimoine ("Flat tax
  ou barème") lists the CDHR as a case for the scale. 61 € threshold with credits: Moneyvox, meilleurtaux. We found
  nothing describing a combined marginal rate above 100 % in the CDHR band, the use of a 75 % gift to fall under
  61 €, or the art. 197 C double rounding that lowers tax when income rises. Absence in these sources is not proof
  that nobody has described them.
