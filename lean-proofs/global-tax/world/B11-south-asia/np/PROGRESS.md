# Nepal (NP) progress

**Status (2026-11-20T06:25Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md; SOFTWARE.md lists none for this country unless updated), then datasets.**

- Year: 2081/82 (16 July 2024 - 16 July 2025; same provisions in 2082/83); access tier A; reused patterns: IN, UK.
- Statute read: Income Tax Act 2058 consolidated with the amendments up to the Finance Act 2082 (Government of Nepal CDN, Internet Archive copy 2026-04-20; Schedule 1 para 1 (1), (2), (9क), (11); ss. 12, 50, 63, 88 (2)-(3), 92 (1)); Income Tax Rules 2059 r. 21 (consolidation to 2079, Internet Archive).
- Registry correction: Registry: Income Tax Act 2058 confirmed; Global law holds only the 2018 Law Commission compilation (outdated). Rates: 1 % (social security tax, employment income only) to 5 lakh, 10 / 20 / 30 % to 7 / 10 / 20 lakh, 36 % to 50 lakh, 39 % above; couple election (s. 50) with 6 / 8 / 11 lakh; women with only remuneration 10 % rebate; interest 6 % and dividends 5 % final.
- Lean: 156 lines, 17 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/nptax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS).
- Unsupported: rental income of non-business persons (local house-rent tax); gains on non-business assets; SSF contributions (11 %); pension deduction cap 'as prescribed' not located.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean) + #guard notches; 4-5: FINDINGS.md (catalogue, scanners, search record); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
