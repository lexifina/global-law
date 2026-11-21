# Kenya (KE) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The SHIF minimum of KES 300 a month makes the health contribution regressive below KES 10,909 a month: 6 % of pay at KES 5,000 a month
- kind: statute-fault
- Social Health Insurance Regulations 2024 reg. 17(1)-(2): 2.75 % of 'the gross salary or wage of the household' but 'not, in any case, ... less than Kenya shillings three hundred per month'. A worker on KES 60,000 a year pays SHIF 3,600 (6.0 %), on 130,000 a year 3,600 (2.8 %); above 10,909 a month it is 2.75 % (exe ke-60k, ke-130k). The regulation also says 'of the household' while the employer deducts per employee (reg. 17(1)): the model deducts per employee.
- provisions: SHI Regulations 2024 reg. 17(1),(2); ITA s. 15(2)(ae)
- Lean: KeTax.shifMonth (#guard 10,000 -> 300; 20,000 -> 550)
- status: modelled

### F2 The personal relief exactly cancels the 10 % band: the first KES 288,000 of taxable income is in effect a zero band, and the relief is lost below it
- kind: loophole-known
- Head A para. 1 (28,800) = 10 % x 288,000 (Head B first band). The relief is a credit, not refundable: below 288,000 of taxable income part of it is wasted (kernel applyCredits_waste); a couple with one earner cannot use the second relief (individual taxation, s. 45 repealed).
- provisions: ITA s. 30, Third Schedule Heads A, B
- Lean: KeTax.person (#guard tax 288,000 = personalRelief)
- status: modelled

### F3 Since 27 December 2024 SHIF, the Housing Levy and NSSF are deducted before tax: the statutory top combined rate on wages is 37.8 %, not 39.25 %
- kind: model-fix
- Tax Laws (Amendment) Act 2024 s. 7 inserted s. 15(2)(ac) (Housing Levy) and (ae) (SHIF); NSSF counts as a registered-fund contribution (s. 22(8)) within s. 22A (30 % of pensionable income, 360,000). Above 9.6 M: 35 % x (1 - 0.0425) + 4.25 % = 37.8 % (scanner top-rate line, 10 x 6 M). Before the Act these levies were paid out of taxed income.
- provisions: ITA ss. 15(2)(ac),(ae), 22(8), 22A; TLA 2024 ss. 7, 8
- Lean: KeTax.person
- status: modelled; scan reproduces (37.8 %)

### F4 The 2025 NSSF ceiling is not in the statute: it is 2 x a KNBS average-earnings figure, and the year count depends on a commencement date the Act does not print
- kind: statute-fault
- NSSF Act 2013 Third Schedule: 'Year 3 | 8,000 | 2 times National Average Earnings'; 'National Average Earnings' is 'published by the Kenya National Bureau of Statistics in the Economic Survey for the prior year' (s. 2). Which 'year' 2025 is depends on the commencement date (not in the consolidated text read). A reader of the statute alone cannot compute the Tier II contribution; the model takes it as input.
- provisions: NSSF Act 2013 ss. 2, 20, Third Schedule
- Lean: KeTax.nssfMonth (input nssfUEL)
- status: flagged

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Contribute up to KES 30,000 a month (360,000 a year) to a registered pension or provident fund, deductible | recreated: NSSF inside the cap; extra contributions need an input | ITA s. 22A(1) as amended by TLA 2024 s. 8 |
| K2 | Post-retirement medical fund contributions up to 15,000 a month, deductible | not modelled: no input field | ITA s. 15(2)(ad) |
| K3 | Mortgage interest up to 360,000 a year on an owner-occupied home | not modelled | ITA s. 15(3)(b) (TLA 2024 s. 7(b)) |
| K4 | Insurance relief: 15 % of life/health premiums up to 60,000 a year | not modelled | Third Schedule Head A para. 2 |
| K5 | Shift income to a spouse (individual taxation; each has a 288,000 zero band through the relief) | recreated: filing-unit scanner: split gains | ITA s. 45 repealed, s. 30 |
| K6 | Pay the owner-manager in dividends (final withholding) rather than salary | not modelled: dividend rates not read | Third Schedule Head B para. 3 (rates not read) |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with scale 6,000,000 (Head B 32.5 % band)
- direct household checks with the exe (SHIF minimum, relief vs first band)
- Head B para. 1 compared in the 2025-07-01 and 2026-01-01 consolidations and in the Finance Act 2025 s. 30 text (bands unchanged)
- Tax Laws (Amendment) Act 2024 read for every section touching ss. 15, 22A and the Third Schedule

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Round W2 (improvement agent, 2026-11-20): W1 software-grid dev failures settled from the statute

### W2-1 The KES 15,400 gap is the NSSF Upper Earnings Limit, which the statute delegates (no change)
- kind: test-note
- The model already deducts NSSF (ITA s. 22(8), 22A), SHIF (s. 15(2)(ae)) and the housing levy (s. 15(2)(ac)), all in
  force from 27 December 2024 (Tax Laws (Amendment) Act 2024). kenya-payroll uses the NSSF Board's UEL (36,000 in January
  2025, 72,000 from February); the Act's Third Schedule says only "2 times National Average Earnings" for year 3 (s. 2:
  the KNBS Economic Survey figure), so the model keeps the input `nssfUEL` (default: Tier I only). Run with
  nssfUEL = 72,000: 1,080 of 1,080 dev within 1 % (16 exact; residual = January at 36,000, ~KES 750 per earner). NSSF's
  2014 notice (law/nssf_new_rates.html, fetched 2026-11-20) shows the Board's year-1 UEL 18,000 = 0.5 x 36,000: the
  Board has used a fixed NAE of 36,000, not a KNBS figure. Using its numbers would be a convention (rule 8).
