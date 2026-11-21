# Rwanda (RW) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Monthly withholding is the final tax on wages: 3.6 M paid in one month costs 1,044,000 against 648,000 paid evenly
- kind: loophole-new
- art. 56 tables are monthly; the model (and the law's withholding) applies them to each month. The kernel's annual timing scanner spreads pay evenly and cannot see this; #guard proves 12 x payeMonth 300,000 = 648,000 and payeMonth 3,600,000 = 1,044,000. An individual who 'receives only employment income' is 'not required to file his or her annual declaration' (Law 027/2022, article on annual declarations); one with several employers 'may file' to claim a refund: annual reconciliation is optional and not modelled.
- provisions: Law 027/2022 art. 56
- Lean: RwTax.payeMonth (#guard)
- status: modelled

### F2 The 2024 pension order sets a 12 % total but no split; the split comes from the 2015 Law ('contribute equally')
- kind: statute-fault
- P.O. n° 086/01 art. 1 fixes '12%' from 1 January 2025 and repeals P.O. 009/01 (which stated 3 % each); Law 05/2015 art. 8: 'The employer and the employee shall contribute equally'. Employee 6 % in 2025 (14 % total in 2027, 16 % 2028, 18 % 2029, 20 % 2030).
- provisions: P.O. 086/01 arts. 1, 5; Law 05/2015 art. 8
- Lean: RwTax.pensionEmployee
- status: modelled

### F3 Casual labourers pay a flat 15 % above 60,000 a month while employees reach 30 %
- kind: loophole-known
- art. 56 para. 2-3: 'income from a casual labourer is subject to tax on the special rate of fifteen percent (15%) ... an income not exceeding sixty thousand ... (60,000 FRW) per month is rated at zero percent'. Above 160,000 a month the casual rate is lower than the employee scale's average; classification matters. Not modelled (no input).
- provisions: Law 027/2022 art. 56
- Lean: -
- status: catalogued

### F4 The rate table is chosen by the date ('First year following the date of commencement' / 'From the second year')
- kind: statute-fault
- art. 56 prints two tables, the first for the year after 28/10/2022 (20 % from 60,000, 30 % from 100,000), the second thereafter; the French column of Table 2 prints '200,001' with a comma (other cells use a dot), and the article on annual declarations prints the turnover limit as 'FRW 2,000,0000' in the English column ('2.000.000' in French). Harmless for 2025; a statute that changes rates by elapsed time needs its commencement date to be read correctly.
- provisions: Law 027/2022 art. 56
- Lean: RwTax.sched
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Pay as casual labour (15 % flat above 60,000 a month) | not modelled: no input | Law 027/2022 art. 56 |
| K2 | Smooth pay over months (monthly final withholding) | recreated: #guard F1 (annual scanner blind) | Law 027/2022 art. 56 |
| K3 | Employer social-security contributions excluded from employment income | recreated: only employee side modelled | Law 027/2022 art. 16 2° |
| K4 | Small-enterprise lump-sum tax (3 % of turnover) instead of the profit tables | not modelled | Law 027/2022 (business profit tables) |

## Step 5: what was searched

- kernel scanners with scale 2,400,000 (12 x the 200,000 30 % threshold)
- Laws 051/2023 and 014/2025 read for changes to art. 56 (none)
- #guard on the monthly tables and bunching

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5A-1 Employee contribution added (W5 pattern A, 2026-11-20)
- kind: model gap fixed from the statute
- provisions: Law 003/2016 art. 7; P.M.O. 105/03 of 30/09/2020 art. 5 (replaced only from 23/02/2026 by P.M.O. 001/03 of 2026, same rate)
- maternity leave 0.3 % of gross salary and CBHI 0.5 % of net salary (gross - PAYE - pension - maternity); not deductible. Before W5 the model booked no such contribution ("rates not reached"); the W5a grids flagged it (IMPROVE_W5 pattern A). Input `"w5Contrib": false` restores the old outputs (checked: 0 of 300 random households differ in any money line). Sources under `law/w5/` with SHA256SUMS.
- status: fixed

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/RwTax/Verify.lean` (imported by the `RwTax` library and built; each guard evaluates `RwTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/RW.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | confirmed | Monthly PAYE is final for employees with only employment income: 3.6 M in one month bears 1,044,000 against 648,000 paid evenly. G: f1_monthly_final (model #guard). S: law/law027_2022.txt:2837 (art. 56 'Monthly Taxable Income ... Tax Rate'); not-required-to-file rule as cited by the model. Rescan timing_monthly: 1.5 'AW' in one month costs 394,026 more. |
| F2 | explained | Pension split from the 2015 law: modelled. |
| F3 | lead | Casual labourers' flat 15 %: not modelled. S: law/law027_2022.txt:640 (definition). |
| F4 | explained | Date-chosen tables and typos: record. |
| W5A-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Annual rescan flat; F1 is in timing_monthly. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F1: Monthly PAYE is final for employees: bunched pay is taxed at 30 % at once | timing or bunching | **new**: PwC Rwanda: final withholding is described for dividends and interest, not for monthly PAYE on bunched pay; OpenAlex: not answered. | 2026-11-20: OpenAlex queries 'Rwanda PAYE monthly final tax bonus no annual return'; 'Rwanda employment income tax bunching' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (rwanda, 5 individual pages): 4 passages with the item's terms; Crossref IMF prefix 10.5089 'Rwanda tax policy' (8290 records, titles only). Record: world/loopholes/africa_mena/search/RW-F1.json |

<!-- L1-VERIFICATION END -->
