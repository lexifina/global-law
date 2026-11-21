# SZ progress

**2026-11-20T06:18Z: status built (access B); build phase done; next: software phase (SOFTWARE.md), then datasets.**

Year: 2025/26 (year of assessment 1 July 2025 - 30 June 2026). Lean: 83 lines, 7 defs, 5 theorems, 2 #guard, 0 sorry. Sources in `law/` with sha256 where downloaded. Findings: FINDINGS.md.

- 2026-11-20 W5 pattern A (contributions agent): ENPF employee 5 % of wages up to E4,000 / month (2025) and E4,300 (2026); deducted (s. 14 (1) (i)). Provision: ENPF (Statutory Contributions) Regulations 2025 (LN 5/2025) reg. 2 (1) (a)-(b), as reproduced by the Fund; rate 5 % + 5 % (Fund notice); Income Tax Order s. 2 "pension fund", s. 14 (1) (i), Fourth Schedule para 2 (4). Rebuilt (#guards pass), check `w5/pa/check.py SZ` 0 / 300 differ with the switch off, rescanned (`scan_world.py SZ`).

- 2026-11-20 D9 review: ENPF caps applied per month (LN 5/2025 reg. 2 (1)-(2)): `enpfMonthly`, input `"szEnpfAnnualCap": true` restores the annual cap; #guards pass; check4 0 / 300 differ with the input; rescanned. FINDINGS D9R-1; world/IMPROVE_D9.md.
