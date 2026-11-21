# Kyrgyzstan (KG) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: KZ, RU.
- Statute read: Tax Code of 18.01.2022 No. 3, official editions of 12.02.2025 and 29.10.2025 from cbd.minjust.gov.kg (GetEdition 27071, 44293; same words in arts. 187, 191, 194, 197) and Global law's current text; Law No. 136 of 23.07.2024 art. 7 (social insurance tariffs; Global law), in force 2024-08-01.
- Registry correction: Registry 'flat' confirmed: 10 % (art. 197(1)), social contributions 10 % deductible; but two amounts sit outside the Code and were not reached: the расчетный показатель (personal deduction 6.5 RP/month, dependants 1 RP) and the district average monthly wage used as a minimum tax base (art. 187(2)).
- Lean: 95 lines, 9 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/kgtax` (worldMain).
- Unsupported (listed in the outputs): personal and dependant deductions (RP value not reached); art. 187(2) district average wage (not reached); special regimes.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/a191_201_ed27071.txt` (7,152 B, sha256 d5f3b2873a70675b…)
  - `law/art187_198_current.txt` (19,911 B, sha256 f1aaba883a88d4c0…)
  - `law/ed57656.json` (2,948,726 B, sha256 a1ff24ecdcbc9eac…)
  - `law/gl_list.txt` (80,199 B, sha256 04a0f68a6e6a5a55…)
  - `law/kg_tc_ed13809.txt` (1,356,090 B, sha256 5f7adbefca840ac3…)
  - `law/kg_tc_ed27071.txt` (1,448,079 B, sha256 bcafece4ed892aa7…)
  - `law/kg_tc_ed34825.txt` (1,451,269 B, sha256 79a9a7ac2d9e38fd…)
  - `law/kg_tc_ed36891.txt` (1,455,396 B, sha256 fe1c3c39a4fbec74…)
  - `law/kg_tc_ed44293.txt` (1,507,070 B, sha256 1efbaea75e40dd0e…)
  - `law/kg_tc_ed45757.txt` (1,519,479 B, sha256 fd479e2d8f6b17b0…)
  - `law/s_amend.txt` (19,103 B, sha256 ccf6a63138aceffb…)
  - `law/s_tariff.txt` (34,420 B, sha256 392d36801e220f22…)
  - `law/z136_s7.txt` (30,751 B, sha256 1e09b176c3f545db…)
