# Saint Vincent and the Grenadines (VC) findings, B13-caribbean (2026-11-20T07:27Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory amount (official secondary where marked), so 1 'AW' there is that amount, not an average wage).

### F1 The House of Assembly publishes only one-page lists of each year's Acts, not the Acts
- kind: gov-error
- assembly.gov.vc 'Acts' page links one PDF per year (2010-2025) that lists titles, dates and numbers (e.g. 'Income Tax (Amendment) ... No. 5 of 2019', 'No. 20 of 2020', Finance Acts 2018-2024) without the texts; the Inland Revenue site (ird.gov.vc) did not answer; Global law holds only three 1979 UK instruments.
- provisions: -
- Lean: -
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|

## Step 5: what was searched

- assembly.gov.vc annual Acts lists 2018-2025
- gov.vc, finance.gov.vc, etax.gov.vc

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and technical-assistance reports for the Caribbean (tax policy diagnostics, CARTAC papers)
- CARICOM / OECS / ECCB papers on income-tax harmonisation and social-security reform in the Eastern Caribbean
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Inter-American Development Bank and CIAT/ECLAC (CEPAL) studies of personal income tax in Latin America and the Caribbean
- Academic work on Caribbean PAYE design, social-security contribution ceilings and the effect of thresholds on low earners
- Official tax calculators and withholding tables (referee material for the dataset phase: deliberately not read)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### R1 Rescue pass 2026-11-20T11:52Z: no dated text reached
- kind: access
- Internet Archive CDX of finance.gov.vc found its 'PDF/Acts' folder; the live site serves Cap. 435 Income Tax Act (Revised Edition 2009, 159 pages, text layer), Income Tax (Amendment) Acts No. 5 of 2019 and No. 20 of 2020 (territorial basis, withholding), and Finance Act No. 10 of 2023 (s. 47(1)(b) allowance raised to 22,000 dollars; Fifth Schedule 'On $10,001 - $30,000' 30 % -> 28 %): saved in vc/law/rescue/ (scans OCR'd) | House of Assembly annual lists 2010-2025 (live and archived) show a Finance Act every year 2010-2024 amending 'the laws contained in' the Finance Act; their texts (except 2023) were not reached, so the rest of the 2025 Fifth Schedule (first bands, top rate) and allowances cannot be established | finance.gov.vc and ird.gov.vc 'tax tables' (2018-2024) are withholding tables (referees): Tax_Tables-2024 downloaded, not opened
- would unlock: the Finance Acts 2010-2022 and 2024 (or a consolidation of Cap. 435 after 2009); with them the model is a short step from Cap. 435 + Finance Act 2023
- status: unsupported

## Rescue pass 2 (2026-11-20T13:11Z, rescue2 agent; log ~/cmp20/world/RESCUE.md, Pass 2)

Outcome: still unsupported (access C). Routes tried (laptop and lean1):
- legal.gov.vc (Attorney General's Chambers; found by WebSearch): Official Gazettes 2016-2026 (2024: 72 issues downloaded on the laptop): No. 10 lists S.R.&O. No. 4 of 2024 (Provisional Collection of Taxes Order 2024), No. 11 S.R.&O. No. 6 of 2024, No. 24 Act No. 6 of 2024 (Finance Act 2024): the gazette prints the notices only ('can be purchased at the Government Printing Office'), not the texts
- ird.gov.vc (laptop): legislation page = the same files as pass 1; 'Standard Deduction' page: 2025 25,000, 2024 25,000, 2023 22,000, 2022-2018 20,000 (official secondary; consistent with Finance Act 2023 s. 47(1)(b)); PIT 'current rate' links only to the 2024 tax tables (referee, not opened)
- finance.gov.vc forms: 2021 return form prints the allowances (personal 1,200, spouse 700, child 400, standard deduction 20,000) but no rate schedule; 2023 form 404
- Wayback CDX of finance.gov.vc, ird.gov.vc, assembly.gov.vc, pmoffice.gov.vc, gov.vc: budget addresses (proposals) and annual act lists; no Finance Act 2010-2022 or 2024 text
- two WebSearches: no host of the Finance Acts or a consolidated Fifth Schedule
- Cap. 435 (2009 RE) Fifth Schedule itself prints three conflicting 'Over $45,000' lines (40 %, 32.5 %, 40 % 'with effect from income year 1996'): recorded as a finding
- legis-palop.org (PALOP+TL legal database): full texts need a paid subscription and login (free registration gives listings only); its search form posts redirect to the home page without a session: not used (login)
- natlex.ilo.org, www.fao.org/faolex, www.refworld.org: Cloudflare 'Sorry, you have been blocked' (403) from the laptop and WebFetch: not bypassed
- droit-afrique.com: live site 403 ('Server unable to read htaccess file'); its tax codes are sold in a shop (Wayback: only the free 'sommaire')
- Global law list_jurisdictions (rescue2/tools/gl.py, 2026-11-20): no tax law in this country's corpus
- WIPO Lex country profile (www.wipo.int/wipolex/en/members/profile/<CC>): no tax law listed (except SY, GM: see below)
- What would unlock it: the Finance Acts 2010-2022 and 2024 (or a post-2009 consolidation of Cap. 435) to fix the 2025 Fifth Schedule

### R2 Cap. 435 Fifth Schedule prints three conflicting top rates (gov-error)
- kind: gov-error
- The Revised Edition 2009 Fifth Schedule item 1 lists 'Over $45,000 ... 40%', 'Over $45,000 ... 32.5%' and 'With effect from income year 1996 - over $45,000 ... 40%' after '$30,001 - $45,000 ... 40%': the consolidation keeps superseded lines without dates, so the top rate cannot be read from the official text alone.
- provisions: Income Tax Act Cap. 435 (RE 2009) Fifth Schedule item 1

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| F1 | gov-error | explained | Access. |
| R1 | record | explained | Record (access): not a loophole; kept as recorded (W-round evidence in world/IMPROVE_*.md). |
| R2 | gov-error | explained | Conflicting printed rates (builder). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/VC.json`): no model (access C).
