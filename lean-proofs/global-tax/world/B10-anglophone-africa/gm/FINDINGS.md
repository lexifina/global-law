# The Gambia (GM) findings, B10-anglophone-africa (2026-11-20T06:19Z)

Built from the statute only (no referee values seen). Scanner leads: `results/search/SUMMARY.md` (scale: `scale.json`, a statutory band threshold, so 1 'AW' there is that amount, not an average wage).

### F1 The Gambia Revenue Authority's two 2018 brochures give different zero bands: D36,000 for employment income, D24,000 for personal income tax
- kind: gov-error
- GRA 'Employment Income Tax (PAYE)' brochure: 'The employment income tax rates as at January 2018 ... D0.00 - D36,000 0% ... Above D76,000 25%'; GRA 'Personal Income Tax' brochure: 'as at 2018 ... D0 - D24,000 0% ... Above D64,000 25%'. Both refer to the Income and Value Added Tax Act 2012; whether the Act sets different scales for employees and other individuals could not be checked (Act not reached). The brochures are seven years old; 2025 rates are in Finance Acts not reached.
- provisions: Income and VAT Act 2012 (not reached); GRA brochures
- Lean: -
- status: recorded (not modelled)

## Step 4: known ways of paying less tax that the statute makes visible (catalogue, recreated blind?)

| # | way | model / scanners | where in the statute |
|---|---|---|---|

## Step 5: what was searched

- GRA downloads page (gra.gm/downloads): brochures and forms only
- National Assembly documents (assembly.gm/documents?search=income|finance): Income and Sales Tax Amendment Acts 2007/2010, the 2012 Act's arrangement pages, no Finance Act

## Literature not checked (no web-search budget this session)

- OECD/ATAF/AUC 'Revenue Statistics in Africa' country notes (KE UG RW GH ET among the covered countries)
- IMF Article IV and technical-assistance reports (tax policy diagnostics) for each country
- African Tax Administration Forum (ATAF) and East African Community harmonisation papers on PAYE and social contributions
- Big-four worldwide personal tax guides (EY, PwC, KPMG, Deloitte) for each country
- Academic work on PAYE design, minimum contributions and informal-sector presumptive taxes in anglophone Africa
- ICTD / UNU-WIDER working papers (UNU-WIDER refuses scripts; SOUTHMOD not verifiable)

Novelty: every finding above is reported as 'not found in the statute texts and official pages read for this country (listed in PROGRESS.md)'; none of the literature above was searched, so none is claimed new.

### R1 Rescue pass 2026-11-20T11:52Z: no dated text reached
- kind: access
- gra.gm downloads list: 'Income Tax Table 2025' (gra.gm/download-file/2a69ec11-...) is a 695-page withholding table, i.e. a referee value: downloaded to gm/law/rescue/gra_income_tax_table_2025_UNOPENED_referee.pdf and NOT opened (reserved for the datasets phase) | the Income and Value Added Tax Act 2012 text and the Finance Acts setting 2025 rates: not on gra.gm or assembly.gm (arrangement pages only, as before)
- would unlock: the IVAT Act 2012 text and the Finance Acts 2018-2025 (rates schedule)
- status: unsupported

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

<!-- L1-VERIFICATION BEGIN -->

## Verification (L1 loophole round, Africa / Middle East, 2026-11-20)

Every finding above re-checked on the current model (post-W5 exe; Lean sources newer than the exe were rebuilt) and, where the text is on disk, against the statute (file:line under this folder). Scanner leads come from the L1 rescan (`results/search/SUMMARY.md`, 2026-11-20 22:44 CET). Statuses as in `report/CROSS38.md`: confirmed (guard or theorem plus the statute re-read), explained, lead, withdrawn. G: = a Verify.lean guard; T: = a theorem or #guard already in the model; S: = statute text re-read.

| ID | status | evidence |
|---|---|---|
| F1 | lead | Two GRA brochures with different zero bands (D36,000 employment vs D24,000 personal): the IVAT Act 2012 was not reached, so whether this is a rule set outside the law cannot be settled. |
| R1, rescue 2 | explained | Tier-C stub; not scanned (zero model, no cited scale). |

<!-- L1-VERIFICATION END -->
