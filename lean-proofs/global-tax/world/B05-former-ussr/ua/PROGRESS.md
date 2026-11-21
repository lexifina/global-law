# Ukraine (UA) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: RU, EE, PL.
- Statute read: Tax Code 2755-VI, edition of 15.06.2025 (Internet Archive copy of zakon.rada.gov.ua, 2025-06-20) arts. 163-169, 167, 169 and Section XX subsection 10 item 16-1 (military levy, as restated by Law 4015-IX); Law 4059-IX on the State Budget 2025 arts. 7-8 (archived 2025-04-10); Law 2464-VI on the single contribution arts. 4, 8 (archived 2025-03-14).
- Registry correction: Registry 'flat; military levy' confirmed and dated: PIT 18 %, military levy 5 % from 1 December 2024 (Law 4015-IX) for the martial-law period; employees pay no single contribution (ESV 22 % is the employer's); the tax social benefit (1 514 a month) applies only if the month's wage is at most 4 240.
- Lean: 113 lines, 14 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/uatax` (worldMain).
- Unsupported (listed in the outputs): pensions; single-tax groups; deposit/property-sale rules; special benefits 150 %/200 %.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/budget2025_wb20250410.html` (265,929 B, sha256 69e0f8f6aa42195b…)
  - `law/budget2025_wb20250410.txt` (179,088 B, sha256 c71101497f91ce06…)
  - `law/esv_wb20250314122800.html` (729,144 B, sha256 006bc735fe889291…)
  - `law/esv_wb20250314122800.txt` (467,666 B, sha256 f7d123d2c63aa546…)
  - `law/ptk_wb20250620.txt` (6,929,226 B, sha256 9950e86de81a4993…)
  - `law/zrada_2755-17_wb20250620.dec.html` (9,776,375 B, sha256 4798a676aaefa89e…)
  - `law/zrada_2755-17_wb20250620.html` (1,326,942 B, sha256 c6b639ba9fb97c53…)
- 2026-11-20 W5 review: see FINDINGS W5-1.
