# Somalia (SO) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (Federal Government; Income Tax Law No. 37 of 11 May 2025); access tier A; reused patterns: UK/IE PAYE, kernel Tariff (column form).
- Statute read: Income Tax Law (Sharciga Canshuurta Dakhliga) No. 37 of 11 May 2025 (Ministry of Finance publication, Internet Archive capture 2025-10-01; Somali scan, OCR; table checked on the page image) promulgation arts. 1-2, First Schedule para. 1(1)-(4)
- Registry correction: Registry 'Income tax law (federal); little accessible law; USD widely used' replaced: the Federal Government enacted a new Income Tax Law (No. 37, 11 May 2025) with a resident scale in US dollars: 0 % to $1,200, 6 % to $6,000, 12 % to $18,000, 18 % above (printed fixed amount $1,788 at $18,000); under-18 residents 20 % flat; non-residents 18 % flat.
- Lean: 93 lines, 8 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/sotax` (worldMain).
- Unsupported (listed in the outputs): deductions/exemptions of the Law (Somali OCR) not modelled; Federal Member State and Somaliland taxes; transitional rules for 2025.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: Somalia corpus (provisional constitution, 1962 penal code)
  - mof.gov.so legislation pages (the Revenue Act 2019 page has no file); Internet Archive CDX of mof.gov.so/sites/default/files found Law No. 37 and 'Xeerarka Maaliyadda 2020'
  - no Somali OCR model: tesseract eng reads Somali (Latin script); every number used checked on the page image
- Files on disk:
  - `law/sharciga_cashuurta_dakhliga_37.pdf` (25,364,163 B, sha256 3fbb3fa42e2998c6…)
  - `law/xeerarka_maaliyadda_2020.pdf` (39,434,077 B, sha256 c288016b03963936…)
- 2026-11-20 round D6: First Schedule para. 1(3) (gains on chargeable investment assets, 15 % slice above $18,000) implemented; capitalGains now taxed.
