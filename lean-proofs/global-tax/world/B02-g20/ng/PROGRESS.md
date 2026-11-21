# Nigeria (NG) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (year of assessment 2025; Nigeria Tax Act 2025 applies from 2026); access tier A; reused patterns: UK, IE.
- Statute read: Personal Income Tax Act Cap. P8 as amended by the PITA (Amendment) Act 2011 (s. 5 → s. 33 (1), s. 34 Sixth Schedule) and the Finance Act 2020 (ss. 29-30 → s. 33 (2), s. 37 proviso); Pension Reform Act 2014 s. 4 (1) (b); scanned gazettes from lirs.gov.ng / pencom.gov.ng read by OCR, the rate page checked as an image.
- Registry correction: Registry: 2025 is PITA, not the Nigeria Tax Act 2025 (from 2026). Lagos default (PITA is a federal law administered by the state of residence: same rates).
- Lean: 87 lines, 11 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/ngtax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): NHF/NHIS; minimum-wage proviso; investment income; pensions.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.
