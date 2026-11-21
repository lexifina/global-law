# Bolivia (BO): progress

**Status (2026-11-20 07:15 UTC): built (models frozen for the software phase); access B.**

| Step | Status |
|---|---|
| 1 statute + 2025 amounts | done: SIN Ley 843 compilation (sac.impuestos.gob.bo 1.-LEY N 843-09-23.pdf, Internet Archive 2024-08-09); SIN D.S. 5383 PDF |
| 2 testing | not started (software phase W1, then datasets; no referee seen) |
| 3 proofs | done: 2 theorems, 2 #guard, 0 sorry |
| 4 known loopholes | catalogued 4, recreated 3 |
| 5 new loopholes | scanners run (results/search) + statute-visible notches proved |
| 6 gov errors | recorded in FINDINGS.md |
| 7 USEFUL.md | done |

Registry check: see the batch PROGRESS.md (registry corrections).

- 2026-11-20 W5 pattern A (contributions agent 2): SIP employee contributions 12.71 % (11 % from 65) of the monthly wage up to 60 SMN (Bs 165.000) plus the Aporte Nacional Solidario 1 / 5 / 10 % over Bs 13.000 / 25.000 / 35.000, when boEmployeeContrib is not given; deducted under Ley 843 art. 25. Provision: Ley 065 de Pensiones arts. 83 b), 87 b) and f), 88, 151 a), glossary "Total Ganado" (60 SMN); D.S. 778 annex table (Riesgo Común 1,71 %, Comisión 0,50 %) (aps.gob.bo). Rebuilt (#guards pass), check `w5/pa/check.py BO` 0 / 300 differ with the switch off, rescanned (`scan_world.py BO`).
