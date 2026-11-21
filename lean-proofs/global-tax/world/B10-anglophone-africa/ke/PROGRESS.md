# Kenya (KE) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year of income); access tier A; reused patterns: UK/IE PAYE (annual bands, personal relief), NG (B02: per-person PAYE).
- Statute read: Income Tax Act (Cap. 470) Kenya Law consolidations 2024-12-27 (truncated archive capture), 2025-07-01 and 2026-01-01 (Internet Archive copies of new.kenyalaw.org; kenyalaw.org answers scripts with an AWS WAF challenge, not bypassed): s. 15(2)(ac),(ad),(ae), s. 15(3)(b), s. 22(8), s. 22A, s. 30, s. 45 (repealed), Third Schedule Heads A and B; Tax Laws (Amendment) Act 2024 (No. 12 of 2024, commencement 27 Dec 2024) ss. 7, 8, 16; Finance Act 2025 (No. 9 of 2025) ss. 1, 30; NSSF Act 2013 (No. 45 of 2013, version 2022-12-31) s. 2, s. 20, Third Schedule; Affordable Housing Act 2024 (No. 2 of 2024) s. 4; Social Health Insurance Act 2023 (No. 16 of 2023) s. 27; Social Health Insurance Regulations 2024 (L.N. 49 of 2024, versions 2024-03-08 and 2025-02-28) reg. 17
- Registry correction: Registry 'Income Tax Act (Cap. 470); personal relief; SHIF, NSSF, housing levy' confirmed: individual taxation (s. 45 repealed by Act 4 of 2023), annual bands 10/25/30/32.5/35 % (288,000 / 388,000 / 6,000,000 / 9,600,000), personal relief 28,800; since 27 Dec 2024 SHIF (2.75 %, min 300 a month) and the Affordable Housing Levy (1.5 %) are deductible (s. 15(2)(ac),(ae)), NSSF (6 % to the UEL) deductible as a registered-fund contribution (s. 22(8), s. 22A cap 360,000).
- Lean: 132 lines, 17 defs, 5 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/ketax` (worldMain).
- Unsupported (listed in the outputs): NSSF Tier II (UEL = 2 x KNBS National Average Earnings not reached; input nssfUEL); insurance relief, mortgage interest, post-retirement medical fund (need inputs); investment, rental and business income; wages assumed paid evenly over 12 months.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: Kenya corpus holds the Tax Procedures Act, KRA Act and 7 others, not the Income Tax Act
  - kenyalaw.org legislation listing (works) -> act pages answer an AWS WAF challenge (202, empty) from lean1 and the laptop: not bypassed; Internet Archive copies used
  - nssf.or.ke: Act page, no contribution table; KNBS National Average Earnings not reached
  - not opened (referee values): KRA PAYE calculators and tables
- Files on disk:
  - `law/aha2024.html` (272,844 B, sha256 2adc97980954152c…)
  - `law/fa2025.html` (33,667 B, sha256 39af33204ccf1d81…)
  - `law/fa2025.pdf` (817,849 B, sha256 2b2c8b8b032dc125…)
  - `law/ita_2024-12-27.html` (1,048,576 B, sha256 e4d6a1354d08ecc0…)
  - `law/ita_2025-07-01.html` (1,462,530 B, sha256 01489cc5b3562e7e…)
  - `law/ita_2026-01-01.html` (1,467,086 B, sha256 0ac3b159293bd9e5…)
  - `law/nssf2013.html` (353,428 B, sha256 2e968d814fbd44fb…)
  - `law/nssf_clarification.html` (65,688 B, sha256 5abe3552080ebe6d…)
  - `law/shi_regs_2024-03-08.html` (345,041 B, sha256 fbce01c587db73c6…)
  - `law/shi_regs_2025-02-28.html` (398,601 B, sha256 104dd5526b745a8e…)
  - `law/shia2023.html` (271,135 B, sha256 91de9e0165a15e0b…)
  - `law/tla2024.html` (36,627 B, sha256 72aa06592c30c313…)
  - `law/tla2024.pdf` (662,106 B, sha256 ceb065b74fe330a9…)

- 2026-11-20 W5 pattern A (contributions agent 2): NSSF Tier II: default year-3 Upper Earnings Limit KES 72,000 a month (2 x NAE 36,000) when nssfUEL is not given. Provision: NSSF Act 2013 s. 20 (1) (b), Third Schedule (year 3 UEL = 2 x NAE); NSSF notices "Year 2 contribution rates, 2024" (UEL 36,000 = 1 x NAE) and "Year 4 (2026)" (UEL 108,000 = 3 x NAE), official secondary; the year-3 notice itself not found. Rebuilt (#guards pass), check `w5/pa/check.py KE` 0 / 300 differ with the switch off, rescanned (`scan_world.py KE`).

- 2026-11-20 W5 pattern A follow-up (contributions agent 2): NSSF contribution period: January 2025 at year-2 limits (LEL 7,000, UEL 36,000), February-December at year 3 (LEL 8,000, UEL 72,000), with the switch on. Provision: NSSF Act 2013 Third Schedule; NSSF Year 4 notice (18 Feb 2026): "the implementation of Year 3 contribution rates ended on 31st January, 2026" (reviewer 3 pass 3 row 127; gaa.go.ke copy `law/w5/nssf_year4_notice_gaa.pdf`); NSSF year-2 notice (UEL 36,000). Rebuilt, check 0 / 300 with the switch off, rescanned.
