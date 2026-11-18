# HMRC tax-kalculator and GOV.UK's Child Benefit tax calculator vs the Lean UK model, 2025-26

Date: 18 November 2026.

## 1. Setup and versions

| Item | Version / source |
|---|---|
| hmrc/tax-kalculator | tag **2.16.1**, commit `26190cf52c4e93031486d228c15f057137c35e08` (4 June 2026), `src/tax-kalculator` |
| alphagov/smart-answers | `main` at `be649a544cf720a708c29e0bbfc07510e5af0796` (18 Nov 2026), `src/smart-answers` |
| JDK | Eclipse Temurin 17.0.21+9 (adoptium.net), `opt/jdk17`; Gradle 8.9 via the project's wrapper |
| Ruby | 4.0.8 (smart-answers' `.ruby-version`), built from cache.ruby-lang.org into `opt/ruby`, without libyaml |
| Pillow | venv `opt/venv` |
| Lean | 4.35 core. Our model `~/cmp/uk/lean` (exe `uktax`, read only); PAYE routine copied read-only into `lean/` (exe `payegrid`) |

**tax-kalculator build.** The upstream Gradle build needs `uk.gov.hmrc.gradle:spotless:1.1.1` from a private GitHub
Packages registry (credentials) and iOS targets. `kalc-build/` is a minimal JVM-only build with the same Kotlin
(1.9.24) and library versions, sources copied verbatim (`commonMain`, `commonTest`, `jvmTest`), plus a driver
`kalc-build/src/jvmMain/kotlin/driver/Driver.kt` calling the public `Calculator(...).run()` and printing every
`CalculatorResponsePayPeriod` field. Upstream's own tests: **810/810 pass** in this build. Wrapper: `scripts/kalc`.

**smart-answers.** `scripts/hicbc_run.rb` loads the real, unmodified
`lib/smart_answer/calculators/child_benefit_tax_calculator.rb` outside Rails with small shims (Rails.root,
HashWithIndifferentAccess, a reader for the flat rates YAML since this Ruby has no libyaml). Inputs are `BigDecimal`,
what `SmartAnswer::Money` holds (`Money#to_f` delegates to it), so the code's `.to_f` path is the website's. Ruby
`Float` is IEEE 754 binary64, as on the server. Running Ruby was practical, so nothing was ported.

## 2. Coverage

### tax-kalculator vs Lean (`scripts/compare_kalc.py`, results `results/kalc_*`)
- **Statute grid, 20,490 cases** (2025-26): annual wages £0-£200,000 every £25 plus every threshold ± £1, £2, £9,
  £10 (PA £12,570/£12,579, PT, UEL £50,270, £60,000, £80,000, taper £100,000-£125,158, £125,140, Scottish edges
  £15,397, £27,491, £43,662, £75,000); rUK and Scotland; age 40 and pension age; default code (tapering) and
  user-supplied 1257L; 1257T; monthly (668) and weekly (771) pay; pension contributions 5 % and £200 a month (net pay
  arrangement: income tax on pay less contribution, NI on pay). Compared with `uktax` (ITA 2007 s. 23 liability,
  Class 1 NI on the annual earnings period).
- **Code grid, 1,755 cases**: 27 codes (1257L, 1257T, 0T, 1383M, 1131N, K100, K475, K2000, BR, D0, D1, NT, 1257L M1,
  C1257L, CBR, CD0, CD1, CK475, S1257L, S1257T, S0T, SBR, SD0-SD3, SK475) x monthly pay £0-£16,000 every £250, vs
  HMRC's PAYE tax-table routine (our Lean copy, which reproduces HMRC's 2025-26 PAYE test data, 168 payments within
  1p) over 12 equal monthly payments.
- An exact-arithmetic replica of the kalculator's conventions explains every difference (residual < 10^-6); the same
  replica with the statute's settings reproduces `uktax` to the penny in all 20,478 computed cases.

### Child Benefit tax calculator vs ITEPA s. 681C vs Lean (`scripts/compare_hicbc.py`, `scripts/hicbc_partial.py`)
- 88,004 cases: whole-pound adjusted net income £59,000-£81,000 x 1-4 children, 2025-26: Ruby class vs exact s. 681C
  vs `uktax` (Lean = exact statute in **all 88,004**).
- 404 pence probes (-1p, 0, +1p, +99p at each of the 101 steps) for 2023-24, 2024-25, 2025-26, 2026-27.
- 20,000 random cases with allowable deductions (x 1.25) and other deductions.
- 3,000 random partial-year claims (1-4 children, start/stop dates) vs a week-by-week reading of the rates.

## 3. Every difference and its classification

