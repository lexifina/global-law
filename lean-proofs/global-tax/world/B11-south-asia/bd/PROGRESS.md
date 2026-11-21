# Bangladesh (BD) progress

**Status (2026-11-20T06:25Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md; SOFTWARE.md lists none for this country unless updated), then datasets.**

- Year: 2025-26 (income year 1 July 2025 - 30 June 2026; assessment year 2026-27); access tier A; reused patterns: IN, PK.
- Statute read: Finance Ordinance 2025 (Ordinance No. 28 of 2025, Bangladesh Gazette Extraordinary 2 June 2025; bdlaws upload via Internet Archive; Bengali OCR with tessdata_best ben, numbers checked on page images pp. 102, 105) s. 136, Schedule 2 Parts 1-2, s. 130 (7); Income Tax Act 2023 (Act 12 of 2023) ss. 32, 78, 331 (archived bdlaws HTML); NBR Income tax circular (Paripatra) 2025-26 (official secondary, consistent).
- Registry correction: Registry: Income Tax Act 2023 confirmed (Bengali only; Global law's English corpus does not hold it); the year's rates are in the Finance Ordinance 2025 (no parliament: ordinance), Schedule 2 for AY 2026-27: nil 375,000 / 10 % 300,000 / 15 % 400,000 / 20 % 500,000 / 25 % 2,000,000 / 30 %; higher exempt limits (425,000 women and 65+; 500,000; 525,000); minimum tax 5,000; salary exemption min(1/3, 500,000).
- Lean: 140 lines, 13 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/bdtax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS).
- Unsupported: withholding as minimum tax on interest/dividends (s. 163 (2)); house-property allowances and capital-gains rates; s. 78 eligible-investment limits (Sixth Schedule Part 3); environmental surcharge; no employee social contribution located.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean) + #guard notches; 4-5: FINDINGS.md (catalogue, scanners, search record); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
