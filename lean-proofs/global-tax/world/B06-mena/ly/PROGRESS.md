# Libya (LY) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: UK.
- Statute read: Income Tax Law No. 7 of 2010 (arts. 35, 36, 55, 57, 58, 61, 62), Jihad Tax Law 44/1970, Social Solidarity Fund Law 20/1428 as amended by Law 10/1430, social security Law 1/1991 and decision 182/1991, as compiled in the Tax Authority's 2016 encyclopaedia (scanned).
- Registry correction / check: Registry right (schedular): a separate tax on work income 5 %/10 % after 1,800/2,400 + 300 per child; plus the 1970 Jihad tax (1-3 % of the whole salary) and 1 % solidarity contribution.
- Lean: 93 lines, 10 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/lytax` (worldMain).
- Sources (law/):
- `law/m2016.pdf` sha256 2bbd8962f6d55ac6a2f7306b36e8e99dc80b4a7e25a210c50c7cd0f35d4338e0
- Unsupported (in every output line): trade, craft, professional income; post-2016 amendments; Jihad tax status in 2025; pension income tax.
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.