(a) genuine error in the official code; (b) error in our model; (c) documented scope or convention; (d) ambiguous.

### tax-kalculator

| # | Difference | Cases | Size | Class |
|---|---|---|---|---|
| K1 | L/M/N/emergency codes use PAYE Free Pay = code x £10 **+ £9** (£12,579 for 1257L); the statute allows £12,570 (ITA s. 35(1)) | 8,852 of 20,478 | £0.19-£4.05 less tax | (c) the PAYE tax-table routine (spec para 4.3.1(b)); explicit in code (`getTrueTaxFreeAmount`) |
| K2 | Taper not rounded (s. 35(3) rounds the remaining allowance up to £1), applied to £12,579 | 2,505 (with K1) | <= £4.05 | (c) estimator convention |
| K3 | No taper when `userSuppliedTaxCode = true` | 400 (1257L, 1257T above £100k) | up to £6,037.92 | (c) documented in README |
| K4 | Weekly/monthly = annual / 52 or / 12; NI on annual thresholds (£1,048 a month: £0.04 NI where the monthly PT gives nil) | all period cases | pennies | (c) annual estimator; our model also uses the annual period (FINDINGS F8) |
| K5 | L codes vs 12-month PAYE run | 361 of 1,728 | <= £0.48 | (c) period rounding |
| K6 | Wage £0 rejected (`InvalidWagesException`) | 39 | - | (c) validation |
| K7 | Pension deducted before tax, NI on gross | 1,600, all explained by K1/K2 | - | (c) net pay arrangement (FA 2004 s. 193) |
| **K8** | **T codes (T/ST/CT) built without the £9 but `getTrueTaxFreeAmount()` still subtracts it: `taxFree` £12,561 for 1257T, tax £9 x marginal rate above the same L code and PAYE. K codes (K/SK/CK) without the £9: tax £9 x marginal rate below PAYE** | 433 code cases (120 T, 313 K) + 200 T statute cases | £1.80-£4.50 | **(a) issue 03** |
| **K9** | **Taper test uses the current year's default code: TaxYear 2020 (default 1250L) never tapered** | 2020 only (found reading the code; reproduced via the API) | £4,000 at £120,000 | **(a) issue 04** |
| K10 | `employersNI` for 2024 onward uses 2023 bands (13.8 % above £9,100); 2025-26 is 15 % above £5,000 (HMRC rates and thresholds for employers 2025-26). £50,000: £5,644.20 vs £6,750.00 | every case | large | (d) code says "We don't expect to use this value so we have stopped updating it"; README still lists the field. A question at most; not drafted |
| K11 | Pension "annual allowance" check £10,000 for 2020-2026 (FA 2004 s. 228: £40,000 to 2022-23, £60,000 from 2023-24; £10,000 is the money purchase annual allowance from 2023-24) | flag only | no effect on figures | (d) warning threshold; not drafted |
| K12 | rUK/Scottish band edges, NI rates and thresholds 2025-26 | - | none | equal |
| - | Employee NI | 20,478 | equal in all | - |

Income tax equal to the penny in 8,721 statute-grid cases; every other case explained (residual 0).

### Child Benefit tax calculator (GOV.UK)

| # | Difference | Cases | Size | Class |
|---|---|---|---|---|
| **H1** | **Percentage `((ANI - L)/(U - L) * 100.0).floor` in binary64: one percent short at exactly £65,800, £71,400, £71,600 (2024-25 on) and £52,900, £55,700, £55,800 (2013-14 to 2023-24)** | 12/88,004; 12 probes (3 per year x 4 years) | 2025-26: £13-£41 too low | **(a) issue 01** |
| **H2** | **Total child benefit not rounded down to whole pounds before the percentage (s. 681C(3)(a))** | 23,197/88,004; 441/1,616 probes; 3,239/20,000 with deductions; 574/3,000 partial-year | £1 too high, never lower | **(a) issue 02** |
| H3 | Benefit totals (52 Mondays in 2025-26; 53 in 2026-27), partial-year weeks, eldest-child rate per week | 0 differences in 3,000 partial-year cases | - | equal; the date convention (a week counts if its Monday is in [start, stop]) is the calculator's reading of user dates (c) |
| H4 | "No charge below £60,200" message; 100 % at £80,000 | - | - | equal |


## 4. Our side (class (b))

None found. `uktax` equals the exact statute replica in all 20,478 income tax / NI cases and all 88,004 HICBC cases;
every kalculator difference is explained by a documented convention or by issues 03-04. Limits (not errors): our
liability model has no tax codes (only the PAYE routine has them), no employer NI, no student loans, no partial-year
child benefit and only 2025-26; K10, K11, student-loan tables and 2020/2026 parameters were checked only where stated.
