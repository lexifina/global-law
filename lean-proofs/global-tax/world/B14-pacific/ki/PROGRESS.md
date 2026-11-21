# Kiribati (KI) progress

**Status (2026-11-20T07:14Z): unsupported.**

- Year: 2025; access tier C; reused patterns: -.
- Statute read: only the Laws of the Gilbert Islands Revised Edition 1977, Cap. 44 Income Tax (archived PacLII copy) and PacLII's list of income-tax amendment acts to 2009
- Registry correction: Registry 'Income Tax Act': no 2025 text reached (Global law holds only the 1979 Independence Order).
- Lean: tier-C stub exe `lean/.lake/build/bin/kitax` (every household: unsupported 'no accessible statute').
- Unsupported (listed in the outputs): no accessible statute.
- What would unlock it: a current consolidation of Kiribati's Income Tax Act and the Kiribati Provident Fund Act (Kiribati legislation site or PacLII past its challenge).
- Tried / sources:
  - Global law: kiribati corpus (legislation.gov.uk) holds the 1979 Order only
  - paclii.org: challenge (not bypassed); Internet Archive: Cap. 44 (1977 edition, ki/legis/consol_act/ita116.pdf, capture 2025-04-04) and amendment-act titles 1980-2009 (ita1990116, ita2009196 ...)
  - kiribatilaws.gov.ki: no answer from lean1 or the laptop
- Files on disk:
  - `law/paclii_ki_ita116.pdf` (1,793,868 B, sha256 0aa00ae7852eb8e4…)

## Rescue pass (2026-11-20T11:52Z, rescue agent; log ~/cmp20/world/RESCUE.md)

Outcome: still unsupported (access C). Routes tried:
- tax.gov.ki (Kiribati Tax Office, found via mfed.gov.ki 'TAXATION'): WordPress media library (all pages) holds forms, the VAT Act 2013 and VAT regulations, return instructions and pamphlets; no Income Tax Act; an 'Income Tax' page exists (official secondary, not a statute)
- kiribatilaws.gov.ki: no answer
- What would unlock it: a current consolidation of the Income Tax Act (only the 1977 Cap. 44 is on hand)

## Rescue pass 2 (2026-11-20T13:11Z, rescue2 agent; log ~/cmp20/world/RESCUE.md, Pass 2)

Outcome: still unsupported (access C). Routes tried (laptop and lean1):
- kiribatilaws.gov.ki: no answer from the laptop; tax.gov.ki WordPress media search 'income tax': return forms and instructions only
- parliament.gov.ki (laptop): 'Acts' page embeds phocadownload categories 19-22 (Acts passed 2022-2025) whose plugin tag is not rendered; the category URLs answer 404 live; Wayback copies of the 2024 and 2025 category pages list five acts per page (none on income tax on the first page)
- Wayback CDX of parliament.gov.ki: Income Tax (Amendment) Acts 1994, 1996, 1997 (x2), 2009 and an 'Income Tax Act (No 9) amendment of s7' (2021 upload); acts of 2013-2025 incompletely archived, so the 2025 law cannot be shown complete
- legis-palop.org (PALOP+TL legal database): full texts need a paid subscription and login (free registration gives listings only); its search form posts redirect to the home page without a session: not used (login)
- natlex.ilo.org, www.fao.org/faolex, www.refworld.org: Cloudflare 'Sorry, you have been blocked' (403) from the laptop and WebFetch: not bypassed
- droit-afrique.com: live site 403 ('Server unable to read htaccess file'); its tax codes are sold in a shop (Wayback: only the free 'sommaire')
- Global law list_jurisdictions (rescue2/tools/gl.py, 2026-11-20): no tax law in this country's corpus
- WIPO Lex country profile (www.wipo.int/wipolex/en/members/profile/<CC>): no tax law listed (except SY, GM: see below)
- What would unlock it: a consolidated Income Tax Act (Cap. 44) as amended to 2025, or the complete list of income tax amendments since 2009

