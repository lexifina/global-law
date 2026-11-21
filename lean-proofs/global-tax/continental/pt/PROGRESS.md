# PT (Portugal, IRS rendimentos de 2025, mainland): progress

Owner: PT worker (continental family). Contract: `~/cmp20/CONTRACT20.md`. Kernel: `~/cmp20/kernel` (TaxKernel 1.0).

## Status (2026-11-19): DONE, 7/7 steps (open items below)

| Step | State |
|---|---|
| 1 Model + OECD | done. `lean/` builds; exe `lean/.lake/build/bin/pttax`. OECD TW 2025: 56/56 within 1 EUR (family harness); at the OECD's gross to the cent (`oecd_exact.py`): 48/48 within 0,20 EUR, 37/48 exact; with `--bandsum --abono-annual` 44/48 exact, 4 at 0,01. F1-F2. |
| 2 Other referees | done: AT leaflet dependant examples 5/5 (`Referees.lean`); AT withholding tables compared with the statute (F7-F9, `harness/withholding_vs_statute.py`). Portal das Finanças IRS simulator needs login: not used. No maintained open model found. |
| 3 Proofs | done: 43 theorems, 0 sorry (art. 68 statute vs band sum, non-monotone, quociente can cost more, kernel instances, art. 70 slopes, withholding jumps, abono and ME notches, referee values). |
| 4 Known loopholes | done: CATALOGUE.md (14 catalogued, 9 recreated, 4 not modelled). |
| 5 New loopholes | done: NOVEL.md (abono cliffs, joint ME notch, low-pay 56 % METR, timing); scanners `results/search/SUMMARY.md`. |
| 6 Gov/statute errors | done: FINDINGS F1, F3-F5, F7-F9, F13 (lead). |
| 7 USEFUL.md | done. |

## Open items (for a later pass)
* Novelty search for N1-N3 not run (web search limit reached); CATALOGUE has no planning-literature sources yet.
* AT art. 70 n.º 6 publication of the 2025 variables (would settle F4's reading) not located.
* Art. 68-B indexation vs the OE 2025 thresholds (F6) and the 2026 art. 68 n.º 2 text (F13) unchecked.
* Not modelled: PPR (EBF 21), invoice deductions other than 78-B, owner-manager (IRC), NHR/IFICI, Regressar,
  municipal IRS participation, Azores/Madeira.

## How to resume
* Build: `cd ~/cmp20/continental/pt/lean; export PATH=$HOME/.elan/bin:$PATH; lake build` (imports only the
  kernel modules it uses, so a kernel file under construction does not break it).
* OECD: `python3 ~/cmp20/continental/harness/oecd_check.py PT`; `python3 oecd_exact.py [--bandsum --abono-annual]`.
* Withholding: `python3 harness/parse_tables.py law` then `python3 harness/withholding_vs_statute.py`.
* Scanners: `python3 ~/cmp20/harness/search/run_all.py PT --out ~/cmp20/continental/pt/results/search`.
* Lean stats: `bash harness/stats.sh`. Sources: `law/` (laws, AT pages, circulars), `refs/` (AT leaflets, tables JSON).
* Exe options: `--joint`/`--separate`, `--no-englobamento`, `--bandsum`, `--abono-annual`; input fields
  `pt_jovemYear1/2`, `pt_despesasGerais`, `pt_unit`, `pt_wagesCents1/2`.

## Family-lib / kernel gaps
See `results/summary.json` "kernel_gaps"; kernel INBOX line sent (statutory art. 68 not monotone; cents output).

## Round 2 testing (2026-11-19, improve-continental)
- Tax years 2022, 2023, 2024 added (PTTax/Years.lean; dated CIRS wordings in law/hist/; years.json in this folder):
  art. 68 tables, art. 25 dedução específica, art. 70 (old floor for 2022-2023, abatimento model for 2024), art. 78-A,
  IAS; abono de família 2024 (Portaria 422/2023). Abono 2022-2023 not modelled (CTGG not reported for those years).
- conventions.json: --taxben-despesas-gerais for oecd_taxben_imw_2024 (TaxBEN assumes the full art. 78-B deduction).
- Dev: OECD TW 2022-2024 0 -> 216 exact of 224 covered; TaxBEN 2024 0 -> 8 (statute), 16 (convention) of 24.
  Log: ~/cmp20/improve-continental/IMPROVE.md (Round 2).
- Round 10: `--start-of-year` (Eurostat earn_net ESMS 3.4): the art. 68 table in force on 1 January 2025 (before Lei
  55-A/2025), declared for the Eurostat datasets in conventions.json.
