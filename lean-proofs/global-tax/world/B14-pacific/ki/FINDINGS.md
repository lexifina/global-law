# Kiribati (KI) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|

## Step 5: what was searched

- Global law (kiribati: Kiribati Independence Order 1979 only)
- Internet Archive listing of PacLII ki consolidated and numbered acts

## Literature not checked (no web-search budget this session)

- IMF Article IV staff reports and PFTAC (Pacific Financial Technical Assistance Centre) tax-policy diagnostics for each country
- Asian Development Bank Pacific Economic Monitor and country tax-reform reports (Palau 2023 reform, RMI 2025 reform)
- Pacific Islands Tax Administrators Association (PITAA) and Pacific Islands Forum Secretariat papers on PAYE and provident funds
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on Pacific provident funds, final-withholding wage taxes and Compact-state (FSM, RMI, Palau) wage taxes
- OECD Revenue Statistics in Asia and the Pacific (country notes for Fiji, PNG, Samoa, Solomon Islands, Tonga, Nauru, Kiribati, Tuvalu)


Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### R1 Rescue pass 2026-11-20T11:52Z: no dated text reached
- kind: access
- tax.gov.ki (Kiribati Tax Office, found via mfed.gov.ki 'TAXATION'): WordPress media library (all pages) holds forms, the VAT Act 2013 and VAT regulations, return instructions and pamphlets; no Income Tax Act; an 'Income Tax' page exists (official secondary, not a statute) | kiribatilaws.gov.ki: no answer
- would unlock: a current consolidation of the Income Tax Act (only the 1977 Cap. 44 is on hand)
- status: unsupported

## Rescue pass 2 (2026-11-20T13:11Z, rescue2 agent; log ~/cmp20/world/RESCUE.md, Pass 2)

Outcome: still unsupported (access C). Routes tried (laptop and lean1):
- kiribatilaws.gov.ki: no answer from the laptop; tax.gov.ki WordPress media search 'income tax': return forms and instructions only
- parliament.gov.ki (laptop): 'Acts' page embeds phocadownload categories 19-22 (Acts passed 2022-2025) whose plugin tag is not rendered; the category URLs answer 404 live; Wayback copies of the 2024 and 2025 category pages list five acts per page (none on income tax on the first page)
- Wayback CDX of parliament.gov.ki: Income Tax (Amendment) Acts 1994, 1996, 1997 (x2), 2009 and an 'Income Tax Act (No 9) amendment of s7' (2021 upload); acts of 2013-2025 incompletely archived, so the 2025 law cannot be shown complete
- legis-palop.org (PALOP+TL legal database): full texts need a paid subscription and login (free registration gives listings only); its search form posts redirect to the home page without a session: not used (login)
- natlex.ilo.org, www.fao.org/faolex, www.refworld.org: Cloudflare 'Sorry, you have been blocked' (403) from the laptop and WebFetch: not bypassed
- droit-afrique.com: live site 403 ('Server unable to read htaccess file'); its tax codes are sold in a shop (Wayback: only the free 'sommaire')
- Global law list_jurisdictions (rescue2/tools/gl.py, 2026-11-20): no tax law in this country's corpus
- WIPO Lex country profile (www.wipo.int/wipolex/en/members/profile/<CC>): no tax law listed (except SY, GM: see below)
- What would unlock it: a consolidated Income Tax Act (Cap. 44) as amended to 2025, or the complete list of income tax amendments since 2009

## Verification (L1 REST, 2026-11-21)

Verifier: the L1 loophole round for Asia, the Americas, Europe and the Pacific (`world/loopholes/PROGRESS_REST.md`). Scanners re-run on the current model on 2026-11-20 (`world/tools/scan_world.py`; `results/search/`). Statuses as in `report/CROSS38.md`: **confirmed** = the amount reproduced by the exe and by Lean #guards on the model, and the provision re-read in the country's sources; **model-proved** = reproduced by exe and Lean, provision cited by the builder but not re-located in a text file; **proved** = a Lean theorem of the model (rebuilt); **explained**; **lead**; **withdrawn**. Known/new: `world/loopholes/REST.md` and `world/loopholes/rest/novelty/`.

| finding | class | status | verification |
|---|---|---|---|
| R1 | record | explained | No model (access C). |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/KI.json`): no model (access C).
