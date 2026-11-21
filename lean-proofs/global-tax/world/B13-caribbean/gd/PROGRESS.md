# Grenada (GD) progress

**Status (2026-11-20T07:27Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (year of assessment); access tier A; reused patterns: UK/IE PAYE, LC (this batch).
- Statute read: Income Tax Act Cap. 149, 2010 Continuous Revised Edition (laws.gov.gd PDF 2016) ss. 13, 42A, 56, 128, Fifth Schedule; S.R.O. 1 of 2014, S.R.O. 2 of 2017, S.R.O. 25 of 2018 (Income Tax (Amendment) Orders); Income Tax (Amendment) Acts 15/2012, 41/2013, 22/2014, 12/2015, 27/2015, 43/2015, 8/2016, 1/2017 read; National Insurance (Collection of Contributions) (Amendment) Regulations S.R.O. 38/2019, 19/2020, 52/2020, 8/2023, 43/2023
- Registry correction: Registry 'Income Tax Act' identified as Cap. 149: deduction 36,000 (s. 42A as amended by S.R.O. 1 of 2014); 10 % on the first 24,000 of chargeable income and 28 % above (S.R.O.s 1/2014, 2/2017, 25/2018); NI employee 6 % in 2025 to 5,200 a month (S.R.O. 43 of 2023), nil from age 60.
- Lean: 87 lines, 7 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/gdtax` (worldMain).
- Unsupported (listed in the outputs): investment income; exempt pension income (Act 1 of 2017); self-employed NI.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law grenada corpus (7 old acts)
  - laws.gov.gd (406 from lean1; read from the laptop: chapters, acts and S.R.O. listings by year)
  - ird.gov.gd (TLS name mismatch)
  - not opened (referee values): IRD PAYE tables
- Files on disk:
  - `law/Cap149_Income_Tax_Act_lawsgovgd.pdf` (733,298 B, sha256 6c0ddb7be452ece3…)
  - `law/acts/1565-act-no-6-of-2025-tax-administration-post-hurricane-beryl-fiscal-support-special-measures-act-2025.pdf` (457,372 B, sha256 b5e8bf485cdf9042…)
  - `law/acts/657-act-no-11-of-2011-national-insurance-amendment-act.pdf` (292,787 B, sha256 32d1b47f7573a1ce…)
  - `law/acts/689-act-no-15-of-2012-income-tax-amendment.pdf` (309,109 B, sha256 4ca0c9c3f8d8a64c…)
  - `law/acts/745-act-no-41-of-2013-income-tax-amendment.pdf` (238,133 B, sha256 0c931e89fd203a47…)
  - `law/acts/768-act-no-22-of-2014-income-tax-amendment-act.pdf` (599,745 B, sha256 da69a3bc90ccb2ad…)
  - `law/acts/803-act-no-12-of-2015-income-tax-amendment.pdf` (44,798 B, sha256 cec74f8ba29afb64…)
  - `law/acts/818-act-no-27-of-2015-income-tax-amendment.pdf` (341,985 B, sha256 720d7d108a2b51c7…)
  - `law/acts/834-act-no-43-of-2015-income-tax-amendment-no-3-act.pdf` (291,703 B, sha256 36ba8fbca3074742…)
  - `law/acts/842-act-no-8-of-2016-income-tax-amendment.pdf` (278,716 B, sha256 041894329334769e…)
  - `law/acts/871-act-1-of-2017-income-tax-amendment.pdf` (357,190 B, sha256 48599590844e7e2b…)
  - `law/acts/899-act-29-of-2017-national-insurance-amendment-act.pdf` (374,177 B, sha256 334538a3a79ca701…)
  - `law/acts/976-act-no-6-of-2023-national-insurance-amendment.pdf` (242,909 B, sha256 9afda902931b7dab…)
  - `law/acts/977-act-no-7-of-2023-national-insurance-amendment-no-2.pdf` (304,346 B, sha256 2064d6ccbc534927…)
  - `law/sro/120-sr-o-1-of-income-tax-amend-order-2014.pdf` (356,849 B, sha256 fd3e6a4df36223e6…)
  - `law/sro/252-sr-o-26-of-2016-income-tax-amendment-act-commencment-order.pdf` (188,291 B, sha256 7c67c4727dce03a0…)
  - `law/sro/298-sr-o-2-of-2017-income-tax-amendment-order.pdf` (209,935 B, sha256 99ae7e80f35cd620…)
  - `law/sro/363-sr-o-25-of-2018-income-tax-amendment-order-1.pdf` (232,547 B, sha256 2453dd03d60cbc30…)
  - `law/sro/402-sr-o-38-of-2019-national-insurance-collection-of-contributions-amendment-regulations-2019.pdf` (243,121 B, sha256 abef318480170b60…)
  - `law/sro/422-sr-o-19-of-2020-national-insurance-collection-of-contributions-amendment-regulations-2020.pdf` (245,619 B, sha256 f0edbaab6ca94c09…)
  - `law/sro/455-sr-o-52-of-2020-national-insurance-collection-of-contributions.pdf` (334,050 B, sha256 a33daae40c952bc0…)
  - `law/sro/598-sr-o-8-of-2023-national-insurance-collection-of-contributions-amendment-regulations.pdf` (168,138 B, sha256 8aecc02de9ae6905…)
  - `law/sro/633-sr-o-43-of-2023-national-insurance-collection-of-contributions-amendment-no-2-regulations-2023.pdf` (203,719 B, sha256 e4e1f4dfd9d6c43c…)
