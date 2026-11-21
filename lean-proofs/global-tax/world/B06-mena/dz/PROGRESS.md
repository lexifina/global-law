# Algeria (DZ) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier A; reused patterns: FR.
- Statute read: CIDTA art. 104 as rewritten by LF 2022 (loi 21-16) art. 31, LF 2023 (loi 22-24) art. 5, LF 2025 (loi 24-08) art. 8 (JORADP French edition).
- Registry correction / check: Registry right (progressive IRG). Detail: 0/23/27/30/33/35 % barème from LF 2022; salaries monthly with a 40 % abatement (1,000-1,500 DA/month), exemption up to 30,000 DA/month and a smoothing formula to 35,000.
- Lean: 96 lines, 11 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/dztax` (worldMain).
- Sources (law/):
- `law/jo/F2021100.pdf` sha256 884c2d7d98c03f0b4d39664fde2961c420ea55d70ee731d18375c399b4c24436
- `law/jo/F2022089.pdf` sha256 0ad2298a51f9a7129d469fdb97e15bbb4bf54fd19c03edef8d615f77cf88b8b8
- `law/jo/F2023086.pdf` sha256 b7d03bc0b7fbd13554dc7cec527379c3a6c0f13391368a71f72c26fe44cd8faa
- `law/jo/F2024084.pdf` sha256 d0da2a51d5375e4ebe15e7aa6faf99b9606039c307feb5a7f8758a1431cf2ba1
- Unsupported (in every output line): CNAS employee contributions (deducted before IRG; not modelled); rents above 1.8 M credited against the barème (modelled as barème); capital income; disabled workers' formula.
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNAS worker 9 % of the contribution base (no ceiling), reported; NOT deducted from the IRG base (CIDTA not reached). Provision: Décret exécutif n° 06-339 du 25 septembre 2006 modifiant le décret exécutif n° 94-187 (JO n° 60 of 27 September 2006, p. 16), arts. 1-2 (worker 9 % = 1,5 + 6,75 + 0,5 + 0,25, from 1 October 2006). Rebuilt (#guards pass), check `w5/pa/check.py DZ` 0 / 300 differ with the switch off, rescanned (`scan_world.py DZ`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
