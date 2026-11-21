# Tonga (TO) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025/26 (fiscal year 1 July 2025 - 30 June 2026); access tier B; reused patterns: AU/NZ PAYE (annual bands).
- Statute read: Income Tax Act (Cap. 11.05, 2020 Revised Edition) ss 2, 5, 13, 19, 21, 35 (ago.gov.to; point-in-time list 2025-07-01); Income Tax (Amendment) Act 2020 (Act 12 of 2020); Income Tax (Amendment) Order 2017 (revenue.gov.to, laptop only); National Retirement Benefits Fund Act (Cap. 8.08) Second Schedule
- Registry correction: Registry 'Income Tax Act 2007' confirmed (Cap. 11.05); the rates are not in the Act but in a Ministerial Order under s 5(1): Income Tax (Amendment) Order 2017, 0 % to 10,000, 10 % to 30,000, 20 % to 60,000, 25 % above; fiscal year ending 30 June; NRBF employee 5 % (not deductible); dividends exempt.
- Lean: 99 lines, 7 defs, 5 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/totax` (worldMain).
- Unsupported (listed in the outputs): interest withholding; small business tax; public-service Retirement Fund contributions; later rate Orders (none listed by the Ministry).
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: tonga corpus holds the Constitution and Criminal Offences Act only
  - ago.gov.to: point-in-time POST (pointintime=2025-07-01, submit4=<letter>) lists acts and regulations in force, with history tables; Orders are not indexed
  - revenue.gov.to answers the laptop but not lean1: Income Tax (Amendment) Order 2017 fetched from the laptop and pushed (sha256 988387ec...)
- Files on disk:
  - `law/IncomeTaxAct_3.pdf` (1,130,183 B, sha256 7f5de851f0b188f7…)
  - `law/IncomeTaxAmendmentAct2020.pdf` (425,038 B, sha256 3b38499ad0e65dcf…)
  - `law/IncomeTaxAmendmentOrder2017_English.pdf` (290,524 B, sha256 988387ec2c0de258…)
  - `law/IncomeTaxRegulations_3.pdf` (418,171 B, sha256 a2bf1666e4d37c4f…)
  - `law/NationalRetirementBenefitsFundAct_3.pdf` (708,027 B, sha256 b3b36cb9027a8ac5…)
  - `law/b14to_I.html` (145,703 B, sha256 ebc44ab770a30aa7…)
  - `law/b14to_N.html` (154,403 B, sha256 9556937ff9e01751…)
  - `law/b14to_R.html` (252,025 B, sha256 d04672ea464b9fa8…)
  - `law/b14to_subI.html` (49,488 B, sha256 f124eee9e1f91ed2…)

- 2026-11-20 D9 review: the 1 July 2021 PAYE worksheet grid (123 / 1,056 dev) shows the model's 2017 rates are out of date (Ministry notice: 0 / 10 / 15 / 20 / 25 % with bands 12,000 / 30,000 / 50,000 / 70,000); the rate Order's text was not found (the gazetted "Income Tax (Amendment) Order 2021" is the World Bank employees exemption). OPEN model gap: FINDINGS D9M-1; model unchanged. world/IMPROVE_D9.md.
