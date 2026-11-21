# Canada (federal + Ontario), tax year 2025: progress
Updated 2026-11-19 (milestone: all 7 steps done). Status: done. Done 7/7.

| Step | Status | Where |
|---|---|---|
| 1 research | done | refs/leg (ITA XML 2025-06-27 and 2026-06-18, CPP, EI, S.C. 2026 c.2), refs/cra (T4127 Jan 2025, TD1, TD1ON, ON428, T4114 2025-26); Global law for OTA 07t11 |
| 2 model | done | lean/ (CaTax on TaxKernel), exe catax; 6 modules, no sorry |
| 3 validation | done | OECD 52/56 to the cent (all tax/SSC lines); T4127 601/601 within $1; PolicyEngine (benefits) |
| 4 known loopholes | done | CATALOGUE.md: 16 catalogued, 8 recreated blind, 7 not modelled |
| 5 new loopholes | done | harness/scan_ca.py + kernel scanners (results/search, results/search/kernel): F1 METR > 100 %, F6 bunching |
| 6 gov / statute errors | done | F8, F9 (gov), F10-F12 (statute), F13 reading, F14 open (OECD CTGG), F15 (PolicyEngine) |
| 7 usefulness | done | USEFUL.md |

Open: F14 (OECD cash transfers +$255.09 for couples, +$627.58 single parent: needs the OECD country chapter);
alternative minimum tax not modelled (affects F5); OAS not in the contract; provinces other than Ontario.

Resume commands: `cd lean && lake build`; `python3 harness/oecd_ca.py`; `python3 harness/t4127_ca.py`;
`~/cmp20/anglo/venv/bin/python harness/pe_ca.py` (PE_YEAR=2026 FULL_CUSTODY=1 for the benefit comparison);
`python3 harness/scan_ca.py all`; kernel: `python3 ~/cmp20/harness/oecd_check20.py CA`,
`python3 ~/cmp20/harness/search/run_all.py CA --out ~/cmp20/anglo/ca/results/search/kernel`.
Web searches used: 4 of 8.

## 2026-11-19 follow-up: common-law partners
catax now treats a two-adult household as spouses when `married` or the kernel's optional `cohabiting` field is
true (ITA s. 248(1) "common-law partner"; `isSpouses` in lean/CaTax/Household.lean; also gates `--split-pension`).
Rebuilt (no sorry); OECD check unchanged (52/56 to the cent; kernel 47/56 exact, 52/56 within 1 %); kernel scanners
rerun: married vs cohabiting now differ nowhere (was a false "marriage penalty" at 72.8 % of couple points). F4
reworded (the penalty is for living together vs two households, not for marrying); CATALOGUE K6/K7 reworded.
No other finding depended on it.
