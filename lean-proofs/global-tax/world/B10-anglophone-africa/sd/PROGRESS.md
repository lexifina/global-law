# Sudan (SD) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (assessment year; law of the Government of Sudan); access tier B; reused patterns: UK/IE PAYE.
- Statute read: Income Tax Act 1986 (Ministry of Justice English consolidation as published by the Taxation Chamber, tax.gov.sd, Feb 2025) s. 2, s. 30, Schedule III Sector (B) (amendment note 'Act No. 25, 2013')
- Registry correction: Registry 'Income Tax Act 1986; conflict' confirmed for the Government of Sudan: personal income tax Schedule III Sector (B) 0/5/10/15 % (9,090 / +120 / +240 pounds); the amounts are those of the 2013 amendment as printed; later finance laws not reached.
- Lean: 71 lines, 4 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/sdtax` (worldMain).
- Unsupported (listed in the outputs): finance laws after 2013; Schedule I exemptions and Schedule II deductions; social insurance; Arabic texts (no Arabic OCR).
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: Sudan corpus holds only the Criminal Act 1991
  - sudantax.gov.sd unreachable; tax.gov.sd reachable from the laptop (laws page)
  - Arabic Income Tax Regulations 2021/2022 downloaded: text layer not searchable
- Files on disk:
  - `law/Income-tax.pdf` (1,543,966 B, sha256 ed008d97b27f6008…)
  - `law/The-Income-Tax-Act-1986.pdf` (728,131 B, sha256 77b3ef0223ac3f4d…)
  - `law/income1.pdf` (1,730,974 B, sha256 02252eb18ec00007…)
  - `law/list43-44.pdf` (469,108 B, sha256 5e799f7e2dd36391…)
