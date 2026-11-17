# FrTax: the French income tax in Lean

The French personal income tax (impôt sur le revenu) for income 2020 to 2025, written from the Code général des
impôts as it applied to each year, and tested against the DGFiP's own M code (run with Mlang), OpenFisca-France, the
DGFiP's online simulator, other public implementations (Catala, Publicodes, INES, EUROMOD), court decisions and the
DGFiP's published national statistics. Lean 4.35, core library only. CC0, like the rest of this repository.

```sh
cd lean-proofs
lake build FrTax          # the model and every theorem
lake build frtax          # the command-line calculator
echo "h1;2024;0AC=1,1AJ=30000" | .lake/build/bin/frtax
```

`frtax` reads one return per line (`id;year;BOX=VALUE,...`, using the boxes of form 2042) and prints the figures,
named after the M variables they are compared with.

## Files

| File | What it holds |
|---|---|
| `Basic.lean` | Euro rounding (art. 193 and 1657), with lemmas |
| `Params.lean` | The amounts the CGI fixes for each year: scale, caps, décote, allowances, limits |
| `Decl.lean` | A return as the boxes of form 2042 |
| `Income.lean` | Categories of income, allowances, charges, net and taxable income (art. 13–163) |
| `Tax.lean` | Parts (art. 194–196 B), the scale, the family-quotient cap and its complements, the décote |
| `Liquidation.lean` | Reductions, credits, flat taxes, the effective-rate rule (197 C), the 61 € threshold, the reference income (1417) |
| `Social.lean` | CSG, CRDS and the solidarity levy on investment and property income |
| `HighIncome.lean` | The high-income contribution (223 sexies) and the minimum tax on high incomes (224, from 2025) |
| `Withholding.lean` | Withholding rates: household rate (204 H I and II), couples' rates (204 M), default grids (204 H III) |
| `Penalties.lean` | Late-payment interest and majorations (art. 1727–1732, 1758 A; LPF L62) |
| `Theorems.lean`, `Brochure67.lean` | Proofs for every input (monotonicity, cliffs), and one theorem per printed cell of the DGFiP brochure's Tableaux 6 and 7 |
| `Loopholes.lean` | 18 theorems on loopholes (5 kernel-only, 13 with `native_decide`, reported by `#print axioms`) |
| `Main.lean` | The `frtax` calculator |

## Results and findings

Start with [reports/RESULTS.md](reports/RESULTS.md) (every benchmark) and [reports/FINDINGS.md](reports/FINDINGS.md)
(every disagreement, with the production simulator's verdict and what the authorities say). One report per study:

| Report | Study |
|---|---|
| [PAS.md](reports/PAS.md) | Withholding rates, Lean vs M vs the simulator |
| [OFSUITE.md](reports/OFSUITE.md) | OpenFisca-France's own test suite run through Lean and Mlang |
| [AUTHORITY.md](reports/AUTHORITY.md) | BOFiP doctrine, court decisions and written questions on each finding |
| [HISTORY.md](reports/HISTORY.md) | The DGFiP's published M releases and the corrections between them |
| [POPULATION.md](reports/POPULATION.md) | A population calibrated to national statistics: totals and the scale of each finding |
| [LOOPHOLES.md](reports/LOOPHOLES.md) | Known optimisations recreated and new loopholes found by search |
| [CATALA.md](reports/CATALA.md) | Head to head with the DGFiP and Inria's Catala model |
| [IMPLEMENTATIONS.md](reports/IMPLEMENTATIONS.md) | Publicodes, INES, EUROMOD and a survey of the rest |
| [COURTS.md](reports/COURTS.md) | Court decisions as test cases |
| [PENALTIES.md](reports/PENALTIES.md) | Penalties and interest: rules, M, Lean, courts, what the DGFiP publishes |
| [FIX_2AB_6GP.md](reports/FIX_2AB_6GP.md) | Two Lean errors found by the population study, and their fix |

[reports/logs/](reports/logs) holds the progress log of each study.

## Data and tools

- [../data/fr-tax/](../data/fr-tax): the DGFiP brochure's scale tables (gzipped), the official worked examples, the
  withholding grids, the court cases extracted from decisions, the penalty cases, the population targets, every
  answer received from the DGFiP's simulator (`simulator/`) and the score tables (`results/`).
- [../tools/frtax/](../tools/frtax): the test harness. The scripts expect a working folder `~/fr` with this model
  built in `~/fr/lean` and Mlang's C binaries in `~/fr/bin/cal<year>`; each script's docstring says what it reads.
- Not included: the downloaded legal corpora (BOFiP, court decisions, parliamentary questions; each report names its
  source), per-household run outputs, third-party code and the converted contents of OpenFisca's and Catala's tests.

The DGFiP's simulator was queried one request at a time, 1.2 s apart.
