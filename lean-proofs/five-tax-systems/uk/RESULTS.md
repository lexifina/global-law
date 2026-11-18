# UK income tax 2025-26 in Lean — results

Lean model `lean/` (UkTax): income tax, capital gains tax, Class 1/2/4 National Insurance, child benefit and the high
income child benefit charge for 2025-26, England, Wales and Northern Ireland, and Scottish taxpayers (ITA 2007 s. 11A)
as an option, written from the statute (ITA 2007, ITEPA 2003, TCGA 1992, SSCBA 1992, FA 2004, Finance Acts 2021 and
2025, S.I. 2001/1004, S.I. 2006/965), with HMRC's PAYE tax-table routine for withholding. Lean 4.35, core only. 2,320
hand-written lines + 603 generated (HMRC NI and PAYE test data); 94 theorems and 31 `#guard` checks; no `sorry`, no
`native_decide`; `#print axioms`: `propext`, `Classical.choice`, `Quot.sound` only. Findings F1–F10 and the Lean errors
L1–L2 are in FINDINGS.md; the interface in EXAMPLE.md. Harness `harness/`, runs `runs/`.

## 1. Official figures and worked examples (all pass)

| # | Source (saved in `refs/`) | Checked | Where |
|---|---|---|---|
| 1 | HMRC, Income Tax rates and allowances, column 2025 to 2026 | 15 parameters (allowances, limits, rates, dividend rates) | `hmrc_income_tax_table_2025` |
| 2 | HMRC, Rates and thresholds for employers 2025 to 2026 | PT/UEL weekly, monthly, annual; monthly LEL £542 from reg. 11(2)(b) "4 1/3", rounded up | `hmrc_employer_rates_2025`, `lel_monthly`, `pt_equivalents` |
| 3 | HMRC, Rates and allowances: NICs, tables 3.1–3.2 | Class 2, small profits threshold, Class 4 limits and rates | `hmrc_ni_self_employed_2025` |
| 4 | gov.uk/income-tax-rates | allowance nil at £125,140; £35,000 taxable income example | `pa_zero_at_125140`, `#guard` |
| 5 | gov.uk/apply-tax-free-interest-on-savings | £16,000 wages + £200 interest (starting rate £1,570 left); "less than £17,570"; £1,300 interest = £60 | 5 `#guard` |
| 6 | HMRC Dividend Allowance factsheet (2016-17 figures) | Examples 3, 4, 5 and **6 (s. 25(2): allowance set against dividends, £6,725, not £7,100)** | 6 `#guard` |
| 7 | gov.uk/tax-on-dividends (2026-27 rates) | £3,000 dividends + £29,570 wages | `#guard` |
| 8 | gov.uk/marriage-allowance | £11,500 / £20,000 couple: transferor taxed on £190, partner on £6,170, saving £214; "up to £252" | 3 `#guard`, `ma_252` |
| 9 | GOV.UK Personal Allowances: adjusted net income | Bill: net income £105,000 → allowance £10,070; Clara: net income £65,250, ANI £64,000 | 4 `#guard` |
| 10 | gov.uk/child-benefit-tax-charge; S.I. 2025/292 | 1 % per £200 over £60,000, all at £80,000; child benefit for 1–4 children | `hicbc_points`, `child_benefit_k` |
| 11 | GOV.UK Capital Gains Tax, examples 1 and 2 | £1,728; £10,842 | 2 `#guard` |
| 12 | HMRC Capital Gains Manual CG21204 example (2018-19 figures) | Gift Aid extends the band: CGT £6,210, band £84,500 | 2 `#guard` |
| 13 | HMRC Pensions Tax Manual PTM044220 | £1,000 contribution: £200 at source + £200 higher-rate; £100/£80 monthly | 4 `#guard` |
| 14 | **HMRC payroll test data 2025-26, NIC v1.1** (machine-readable) | **448/448 rows** (categories A B C H J M V Z × weekly, 2-weekly, 4-weekly, monthly), employee's contribution to the penny | `hmrc_ni_test_data` |
| 15 | same, directors' NIC test data v1.0 | annual earnings period, £52,000 → £3,050.60 | `director_annual_52000` |
| 16 | HMRC CWG2 2025-26 "round ... to the nearest penny, rounding down exact amounts of £0.005" | 401/448 of HMRC's own test rows (F8) | `cwg2_rule_rows` |
| 17 | **HMRC payroll test data 2025-26, PAYE Tax v1.0** + Specification for PAYE tax table routines (`PAYE.lean`) | 22 sheets, 168 payments (rest of UK, Wales, Scotland; cumulative and Week 1/Month 1; L, K, BR, D0–D3, NT and large codes): **159 exact, all 168 within HMRC's stated £0.01 tolerance** (the 9: Scottish monthly payments, a penny off) | `hmrc_paye_test_data` |
| 18 | GOV.UK Married Couple's Allowance: "between £436 and £1,127 a year" (2025-26) | full amount to £37,700 of adjusted net income, minimum from £51,520 | `mca_range_2025` |

