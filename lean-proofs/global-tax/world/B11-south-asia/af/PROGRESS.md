# Afghanistan (AF) progress

**Status (2026-11-20T06:25Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md; SOFTWARE.md lists none for this country unless updated), then datasets.**

- Year: 2025 (last accessible statute; de facto status unverified); access tier B; reused patterns: PK.
- Statute read: Income Tax Law 2009 (Official Gazette 976) consolidated to OG 1209 (13 April 2016), Afghanistan Revenue Department English translation ('unofficial'), Internet Archive copy (2018-12-22) of ard.gov.af: Art. 4 (3), Art. 17 (2). Authority: the Islamic Republic's statute; the de facto authorities' texts were not reachable (ard.gov.af PHP fatal error, moj.gov.af no connection, mof.gov.af without legislation pages; Global law: only the 2004 Constitution)..
- Registry correction: Registry: 'Income Tax Law 2009; de facto authorities' -> the model states the last accessible statute (2016 consolidation); whether the de facto authorities apply it unchanged in 2025 is not verified. Monthly schedule 0 / 2 / 10 / 20 % at 5,000 / 12,500 / 100,000 Afs.
- Lean: 70 lines, 7 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/aftax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS).
- Unsupported: 2025 status under the de facto authorities; rent, interest, dividends, pensions; social contributions.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean) + #guard notches; 4-5: FINDINGS.md (catalogue, scanners, search record); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
