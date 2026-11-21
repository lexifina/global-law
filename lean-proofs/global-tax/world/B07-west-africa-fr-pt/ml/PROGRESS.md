# ML progress

**2026-11-20 03:57 UTC: BUILD DONE (status built, access B). Next: software phase (SOFTWARE.md), then datasets; both by the test role.**

- statute read and modelled: Code général des impôts du Mali, DGI online code https://www.dgi.gouv.ml/CGI/ (fetched 2026-11-20; document metadata 2017-08-23; latest notes Loi n° 2016-10, LF 2012/2013); DGI annual activity reports 2024 and 2025 (dgi.gouv.ml, scanned; OCR): no ITS change mentioned
- exe `mltax` built (kernel 1.3, `worldMain`); Lean 126 lines, 6 theorems, 0 sorry
- scanners: `world/tools/scan_world.py B07-west-africa-fr-pt --full` with scale.json
- registry correction: ML: ITS confirmed (CGI, Loi 2016-10 barème); access B.

- 2026-11-20 W5 pattern A (contributions agent, Africa/MENA sweep): INPS assurance vieillesse 3,6 % and AMO 3,06 % of all remuneration, reported; the 3,6 % pension retention deducted (CGI art. 7 a), limit 4 %). Provision: INPS "Guide du cotisant" (PDF of 10 August 2013, Internet Archive capture 2021-09-23): AMO salarié 3,06 %, vieillesse salarié 3,6 %; Code de prévoyance sociale art. 187 (base); official secondary; CGI art. 7 a). Rebuilt (#guards pass), check `w5/pa/check.py ML` 0 / 300 differ with the switch off, rescanned (`scan_world.py ML`, logs/w5_pa2_scan.log), inputs.json refreshed (tools/world_meta.py).

- 2026-11-20 D9 review: `world_ml_taxdev_eitd_2020` (0 / 28 dev, all below) is a referee omission (EITD row on gross pay, no art. 7 a) deduction, no arts. 12-A / 12-B reduction): FINDINGS D9S-1; model unchanged. world/IMPROVE_D9.md.
