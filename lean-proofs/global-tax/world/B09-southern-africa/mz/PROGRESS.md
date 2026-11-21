# MZ progress

**2026-11-20T06:18Z: status built (access B); build phase done; next: software phase (SOFTWARE.md), then datasets.**

Year: 2025. Lean: 121 lines, 9 defs, 5 theorems, 4 #guard, 0 sorry. Sources in `law/` with sha256 where downloaded. Findings: FINDINGS.md.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): INSS worker 3 % of remuneration (no ceiling), reported, not deducted (AT FAQ: no deduction for 1st-category income, CIRPS art. 29). Provision: INSS page "Taxa contributiva TCO" (inss.gov.mz, fetched 2026-11-20): worker 3 % + employer 4 % = 7 %; official secondary; RSSO (Decreto 51/2017, republished by Decreto 56/2024 de 30 de Julho) arts. 14-15; AT "As 100 questões ... sobre o CIRPS" (2015) q. 25. Rebuilt (#guards pass), check `w5/pa/check.py MZ` 0 / 300 differ with the switch off, rescanned (`scan_world.py MZ`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
