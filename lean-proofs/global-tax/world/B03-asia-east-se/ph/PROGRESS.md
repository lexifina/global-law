# Philippines (PH) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: UK, AU.
- Statute read: RA 10963 (TRAIN) Sec. 5 (NIRC Sec. 24 (A) (2) schedule from 2023), Sec. 24 (B), Sec. 32 (B) (7) (e): Official Gazette signed scan archived by the Internet Archive (2018-01-08), page images OCR'd and checked by eye; officialgazette.gov.ph, judiciary e-library, Congress and Senate answer 403 to scripts; Global law lacks RA 10963.
- Registry correction: Main statute for 2025 is NIRC Sec. 24 (A) as amended by RA 10963 (2023 schedule 0/15/20/25/30/35 %); spouses compute separately; minimum wage earners exempt.
- Lean: 81 lines, 7 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/phtax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS where files were saved).
- Unsupported: SSS, PhilHealth, Pag-IBIG contributions; rent; capital gains; pensions; 8 % option for the self-employed.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py + b03scan); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent): SSS 5 % (MSC 5,000-35,000), PhilHealth 2.5 % (10,000-100,000), Pag-IBIG 2 % (max 10,000 / month); excluded from gross income (NIRC s. 32 (B) (7) (f)). Provision: RA 11199 s. 4 (a) (9); RA 11223 s. 10 with PhilHealth Circ. 2020-0005 and Adv. 2025-0002; RA 9679 s. 7 with HDMF Circ. 460 (per DBM CL 2024-2). Rebuilt (#guards pass), check `w5/pa/check.py PH` 0 / 300 differ with the switch off, rescanned (`scan_world.py PH`).

- 2026-11-20 W5 pattern A follow-up (contributions agent 2): SSS monthly salary credit = compensation rounded to the nearest P500 (halves up) within 5,000-35,000 (was: compensation clamped), member 5 %. Provision: SSS Circular No. 2024-006 (19 Dec 2024), Schedule of SSS contributions effective January 2025 (SSS table image, `law/w5/sss_circular_2024-006_schedule_2025.jpg`); RA 11199 Sec. 4 (a) (9). Rebuilt, check 0 / 300 with the switch off, rescanned.
