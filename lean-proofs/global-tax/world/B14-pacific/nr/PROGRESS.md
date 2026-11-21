# Nauru (NR) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (pay periods in calendar 2025); access tier A; reused patterns: B08 DJ / B10 RW (final per-period withholding).
- Statute read: Employment and Services Tax Act 2014 ss 2, 5, 7, 11, 12, 13, 14, 17 and Schedule (SL 3 of 2021 as amended by SL 3 of 2023, opn 1 July 2022); Naoero Superannuation Act 2018 ss 23, 26, 28, Schedule 1 (Global law, RONLAW consolidation, record to 2026-10-08); Nauru Superannuation (Amendment) Act 2025 (No. 49 of 2025, ronlaw.gov.nr) ss 2, 6
- Registry correction: Registry 'Employment and Services Tax Act 2014; tax on employment income since 2014' confirmed, but the tax is not progressive: a final tax per pay period of 20 % above $9,240 a month ($4,257 a fortnight, $2,129 a week) for residents (citizens, refugees, spouses of citizens), 20 % flat for other non-residents (30 % Regional Processing Centre; 0 % on the first $20,000 a year for expatriates of the Republic or a State-owned enterprise); no tax on investment income under this Act; superannuation 5 % employee (employer 5 % in 2025, 10 % from 1 February 2026).
- Lean: 111 lines, 15 defs, 2 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/nrtax` (worldMain).
- Unsupported (listed in the outputs): services tax on self-employment fees and the Business Tax Act 2016; investment income (outside the Act); wages paid evenly in equal pay periods.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: nauru/national/acts (RONLAW; current text with dated history notes): ESTA 2014, Naoero Superannuation Act 2018, Revenue Administration Act 2014
  - ronlaw.gov.nr: Angular bundle gives the API base https://ronlaw.gov.nr/api/pdf/ (latest/<year>/any/<category>/any/50 lists documents; files under /assets/docs/...): Nauru Superannuation (Amendment) Act 2025 fetched
- Files on disk:
  - `law/nsa_amend_2025.pdf` (151,226 B, sha256 898041de1c385e29…)
