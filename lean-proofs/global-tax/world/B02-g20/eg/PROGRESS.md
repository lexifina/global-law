# Egypt (EG) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: FR.
- Statute read: Income Tax Law 91/2005 art. 8 and art. 13 (1) as replaced by Law 7/2024 (Official Gazette 7 bis (a), 21 Feb 2024), ETA copy law_no.7-2024.pdf (HTML appended after %%EOF stripped).
- Registry correction: Registry right; the art. 8 table chooses the bands by the size of the whole net income (six columns).
- Lean: 81 lines, 7 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/egtax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): social insurance (Law 148/2019); rent, dividends, interest; pensions.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent): Law 148/2019 employee 9 % + 1 % on the monthly contribution wage 2,300-14,500; deducted (ITL art. 13 item 5). Provision: Law 148/2019 arts. 19 (1) (b), 36 (1); NOSI notice 30/11/2025 (2025 limits, official secondary); ITL 91/2005 art. 13 (ETA circular 1/2005). Rebuilt (#guards pass), check `w5/pa/check.py EG` 0 / 300 differ with the switch off, rescanned (`scan_world.py EG`).
