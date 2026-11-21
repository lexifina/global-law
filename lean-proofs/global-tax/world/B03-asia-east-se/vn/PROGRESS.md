# Viet Nam (VN) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: KR, JP.
- Statute read: Consolidated Law on Personal Income Tax 103/VBHN-VPQH (Official Gazette 1283+1284, 11-9-2025): arts. 4, 19, 21, 22, 23; Law on Social Insurance 41/2024/QH15 art. 33 (Global law); vbpl.vn answers 403 to scripts; the Standing Committee resolution adjusting the art. 19 amounts was not found in the Gazette's listings.
- Registry correction: PIT Law 04/2007/QH12 is reachable as the Office of the National Assembly's consolidated text in the Official Gazette (congbao.chinhphu.vn, which also serves amending laws as PDF); the family-deduction amounts in force are set by a Standing Committee resolution, not by the Law's text. New PIT law 109/2025/QH15 applies from 2026.
- Lean: 90 lines, 9 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/vntax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS where files were saved).
- Unsupported: family deductions as adjusted under art. 19 (1) CPI clause (statute's printed 9 / 3.6 million used); health and unemployment insurance; SI ceiling; business, rent, capital gains.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py + b03scan); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent 2): social-insurance ceiling defaulted to 20 x lương cơ sở 2,340,000 = 46.8 million a month (input vnSiBaseCapMonthly still wins). Provision: Nghị định 73/2024/NĐ-CP Điều 3 (2) (datafiles.chinhphu.vn); Law 41/2024 art. 31 (1) đ). Rebuilt (#guards pass), check `w5/pa/check.py VN` 0 / 300 differ with the switch off, rescanned (`scan_world.py VN`).
