# Suriname (SR) progress

**Status (2026-11-20T07:27Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (belastingjaar); access tier B; reused patterns: NL (Dutch-heritage wage/income tax: forfaitaire aftrek, schijven).
- Statute read: Wet Inkomstenbelasting 1922 (consolidation 'laatstelijk gewijzigd bij S.B. 2024 no. 3', belastingdienst.sr) arts. 18, 31, 34, 34a, 34c, 52f, 52g, 52h; Staatsbesluit 11 January 2024 (S.B. 2024 no. 2) on Wet Loonbelasting arts. 12-14, 17a
- Registry correction: Registry 'Wet Inkomstenbelasting 1922; Wet Loonbelasting' confirmed: zero band 108,000; 8/18/28/38 % to 150,000/192,000/234,000/above (art. 34, S.B. 2024 no. 2); wage costs 4 % up to 4,800; individual assessment with deductions to the higher-income spouse (art. 31).
- Lean: 81 lines, 6 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/srtax` (worldMain).
- Unsupported (listed in the outputs): AOV and health-insurance contributions not reached; 2025 staatsbesluit (if any) not reached; investment income (dividendbelasting).
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law suriname corpus (8 acts, no tax law)
  - belastingdienst.sr (403 from lean1; read from the laptop)
  - sris.sr (406 from lean1)
  - dna.sr (bills only)
  - not opened (referee values): loonbelasting tables and handleidingen
- Files on disk:
  - `law/SB-2024-no-2-Staatsbesluit-art18a-Wet-Loonbelasting.pdf` (139,552 B, sha256 6fb55d1d19734e03…)
  - `law/Wet-Inkomstenbelasting.pdf` (309,046 B, sha256 f38a43d14a59054e…)
  - `law/dna.html` (74,181 B, sha256 3ca09bc1bb83e090…)

- 2026-11-20 W5 pattern A (contributions agent): AOV premium 4 % of zuiver loon for residents under 60; not deductible (IB art. 18 (1) (b), art. 8 (2) (a)). Provision: Wet AOV (S.B. 1981 no. 30 as amended to S.B. 2002 no. 96) arts. 19-20. Rebuilt (#guards pass), check `w5/pa/check.py SR` 0 / 300 differ with the switch off, rescanned (`scan_world.py SR`).
