# Tunisia (TN) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: FR.
- Statute read: Code de l'IRPP et de l'IS (loi 89-114) as amended by loi 2024-48 (LF 2025) art. 36; DGI consolidated code July 2025; CSS: LF 2018 art. 53 and LF 2023 art. 22 via DGI Note commune 1/2026.
- Registry correction / check: Registry right (progressive, individual; OpenFisca-Tunisia exists). Barème replaced by LF 2025 art. 36 (eight bands 0-40 %); Global law's copy stops in 2020/21 and shows the old five-band barème.
- Lean: 128 lines, 13 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tntax` (worldMain).
- Sources (law/):
- `law/LF2025.pdf` sha256 08feaf86e175c192c3f3f87a176b126abfafea044eb36e634a3ed5818cd0f889
- `law/code2025fr.pdf` sha256 0006d25e15d7a9ed1fd844e69c4abbaa012d779c06004369acb225e881fbd885
- `law/nc2026_1.pdf` sha256 6f89c68c5be8965f800c2f6091b9040e37695fe17a870f793b2d8f707f83a6db
- Unsupported (in every output line): CNSS employee contributions (not deducted); interest and dividends; art. 39 deductions; students/disabled children deductions.
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNSS employee 9,18 % of all remuneration, deducted under Code IRPP art. 26 I before the 10 % frais. Provision: CNSS page for non-agricultural employers, contributions tab (cnss.tn, fetched 2026-11-20): 25,75 % = 16,57 % employer + 9,18 % employee, base all remuneration (loi 60-30 arts. 40-47, 105); official secondary (décrets not reached); Code IRPP art. 26 I. Rebuilt (#guards pass), check `w5/pa/check.py TN` 0 / 300 differ with the switch off, rescanned (`scan_world.py TN`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
