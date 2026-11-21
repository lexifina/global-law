# Russia (RU) progress

**Status (2026-11-20T01:50Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: EE, LV, LT.
- Statute read: Tax Code part two ch. 23 as amended by Federal Law 176-FZ of 12.07.2024 (kremlin.ru acts bank, official text) art. 2 items 28 and 36, in force 2025-01-01 (art. 8 (2)); Federal Law 330-FZ of 21.11.2011 (Global law) for the first-child amount and the deduction's month rule.
- Registry correction: Registry 'progressive scale from 2025' confirmed: five bands 13/15/18/20/22 % on the main base, 13/15 % on the investment base (art. 224 (1), (1.1)).
- Lean: 93 lines, 9 defs, 5 theorems, 2 #guard checks, 0 sorry; exe `lean/.lake/build/bin/rutax` (worldMain).
- Sources: `law/` (every file with its sha256 in the Lean docstrings).
- Unsupported (in every output line): interest (art. 214.2); pensions (art. 217); employer-paid insurance contributions.
- Steps: 1 model done; 2 validation: statute's own tables/examples only (#guard) — referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 known/new loopholes: FINDINGS.md (B02 scan; the harness scanners need an average wage that world countries lack, see KERNEL_REQUESTS); 6 government errors: FINDINGS.md; 7 USEFUL.md.
