# Seychelles (SC): findings, B09 build phase (2026-11-20T06:18Z)

Seychelles built from the emoluments tax schedule (Act 27 of 2017): monthly and per source of employment, so two employers each give a nil band; a non-citizen on SR20 000 a month pays SR15 400 a year more than a citizen.

Scale for scanner numbers: 120,000 SCR = 12 x the SR10 000 monthly threshold of the 20 % band (citizens) (Income and Non-Monetary Benefits Tax Act First Schedule para 1 as replaced by Act 27 of 2017); a statutory threshold, not an average wage.

### F1 Each source of employment gets its own monthly bands
- kind: loophole-known
- First Schedule para 1: tax 'in respect of emoluments received from each source of employment in a month'. SR20 000 a month from one employer: SR2 216.68; from two employers paying SR10 000 each: 2 x SR216.68 = SR433.36 (Lean #guard). No annual aggregation of employment income in the charging schedule.
- provisions: INMBT Act s. 4 (1), First Schedule para 1
- Lean: ScTax.monthlyCents (#guard)
- status: found by reading, proved

### F2 Non-citizens have no nil band
- kind: fact
- para 2: 'Not exceeding SR10,000 15% of the amount'. At SR20 000 a month the non-citizen pays SR42 000 a year vs SR26 600 for a citizen (input 'citizen': false).
- provisions: First Schedule para 2
- Lean: ScTax.nonCitizenSched
- status: modelled

### F3 Printed cumulative amount rounds half a cent
- kind: fact
- SR216.68 = 15 % x 1 444.50 = 216.675 rounded; the printed 14 883.28 carries the rounding. Exact and printed agree to the cent (#guard).
- provisions: First Schedule para 1
- Lean: ScTax citizenSched guards
- status: checked

### F4 Monthly final tax: uneven pay costs more
- kind: fact
- No annual reconciliation in the schedule: SR120 000 paid in one month costs more than SR10 000 a month (bands are monthly).
- provisions: First Schedule para 1
- Lean: ScTax.annual
- status: noted

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- per-source monthly bands (two employers): recreated
- citizen nil band SR8 555.50: recreated
- bonus up to 1/12 of annual basic salary tax-free (para 6, SI 26/2024): not modelled
- non-monetary benefits taxed on the employer at 15 % (Third Schedule): not modelled
- self-employment under the Business Tax Act: not modelled

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.2, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.2, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.18, "netIncomeFalls": 0}}
- `world/tools/scan_world.py SC` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- Seychelles Pension Fund contributions
- bonuses / 13th-month pay
- business tax on self-employment
- investment income

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: SPF Act 2005 ss. 17-18 (consolidated 01/01/2023); rate from the Fund notice of 08/12/2022 (4 % -> 5 % from 1 Jan 2023), official secondary
- SPF employee 5 % of emoluments for citizens (no ceiling); not deducted. Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed (model guard) | Each source of employment has its own monthly bands: SR20,000 a month from one employer pays SR2,216.68, from two employers paying SR10,000 each SR433.36 (T: #guard monthlyCents true 2000000 = 221668 ∧ 2 * monthlyCents true 1000000 = 43336). The contract has one wage per adult, so no exe guard. S: law/Income-and-Non-Monetary-Benefits-Tax-Amendment-Act-2017-Act-27-of-2017.ocr.txt:49 ('from each source of employment in a' [month]). |
| F2 | explained | Non-citizens without a nil band: design. |
| F3 | explained | Printed rounding: checked by #guard. |
| F4 | explained | Monthly final tax: same mechanism as F1 / DJ F1; not separately guarded. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: no notch; wedges for other income types are model gaps. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Each source of employment has its own monthly bands | timing or bunching | **new**: Nothing found (no PwC page for Seychelles: the pages came back empty; OpenAlex not answered); the per-employer monthly charge is printed in the 2017 amending Act. | 2026-11-20: OpenAlex queries 'Seychelles income tax each source of employment monthly'; 'Seychelles income and non-monetary benefits tax secondary employment' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries: no page for this country; Crossref IMF prefix 10.5089 'Seychelles tax policy' (8270 records, titles only). Record: world/loopholes/africa_mena/search/SC-F1.json |

<!-- L1-VERIFICATION END -->
