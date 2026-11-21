# Gabon (GA) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: FR (family quotient), kernel quotient, Tariff.SubRow.
- Statute read: CGI 2025 (dgi.ga 'Code général des impôts 2025') arts. 73-77, 90-95, 109-110, 168-175, 346-351; CNAMGS employee rate and ceiling from cnamgs.ga 'Paiement des cotisations' (archived 2025-08-15; official secondary: Décret 0022 art. 38 not reached)
- Registry correction: Registry 'progressive, family quotient' confirmed: joint return of the 'chef de famille' (art. 75), parts 1 / 2 / + 1/2 per child up to six children (art. 170), no cap on the quotient's advantage, tariff per part 0-35 % (art. 174); base after social contributions, the TCS and 20 % frais capped at 10 M; TCS 5 % above 150 000 a month; RCM 20 % final.
- Lean: 141 lines, 18 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/gatax` (worldMain).
- Unsupported (listed in the outputs): employee CNSS pension contribution (rate not reached; input cnssEmployee); self-employment, rents, gains; children aged 18-28 in studies.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: gabon corpus = civil code, penal code, constitution (no tax law)
  - dgi.ga 'Documents' > 'Code général des impôts 2025' (PDF with text)
  - cnss.ga: no contribution rates on the employer page; cnamgs.ga 'Paiement des cotisations' (live and archived 2025-08-15)
- Files on disk:
  - `law/cgi2025.pdf` (2,019,005 B, sha256 69fdb3d87ede508e…)
  - `law/cnamgs_cotisations_20261120.html` (166,137 B, sha256 7965c033a34cdc05…)
  - `law/cnamgs_cotisations_wb20250815.html` (160,310 B, sha256 d098c444f979ce5d…)
