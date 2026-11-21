# Jamaica (JM) progress

**Status (2026-11-20T07:27Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (year of assessment); access tier B; reused patterns: UK/IE PAYE.
- Statute read: Income Tax Act (MOJ consolidation, Internet Archive copy of 2025-02-04; older scanned edition); amounts from Tax Administration Jamaica 'Payroll Taxes and Statutory Contributions' (2025-04-29) pp. 1-2 and 'Individual Income Tax Rates, Threshold and Exemptions 2013-2028' (official secondary)
- Registry correction: Registry 'Income Tax Act; NIS, NHT, education tax' confirmed (from TAJ tables): YA 2025 effective threshold 1,774,554 (1,700,088 Jan-Mar, 1,799,376 Apr-Dec); 25 % to 6 M of statutory income, 30 % above; NIS 3 % to 5 M; NHT 2 %; Education Tax 2.25 % of statutory income.
- Lean: 100 lines, 9 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/jmtax` (worldMain).
- Unsupported (listed in the outputs): Act's current wording not reached (TAJ tables); age limits for NIS/NHT/Education Tax; approved pension contributions; investment income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law jamaica corpus (metadata only)
  - laws.moj.gov.jm (503 from lean1 and the laptop); Internet Archive copy of the ITA PDF (laptop; the Archive later refused both hosts)
  - japarliament.gov.jm (403)
  - jamaicatax.gov.jm rates pages and PDFs (pp. 1-2 of the payroll guide only)
- Files on disk:
  - `law/ITA_moj_wayback_20250204.pdf` (26,994,379 B, sha256 3e6a4453dc524c52…)
  - `law/TAJ_INDIVIDUAL_INCOME_TAX_RATES_THRESHOLD_AND_EXEMPTIONS_2013-2028.pdf` (272,621 B, sha256 b687e8d2978276a6…)
  - `law/TAJ_Payroll_Taxes_and_Statutory_Contributions_Employee_Employer.pdf` (860,716 B, sha256 1e04fdae83aea4c7…)
  - `law/moj.html` (107,941 B, sha256 2d08400e97310e93…)
  - `law/moj_s.html` (107,941 B, sha256 2d08400e97310e93…)
