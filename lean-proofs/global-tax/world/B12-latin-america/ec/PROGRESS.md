# Ecuador (EC): progress

**Status (2026-11-20 07:15 UTC): built (models frozen for the software phase); access A.**

| Step | Status |
|---|---|
| 1 statute + 2025 amounts | done: SRI LRTI codification PDF (2025-10-31); SRI 'Tablas de calculo' PDF; SRI Impuesto a la Renta page |
| 2 testing | not started (software phase W1, then datasets; no referee seen) |
| 3 proofs | done: 6 theorems, 3 #guard, 0 sorry |
| 4 known loopholes | catalogued 3, recreated 2 |
| 5 new loopholes | scanners run (results/search) + statute-visible notches proved |
| 6 gov errors | recorded in FINDINGS.md |
| 7 USEFUL.md | done |

Registry check: see the batch PROGRESS.md (registry corrections).

- 2026-11-20 W5 pattern A (contributions agent 2): personal IESS 9.45 % of wages when ecIessPersonal is not given; deducted (LRTI); now also reported as employeeSocial. Provision: IESS Resolución C.D. 515 (30 Mar 2016) Anexo Único, Primera (private-sector dependent workers 9,45 / 11,15 / 20,60), replacing C.D. 501; Ley de Seguridad Social (iess.gob.ec). Rebuilt (#guards pass), check `w5/pa/check.py EC` 0 / 300 differ with the switch off, rescanned (`scan_world.py EC`).
