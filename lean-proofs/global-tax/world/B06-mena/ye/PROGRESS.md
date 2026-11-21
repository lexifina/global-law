# Yemen (YE) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: UK.
- Statute read: Income Tax Law No. 17 of 2010 (English translation published by the Tax Authority at tax.gov.ye, Sana'a), arts. 49, 50, 62, 66, 67; Law No. 8 of 2020 (Sana'a).
- Registry correction / check: Registry partly right: progressive (10/15/20 % after 120,000) but schedular in structure (payroll tax, profits taxes each with the art. 62 scale); 'divided authorities' confirmed (Law 8/2020 issued in Sana'a by the Supreme Political Council).
- Lean: 73 lines, 7 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/yetax` (worldMain).
- Sources (law/):
- `law/itl17_en.pdf` sha256 f15a682277ccfa68bdbfec1c0d780726a45ee6d748940506c8b3a7abb5125a54
- `law/law8_2020.html` sha256 ad65a4780299f2db77ffdc518c1ca7b0fd63c5c50ca19dad6821d4747d19083e
- Unsupported (in every output line): pension contributions (art. 49 (a)); Law 8/2020 small-enterprise exemption; real-estate revenue tax, interest, dividends.
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.
