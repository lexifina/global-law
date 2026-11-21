# Sierra Leone (SL) progress

**Status (2026-11-20T06:19Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025 (calendar year of assessment); access tier A; reused patterns: UK/IE PAYE.
- Statute read: Income Tax Act 2000 as amended to Finance Act 2017 (NRA compilation) s. 4, s. 38, First Schedule; Finance Act 2019 s. 11; Finance Act 2020 s. 21 (scan, OCR checked on the page image); Finance Acts 2021-2026 (no change to Part I); Redenomination of the Leone Regulations 2024 (S.I. 4 of 2024) regs. 1, 2, 3(6), 10(3), 14
- Registry correction: Registry 'Income Tax Act 2000' confirmed: resident individuals 0/15/20/25/30 % (Finance Act 2020: 7.2 M / 14.4 M / 21.6 M / 28.8 M old leones = NLe 7,200 / 14,400 / 21,600 / 28,800); currency now SLE (new leone).
- Lean: 83 lines, 7 defs, 5 theorems, 1 #guard checks, 0 sorry; exe `lean/.lake/build/bin/sltax` (worldMain).
- Unsupported (listed in the outputs): NASSIT contribution (Act not reached; input); allowance exemptions; investment income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: SierraLII corpus (7 acts) has no tax law
  - nra.gov.sl answers the laptop, not lean1: files pushed through the hop
  - sierralii.gov.sl act pages 403 to scripts: Internet Archive copy of the Redenomination Regulations
  - NASSIT site not reachable
- Files on disk:
  - `law/2019_Finance_Act_1_8136241a71.pdf` (128,125 B, sha256 958a244f85af1cb1…)
  - `law/Finance_Act_2018_1_b96b9c2841.pdf` (54,714 B, sha256 a8a4a98eae248227…)
  - `law/Finance_Act_2020_d8deee2366.pdf` (9,518,346 B, sha256 55de00c4f7b04056…)
  - `law/Finance_Act_2021_be1efb0bcc.pdf` (210,947 B, sha256 f659b25e9d981671…)
  - `law/Income_Tax_Act_2000_as_amended_to_Finance_Act_2017_1_83760e046c.pdf` (900,613 B, sha256 71ab1f1fd46729e7…)
  - `law/The_Finance_Act_2022_e416cfed24.pdf` (432,657 B, sha256 e14de0f623434283…)
  - `law/The_Finance_Act_2023_8629ff7803.pdf` (736,593 B, sha256 dc0eb8a9e8a52d5f…)
  - `law/The_Finance_Act_2024_0d6d83e684.pdf` (3,410,826 B, sha256 5314b7e510cfa9d3…)
  - `law/The_Finance_Act_2025_beb680faed.pdf` (701,135 B, sha256 3e05fc9d932106fc…)
  - `law/The_Finance_Act_2026_121df05d9b.pdf` (960,719 B, sha256 372edaf9bae9bc3f…)
  - `law/redenomination_regs_2024.pdf` (730,069 B, sha256 539b577357fb0e9f…)

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): NASSIT worker 5 % of earnings (no ceiling), deducted (Act s. 20 (2); within ITA s. 38 (2)); input nassitEmployee still overrides. Provision: National Social Security and Insurance Trust Act 2001 (Act No. 5 of 2001) s. 25 (1)-(2), s. 2 "earning", s. 20 (2) (sierra-leone.org scan, OCR). Rebuilt (#guards pass), check `w5/pa/check.py SL` 0 / 300 differ with the switch off, rescanned (`scan_world.py SL`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
