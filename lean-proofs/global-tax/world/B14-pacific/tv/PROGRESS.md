# Tuvalu (TV) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year); access tier A; reused patterns: AU/NZ PAYE (tax-free threshold).
- Statute read: Income Tax Act (Cap. 26.16, 2022 Revised Edition) s 15(1)(a), Schedule 6 (endnote 26); Income Tax Regulations (Cap. 26.16.1) reg 4; Provident Fund (Contributions) Regulations (Cap. 32.08.4) Schedule 1 (tuvalu-legislation.tv; point-in-time list 2025-07-01)
- Registry correction: Registry 'Income Tax Act' confirmed (Cap. 26.16, 2022 Revised Edition, no later version in force in 2025): 0 % to 10,000, 15 % to 14,000, 30 % above; Provident Fund employee 13 % (employer 10 %), deductible as an approved-fund contribution; currency AUD.
- Lean: 105 lines, 9 defs, 5 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tvtax` (worldMain).
- Unsupported (listed in the outputs): withholding on interest and dividends; presumptive business tax; approved-fund status of the Provident Fund assumed.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: Tuvalu corpus empty (paused: the publisher's copyright notice forbids redistribution); the model quotes only short phrases
  - tuvalu-legislation.tv (Attorney-General): point-in-time POST lists (pointintime=2025-07-01) and the 2022 Revised Edition PDFs
- Files on disk:
  - `law/1984-0005_2.pdf` (330,931 B, sha256 067d4ee882701bc0…)
  - `law/1985-0016_2.pdf` (206,084 B, sha256 4ee8a1ac68d8aa39…)
  - `law/1992-0005_2.pdf` (873,876 B, sha256 77bc3b29ff62c61e…)
  - `law/2021-0125_1.pdf` (154,643 B, sha256 19ef173f77bf7037…)
  - `law/b14tv_I.html` (94,975 B, sha256 bfafd050e0ebf67c…)
  - `law/b14tv_P.html` (391,984 B, sha256 82ac6e0c08035ecd…)
