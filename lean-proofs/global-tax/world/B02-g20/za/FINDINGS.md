# South Africa (ZA) findings, B02-g20 (2026-11-20T01:50Z)

Built from the statute only (no referee values seen). Leads from the B02 generic scan (`results/search/b02scan.md`).

### F1 Third year without bracket or rebate indexation (2024-2026)
- kind: fact
- SARS marks 2025 'No changes from last year' and 2026 'No changes': the 2024 table and rebates applied for three years (fiscal drag).
- provisions: s. 5, s. 6 (as fixed by the Rates Acts)
- Lean: ZaTax.sched
- status: fact

### F2 Generic scan: no notch; max METR 45 % + UIF
- kind: model-fix
- b02scan 0-2.5 × R1.817m: no net-income fall (rebates are flat credits; no withdrawal).
- provisions: -
- Lean: results/search/b02scan.md
- status: scan done


### W5S-1 payroll_africa (South Africa): UIF deducted from the PAYE base (W5 review pass 2, 2026-11-20)
- kind: software-error
- `za_open_payroll_africa_grid`: calculators/south_africa.py computes taxable income as (gross - UIF) x 12 ('UIF is deductible before PAYE calculation'); the Income Tax Act 58 of 1962 allows an employee no deduction for UIF contributions (s. 23 (m) limits an employee's deductions to those listed; UIF is not among them). PAYE too low by 45 % x 2,125.44 = 957 at the cap.
- status: recorded (world/IMPROVE_W5.md pass 2)

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | explained | No bracket indexation 2024-2026: fact (fiscal drag). |
| F2 | explained | Superseded by the L1 rescan 2026-11-20 22:44 CET (world/tools/scan_world.py --full, current exe; results/search/SUMMARY.md): no notch. |
| W5S-1 | explained (record of model/test work, not a loophole; kept as written) |  |
| Leads | explained | Rescan: capital-gains wedge +42.9 % is a model gap; dividends +22.9 % = 20 % DWT vs 45 % top rate (known). |

<!-- L1-VERIFICATION END -->
