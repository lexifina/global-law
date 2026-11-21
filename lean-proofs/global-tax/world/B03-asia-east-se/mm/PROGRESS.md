# Myanmar (MM) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: FY 2025-26 (1 April 2025 - 31 March 2026); access tier B; reused patterns: IN.
- Statute read: Internal Revenue Department page on individuals (ird.gov.mm), citing the Union Tax Law 2025 ss. 14, 15, 19, 24, 25, 27, 28 and the Income Tax Law s. 6 reliefs; the statutes themselves were not reached (Global law holds 4 Myanmar acts; mlis.gov.mm did not answer).
- Registry correction: Rates are in the yearly Union Tax Law (2025: s. 19 (c) bands 0/5/10/15/20/25 % on salary less reliefs) with an all-or-nothing exemption of salary up to 4,800,000 kyat (s. 19 (a)).
- Lean: 89 lines, 9 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/mmtax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS where files were saved).
- Unsupported: social security contributions; rent, capital gains, interest/dividends, self-employment, pensions.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py + b03scan); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
- 2026-11-20 W5 review: see FINDINGS W5-1.
