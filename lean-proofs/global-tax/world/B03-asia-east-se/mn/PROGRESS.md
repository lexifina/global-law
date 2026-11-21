# Mongolia (MN) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: KR, JP.
- Statute read: Law on Personal Income Tax (revised 2019, lawId 14410): art. 21.1 as reworded 2022-11-11 and art. 23.1 credit table, read from the archived official page (legalinfo.mn, Wayback 2025-06-25) because Global law holds only the 2026-10-28 consolidated text (art. 21.1/23.1 replaced from 2027); Social Insurance General Law 2023 arts. 18.1, 19.4 (archived 2025-08-09); Health Insurance Law art. 8 + Government resolution 02/2025 (2 %); minimum wage 792,000 from 2025-04-01 (General Authority for Social Insurance).
- Registry correction: Rates: 10 % to 120m MNT, 15 % to 180m, 20 % above (from 2023, law of 2022-11-11), not a flat 10 %; plus a stepped annual tax credit (art. 23.1) that ends at 36m. The law of 2026-06-26 adds a zero band of 9,504,000 and repeals the credit from 2027 (Global law's current text already shows it).
- Lean: 116 lines, 12 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/mntax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS where files were saved).
- Unsupported: capital gains (art. 17 needs asset type/price); Jan-Mar 2025 SI ceiling (earlier minimum wage not reached; flagged above 3,960,000 a month); voluntary social insurance of the self-employed.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py + b03scan); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.
- 2026-11-20 W5 review: see FINDINGS W5-1.
