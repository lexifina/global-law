# Kazakhstan (KZ) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: RU, EE.
- Statute read: Tax Code K1700000120 (in force to 2025-12-31) arts. 320, 341, 342, 346, 347 (Internet Archive copy of adilet.zan.kz, 2025-06-11); budget law Z2400000141 art. 9 (MRP 3 932, MZP 85 000; archived 2025-04-19); Social Code K2300000224 art. 249 (OPV 10 %, cap 50 MZP; archived 2025-04-30); Law Z1500000405 art. 28 (VOSMS 2 %, cap 10 MZP; archived 2025-07-04).
- Registry correction: Registry 'flat; new Code from 2026' confirmed: 2025 is under the 2017 Code: 10 % flat (art. 320) after OPV, VOSMS and a standard deduction of 14 MRP a month; the 2026 Code (progressive) does not apply to 2025. Global law's KZ corpus has no Tax Code; adilet's API needs credentials, so archived official copies were used.
- Lean: 99 lines, 16 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/kztax` (worldMain).
- Unsupported (listed in the outputs): OPV at pension age; special regimes for entrepreneurs; conditions of the dividend exclusion beyond the cap.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/adilet_K1700000120_wb20250611.html` (5,985,571 B, sha256 616519027bd1c406…)
  - `law/art341.txt` (37,405 B, sha256 6c67586ce13d81ae…)
  - `law/osms_wb20250704.html` (234,623 B, sha256 0273faa06de872ab…)
  - `law/osms_wb20250704.txt` (176,239 B, sha256 40101c9dcb8d9672…)
  - `law/socode_wb20250430.html` (1,544,079 B, sha256 7f2fdd26e597d20e…)
  - `law/socode_wb20250430.txt` (1,331,664 B, sha256 212c1a76b3c80036…)
  - `law/tc_wb20250611.txt` (5,013,747 B, sha256 c357384800024df7…)
  - `law/z140.html` (31,530 B, sha256 8b25beeb012dce29…)
  - `law/z140.txt` (7,927 B, sha256 e4f89eb6a4562135…)
  - `law/z141.html` (437,832 B, sha256 9c5ade73f2c8e4f7…)
  - `law/z141.txt` (246,886 B, sha256 71458fdf7c8a4cd5…)
