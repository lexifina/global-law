# Finland (Helsinki), tax year 2025: progress

Owner: FI worker of the Nordic + Baltic family. Contracts: ~/cmp20/CONTRACT38.md + CONTRACT20.md. Writes only in
~/cmp20/baltic/fi/. Status: **done** (7 of 7 steps), 2026-11-19.

| step | status | where |
|---|---|---|
| 1 model | done: `lean/FiTax` (Params, Assess, Household, Main), exe `fitax`, cents, 870 lines, 113 defs | `lean/` |
| 2 validation | done: OECD 48/48 lines + 8/8 THP (at 7,54 %); Veronmaksajat 287/287; Kela 32/32; Vero thresholds 4/4 | `results/oecd_check_FI.md`, `runs/referees.json`, `FiTax/Tests.lean` |
| 3 proofs | done: 53 theorems, no `sorry` (kernel one-liners, table = formula, notches, findings) | `FiTax/Theorems.lean`, `Tests.lean`, `Loopholes.lean` |
| 4 known loopholes | done: 22 catalogued, 12 recreated, 10 not modelled | `CATALOGUE.md` |
| 5 new loopholes | done: F3 (bunching pays in 2025), F4 (8 % band can raise the tax) | `FINDINGS.md`, `runs/fi_scan.json`, `results/search/` |
| 6 gov/statute errors | done: G1, G2 (HE threshold mislabels), R1, R2 readings; no stale references found | `FINDINGS.md` |
| 7 USEFUL | done | `USEFUL.md`, `FAMILY_NOTES.md` |

## How to rebuild and rerun (a fresh agent can resume from here)
- `cd ~/cmp20/baltic/fi/lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (kernel by path `../../../kernel`).
- OECD: `python3 ~/cmp20/baltic/harness/b38.py oecd FI --out ~/cmp20/baltic/fi/results` (map: `oecd_map.py`, which
  reads the exe's `oecd754_*` detail lines computed at the OECD's average municipal rate 7,54 %).
- Other referees: `python3 harness/referees.py` -> `runs/referees.json` (Veronmaksajat table parsed into
  `refs/veronmaksajat_2025_table.json`; Kela rows typed in the script from `refs/kela_elaketulo_verotaulukko.txt`).
- Scans: `python3 ~/cmp20/baltic/harness/b38.py scan FI --out results/search`; `python3 harness/fi_scan.py`;
  owner-manager with Finland's own company side: `python3 harness/owner_fi.py` (see FINDINGS M2: b38.py otherwise
  prefers the harness's generic FI entry).
- Statute texts: `refs/` (Finlex pages decoded by `refs/rsc2txt.py`, all versions with their amending acts).

## Model scope and choices
- Inputs in the contract; extension fields: `municipalRateBp` (default Helsinki 530), `churchRateBp` (default 0,
  church tax off), `fiUnlistedDividends` + `fiNetAssets` (TVL 33 b §, adult 1), `fiYel` (owner insured under YEL: no
  TyEL/unemployment on the salary; the YEL contribution itself is not modelled), `cohabiting`.
- Contract `dividends` = listed-company dividends (85 % capital income). Capital gains taken as given (no deemed
  acquisition cost). Self-employment taxed as earned work income (no YEL, no business-income split).
- Canonical `age` = age at the end of 2025 ("täyttänyt 65 vuotta ennen verovuoden alkua" = age 66+).
- Not modelled: kotitalousvähennys, elatusvelvollisuusvähennys, opintoraha- and merityötulovähennys, voluntary
  pension (54 d §), osakesäästötili, church tax by default.

## Notes for the family lead
- M2: the harness's FI company entry (OECD generic) shadows `fi/company.json` in b38.py and routes the owner's
  dividend as listed; use `harness/owner_fi.py` or let the kernel adopt `fi/company.json`.
- Web searches used: 3 of 3 (2025 scale act number; 2025 contribution rates; 2025 municipal rates).
