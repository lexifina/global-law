# Papua New Guinea (PG) progress

**Status (2026-11-20T13:10Z): built (access tier A; rescue pass 2, see ~/cmp20/world/RESCUE.md, Pass 2). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: FJ, SB.
- Statute read: Certified prints on the National Parliament's legislation service (parliament.gov.pg 'Acts and Legislation' -> public REST /wp-json/parliament-pg/v1/get-bills -> pdis.parliament.gov.pg/uploads/<uuid>; pg/law/rescue2/, sha256 in SHA256SUMS; scans OCR'd and checked on page images): Income Tax (Salary or Wages Tax)(Rates)(2024 Budget)(Amendment) Act 2023 (No. 25 of 2023; Sch. 1 Part 7 Table 1, residents, '1 January 2024 and onwards': 0 to K20,000; 30 % to K33,000; 35 % to K70,000; 40 % to K250,000; 42 % above); Income Tax (Salary or Wages Tax)(Rates)(2025 Budget)(Amendment) Act 2024 (No. 18 of 2024; non-residents' Table 2A only, s. 1(2A), 1(5)); Income Tax (2025 Budget)(Amendment) Act 2024 (No. 16) and Income Tax (Amendment) Act 2024 (No. 23) (no rate change); Income Tax Act 2025 (in operation 1 January 2026). Structure: Income Tax (Salary or Wages Tax)(Rates) Act 1979 s. 1 (PacLII consolidation, Wayback 20241027) and ITA 1959 s. 65J (pass-1 file).
- Registry correction: Salary or wages tax (final for salary-only residents): Rates Act 1979 Sch. 1 Part 7 Table 1 (2024 Budget amendment): 0/30/35/40/42 % with a K20,000 tax-free band; unchanged for residents in 2025; new Income Tax Act 2025 from 2026.
- Lean: 72 lines, 5 defs, 4 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/pgtax` (worldMain). Scale: `scale.json`.
- Sources: `law/`, `law/rescue/` and `law/rescue2/` (sha256 in each folder's SHA256SUMS).
- Unsupported: superannuation employee contribution: not read; non-salary income (resident general rates, Schedule 1 of the Income Tax, Dividend (Withholding) Tax and Interest (Withholding) Tax Rates Act): not read; pensions: ITA s. 29 exemptions not modelled
- Routes tried in rescue pass 2 (UTC 2026-11-20; pass-1 routes below them):
  - parliament.gov.pg (laptop) 'Acts and Legislation' is a React app; its bundle calls the public WordPress route /wp-json/parliament-pg/v1/get-bills (no key; the page's anonymous nonce not used), which proxies pdis.parliament.gov.pg: 550 certified acts with PDF links, all 55 pages listed (pg/law/rescue2/pdis_bills.json)
  - PacLII still a Cloudflare challenge (not bypassed); its Rates Act 1979 consolidation read from a Wayback capture (20241027212335 rtf, 20241223021710 html) for s. 1 only
  - irc.gov.pg: not used (its calculator is a referee)
- Pass-1 routes (rescue agent):
  - irc.gov.pg (answers the laptop) is a Vue app; its route list has a salary-tax calculator (a referee) and CMS pages loaded by lazy chunks that did not load by script (302): not pursued further
  - PacLII still behind a challenge (not bypassed)
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B14-pacific/pg/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py PG`.
