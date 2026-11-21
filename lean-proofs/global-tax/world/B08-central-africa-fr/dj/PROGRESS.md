# Djibouti (DJ) progress

**Status (2026-11-20T04:05Z): built (step 1 of the world testing order). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: kernel monthly perPeriod pattern.
- Statute read: CGI art. 15 as rewritten by Loi de finances 142/AN/21/8ème L (2022) art. 7 (journalofficiel.dj); earlier wording LF 111/AN/20/8ème L (2021) art. 6; finance laws 2022R-2026 checked for changes to art. 15 (none)
- Registry correction: Registry 'progressive, ITS' confirmed: monthly ITS 2/12/15/22/25/30/35/45 % (30 000 / 50 000 / 150 000 / 300 000 / 600 000 / 1 M / 2 M) since 2022; the CGI's base articles (1-14) were not reached.
- Lean: 82 lines, 6 defs, 5 theorems, 3 #guard checks, 0 sorry; exe `lean/.lake/build/bin/djtax` (worldMain).
- Unsupported (listed in the outputs): CGI arts. 1-14 (base, deductions, exemptions) not reached; CNSS employee (input reported); business, capital income.
- Steps: 1 model done; 2 validation: statute's own printed figures and hand-computed statutory cases only (#guard); referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean: monotone, convex, no jump, splitting <= separate); 4-5 loopholes: FINDINGS.md (catalogue + generic scanners, scan_world.py with the cited scale.json); 6 statute faults / government errors: FINDINGS.md; 7 USEFUL.md.
- Tried / sources:
  - Global law: djibouti corpus = civil, commerce, family, labour, penal codes, constitution (no CGI)
  - journalofficiel.dj: issue pages and 'texte-juridique' pages of finance laws 2017-2026 (live); the site search returns nothing for tax terms
  - economie.gouv.dj, impots.dj, cnss.dj: no answer
- Files on disk:
  - `law/lf2025.html` (159,803 B, sha256 e28df048c1fb3a1f…)
  - `law/lf_n-45-an-23.html` (132,660 B, sha256 3a9c9fbf3110bc24…)
  - `law/lf_n-64-an-23.html` (169,854 B, sha256 a6b0c549d7574cc7…)
  - `law/lf_n-69-an-19.html` (160,393 B, sha256 fede453bc70a698e…)
  - `law/lf_n111-an-20.html` (182,095 B, sha256 a448c90c0e22961d…)
  - `law/lf_n129-an-24.html` (129,775 B, sha256 8f2e4b10c141b6f1…)
  - `law/lf_n138-an-21.html` (145,410 B, sha256 666008305d143300…)
  - `law/lf_n142-an-21.html` (193,294 B, sha256 a03bd86d1fb81cf2…)
  - `law/lf_n169-an-22.html` (157,333 B, sha256 88405d595d278f2e…)
  - `law/lf_n181-an-22.html` (174,491 B, sha256 9252177173915005…)
  - `law/lf_n189-an-85.html` (118,922 B, sha256 154e1e8fdbb37629…)
  - `law/lf_n203-an-25.html` (160,248 B, sha256 70f5cf4d60c76e5e…)
  - `law/lf_n205-an-17.html` (138,344 B, sha256 f731f14772264c54…)
  - `law/lf_n34-an-18.html` (165,919 B, sha256 ac5f56db2958c211…)
  - `law/lf_n62-an-19.html` (154,045 B, sha256 04f2d955e6bdd8df…)
  - `law/lf_n89-an-20.html` (147,495 B, sha256 19e95de0d5f9bd03…)

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNSS salarié 4 % retraite + 2 % soins = 6 % of all remuneration, reported, not deducted (CGI arts. 1-14 not reached); input cnssEmployee still overrides. Provision: CNSS page "Déclaration et versement des cotisations" (cnss.dj, published 04/12/2016, Internet Archive capture 2024-07-13); official secondary. The same page also calls the soins contributions employer-only; the specific 5 % / 2 % sentence is followed. Rebuilt (#guards pass), check `w5/pa/check.py DJ` 0 / 300 differ with the switch off, rescanned (`scan_world.py DJ`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
