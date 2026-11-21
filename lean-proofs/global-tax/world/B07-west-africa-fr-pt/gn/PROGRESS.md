# GN progress

**2026-11-20 03:57 UTC: BUILD DONE (status built, access B). Next: software phase (SOFTWARE.md), then datasets; both by the test role.**

- statute read and modelled: Code général des impôts, Loi ordinaire L/2021/032/AN (promulgated 21 July 2021, applicable 1 January 2022), Journal officiel SGG: https://journal-officiel.sgg.gov.gn/textes-officiels/lois/2021/Guinee-Loi-2021-32.pdf; Loi L/2024/023/CNT portant loi de finances pour l'année 2025 (scanned; OCR): budget articles only
- exe `gntax` built (kernel 1.3, `worldMain`); Lean 95 lines, 5 theorems, 0 sorry
- scanners: `world/tools/scan_world.py B07-west-africa-fr-pt --full` with scale.json
- registry correction: GN: ITS under the 2021 CGI (L/2021/032/AN), not 'RTS'; access B.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): CNSS employee 5 % of the monthly wage up to the 2 500 000 GNF plafond, deducted from the ITS base (art. 58). Provision: CNSS page "Cotisations sociales employeurs" (cnss.gov.gn, fetched 2026-11-20): plafond 2 500 000, plancher 550 000, 23 % = employeur 18 % + salarié 5 %; official secondary (the rate / plafond décrets under the Code 1994 arts. 32-33 not reached). Rebuilt (#guards pass), check `w5/pa/check.py GN` 0 / 300 differ with the switch off, rescanned (`scan_world.py GN`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).
