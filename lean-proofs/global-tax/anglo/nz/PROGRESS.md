# New Zealand (NZ): progress

Updated: 2026-11-19 (milestone 8: done)

Year: income year 2025-26 (1 April 2025 - 31 March 2026) = the OECD's "2025" for NZ (S100 income tax 17,291.59
exactly); 2024-25 (composite year, thresholds changed 31 July 2024) also modelled (`"year": 2024` in the household).

| # | Step | Status |
|---|---|---|
| 1 | Research + parameters (refs/SOURCES.md) | DONE. ITA 2007 not readable (not in Global law; legislation.govt.nz and NZLII block automated fetches; not bypassed): cited through IRD publications; ACC Act via Global law |
| 2 | Lean model `lean/` (NzTax, exe nztax) on TaxKernel | DONE: 683 lines, 50 definitions, money in cents; income tax, IETC, imputation, donation credit, ACC levy, WFF (FTC, IWTC, MFTC, Best Start), student loan (detail), PIE (extension) |
| 3 | Validation | DONE: OECD 2025 all mapped lines exact (THP differs by exactly the ACC levy, F1); OECD 2024 within 1 % (F2); IR340 = IRD spec on 69,228/69,228 cells; IR271 charts; 19 #guard examples |
| 4 | Proofs | DONE: 30 theorems, no sorry (Theorems.lean, Loopholes.lean) |
| 5 | Known loopholes | DONE: CATALOGUE.md, 16 catalogued, 12 recreated, 3 not modelled |
| 6 | New loopholes (scans) | DONE: kernel metr.py (results/search/), harness/scan_nz.py (2025, 2024), F9 notch, F10 METR > 100 % |
| 7 | Government/statute errors | DONE: F1-F8, F11, F14, F15 |
| 8 | USEFUL.md, results/summary.json | DONE |

Open: F7 and F8 need the Act's text (legislation.govt.nz); IRD online calculators not queried (JavaScript tools; the
payroll specification and tables were used instead); OpenFisca-Aotearoa unusable (F14).

Web searches used: 5 of 6.

Resume / rerun:
- build: `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build`
- OECD: `python3 harness/oecd_nz.py`; harness: `python3 ~/cmp20/harness/oecd_check20.py NZ --map ~/cmp20/anglo/nz/oecd_map.py`
- PAYE tables: `python3 harness/paye_tables.py`; IR271: `python3 harness/ir271_chart.py`
- scans: `python3 harness/scan_nz.py --year 2025|2024`; kernel `python3 ~/cmp20/harness/search/metr.py NZ --out ~/cmp20/anglo/nz/results/search`
- loopholes: `python3 harness/loopholes_nz.py`
