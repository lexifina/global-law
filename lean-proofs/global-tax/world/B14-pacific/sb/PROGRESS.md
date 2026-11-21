# Solomon Islands (SB) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year); access tier A; reused patterns: AU/NZ PAYE (personal exemption + bands).
- Statute read: Income Tax Act (Cap. 123) reprint as in force at 5 February 2024 (ird.gov.sb) ss 28, 32, Fifth Schedule, endnotes; Solomon Islands National Provident Fund Act (Cap. 109) s 13 and Second Schedule (archived PacLII copy of the 1996 Revised Edition, OCR checked on the image); SINPF (Amendment) Act 2018 (archived PacLII copy)
- Registry correction: Registry 'Income Tax Act (Cap. 123)' confirmed: personal exemption $30,080 (s 28, since 1 January 2020), then 11/23/35/40 % (Fifth Schedule brackets 15,000/30,000/60,000); SINPF employee 5 cents per complete dollar of monthly wages (employer 12.5).
- Lean: 119 lines, 13 defs, 5 theorems, 7 #guard checks, 0 sorry; exe `lean/.lake/build/bin/sbtax` (worldMain).
- Unsupported (listed in the outputs): interest and dividend withholding / s 36 credit; the s 32 $5 proviso; later amendments after 5 February 2024 (none found).
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: solomon-islands corpus holds the Constitution and UN treaties only
  - ird.gov.sb Tax Legislation page: Income Tax Act reprint (as in force at 5 February 2024)
  - PacLII (paclii.org) answers lean1 and the laptop with a Cloudflare challenge: not bypassed; Internet Archive copies used (CDX listing in logs/cdx_paclii.log)
- Files on disk:
  - `law/INCOME-TAX-ACT-CAP-123.pdf` (633,157 B, sha256 1676176a67a2579b…)
  - `law/paclii_sinpfa1993501.pdf` (195,740 B, sha256 59724e0b93e761bc…)
  - `law/paclii_sinpfa2018501.pdf` (216,963 B, sha256 3cecb5c1f30a11f4…)
  - `law/paclii_sinpfa421.pdf` (771,782 B, sha256 a87f22d5ba1af56c…)
