# Georgia (GE) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: EE, LV, LT, RU.
- Statute read: Tax Code of Georgia (2010) arts. 80, 81, 82, 130, 131 via Global law (georgia/national/acts/code/2010/3591, dated text 2025-07-01; art. 81 last changed by Law №134 in force 2025-01-01; official matsne.gov.ge/ka/document/view/4595604); Law on Funded Pensions №3303-რს art. 3 (Global law, in force 2024-07-12).
- Registry correction: Registry 'flat; funded pension 2 %' confirmed: 20 % flat (art. 81(1)), no personal allowance; employee 2 % funded-pension contribution exempt from the tax (art. 82(1)(b3)); dividends and non-bank interest 5 % final, bank interest exempt, residential rent 5 %.
- Lean: 107 lines, 13 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/getax` (worldMain).
- Unsupported (listed in the outputs): participation at ages 62-66 depends on sex; capital gains: 5 % dwellings/cars and holding-period exemptions; private pensions; rounding rule (art. 37) not read.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/art130_131_20250701.txt` (14,322 B, sha256 68e814f95dfe8f2c…)
  - `law/art80_82_20250701.txt` (76,591 B, sha256 ee1b8fde80585eb7…)
  - `law/gl_list.txt` (55,141 B, sha256 0f57ef8942529603…)
  - `law/pension_3_21_20250701.txt` (15,969 B, sha256 f5b6be71039f8cb6…)
  - `law/pension_list.txt` (7,619 B, sha256 0c2dcca663dc009c…)
