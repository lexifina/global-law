# Liberia (LR) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar tax year); access tier A; reused patterns: UK/IE PAYE.
- Statute read: Liberia Revenue Code (Revenue Code of 2000) as amended, LRA consolidation 2020, ss. 200(a)(3)(A), 205(a); Tax Amendment Act of 2024 (chapters 8 and 10); Tax Amendment Act of December 2024 (ss. 602, 702, 741, withholding, excise); Act amending ss. 1003 and 1066(a) (VAT); Tax Amendment Act of December 2025 (excise; 2026)
- Registry correction: Registry 'Liberia Revenue Code 2000 as amended' confirmed: resident natural persons 0/5/15/25 % in Liberian dollars (70,000 / 200,000 / 800,000), the standard deduction being the zero bracket (s. 205(a)).
- Lean: 73 lines, 5 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/lrtax` (worldMain).
- Unsupported (listed in the outputs): NASSCORP contribution (input, reported only); US-dollar wages must be converted by the user; investment and business income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: LiberLII corpus (5 acts) has no tax law; liberlii.org 403
  - lra.gov.lr Domestic Tax Laws & Regulations and Laws and Amendments pages
  - nasscorp.org.lr reachable but the decree was not located
- Files on disk:
  - `law/ANACTT1.pdf` (1,512,914 B, sha256 b63e53e7c77d9a70…)
  - `law/LRC-Amendment-December-2025.pdf` (2,819,192 B, sha256 6d498c8d05fa33a8…)
  - `law/REVENUE-CODE-LIBERIA-REVENUE-CODE-AMENDEMENT-2020-min.pdf` (1,151,092 B, sha256 b96f4d43bca76d72…)
  - `law/TAX-AMENDMENT-ACT-OF-2024-AMENDING-CERTAIN-PORTIONS-OF-CHAPTERS-8-AND-10-OF-THE-LIBERIA-CONSOLIDATED-REVENUE-CODE-AS-AMENDED.pdf` (1,507,776 B, sha256 4ee7dea9c9e4bf92…)
  - `law/TAX-AMENDMENT-ACT-OF-DECEMBER-2024-AMENDING-THE-LIBERIA-CONSOLIDATED-REVENUE-CODE-AS-AMENDED.pdf` (3,435,693 B, sha256 c6c0733e0db6d185…)
