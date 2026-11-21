# South Sudan (SS) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 'Taxable incomes ... are charged at the rate of': the brackets can be read as slabs, which would make the tax jump by SSP 2,000 at 40,001 a month
- kind: statute-fault
- Financial Act 2024/2025 s. 4(2)(b)-(e): 'Taxable incomes ranging from 20,001 but does not exceed SSP 40,000 per month are charged at the rate of five percent' etc. Graduated reading (default): 100,000 a month -> 9,650. Slab reading (input ssSlabReading): 40,000 -> 2,000, 40,001 -> 4,000; 90,000 -> 13,500, 90,001 -> 18,000 (#guard). A year at 1.2 M costs 115,800 graduated vs 240,000 slab.
- provisions: Financial Act 2024/2025 s. 4(2)
- Lean: SsTax.taxMonth (#guard)
- status: statute fault (reading)

### F2 The 20 % 'standard allowable expenses' are written for wages and entrepreneurial income together
- kind: statute-fault
- s. 4(1): tax 'on taxable income from wages and entrepreneurial Activities after standard allowable expenses of twenty percent (20%) and other expenses such as town rate, ground rate, etc. are deducted'; s. 5(2) keeps the wage deductions of Taxation Act s. 58(3) (pension 5 %). Default: 20 % only for entrepreneurial income; input standard20OnWages applies it to wages (tax on 1.2 M a year falls from 115,800 to the tax on 960,000).
- provisions: Financial Act 2024/2025 ss. 4(1), 5(2)
- Lean: SsTax.out
- status: reading

### F3 The Financial Act 2023/2024 charges tax 'for the tax year 2022/23'
- kind: statute-fault
- Financial Act 2023/2024 s. 4(1): 'Personal income tax is charged for the tax year 2022/23'; s. 5(1): deductions 'allowed for the FY 2022/23'. The 2024/2025 Act corrects the year. A stale year in a charging section is a cheap statute-fault search for annual finance acts.
- provisions: Financial Act 2023/2024 ss. 4(1), 5(1)
- Lean: -
- status: recorded

### F4 Exactly SSP 20,000 a month falls in no bracket ('less than SSP 20,000' / 'from 20,001')
- kind: statute-fault
- s. 4(2)(a)-(b). Harmless under the graduated reading (no tax up to 20,000); (d) also omits 'per month'.
- provisions: Financial Act 2024/2025 s. 4(2)
- Lean: SsTax.slabRate
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Members of a GRS-approved pension scheme deduct up to 5 % of gross wages | recreated: input pensionMember | Financial Act 2024/2025 s. 5(2) |
| K2 | Rental/investment income at 20 % after a 20 % standard allowance | not modelled | s. 4(2)(f) |
| K3 | Treaty-country exemption only | not modelled | s. 6(2) |

## Step 5: what was searched

- kernel scanners with scale 1,080,000 SSP (12 x 90,000)
- both readings of s. 4(2) compared on the exe
- 2023/24 and 2024/25 Financial Acts compared section by section for PIT

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5S4-1 Horizon HR (JohnMarit): bands of no year's text; an 8 % social security contribution (W5 review pass 4, 2026-11-20)
- kind: software-error
- `ss_open_horizon_hr_johnmarit_grid`: 0 / 10 / 15 / 20 / 25 / 30 % at 500 / 1,000 / 2,000 / 5,000 / 10,000 SSP a month; Financial Act 2024/2025 s. 4(2): exempt to 20,000 a month, then 5 / 10 / 15 / 20 % at 40,000 / 57,000 / 90,000 (the Taxation Act 2016 and Financial Act 2023/24 on file differ from the tool too). Dev: tool far above (216,363 a year: 51,709 vs 0). Its 8 % 'social security contribution' matches no text on file (reading: no contribution statute read for SS; the model keeps the s. 5(2) pension input).
- status: recorded (world/IMPROVE_W5.md pass 4)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | lead | Slab reading would give SSP 2,000 at 40,001 a month (input ssSlabReading); the graduated reading is modelled: a reading, not a confirmed loophole. |
| F2 | lead | 20 % standard expenses for wages: reading. |
| F3, F4 | explained | Stale year; 20,000 in no bracket: records. |
| W5S4-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan timing_monthly: 1 'AW' in one month costs 113,850 more (monthly final PAYE, same mechanism as RW F1; not a FINDINGS item). |

<!-- L1-VERIFICATION END -->
