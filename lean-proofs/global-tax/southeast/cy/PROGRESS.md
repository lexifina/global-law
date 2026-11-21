# CY Cyprus: PROGRESS

Updated: 2026-11-19 (milestone 6: all 7 steps done; status "done")
Status: done (7/7). Tax year 2025 (calendar year). Web searches used: 1/3.
Next step (optional): a Tax Department worked example or calculator as a second referee (none found without login;
not searched); rerun `python3 ~/cmp20/harness/search/run_all.py CY --out ~/cmp20/southeast/cy/results/search` once the
kernel adds the CY company side (owner-manager scan).

## Files
- `lean/` Lake project `CYTax`, exe `cytax` (money in cents; output euros with 2 decimals, own `CYTax/Main.lean` as PT).
  `Params.lean` (every number cited), `Basic.lean` (model), `Theorems.lean` (kernel instances + statute properties),
  `Findings.lean` (one statement per finding). 534 lines, 66 definitions, 34 theorems, 0 sorry. Build:
  `cd lean && export PATH=$HOME/.elan/bin:$PATH && lake build`.
- Input extras: per adult `"cyFirstEmployment": "21A" | "23A"` (ITL art. 8 status); household `"cyNonDom": true`
  (or exe flag `--non-dom`); exe flag `--statute-si` (SI rates as printed in SIL, F1).
- `harness/eurostat_check.py` (referee), `harness/owner_cy.py` (owner-manager), `harness/explore1.py` (notches),
  `harness/cy.py` (runner). Results: `results/eurostat_2025.txt`, `results/owner_cy.txt`, `results/explore1.txt`,
  `results/search/` (generic scanners, run 2026-11-19), `results/summary.json`.
- `law/`: statute texts (txt) and sources below. `refs/eurostat_earn_nt_net_cy.json`.
- `FINDINGS.md` (F1-F15), `CATALOGUE.md` (K1-K14), `USEFUL.md`, `elections.json` (empty: Cyprus gives individuals no
  income-tax election that the household contract can express; 21Α/23Α/non-dom are statuses, not choices).

## What is modelled (2025)
Income tax: ITL Second Schedule 1(β) (0/20/25/30/35 % at 19.500/28.000/36.300/60.000), individual taxation, art. 8
exemptions of interest, dividends, gains on securities, 21Α and 23Α (input status), art. 9(2) 20 % rent deduction,
art. 9(1)(στ) donations, art. 14 deductions (SI, GESY, pension contributions) capped at one fifth. SDC: dividends 17 %,
interest 17 % (3 % at total income ≤ 12.000 €), rent 3 % × 75 %; domiciled only. GESY: 2,65 % employees/pensioners/
income, 4 % self-employed, 180.000 € cap in the statutory order. SI: 8,8 % employees, 16,6 % self-employed (applied
rates; F1), ceiling 66.612 €. Child benefit (CBL Table A, 2025 indexed amounts) and single-parent benefit (Table B):
in scope because both are in Eurostat's/EUROMOD's household picture (FAM line) and they carry the largest METR effects.
Not modelled: listed in each output's `unsupported`.

## Validation (step 2)
- Eurostat earn_nt_net 2025 (EC tax-benefit model, OECD Taxing Wages method, 13 household types, gross to the cent):
  52/52 lines within 0,01 €, 40/52 to the cent; income tax and family allowances exact in all 13; the 12 one-cent
  differences are Eurostat rounding SI + GESY as one sum (F15). Also confirms the applied 8,8 % SI rate (F1).
- EUROMOD CR Cyprus 2022-2025 (JRC 2026) parameter description: 48 parameters compared (scale, SI rate and ceiling,
  GESY rates and cap, SDC rates and the 12.000 € rule, rent deductions, one-fifth cap, child and single-parent benefit
  amounts and limits), 48 agree; 3 described items disagree with the 2025 statute (F9: EUROMOD wrong on 2, right on the
  applied SI rate).
- Cyprus is not in OECD Taxing Wages. Official calculator: none used (the Tax Department's TaxisNet needs a login).

## Owner-manager company side (proposed entry for ~/cmp20/harness/search/company.json; INBOX line sent)
CIT 12,5 % flat (ITL Second Schedule para 2, 2025 text: "δώδεκα και μισό τοις εκατόν (12,5%)"); employer: SI 8,8 %
(EUROMOD CR §2.7.2.3(a); SIL art. 5 proviso) + Redundancy Fund 1,2 % + Human Resource Development Fund 0,5 % on pay up
to 66.612 € (EUROMOD CR §2.7.2.3(c),(d)), Social Cohesion Fund 2 % uncapped (§2.7.2.3(e)), GESY 2,90 % (GESY Law art.
19(1)(β); not in the art. 19(4) cap list); Central Holiday Fund 8 % only for non-exempt employers (left out).
Dividends: personal side in cytax (`dividends`, SDC 17 % + GESY 2,65 %; `cyNonDom: true` for the non-dom route).

## Sources (law/)
- ITL 118(I)/2002 as of 2025-11-09: Wayback http://web.archive.org/web/20251109040059id_/https://cylaw.org/nomoi/enop/non-ind/2002_1_118/full.html
  (`itl_118_2002_as_of_2025-11-09.txt`); current: http://www.cylaw.org/nomoi/enop/non-ind/2002_1_118/full.html
  (`itl_118_2002.txt`, fetched 2026-11-19 from the laptop; lean1 gets HTTP 403 from cylaw.org).
- Amending laws 219(I)/2025, 244(I)/2025: http://www.cylaw.org/nomoi/arith/2025_1_219.pdf, ..._244.pdf (`*.txt`).
- SDC 117(I)/2002 as of 2025-11-07 (Wayback 20251107181827) and current; GESY 89(I)/2001 current (rates unchanged since
  2020); SIL 59(I)/2010 as of 2025-09-12 (Wayback) and current; CBL 167(I)/2002 current (amendments 46(I)/2025 in force
  1.1.2025 and 159(I)/2025 included).
- EUROMOD Country Report Cyprus 2022-2025: https://euromod-web.jrc.ec.europa.eu/sites/default/files/2026-02/Y16_CR_CY.pdf.
- Eurostat earn_nt_net: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/earn_nt_net?geo=CY&sinceTimePeriod=2023
- OEB circular Αρ.α.257/2024 (2 Dec 2024, the 2025 SI ceiling 1.281/5.551/66.612 €), via the one web search.
- Global law holds only 11 Cyprus acts (none of the tax acts): checked with `gl.py list_jurisdictions` and
  `list_provisions cyprus/national/acts`.

## Steps
1. Model: done. 2. Validation: done (above). 3. Proofs: done (Theorems.lean 18, Findings.lean 16). 4. Known loopholes:
done (CATALOGUE: 14 catalogued, 8 recreated, 5 not modelled). 5. New loopholes: done (F3, F4, F5, F10; generic
scanners in results/search). 6. Government errors / statute faults: done (F1, F9, F11-F14). 7. USEFUL.md: done.
