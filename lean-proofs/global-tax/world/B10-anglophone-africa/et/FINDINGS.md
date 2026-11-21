# Ethiopia (ET) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Proclamation 1395/2025 was published on 1 September 2025 but applies to income derived from 8 July 2025
- kind: statute-fault
- Federal Negarit Gazette No. 64, '1st september, 2025'; art. 4(3): 'all other provisions of this amendment shall be applicable on income derived as of July 8, 2025'. Employers withheld July and August 2025 under the old table (0 % only to 600 birr); the retroactive change needs refunds or adjustments the Proclamation does not describe in the parts read.
- provisions: Proclamation 1395/2025 art. 4
- Lean: EtTax.sched, EtTax.sched979
- status: recorded

### F2 The reform cut tax on 10,000 birr a month from 2,045 to 1,650 and raised the zero band from 600 to 2,000
- kind: model-fix
- #guard sched979 10,000 = 2,045 vs new 1,650; top rate 35 % now from 14,000 (was 10,900).
- provisions: Proclamation 979/2016 art. 11; 1395/2025 art. 1(6)
- Lean: EtTax (#guard)
- status: modelled

### F3 Monthly final tax: pay bunched into one month is taxed at 35 % at once
- kind: loophole-new
- art. 11 is a monthly rate table; art. 11 sets a monthly rate; the model applies it month by month (no annual reconciliation provision for employees was read). Bunching 240,000 birr into one month costs 2,850 + 35 % x 226,000 = 81,950 vs 59,400 paid evenly (exe: 12 x taxMonth 20,000 = 59,400).
- provisions: Proclamation 1395/2025 art. 1(6)
- Lean: EtTax.taxMonth
- status: modelled

### F4 The employee's 7 % pension contribution is not deductible while the employer's 11 % is exempt
- kind: model-fix
- 979 art. 65(1)(c) exempts employer contributions up to 15 % of monthly employment income; no provision deducts the employee's own. Statutory top combined rate 42 % (35 % + 7 %; scanner 42.9 % with whole-birr monthly rounding).
- provisions: 979 art. 65; 1268/2022 art. 10
- Lean: EtTax.out
- status: modelled

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Employer pension contributions up to 15 % of salary exempt (pay in contributions rather than wages) | not modelled: employer side | 979 art. 65(1)(c) |
| K2 | Smooth monthly pay (monthly final tax) | recreated: F3 | art. 11 |
| K3 | Exempt allowances (transport, hardship) listed in art. 65 | not modelled | 979 art. 65 |

## Step 5: what was searched

- kernel scanners with scale 168,000 birr (12 x 14,000)
- Proclamation 1395/2025 read for every article touching employment income
- old vs new art. 11 compared with #guard

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5S-1 payroll_africa (Ethiopia): capped employee pension deducted before PIT (reading) (W5 review pass 2, 2026-11-20)
- kind: software-error
- `et_open_payroll_africa_grid`: the app taxes gross - 7 % pension, the pension base capped at 15,000 a month; no article of Proclamation 979/2016 (as amended by 1395/2025) deducts the employee's contribution (EtTax note) and Proclamation 1268/2022 art. 10 bases contributions on the salary without a ceiling. Misses +4,404 / +4,410 (35 % x 12 x 1,050).
- status: recorded (world/IMPROVE_W5.md pass 2)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Money amounts are proved by #guards in `lean/EtTax/Verify.lean` (imported by the `EtTax` library and built; each guard evaluates `EtTax.country` on the contract household the exe reads; generator `world/loopholes/africa_mena/vgen.py`, spec `checks/ET.json`). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | Retroactive Proclamation 1395/2025: record. |
| F2 | explained | Reform amounts (#guard sched979). |
| F3 | confirmed | Monthly final tax: 240,000 birr in one month bears 81,950 against 59,400 paid evenly. G: f3_monthly_final. S: law/mor_proc_1395.txt:289-292 ('The monthly rate of employment' income table). |
| F4 | explained | Employee pension not deductible: design. |
| W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan bands above the top rate (46.7 % max, 41.8 % avg) are whole-birr monthly rounding; timing_monthly 22,550 = F3. |

### Known or new (recorded searches)

| loophole | type | verdict | search |
|---|---|---|---|
| F3: Monthly final employment tax: bunched pay is taxed at 35 % at once | timing or bunching | **new**: PwC Ethiopia prints the monthly brackets and counts bonuses as employment income, without the cost of bunching; OpenAlex: not answered. | 2026-11-20: OpenAlex queries 'Ethiopia employment income tax monthly bonus taxation'; 'Ethiopia income tax proclamation 1395/2025' not answered (free daily budget exhausted; search reduced); Semantic Scholar (same queries; rate-limited, no answer); PwC Worldwide Tax Summaries (ethiopia, 5 individual pages): 4 passages with the item's terms; Crossref IMF prefix 10.5089 'Ethiopia tax policy' (8291 records, titles only). Record: world/loopholes/africa_mena/search/ET-F3.json |

<!-- L1-VERIFICATION END -->
