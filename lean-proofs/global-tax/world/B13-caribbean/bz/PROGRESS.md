# Belize (BZ) progress

**Status (2026-11-20T07:27Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (basis year); access tier A; reused patterns: UK/IE PAYE (basic deduction), TT (this batch: weekly class table).
- Statute read: Income and Business Tax Act Cap. 55 (Laws of Belize Rev. Ed. 2020, Global law) ss. 8(1)(m), 16(5), 19(1),(3); Income and Business Tax (Amendment) Act 2024 (No. 40 of 2024, Global law, in force 1 January 2025) ss. 3 (new s. 6), 4 (new s. 16(1)-(3)), 5 (s. 20 repealed), 34; Income and Business Tax (Amendment) Act 2021 (No. 12) read; Social Security (Collection of Contributions) Regulations reg. 6 and Schedule Tables 1-3 (agm.gov.bz PDF); Social Security (Amendment) Act 2024 (No. 1 of 2025) read
- Registry correction: Registry 'Income and Business Tax Act (Cap. 55)' confirmed and updated: from 1 January 2025 (Act 40 of 2024) employed persons pay 25 % on total income less a 20,000 basic deduction once total income exceeds 29,000, with a phase-in credit of 2,250 - 75 % x (income - 29,000) up to 32,000; no income tax on other persons' chargeable income (business tax instead); Social Security Table 2 (from 6 Jan 2020) weekly contributions, insurable earnings capped at $480 a week.
- Lean: 123 lines, 12 defs, 4 theorems, 9 #guard checks, 0 sorry; exe `lean/.lake/build/bin/bztax` (worldMain).
- Unsupported (listed in the outputs): business tax on receipts (self-employed, Part XI); dividends, rents and gains; Social Security Table 3 (period not declared in any notice found); wages assumed paid evenly over 52 weeks.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law belize corpus (Rev. Ed. 2020 + Acts 2021-2026 as enacted)
  - agm.gov.bz Cap. 44 subsidiary PDF (Social Security)
  - not opened (referee values): Belize Tax Service calculators
- Files on disk:
  - `law/CAP_044s_Social_Security_Act.pdf` (2,130,245 B, sha256 a0f738e03c9bf4fc…)
