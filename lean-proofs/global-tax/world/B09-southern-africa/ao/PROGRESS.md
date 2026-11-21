# Angola (AO) progress

**Status (2026-11-20T13:10Z): built (access tier B; rescue pass 2, see ~/cmp20/world/RESCUE.md, Pass 2). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: MZ.
- Statute read: Diário da República scans hosted by lex.ao (free database; files.lex.ao PDFs; sha256 in ao/law/rescue2/SOURCE_SHA256_full.txt and SHA256SUMS), OCR (tesseract por) + page images: Lei n.º 18/14 (Código do IRT) arts. 7 (Group A base = pay less compulsory social security), 10 (monthly settlement by the table); Lei n.º 28/20 (DR I Série n.º 109, 22 Jul 2020) art. 2 (new art. 16 n.º 3: Groups B/C 25 %) and art. 3 (2020 table; also as HTML on angolex.com); Lei n.º 18/24 de 30 de Dezembro (OGE 2025; DR I Série n.º 247; in force 1 Jan 2025) art. 20 n.º 3 + Anexo I 'TABELA DO IRT (Proposta)' (DR p. 13798, read on the page image); Decreto Presidencial n.º 227/18 art. 12 (employee 3 %, employer 8 %) and art. 13 (gross pay base). Cross-checks: OGE 2024 Lei 15/23 art. 20 n.º 3 (same 100,000 Kz exemption), OGE 2026 Lei 14/25 (150,000 Kz from 2026).
- Registry correction: IRT Group A: monthly table of the OGE 2025 (Lei 18/24, Anexo I): exempt to 100,000 Kz, then 13-25 % with fixed amounts; INSS 3 % deducted first (DP 227/18); Group B 25 % (Lei 28/20).
- Lean: 114 lines, 13 defs, 4 theorems, 6 #guard checks, 0 sorry; exe `lean/.lake/build/bin/aotax` (worldMain). Scale: `scale.json`.
- Sources: `law/`, `law/rescue/` and `law/rescue2/` (sha256 in each folder's SHA256SUMS).
- Unsupported: investment income (Imposto sobre a Aplicação de Capitais) and rental income (Imposto Predial): not modelled; pensions: treatment under the CIRT not read; later amendments of DP 227/18: not checked
- Routes tried in rescue pass 2 (UTC 2026-11-20; pass-1 routes below them):
  - lex.ao (Docusaurus site, laptop): sitemap.xml (11,725 documents) -> 116 Assembleia Nacional laws 2021-2025 with their descriptions (an_desc.tsv); OGE laws 32/21, 2/23, 15/23, 18/24, 14/25, Lei 28/20, Lei 18/14 and DP 227/18 downloaded from files.lex.ao (gazette scans); first 30 pages of each OGE law OCR'd on lean1 (rescue2/tools/ocr2.sh, tessdata_fast por)
  - Lei 18/24 Anexo I table unreadable by OCR (graphic table): read on the 110-dpi page image
  - angolex.com (laptop): HTML text of Lei 28/20 (2020 table, superseded) and of the 2014 CIRT; no later IRT amendment listed
  - AGT and imprensanacional.gov.ao: as pass 1 (no answer / 2014 code only)
  - one WebSearch found lex.ao and angolex
- Pass-1 routes (rescue agent):
  - build pass: Global law angola corpus (Constitution only)
  - build pass: AGT portal content API: 234 menu pages, 84 attachments, only Lei 18/14 (2014 CIRT, inactive menu) and IRT forms
  - build pass: Wayback CDX agt.minfin.gov.ao (722 captures)
  - build pass: minfin.gov.ao, parlamento.ao (script shells)
  - build pass: imprensanacional.gov.ao (no answer from lean1 or the laptop)
  - minfin.gov.ao (answers lean1) is an Angular app whose legislation list is served by a Squidex CMS (cms.minfin.gov.ao) through a client id and secret embedded in its JavaScript: not used (a hidden token, outside the rules)
  - agt.minfin.gov.ao, imprensanacional.gov.ao: no answer from lean1
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B09-southern-africa/ao/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py AO`.
