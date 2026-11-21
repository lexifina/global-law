# Ethiopia (ET) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025/26 (Ethiopian fiscal year 2018 E.C., from 8 July 2025); access tier A; reused patterns: DJ (B08: monthly final tax), UK/IE PAYE.
- Statute read: Federal Income Tax Proclamation 979/2016 (Global law, as enacted) arts. 11 (replaced), 12, 65; Income Tax (Amendment) Proclamation 1395/2025 (Federal Negarit Gazette No. 64, MoR website API) art. 1(6) (new art. 11), art. 4 (effective dates); Private Organization Employees' Pension Proclamation 1268/2022 art. 10 (Global law)
- Registry correction: Registry 'Proclamation 979/2016; schedule A' updated: Proclamation 1395/2025 replaced art. 11 from 8 July 2025 (0 % to 2,000 birr a month, 15/20/25/30/35 %, top from 14,000); employee pension 7 % (not deductible), employer 11 % (exempt up to 15 %).
- Lean: 86 lines, 8 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/ettax` (worldMain).
- Unsupported (listed in the outputs): regional employment tax; public servants' pension; Schedules B-D.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: Ethiopia corpus holds Proclamation 979/2016 as enacted (no amendments) and the pension proclamations
  - mor.gov.et (laptop only) website-api/domestic-proclamations -> PDFs of 979/2016 and 1395/2025
  - hopr.gov.et reachable (not needed)
- Files on disk:
  - `law/mor_proc_1395.pdf` (1,199,975 B, sha256 aab1118b602dc387…)
  - `law/mor_proc_979.pdf` (936,011 B, sha256 29e01d8decc53e39…)
