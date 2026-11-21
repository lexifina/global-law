# Slovenia (SI), tax year 2025: progress

Owner: SI worker of the central family. Folder `~/cmp20/central/si/` only. Contracts: `~/cmp20/CONTRACT38.md`,
`~/cmp20/CONTRACT20.md`; kernel `~/cmp20/kernel/API.md`. Relatives read: `~/cmp20/emerging/{cz,pl}`, `~/cmp/de`.

Updated: 2026-11-19

## Status: done (7/7 steps)

| Step | State | Where |
|---|---|---|
| 1 Model | done | `lean/` (SiTax, exe `sitax`, `TaxKernel.countryMain`): ZDoh-2 (NPB 34, in force 1.1.2025), FURS Lestvica 2025, contributions incl. OZP and long-term care, otroški dodatek + large-family allowance, capital/rent/flat-rate s.p. final taxes; cents internally |
| 2 Validation | done | OECD TW 2025: 56/56 exact, THP 8/8 (`results/oecd_check*.{json,md}`); FURS tables: 26 printed figures proved equal to the statute, 1 guide figure wrong (F5) |
| 3 Proofs | done | `Theorems.lean` (kernel one-liners, FURS table = schedule, indexation), `Findings.lean` (F7-F13 on named households); 0 sorry |
| 4 Known loopholes | done | `CATALOGUE.md`: 24 catalogued, 17 recreated (8 blind), 7 not modelled |
| 5 New loopholes | done | F9 dependent-spouse notch, F10 forgo child allowance, F11 flat-rate s.p. child benefit, F14 flat-rate income outside the allowance test |
| 6 Gov errors / statute faults | done | F2 (convention), F5 (FURS guide), F3 and F6 (statute) |
| 7 USEFUL.md | done | `USEFUL.md` |

Web searches used: 3 of 3 (normiranci literature; OECD/low-wage METR literature; normiranci and child benefit).
Generic scanners: `results/search/SUMMARY.md` (run_all.py SI). Own scans: `tools/scan_si.py` (S1, S2, S4-S6),
`tools/scan_s3.py` (S3) → `results/scan_si.json`.

## Open
- Child benefit uses the same year's income and the March-2025 amounts for 12 months (OECD convention); the law uses
  the previous calendar year (ZUPJS čl. 15(2)) and Jan-Feb 2025 used the 2024 amounts (Sklep 2024 not fetched).
- Not modelled: employee minimum contribution base (60 % PP), tax-free bonus/holiday pay, student work, voluntary
  pension premium, new-resident credit, special-needs children, parents as dependants, assets test, +20 % for a child
  under 4 not in kindergarten, s.p. contribution base from the previous year's profit.
- F10 legality (forgoing a relief to keep a lower class) not tested against CSD practice; F11 reading rests on
  PRAV12104 čl. 10(2).
- No public FURS calculator without login was found; official worked examples with full computations: none found.

## How to resume
Build: `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build`. OECD: `python3 ~/cmp20/central/oecd/check.py SI`
or `python3 ~/cmp20/harness/oecd_check20.py SI --out ~/cmp20/central/si/results`. Scanners:
`python3 ~/cmp20/harness/search/run_all.py SI --out ~/cmp20/central/si/results/search`. Stats: `python3 tools/stats.py`.
Statute copies: `refs/zdoh2_npb34.txt` (also NPB 33, 35, 36, osnovni), `refs/zupjs_npb21.txt`, `refs/zsdp1_npb7.txt`,
`refs/skle13906_transferji_2025.txt`, `refs/prav12104_npb1.txt`; FURS: `refs/fu_*`. PISRS texts come from
`https://pisrs.si/api/rezultat/zbirka/id/<ID>` (versions) and `https://pisrs.si/api/datoteke/integracije/<file id>`.
Extra input fields: per adult `siNormRevenue`, `siNormFullTime`; household `siHoldingYears`, `siChildClaim` (0, 1,
"half"), `siForgoDependants`, `siLoneParent`, `siChildrenInSchool`, `cohabiting`.
