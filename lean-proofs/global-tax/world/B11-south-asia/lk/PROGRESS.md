# Sri Lanka (LK) progress

**Status (2026-11-20T06:25Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md; SOFTWARE.md lists none for this country unless updated), then datasets.**

- Year: 2025/26 (year of assessment 1 April 2025 - 31 March 2026); access tier A; reused patterns: IN, UK.
- Statute read: Inland Revenue Act No. 24 of 2017 with Inland Revenue (Amendment) Acts No. 10 of 2021 (s. 55), 45 of 2022 (ss. 19, 33, 36), 4 of 2023 (s. 18), 14 of 2023, 2 of 2025 (ss. 3, 5; in operation 1 April 2025) and 11 of 2026 (parliament.lk 6420.pdf: Fifth Schedule and s. 52A from 1 April 2025; reliefs used unchanged), all from Global law (sri-lanka/national/acts/act/...; Parliament of Sri Lanka); EPF: epf.lk pages (official secondary) and the Cap. 623 Act copy on epf.lk.
- Registry correction: Registry: Inland Revenue Act 24/2017 confirmed; fiscal year April-March; 2025/26: 6 / 18 / 24 / 30 / 36 % at 1.0 / 1.5 / 2.0 / 2.5 m after personal relief 1.8 m (Act 2 of 2025); EPF employee 8 % (official secondary). Global law prints the 2017 schedules unamended ('as in force on 2025-10-01' shows the 2017 4-24 % table): the amending acts must be applied by hand.
- Lean: 112 lines, 14 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/lktax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS).
- Unsupported: terminal benefits (First Schedule para 1(2)(b)); foreign-currency service income at 15 % (para 1(6)); betting/liquor/tobacco income at 45 %; interest WHT treated as credit (included at normal rates).
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean) + #guard notches; 4-5: FINDINGS.md (catalogue, scanners, search record); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
