# Rwanda (RW) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar tax period); access tier A; reused patterns: UK/IE PAYE, DJ (B08: monthly final withholding).
- Statute read: Law n° 027/2022 (O.G. n° Special of 28/10/2022) arts. 15, 16, 56, entry into force; Law n° 051/2023; Law n° 014/2025; Presidential Order n° 086/01 of 12/12/2024 art. 1; P.O. n° 009/01 of 10/05/2016 (repealed); Law n° 05/2015 art. 8 (amategeko.gov.rw API)
- Registry correction: Registry 'Law 027/2022 on income tax' confirmed: employment income taxed monthly at 0/10/20/30 % (60,000 / 100,000 / 200,000 a month; Table 2, from the second year after 28/10/2022); employee pension 6 % from 1 Jan 2025 (12 % shared equally), not deductible.
- Lean: 78 lines, 7 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/rwtax` (worldMain).
- Unsupported (listed in the outputs): maternity leave and CBHI contributions; annual declaration rules; investment, rental and business income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: Rwanda corpus holds the Constitution and a few acts, not tax law
  - amategeko.gov.rw search API (documents/search?name=...) and documents-files/<id> -> file_url (official gazette PDFs)
  - rra.gov.rw (JS application): not used
- Files on disk:
  - `law/law014_2025.json` (4,112 B, sha256 f6347bb2e655b50d…)
  - `law/law014_2025.pdf` (275,716 B, sha256 b9ae2622b4b506cb…)
  - `law/law027_2022.json` (3,763 B, sha256 4036c98ba21ae198…)
  - `law/law027_2022.pdf` (2,243,335 B, sha256 e125a5a89e70601e…)
  - `law/law051_2023.json` (3,808 B, sha256 0530edf4bd9ce3c0…)
  - `law/law051_2023.pdf` (553,959 B, sha256 94d3ad64b465d2e8…)
  - `law/law05_2015.json` (3,591 B, sha256 34a6ad24a5db05b4…)
  - `law/law05_2015.pdf` (970,675 B, sha256 0f4808661161cf92…)
  - `law/po009_2016_pension.json` (3,737 B, sha256 7fe28272a268abe6…)
  - `law/po009_2016_pension.pdf` (365,451 B, sha256 de2ff09bf57f4cd8…)
  - `law/po086_2024_pension.json` (4,631 B, sha256 601ca4db0b71b74b…)
  - `law/po086_2024_pension.pdf` (693,677 B, sha256 8eb2f49317f18673…)

- 2026-11-20 W5 pattern A (contributions agent): maternity leave 0.3 % of gross salary and CBHI 0.5 % of net salary (gross - PAYE - pension - maternity); not deductible. Provision: Law 003/2016 art. 7; P.M.O. 105/03 of 30/09/2020 art. 5 (replaced only from 23/02/2026 by P.M.O. 001/03 of 2026, same rate). Rebuilt (#guards pass), check `w5/pa/check.py RW` 0 / 300 differ with the switch off, rescanned (`scan_world.py RW`).
