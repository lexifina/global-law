# Withholding-tax rates (prélèvement à la source): Lean vs Mlang vs production (17 November 2026)

Scope: the rates computed on income 2020–2025, which apply from September 2021–2026 (CGI art. 204 H, I, 2), and the
default grids of rate years 2021–2026. Programs: the Lean model (`lean/FrTax/Withholding.lean`, written from the
statute), the DGFiP's M code built with Mlang (`~/fr/bin/cal2020` … `cal2025`), and the DGFiP's production simulator
(calc-2021.cgi … calc-2026.cgi) as arbiter. OpenFisca-France (commit 0fb80f6) has no withholding-rate variable
(searched `openfisca_france/model` and `parameters`), so it has no column here.

Outputs: `~/fr/runs/pas/` on the build server. Harness: `harness/pas_*.py`. Dataset: `data/pas_grids.jsonl`.

## 1. The statute, per rate year

Statute text from the global-law record of the consolidated CGI (DILA LEGI); official text: Légifrance,
art. 204 H as amended by each law below. The record holds text changes only (no commencement rules), so the
commencement dates below come from each version's NOTA.

**Art. 204 H, I (the household rate), the same words in every year 2021–2026.**
- 1: rate = income tax of the household on the income of art. 204 A, less treaty tax credits, ÷ that income
  "pour leurs montants déterminés dans les conditions mentionnées à l'article 204 F et à l'article 204 G":
  salaries and pensions under the retenue **before** the 10 % deduction for expenses (art. 83, 3°) and the 10 %
  pension allowance (art. 158, 5, a) (204 F); alimony, annuities, business profits, property income at their **net
  taxable** amount (204 G, 2, 1° to 5°), a deficit counting for nothing (204 G, 3).
- Numerator: the tax "résultant de l'application des règles prévues aux 1 à 4 du I de l'article 197" (scale, cap on
  the quotient familial, DOM reduction, décote: no reductions or credits) "multiplié par le rapport entre les
  montants nets imposables des revenus mentionnés au 1 de l'article 204 A, les déficits étant retenus pour une
  valeur nulle, et le revenu net imposable au barème ..., hors déficits, charges et abattements".
- 2: income N gives the rate from 1 September N+1 to 31 August N+2.
- 3: "Le taux est arrondi à la décimale la plus proche. La fraction de décimale égale à 0,50 est comptée pour un."
- No 61 € rule anywhere in 204 H (the 61 € of art. 1657, 1 bis is a collection threshold).

**Art. 204 H, II (zero rate).** Nil when (1°) the income tax "mis en recouvrement" for the last two known years is nil
and (2°) the RFR of the last known year is "inférieur à X € par part", X "indexé chaque année comme la limite
supérieure de la première tranche du barème". X is the only figure of the II test: one amount per part (M:
`RFRPARQF × NBPT > REVKIRE`), no separate half-part or quarter-part amount, no second RFR condition.

| Rate year (income) | X as indexed (BOFiP BOI-IR-PAS-20-20-10; M `RFRPARQF`; Lean) | BOFiP version | X printed in the consolidated CGI on 1 Sept | Printed by |
|---|---|---|---|---|
| 2021 (2020) | 25 705 € | 20220516 | 25 654 € (25 000 € until 11 June 2021) | décret n° 2021-744 |
| 2022 (2021) | 26 065 € | 20230626 | 25 705 € | décret n° 2022-782 |
| 2023 (2022) | 27 473 € | 20240618 | 26 065 € | décret n° 2023-422 |
| 2024 (2023) | 28 792 € | 20250507 | 27 473 € | décret n° 2024-496 |
| 2025 (2024) | 29 310 € | 20260407 | 28 792 € | décret n° 2025-547 |
| 2026 (2025) | 29 574 € | 20260407, "Remarque" | 29 310 € (from 1 July 2026) | décret n° 2026-562 |

