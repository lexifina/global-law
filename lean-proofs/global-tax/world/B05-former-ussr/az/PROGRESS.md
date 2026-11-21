# Azerbaijan (AZ) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: RU, KZ.
- Statute read: Tax Code (2000) arts. 101, 102, 122, 123 via Global law (azerbaijan/national/acts/mecelle/2000/46948, dated 2025-07-01; art. 101 words unchanged during 2025; official e-qanun.az/framework/59338); Law 250-IQ on social insurance art. 14 (consolidated 2025-08-13 = amending Law 1360-VQD in force 2019-01-01); Law 765-VQ on unemployment insurance art. 9; Law 725-IQ on medical insurance art. 15-10.
- Registry correction: Registry 'progressive; non-oil private sector exemption' confirmed: state/oil sector 14 % to 2 500 a month and 25 % above (350 + 25 %); non-oil private sector 0 % to 8 000 a month and 14 % above, for 7 years from 2019 (ends 2025-12-31); employee premiums 3 % (10 % above 200 in the private sector) + 0.5 % unemployment + 2 % / 0.5 % medical.
- Lean: 124 lines, 20 defs, 7 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/aztax` (worldMain).
- Unsupported (listed in the outputs): self-employed social premium (minimum wage not read); 18-month deposits; 50 % gain exemption on shares held 3+ years; multiple workplaces.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/gl_list.txt` (14,579 B, sha256 cdfd6a9e7d1799fc…)
  - `law/m101_20250701.txt` (18,710 B, sha256 6f00f656d6cf0fe2…)
  - `law/m102_122_123_20250701.txt` (93,630 B, sha256 f565ae4ae10a2952…)
  - `law/med_15-10.txt` (7,346 B, sha256 6ff8dcf63c324c1d…)
  - `law/med_15-11.txt` (18,341 B, sha256 87b37d5079214fe5…)
  - `law/s_unemp.txt` (15,720 B, sha256 4c804d0cefcedfdb…)
  - `law/ssi250_14_20250813.txt` (19,632 B, sha256 87cd531b00fb9a81…)
  - `law/ssi_14.txt` (9,622 B, sha256 2350333ade2451b4…)
