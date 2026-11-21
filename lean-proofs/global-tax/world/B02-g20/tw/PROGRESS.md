# Taiwan (TW) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (民國114年度 income year); access tier A; reused patterns: KR, JP.
- Statute read: 所得稅法 (Income Tax Act) arts. 5, 5-1, 14, 15, 17, 71 via Global law (taiwan/national/acts/law/1943/G0340003, as in force 2025-12-31); MOF art. 5 (4) announcement of 2024-11-28 for 114年度 (no CPI adjustment: +2.29 % < 3 %); MOF basic living expense 213,000 (2025-11-27); 114年度 filing briefing.
- Registry correction: Unit: joint return of the taxpayer and spouse (art. 15 (1)) with three computation options (all combined / one spouse's salary separately / one spouse's all income separately) and two dividend options (8.5 % credit up to 80,000 or 28 % separate); registry 'joint' is right but the options make it close to separate assessment of salaries.
- Lean: 218 lines, 35 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/twtax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): employee social insurance; AMT (所得基本稅額條例); adult-children dependants conditions.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent 2): labour + employment insurance (20 % of 11.5 % + 1 % on the 2025 insured-salary grade, 28,590-45,800, part-time grades below) and NHI (30 % of 5.17 % on the 59-grade table 28,590-313,000, x (1 + dependants up to 3)); NHI and LI premiums added to the itemized deduction (art. 17 (1) 2 (二) 2). Provision: 勞工保險條例 art. 13 (2) (12.5 % for 2025), 14, 15; 就業保險法 arts. 8, 40, 41 (2) (-1 %); 勞動部令 2024-11-15 勞動保2字第1130087589號 grading table; BLI 114 share table (official secondary); 全民健康保險法 arts. 2, 18, 19, 27; NHIA 114 grading and share tables (5.17 %, official secondary); 所得稅法 art. 17 (1) 2 (二) 2. Rebuilt (#guards pass), check `w5/pa/check.py TW` 0 / 300 differ with the switch off, rescanned (`scan_world.py TW`).