The printed figure lags one indexation behind: each codification decree records the previous year's indexation.
The law's figure is the indexed one (BOI-IR-PAS-20-20-10-20260407 § 180: "indexé chaque année, le 1er septembre,
comme la limite supérieure de la première tranche du barème"), and M, production and Lean all use it (see W3).

**Art. 204 H, III, 1 (default grids).** Twenty brackets of monthly base, rates 0 %, 0.5 %, 1.3 %, 2.1 %, 2.9 %, 3.5 %,
4.1 %, 5.3 %, 7.5 %, 9.9 %, 11.9 %, 13.8 %, 15.8 %, 17.9 %, 20 %, 24 %, 28 %, 33 %, 38 %, 43 %, unchanged since 2021;
only the bounds move, by the finance law of each year:

| Rate year | Grid set by | Applies | Mainland first / last bound |
|---|---|---|---|
| 2021 | loi n° 2020-1721 (LFI 2021), art. 2 | 1 Jan 2021 | 1 420 / 48 292 € |
| 2022 | loi n° 2021-1900 (LFI 2022), art. 2 | 1 Jan 2022 | 1 440 / 48 967 € |
| 2023 | loi n° 2022-1726 (LFI 2023), art. 2 | 1 Jan 2023 | 1 518 / 51 611 € |
| 2024 | loi n° 2023-1322 (LFI 2024), art. 2 | 1 Jan 2024 | 1 591 / 54 088 € |
| 2025 | loi n° 2025-127 (LFI 2025), art. 2 | income from 1 May 2025 (2024 grid before) | 1 620 / 55 062 € |
| 2026 | loi n° 2026-103 (LFI 2026), art. 4 | income from 1 May 2026 (2025 grid before) | 1 635 / 55 558 € |

III, 1, d: bounds scaled to the pay period; for the acompte income of art. 204 C the grids apply to that income
"majorés de 11 %". III, 2: the default grid also applies to the income of dependants and attached children.

