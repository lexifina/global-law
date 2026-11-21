# Fiji (FJ) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar tax year); access tier A; reused patterns: AU/NZ PAYE (annual bands, individual unit), B10 KE (per-person PAYE with monthly contributions).
- Statute read: Income Tax Act 2015 ss 6, 8, 13-15, 21-23, 125 and Income Tax (Rates of Tax and Levies) Regulations 2016 Schedule, Income Tax (Exempt Income) Regulations 2016 Schedule Parts 4-6, FNPF Act 2011 ss 36-39 (Global law, laws.gov.fj consolidation to 2026-10-28); dated with the gazetted texts from laws.gov.fj 'Laws as published' (API /api/show_pdf_lawsaspublished/<id>): Income Tax (Budget Amendment) Acts 2023 (No 5), 2024 (No 5), 2025 (No 9), LN 55 of 2023, LN 12 of 2025, LN 36 of 2025, FNPF (Budget Amendment) Acts 2023, 2024, 2026, FNPF (Amendment) Act 2025, LN 58 of 2024, LN 43 of 2025
- Registry correction: Registry 'Income Tax Act 2015' confirmed; the rates are in the Income Tax (Rates of Tax and Levies) Regulations 2016 Schedule (resident 0/18/20/33/34/35/36/37/38/39 % with 30,000 tax-free; non-resident 20 % from the first dollar); Social Responsibility Tax abolished from 1 January 2024 (Act 5 of 2023); dividends exempt; bank interest 10 % final; FNPF employee 8 % (s 37(4) 18 % x s 39 8/18), not deductible.
- Lean: 166 lines, 16 defs, 6 theorems, 20 #guard checks, 0 sorry; exe `lean/.lake/build/bin/fjtax` (worldMain).
- Unsupported (listed in the outputs): presumptive income tax and business deductions; CGT exemptions of s 67; pension exemptions beyond FNPF/approved funds; wages paid evenly over 12 months.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: fiji/national/acts (current-only consolidation to 2026-10-28): ITA 2015, Rates Regulations 2016, Exempt Income Regulations, FNPF Act 2011, ECAL Act 2015 (Parts 2-4 not in force in the record)
  - laws.gov.fj: the Angular site's API (https://www.laws.gov.fj/api, from its main bundle): /toc_lawsaspublished lists every gazetted act and legal notice by year; /show_pdf_lawsaspublished/<id> returns the gazette PDF (base64); 14 texts fetched (tools/fjlap.py)
  - the consolidation link Global law gives (laws.gov.fj/acts/DisplayAct/2669) answers 404 to scripts (SPA route)
- Files on disk:
  - `law/act11_2024_fnpf.pdf` (501,913 B, sha256 458dc83611701ef5…)
  - `law/act13_2023_fnpf.pdf` (477,438 B, sha256 d547d056ba42a9f3…)
  - `law/act14_2026_ita_budget.pdf` (425,099 B, sha256 d5b7d0514764e196…)
  - `law/act1_2026_ita.pdf` (475,837 B, sha256 fdb5cedc06b19c33…)
  - `law/act21_2026_fnpf.pdf` (380,130 B, sha256 f28cf7faa12e58f4…)
  - `law/act23_2025_fnpf.pdf` (234,889 B, sha256 5a8c0cb69bc6a3a7…)
  - `law/act5_2023_ita_budget.pdf` (656,475 B, sha256 274b2e599681ba35…)
  - `law/act5_2024_ita_budget.pdf` (506,298 B, sha256 04868244f4cbcd10…)
  - `law/act9_2025_ita_budget.pdf` (283,465 B, sha256 bfb489a7b96e7464…)
  - `law/laws_as_published_toc.json` (808,854 B, sha256 d9e38cc9c951376c…)
  - `law/ln12_2025_exempt.pdf` (164,037 B, sha256 09534435ac79feb6…)
  - `law/ln36_2025_rates.pdf` (535,475 B, sha256 cf6cd64ba9291153…)
  - `law/ln43_2025_fnpf_regs.pdf` (118,344 B, sha256 e80f37aab49caf5c…)
  - `law/ln55_2023_rates.pdf` (146,657 B, sha256 413c61a7f15c16e6…)
  - `law/ln58_2024_fnpf_regs.pdf` (462,185 B, sha256 ebc72ba68efa9117…)
