# Dominican Republic (DO) progress

**Status (2026-11-20T07:27Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (fiscal year = calendar year, art. 300); access tier B; reused patterns: ES/MX (Spanish-language progressive scale), B12 Latin America patterns.
- Statute read: Código Tributario (Ley 11-92) Título II (DGII PDF) arts. 296 (Ley 253-12), 297, 299 o), 300, 327; 2025 amounts from the DGII 'Impuesto sobre la Renta' page as archived on 2025-06-22 (official secondary); SDSS rates and caps from the TSS FAQ (official secondary)
- Registry correction: Registry 'Codigo Tributario (Ley 11-92)' confirmed: art. 296 progressive scale indexed by inflation (art. 327); DGII 2025 table exempt to 416,220, 15 % to 624,329, 20 % to 867,123, 25 % above; SDSS employee 3.04 % (SFS) + 2.87 % (AFP), caps 10 and 20 minimum wages.
- Lean: 99 lines, 6 defs, 5 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/dotax` (worldMain).
- Unsupported (listed in the outputs): SDSS caps need the 2025 SMN (input doSmn); deductibility of SDSS (Ley 87-01) not read; salario de Navidad exemption; investment income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law dominican-republic corpus (Constitution only)
  - dgii.gov.do (403 from lean1; read from the laptop: Codigo Tributario Titulo II PDF, ISR page)
  - consultoria.gov.do (403)
  - tss.gob.do FAQ (2026 caps only)
  - Internet Archive copy of the DGII ISR page (2025-06-22); later the Archive refused both hosts
- Files on disk:
  - `law/CodigoTributario_Titulo2_dgii.pdf` (457,505 B, sha256 9118c0e2afd1da1a…)
  - `law/dgii_impuestoSobreRenta_wayback_20250622.html` (310,205 B, sha256 ebfc723553183e5c…)
  - `law/tss.html` (175,496 B, sha256 7616767cb4e4282e…)
  - `law/tss_preguntas-frecuentes.html` (199,098 B, sha256 9ca2b36fecc62cd6…)
  - `law/tss_sobre-nosotros_marco-legal.html` (164,067 B, sha256 08d3182ffc19b9a5…)
