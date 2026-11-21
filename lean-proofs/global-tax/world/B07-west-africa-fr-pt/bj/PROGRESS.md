# BJ progress

**2026-11-20 03:57 UTC: BUILD DONE (status built, access B). Next: software phase (SOFTWARE.md), then datasets; both by the test role.**

- statute read and modelled: Code général des impôts 2023 (Loi n° 2021-15 du 23 décembre 2021, mise à jour LF 2023 loi n° 2022-33), Ministère de l'Economie et des Finances: https://finances.bj/wp-content/uploads/2023/01/63c7b8d3eef3c_Benin-CGI-2023-officiel.pdf
- exe `bjtax` built (kernel 1.3, `worldMain`); Lean 116 lines, 6 theorems, 0 sorry
- scanners: `world/tools/scan_world.py B07-west-africa-fr-pt --full` with scale.json
- registry correction: BJ: ITS confirmed (CGI Loi 2021-15); no family relief; access B.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNSS salarié 3,6 % of all remuneration (pension branch, no ceiling), reported, not deducted (ITS base is gross pay, CGI art. 122). Provision: CNSS page "Procédure de recouvrement des cotisations" (cnss.bj, fetched 2026-11-20): "Pension : 10 % dont : 6.4 % à la charge de l'employeur 3.6 % à la charge du salarié", base "l'ensemble des rémunérations"; official secondary (rate décret under Code SS 2003 art. 24 2) not reached); CGI 2023 arts. 120, 122, 124. Rebuilt (#guards pass), check `w5/pa/check.py BJ` 0 / 300 differ with the switch off, rescanned (`scan_world.py BJ`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
