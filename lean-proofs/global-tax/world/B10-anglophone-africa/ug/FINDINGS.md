# Uganda (UG) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 Rent is taxed on its own scale (12 % above 2.82 M) while wages reach 30-40 %: income-type conversion is visible in the statute
- kind: loophole-known
- Schedule 4 Part II: rental income of an individual 'Not exceeding Ushs. 2,820,000 ... Nil | Exceeding Ushs. 2,820,000 | 12%', charged separately (s. 5(3): rent 'shall not be included in the gross income'); Part I: wages to 30 % plus 10 % above 120 M. The model does not compute the rental tax (marked unsupported), so the income-type scanner cannot show the gain; the statute does.
- provisions: ITA s. 5(3), s. 6(1),(2), Schedule 4 Parts I-II
- Lean: UgTax.sched
- status: catalogued (not modelled)

### F2 The NSSF employee contribution (5 %) is not deductible: tax is paid on contributions
- kind: model-fix
- NSSF Act s. 12(1): 5 % of total wages, no ceiling; no provision of the Income Tax Act text read allows a deduction. Statutory top combined rate on wages 35 % below 120 M (30 % + 5 %), 45 % above (scanner top line at 10 x 4.92 M = 49.2 M shows 35 %).
- provisions: NSSF Act ss. 11-12; ITA s. 6
- Lean: UgTax.person
- status: modelled

### F3 The 2025/26 law was not reachable: neither ULII nor the Parliament's Acts pages list an Income Tax (Amendment) Act 2025
- kind: statute-fault
- ULII's Income Tax Act page (captured 2025-10-20) lists versions 2000-12-31, 2023-12-31, 2024-12-23 only; parliament.go.ug 'Acts 2024' holds the Income Tax (Amendment) Act 2024 (withholding on payment-service-provider commissions only) and there is no 'Acts 2025' page. A citizen cannot read the year's law from the official sites: recorded as an access gap, not a law fault.
- provisions: ITA; Income Tax (Amendment) Act 2024
- Lean: -
- status: recorded

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|
| K1 | Take income as rent (separate 12 % rental tax) rather than wages | not modelled: rental tax not in the exe | ITA s. 5, Schedule 4 Part II |
| K2 | Shift income to a spouse (individual taxation, 2.82 M zero band each) | recreated: filing-unit scanner split gains | ITA s. 6 |
| K3 | Stay below 120 M of chargeable income (additional 10 %) | recreated: marginal band, no notch | Schedule 4 Part I para. 1(b) |
| K4 | Exempt income list (s. 21) for special employments | not modelled | ITA s. 21 |

## Step 5: what was searched

- kernel scanners with scale 4,920,000 (start of the 30 % band)
- Schedule 4 Part I printed fixed amounts proved with #guard
- Income Tax (Amendment) Act 2024 read in full (no rate change)

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### W5S-1 payroll_africa (Uganda): NSSF deducted before PAYE (reading); calcular: 10 % band untaxed (W5 review pass 2, 2026-11-20)
- kind: software-error
- `ug_open_payroll_africa_y2025_grid`: calculators/uganda.py taxes gross - employee NSSF ('NSSF employee contribution is deducted before tax'); the Income Tax Act gives no such deduction (UgTax: 'NSSF 5 % not deductible'). `ug_open_calcular_y2025_grid`: a constant +120,000 a year = the whole Schedule 4 Part I 10 % band (2,820,000-4,020,000) untaxed by the app, +165,000 above it.
- status: recorded (world/IMPROVE_W5.md pass 2)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | lead | Rent on its own 12 % scale: not modelled. |
| F2 | explained | NSSF not deductible: design. |
| F3 | explained | 2025/26 law not reachable: access record. |
| W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: no notch; wedges are model gaps. |

<!-- L1-VERIFICATION END -->
