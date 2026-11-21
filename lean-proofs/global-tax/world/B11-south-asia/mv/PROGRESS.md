# Maldives (MV) progress

**Status (2026-11-20T06:25Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md; SOFTWARE.md lists none for this country unless updated), then datasets.**

- Year: 2025 (calendar tax year); access tier A; reused patterns: UK.
- Statute read: Income Tax Act (Law 25/2019) consolidated with the first amendment (Law 15/2021), in force 20 July 2021 - 31 August 2026 (mvlaw.gov.mv consolidation 1313, page data saved; Dhivehi) ss. 7, 12, 19, 54; Pension Act (Law 8/2009), 7 % paragraph (mvlaw legislation 113; Global law law-113).
- Registry correction: Registry: Income Tax Act 25/2019 confirmed (Global law holds it as law-294, Dhivehi, only the 2026 consolidation). Rates: 0 % to 720,000; 5.5 % to 1.2 m; 8 % to 1.8 m; 12 % to 2.4 m; 15 % above (unchanged by Law 11/2026); pension 7 % employee.
- Lean: 84 lines, 10 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/mvtax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS).
- Unsupported: capital gains; donation cap; expatriate pension coverage.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean) + #guard notches; 4-5: FINDINGS.md (catalogue, scanners, search record); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
