# Cuba (CU) progress

**Status (2026-11-20T07:27Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: ES (Spanish-language schedule), B12 Latin America patterns.
- Statute read: Ley 113 Del Sistema Tributario, texto anotado y concordado (G.O. ES No. 1 de 2021) arts. 19 g), 20, 22 (Decreto-Ley 21/2020), 25-29, 30-39; Ley 174 Del Presupuesto del Estado para el Año 2025 (G.O. No. 127 Ordinaria de 2024) arts. 17-21, 63-68
- Registry correction: Registry 'Ley 113 del Sistema Tributario; state-sector wages treated specially' updated: Ley 174 art. 67.1 applies the personal income tax to salaries of all sectors in 2025; Ley 113 art. 22 mínimo exento 39,120 CUP and art. 26 scale 15-50 %; Contribución Especial a la Seguridad Social 5 % to 15,000 a month and 10 % above (Ley 174 art. 20.2). The monthly withholding scale for salaries was not reached.
- Lean: 85 lines, 7 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/cutax` (worldMain).
- Unsupported (listed in the outputs): the monthly salary withholding scale (MFP resolution) not reached: reading switch cuWageTax; self-employed regimes; other income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law cuba corpus (7 acts, no tax law)
  - gacetaoficial.gob.cu node search and issue PDFs (GOC-2021-ES1, GOC-2024-O127)
  - onat.gob.cu (unreachable from both hosts)
  - mfp.gob.cu (home only)
- Files on disk:
  - `law/g.html` (26,660 B, sha256 d22800a4041d368a…)
  - `law/g174.html` (22,979 B, sha256 fe8166155148931f…)
  - `law/gaceta-oficial-no-1-edicion-especial-de-2021.html` (28,860 B, sha256 f7d691a7a5887095…)
  - `law/gaceta-oficial-no-1-edicion-especial-de-2026.html` (26,770 B, sha256 3b55017be3dcd7d2…)
  - `law/goc-2021-es1.pdf` (1,265,453 B, sha256 c9d878f0468c572c…)
  - `law/l174.html` (24,351 B, sha256 64e0ca0ce9aecbde…)
  - `law/l181.html` (24,366 B, sha256 3de2e39c8c07c7ba…)
  - `law/ley-113-de-2012-de-asamblea-nacional-del-poder-popular-0.html` (24,848 B, sha256 da1f4e9af94ac8b1…)
  - `law/ley-113-de-2012-de-asamblea-nacional-del-poder-popular-1.html` (24,524 B, sha256 0cdceb27d8b383a8…)
  - `law/ley-113-de-2012-de-asamblea-nacional-del-poder-popular.html` (31,300 B, sha256 0627db5848c386b4…)
  - `law/ley174_presupuesto2025.pdf` (336,775 B, sha256 63ec5799224564ee…)
  - `law/p.html` (28,938 B, sha256 ba4274428ee808c1…)
  - `law/p25.html` (29,673 B, sha256 406fd02ae9644d9a…)
  - `law/s.html` (28,695 B, sha256 bac8b38821e0d4c4…)
