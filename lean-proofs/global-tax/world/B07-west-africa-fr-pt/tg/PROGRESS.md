# Togo (TG) progress

**Status (2026-11-20T13:10Z): built (access tier B; rescue pass 2, see ~/cmp20/world/RESCUE.md, Pass 2). Next: open-source software (coordinator, TESTING.md), then datasets.**

- Year: 2025; access tier B; reused patterns: CI, SN.
- Statute read: Code général des impôts & Livre des procédures fiscales 2025, 'mis à jour par la Direction de la Législation Fiscale et du Contentieux' (Office Togolais des Recettes, otr.tg document 600; Internet Archive capture 20251211205452 of otr.tg/index.php/fr/impots/reglementations-fiscales/code-general-des-impots/600-code-general-des-impots-livre-des-procedures-fiscales-mis-a-jour-2025/file.html; 361 pages, text layer; sha256 7d0df3af53833e47266f4b77cf134ac3acb14bb3e8049d1bf92ac2438be4f4c3; tg/law/rescue2/otr_cgi_lpf_2025.pdf): arts. 5-6 (family unit, separate taxation), 23-3 and 27 (pensions), 26 (net employment income, 28 % flat deduction on the fraction up to 10,000,000), 72-73 (dependants, 10,000 FCFA a month each, max 6), 74 (barème 0/3/10/15/20/25/30/35 %, base rounded down to 1,000, tax to 10; read on the page image p. 40), 78 (business income 30 %), 79-80 (13 % final withholding). Cross-checks: PLF 2024 art. 16 (tg/src/PLF-2024.pdf p. 17: same art. 74 wording), PLF 2025 art. 17 and LF 2026 art. 21 article lists (no change to arts. 5-6, 23, 26-27, 72-80).
- Registry correction: IRPP under the CGI of 2018 (Loi n° 2018-024) as amended; employment income: 28 % flat deduction (to 10 M), 10,000 FCFA a month per dependant (max 6), annual barème 0-35 % in eight bands (art. 74 as rewritten by the 2024 finance law per the OTR consolidation); spouses taxed separately.
- Lean: 157 lines, 21 defs, 5 theorems, 8 #guard checks, 0 sorry; exe `lean/.lake/build/bin/tgtax` (worldMain). Scale: `scale.json`.
- Sources: `law/`, `law/rescue/` and `law/rescue2/` (sha256 in each folder's SHA256SUMS).
- Unsupported: CNSS employee contributions (rates fixed by decree; Code de sécurité sociale 2011 arts. 12-13 read via the droit-afrique archive): employeeSocial = 0 and the art. 26 (1)-(2) deductions not made; rental income (arts. 14-16, 77) and capital gains: not modelled; children 21-24 in studies: not counted as dependants
- Routes tried in rescue pass 2 (UTC 2026-11-20; pass-1 routes below them):
  - otr.tg live (laptop): the CGI document page answers 404 (site reorganised); Internet Archive CDX of otr.tg/index.php/ from 2025 lists document 600 'code-general-des-impots-livre-des-procedures-fiscales-mis-a-jour-2025/file.html' (captures 20251211205452, 20260118144945, 20260413105509): the 20251211205452 capture is the complete 361-page PDF (downloaded on the laptop, pushed to tg/law/rescue2/)
  - OTR document 599 'cahier fiscal 2025' (capture 20260218202834): truncated at 5,242,880 bytes (known Wayback truncation; not needed)
  - art. 74 barème compared on the page images with PLF 2024 art. 16 p. 17 (identical table and the stray 'Abrogé.' line); the enacted LF 2024 was not reached (reason for grade B)
  - droit-afrique.com: live site 403 ('unable to read htaccess'); Wayback: the Togo CGI is sold in its shop (only the 'sommaire' is free); Togo social security code 2011 (Wayback copy) leaves rates to decree
  - legis-palop.org, NATLEX, FAOLEX, Refworld: see RESCUE.md Pass 2 (login or Cloudflare block)
  - one WebSearch found the OTR document link
- Pass-1 routes (rescue agent):
  - build pass: OTR site (otr.tg/documentation): only the 2026 'cahier fiscal' (a summary of the LF 2026, scanned; OCR'd: no IRPP rates).
  - build pass: Ministry of finance WordPress media API (finances.gouv.tg/wp-json/wp/v2/media): LF 2023 (enacted), projets de LF 2024 and 2025, LF 2026 — all scanned; OCR'd: they amend CGI articles (e.g. art. 25 on employment income) but none restates the IRPP barème or family relief.
  - build pass: Wayback CDX of otr.tg (2018-2026): the 2018 CGI reform notes but no CGI text; legitogo.gouv.tg unreachable; new.jo.gouv.tg is a script app whose search API was not found.
  - build pass: Global law: Togo corpus holds the Code du travail, constitution, data-protection law; no tax law.
  - Internet Archive CDX of otr.tg (30,829 URLs): only the 2019 note de service on the new CGI and a reform summary; no CGI text, no finance law
  - otr.tg and new.jo.gouv.tg answer lean1; no CGI 2025 edition found by navigation
- Steps: 1 model done; 2 validation: statute's own tables only (#guard), referees wait for the testing phase; 3 proofs: kernel one-liners (Theorems.lean); 4-5 loopholes: FINDINGS.md (scan_world.py); 6 statute faults: FINDINGS.md; 7 USEFUL.md.
- Rebuild: `cd /home/lean/cmp20/world/B07-west-africa-fr-pt/tg/lean && lake build`; scan: `python3 ~/cmp20/world/tools/scan_world.py TG`.

- 2026-11-20 W5 pattern A (contributions agent): CNSS 4 % and AMU 5 % of gross remuneration, both deducted under CGI art. 26 (1)-(2) before the 28 % forfait. Provision: CNSS page "Cotisations sociales" (official secondary; rate decree under Code 2011 art. 13 not reached); Décret 2023-096/PR arts. 12, 29. Rebuilt (#guards pass), check `w5/pa/check.py TG` 0 / 300 differ with the switch off, rescanned (`scan_world.py TG`).
