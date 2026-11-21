# Uganda (UG) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2024/25 (year of income 1 July 2024 - 30 June 2025); access tier A; reused patterns: UK/IE PAYE, KE (this batch).
- Statute read: Income Tax Act, ULII version 2024-12-23 (Revised Edition; Internet Archive capture 2025-10-20; ULII answers scripts 403): s. 2 ('year of income'), s. 6, Schedule 4 Part I and II; Income Tax (Amendment) Act 2024 (Parliament of Uganda cmis PDF); NSSF Act (ULII version 2022-01-07) ss. 11, 12; Local Governments Act s. 83 (Global law)
- Registry correction: Registry 'Income Tax Act (Cap. 340); NSSF' corrected: the Revised Edition in force 2024-12-23 renumbers the rates as Schedule 4 (Part I individuals); year of income ends 30 June; resident rates 0/10/20/30 % (2.82 M / 4.02 M / 4.92 M) plus an additional 10 % above 120 M; NSSF employee 5 % of total wages, no ceiling, not deductible; local service tax under the Local Governments Act (rates not in the consolidated Act).
- Lean: 92 lines, 7 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/ugtax` (worldMain).
- Unsupported (listed in the outputs): local service tax (rates not reached); Income Tax (Amendment) Act 2025 (if any) not reached: 2024/25 modelled; investment, rental and business income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: Uganda corpus (32 acts, ULII) lacks the Income Tax Act; Local Governments Act s. 83 found
  - ULII act pages answer 403 to scripts: Internet Archive copies; ULII legislation listings (work) for 2024/2025 show no income tax amendment
  - ura.go.ug 'Laws, Acts & Regulations' (no 2024/2025 income tax act listed); parliament.go.ug Acts 2024 (cmis PDF read)
  - not opened (referee values): URA PAYE calculators
- Files on disk:
  - `law/ita_2024-12-23.html` (1,593,093 B, sha256 6c32f938c0a3077f…)
  - `law/ita_amend_2024.pdf` (395,909 B, sha256 8f608b64aa7a2fc9…)
  - `law/nssf_2022-01-07.html` (1,226,020 B, sha256 ad43bfd30efc43c4…)
