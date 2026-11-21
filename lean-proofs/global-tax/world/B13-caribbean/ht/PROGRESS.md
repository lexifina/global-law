# Haiti (HT) progress

**Status (2026-11-20T07:27Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2026-27 (fiscal year from 1 October 2026; the 2024-25 law was not reached); access tier B; reused patterns: FR (francophone code, barème par fractions).
- Statute read: Décret remplaçant le Décret du 19 décembre 2022 portant Code Fiscal (Le Moniteur Spécial N° 48-A, 30 septembre 2026; DGI PDF) arts. 3, 98-103, 126, 132, 243, 540-543
- Registry correction: Registry 'Decret sur l'impot sur le revenu; little accessible law' updated: a Code Fiscal (Décret of 19 December 2022) governed FY 2024-25 but was not reached; its replacement in force 1 October 2026 taxes global income 0/12/18/25/30 % (360,000 / 540,000 / 1,080,000 / 2,160,000) with a 1 % CAS levy on salaries; couples declare separately.
- Lean: 84 lines, 6 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/httax` (worldMain).
- Unsupported (listed in the outputs): model is for FY 2026-27, not 2025; ONA contribution; art. 126 deductions needing inputs; categorical capital income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law haiti corpus (Constitution, Code du travail, pension decree)
  - dgi.gouv.ht (laptop): textes-de-loi, dgi_doc pages, wp-json media search
  - mef.gouv.ht (home only)
  - ona.gouv.ht (does not resolve)
- Files on disk:
  - `law/Code-Fiscal_dgi_2026-10.pdf` (95,352,363 B, sha256 9b00c3196dab63be…)
