# Micronesia (Federated States of) (FM) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year); access tier A; reused patterns: US-style wage tax + social security (Compact states).
- Statute read: FSM Code Annotated 2014 (fsmlaw.org, FSM Legal Information System): 54 F.S.M.C. 112, 121, 122, 123, 124, 141; 53 F.S.M.C. 603(15), 901(1)(g); Global law record of FSM public laws (323 laws to 2026-11-03) searched for later amendments (none to these sections); PL 21-145 (2020) read
- Registry correction: Registry 'FSM Code title 54 (wage and salary tax)' confirmed: national tax of 6 % on the first $11,000 and 10 % above on all wages and salaries (no allowance), a $1,000 deduction only below $5,000 of annual wages; social security 7.5 % employee to $9,000 a quarter per employer (2023-2027); businesses pay a gross revenue tax ($80 + 3 % above $10,000) instead.
- Lean: 116 lines, 16 defs, 5 theorems, 7 #guard checks, 0 sorry; exe `lean/.lake/build/bin/fmtax` (worldMain).
- Unsupported (listed in the outputs): self-employed social security; state taxes; investment income (no national tax on an individual's interest or dividends).
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: micronesia/national/acts (FSM LIS, unofficial): 323 public laws, no Code titles 53/54
  - fsmlaw.org: FSM Code 2014 index (fsm/code/indexcode2014.html) and Title 53/54 chapter pages (the older 'updated through PL 12-12 (2001)' pages were discarded)
  - cfsm.gov.fm public-law PDFs: Global law's official links (PL 21-145)
- Files on disk:
  - `law/T53_Ch06_2014.html` (39,435 B, sha256 3f70a042a86878f1…)
  - `law/T53_Ch09_2014.html` (9,257 B, sha256 b94581b17b99cd45…)
  - `law/T54_Ch01_SubChpII_2014.html` (80,567 B, sha256 b0556df4e7f4933c…)
  - `law/T54_Ch01_SubChpI_2014.html` (80,628 B, sha256 0d183eabfe084700…)
