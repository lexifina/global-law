# Sweden (SE, Stockholm municipality), inkomstår 2025: progress

Owner: SE agent (delegated by the Nordic lead). Contract: `~/cmp20/CONTRACT20.md`. Folder: `~/cmp20/nordic/se` only.

## Status: DONE (all 7 steps)
Updated: 2026-11-19 (milestone 4, final)

| # | Step | Status |
|---|---|---|
| 0 | Read contracts, DE style, UK loop catalogue, kernel API.md | done |
| 1 | Parameters 2025 with citations (`refs/PARAMS.md`), statute text (`refs/raw/`) | done |
| 1 | Lean model `lean/` (SETax on TaxKernel by path, exe `setax`) | done: 948 lines, 60 definitions, 56 theorems, 0 sorry |
| 2a | OECD Taxing Wages 2025 (`harness/oecd_check.py`) | done: 56/56 lines exact |
| 2b | Official worked examples (SKV 433 2025) as Lean theorems (`SETax/Tests.lean`) | done: 22/22 |
| 2c | Skatteverket withholding tables 2025, open data (`harness/table_check.py`, `harness/pct_scan.py`) | done: 26 936/26 936 cells; percent rows 360 919/360 928 steps (9 ties) |
| 3 | Proofs (`SETax/Theorems.lean`, `SETax/Loopholes.lean`) | done |
| 4 | Known loopholes (`CATALOGUE.md`) | done: 29 catalogued, 17 recreated, 12 not modelled |
| 5 | New loopholes (`harness/scan.py`, `harness/loop.py`, kernel scanners in `results/search/`) | done: 1 new (F2) |
| 6 | Government / statute errors (`harness/gov_check.py`, versioned law) | done: 0 gov errors (3 conventions, 2 verifications), 3 statute faults |
| 7 | `USEFUL.md`, `FAMILY_NOTES.md`, `results/summary.json` | done |

Done 7/7. Next (optional): the 3:12 huvudregel (lönebaserat utrymme, 2025 wording of 57 kap. 16-19 §§ not yet
retrieved); kyrkoavgift as an option; ISK/KF in the Lean model; answer to the F3 question if Skatteverket's
skatteuträkningsbroschyr (SKV 425) for 2025 states the order of the taxes.

## How to resume
- Build: `export PATH=$HOME/.elan/bin:$PATH; cd ~/cmp20/nordic/se/lean; lake build` (kernel by path ../../../kernel).
- Run: `echo '{"id":"x","adults":[{"age":40,"wages":557053}]}' | lean/.lake/build/bin/setax` (`--oecd` for the
  OECD's average municipal rate and no begravningsavgift; `--state-first` for the other reading of 67 kap. 2 §;
  `--table T COL MONTH` for one withholding-table cell). Extension fields: `seKommunBp`, `seBegravningBp`,
  `interestPaid`, `seKapital: [k1, k2]`, `seGifts: [g1, g2]`.
- Checks: `cd harness; python3 oecd_check.py; python3 table_check.py; python3 pct_scan.py; python3 scan.py;
  python3 loop.py; python3 gov_check.py` (results in `runs/`); kernel scanners:
  `python3 ~/cmp20/harness/search/run_all.py SE --out ~/cmp20/nordic/se/results/search`.
- Sources: `refs/raw/` (IL current text from riksdagen, amending SFS PDFs 2024:1131, 2025:539/1361/1370/1376,
  2022:445, 2021:1160, 2019:454, SKV 433 2025, Belopp och procentsatser 2025, SCB/Skatteverket rate files, KPI),
  `refs/tables/skattetabeller_2025.json` (7 934 rows, open data).

## Notes / proposals
- The task text names IL 63 kap. 11-11 b §§ for grundavdrag; in the 2025 statute it is 63 kap. 3, 3 a, 5 §§.
- Age convention: contract `age` = age reached in 2025, so "fyllt 66 vid beskattningsårets ingång" = age >= 67.
- Proposed SE entry for the kernel's `~/cmp20/harness/search/company.json` (not written: outside this folder):
  `"SE": {"cit": 0.206, "cit_note": "IL 65 kap. 10 §: 20,6 %", "employer_rate": 0.3142, "employer_threshold": 0,
  "salary_points": [475100, 643100], "source": "Skatteverket, Belopp och procentsatser för inkomståret 2025
  (arbetsgivaravgifter 31,42 % for those born 1959 or later); dividends: IL 57 kap. 20 § (2/3 in kapital up to the
  gränsbelopp, 209 550 kr by the förenklingsregel), above it inkomstslaget tjänst"}`.
- Web searches used: 6 of 10.
