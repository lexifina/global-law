# Botswana (BW): findings, B09 build phase (2026-11-20T06:18Z)

Botswana modelled under the Income Tax Act 2026 (tax year 2026/27; the 2025/26 Cap. 52:01 schedule was not reachable): 0 % to P48 000, 5-27.5 %, final 10 % on bank interest and dividends; BURS's own pages still give P30 000 and P36 000 thresholds.

Scale for scanner numbers: 156,000 BWP = threshold of the 25 % band (Income Tax Act 2026 (No. 13 of 2026) Schedule 1 Part I para 1); a statutory threshold, not an average wage.

### F1 BURS pages give three different tax thresholds
- kind: gov-error
- BURS PAYE page: 'taxable threshold (P2500 per month)'; BURS income-tax FAQ: 'more than P3,000 per month or P36,000 per annum'; Income Tax Act 2026 Schedule 1: '0 – 48,000 0 per cent'. The pages date from 2011-era rules and were not updated.
- provisions: Income Tax Act 2026 Sch. 1 Part I para 1
- Lean: BwTax.sched
- status: found by reading

### F2 Final 10 % on bank interest and dividends
- kind: loophole-known
- Sch. 1 para 7 (a)-(b) 10 %; s. 140 (b)-(c) final. P600 000 of wages: 129 050; P500 000 wages + P100 000 bank interest: 111 550. Scanner: +13.7 % of income at 5 x scale (P156 000 = 25 % band threshold).
- provisions: ITA 2026 s. 133, 140, Sch. 1 para 7
- Lean: BwTax.out
- status: recreated

### F3 Capital gains have their own schedule with a lower zero band
- kind: fact
- Sch. 1 para 2: net aggregate gain 0 % only to P36 000 (income: P48 000), same rates above.
- provisions: Sch. 1 para 2
- Lean: BwTax.gainSched
- status: modelled

### F4 Retirement deduction capped by a circular measure
- kind: statute-fault
- s. 28 (5): the deduction 'shall not exceed 15 per cent of the taxable income ... for the year', but taxable income is computed after the deduction (s. 13). The model reads 15 % of income before the deduction; the fixed point would be 15/115 of it.
- provisions: ITA 2026 s. 13, 28 (5)
- Lean: BwTax.personTI
- status: reading flagged

### F5 The year modelled is 2026/27, not 2025
- kind: model-fix
- Cap. 52:01's rate schedule (2025/26) was not reachable: botswanalaws.com now serves the 2026 Act and sells PDFs; no archived copy.
- provisions: ITA 2026 s. 144 (a)
- Lean: -
- status: open

## Step 4: known loopholes, catalogued from the statute (blind to referees)

- final 10 % WHT on bank interest and dividends: recreated
- separate capital-gains schedule: recreated
- retirement contributions up to 15 %: recreated
- 50 % exemption of retirement lump sums (Act 1 of 2024): not modelled
- resident vs non-resident schedules (5 % from the first Pula): not modelled

Literature not checked (no web-search budget this session): IMF Article IV / FAD reports, ATAF African Tax Outlook, ICTD/ITC working papers, World Bank PER chapters, Big-4 country tax guides, academic papers on the country's PIT; the catalogue above is therefore limited to what the statute and the official pages read here make visible.

## Step 5: searches run
- `tools/scan.py` (fine grid 0-2.5 x scale, single / couple 1 earner + 2 children / couple 60-40 + 2 children): {"single": {"maxMETR": 0.2513, "netIncomeFalls": 0}, "couple1earner2kids": {"maxMETR": 0.2513, "netIncomeFalls": 0}, "couple60_40_2kids": {"maxMETR": 0.2308, "netIncomeFalls": 0}}
- `world/tools/scan_world.py BW` (METR, phase-outs, timing, edges, filing unit, income type): `results/search/SUMMARY.md`. Scanner gains for income types the model marks unsupported are artefacts, not loopholes.

## Unsupported (listed in every output line where it applies)
- the 2025/26 rate schedule under Cap. 52:01
- social contributions (none found)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/BwTax/Verify.lean` (imported by the `BwTax` library and built; each guard evaluates `BwTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/BW.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Three thresholds on BURS pages: gov record. |
| F2 | confirmed | Final 10 % on bank interest: 100,000 moved from wages to interest keeps 17,500 more at 600,000. G: f2_interest_final_10pct. S: law/ita_amend_2026.txt:3080 ('(b) 10 per cent'), :4857 ('(a) Dividends 10 per cent'). |
| F3 | explained | Gains schedule with a lower zero band. |
| F4 | lead | Circular 15 % retirement cap: reading. |
| F5 | explained | Year modelled 2026/27: record. |
| Leads | explained | Rescan: no notch; interest/dividend wedge +13.7 % = F2. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F2: Final 10 % on bank interest and dividends against wage rates to 25 % | income-type gap | **unclear**: The final 10 % on domestic bank interest is in the statute; PwC Botswana's interest passage covers only foreign interest of resident citizens; OpenAlex: nothing. | 2026-11-20: OpenAlex specific queries 'Botswana withholding tax interest final 10% individuals' (1232 hits, titles checked); OpenAlex broad 'Botswana personal income tax', 'Botswana income tax wages', 'Botswana tax system reform' (75 records, titles and abstracts grepped, 1 term matches, none on the mechanism); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (botswana, 5 individual pages): 12 passages with the item's terms. Record: world/loopholes/africa_mena/search/BW-F2.json |

<!-- L1-VERIFICATION END -->
