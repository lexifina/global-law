# Samoa (WS) progress

**Status (2026-11-20T07:14Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar tax year); access tier A; reused patterns: AU/NZ PAYE, B08/B10 final per-period withholding.
- Statute read: Income Tax Act 2012 ss 2, 9, 24, 59-61 and Schedules 1-2; National Provident Fund Act 1972 s 22; Accident Compensation Act 1989 s 52 (MJCA official versions as at 31 December 2024)
- Registry correction: Registry 'Income Tax Act 2012' confirmed: wages bear a final fortnightly salary and wage income tax (0 % to 576, 20 % to 962, 27 % above, per fortnight); other income at the annual 0/20/27 % (15,000/25,000) scale stacked on wages (s 9(6)); NPF employee 10 %, ACC levy 1 %; dividends from resident companies exempt.
- Lean: 120 lines, 12 defs, 6 theorems, 5 #guard checks, 0 sorry; exe `lean/.lake/build/bin/wstax` (worldMain).
- Unsupported (listed in the outputs): interest withholding; capital gains tax (holding period); 26-fortnight assumption.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: samoa corpus is metadata-only (MJCA catalogue, no text)
  - MJCA Firebase storage (the official link Global law gives): object listing ?prefix=legislation%2F and alt=media downloads of the Income Tax Act 2012, NPF Act 1972, ACC Act 1989 (official versions as at 31 December 2024)
- Files on disk:
  - `law/Accident_Compensation_Act_1989.pdf` (697,555 B, sha256 d2e864c85f63191f…)
  - `law/Income_Tax_Act_2012.pdf` (1,168,338 B, sha256 baef05164ac391c6…)
  - `law/National_Provident_Fund_Act_1972.pdf` (672,006 B, sha256 956fff33729d163d…)
  - `law/mjca_legislation_list.json` (34,183 B, sha256 f1d3916b0f72c614…)
