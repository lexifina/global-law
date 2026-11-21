# Mauritania (MR) progress

**Status (2026-11-20T05:30Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: FR.
- Statute read: Code général des impôts (DGI consolidation of 17/2/2023, archived official copy; CGI of 10/3/2020), arts. 109-115 (ITS); LF 2025 and LFR 2025 checked.
- Registry correction / check: Registry right (ITS, monthly progressive, individual). Detail: monthly bands 15/25/40 % at 9,000 and 21,000 MRU after a 6,000 monthly exemption.
- Lean: 80 lines, 8 defs, 5 theorems, 4 #guard checks, 0 sorry; exe `lean/.lake/build/bin/mrtax` (worldMain).
- Sources (law/):
- `law/cgi2023fr.pdf` sha256 2972be620009381468a05ee21295c8b5b01cdebc15e4a7692c1fcdf861edd71f
- `law/cgi2020fr.pdf` sha256 53ebf34e4d5a5a7c5a3fa82528c0fe36840a005d2f811545d4efaf2e615eac41
- `law/lf2025ar.pdf` sha256 921e1606a46e7ed9a53bca98d762d7041c19c96b3a8ff255dc2b87d9b8e26bf3
- `law/lfr2025ar.pdf` sha256 873d330af26a78970ac0b63f6e0902a9188801ccff16a106f8aee7a22fc8f881
- Unsupported (in every output line): CNSS/CNAM contributions; IBAPP/BIC, IRF, IRCM; 2024 finance laws not verified.
- Scale for the scanners: `scale.json` (statutory threshold, cited).
- Steps: 1 model done; 2 validation: statute's own tables/formulas only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (`Theorems.lean`); 4-5 known/new loopholes: FINDINGS.md (scanner results in `results/search/`, probes in `../logs/probe.json`); 6 government errors: FINDINGS.md; 7 USEFUL.md.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNSS worker 1 % of pay up to 7 000 MRU a month (70 000 old UM), deducted (CGI art. 113 2) a)). Provision: CNSS page "Recouvrement des cotisations" (cnss.mr, Internet Archive capture 2021-08-12; same text on the 2016 page): plafond 70 000 UM a month, 14 % = 1 % worker + 13 % employer; official secondary; old-to-new ouguiya at 10:1 (reading). Rebuilt (#guards pass), check `w5/pa/check.py MR` 0 / 300 differ with the switch off, rescanned (`scan_world.py MR`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
