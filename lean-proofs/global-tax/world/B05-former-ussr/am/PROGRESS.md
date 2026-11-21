# Armenia (AM) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: EE, LV, LT.
- Statute read: Tax Code HO-165-N arts. 143, 147, 150 via Global law (armenia/national/acts/code/2016/ՀՕ-165-Ն, dated 2025-07-01; art. 150 unchanged in words during 2025; official arlis.am/hy/acts/153403); Law HO-244-N on funded pensions arts. 5, 6, 81 (in force text 2025-01-01); Law HO-66-N on the minimum monthly wage art. 1 (75 000 dram); Law HO-245-N arts. 10-12 (stamp duty).
- Registry correction: Registry 'flat; social payment' confirmed and extended: 20 % flat (art. 150(1), from 2023); funded-pension social payment 5 % / 10 % less 25 000 above 500 000 a month, capped at 15 x minimum wage, only for those born 1974 or later; plus a monthly stamp duty (military compensation fund) of 1 500-15 000 dram by wage band.
- Lean: 124 lines, 20 defs, 5 theorems, 6 #guard checks, 0 sorry; exe `lean/.lake/build/bin/amtax` (worldMain).
- Unsupported (listed in the outputs): voluntary social payment of pre-1974 cohorts; turnover/micro regimes; combined salary + business social payment cap.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/art150_147_20250701.txt` (43,320 B, sha256 9320be4be1946628…)
  - `law/art154_143.txt` (5,522 B, sha256 609544b77d9199d0…)
  - `law/funded_5_6_20250701.txt` (23,822 B, sha256 d01355bba8c2ace2…)
  - `law/funded_81_20250701.txt` (17,978 B, sha256 78d33cddb16f17d0…)
  - `law/funded_list.txt` (13,207 B, sha256 b0661d82ebdeb40e…)
  - `law/gl_list.txt` (81,770 B, sha256 2d420c1b7dfb3122…)
  - `law/minwage_1.txt` (2,231 B, sha256 a79b3b55cf199bd9…)
  - `law/pension_list.txt` (9,808 B, sha256 0166386a02b9a755…)
  - `law/s_socpay2.txt` (23,477 B, sha256 7db9520b3abdced8…)
  - `law/s_stamp.txt` (24,038 B, sha256 85d85ce143a1e1eb…)
  - `law/stamp_11_12_20250701.txt` (10,412 B, sha256 d9d5170a3aba9b6d…)
