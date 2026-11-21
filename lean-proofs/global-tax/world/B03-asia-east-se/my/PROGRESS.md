# Malaysia (MY) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (Year of Assessment 2025); access tier B; reused patterns: UK, AU.
- Statute read: IRBM (LHDN) published tables: 'Tax Rate' YA 2023-2025 (Schedule 1), 'Tax Relief' YA 2025, 'Rebates' (s. 6A); the Income Tax Act 1967 is not in Global law and the Laws of Malaysia portal serves encrypted JSON behind signed tokens (not bypassed).
- Registry correction: Unit: separate assessment with optional joint assessment (s. 45); reliefs 9,000 / spouse 4,000 / child 2,000; RM400 rebate (x2 when the spouse has no income) for chargeable income up to RM35,000.
- Lean: 95 lines, 10 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/mytax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS where files were saved).
- Unsupported: EPF, SOCSO, EIS contributions and their reliefs (kwsp.gov.my 403, perkeso.gov.my timeout); interest/dividends (Schedule 6, dividend tax); capital gains; pensions.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py + b03scan); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent 2): EPF 11 % (Third Schedule bands, rounded up; nil from 60), SOCSO first category (0.5 % of the band mid-wage, ceiling RM6,000; under 60) and EIS (0.2 %, ceiling RM6,000; 18-59); reliefs EPF up to 4,000 and SOCSO+EIS up to 350. Provision: EPF Act 1991 Third Schedule Parts A, E (KWSP copy 2022); Employees Social Security Act 1969 Third Schedule para 2 (as at 1 Sep 2022) and Act A1724 (2024) s. 3; EIS Act 2017 Second Schedule and Act A1725 (2024) s. 3; LHDN YA 2025 reliefs 17, 20. Rebuilt (#guards pass), check `w5/pa/check.py MY` 0 / 300 differ with the switch off, rescanned (`scan_world.py MY`).