PAYE is the withholding routine, not the liability; it shares the 2025-26 bands and rates, so this checks those
parameters (and the Scottish bands) against HMRC's own test vectors.

## 2. PolicyEngine-UK 2.179.1 as referee (random canonical households)

Lean (`uktax`) and PE (`harness/pe_run.py`, same household mapping, relationships stated) on four generated sets;
equal within £1 on income tax, CGT, NI, child benefit and HICBC.

| Set | n | Lean (statute) = PE, every figure | Lean with PE's 5 conventions (`--pe`) = PE |
|---|---|---|---|
| mixed | 5,000 | 4,207 (84 %) | **5,000** |
| investment-heavy | 3,000 | 2,373 (79 %) | 2,998 (2: F6) |
| threshold edges | 3,000 | 2,495 (83 %) | 2,998 (2: F6) |
| wages only | 2,000 | 1,971 (the 29: married couple's allowance) | **2,000** |
| Scottish taxpayers (mixed, `"region": "scotland"`) | 2,500 | 2,070 (83 %) | **2,500** |

NI, child benefit and HICBC: 15,500/15,500 equal (all sets, after fix L2). Every statute-vs-PE difference is removed by switching
on one of PE's conventions (`harness/attribute.py`, `runs/attribution.txt`):

| PE convention (finding) | mixed | invest | edges | simple | range (Lean − PE) |
|---|---|---|---|---|---|
| relief at source as a deduction (F4) | 429 | 339 | 251 | – | −£3,708.40 … +£1,532.70 |
| no Gift Aid charge (F5) | 179 | 103 | 94 | – | +£2.50 … +£4,981 |
| no married couple's allowance (F5) | 73 | 43 | 53 | 29 | −£1,127 … −£143.62 |
| marriage allowance = unused allowance (F3) | 51 | 58 | 48 | – | −£252.01 … +£86.60 |
| several of these | 61 | 84 | 59 | – | |

Scottish set (2,500): relief at source 221, Gift Aid charge 94, married couple's allowance 44, marriage allowance 34,
several 37: the same five conventions, nothing else.

## 2b. OECD Taxing Wages 2026 (UK, 2025 = tax year 2025-26) as referee

Source: OECD SDMX API, dataflow `OECD.CTP.TPS,DSD_TAX_WAGES_DECOMP@DF_TW_DECOMP` (`refs/oecd/gbr_decomp_2025.csv`):
4 household types (single / one-earner married couple, without / with 2 children) × 201 earnings levels (50 %–250 % of
the average wage, £55,982.59), 804 cases. `harness/oecd_compare2.py`; the model gets the wage rounded down and up to
whole pounds.

| Figure | Agreement |
|---|---|
| Employee social security (Class 1) | **804/804** within the whole-pound bracket (OECD uses the annual thresholds, like the model) |
| Central government income tax | 780/804 within the bracket; the other 24 (taper band) equal OECD's to the penny once the allowance is not rounded up: OECD does not apply s. 35(3) (up to 20p) |
| Marriage allowance | applied by both for one-earner couples (e.g. 50 % AW: £2,832.26 = single's tax − £252) |
| Child benefit (net of HICBC) | differs by convention: OECD annualises £43.30 × 365/7 = £2,257.79 (the statute's 2025-26 has 52 Mondays: £2,251.60, ITEPA s. 681H(3)); OECD's HICBC is continuous (no whole-percent or whole-pound rounding, s. 681C(3); up to £20.23 apart); at 100 % the statute leaves the 60p of the odd pence (OECD nil); below about 80 % (couple) / 68 % (single) of AW OECD adds Universal Credit (not in this model) |

## 3. The s. 25(2) search, checked independently

`harness/check_alloc.py`: a separate Python implementation of Step 4; for each of 13,587 people with savings or
dividends, 300 random feasible allocations of the allowances plus the corners: no sample ever beats Lean's
allocation; in 236 cases Lean's (a break-point vertex) is strictly cheaper than every sample. A stress set for the
search (`runs/r_alloc.jsonl`: 3,000 single adults with wages, interest and dividends around the 0 % bands and the
limits): Lean = PE on 3,000/3,000 (PE's conventions; PE never cheaper than Lean), and 500 random allocations for each of
2,857 people never beat Lean (189 strictly worse than Lean's).

## 4. Readings (how many households another reading changes; income tax + CGT)

| Reading | mixed (5,000) | invest (3,000) | edges (3,000) | simple |
|---|---|---|---|---|
| s. 12B(8) by its words (F1) | 36 (−£430 … −£6.20) | 63 (−£200 … −£0.40) | 198 (−£400 … −£2.40) | 0 |
| s. 192(4) by its words, main rates only (F2a) | 27 (+£33.50 … +£1,799.20) | 82 (+£6.25 … +£9,893.50) | 97 (+£0.14 … +£2,245.67) | 0 |
| s. 192(4) unconditional, CG21204/PE (F2b) | 14 (−£1,513.44 … −£23.88) | 69 (−£1,532.70 … −£0.72) | 37 (−£556.32 … −£0.06) | 0 |

## 5. Monotonicity of the full household model (`harness/mono_scan.py`)

Each household, each income (adults' wages, profits, pension; interest, dividends, rent, gains) raised by £1, £100,
£2,000: 79,323 perturbations of 3,500 households.
- Income tax + CGT never falls under the default reading except through the s. 192(4) condition (F2c): 0/34,008
  (mixed), 2/22,638 (invest), 6/22,677 (edges). Extending unconditionally removes these; the 4 that remain come from
  the FA 2004 s. 190 cap (more earnings make more of a contribution relievable, so CGT falls; −£4.02) and from the
  harness's pro-rata split of contributions (−£0.37).
- Reading s. 12B(8) and s. 192(4) by their words (`--literal`): falls in 4 (invest) and 17 (edges) perturbations, down to −£1,345.67.
- The contract's `incomeTax` (liability less relief at source) falls when earnings rise in 0.2–0.6 % of perturbations:
  relief at source grows with relievable contributions (s. 190), by design. The s. 23 liability alone falls when
  gains rise (the s. 424 Gift Aid charge counts CGT): by design.

## 6. Theorems (lean/UkTax/Theorems.lean; all inputs unless stated)

| Theorem | Statement |
|---|---|
| `liability_nsOnly` | bridge: for anyone with non-savings income only, the model's liability is the closed form |
| `nsTax_mono`, `liability_mono_nsOnly` | income tax is non-decreasing in income (non-savings income) |
| `taper_60` | £100,000–£125,140: every £2 costs exactly £1.20 (60 %) |
| `taper_one_pound` | pound by pound 40p and 80p in turn (allowance rounded up, s. 35(3)) |
| `below_taper_40`, `above_taper_45`, `taper_band_exact` | 40 % below, 45 % from £125,140, the band is exactly [£100,000, £125,140] |
| `hrl_is_taper_end` | any year with s. 10(5A)'s formula: the additional rate starts exactly where the allowance runs out |
| `nsTax_step_le_80p` | continuity: £1 more income never costs more than 80p of income tax (no notches without savings, children or elections) |
| `nsTax_le_45pct`, `burden_le_wages` | income tax ≤ 45 % of income; income tax + Class 1 + HICBC ≤ wages (any wages, up to 30 children) |
| `taper_62_with_ni`, `combined_42_47` | with Class 1: 62 % in the taper band; 42 % below; 47 % above |
| `hicbc_mono`, `hicbc_le_cb` | the charge never falls with income and never exceeds child benefit |
| `hicbc_steps`, `hicbc_max_steps` (decide) | each £200 step of the charge: £13/14 (1 child), £22/23 (2), £31/32 (3), £40/41 (4) |
| `it_ni_200_in_hicbc_band`, `highest_marginal_four_children` | **£200-averaged marginal rate: taper band 62 %; HICBC band 49 % / 53.5 % / 58 % / 62.5 % for 1–4 children: with four children the HICBC band is the steepest** |
| `hicbc_notches` (decide) | the £1 notches: one child £13 at £60,200; four children £41 at £80,000 |
| `psa_cliff`, `psa_cliff_additional` (decide) | £1 more wages: +£100.20 (allowance £1,000 → £500), +£200.45 (£500 → nil) |
| `ma_cliff` (decide) | recipient one pound into higher rate: the couple's tax +£252.40 |
| `giftaid_charge_exceeds_income` (decide) | tax can exceed income: no income, £800 gift → £200 (s. 424) |
| `f1_psa_literal`, `f2_ras_literal`, `f2_literal_not_monotone`, `f2b_condition_cliff`, `f3_ma_full_transfer`, `f6_pound_125141` (decide) | the findings |
| `s25_allowance_against_dividends` (decide) | s. 25(2): £606.37 instead of £1,043.87 |
| `reg100_cap`, `cgt_income_26` (decide) | Class 4 annual maximum; extra income costs 26 % where gains straddle the band |
| `bestSlices_le_dflt`, `bestSlices_le`, `allocate_ns` | the search never does worse than the usual order or any candidate |
| `scot_50000`, `scot_vs_ruk_marginal` (decide) | Scottish taxpayer on £50,000: £9,013.80; marginal income tax + Class 1 per £1: Scotland 28 / 29 / **50 (£43,663–£50,270)** / 44 / 47 / **69.5 % in the taper band** / 50, rest of the UK 28 / 28 / 28 / 42 / 42 / 62 % / 47 |

## 7. Effective marginal rates (`harness/marginal_table.py`, `runs/marginal_rates.csv`)

One employee, k children, wages £0–£200,000 in £100 steps; burden = income tax + Class 1 − (child benefit − HICBC).
Average marginal rate over the HICBC band (£60,000–£80,000) and the taper band (£100,000–£125,100):

| | 0 children | 1 | 2 | 3 | 4 | taper band |
|---|---|---|---|---|---|---|
| rest of the UK | 42.0 % | 48.8 % | 53.3 % | 57.7 % | **62.2 %** | 62.0 % |
| Scotland | 44.8 % | 51.5 % | 56.0 % | 60.5 % | 65.0 % | **69.5 %** |

The steepest £100 step: 62 % (rUK, 0–1 children, taper band), 65 / 74 / 83 % (2 / 3 / 4 children: a £100 step that
crosses a £200 boundary of the charge); Scotland 69.5 %, 70 / 79 / 88 %.

## 8. Speed
Lean: 5,000 households in 2.0 s (0.4 ms each, one core). PolicyEngine: 98.7 s for 5,000 (batches of 500, ~20 ms each).
