# Tanzania (TZ) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year of income); access tier A; reused patterns: UK/IE PAYE, KE (this batch).
- Statute read: Income Tax Act Cap. 332 R.E. 2023 (TRA 'Acts' page) ss. 20, 61, First Schedule para. 1; Finance Act 2024 (No. 6) s. 46 and Finance Act 2025 (No. 11) s. 60 (First Schedule paras. 2 and 4 only); NSSF Act Cap. 50 R.E. 2023 (nssf.go.tz) First Schedule and definitions
- Registry correction: Registry 'Income Tax Act (Cap. 332)' confirmed: calendar year; resident 0/8/20/25/30 % (3.24 M / 6.24 M / 9.12 M / 12 M) on total income after retirement contributions (s. 61); NSSF employee 10 % of wages without ceiling; Mainland only (Zanzibar rate set separately, para. 1(7)).
- Lean: 90 lines, 6 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tztax` (worldMain).
- Unsupported (listed in the outputs): Zanzibar; PSSSF (public servants); investment, rental, business income and gains.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: TanzLII corpus holds Finance Acts 2015-2023 and 2026 but not the 2024/2025 Finance Acts or the ITA
  - tanzlii.org act pages 403 to scripts (archive only had the 2019 version)
  - tra.go.tz resource-center/8 (ITA R.E. 2023, Finance Acts 2024-2026) and nssf.go.tz/publications/act
  - not opened (referee values): TRA PAYE tables
- Files on disk:
  - `law/Finance_Act_2024_1.pdf` (440,473 B, sha256 bd5951f198eafa40…)
  - `law/THE_FINANCE_ACT_2025.pdf` (511,401 B, sha256 a294f4b5bfb17bc5…)
  - `law/THE_FINANCE_ACT_2026.pdf` (844,978 B, sha256 ea7ad0181a36a7d2…)
  - `law/The_Income_Tax_Act.pdf` (1,256,766 B, sha256 a128d3293c3d9c5c…)
  - `law/nssf_cap50_re2023.pdf` (773,203 B, sha256 2a820e67ed109cd3…)
