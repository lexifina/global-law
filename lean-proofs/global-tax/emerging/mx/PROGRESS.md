# Mexico (MX): progress

Owner: MX sub-agent of the emerging group. Tax year: ejercicio fiscal 2025 (= calendar 2025). Files: `lean/` (Lake
project MxTax, exe `mxtax`, depends on `~/cmp20/kernel` TaxKernel 1.0 by path), `oecd_map.py`, `FINDINGS.md`
(F1-F17), `CATALOGUE.md` (K1-K14), `USEFUL.md`, `HOWWRITTEN.md`, `results/summary.json`, `results/oecd_check.*`,
`results/search/` (harness scanners), `refs/` (official sources fetched), `runs/` (scan scripts and outputs).

## Status: DONE (7/7), 2026-11-19 (resumed after the usage-limit reset; summary.json status "done")
| Step | State |
|---|---|
| 1 Model + exe | DONE: ISR arts. 152/96 (RMF 2025 Anexo 8), art. 93 exemptions (aguinaldo, prima, previsión social, pensions), art. 151 (donativos, fr. V, caps), subsidio para el empleo (DOF 01-05-2024 + 31-12-2024, monthly and annual), dividends art. 140 (gross-up/credit chosen), gains art. 129, rent art. 115, interest (as given), RESICO 113-E/F with in-year exit (RMF 3.13.5), own-company option, asimilados, IMSS employee quotas (calendar or OECD UMA). |
| 2 Validation | OECD 56 lines: 41 exact, 48 within 1 %; all income-tax lines exact; EECSSC exact with `mxImss:"oecd"`; THP gap = cesantía y vejez (F1). DOF decree figures 3/3. SAT calculators need a login: not run. |
| 3 Proofs | 37 theorems (incl. kernel 1.1 `Table` checks of the cuotas fijas), no sorry/native_decide: tarifas vs kernel bands (all incomes), non-monotone tarifa, subsidy cliffs, IMSS notch, RESICO notches, deduction caps, OECD/decree figures. |
| 4 Known loopholes | CATALOGUE.md: 14 catalogued, 10 recreated, 4 not modelled. |
| 5 New loopholes | F6-F9, F11, F16 (subsidy cliff monthly/annual, December aguinaldo, IMSS art. 36, RESICO exit months, timing). |
| 6 Gov/statute | F4, F5, F11 (gap), F13, F14 statute-faults; OECD conventions F1-F3 explained (no gov error found). |
| 7 USEFUL.md | done |

## Left open (documented, not blocking)
- Interest: real-interest adjustment (art. 134) with a principal/inflation input; RLISR art. 174 option for the aguinaldo.
- Retained-profit deferral for the own-company route; art. 185 deferral; PTU and overtime exemptions.
- Verify the 2023/2026 tarifa updates against INPC (art. 152 último párrafo) with INEGI data.
- Note for the group/kernel: Global law `compare_dates` on LISR art. 151 (2021-06-30 vs 2022-06-30) reported "no
  difference" although `search_law` shows different texts on those dates (phrase_history confirms the change).

## Resume notes
- Build: `cd ~/cmp20/emerging/mx/lean && export PATH=$HOME/.elan/bin:$PATH && lake build`; OECD: `python3 ~/cmp20/emerging/oecd/check.py MX`; scans: `cd runs && python3 scan_wage.py | quantify.py | scan_regime.py`; harness: `python3 ~/cmp20/harness/search/run_all.py MX --out ~/cmp20/emerging/mx/results/search`.
- diputados.gob.mx unreachable from lean1 and the laptop; use Global law for text, dof.gob.mx (no www) / sidof / sat.gob.mx for tables.
- Web searches used: 5 of 6.
