# BE (Belgium) - income year 2025 (exercice d'imposition / aanslagjaar 2026): progress

Status: **done** (7/7 steps). Updated 2026-11-19. Worker: germanic family, BE.
Default: resident of the City of Brussels (Brussels-Capital Region), City of Brussels municipal tax 4,9 % (AI 2026).

## Files
* `lean/` (Lake project, lib `BETax`, exe `betax`; 660 lines, 72 definitions, 25 theorems, 0 sorry):
  `BETax/Params.lean` (every number cited), `BETax/Basic.lean` (the computation), `BETax/Theorems.lean`.
  Build: `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build`.
  Options: `--oecd` (municipal 6,0 % as the OECD lines imply, LGAF age supplements unfrozen), `--commune-bp=N`
  (municipal rate in bp), `--unfrozen-age`. Extra input field: `"cohabiting": true` (de facto cohabitants).
* `oecd_map.py` (OECD lines: CGITFP = federal tax; SLT = Brussels regional + municipal; EECSSC = ONSS - work bonus +
  CSSS; CTGG = Famiris), `results/oecd_check*.{json,md}` (`oecd_check` = --oecd run; `_default` = City of Brussels).
* `harness/fisconet.py` (FisconetPlus public REST fetch), `harness/fsearch.py` (Fisconet search),
  `harness/h2t.py`, `harness/withholding.py` (withholding key formula referee -> `results/withholding.{json,md}`).
* `results/search/` (generic scanners, `SUMMARY.md`), `FINDINGS.md` (F1-F17), `CATALOGUE.md` (21 known),
  `NOVEL.md`, `USEFUL.md`, `results/summary.json`.
* `law/`: Fisconet indexation AI 2026, CIR 92 articles with dated history (`law/cir92/`), LSF 5/1-5/2, AR facteur
  d'autonomie, Brussels ordinance 15.12.2014, loi 30.03.1994 (CSSS, Justel), withholding formule-clé 2025 (PDF+txt).
* `refs/`: SPF pages, municipal rate lists 2024-2026 (xlsx), ONSS work-bonus and CSSS instructions 2025, Famiris
  barèmes 01/01/2025 and 01/02/2025, Fisconet navigation tree and TOCs.

## Model (what is in)
ONSS 13,07 % less the social work bonus (two volets, January and Feb-Dec tables), art. 51 forfait, quotient conjugal
art. 87-88, art. 130 tariff, exempt sum art. 131-134 on its own tariff with child/single-parent/extra supplements,
spouse transfers and the refundable child credit, impôt Etat réduit (24,957 %), Brussels centimes 32,591 %, municipal
tax on federal + regional, fiscal work bonus art. 289ter/1 (refundable, art. 304 § 2), dividends (833 exempt per
taxpayer) and interest at 30 % separately, CSSS (individual / joint scale), Famiris (Brussels regime vs transitional
LGAF, social supplements, July age supplement). Not in: pensions' art. 147 reduction, INASTI, rental income, federal
tax reductions (gifts, pension savings), co-parenting, real expenses.

## Validation
OECD TW 2025: 56/56 within 1 EUR with `--oecd`; default 38/56 (municipal rate and F2). SPF worked example 1/1 (Lean).
Withholding formula: 542 points, 454 within 1 % (differences explained, F9).

## Not done / open
* Tax-Calc not queried; OpenFisca-Belgium not located (no web search possible: the WebSearch tool failed on a usage
  limit; 0 of 3 searches used). OECD country description unreadable (403): F10 open.
* Owner-manager with INASTI and VVPR-bis/liquidation reserve not modelled (only the art. 215 CIT notch in Lean).
