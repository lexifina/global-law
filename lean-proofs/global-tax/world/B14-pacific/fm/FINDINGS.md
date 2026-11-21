# Micronesia (Federated States of) (FM) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The $1,000 deduction of 54 F.S.M.C. 122 is withdrawn in full at $5,000 of wages: $1 more wage costs $61 (METR 6,100 % on that dollar; scanner 121.8 % on its grid)
- kind: statute-fault
- § 122(1): 'Every employee ... except those whose gross annual wages and salaries are $5,000 or more, shall be allowed a deduction of $1,000'. Tax at 4,999 = 239; at 5,000 = 300 (#guard). Scanner: notch 61 at 4,999 for singles and second earners.
- provisions: 54 F.S.M.C. 121, 122
- Lean: FmTax.wageTax (#guard)
- status: modelled; scanner reproduces

### F2 The social security ceiling is per employer per quarter: an employee with two jobs pays up to twice the maximum, with no refund provision in the chapters read
- kind: statute-fault
- 53 F.S.M.C. 603(15)(a): wages exclude remuneration 'in excess of $9,000 ... paid in a quarterly reporting period by one employer'. $50,000 from one employer: 2,700; split over two employers: 3,750 (#guard). The RMI act has a multi-employer refund (49 MIRC 132); the FSM chapters read do not.
- provisions: 53 F.S.M.C. 603(15)(a), 901
- Lean: FmTax.ssEmployee (#guard)
- status: modelled (input fmEmployers)

### F3 Employee or business? Contractors who are 'a business' pay 3 % of gross revenue (and $80 below $10,000) instead of 6-10 % of pay, and the Code's own annotations record the disputes
- kind: loophole-known
- 54 F.S.M.C. 112(1), (3), 141; the annotations to § 112 and § 121 cite Heston v. FSM, 2 FSM R. 61 and Rauzi v. FSM, 2 FSM R. 8 (expenses 'well below 10%' do not make a contractor a business). Gross revenue tax on 20,000: 380 vs wage tax 1,560.
- provisions: 54 F.S.M.C. 112, 121, 141
- Lean: FmTax.grossRevenueTax (#guard)
- status: modelled (self-employment read as gross revenue)

### F4 The wage tax bands date from the Trust Territory Code (COM PL 7-67): $11,000 and $5,000 have never been indexed
- kind: statute-fault
- Source notes to §§ 121-122: 'COM PL 7-67 § 1(1) ... TT Code 1980, 77 TTC 252'. No later amendment in the Global law record of public laws.
- provisions: 54 F.S.M.C. 121, 122 (source notes)
- Lean: FmTax.sched
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Be engaged as a business (gross revenue tax 3 %) instead of an employee (6-10 %) | recreated: income-type scanner (self-employment +13.9 %) | 54 F.S.M.C. 112, 141 |
| K2 | Keep annual wages just below $5,000 to keep the $1,000 deduction | recreated: notch scanner | 54 F.S.M.C. 122 |
| K3 | Receive interest, dividends or rents as an individual: no national income tax on them | recreated: scanner income type | 54 F.S.M.C. ch. 1 (wages and business gross revenue only) |
| K4 | Per diem and housing allowances excluded from wages | not modelled: no input | 54 F.S.M.C. 112(11)(b), (c) |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 11,000, end of the 6 % band)
- #guard on the cliff, the ceilings and the gross revenue tax
- Global law search of FSM public laws for '121 of title 54', '122 of title 54', 'chapter 1 of title 54', 'section 603/901/902 of title 53', 'Social Security Act', 'wage and salary tax'

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and PFTAC (Pacific Financial Technical Assistance Centre) tax-policy diagnostics for each country
- Asian Development Bank Pacific Economic Monitor and country tax-reform reports (Palau 2023 reform, RMI 2025 reform)
- Pacific Islands Tax Administrators Association (PITAA) and Pacific Islands Forum Secretariat papers on PAYE and provident funds
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on Pacific provident funds, final-withholding wage taxes and Compact-state (FSM, RMI, Palau) wage taxes
- OECD Revenue Statistics in Asia and the Pacific (country notes for Fiji, PNG, Samoa, Solomon Islands, Tonga, Nauru, Kiribati, Tuvalu)


Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | statute-fault | confirmed | 61 USD for one dollar at 5,000 of wages. exe and #guard L1FM.F1. Evidence: exe + Lean `L1FM.F1` (`world/loopholes/rest/lean/L1FM.lean`, 1 #guard): it(b)-it(a) = 61; statute re-read: `law/T54_Ch01_SubChpI_2014.txt`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F2 | statute-fault | confirmed | 1,050 USD more social security on 50,000 split over two employers. exe and #guard L1FM.F2. Evidence: exe + Lean `L1FM.F2` (`world/loopholes/rest/lean/L1FM.lean`, 2 #guard): soc(a) = 2700; soc(b) = 3750; statute re-read: `law/T53_Ch06_2014.html`. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F3 | loophole | model-proved | 1,180 USD: 1,560 wage tax vs 380 gross revenue tax on 20,000. exe and #guard L1FM.F3. Evidence: exe + Lean `L1FM.F3` (`world/loopholes/rest/lean/L1FM.lean`, 2 #guard): it(a) = 1560; tot(b) = 380. Known/new: **new**: new (weak: Crossref only, no description in the hits) |
| F4 | fact | explained | Unindexed since TT Code (fact). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/FM.json`): METR 121.8 % and notches 61 = F1 (couple multiples); bands 21.8 % above the 10 % top = social security below its quarterly ceiling (the top rate is measured above it).

<!-- R2-SCANNERS:BEGIN -->
## Loophole round 2 (new scanners, 2026-11-21)

Agent R2 scanners; method and the cross-country tables in `world/loopholes/ROUND2_SCANNERS.md`. Scanner outputs: `results/search/{ceilings,mix,spouse,pension,multijob,payperiod,owner}.md` and `SUMMARY_ROUND2.md`.

- **FM-R2** Social security ceiling of US$9,000 a quarter per employer: two employers pay more on the same pay. Money: -600 USD a year at 44,000 (4 AW). Lean: `world/loopholes/round2/v/lean/R2FM.lean` (R2FM.R2 (3 #guard)); exe check `round2/v/out/FM.json`. Provision: 53 F.S.M.C. 603(15)(a), 901(1)(g) (model citation). Status: model-proved (a penalty, not a gain). Known/new: not searched (refund rule not read) (`round2/v/novelty/`).
- mix.py (wage vs fee split): lead: gross revenue tax on self-employment (see section 2 entry).
<!-- R2-SCANNERS:END -->
