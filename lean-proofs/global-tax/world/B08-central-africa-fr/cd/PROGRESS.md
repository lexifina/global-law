# DR Congo (CD) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: kernel Schedule + cap.
- Statute read: Ordonnance-loi 69/009 arts. 47, 48, 50, 84, 85, 88, 89, 90 as in the DGI 'Code des impôts mis à jour au 10 juillet 2023' (dgi.gouv.cd); Loi 23/053 du 30 novembre 2023 (IS and IRPP reform; JO numéro spécial 29 décembre 2023, dgi.gouv.cd copy, OCR) art. 153: in force 24 months after 31 December 2023, i.e. from 2026
- Registry correction: Registry 'schedular, IPR on remunerations' confirmed for 2025: IPR 3/15/30/40 % (1.944 M / 21.6 M / 43.2 M), total capped at 30 % of the income, less 2 % per dependant (max 9), minimum 2 000 FC a month; the IRPP of Loi 23/053 applies from 2026.
- Lean: 97 lines, 11 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/cdtax` (worldMain).
- Unsupported (listed in the outputs): employee CNSS (input cnssEmployee); impôt mobilier, rents, gains; immune housing/transport allowances; finance laws 2024 and 2025.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: dr-congo corpus = labour code, criminal procedure, public-agent conduct code, constitution
  - dgi.gouv.cd: 'Code des impôts' -> CODE-DES-IMPOTS-2023.pdf; IPR leaflet; 'Arrêtés, Décrets & Lois' (ordonnances-lois, scanned); loi-is-et-Irpp.pdf (Loi 23/052-23/053, scanned, OCR)
  - Finance laws 2024 and 2025: not on dgi.gouv.cd (CDX listing of uploads checked)
- Files on disk:
  - `law/CODE-DES-IMPOTS-2023.pdf` (3,147,312 B, sha256 23713ec47640b9e7…)
  - `law/IPR.pdf` (783,228 B, sha256 51b3f4f1a1362885…)
  - `law/O.L-REFORMES-S.pdf` (296,818 B, sha256 af2818b74d0f4069…)
  - `law/loi-is-irpp.pdf` (2,931,692 B, sha256 912180f40cb264b2…)
  - `law/ord-loi-001.pdf` (6,309,824 B, sha256 01fa7c61458c2761…)
  - `law/ord-loi-002.pdf` (831,892 B, sha256 16a176a6b26cd225…)
  - `law/ord-loi-003.pdf` (2,275,508 B, sha256 5573a0cc908088a0…)
  - `law/ord-loi-004.pdf` (5,571,265 B, sha256 2bacc32ac500d067…)
  - `law/ord-loi-006.pdf` (847,113 B, sha256 b282cd87010eaae6…)
- 2026-11-20 W5 review: see FINDINGS W5-1.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNSS worker 5 % of remuneration (pensions branch, no ceiling), deducted (CGI art. 50); input cnssEmployee still overrides. Provision: Décret n° 18/041 du 24 novembre 2018 fixant les taux de cotisations dues à la CNSS, art. 3 (10 % = 5 % + 5 %), art. 10 (transitional 3,5 % only to 1 January 2019); Loi 16/009 du 15 juillet 2016 arts. 13, 16, 18 (Leganet copies via the Internet Archive). Rebuilt (#guards pass), check `w5/pa/check.py CD` 0 / 300 differ with the switch off, rescanned (`scan_world.py CD`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
