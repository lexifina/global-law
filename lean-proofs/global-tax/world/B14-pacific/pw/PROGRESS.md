# Palau (PW) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year); access tier A; reused patterns: US-style wage tax (Compact states).
- Statute read: RPPL No. 11-11 (Palau Tax Reform Act, palaugov.pw) ss 5 (40 PNC 1101, 1104), 6 (1106), 21 (effective 1 January 2023); Palau National Code Title 40 (2018 consolidation, palaugov.pw)
- Registry correction: Registry 'Palau National Code title 40 (income tax; 2023 reform)': the 2023 reform kept a wage and salary tax (no general income tax for individuals): 6 % on the first $8,000, 10 % to $40,000, 12 % above, on all wages; citizens earning $15,000 or less get the whole tax refunded (40 PNC 1104); businesses pay the new Business Profits Tax and PGST.
- Lean: 90 lines, 6 defs, 5 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/pwtax` (worldMain).
- Unsupported (listed in the outputs): social security (41 PNC) and Civil Service Pension Plan contributions (not reached); Business Profits Tax; tuition/donation refunds.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: palau corpus (Palau Code Commission) holds the Constitution and Titles 1 and 17 only
  - palaugov.pw Bureau of Revenue and Taxation pages: RPPL 11-11 and Title 40 PDFs (the withholding table on the same page was not opened: referee material)
- Files on disk:
  - `law/Palau-National-Code-Title-40.pdf` (521,009 B, sha256 9cd0a9670086a275…)
  - `law/RPPL-11-11.pdf` (55,468,051 B, sha256 5b3c4ab5d16a4309…)
- 2026-11-20 round D6: § 1101 bands (RPPL 11-11) confirmed for 2025; no change; withholding-table gap left to the test agent.
