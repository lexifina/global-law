# The Gambia (GM) progress

**Status (2026-11-20T06:19Z): unsupported.**

- Year: 2025; access tier C; reused patterns: -.
- Statute read: Income and Value Added Tax Act 2012: only its arrangement pages reached (National Assembly document 158, five page images); GRA brochures (official secondary, 'as at January 2018' / 'as at 2018') read but not used
- Registry correction: Registry 'Income and Value Added Tax Act 2012' unverified for 2025: the Act's text and the Finance Acts that set the 2025 rates were not reached.
- Lean: tier-C stub exe `lean/.lake/build/bin/gmtax` (every household: unsupported 'no accessible statute').
- Unsupported (listed in the outputs): no accessible statute.
- What would unlock it: the full text of the Income and Value Added Tax Act 2012 and the Finance Acts 2018-2025 (rates schedule), e.g. on assembly.gm or gra.gm; the SSHFC Act 2015 (scan downloaded and OCR'd) for contributions
- Tried / sources:
  - Global law: gambia corpus (constitution only)
  - gra.gm downloads (PAYE and PIT brochures dated 2018)
  - assembly.gm documents: IVAT Act 2012 = five one-page images (contents); SSHFC Act 2015 (50-page scan)
  - mofea.gm unreachable; Internet Archive CDX of gra.gm (brochures only)
  - note: the PAYE brochure contains a worked example (a referee value); it was seen while checking the brochure's date and is not used
- Files on disk:
  - `law/gra_8d0ccc58-d217-11ed-9b31-029254d29bb1.pdf` (165,101 B, sha256 289fde30ed14f89f…)
  - `law/gra_8d0cd78a-d217-11ed-9b31-029254d29bb1.pdf` (133,964 B, sha256 f81f51d46f2475c7…)
  - `law/ivat2012_part31.pdf` (199,927 B, sha256 70dec09140ee9d84…)
  - `law/ivat2012_part32.pdf` (209,458 B, sha256 21471c7e10b259c0…)
  - `law/ivat2012_part33.pdf` (300,490 B, sha256 95784c90fe9b5916…)
  - `law/ivat2012_part34.pdf` (319,927 B, sha256 f70fa55e91f05a15…)
  - `law/ivat2012_part35.pdf` (350,098 B, sha256 fe9587c2dd8eb263…)
  - `law/sshfc2015.pdf` (20,134,427 B, sha256 216738a6590a8bde…)

## Rescue pass (2026-11-20T11:52Z, rescue agent; log ~/cmp20/world/RESCUE.md)

Outcome: still unsupported (access C). Routes tried:
- gra.gm downloads list: 'Income Tax Table 2025' (gra.gm/download-file/2a69ec11-...) is a 695-page withholding table, i.e. a referee value: downloaded to gm/law/rescue/gra_income_tax_table_2025_UNOPENED_referee.pdf and NOT opened (reserved for the datasets phase)
- the Income and Value Added Tax Act 2012 text and the Finance Acts setting 2025 rates: not on gra.gm or assembly.gm (arrangement pages only, as before)
- What would unlock it: the IVAT Act 2012 text and the Finance Acts 2018-2025 (rates schedule)

## Rescue pass 2 (2026-11-20T13:11Z, rescue2 agent; log ~/cmp20/world/RESCUE.md, Pass 2)

Outcome: still unsupported (access C). Routes tried (laptop and lean1):
- gra.gm downloads page (laptop, 55 files listed with titles): forms, 2023 brochures (PIT, PAYE, capital gains, rental, informal sector, VAT), Stamp Act, Customs & Excise Act and Regulations, strategic plans, 'Income Tax Table 2025' (the referee, not opened); no Income and VAT Act 2012 or Finance Act
- assembly.gm documents/type/acts (pages 1-6): Income and Value Added Tax Act 2012 = document 158 (contents images only, as pass 1); Income and Sales Tax amendment acts 2007/2010; no Finance Act
- one WebSearch: no host of the 2012 Act's text (WIPO Lex holds the 2004 Income and Sales Tax Act only)
- legis-palop.org (PALOP+TL legal database): full texts need a paid subscription and login (free registration gives listings only); its search form posts redirect to the home page without a session: not used (login)
- natlex.ilo.org, www.fao.org/faolex, www.refworld.org: Cloudflare 'Sorry, you have been blocked' (403) from the laptop and WebFetch: not bypassed
- droit-afrique.com: live site 403 ('Server unable to read htaccess file'); its tax codes are sold in a shop (Wayback: only the free 'sommaire')
- Global law list_jurisdictions (rescue2/tools/gl.py, 2026-11-20): no tax law in this country's corpus
- WIPO Lex country profile (www.wipo.int/wipolex/en/members/profile/<CC>): no tax law listed (except SY, GM: see below)
- What would unlock it: the Income and Value Added Tax Act 2012 (First Schedule) and the Finance Acts to 2025

