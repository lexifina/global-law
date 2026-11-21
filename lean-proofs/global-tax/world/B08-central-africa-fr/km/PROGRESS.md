# Comoros (KM) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: CM (30 % frais), kernel Schedule.
- Statute read: CGI 2022 (finances.gouv.km 'Comores-CGI-2022.pdf', archived 2022-10-22) arts. 55-60, 97; LF 2024 (Loi 23-019/AU, archived, scanned, OCR pp. 1-60): arts. 12-13 amend CGI arts. 15, 38, 89, 100, 155, 196 (no wage article); LF 2023 and LF 2025 not reached
- Registry correction: Registry 'progressive, IRPP' confirmed: individual, 0 % to 150 000, 5/10/15/20/25/30 % (art. 97) on gross less social deductions (cap 6 %) less 30 % (art. 59).
- Lean: 80 lines, 8 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/kmtax` (worldMain).
- Unsupported (listed in the outputs): employee social contributions (input socialEmployee); revenus de valeurs mobilières, rents, gains; LF 2023, LF 2025.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: comoros corpus = metadata only
  - finances.gouv.km: no answer; Internet Archive: 'Code des impôts 2022' page and PDF, LF 2024 promulgation decree PDF (scanned)
  - agid.km, impots.km: nothing archived
- Files on disk:
  - `law/cgi2022.pdf` (1,027,036 B, sha256 aaf119ac2a062558…)
  - `law/cgi2022_page.html` (122,105 B, sha256 09c55a2c0cf09043…)
  - `law/lf2024.pdf` (31,216,571 B, sha256 79e5c0c5824b8fe3…)
  - `law/lf2024_page.html` (328,331 B, sha256 1948c7fc1521d5a1…)
