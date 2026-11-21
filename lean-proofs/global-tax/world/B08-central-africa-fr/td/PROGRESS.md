# Chad (TD) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: CM (wage base), kernel flat-capital pattern.
- Statute read: Loi de finances 2023 art. 36 (CGI art. 1 rewritten: revenus du travail barème 0/10.5/15/20/25/30 %, revenus du capital 20 %; archived dgi.td, scanned, OCR checked on the page image); LF 2025 (archived, OCR): art. 116, 82, 90 amended, art. 1 unchanged; LF 2024 circular 001 (PSA 400 FCFA a month); CGI 2016 (archived dgi.td) arts. 47-48 for the wage base
- Registry correction: Registry 'progressive, individual, IRPP' corrected: since 2023 the IRPP is split into 'revenus du travail' (barème 0 % to 800 000, 10.5 % to 6 M, 15 %, 20 %, 25 %, 30 % above 12 M) and 'revenus du capital' (flat 20 %); the 2016 quotient (arts. 109-115) is taken as superseded; PSA 400 FCFA a month on every salary (LF 2024).
- Lean: 95 lines, 9 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tdtax` (worldMain).
- Unsupported (listed in the outputs): the current CGI's wage base (2016 arts. 47-48 used); family quotient (2016) not applied; employee CNPS (input cnpsEmployee); self-employment, rents, gains.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: chad corpus = labour code, penal code, constitution (presidence.td)
  - dgi.td: 403 / suspended page; Internet Archive copies of CGI2016, LF2023, LF2024 (truncated at 1 MB), LF2025, circulars 2023 and LF2024
  - presidence.td 403; finances.gouv.td, cnps.td, sgg.td: no answer
- Files on disk:
  - `law/cgi2016.pdf` (1,531,741 B, sha256 473f405524cdba51…)
  - `law/circ2023.pdf` (669,587 B, sha256 389412825faf615e…)
  - `law/circ_lf2024.pdf` (6,136,675 B, sha256 9fe13881ff69fa1d…)
  - `law/lf2023.pdf` (5,479,931 B, sha256 01078222c7649694…)
  - `law/lf2024.pdf` (1,048,576 B, sha256 508f6a93f87262b3…)
  - `law/lf2025.pdf` (35,927,439 B, sha256 6347f0c1069b1772…)
