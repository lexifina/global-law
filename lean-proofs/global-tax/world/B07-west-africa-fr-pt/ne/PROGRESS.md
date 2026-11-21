# NE progress

**2026-11-20 03:57 UTC: BUILD DONE (status built, access B). Next: software phase (SOFTWARE.md), then datasets; both by the test role.**

- statute read and modelled: Code général des impôts (Loi n° 2012-37 du 20 juin 2012), DGI edition 'CGI 2013 MAJ LF 2022', archived official copy https://web.archive.org/web/20230727151430id_/https://www.impots.gouv.ne/media/telech/CGI%202013%20MAJ%20LF%20%202022.pdf; Ordonnance n° 2024-59 portant loi de finances 2025 (archived https://web.archive.org/web/20250709034954id_/https://impots.gouv.ne/media/loi/ORDONNANCE%20N%202024-59%20LOI%20DE%20FINANCES%202025..pdf): art. 11 (CGI art. 52), art. 12 (arts. 73-75 IRVM)
- exe `netax` built (kernel 1.3, `worldMain`); Lean 132 lines, 5 theorems, 0 sorry
- scanners: `world/tools/scan_world.py B07-west-africa-fr-pt --full` with scale.json
- registry correction: NE: ITS confirmed (CGI Loi 2012-37 as amended; LF 2025 Ord. 2024-59); access B.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNSS worker 5,25 % (retraite) of pay up to 6 000 000 F a year, deducted first under CGI art. 60 1) (6 % limit) before the 13 % abatement. Provision: CNSS "Guide de l'employeur" (Décembre 2019, cnss.ne): retraite 11,50 % = 5,25 % worker + 6,25 % employer, plafond annuel 6 000 000 F; official secondary (rate décret not reached); CGI arts. 60 1), 4). Rebuilt (#guards pass), check `w5/pa/check.py NE` 0 / 300 differ with the switch off, rescanned (`scan_world.py NE`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
