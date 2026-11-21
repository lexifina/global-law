# Morocco (MA) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: FR.
- Statute read: Code général des impôts 2025 (DGI consolidation, archived official copy), arts. 59, 73, 74; LF n° 60-24 art. 8 III-12°.
- Registry correction / check: Registry right (progressive, individual). Detail: 0-37 % in six bands from 2025; professional expenses 35 %/25 % with a 78,000 threshold; family reduction 500 per dependant, max 3,000.
- Lean: 90 lines, 8 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/matax` (worldMain).
- Sources (law/):
- `law/cgi2025fr.pdf` sha256 f510cca73c15fea490d6d515854f89766555ed756831ef260f2dae8eb9f2fe75
- Unsupported (in every output line): CNSS/AMO/pension contributions (art. 59-II, III); pensions, rents, capital income; self-employment.
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.
- 2026-11-20 round D6: pensions modelled (art. 60-I abatement 70 % / 40 %; 2025 50 % reduction for basic-scheme pensions, LF 60-24 art. 8-III-8°).
- 2026-11-20 round D7: pension residual traced to art. 59 III/IV contributions deducted before the art. 60-I abatement; rates not in the CGI; no change.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNSS employee 0,52 % + 3,96 % on wages up to 6 000 MAD a month and AMO 2,26 % on the whole wage, all deducted (CGI art. 59-II-A, III). Provision: CNSS page "Paiement de vos cotisations sociales", section "Barèmes et taux de cotisation" (Internet Archive capture 2025-03-25) and notice "AMO Ajustement des taux de cotisation" (AMO 2,26 % from 1 January 2016); official secondary (décret 2-01-2723 as amended and the AMO décrets not reached); CGI 2025 art. 59. Rebuilt (#guards pass), check `w5/pa/check.py MA` 0 / 300 differ with the switch off, rescanned (`scan_world.py MA`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