**Art. 204 M (individualised rates for a couple).** Optional ("sur option") until 31 August 2025; the default ("sauf
option contraire") from 1 September 2025 (loi n° 2023-1322, art. 19, II). Same method throughout:
- 2: the partner "qui a personnellement disposé des revenus les plus faibles" gets the rate of 204 H, I on their own
  income plus half the common income, the tax computed by art. 197, I, 1 to 4 "en retenant la moitié des déficits,
  charges et abattements ... ainsi que la moitié des parts".
- 3: the other partner: the household numerator less the tax on the first partner's own income at the first
  partner's rate and on the common income at the household rate, over the other partner's own income alone.

## 2. Datasets built

- `data/pas_grids.jsonl`: 18 grids (6 rate years × 3 zones: mainland, Guadeloupe/Martinique/La Réunion,
  Guyane/Mayotte), 19 bounds and 20 rates each, with the law, its commencement and the 204 H, II threshold as
  printed on 1 September (the lagging figure; `harness/pas_grid_check.py` holds the indexed ones).
  Transcribed from the consolidated statute (global-law record). Cross-check: BOFiP BOI-BAREME-000037-20250410
  (the only grid it prints, from 1 May 2025) equals the 2025 rows on all 57 bounds.
- `runs/pas/edges.jsonl`: 263 targeted returns, income 2020–2025, in 22 families (rate rounding, small tax, 204 H II
  threshold, couples, income outside the base, deficits).
- `runs/pas/prod_cases.jsonl`: those 263 plus 60 returns from the random sets' disagreements, sent to production;
  answers in `runs/pas/sim_prod.jsonl` (+ pages in `sim_prod.jsonl.html/`).
- `runs/pas/saved_pages.json`: 136 production pages saved by earlier runs (sim2, sim_refetch), matched back to their
  inputs and re-read for the rates.

## 3. Where the programs compute the rates

**M** (`mlang/ir-calcul/sources<year>/chap-taux.m`, rules 201600–201740): household rate `RASTXFOYER`
(numerator `PASNUMF = arr(IRTOTAL × min(1, (TSRASF + REVACOMP) / REVTOT))`, denominator `PASDENF`, IR `IRTOTAL`),
zero rate `INDTAZ` (res-ser1.m), individualised rates `RASTXDEC1`, `RASTXDEC2` (from `TXINDIV1`, `TXINDIV2`, the lower
earner chosen by `TXPASMIN`), dependants' default rates `RASTXPAC1..7` (the grids, with the 1.11 factor). All are
written by `cal<year> -completion -m p` in the completed IRJ (`restituee` variables); `harness/pas_run.py` greps them.

**Lean** (`lean/FrTax/Withholding.lean`): `PAS.household` (204 H I and II), `PAS.individual` (204 M),
`PAS.gridLows`/`PAS.defaultRate` (III). `Main.lean` adds to each return in scope: `TXFOYER`, `TXDEC1`, `TXDEC2`
(décote of couples, the words of art. 197, I, 4), `TXDEC1S`, `TXDEC2S` (décote of single people), `TXFOYER61`
(diagnostic: a tax under 61 € counted as nil), `PASNUM`, `PASDEN`, `PASIR`, `PASX`, `PASTOT`, `PASII`; and a line
`G;id;rateYear;zone;base` prints `GRID=`. Box `8OT` (or `BTINDIR`) states that the previous year's tax was nil.
Scope: every box of the income-tax model except foreign-source salaries and pensions (1AF, 1AG, 1AL, 1AM rows) and
art. 62 pay (1GB row); individualised rates not for households with flat-levy micro income.
Readings where the statute is silent, taken from M: the household pension-allowance cap is shared as M shares it
(minimum allowances kept, the rest pro rata, the last pensioner takes the remainder); alimony's share of the
allowance pro rata with the last box taking the remainder; the numerator rounded to the euro; each half of common
income and of each deduction rounded separately; equal incomes give both partners the household rate; the lower
earner is the one with the lower net income of art. 204 A.

## 4. Scoreboard

Rates compared to the tenth of a point. "Lean" is the statute reading (décote of couples for 204 M, no 61 € rule,
indexed II threshold since the W3 fix); "Lean S" is the same model with the décote of single people for 204 M.
Rows 5 and 6 changed with the W3 fix (before → after); every other row was rerun and is unchanged.
Scripts: rows 2–5 `harness/pas_run.py recheck` (+ `pas_family.py` for 5 and 6), rows 6–9 `harness/pas_score_saved.py`
(saved simulator answers only; nothing is sent), row 1 `pas_grid_lean.py` and `pas_grid_check.py`, row 11
`pas_regress.py`. Outputs of the fix: `runs/pas/w3fix/`.

| # | Benchmark | Lean | M | Production (arbiter) |
|---|---|---|---|---|
| 1 | Default grids vs statute text, cell by cell (18 grids, 720 probes: each bound and one euro below, 0 and the top) | 720/720 | 701/702 cells (bounds + rates of the dependants' grid, income 2020–2025) | BOFiP BOI-BAREME-000037 (2025 grid) = statute, 57/57 |
| 1b | 204 H, II threshold per part, income 2020–2025 | 6/6 = BOFiP = M (was 0/6: the printed figures) | 6/6 = BOFiP | (= M on all 30 threshold returns) |
| 2 | Random households income 2020–2023 (runs/old, 19 748 accepted by M), household rate | 19 643/19 748 = M (the 105: 61 € rule) | — | — |
| 3 | Random households income 2024–2025 (runs/final, 98 868), household rate | 98 235/98 868 = M (the 633: 61 € rule) | — | — |
| 4 | Same sets, individualised rates (36 779 couples) | 27 250 = M; Lean S 36 254 = M (the 525: 61 € rule individual 356, household 61 € rule 163, quarter-part cap rounding 6) | — | — |
| 5 | Targeted edge set (263 returns, 22 families, M accepts 258), household rate | 222/258 = M (was 204/258; the 36: rounding margin 30, 61 € rule 6) | — | — |
| 6 | Production, targeted + random disagreements (323 returns, `runs/pas/sim_prod.jsonl`), household rate | 269/323 (was 251/323; the 54: rounding margin 30, 61 € rule 24) | 318/318 computed (refuses 5 that production computes) | — |
| 7 | Production, individualised rates (53 couples; production prints them only for income 2024–2025) | 30/53; Lean S 43/53 | 53/53 | — |
| 8 | Production pages saved by earlier runs (131 random households: 118 of income 2024–2025, 13 of 2020–2023), household rate | 130/131 | 128/131: = production on all 128 it computes; refuses 3 with anomaly IM15 (amounts of 0.6–5 M€), which production computes and Lean equals | — |
| 9 | Same, individualised rates (34 couples printed; Lean computes 29, the other 5 have flat-levy micro income) | 21/29; Lean S 29/29 | 33/34 (the 34th refused, IM15) | — |
| 10 | OpenFisca-France | no withholding-rate variable | | |
| 11 | Income-tax regression after the W3 fix (Lean before vs after, `runs/pas/w3fix/regress/`) | 98 868/98 868 and 19 748/19 748 returns identical on the 12 compared figures, and on the whole output line, withholding fields included (so RESULTS #7, #8 unchanged: 98 849/98 868, 19 741/19 748 vs M) | | |

On every household rate where the two can be compared (318 returns), production equals M. Production equals
Lean on the 5 returns M refuses (actual expenses above salary with a pension, income 2022–2025, M anomaly IM2001;
a couple with 1BJ = 0, income 2022). Every Lean–M difference in benchmarks 2 to 7 falls into one of the classes
below; none is left unclassified.

## 5. Disagreements, with the arbiter's verdict

W3 was an error of the Lean model, now fixed; it is described after W6 under "Lean error, fixed".

**W1. Tax under 61 € gives a nil rate in M (and production); the statute has no such rule.** M: `IRTOTAL = (IDRS3
+ IBATMARG − IDEC) × positif_ou_nul(... − SEUIL_61)` (chap-taux.m, rule 201600); the same 61 € test zeroes the
individual tax (`IRINDIV1`). Art. 204 H, I, 1 takes the tax "résultant de l'application des règles prévues aux 1 à 4
du I de l'article 197"; the 61 € of art. 1657, 1 bis governs collection, and 204 H, II gives its own, narrower zero
rule. Example (income 2020): single, salary 16 695 €, tax after décote 11 €: statute 11 / 16 695 = 0.07 % → 0.1 %;
M and production 0.0 %. Frequency: 105 of 19 748 and 633 of 98 868 random households (household rate); 356 couples'
individualised rates. **Verdict: production = M** on all 24 differing returns sent (18 from the random sets, 6
targeted) and on the 4 sent for the individual rule; also 1/1 in the saved pages. Where the tax ends below 61 € the rate production transmits is nil, not the 0.1–0.3 % of the statute's
words. Lean's `TXFOYER61` reproduces it (98 868/98 868 and 19 748/19 748 equal to M).

**W2. M rounds a rate up when its exact value ends in .x4995 to .x4999 (income 2020–2024); the statute rounds down.**
Same mechanism as F5: `RASTXFOYER = arr(PASNUMF / PASDENF × 100 × 10) / 10`, and Mlang's `arr` adds 50 × 10⁻⁶
before flooring. Art. 204 H, I, 3: "arrondi à la décimale la plus proche. La fraction de décimale égale à 0,50 est
comptée pour un", so 25.44996 % is 25.4 %. Example (income 2020): single, salary 115 112 €, dividends at the scale
11 799 €: numerator 29 296 €, denominator 115 112 € → 25.44996 %: statute 25.4 %, M 25.5 %. The 2025 code computes
`arr(inf(PASNUMF / PASDENF × 10000) / 10) / 10` (truncation to 1/100 of a point first), and the margin disappears:
the 6 such returns of income 2025 agree. Exact .x5 rates (23 returns) agree everywhere. **Verdict: production = M on
all 36** (30 different from the statute, 2020–2024). Random households hit it rarely (0 in 118 616).

**W4. The décote in the individualised rate (art. 204 M, 2): M and production use the single-person décote.** The
statute applies "les règles prévues aux 1 à 4 du I de l'article 197" with half the parts; art. 197, I, 4, a gives
the larger décote base to "contribuables soumis à imposition commune", which a married or PACS partner is. M:
`DECPAS = min(max(arr(SEUIL_DECOTE1 − DECINDIV × 45.25 %), 0), ...)` (SEUIL_DECOTE1 = single). Example (income 2020):
couple, salaries 60 000 € and 18 000 €: the lower earner's tax with one part is 199 € after the single décote
(M's IRINDIV1) → 1.1 % for that partner and 14.8 % for the other (M, production); the couples' décote wipes the 199 €
→ 0.0 % and 15.1 %. Frequency: 7 694 + 1 666 = 9 360 of 36 779 random couples. **Verdict: production = M.** Of the
24 production couples where the two décotes give different rates, 17 equal the single décote and none the couples'
décote for a reason of its own: the 4 that equal the couples' décote are W1 cases (the lower earner's tax under
61 €, which production zeroes and the couples' décote happens to wipe too), the other 3 are W5. Saved pages: 29/29
single décote. The statute's words support the couples' décote; production does not apply it.

**W5. Quarter-part cap in 204 M (income 2020–2024): M rounds the cap with the tax; its 2025 code rounds it on its
own.** With half a couple's parts, 2.5 parts give 1.25 parts and a cap of half a half-part (e.g. 879.50 € in 2023).
2020–2024: `IRINDPAS2 = arr(REVINDIV × TX − PLABAR − 2 × PLAF_DEMIPART × (NBPTPAS − 1))`; 2025:
`arr(REVINDIV × TX − PLABAR) − arr(2 × PLAF_DEMIPART × (NBPTPAS − 1))`. Lean rounds the cap on its own in every year,
as it does for the household (art. 1657, 1: the amount of a reduction is rounded). Example (income 2023): PACS, one
child, salaries 65 250 € and 48 522 €: lower earner's tax 5 508 € (M, one rounding) or 5 507 € (separate) → 11.4 %
vs 11.3 %; the other partner 15.3 % vs 15.4 %. 6 of 36 779 random couples. **Verdict: production = M on all 5
printed (income 2024)**: production follows each year's program. Not explained by the statute, which is silent.

**W6. M's dependants' grid for income 2025 (rate year 2026): 8 739 € where the statute says 8 789 €.**
`RASTXPACi` (chap-taux.m line 627–628, sources2025m_3_11): `positif_ou_nul(REVMENSPACi − 7037) × positif(8739 −
REVMENSPACi) × TXPAC20 + positif_ou_nul(REVMENSPACi − 8739) × ... × TXPAC24`. Art. 204 H, III, 1, a as amended by loi
n° 2026-103: "Supérieure ou égale à 7 037 € et inférieure à 8 789 € | 20 %". Probe: a dependant's BNC profit of
94 550 € → monthly base 8 746 € → M 24 % (acompte 2 099 €/month), statute 20 % (1 749 €). Every other cell of the 18
grids in M equals the statute (701/702). **No arbiter**: the simulator does not print dependants' acomptes. It is a
departure from the printed statute, affecting monthly bases 8 739–8 788 € only.

### Lean error, fixed

**W3. Lean error, fixed (17 November 2026): the 204 H, II threshold.** Not a DGFiP departure. Lean took the per-part
figure printed in the consolidated CGI for each rate year (25 654 € for income 2020 … 29 310 € for income 2025).
The statute indexes that figure every year ("indexé chaque année comme la limite supérieure de la première tranche
du barème"), and the printed one is only updated a year late, by codification decree. M (`RFRPARQF`), the production
simulator and every BOFiP version (BOI-IR-PAS-20-20-10, 20220516 to 20260407, § 180 in 2026) use the indexed figures:
25 705, 26 065, 27 473, 28 792, 29 310 and 29 574 € per part for income 2020 to 2025 (table in section 1; AUTHORITY.md,
W3). `PAS.zeroRateThreshold` now holds those figures. They are the only figure of the II test. There is no half-part
or quarter-part amount and no second RFR condition, and the rest of the test (tax nil for the last two years,
RFR < X × parts, strictly) was already M's. Example (income 2020, box 8OT ticked, tax nil after a home-help credit, RFR
25 654 €, one part): Lean before 6.0 %; now 0.0 %, as M and production. Effect: the 18 returns in the window
[printed, indexed) of the edge set (3, 3, 4, 2, 3, 3 for income 2020–2025) now equal M (edge set 204 → 222/258);
production set 251 → 269/323, its threshold family 12 → 30/30. No random household is affected (none lies in the
window with 8OT), and every other output is byte-identical (row 11).

**Agreements worth stating.** Every other family agreed in all three programs: income outside the base (dividends
and gains at the scale, flat-levy micro income under art. 197 C), property income and annuities in the base, alimony
with a pension (its share of the allowance), a property deficit on global income, equal incomes (both partners get
the household rate), incomes one euro apart, equal pensions under the household allowance cap (M's sharing makes
them equal), very unequal couples, a lower earner with pensions only, a dependant's salary as common income, charges
halved. Actual expenses above the salary with a pension: M refuses from income 2022; production and Lean agree (2.8,
2.5, 2.4, 2.3 % for 2022–2025).

**Not done.** Non-residents (197 A; M's 20 %/30 % minimum rates), foreign income with treaty credits (8VM, CIPAS),
quotient income, the art. 62 / foreign-salary boxes, the employer-side adjustments of III, 1, d (pay period, short
contracts), the IV option for the default rate, and individualised rates with flat-levy micro income are outside
the Lean model. Production prints individualised rates only for income 2024–2025, so W4 and W5 are arbitrated
only for those years.

## 6. Theorems (Withholding.lean; no sorry, no native_decide)

- `rateOf_nonneg`, `rateOf_mono_num`: the rate is non-negative and non-decreasing in the tax.
- `rateOf_le`, `rateOf_le_full`, `rateOf_le_45`: a rate is at most c tenths of a per cent when 1000 × tax ≤ c × income;
  so at most 100 % when the tax is at most the income, at most 45 % when the tax is at most 45 % of it.
- `countLe_mono`, `countLe_le`, `countLe_zero`, `gridRates_mono`, `gridRates_le_43` (kernel `decide`).
- `gridRate_mono`: every grid is non-decreasing in the monthly base; `gridRate_le_43`: no default rate exceeds 43 %;
  `gridRate_zero`: nil below the first bound.
- `grids_wellFormed` (kernel `decide`): all 18 grids have 19 strictly increasing bounds.
- `defaultRate_mono`: in every rate year and zone, the default rate is a non-decreasing function of the base, at most 43 %.
- `#print axioms` on all fifteen (after the W3 fix, `runs/pas/w3fix/axioms.txt`): `propext` and `Quot.sound` only
  (`gridRates_mono`, `gridRates_le_43`: `propext`; `grids_wellFormed`: none); no `sorryAx`, no `Classical.choice`,
  no `Lean.ofReduceBool`. The same file evaluates `zeroRateThreshold` for 2020–2025: [25705, 26065, 27473, 28792,
  29310, 29574].
