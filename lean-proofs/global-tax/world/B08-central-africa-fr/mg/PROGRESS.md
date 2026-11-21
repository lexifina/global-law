# Madagascar (MG) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: kernel monthly perPeriod pattern.
- Statute read: Code des impôts 'mis à jour suivant la LFI 2025' (impots.mg 'Codes et Manuels', fetched from the laptop) arts. 01.03.02-01.03.19 (IRSA), 01.04.04 (IRCM); CDI LFI 2026 compared (adds a 25 % band above 4 M from 2026)
- Registry correction: Registry 'progressive, individual, IRSA' confirmed: monthly IRSA 0/5/10/15/20 % (350 000 / 400 000 / 500 000 / 600 000), base rounded down to 100 Ar, minimum Ar 3 000 a month, Ar 2 000 a month per dependant above 350 000; pension (10 %) and health (2 %) contributions deductible; IRCM 20 %.
- Lean: 103 lines, 11 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/mgtax` (worldMain).
- Unsupported (listed in the outputs): CNaPS / health contributions (rates not reached; input cnapsEmployee); dividends, rents, gains (IR, IRI); students 21-25 and ascendants as dependants.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: madagascar corpus = labour code, constitution, family law (no tax law)
  - impots.mg (laptop only; no answer from lean1) 'explorer?path=/legislation/Codes et Manuels': CDI LFI 2025, CDI LFI 2026
  - cnaps.mg: no contribution rates published on the home page
- Files on disk:
  - `law/cdi_lfi2025.pdf` (2,617,314 B, sha256 1de82ef9d4a405e2…)
  - `law/cdi_lfi2026.pdf` (2,788,548 B, sha256 d542ae2d3c3f5648…)

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNaPS worker 1 % of wages up to 8 x SME (Ar 2 101 440 a month in 2025), deducted within the 10 % pension limit (art. 01.03.09 1°); input cnapsEmployee still overrides. Provision: Code de prévoyance sociale art. 37 (8 x SME of category M1; CNaPS copy); rate from the CNaPS "Taux des cotisations" page (2011 capture: Général 13 % / 1 %), SME 262 680 (1 Mar 2024 - 28 Feb 2026) from the CNaPS SME table: official secondary. Rebuilt (#guards pass), check `w5/pa/check.py MG` 0 / 300 differ with the switch off, rescanned (`scan_world.py MG`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
