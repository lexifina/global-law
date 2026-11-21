# Lithuania (LT) 2025: progress

Owner: LT worker of the Nordic + Baltic family. Contracts: ~/cmp20/CONTRACT38.md, ~/cmp20/CONTRACT20.md.
Status: **done** (7/7 steps), 2026-11-19. Resume: everything is rebuilt by
`cd lean; export PATH=$HOME/.elan/bin:$PATH; lake build` then `python3 tools/oecd_years.py results/oecd_years.json`,
`python3 ~/cmp20/baltic/harness/b38.py oecd LT --out results`, `python3 ~/cmp20/baltic/harness/b38.py scan LT --out
results/search`, `python3 tools/owner_lt.py standard|small`, `python3 tools/studies.py`, `python3 tools/summary.py`.

| step | status | where |
|---|---|---|
| 1 model | done: GPMĮ 6, 10, 16, 17, 18², 20, 21 str.; Sodra contributions; child benefits; years 2022-2026 | `lean/LtTax/{Params,Npd,Tax}.lean` |
| 2 validation | done: OECD TW 2025 56 lines 55 exact (harness); OECD 2022-2025 128 lines 122 exact, 126 within 1 %; VMI RM-5567 + 5 OECD NPD lines to the cent (theorems); no official calculator usable (vmi.lt / sodra.lt calculators behind Cloudflare) | `results/oecd_check_LT.md`, `results/oecd_years.json`, `Theorems.lean` |
| 3 proofs | done, no `sorry` | `lean/LtTax/Theorems.lean` |
| 4 known loopholes | done: 16 catalogued, 10 recreated (5 blind), 6 not modelled | `CATALOGUE.md` |
| 5 new loopholes | done: F1-F5, F7 (+ F6 known with a new detail, F8 withholding) | `FINDINGS.md`, `results/studies.md`, `results/search/`, `results/owner_*` |
| 6 gov / statute errors | done: F9-F12 errors (EUROMOD ×3, Sodra ×1), F13 OECD convention, F14-F16 statute, F17 reading | `FINDINGS.md` |
| 7 USEFUL | done | `USEFUL.md`, `FAMILY_NOTES.md` |

Source limits (read before extending): e-TAR, e-seimas, vmi.lt, lrv.lt, infolex and oecd.org return 403 (Cloudflare) to
scripts from lean1 and from the laptop; not bypassed. Statute text = web.archive.org copy of the e-TAR consolidated text
from 2023-01-01 (`refs/gpmi_2023_redakcija.txt`); 2025 amounts from EUROMOD CR LT 2022-2025 (JRC), PwC 2025 (archived),
Sodra (archived), OECD TW, a VMI written answer (2024). The 2025 consolidated text (2025-01-02 to 2025-12-31) exists in
the archive's index but its text frame was not archived. Web searches used: 3 of 3.

Open: the 2025 disability NPD (1 124 or 1 127 €), the 2026 individual-activity regime, verslo liudijimas and MB
regimes, the exact income definition of the child-benefit test (act unreachable), F13 (OECD 2022 convention).
