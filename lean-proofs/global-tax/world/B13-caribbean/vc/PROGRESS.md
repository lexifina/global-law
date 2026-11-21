# Saint Vincent and the Grenadines (VC) progress

**Status (2026-11-20T07:27Z): unsupported.**

- Year: 2025; access tier C; reused patterns: -.
- Statute read: none reached
- Registry correction: Registry 'Income Tax Act; ECCU' unverified: the House of Assembly's annual lists name the Income Tax Act 2009 and Income Tax (Amendment) Acts No. 5 of 2019 and No. 20 of 2020, but no text was reached.
- Lean: tier-C stub exe `lean/.lake/build/bin/vctax` (every household: unsupported 'no accessible statute').
- Unsupported (listed in the outputs): no accessible statute.
- What would unlock it: the Income Tax Act 2009 (as amended) and the 2019/2020 amending Acts from the Inland Revenue Department or the Attorney General's chambers; NIS contribution regulations
- Tried / sources:
  - Global law saint-vincent-and-the-grenadines corpus (1979 legislation.gov.uk scans)
  - assembly.gov.vc (TLS name mismatch on www; annual lists only)
  - ird.gov.vc (timeout), svgird.com (no DNS), finance.gov.vc (publications: no legislation)
  - Internet Archive CDX (refused)
- Files on disk:
  - `law/vcacts/2019.pdf` (168,461 B, sha256 8e334478d2145e33…)
  - `law/vcacts/Acts-2018.pdf` (184,404 B, sha256 6e02cc8d6d2d8e29…)
  - `law/vcacts/Acts_-_2021.pdf` (54,276 B, sha256 d60573db03671afd…)
  - `law/vcacts/Acts_2020.pdf` (47,543 B, sha256 68dc43eeb370364a…)
  - `law/vcacts/Acts_2022.pdf` (164,665 B, sha256 654d9a4ef2a51604…)
  - `law/vcacts/Acts_2023.pdf` (115,408 B, sha256 bb2aa5b035fa6bf7…)
  - `law/vcacts/Acts_2024.pdf` (39,053 B, sha256 8cf05fc0ce7ddb6c…)
  - `law/vcacts/Acts_2025.pdf` (133,172 B, sha256 39a08dc5e2c58eeb…)

## Rescue pass (2026-11-20T11:52Z, rescue agent; log ~/cmp20/world/RESCUE.md)

Outcome: still unsupported (access C). Routes tried:
- Internet Archive CDX of finance.gov.vc found its 'PDF/Acts' folder; the live site serves Cap. 435 Income Tax Act (Revised Edition 2009, 159 pages, text layer), Income Tax (Amendment) Acts No. 5 of 2019 and No. 20 of 2020 (territorial basis, withholding), and Finance Act No. 10 of 2023 (s. 47(1)(b) allowance raised to 22,000 dollars; Fifth Schedule 'On $10,001 - $30,000' 30 % -> 28 %): saved in vc/law/rescue/ (scans OCR'd)
- House of Assembly annual lists 2010-2025 (live and archived) show a Finance Act every year 2010-2024 amending 'the laws contained in' the Finance Act; their texts (except 2023) were not reached, so the rest of the 2025 Fifth Schedule (first bands, top rate) and allowances cannot be established
- finance.gov.vc and ird.gov.vc 'tax tables' (2018-2024) are withholding tables (referees): Tax_Tables-2024 downloaded, not opened
- What would unlock it: the Finance Acts 2010-2022 and 2024 (or a consolidation of Cap. 435 after 2009); with them the model is a short step from Cap. 435 + Finance Act 2023

## Rescue pass 2 (2026-11-20T13:11Z, rescue2 agent; log ~/cmp20/world/RESCUE.md, Pass 2)

Outcome: still unsupported (access C). Routes tried (laptop and lean1):
- legal.gov.vc (Attorney General's Chambers; found by WebSearch): Official Gazettes 2016-2026 (2024: 72 issues downloaded on the laptop): No. 10 lists S.R.&O. No. 4 of 2024 (Provisional Collection of Taxes Order 2024), No. 11 S.R.&O. No. 6 of 2024, No. 24 Act No. 6 of 2024 (Finance Act 2024): the gazette prints the notices only ('can be purchased at the Government Printing Office'), not the texts
- ird.gov.vc (laptop): legislation page = the same files as pass 1; 'Standard Deduction' page: 2025 25,000, 2024 25,000, 2023 22,000, 2022-2018 20,000 (official secondary; consistent with Finance Act 2023 s. 47(1)(b)); PIT 'current rate' links only to the 2024 tax tables (referee, not opened)
- finance.gov.vc forms: 2021 return form prints the allowances (personal 1,200, spouse 700, child 400, standard deduction 20,000) but no rate schedule; 2023 form 404
- Wayback CDX of finance.gov.vc, ird.gov.vc, assembly.gov.vc, pmoffice.gov.vc, gov.vc: budget addresses (proposals) and annual act lists; no Finance Act 2010-2022 or 2024 text
- two WebSearches: no host of the Finance Acts or a consolidated Fifth Schedule
- Cap. 435 (2009 RE) Fifth Schedule itself prints three conflicting 'Over $45,000' lines (40 %, 32.5 %, 40 % 'with effect from income year 1996'): recorded as a finding
- legis-palop.org (PALOP+TL legal database): full texts need a paid subscription and login (free registration gives listings only); its search form posts redirect to the home page without a session: not used (login)
- natlex.ilo.org, www.fao.org/faolex, www.refworld.org: Cloudflare 'Sorry, you have been blocked' (403) from the laptop and WebFetch: not bypassed
- droit-afrique.com: live site 403 ('Server unable to read htaccess file'); its tax codes are sold in a shop (Wayback: only the free 'sommaire')
- Global law list_jurisdictions (rescue2/tools/gl.py, 2026-11-20): no tax law in this country's corpus
- WIPO Lex country profile (www.wipo.int/wipolex/en/members/profile/<CC>): no tax law listed (except SY, GM: see below)
- What would unlock it: the Finance Acts 2010-2022 and 2024 (or a post-2009 consolidation of Cap. 435) to fix the 2025 Fifth Schedule

