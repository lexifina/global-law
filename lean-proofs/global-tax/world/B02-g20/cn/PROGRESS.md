# China (CN) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: KR, JP.
- Statute read: 个人所得税法 (2018 amendment, in force 2019-01-01) and 实施条例 (2018) from 国家法律法规数据库 flk.npc.gov.cn (docx via its API).
- Registry correction: Registry right (comprehensive income, annual). 专项附加扣除 standards and social insurance are outside the Act (State Council and city notices): not reached.
- Lean: 93 lines, 11 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/cntax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): 专项附加扣除; 专项扣除 (social insurance, housing fund); preferential notices; interest.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.
- W5 review pass 2 (2026-11-20): 专项附加扣除 for children (国发〔2018〕41号 第五、六条; 国发〔2023〕13号) implemented with
  inputs `cnChildAlloc`, `cnChildDeduction`; FINDINGS W5R-1; rescanned.
