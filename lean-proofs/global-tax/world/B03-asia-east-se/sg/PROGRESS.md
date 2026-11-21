# Singapore (SG) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (Year of Assessment 2026); access tier B; reused patterns: AU, NZ, UK.
- Statute read: IRAS published tables (resident rates from YA 2024; reliefs: EIR, CPF relief, spouse, QCR, relief cap $80,000; no YA 2026 rebate listed) and the CPF Board's 2026 contribution-rate table (method, ages 55 and below); the Income Tax Act 1947 and CPF Act on Singapore Statutes Online answer 403 to scripts and the archived copies were offline during the build.
- Registry correction: Unit: separate assessment; resident progressive rates 0-24 % (from YA 2024) with personal reliefs capped at $80,000; CPF employee 20 % (55 and below) on ordinary wages up to $7,400 a month in 2025.
- Lean: 120 lines, 13 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/sgtax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS where files were saved).
- Unsupported: CPF rates above age 55 in 2025; WMCR; pensions; gains of a trading nature; self-employed MediSave.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py + b03scan); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
