# Marshall Islands (MH) findings, B14-pacific (2026-11-20T07:14Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 2025 has two wage-tax schedules and the dates are ambiguous: P.L. 2024-14 (8/12/16 %) took effect on certification (8 October 2024) with 'a seven (7) months period for the implementation process', and P.L. 2025-34 restored 8/12 % from 1 October 2025
- kind: statute-fault
- P.L. 2024-14 §§ 102-104; P.L. 2025-34 §§ 102-103 (passed 18 February 2025, certified 25 September 2025). On $24,000 a year: 2,307 if the 2024 schedule ran January-September (certification reading), 2,377 if it ran May-September (implementation reading) (#guard). The consolidation _5 prints only the restored text with '[Amended by P.L. 2024-14] [amended by P.L. 2025-34]': a reader of it alone would apply 8/12 % all year.
- provisions: 48 MIRC 103(1); P.L. 2024-14 §§ 102-104; P.L. 2025-34 §§ 102-103
- Lean: MhTax.is2024Month, wageTax (#guard)
- status: modelled (switch mhReading)

### F2 The low-wage exemption is all or nothing: $693.33 a month pays nothing, one cent more pays 8 % of the whole wage ($55.47 a month, $664 a year)
- kind: statute-fault
- 48 MIRC 103(3): 'Any who earns more than $160 per week or $693.33 per month shall not be entitled to an exemption.' Scanner: notch 664 at 8,320 a year, METR 1,294 % on its grid (#guard 69,333/69,334 cents).
- provisions: 48 MIRC 103(3)
- Lean: MhTax.monthTaxCents (#guard)
- status: modelled; scanner reproduces

### F3 The Social Security Act's definition of 'Covered Earnings' is garbled, so whether contributions stop at $10,000 a quarter cannot be read from it
- kind: statute-fault
- 49 MIRC 102(k): 'the worker's ... gross earnings during any quarter prior to March 6, 2017 and thereafter for new retirees ten thousand dollars (US$10,000)'; § 132(1) refunds contributions 'on earnings in excess of the covered earnings, whether from one (1) or more employers', which presupposes a ceiling. Model: $10,000 a quarter (switch mhSSCap none).
- provisions: 49 MIRC 102(k), 129, 132
- Lean: MhTax.ssEmployee
- status: modelled (switch)

### F4 The 1989 schedule prorates by pay period with rounded monthly amounts ($866.67, $693.33) that do not equal the annual ones exactly
- kind: statute-fault
- § 103(1) '$200 per week, or $866.67 per month'; $866.67 x 12 = $10,400.04 and $200 x 52 = $10,400; $693.33 x 12 = $8,319.96 vs $8,320. Weekly and monthly payees therefore get slightly different bands (cents).
- provisions: 48 MIRC 103(1), (3)
- Lean: MhTax.schedOld
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Keep monthly pay at or below $693.33 (or weekly at $160) to keep the exemption | recreated: notch scanner | 48 MIRC 103(3) |
| K2 | US contractor personnel taxed at 5 % flat | recreated: input mhUSContractor | 48 MIRC 103(2) |
| K3 | Bunch pay into months of the cheaper schedule (2025 only) | recreated: #guard of the two readings | P.L. 2024-14, P.L. 2025-34 |
| K4 | Self-employment under the gross revenue / net profit regime instead of the wage tax | not modelled | 48 MIRC 109; Net Profit Act 2025 |

## Step 5: what was searched

- kernel scanners (METR, phase-outs, timing, edges, filing unit, income type) via world/tools/scan_world.py with the cited scale.json (scale 10,400, end of the 8 % band)
- #guard on the exemption edge, both schedules and both readings
- rmiparliament.org acts by year 2024 and 2025 (POST year=...): Income Tax (Amendment) Acts 2024 and 2025, Minimum Wage (Amendment) Act 2024, Net Profit Act 2025, Consumption Tax, Excise Tax and Tax Administration Acts 2025 (titles)

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
| F1 | statute-fault | model-proved | MhTax #guard on both readings (build). |
| F2 | statute-fault | confirmed | 665 USD a year for one dollar at 8,320 (693.33 a month). exe and #guard L1MH.F2. Evidence: exe + Lean `L1MH.F2` (`world/loopholes/rest/lean/L1MH.lean`, 1 #guard): it(b)-it(a) = 665; statute re-read: `law/2024-0014A.ocr.txt`. Known/new: **unclear**: Crossref found the IMF technical-assistance report 'Republic of the Marshall Islands: Consumption and Income Tax Reform' (10.5089/9798229002974.019), which may discuss the exemption; not read. |
| F3 | statute-fault | explained | Garbled definition (builder). |
| F4 | statute-fault | explained | Cents. |

Scanner leads of the fresh scan (`world/loopholes/rest/leads/MH.json`): METR 1,294 % and notches 664 = F2 (multiples); timing 667-1,044 = F2; edge falls at 8,372 = cents of the pro-rated $693.33 (F4).
