# Luxembourg (LU), tax year 2025: progress

Worker: germanic/LU. Folder `~/cmp20/germanic/lu/`. Updated 2026-11-19. **Status: done (7/7 steps).**

| Step | State | Where |
|---|---|---|
| 1 Model | done: `lean/` (LuTax, exe `lutax`, options `--oecd`, `--individual`; probe fields `luRIA`, `luGross`, `luRIAC`), 626 lines, 111 defs | `lean/LuTax/{Params,Basic}.lean`; texts in `law/` (L.I.R. coordinated 1.1.2024/2025/2026 by the ACD, amending laws 20.12.2024, FE law 1976 cons. 1.1.2024, CSS 2025, Code du travail 2025, RELIBI 2005 + reform 2016) |
| 2 Validation | done: OECD 48/56 exact, 56/56 within 1 %; ACD formulas 24 003/24 003; ACD calculator 387/387; circular examples 11/11; salary table vs statute reported (F4) | `results/oecd_check.md`, `results/validate.json`, `harness/validate.py`, `harness/calc.py` |
| 3 Proofs | done: 32 theorems, no sorry | `lean/LuTax/Theorems.lean` |
| 4 Known loopholes | done: 21 catalogued, 12 recreated (11 blind), 9 not modelled | `CATALOGUE.md` |
| 5 New loopholes | done: 4 (N1-N4) | `NOVEL.md`, `results/scan_lu.json`, `results/search/SUMMARY.md` |
| 6 Government errors | done: 2 gov errors (OECD CTGG; salary table convention), 4 statute faults (FE law typo and art. 7; L.I.R. references; CIS gaps) | `FINDINGS.md` F2, F4-F8 |
| 7 Usefulness | done | `USEFUL.md` |

Reproduce: `export PATH=$HOME/.elan/bin:$PATH; cd lean && lake build`; `python3 ~/cmp20/germanic/oecd/check.py LU --args="--oecd"`;
`python3 harness/validate.py`; `python3 harness/scan_lu.py`; `python3 ~/cmp20/harness/search/run_all.py LU --out results/search`.
Open: F2 (OECD CTGG source), F5/F6 (original Mémorial wording of the 1976 law amendments), art. 123bis bonification and
alimony reduction of the CIM not modelled. Web searches used: 2 of 3.