- provisions: NSSF Act 2013 s. 2, s. 20, Third Schedule; ITA ss. 15(2)(ac), (ae), 22(8), 22A
- Lean: KeTax.nssfMonth (input nssfUEL)
- status: open (F4): an official dated UEL for 2025 is still needed

## Round W4 (improvement agent, 2026-11-20): W3 dev failures settled from the statute

### W4-1 NSSF Upper Earnings Limit 2025: no official dated figure found; no change
- kind: test-note
- Searched: nssf.or.ke (site search for "upper earnings", "72,000", "year 3", "February 2025"; the Employed Member page),
  the NSSF Annual Report and Financial Statements for the year ended 30 June 2025 (law/w4/nssf_ar_fy2025.pdf, 172 pp.,
  from nssf.or.ke): it confirms the "Rollout of year 3 statutory contributions under the NSSF Act Cap 258" in FY 2024/25
  but prints no limits. The Kenya Gazette and Kenya Law answer scripts with a WAF challenge (not bypassed). The Act's
  Third Schedule gives year 3 as "2 times National Average Earnings" (KNBS Economic Survey, s. 2). Both calculators use
  the Board's 72,000 (kenyaccounting all year; kenya-payroll from February): rule 8 would need their methodology, and a
  default needs a dated official figure. `nssfUEL` stays an input (default Tier I). kenyaccounting's year-3 limits for
  January 2025 are its simplification (recorded in software/ISSUES.md by the test agent).
- provisions: NSSF Act 2013 s. 2, Third Schedule
- Lean: KeTax.nssfMonth (unchanged)
- status: open (F4)

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: NSSF Act 2013 s. 20 (1) (b), Third Schedule (year 3 UEL = 2 x NAE); NSSF notices "Year 2 contribution rates, 2024" (UEL 36,000 = 1 x NAE) and "Year 4 (2026)" (UEL 108,000 = 3 x NAE), official secondary; the year-3 notice itself not found
- NSSF Tier II: default year-3 Upper Earnings Limit KES 72,000 a month (2 x NAE 36,000) when nssfUEL is not given. Before W5 the model booked no such contribution (or only an optional input); the W5a grids and the pattern A sweep flagged it (IMPROVE_W5 pattern A, `w5/pa/SWEEP.md`). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS. Open: NSSF: year-3 limits applied to all of 2025 (January 2025 was year 2: LEL 7,000, UEL 36,000).
- status: fixed

### W5A-2 Contribution follow-up (W5 pattern A, reviewer 3 pass 3, 2026-11-20)
- kind: model gap fixed from the statute / official secondary
- provisions: NSSF Act 2013 Third Schedule; NSSF Year 4 notice (18 Feb 2026): "the implementation of Year 3 contribution rates ended on 31st January, 2026" (reviewer 3 pass 3 row 127; gaa.go.ke copy `law/w5/nssf_year4_notice_gaa.pdf`); NSSF year-2 notice (UEL 36,000)
- NSSF contribution period: January 2025 at year-2 limits (LEL 7,000, UEL 36,000), February-December at year 3 (LEL 8,000, UEL 72,000), with the switch on. Switch: `"w5Contrib": false` still restores the pre-W5 outputs (0 of 300 random households differ).
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/KeTax/Verify.lean` (imported by the `KeTax` library and built; each guard evaluates `KeTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/KE.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | SHIF minimum of KES 300 a month: a worker on 60,000 a year pays 3,600 (6.0 %), on 130,000 the same 3,600 (2.8 %), 2.75 % above 10,909 a month; 12 shillings of annual pay bear 3,600 of SHIF (G: f1_shif_minimum); rescan second earner: 299 for the first unit. T: KeTax.shifMonth #guard 10,000 -> 300. S: SHI Regulations 2024 reg. 17(1)-(2) as cited by the model. |
| F2 | explained | Personal relief = the 10 % band: wasted below 288,000 (applyCredits_waste). |
| F3 | explained | Levies deducted before tax: model fix. |
| F4 | explained | NSSF ceiling outside the statute: statute fault (W4-1 open). |
| W2-1, W4-1, W5A-1, W5A-2 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: timing gain 31,002 = NSSF/SHIF floors and ceilings; income-type wedges are model gaps. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: SHIF minimum of KES 300 a month: 6 % of pay at KES 5,000 a month | cliff or notch | **new**: PwC Kenya describes the SHIF deduction (ITA s. 15(2)(ae), TLAA 2024), not the 300-shilling minimum or its regressivity; OpenAlex: not answered. | 2026-11-20: OpenAlex queries 'Kenya Social Health Insurance Fund minimum contribution 300 shillings regressive'; 'Kenya SHIF 2.75% contribution low income workers' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (kenya, 5 individual pages): 9 passages with the item's terms; Crossref IMF prefix 10.5089 'Kenya tax policy' (8380 records, titles only). Record: world/loopholes/africa_mena/search/KE-F1.json |

<!-- L1-VERIFICATION END -->

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- ceilings.py: ceiling at 0.08 AW (contribution rate 8.7 -> 2.8 %, combined marginal 23 -> 37 %); floor: contribution rate 9 % at 0.05 AW vs 4 % at 0.5 AW (only with the W5 contributions). Lead (statutory ceiling/minimum base; known pattern). `results/search/ceilings.md`.
<!-- R2-SCANNERS:END -->
