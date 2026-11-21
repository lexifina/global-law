# Australia (AU): progress

Year: income year 2024-25 (1 July 2024 - 30 June 2025) = the OECD's "2025" for Australia (the OECD chapter is titled
"Australia (2024-2025 income tax year)"; OECD 2024 S67 matches the 2023-24 rates, 2025 the 2024-25 rates). 2025-26
modelled as a second year (`"year": 2026`): same rates; new Medicare, MLS, FTB and HELP parameters.

## Status (2026-11-19 01:20 UTC): done, 7/7 steps
- [x] 1 Parameters + sources (`refs/SOURCES.md`; statute via Global law / legislation.gov.au; ATO, DSS, OECD pages
      via web.archive.org snapshots because the live sites answer 403)
- [x] Model `lean/` (AuTax, exe `autax`, also `ausched`), on TaxKernel 1.0 (Schedule, Surcharge, Credit, Taper);
      1,198 lines, 84 definitions, 37 theorems, 22 #guard checks, 0 sorry (12 native_decide)
- [x] 2 Validation: OECD 40/40 within $1 with the OECD's assumptions (`harness/oecd_check.py --es`), 36/40 on
      statutory defaults (kernel `oecd_check20.py AU`); PAYG Schedule 1 sample data 240/240; 16 official examples
- [x] 3 Proofs: kernel Schedule theorems instantiated (progressive, monotone, convex, 45 % Lipschitz, closed forms),
      LITO and Medicare levy kernel forms proved equal to the statute's words, MLS notch from `exempt_notch`,
      named notches, Schedule 1 never under-withholds
- [x] 4 Known loopholes: `CATALOGUE.md` (24 catalogued, 15 recreated, 7 blind, 9 not modelled)
- [x] 5 New loopholes: `harness/scan.py`, `harness/generic_scan.py`, kernel scanners (`results/search/`): F3, F14
- [x] 6 Government / statute errors: F8-F13
- [x] 7 `USEFUL.md`, `results/summary.json`

## Files
`FINDINGS.md` (F1-F16), `CATALOGUE.md`, `USEFUL.md`, `results/summary.json`, `results/search/SUMMARY.md` (kernel
scanners), `runs/` (oecd_2025.json, oecd_2025_es.json, metr_scan.json, loopholes.json, generic_scan.json,
sched1_vs_statute_2025.csv / 2026.csv), `harness/` (common.py, oecd_check.py, scan.py, loopholes.py,
generic_scan.py, write_summary.py).

## How to rerun
    export PATH=$HOME/.elan/bin:$PATH; cd ~/cmp20/anglo/au/lean && lake build
    cd ../harness && python3 oecd_check.py --es && python3 oecd_check.py && python3 scan.py && python3 loopholes.py \
      && python3 generic_scan.py && python3 write_summary.py
    python3 ~/cmp20/harness/search/run_all.py AU --out ~/cmp20/anglo/au/results/search

## 2026-11-19 01:30 UTC: cohabiting couples (coordinator follow-up)
`autax` now reads `married || cohabiting` as a couple (Household.lean `coupled`, citations in its docstring); before,
any two adults were a couple unless `"deFacto": false`. Rebuilt; OECD check unchanged (40/40 with --oecd, 36/40
defaults); METR scan, loophole scenarios and the kernel unit scanner unchanged (marriage penalty 0.0 % of the grid:
married and cohabiting households now give identical results). No finding depended on it; FINDINGS F17 added.

## Open issues
- PP(S) parameters are the OECD's annualised figures (DSS rate lists unreachable); the real test is fortnightly.
- SAPTO, Division 6AA (minors), excess concessional contributions, reportable fringe benefits, PSI rules: not modelled
  (flagged in `unsupported`).
- The kernel's `harness/search/company.json` has no AU entry (owner-manager scanner skipped); the AU owner-manager
  comparison is in `harness/loopholes.py` (K8, K9). Suggested entry: cit 0.25 (base rate entity, ITRA s. 23(2)),
  no employer social contributions (the 11.5 % SG is a super contribution, Superannuation Guarantee (Administration)
  Act 1992 s. 19).
- Novelty of F3 and F14 checked with 1 web search only.

## Notes for a resuming agent
- ATO and DSS sites answer 403 to lean1 and to WebFetch; read their pages from web.archive.org `id_` snapshots.
  legislation.gov.au works directly (docx/epub links).
- Couple = `married` or `"cohabiting": true` (kernel API 1.0.2; `"deFacto": true` read the same), per ITAA 1997
  s. 995-1 "spouse" (de facto partner), MLA s. 3(4) / ITAA 1936 s. 6(1), FA Act s. 3(1) "member of a couple".
  Two adults with neither flag are unrelated housemates (children belong to the first).
- `autax --oecd` = `--es --income-support` (the OECD's assumptions).
