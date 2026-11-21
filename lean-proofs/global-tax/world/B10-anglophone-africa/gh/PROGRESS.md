# Ghana (GH) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year of assessment); access tier A; reused patterns: UK/IE PAYE (reliefs), NG (B02).
- Statute read: Income Tax Act 2015 (Act 896, GRA scan, OCR) s. 4 (employment income incl. retirement contributions), s. 51, ss. 94-96, Fifth Schedule, interpretation ('currency point'); Act 1111 (Income Tax (Amendment) (No. 2) Act 2023, Parliament repository, OCR checked on the page image); Act 1094 (2023); Act 1134 (2025); Acts 1071 and 2021 (OCR); GRA notice on Act 1178 (2026); National Pensions Act 2008 (Act 766) ss. 3, 63, 89 (Global law)
- Registry correction: Registry 'Income Tax Act 2015 (Act 896); SSNIT' confirmed: individual taxation; resident bands for 2024-2025 by Act 1111 (0/5/10/17.5/25/30/35 %); Fifth Schedule reliefs in cedis; SSNIT employee 5.5 % exempt (Act 766 s. 89). Act 896 itself is in the GRA's scan, not in Global law's corpus.
- Lean: 121 lines, 13 defs, 6 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/ghtax` (worldMain).
- Unsupported (listed in the outputs): disability and dependant-relative reliefs; education relief needs input childrenInSchool; investment and rental income; any later amendment of Act 766 (insurable-earnings ceiling).
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: Ghana corpus (GhaLII) has amending Acts 902-973 and Act 766 but not Act 896 itself
  - gra.gov.gh/acts (Act 896 scan, Acts 1071, 1094, 2021 amendment, GRA notice Act 1178)
  - repository.parliament.gh DSpace API (Acts 1111, 1134)
  - ghalii.org act pages 403 to scripts
  - not opened (referee values): GRA PIT calculator
- Files on disk:
  - `law/Amendments-To-The-Income-Tax-2015-Act-896_Updated-1.pdf` (299,002 B, sha256 fdd3f8179f3d8d75…)
  - `law/GROWTH-AND-SUSTAINABILITY-LEVY-ACT-2023-ACT-1095.pdf` (2,086,188 B, sha256 786886fff33649b9…)
  - `law/INCOME-TAX-ACT-2015-ACT-896.pdf` (15,115,430 B, sha256 9a3f9c91702e01ea…)
  - `law/INCOME-TAX-AMENDMENT-ACT-2021.pdf` (857,993 B, sha256 97e6ee2c26655908…)
  - `law/INCOME-TAX-AMENDMENT-ACT-2023-ACT-1094.pdf` (4,711,394 B, sha256 26ba452ebf63d609…)
  - `law/Income-Tax-amendment-No-2-Act-2021-Act-1071.pdf` (1,000,861 B, sha256 917e895a4b3c0376…)
  - `law/act1111_1.pdf` (848,291 B, sha256 6591aea459035e03…)
  - `law/act2025_1.pdf` (2,279,340 B, sha256 f42f2c05313fc0e1…)
