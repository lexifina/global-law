# Burundi (BI) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: kernel Schedule (two bands).
- Statute read: Loi n° 1/14 du 24 décembre 2020 modifying the Loi n° 1/02 du 24 janvier 2013 relative aux impôts sur les revenus (archived obr.bi, scanned; OCR checked on the page image) arts. 19, 21, 30-33; Loi de finances 2025/2026 (archived obr.bi 2025-07-23, OCR pp. 1-70): art. 138 restates art. 30, art. 139 amends art. 122 (15 % withholding), no change to arts. 21 and 33
- Registry correction: Registry 'progressive, IPR' corrected: the tax on employment income (cédule 1 with business and rental income, art. 19) is 0 % to 1.8 M, 20 % to 3.6 M, 30 % above (art. 21), on income rounded to the nearest 1 000; employee pension and health contributions and transport (15 %) and housing (60 %) allowances deductible (art. 33); dividends and interest 15 % withholding (art. 122, LF 2025/2026).
- Lean: 94 lines, 9 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/bitax` (worldMain).
- Unsupported (listed in the outputs): employee INSS / health contributions (input inssEmployee); business and rental income; the January-June 2025 finance law (2024/2025).
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: burundi corpus = catalogue entries and treaties (no tax law)
  - obr.bi: application error page; Internet Archive copies of the income-tax laws 2013 and 2020, finance laws 2023/2024 (truncated) and 2025/2026
  - LF 2024/2025: not found in the archive listing of obr.bi/images
- Files on disk:
  - `law/lf2023_24.pdf` (1,048,576 B, sha256 ade4258e4f5a49c5…)
  - `law/lf2023_24_rev.pdf` (1,048,576 B, sha256 9cb4022cfd765da8…)
  - `law/lf2025_26.pdf` (14,893,774 B, sha256 a3b9ab303a34950f…)
  - `law/lf2025_26_mod.pdf` (5,242,880 B, sha256 7a0e4fde6e01abd1…)
  - `law/loi_ir_2013.pdf` (338,333 B, sha256 afe819482c284473…)
  - `law/loi_ir_2020.pdf` (2,174,407 B, sha256 f682bd7f9aa20eea…)
  - `law/om_540_1777.pdf` (688,008 B, sha256 798b64cb24f8dbb4…)
