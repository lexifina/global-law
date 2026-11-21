# Belarus (BY) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: RU, LT.
- Statute read: Tax Code (Special Part) 71-З, official consolidated text on pravo.by as archived 2025-06-14 (amendments to Law 47-З of 13.12.2024) arts. 208, 209, 214; Global law corpus empty.
- Registry correction: Registry 'flat' corrected: 13 % with 25 % on wages + dividends + service contracts above 220 000 rubles a year (art. 214(8), from 2025); standard deduction 192 a month only if the month's income is at most 1 164 (notch); child deductions 56 / 107. The employee's 1 % pension contribution (Law 138-XIII) was not reached.
- Lean: 98 lines, 14 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/bytax` (worldMain).
- Unsupported (listed in the outputs): employee 1 % pension contribution (Law 138-XIII not reached); rent fixed sums; dividend 6 %/0 % rates; capital-gain exemptions.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/a208_2025.txt` (90,622 B, sha256 d669d0e48d1a796c…)
  - `law/a214_2025.txt` (11,417 B, sha256 5b00293f7ba39093…)
  - `law/eta_hk0200166.html` (1,683,761 B, sha256 f901873e7ec4470e…)
  - `law/eta_hk0200166.txt` (1,112,059 B, sha256 aaa99d4363d2e9a9…)
  - `law/eta_hk0900071.html` (823,329 B, sha256 0948dd4205d774c2…)
  - `law/eta_hk0900071.txt` (112,851 B, sha256 4226c85dab1dffc9…)
  - `law/eta_hk1800159.html` (516,574 B, sha256 8b1b903da3bf9b83…)
  - `law/eta_hk1800159.txt` (112,049 B, sha256 ecfa1d3d784dbae4…)
  - `law/fszn.html` (536,776 B, sha256 574851a7e3370030…)
  - `law/fszn.txt` (117,133 B, sha256 4429d2bc6589ebe6…)
  - `law/fszn_old.html` (536,776 B, sha256 b461a0bb651c04f4…)
  - `law/fszn_old.txt` (117,133 B, sha256 4429d2bc6589ebe6…)
  - `law/fszn_p.html` (4,757 B, sha256 d163f7ed2320ae8a…)
  - `law/fszn_v19600138.html` (4,757 B, sha256 d163f7ed2320ae8a…)
  - `law/pravo_hk0900071_20261120.html` (5,167,289 B, sha256 e9aadd601f234c88…)
  - `law/pravo_tc_sp_20261120.txt` (4,166,904 B, sha256 ec31dbe3f0f35eb1…)
  - `law/pravo_tc_sp_wb20250614.txt` (4,029,612 B, sha256 422106e8c25bb218…)
  - `law/pravo_wb20250614.html` (4,985,659 B, sha256 0eb8e2f0b9358388…)
  - `law/t.html` (5,942,090 B, sha256 95e0404a6e10590e…)
  - `law/t.txt` (4,296,245 B, sha256 3d6bc3f3029109c3…)
