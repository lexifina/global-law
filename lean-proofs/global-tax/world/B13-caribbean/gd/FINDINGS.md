# Grenada (GD) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 Grenada's income-tax rates and personal deduction are set by ministerial order, not by Act
- kind: gov-error
- s. 128 lets the Minister vary rates and Schedules by order; the 2025 law is the 2010 Act as varied by S.R.O. 1 of 2014 (allowance 60,000 -> 36,000; 15 %/30 % at 24,000), S.R.O. 2 of 2017 (15 % -> 10 %) and S.R.O. 25 of 2018 (30 % -> 28 % 'wherever it appears', which also cut the company rate). The consolidated Act on laws.gov.gy still prints 60,000 and a flat 30 %.
- provisions: ITA s. 128, Fifth Schedule; S.R.O.s 1/2014, 2/2017, 25/2018
- Lean: GdTax.sched
- status: modelled

### F2 The 2014 Order cut the personal deduction from 60,000 to 36,000 while adding a 15 % band: taxes rose for most earners below about 60,000
- kind: loophole-known
- S.R.O. 1 of 2014 paras. 3 and 5. Under the 2010 Act a 60,000 earner paid nothing; under the 2014 Order 15 % x 24,000 = 3,600 (2025: 10 % = 2,400).
- provisions: ITA s. 42A; S.R.O. 1 of 2014
- Lean: GdTax.person
- status: recorded

### F3 The NI rate schedule is legislated eight years ahead (6 % in 2025 rising to 7.5 % in 2031) while the ceiling is frozen at EC$5,200 a month
- kind: loophole-known
- S.R.O. 43 of 2023: Part II rows 'January 1, 2025 | 6%' ... 'January 1, 2031 | 7.5%'; Part III maximum insurable earnings only for 'January 1, 2024'.
- provisions: NI (Collection of Contributions) Regs Schedule Parts II-III
- Lean: GdTax.niMonth
- status: modelled for 2025

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Individual taxation of married women: split income | recreated: filing-unit scanner | ITA s. 13 |
| K2 | Approved pension income exempt | not modelled | ITA s. 25(1)(gg),(hh) (Act 1 of 2017) |
| K3 | Employees aged 60+ pay no NI | recreated | NI Regs Part II |

## Step 5: what was searched

- kernel scanners with scale 62,400 (NI ceiling)
- laws.gov.gd Acts 2011-2025 and S.R.O.s 2011-2025 listings (income tax, national insurance titles)

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5S4-1 caribbean-payroll (oecstrading), GD config: first band 15 %; NI 5 % to 5,000; NI at 60+ (W5 review pass 4, 2026-11-20)
- kind: software-error
- `gd_open_caribbean_payroll_oecstrading_grid`: Fifth Schedule para. (a) 10 % since S.R.O. 2/2017 (tool 15 %: dev -1,200 = 5 % x 24,000 above the band); NI 6 % to 5,200 a month and nil from 60 (S.R.O. 43/2023, Schedule Part II): tool 5 % to 5,000 at every age (dev +744 at the ceiling, ratio 1.2 below it, -3,000 at 60+).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Rates by order (builder). |
| F2 | fact | explained | Historical comparison. |
| F3 | fact | explained | Schedule ahead, ceiling frozen. |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/GD.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
