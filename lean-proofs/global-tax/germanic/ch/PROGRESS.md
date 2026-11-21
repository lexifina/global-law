# CH Switzerland 2025: progress

Owner: CH worker (germanic family). Updated 2026-11-19. Status: **done** (7 of 7 steps).

## Jurisdiction (family decision)
CONTRACT38 says "federal + canton and city of Zürich, Gemeinde- and Kirchensteuer off". Family decision: model every
layer with options. Default output: `incomeTax` = direct federal tax (DBG); `localIncomeTax` = Zürich Staatssteuer
(einfache Staatssteuer x 98 %) + City of Zürich Gemeindesteuer (x 119 %) + Personalsteuer (24 per adult, StG ZH
§ 199-200); Kirchensteuer OFF. `--canton-only` = literal contract reading (no Gemeindesteuer, no Personalsteuer);
`--church reformed|catholic` adds church tax (10 % each, City of Zürich 2025). The OECD's SLT for CHE is canton +
City of Zürich + Personalsteuer, no church tax (217 % x simple tax + 24/adult reproduces SLT to the Rappen; its
chapter says church tax is no longer included).

## Steps
1. Model `lean/ChTax` (Params, Assess, Basic, Main, Theorems): 807 lines, 109 definitions, 40 theorems, 0 sorry.
   DBG Art. 9, 16-23, 26, 33, 33a, 35, 36 (printed table, Rappen), 38; StG ZH §§ 20, 26, 31, 32, 34, 35, 37, 199-200;
   AHV/IV/EO, ALV, NBU option, BVG statutory minimum (OECD 7.83 % with --oecd), Säule 3a caps, buy-ins, capital
   withdrawals, family allowances (FamZG Art. 13, 19 + EG FamZG ZH § 4). Texts: law/ (Fedlex, zhlex PDFs).
2. Validation: OECD --oecd 55/56 exact; ESTV calculator grid 1 494/1 494 exact (166 households); ESTV tariff tables
   24/24 rows = statute. Scripts: harness/estv_fetch.py, estv_compare.py; results/.
3. Proofs: Zürich tariffs progressive/convex/no jump/<= 13 %; federal band sums monotone, NOT progressive/convex
   (kernel finding F2); printed tariff vs band sum; notches (25 francs, BVG threshold, 3a, FamZG); marriage penalty.
4. Known loopholes: CATALOGUE.md 22 / 12 recreated / 10 not modelled.
5. New: NOVEL.md N1-N3 (3a trap, BVG-threshold notch, FamZG minimal wage). Scanners: results/search/SUMMARY.md.
6. Government: F3-F6 (OECD, ESTV), statute wording F1, F7, F11.
7. USEFUL.md.

## Options for a re-run
`chtax [--oecd] [--bandsum] [--canton-only] [--church reformed|catholic] [--nbu BP] [--ins-literal] [--estv]`.
OECD: `python3 ~/cmp20/germanic/oecd/check.py CH --args="--oecd"`. ESTV: `python3 harness/estv_compare.py`.
Scans: `python3 harness/{marriage,owner_ch,recreate}.py`; kernel scanners `run_all.py CH --out results/search`.

## Open
Wealth tax, Eigenmietwert/mortgage interest, other municipalities, Kapitaleinlagereserven, childcare and training
deductions not modelled; self-employed IV/EO scale proportional (convention); FamZG non-employed route uses the
federal taxable income before the allowances and assumes no EL.

## Round 6 testing (2026-11-19, improve-continental)
- Tax year 2024 added (ChTax/Years.lean fedFor; years.json [2024, 2025]): DBG 2024 tariffs and deductions (AS 2023
  493), BVV 2 2024 limits, FamZG 2024 minima (ZH 12-15 rate not sourced: flagged), ZH tariff/deductions and
  Steuerfüsse = 2025. Dev TW 2022-24: statute 22 / convention 49 exact of 80 covered. Log:
  ~/cmp20/improve-continental/IMPROVE.md (Round 6).
- Round 7: tax years 2022 and 2023 (DBG 2022/2023, StG ZH Nachtrag 115/121 via zhlex, Steuerfuss 99 % from ESTV, BVG
  2022). years.json [2022-2025]. Dev TW 2022-24: statute 64 / convention 90 exact of 240 covered.
