# Dominica (DM) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The 2018 and 2019 Social Security contribution regulations are listed on the Government's law site but their files are missing (HTTP 404)
- kind: gov-error
- dominica.gov.dm 'Laws of Dominica' search lists 'Social Security (Collection of Contributions) (Amendment) Regulations 2018, SRO 12 of 2018' and '... 2019, SRO 22 of 2019'; both links answer 404 from lean1 and the laptop. The model uses S.R.O. 8 of 2008 (4 %, 6,000 a month) and flags it.
- provisions: S.R.O.s 12/2018, 22/2019 (unreachable); S.R.O. 8/2008
- Lean: DmTax.ssMonth
- status: recorded

### F2 The top income-tax rate of 36 % starts at EC$50,000 of chargeable income (EC$80,000 of pay), unchanged since 2009
- kind: loophole-known
- Fifth Schedule para. 1 (Act 9 of 2008); the allowance rose 20,000 -> 25,000 -> 30,000 (Acts 7/2014, 6/2018) but the bands did not.
- provisions: ITA s. 47, Fifth Schedule
- Lean: DmTax.sched
- status: modelled

### F3 Residential rent became tax-exempt in 2021 one year after a 20 % rental rate was introduced
- kind: loophole-known
- Act 3 of 2020 added Fifth Schedule para. 3 ('20% on the net residential rental income of an individual'); Act 13 of 2021 s. 3 inserted s. 27A: rental from residential property 'is exempt from tax'. Income from residential letting is untaxed (not modelled).
- provisions: ITA s. 27A, s. 61(3), Fifth Schedule para. 3
- Lean: -
- status: catalogued

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Residential rental income exempt (s. 27A) | not modelled: F3 | Act 13 of 2021 |
| K2 | Mortgage interest on two owner-occupied homes (30,000 + 15,000) | not modelled | ITA s. 48A (Act 3 of 2020) |
| K3 | Student-loan interest deductible | not modelled | ITA s. 48C (Act 13 of 2021) |
| K4 | ECSE-listed securities gains exempt | not modelled | S.R.O. 8 of 2006 |

## Step 5: what was searched

- kernel scanners with scale 50,000 (start of the 36 % band)
- dominica.gov.dm laws search ('income tax', 'social security') and every instrument after 2006 (OCR where scanned)

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5S4-1 caribbean-payroll (oecstrading), DM config: allowance 25,000 and bands of no year (W5 review pass 4, 2026-11-20)
- kind: software-error
- `dm_open_caribbean_payroll_oecstrading_grid`: s. 47 as amended by Act 6 of 2018 s. 11: resident allowance 30,000 from 1 January 2018; the config's 25,000 is the 2015-2017 level and its bands (15 % to 20,000, 25 % to 30,000, 35 % above) are no year's Fifth Schedule. Dev: tool above (32,782: 1,167 vs 445 = 16 % x 2,782). Open on the model side: the Acts on file give 16 / 26 / 36 % (Act 9 of 2008) while the IRD page (official secondary) prints 15 / 25 / 35 %; no amending instrument found (W5 review pass 4). NIC: the tool's 5.25 % to 5,000 a month vs the model's 4 % to 6,000 (S.R.O. 8/2008): S.R.O. 12/2018 and 22/2019 not reached (lean1 copies are 940-byte error pages; F1).
- status: recorded (world/IMPROVE_W5.md pass 4)

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Missing regulations (builder). |
| F2 | fact | explained | Unindexed bands (fact). |
| F3 | loophole | explained | Residential rent exempt (s. 27A); not modelled. |
| W5S4-1 | record | explained | Record (software-error): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/DM.json`): income-type gains are published rates or exemptions on capital income or model limits on it (dual / owner-manager pattern), not new findings.
