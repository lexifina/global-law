# Ireland (IE), year of assessment 2025: progress

Owner: IE worker of the Westminster family (`~/cmp20/anglo/ie`). Contract: `~/cmp20/CONTRACT20.md`.

## Status: DONE (all 7 steps); see FINDINGS.md, USEFUL.md, CATALOGUE.md, results/summary.json

| Step | What | Status |
|---|---|---|
| 1 | Research + parameters (FA 2024, SWCA 2005 as revised, SW(MP)A 2024, SWA 2024, Revenue notes for guidance) | done |
| 2 | Lean model `lean/` (lib `IeTax`, exe `ietax`, on TaxKernel 1.0) | done: builds, 0 sorry |
| 3a | OECD Taxing Wages 2025 (8 types) | done: 32 lines, 22 exact, 31 within 1 %; under the OECD's own conventions (`--oecd`) 31/32 exact; every gap explained (F2-F4) |
| 3b | Official worked examples | done: 15 `#guard` (Revenue TDM 44-01-01 Ex. 3, 5, 7; TDM 18D-00-01 Ex. A, B, para 4.3, para 1; OECD lines) |
| 3c | Open model / calculator | no open Irish model exists (no OpenFisca/PolicyEngine Ireland on PyPI; checked 2026-11-19); Revenue has no public liability calculator; "table vs statute" done on Revenue's Employers' Guide to PAYE (cut-off points) |
| 4 | Proofs | 39 theorems, 31 `#guard`s, 0 sorry (kernel instances; band transfer; joint <= single; USC notch; PRSI notch/taper; home carer; s. 188; findings) |
| 5 | Known loopholes recreated blind | done: CATALOGUE.md, 22 catalogued, 12 recreated, 7 not modelled |
| 6 | New loopholes (scans) | done: harness/scan.py S1-S6, results/search/; 0 new claimed |
| 7 | Government / statute errors | done: 6 gov errors (F1, F2, F4-F7), 3 statute faults (F3, F8, F9) |
| 8 | USEFUL.md | done |

## How to resume
- Sources are edited locally in the agent scratchpad and copied here; the copy here is the truth.
- Build: `cd ~/cmp20/anglo/ie/lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (checks are `#guard`s: the build
  fails if an official example stops matching).
- OECD: `python3 ~/cmp20/anglo/ie/harness/oecd_ie.py [--args=--oecd]` (writes `results/oecd_check*.json`) or the
  kernel's `python3 ~/cmp20/harness/oecd_check20.py IE`.
- References saved in `refs/` (FA 2019-2024 text, SWCA revised PDF/text, SW(MP)A 2024, SWA 2024, Revenue notes for
  guidance `refs/nfg/`, TDMs `refs/tdm/`, rate charts `refs/rev/`).

## Decisions
- Year = calendar 2025. PRSI Class A1: weekly pay = wages/52, Friday pay days, 39 weeks at 4.1 % and 13 at 4.2 %
  (SW(MP)A 2024 s. 3). Class S: 4.125 % blended (the Department's and Revenue's reading, F3).
- Married couple: the better of joint assessment (with the better of the s. 15(3) band increase and the s. 466A home
  carer credit) and single treatment of each spouse (s. 1018 election); separate assessment (s. 1023-1024) equals
  joint by statute and is not computed separately.
- Contract `pension` = occupational pension (PAYE emoluments: employee credit, USC; no PRSI).
- Web searches used: 6 of 7.
- Open items: employer pension route for owner-managers, rent-a-room, medical card USC, PRSI on irregular weekly pay
  (annual model), WFP assessed at claim (annual approximation), DIRT refund to over-65s (s. 267). The WFP €20
  minimum rests on secondary sources (the Department's page and the regulation could not be fetched by script).

Updated: 2026-11-19 (milestone: all steps done)
