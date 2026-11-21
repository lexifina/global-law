# Iraq (IQ) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: UK.
- Statute read: Income Tax Law No. 113 of 1982 as amended (CPA Order 49 of 2004 and later), GCT consolidated text (archived official copy, 26/9/2023), arts. 12, 13.
- Registry correction / check: Registry right (progressive, individual; Kurdistan separate: federal law modelled). Detail: allowances 2.5 M (+2 M housewife, +200,000 per child, 3.2 M widow/divorcee, +300,000 over 63); rates 3/5/10/15 %.
- Lean: 82 lines, 6 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/iqtax` (worldMain).
- Sources (law/):
- `law/itl113.html` sha256 40e590aec5bf3d70b10d5d41ee4a1d57368b157f0308bf1f81ed1db6f5c265fb
- Unsupported (in every output line): social security (Law 18/2023); budget-law changes 2023-2025; exempt allowances, investment income, Kurdistan.
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.
