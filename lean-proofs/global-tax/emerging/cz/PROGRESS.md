# Czechia (CZ), tax year 2025: progress

Owner: CZ sub-agent of the emerging group. Folder `~/cmp20/emerging/cz/` only. Contract: `~/cmp20/CONTRACT20.md`.

## Status: done (7/7 steps); open items below

| Step | State | Where |
|---|---|---|
| 1 Model | done | `lean/` (CzTax, exe `cztax`), builds clean, 0 sorry, no native_decide; depends on TaxKernel by path (`czSched` bridge) |
| 2a OECD TW 2025 | done | 56 line-cases: 26 exact, 56/56 within 1 %, THP 8/8 within 11 CZK; F1, F2 explain every difference |
| 2b Official worked figures | done | Finanční správa paušální daň 2025: 12 amounts + 3 band examples, exact (`Tests.lean`) |
| 3 Proofs | done | `Theorems.lean`, `KernelBridge.lean`, `Walls.lean` (schedule, rounding, credits, notches, withholding, N1/N2) |
| 4 Known loopholes | done | `CATALOGUE.md`: 24 catalogued, 16 recreated, 8 not modelled; blind search finds 5 |
| 5 New loopholes | done | F5, F6 (child credit vs přídavek), F8 (paušální daň band notches); F7, F9 notches known |
| 6 Gov errors / statute faults | done | F3 (dead bonus cap § 35c(7)), F10 (withholding), F11 (68 000 Kč not indexed), F12 (MF relief report), F13 (clean) |
| 7 USEFUL.md | done | `USEFUL.md` |

## Open / next
- Switch Rounding/Credit/Social to TaxKernel parts where they fit (kernel Contribution is yearly; monthly rounding
  needed here). Generic scanners: only `metr.py` existed; rerun `~/cmp20/harness/search/run_all.py CZ` when it exists.
- OSVČ minimum imputed income in the přídavek test (ZSSP § 5 odst. 5: 50 % of the national average monthly wage,
  MPSV notice not fetched) is not modelled; affects low-income self-employed families only.
- Verify F5/F6 reading with an official Úřad práce example (employer income confirmation form); DSSP (zákon
  151/2025) other conditions not modelled.
- State-insured status (health) uses a default rule; job seekers and students need `czStateInsured`.

## How to resume
- Build: `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build`; OECD: `python3 ~/cmp20/emerging/oecd/check.py CZ`
  (or `python3 ~/cmp20/harness/oecd_check20.py CZ`).
- Scripts: `tools/recreate.py`, `tools/blind.py`, `tools/notches.py`, `tools/wh_scan.sh` (withholding, `cztax --wh lo hi
  step kids`), `tools/stats.py` (Lean counts), `tools/esb_fetch.py act date outdir` (e-Sbírka API, 1.5 s apart).
- Statute copies: `refs/esb/*/text.txt` (ZDP 2020-12-31, 2025-01-01, 2025-12-31; 589/1992, 592/1992, 48/1997, 117/1995
  2025-05 and 2025-10, 151/2025, 152/2025, 155/1995, 187/2006, 280/2009, 427/2011, 435/2004, 110/2006, NV 436/2022, 609/2020);
  `refs/fs_pausal_2025.txt`, `refs/mf_ulevy_2023.txt`, `refs/mpsv_vycet_prijmu.txt`.
- Web searches used: 4 of 6.
