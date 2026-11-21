# Cameroon (CM) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: FR (individual IRPP with centimes), kernel Multiplier pattern (CAC).
- Statute read: CGI 2024 (archived impots.cm 2024-02-17) and CGI 2026 (impots.cm): arts. 29, 30, 31, 34, 67, 69, 70, 71, 81 read identically in both; LF 2025 circular (archived 2025-02-28, scanned, OCR): no wage change, IRCM 10 % for dividends of companies with turnover <= 3 bn from 2025 (CGI 2026 art. 70 (2)); Loi 77-10 (CFC) arts. 4-6; Ordonnance 89/004 (RAV) art. 3 (5) as modified by LF 2003/017; TDL CGI 2024 art. C 58 (= CGI 2026 art. C 86); CNPS: Décret 2016/072 arts. 3-4 (CNPS 'Recueil des textes de base' Nov. 2022, archived; listed on cnps.cm 'Textes réglementaires', archived 2025-10-13)
- Registry correction: Registry 'progressive, individual, IRPP + CAC multiplier' confirmed and extended: IRPP 10/15/25/35 % on (gross - 30 % frais capped at 4.8 M - CNPS pension) - 500 000 (arts. 29, 34, 69); CAC 10 % of the tax (art. 71); plus wage levies outside the IRPP: TDL (communal, flat by monthly base salary), CFC 1 %, RAV (monthly flat by gross); CNPS pension 4.2 % capped at 750 000 a month. No family quotient.
- Lean: 152 lines, 19 defs, 5 theorems, 6 #guard checks, 0 sorry; exe `lean/.lake/build/bin/cmtax` (worldMain).
- Unsupported (listed in the outputs): self-employment (art. 17 rate + 2 % turnover minimum); rental income; capital gains; TDL at the CGI's maximum rates (communes may set lower).
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: cameroon corpus = constitution + 2 acts (no tax law)
  - impots.cm 'Lois et règlements': CGI 2026 PDF; CGI 2025 node 404; CGI 2024 and the LF 2025 circular via the Internet Archive
  - cnps.cm: no answer from lean1 or the laptop; Internet Archive copies of the CNPS 'Recueil des textes de base' (Nov. 2022) and the 'Textes réglementaires' page (2025-10-13)
  - not opened (referee values): impots.cm 'BAREME IRPP_DSSI final.pdf' (withholding table), 'BAREME TDL_DSSI'
- Files on disk:
  - `law/cgi2024.pdf` (9,095,444 B, sha256 b90d94c360893c6c…)
  - `law/cgi2026.pdf` (9,983,779 B, sha256 374c1d95ba2843dc…)
  - `law/circ_lf2025.pdf` (17,301,900 B, sha256 483999f0e56708a4…)
  - `law/cnps/cotis_20251013.html` (339,534 B, sha256 fc9746061bb36a90…)
  - `law/cnps/cotis_20260216.html` (339,534 B, sha256 fc9746061bb36a90…)
  - `law/cnps/recueil2022.pdf` (16,674,780 B, sha256 91a6285c3d5cba6b…)
  - `law/cnps/textes_20251013.html` (195,452 B, sha256 ff53350f1b1b5e8b…)
- 2026-11-20 round D6: IRPP barème gap traced to the DGI's published withholding formula (CGI 2026 annex: 2,8 % / 300 000 CNPS, no 4,8 M frais cap); `--dgi-bareme` added per dataset with that citation; statute unchanged.
- 2026-11-20 round D7: `--dgi-bareme` verified against the published note (no error); the 2025 barème's parameters differ from the note; a further flag needs the DGI's statement.
