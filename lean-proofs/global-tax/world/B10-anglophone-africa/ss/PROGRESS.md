# South Sudan (SS) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2024/25 (tax year 1 July 2024 - 30 June 2025; national government); access tier A; reused patterns: DJ (B08: monthly brackets), UK/IE PAYE.
- Statute read: Financial Act 2024/2025 (NRA upload, Internet Archive capture 2025-04-01, scan, OCR) ss. 3, 4, 5, 6; Financial Act 2023/2024 (text layer) s. 4; Transitional Constitution 2011 arts. 177(b), 179(d) (Global law)
- Registry correction: Registry 'Taxation Act 2009 as amended' confirmed and completed: each year's Financial Act replaces Schedule 1 of the Taxation Act 2009; FY 2024/25 monthly brackets 0/5/10/15/20 % (20,000 / 40,000 / 57,000 / 90,000 SSP); states also levy a personal income tax (Constitution art. 179(d)).
- Lean: 99 lines, 7 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/sstax` (worldMain).
- Unsupported (listed in the outputs): Financial Act 2025/26 not reached; state personal income tax; rental and business income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: South Sudan corpus (constitution, penal and procedure codes)
  - nra.gov.ss (Vue application) -> cms.nra.gov.ss uploads (502); Internet Archive CDX of cms.nra.gov.ss/uploads
  - mojca.gov.ss unreachable; archived 'Personal-Income-Tax-Act-1-of-2007' listed (superseded by the Taxation Act 2009)
- Files on disk:
  - `law/financial_act_2023_2024.pdf` (3,840,633 B, sha256 ded23b09e0f50734…)
  - `law/financial_act_2024_2025.pdf` (68,289,536 B, sha256 f63a972f2293ee08…)
  - `law/taxation_act_2016.pdf` (1,595,659 B, sha256 48585d592762d37f…)
