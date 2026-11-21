# Tajikistan (TJ) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: UZ, KZ.
- Statute read: Tax Code (2021) as amended to 14.05.2025, official PDFs of the Tax Committee (andoz.tj; Tajik text and the Committee's English text) arts. 183, 189, 191, 237, 238, 332; State Budget Law 2025 art. 23(1) (indicator 75 TJS, andoz.tj).
- Registry correction: Registry 'flat' confirmed with detail: 12 % at the main job above a personal deduction of 2 indicators (150 TJS) a month, 15 % on other income of individuals, social tax 2 % (1 % budget) deductible; dividends and interest 12 % final. Global law holds only the Constitution.
- Lean: 91 lines, 13 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tjtax` (worldMain).
- Unsupported (listed in the outputs): entrepreneur regimes and social tax; art. 191(8) non-cash spending deduction; secondary jobs.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/Kodex_14_05_2025_Nav_ENG_en.pdf` (1,935,847 B, sha256 8abfc05e3116aaf1…)
  - `law/Tax-Code__14_05_2025-RT_tj.pdf` (3,566,429 B, sha256 974c9ef16c812148…)
  - `law/budget2025_tj.pdf` (282,166 B, sha256 c4c7cbbda6ec6ded…)
  - `law/budget2025_tj.txt` (85,588 B, sha256 c56268d732880032…)
  - `law/tc_en_20250514.txt` (825,550 B, sha256 652dd029ce351bbd…)
  - `law/tc_tj_20250514.txt` (1,446,334 B, sha256 25a8f7dc83d3ff7b…)
