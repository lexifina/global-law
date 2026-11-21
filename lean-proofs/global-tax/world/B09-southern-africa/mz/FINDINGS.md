# Mozambique (MZ): findings, B09 build phase (2026-11-20T06:18Z)

Mozambique built from the 2013 IRPS withholding table (final for wages): 10-32 % with five dependant columns; the gazetted table prints 27.275,00 instead of 28.275,00 for three dependants, so tax falls by 1 000 MT a month at 144 750 MT (annual tax 339 300 vs 327 300).

Scale for scanner numbers: 729,000 MZN = 12 x the 60 750 MT monthly limit of the 25 % row (Código do IRPS art. 65-A annex (Lei 20/2013)); a statutory threshold, not an average wage.

### F1 Gazetted table: three-dependant column falls by 1 000 MT at the top row
- kind: gov-error
- Annex to art. 65-A, last row 'De 144.750,00 até diante': '28.375,00 | 28325,00 | 28.300,00 | 27.275,00 | 28.225,00'. Every other value equals the row above continued by its coefficient (#guard); the fourth column would be 7.275,00 + 0,25 x 84.000 = 28.275,00. A worker with three dependants earning 144 750 MT a month pays 1 000 MT less than at 144 749: annual 339 300 vs 327 300. Likely a typesetting error that, applied literally, cuts 12 000 MT a year for every such worker above the limit.
- provisions: CIRPS art. 65-A annex (Lei 20/2013)
- Lean: MzTax.table, contAt (#guard)
- status: found by the continuity proof

### F2 Dependant columns have no headings
- kind: statute-fault
- The gazette table's five value columns under 'por número de dependentes' are unlabelled; the model reads them as 0, 1, 2, 3, 4 or more.
- provisions: art. 65-A annex
- Lean: MzTax.table
- status: reading flagged

### F3 Final withholding on wages: uneven pay costs more
- kind: fact
- Art. 65 n.º 5: withholding on dependent work 'é efectuada a título definitivo': 12 equal months are cheaper than the same pay concentrated in a few months.
- provisions: CIRPS art. 65
- Lean: MzTax.monthly
- status: noted

### F4 Two different untaxed amounts
- kind: fact
- Art. 56: no tax on annual taxable income up to 225 000 MT; the withholding table, final for wages, starts at 20 250 MT a month = 243 000 MT a year.
- provisions: CIRPS art. 56, 65-A
- Lean: MzTax.table
- status: noted

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- final withholding on wages (no annual aggregation): recreated
- dependants reduce the monthly withholding: recreated
- liberatory 10 %/20 % rates on capital income (art. 57): not modelled
- capital gains on shares reduced by holding period (art. 29: 100/85/65/55 %): not modelled
- tax-free minimum 225 000 MT (art. 56): catalogued

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.3293, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.3293, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.2503, "netIncomeFalls": 0}}
- `world/tools/scan_world.py MZ` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- amendments after 2013
- art. 54 annual tariff (self-employment, pensions)
- liberatory rates on capital income
- INSS

### W5A-1 Employee contribution added (W5 pattern A, second sweep, 2026-11-20)
- kind: model gap fixed (official secondary)
- provisions: INSS page "Taxa contributiva TCO" (inss.gov.mz, fetched 2026-11-20): worker 3 % + employer 4 % = 7 %; official secondary; RSSO (Decreto 51/2017, republished by Decreto 56/2024 de 30 de Julho) arts. 14-15; AT "As 100 questões ... sobre o CIRPS" (2015) q. 25
- INSS worker 3 % of remuneration (no ceiling), reported, not deducted (AT FAQ: no deduction for 1st-category income, CIRPS art. 29). Before W5 the model booked no such contribution (rate not reached); the W5 sweep flagged it (IMPROVE_W5 pattern A, w5/pa/SWEEP.md). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Not covered: INSS 3 % from the INSS page (the joint ministerial diploma fixing the rate, RSSO art. 15, not reached). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/MzTax/Verify.lean` (imported by the `MzTax` library and built; each guard evaluates `MzTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/MZ.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed (statute text; the administration applies another number) | Lei 20/2013's table (the gazetted statute) prints 27,275 in the three-dependant column of the top row (continuity: 28,275) and 28,225 for four or more, so at 144,750 MT a month and above a fourth dependant raises the tax by 950 a month (11,400 a year) on the statute's figures. G: f1_fourth_dependant_costs. S: law/lei20_2013.txt:416 ('De 144.750,00 ate diante 28.375,00 28325,00 28.300,00 27.275,00 28.225,00'). But the Autoridade Tributária's consolidated CIRPS (law/cirps_2015.txt:1865 and law/cirps_at.txt:1865) prints 28.275,00: the administration's text silently corrects the gazette, so a top-row worker with three dependants is charged 1,000 MT a month (12,000 a year) more than the enacted table. The model follows the statute (rule: statute only); this is a rule set outside the law, in the State's favour. |
| F2 | explained | Unlabelled dependant columns: reading (0-4+). |
| F3 | explained | Final withholding on wages: same mechanism as DJ F1. |
| F4 | explained | Two untaxed amounts (225,000 vs 243,000): record. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: no notch on the default (no-dependant) families. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: The gazetted top row prints 27,275 for three dependants; the AT's code prints 28,275 | rule set outside the law | **new**: PwC Mozambique prints the top row as '28,375 28,325 28,300 28,275 28,225', i.e. the administration's figure, not the gazette's 27,275: the gap between the enacted and the applied table is described nowhere in the search. | 2026-11-20: OpenAlex queries 'Moçambique IRPS tabela retenção dependentes artigo 65-A'; 'Mozambique personal income tax withholding table dependants' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (mozambique, 5 individual pages): 9 passages with the item's terms; Crossref IMF prefix 10.5089 'Mozambique tax policy' (8394 records, titles only). Record: world/loopholes/africa_mena/search/MZ-F1.json |

<!-- L1-VERIFICATION END -->
