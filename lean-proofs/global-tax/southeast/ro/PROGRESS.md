# RO Romania: PROGRESS

Updated: 2026-11-19 (milestone 3: all 7 steps done; harness integration pending on the kernel side)
Status: done (7/7). Tax year 2025 (calendar year). Currency RON (lei). ETA: none (resume only for the items below).
Web searches used: 1/3 (payroll worked examples 2025).

## Files
- `lean/` (lib RoTax, exe `rotax`; `lake build` clean, 0 sorry, 1 native_decide in F4): `Params.lean` (every figure
  cited), `DeductionTable.lean` (art. 77 alin. (4) transcribed row by row by `harness/gen_table.py` from
  `law/art-077_2025-06-30.txt`), `Wage.lean` (monthly final tax, law per month; pensions per month), `Basic.lean`
  (household, investment, rents, CASS bands, PFA, child allowance), `Theorems.lean`, `Findings.lean`.
- `law/`: statute texts (Global law) for every provision used, histories in `law/hist/`; `refs/`: EUROMOD CR RO Y16
  (pdf+txt), Eurostat earn_nt_net RO json, BNR 2024/2025 EUR rates, danielgp/salariu clone.
- `harness/`: `eurostat_check.py` (referee), `scan_wage.py` (METR scan), `owner_ro.py` (owner-manager routes),
  `fetch.sh` (polite Global law client), `gen_table.py`.
- `FINDINGS.md` (F1-F18), `CATALOGUE.md` (K1-K10), `USEFUL.md`, `results/summary.json`,
  `results/eurostat_check_2025.json`, `results/search/{wage_metr,owner_ro}.json`.

## Modelling choices (all in `Basic.lean` docstring)
- Wages: monthly (annual / 12, first months +1 leu), each month under its own law (`law2025 m`); 2025 wage law is the
  same in all 12 months. Rounding half-up to the leu for CAS, CASS, deduction and tax (validated on the July 2026
  published example, `jul2026_*`).
- Pensions: Jan-Jul tax only, Aug-Dec CASS on the excess over 3.000 then tax (Legea 141/2025 art. VII).
- Investment split equally between spouses (`roInvestOwner`), dividends 10 % (option `roDividendYear` 2024/2026),
  gains 1 % via a Romanian broker (`roGains`), rent 10 % of 80 %, CASS bands per person.
- 300 lei: only if the contractual base salary equals the minimum wage (`roBaseWage`, default = gross).
- Child allowance 719/292 lei a month (EUROMOD Table 2.4: indexation suspended in 2025).

## Validation (step 2)
- Eurostat earn_nt_net 2025 (EC-OECD model, 13 household types): net within 1 %: 13/13; within 1 leu a month:
  11/13; the 2 others: Eurostat applies the 100-lei child deduction once per earning parent (F12).
- EUROMOD CR Table 2.14 2025 deduction amounts: 5/5 exact (`euromod_2025_amounts`).
- Published July 2026 payroll example (non-official, law parametrised): 2/2 exact, 10 figures (`jul2026_*`).
- danielgp/salariu: last commit 2018-08-26, no 2025 rules: not usable (no issue to file).
- No official calculator found usable without login (ANAF has none public for salaries).

## Open / next (if resumed)
1. RO is not yet in `~/cmp20/harness/common20.py`: when added, run `run_all.py RO` and `owner.py RO` (company entry
   proposed below; INBOX line appended).
2. 2026 law (MW 4.325 from July 2026, 200 lei, micro ceiling 100.000 EUR) only partly parametrised (`lawJul2026`).

## Proposed owner-manager company entry (for `harness/search/company.json`)
RO: CIT 16 % (art. 17); dividend tax 10 % in 2025, 16 % from 2026 (art. 97 alin. (7); Legea 141/2025 art. VII);
micro-enterprise 1 % / 3 % of revenue up to 250.000 EUR in 2025, 100.000 EUR in 2026 (art. 47, 51), needs one
employee; employer CAM 2,25 % (art. 220^3); no employer CAS/CASS (shifted to employees in 2018); dividend_routing:
input field `dividends` (CASS bands applied by rotax).
