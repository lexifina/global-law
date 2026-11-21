# CI progress

**2026-11-20 03:57 UTC: BUILD DONE (status built, access A). Next: software phase (SOFTWARE.md), then datasets; both by the test role.**

- statute read and modelled: Code général des impôts, DGI online edition (DGI publications API item 'CODE GENERAL DES IMPOTS 2025' → https://cgici.com/, pages V2026/page-23, 24, 326, 25, 26, 28, 49, 50; fetched 2026-11-20); ITS articles in the wording of Ord. n° 2023-719 du 13 septembre 2023; Annexe fiscale 2025 (Loi n° 2024-1109 du 18 décembre 2024), DGI e-book text https://www.dgi.gouv.ci/assets/documents/EBOOK/ANNEXE_FISCALE_2025/ (art. 120 bis dockers; art. 37 IRVM 17 %); CNPS 'Employeur' page https://www.cnps.ci/employeur (6,3 % employee retirement; ceiling 1 647 315 F/month; SMIG floor 60 000 F) — official secondary
- exe `citax` built (kernel 1.3, `worldMain`); Lean 168 lines, 9 theorems, 0 sorry
- scanners: `world/tools/scan_world.py B07-west-africa-fr-pt --full` with scale.json
- registry correction: CI: ITS (single tax since the 2024 reform, Ord. 2023-719) with the RICF; main statute = CGI as amended by Ord. 2023-719 and the LF 2025 annex.
