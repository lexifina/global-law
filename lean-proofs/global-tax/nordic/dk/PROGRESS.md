# Denmark (København), indkomståret 2025: progress

Owner: DK agent (delegated by the Nordic lead). Contract: ~/cmp20/CONTRACT20.md. Writes only in ~/cmp20/nordic/dk.

## Status (2026-11-19): DONE — 7/7 steps
| step | state | where |
|---|---|---|
| 1 model | done: lean/DKTax (Params 2023-2026, Person, Tax, Household, Main), exe `dktax`, kernel TaxKernel by path | lean/, refs/PARAMS.md |
| 2 validation | done: OECD 2023-2025 (statute + OECD-conventions runs), Skatteministeriet 2023 examples (27 #guards), Skatteministeriet marginal rates 2025-26 (16) | harness/oecd_check.py, harness/skm_marginal.py, runs/, results/oecd_check_DK.* |
| 3 proofs | done: 30 theorems in Theorems.lean, 5 in Loopholes.lean, no sorry | lean/DKTax/Theorems.lean, Loopholes.lean |
| 4 known loopholes | done: 24 catalogued, 15 recreated, 9 not modelled | LOOPHOLES.md |
| 5 new loopholes | done: Danish scans (harness/scans.py → runs/scans.json) + kernel scanners (results/search/) | FINDINGS F9-F17 |
| 6 gov / statute errors | done: 4 gov errors, 2 statute faults, 1 open reading | FINDINGS F1-F8 |
| 7 USEFUL.md | done | USEFUL.md, FAMILY_NOTES.md |

## How to rerun
- `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build` (Tests #guards and all theorems checked at build).
- `python3 harness/oecd_check.py`; `python3 harness/skm_marginal.py`; `python3 harness/scans.py` (~5 min);
  `python3 ~/cmp20/harness/search/run_all.py DK --out results/search`.

## Open
- Ordinært/ekstra børnetilskud 2025 are inferred (no official 2025 table found); 2023-24 not modelled.
- F8 (grøn check 140 kr. supplement) unresolved; folkepensionsalder by birth year not verified (only affects the 32 % ekstra pensionsfradrag).
- No DK entry in ~/cmp20/harness/search/company.json (kernel owner's file): the kernel's owner-manager scan skipped;
  suggested entry: {"DK": {"cit": 0.22, "cit_note": "selskabsskatteloven § 17, stk. 1: 22 pct.", "employer_rate": 0, "employer_threshold": 0, "salary_points": [611800], "source": "nordic/dk"}} (employer ATP/AES ignored).
- Not modelled: virksomhedsordningen, kapitalafkastordningen, rental income, ejendomsværdiskat, forskerordningen.
- Web searches used: 5 of 10.
