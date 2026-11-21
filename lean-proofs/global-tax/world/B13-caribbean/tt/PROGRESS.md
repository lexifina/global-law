# Trinidad and Tobago (TT) progress

**Status (2026-11-20T07:27Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year of income); access tier A; reused patterns: UK/IE PAYE (annual personal allowance, two rates), B15 AG/KN (weekly social-security classes).
- Statute read: Income Tax Act Chap. 75:01 (Global law: laws.gov.tt consolidation 2025-06-03; notes to Act No. 15 of 2024): ss. 8(1)(k), 17, 18, 27(1)(d), 28(15), 31(1)(c), 48, 79, Third Schedule Parts I and II; Health Surcharge Act Chap. 75:05 (consolidation 2023-10-24) s. 3(1)-(4); National Insurance Act Chap. 32:01 (laws.gov.tt PDF of 2025-01-08) ss. 20(2)(a)(iv), 20(3)(d), 38(1), 41(1)-(2)(i), Second Schedule Table A9
- Registry correction: Registry 'Income Tax Act (Chap. 75:01); NIS, health surcharge' confirmed: personal allowance 90,000 (s. 18); 25 % to 1,000,000 of chargeable income, 30 % above; 70 % of NIS contributions deductible within a 60,000 cap (ss. 28(15), 31(1)(c)); health surcharge 8.25/4.80 a week; NIS employee one third of 13.2 % by weekly class (Table A9, unchanged since 5 Sep 2016 in the 2025 consolidation).
- Lean: 152 lines, 11 defs, 5 theorems, 16 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tttax` (worldMain).
- Unsupported (listed in the outputs): investment, rental and business income (withholding Third Schedule Part II); approved pension contributions (s. 28); self-employed NIS; wages assumed paid evenly over 52 weeks.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law trinidad-and-tobago corpus (ITA 75:01, 75:05, 32:01 and its subsidiary legislation)
  - laws.gov.tt revision download 118843 (NIS Act consolidation, 2025-01-08): Global law's text of Table A9 had merged it with Table A8; the PDF was read
  - not opened (referee values): BIR PAYE tables and calculators
- Files on disk:
  - `law/nis_32-01_118843.pdf` (3,309,064 B, sha256 55a3b1a32cc68037…)
