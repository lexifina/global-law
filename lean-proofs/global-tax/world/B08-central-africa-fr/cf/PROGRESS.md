# Central African Republic (CF) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: CM (individual IRPP, 30 % frais).
- Statute read: CGI 2017 'Edition officielle mise à jour 2023/DGID' (finances.gouv.cf) arts. 36-40, 80, 84, 86, 237-243; Loi de finances 2025 (finances.gouv.cf, scanned; OCR pp. 1-60): fiscal articles 9-18 amend CGI arts. 135 bis 4, 249, 275 bis, 344 and LPF arts. 4, 71, 88, 171, 226, 243 (no wage article); collectif 2024 (OCR pp. 1-40, budget tables only)
- Registry correction: Registry 'progressive, individual, IRPP' confirmed: wage IRPP 0/8/15/28/40 % on gross less 30 % frais and CNSS (arts. 38, 39, 86), individual; RCM 15 % (art. 84); the CDS 10 % (arts. 237-243) is an employer payroll tax.
- Lean: 92 lines, 8 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/cftax` (worldMain).
- Unsupported (listed in the outputs): employee CNSS contributions (rate not reached; input cnssEmployee); self-employment; rents and gains; the 2024 finance law.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: CAR corpus = labour code, penal code, criminal procedure, constitution
  - finances.gouv.cf 'Lois de finances': LF 2025, collectifs 2024 and 2025, LF 2026 (all scanned, 600-700 pages); documentation search 'code general des impots' -> CGI 2017 mise à jour 2023
  - LF 2024 (Loi 23.0014 du 28 décembre 2023): not on the site; Internet Archive listing of 2023-12/2024-01 uploads has budget reports only
- Files on disk:
  - `law/cgi2023.pdf` (2,444,666 B, sha256 9a31a1c421ae4d66…)
  - `law/lf2025.pdf` (155,079,881 B, sha256 0ca701b9387528cd…)
  - `law/lf2026.pdf` (137,204,726 B, sha256 35708d46b1dcb30e…)
  - `law/lfr2024.pdf` (163,693,881 B, sha256 39fdd1171dd83e88…)
  - `law/lfr2025.pdf` (171,563,074 B, sha256 a9515ee6a8d1dadc…)
