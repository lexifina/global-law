# India (IN) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: FY 2025-26 (AY 2026-27); access tier B; reused patterns: UK, IE, AU.
- Statute read: Income-tax Act 1961 (not in Global law; the Income-tax Act 2025 there applies from 2026-04-01); Finance Bill 2025 cls. 20, 24 and memorandum (indiabudget.gov.in); Finance (No. 2) Bill 2024 cl. 10 (s. 16 (ia)); Income Tax Department AY 2026-27 slab page (official secondary).
- Registry correction: Registry: Global law holds the Income-tax Act 2025 (in force 2026-04-01), not the 1961 Act that governs FY 2025-26.
- Lean: 157 lines, 20 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/intax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): EPF; house property; capital gains; 80TTA/80TTB; s. 288A/288B rounding.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.
- W5 review pass 2 (2026-11-20): ss. 288A / 288B rounding (FINDINGS W5R-1); rescanned.
