# Marshall Islands (MH) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year; two schedules); access tier A; reused patterns: US-style wage tax + social security (Compact states), B05 mid-year change pattern (month-weighted schedules).
- Statute read: Income Tax Act 1989 (48 MIRC Ch. 1) consolidation _5 (rmiparliament.org) ss 103-105, 109, 116; Income Tax (Amendment) Act 2024 (P.L. 2024-14, certified 8 October 2024) and Income Tax (Amendment) Act 2025 (P.L. 2025-34, effective 1 October 2025): scans, OCR checked on the page images; Social Security Act of 1990 (49 MIRC Ch. 1) consolidation _6 ss 102(k), 129, 130, 132; Minimum Wage Act 1986 as amended by P.L. 2024-13
- Registry correction: Registry 'Income Tax Act 1989 (wages and salary tax)' confirmed and dated: in 2025 the wage tax changed twice: 8 %/12 %/16 % ($15,600/$26,000 a year, prorated per pay period) from P.L. 2024-14, back to 8 % on the first $10,400 and 12 % above from 1 October 2025 (P.L. 2025-34); all-or-nothing exemption at $8,320 a year ($693.33 a month); 5 % for US contractor personnel; social security 8 % employee on covered earnings.
- Lean: 126 lines, 14 defs, 6 theorems, 7 #guard checks, 0 sorry; exe `lean/.lake/build/bin/mhtax` (worldMain).
- Unsupported (listed in the outputs): gross revenue tax and Net Profit Act 2025 for self-employment; tax on income from immovable property (s 116); wages paid monthly and evenly.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: marshall-islands corpus is catalogue-only (no law text)
  - rmiparliament.org (Nitijela): by-title list, acts-by-year form (POST year), consolidations and amending-act scans; OCR with tesseract eng, numbers checked on the page images
- Files on disk:
  - `law/1986-0015_4.pdf` (578,100 B, sha256 ad6ada8afd0c1ba4…)
  - `law/1989-0050_5.pdf` (585,460 B, sha256 0d49edecc6597083…)
  - `law/1990-0075_6.pdf` (907,106 B, sha256 1c327a25f0fbdba8…)
  - `law/2024-0013A.pdf` (149,053 B, sha256 ce4c907c389ac962…)
  - `law/2024-0014A.pdf` (136,268 B, sha256 6c5d9b8bb022d0f3…)
  - `law/2025-0034A.pdf` (104,266 B, sha256 68018ba44c54d643…)
  - `law/2025-0038A_1.pdf` (608,342 B, sha256 3f0007ea4fc2cc23…)
  - `law/bytitle.html` (1,515,246 B, sha256 723f88798f925dc8…)
  - `law/byyear.html` (67,794 B, sha256 1360835f99fe0b51…)
  - `law/y2024.html` (63,136 B, sha256 e8815d5d5bdfadb9…)
  - `law/y2025.html` (119,806 B, sha256 5855095e9e6317d2…)
