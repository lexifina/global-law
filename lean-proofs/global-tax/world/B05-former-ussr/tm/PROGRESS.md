# Turkmenistan (TM) progress

**Status (2026-11-20T03:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: UZ, KZ.
- Statute read: Tax Code of Turkmenistan (new edition), consolidated Russian text on mejlis.gov.tm (amendments to the Law of 12 April 2025) arts. 172, 185, 187, 188, 192, 193; Code on social protection (mejlis.gov.tm) on contributions.
- Registry correction: Registry 'flat' confirmed: 10 % (art. 192(1)); a monthly deduction of one 'base value for taxes and fees' per person and per dependant whose 2025 amount is set outside the Code (not reached: law.minjust.gov.tm needs a login); dividends 15 %; no compulsory employee contribution.
- Lean: 78 lines, 7 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tmtax` (worldMain).
- Unsupported (listed in the outputs): base-value deduction (amount not reached); simplified regime for entrepreneurs; entry-into-force dates of the 2025 amendments.
- Steps: 1 model done; 2 validation: statute's own printed sums and hand cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (generic scanners via world/tools/scan_world.py where a cited scale exists); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Sources on disk:
  - `law/mejlis_code10_taxcode_20261120.html` (1,084,940 B, sha256 5f853c0e47d1f051…)
  - `law/mejlis_code10_taxcode_20261120.txt` (893,286 B, sha256 754787d7f03e65e6…)
  - `law/tm_pit_181_199.txt` (85,340 B, sha256 3e2a6f2e619b156d…)
