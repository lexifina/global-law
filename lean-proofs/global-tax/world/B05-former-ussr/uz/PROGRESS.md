# Uzbekistan (UZ) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: KZ, TJ.
- Statute read: Tax Code of 30.12.2019, official Russian text on lex.uz, version in force on 01.01.2025 (ONDATE) arts. 369, 378, 381 and the funded-pension credit.
- Registry correction: Registry 'flat' confirmed: 12 % (art. 381), dividends and interest 5 %, bank-deposit interest exempt; the employee's funded-pension contribution is credited against the tax (total burden 12 %); no personal allowance.
- Lean: 72 lines, 7 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/uztax` (worldMain).
- Unsupported (listed in the outputs): entrepreneur regimes; later 2025 versions not compared.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/a378_2025.txt` (21,524 B, sha256 b0093abcb20f5ca6…)
  - `law/lex_4674893_ru.html` (6,749,293 B, sha256 0917345608fffc89…)
  - `law/lex_tc_ru_current.txt` (3,621,344 B, sha256 4f8075fc09b50b9e…)
  - `law/lex_tc_ru_on20250101.html` (6,429,871 B, sha256 1cee7c4fbadc3f05…)
  - `law/lex_tc_ru_on20250101.txt` (2,512,140 B, sha256 8fd26fe9b0b90884…)
