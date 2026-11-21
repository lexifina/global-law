# Cambodia (KH) progress

**Status (2026-11-20T11:11Z): built (access tier A; rescue pass, see ~/cmp20/world/RESCUE.md). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: MN.
- Statute read: Law on Taxation 2023 (Royal Kram NS/RKM/0523/004 of 16 May 2023; GDT scan, OCR'd with tesseract Khmer and checked on the page images) arts. 41-49 (salary tax: rates 0/5/10/15/20 % art. 47, bands and family reliefs by sub-decree art. 46(2)/47, fringe benefits 20 % art. 48, non-residents 20 % art. 49); Sub-Decree No. 48 ANKr.BK of 11 March 2024 on the monthly taxable salary and annual taxable income bands (GDT sub-decree list, 'Valid'; page image read): monthly bands 0-1.5m 0 %, to 2m 5 %, to 8.5m 10 %, to 12.5m 15 %, above 20 %; reliefs 150,000 riel per child and for a homemaker spouse per month; sole-proprietorship annual bands 0-18m/24m/102m/150m.
- Registry correction: Tax on salary is in the Law on Taxation 2023 (replacing the 1997 Law on Taxation) with the bands and family reliefs in Sub-Decree 48 ANKr.BK (11 March 2024); rates 0-20 % monthly, final withholding.
- Lean: 111 lines, 11 defs, 6 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/khtax` (worldMain). Scale: `scale.json`.
- Sources: `law/` and `law/rescue/` (sha256 in each folder's SHA256SUMS).
- Unsupported: NSSF employee pension contribution (deductible under Law on Taxation 2023 art. 45(1)): not read; employeeSocial = 0; investment income (withholding taxes of the 2023 law) not modelled; pensions: treatment not read
- Routes tried in the rescue pass (UTC 2026-11-20):
  - Khmer OCR: tessdata_best khm.traineddata installed in user space (~/cmp20/world/rescue/tools/tessdata, sha256 3d2d975e...), Law on Taxation 2023 (84 pages) OCR'd: kh/law/law_taxation_2023_khm_ocr.txt; arts. 45-49 checked on the page-22 image
  - tax.gov.kh/en/sub-decree list: Sub-Decree 48 ANKr.BK (11 March 2024) downloaded (gdtstream/1f25fa42-...; kh/law/rescue/sd48.pdf), table read on the page image (the OCR of the table digits was unreliable; the image was read and the OCR'd row edges agree)
  - NSSF contribution rules: not looked for on the GDT site (outside its scope); left unsupported
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B03-asia-east-se/kh/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py KH`.
