# MU progress

**2026-11-20T06:18Z: status built (access A); build phase done; next: software phase (SOFTWARE.md), then datasets.**

Year: 2025-26 (income year 1 July 2025 - 30 June 2026). Lean: 100 lines, 10 defs, 5 theorems, 1 #guard, 0 sorry. Sources in `law/` with sha256 where downloaded. Findings: FINDINGS.md.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): NSF employee 1 % of the basic wage up to Rs 18,740 a month, nil at or below Rs 3,000 (Government pays), not deducted. Provision: National Savings Fund Act 1995 s. 5 (2)-(3), First Schedule item 2 (c), s. 2 "basic wage or salary"; National Pensions Act 1976 Fifth Schedule (a) (18,740; GN 268 of 2021 w.e.f. 1 July 2019); ITA ss. 27D, 27DC (MRA consolidations). Rebuilt (#guards pass), check `w5/pa/check.py MU` 0 / 300 differ with the switch off, rescanned (`scan_world.py MU`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
