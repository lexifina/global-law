# Lebanon (LB) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: FR.
- Statute read: Decree-Law 144/1959 Title II (MoF consolidated PDF, 2014), arts. 31 and 58 as rewritten by Budget Law No. 324 of 12/2/2024 arts. 47 and 49.
- Registry correction / check: Registry right (schedular; the salary tax is Title II). Detail: 2-25 % on seven bands rescaled in 2024 (360 M to 13.5 B LBP); family deduction 450 M + 225 M married + 45 M per child (max 5).
- Lean: 85 lines, 8 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/lbtax` (worldMain).
- Sources (law/):
- `law/itl.pdf` sha256 d33fc606841883dd068c845e60ec53518ae44c7dbad472c6648edb6a788a38f5
- `law/budget2024.pdf` sha256 732e766705ad533906e56a7907fd8098194fd398863f5dda3291fa1238a03c22
- `law/budget2025.pdf` sha256 921fb75a42297c0bceced7fd8867427b43682dfb3700f8900b8ab433b7a54899
- Unsupported (in every output line): NSSF contributions, pension deduction (art. 50); Titles I and III; 2025 budget read by OCR (pages 1-40).
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.
