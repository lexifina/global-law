# Thailand (TH) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (B.E. 2568); access tier A; reused patterns: JP, KR.
- Statute read: Revenue Code as published by the Revenue Department (rd.go.th): s. 42 bis (50 % expense deduction max 100,000), s. 47 (allowances 60,000 / 60,000 / 30,000 per child + 30,000 for 2nd+ child born 2018+), s. 47 (2), s. 48 (1)-(3), rate schedule (Act No. 44, B.E. 2560); Royal Decree No. 470 s. 4 (first 150,000 of net income exempt).
- Registry correction: Unit: spouses file separately (s. 57 ter marked repealed from tax year 2555); the 150,000 zero band is a Royal Decree exemption, not part of the Code's schedule.
- Lean: 108 lines, 10 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/thtax` (worldMain). Scale: `scale.json`.
- Sources: `law/` (sha256 in law/SHA256SUMS where files were saved).
- Unsupported: employee social security (ministerial regulations not reached: sso.go.th downloads 404); dividends (10 % final or credit); rent; capital gains; pensions; RD 480 exemption of small s. 48 (2) amounts.
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py + b03scan); 6 government/statute errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent 2): social security 5 % of the monthly wage within 1,650-15,000 (max 750 a month), rounded to the baht; deducted under s. 47 (1) (ฌ). Provision: กฎกระทรวงกำหนดอัตราเงินสมทบ พ.ศ. 2545 ข้อ 2-3, บัญชี ข-ค (1.5 % + 3 %); กฎกระทรวง ... ว่างงาน พ.ศ. 2546 ข้อ 1 (3) (0.5 %); กฎกระทรวง ฉบับที่ 7 (พ.ศ. 2538) ข้อ 1 (1,650-15,000); SSA s. 33, s. 46; Revenue Code s. 47 (1) (ฌ) (SSO copies via the Wayback Machine). Rebuilt (#guards pass), check `w5/pa/check.py TH` 0 / 300 differ with the switch off, rescanned (`scan_world.py TH`).
