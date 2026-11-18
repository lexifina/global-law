# Five tax systems in Lean

The personal income taxes of the United States, France, the United Kingdom, Germany and Japan for 2025 (US TY2025,
French income 2025, UK 2025-26, German VZ 2025, Japanese 令和7年分), each written from its statute as a Lean 4 model,
run on the same households and compared. Three of the models are new here (Germany, Japan, and the UK model already
published in [`../official-checks/uk-model`](../official-checks/uk-model)); the US and French models are the ones in
[`../TaxCode`](../TaxCode) and [`../FrTax`](../FrTax). The work is described in two blog posts:
[Comparing 5 tax systems formally with Lean](https://lexifina.com/blog/comparing-5-tax-systems-formally-with-lean) and
[Auditing the IRS and four other national tax systems with Lean](https://lexifina.com/blog/auditing-the-irs-and-four-other-national-tax-systems-with-lean).

| Folder | What it holds |
|---|---|
| [`shared`](shared) | The contract every model reads and writes ([`CONTRACT.md`](shared/CONTRACT.md): one household per JSON line in, one result per line out) and the OECD's Taxing Wages 2026 figures for the five countries ([`oecd_taxing_wages_2025.json`](shared/oecd_taxing_wages_2025.json)). |
| [`de`](de) | Germany: EStG, SolZG and employee social contributions for VZ 2025 (`DeTax`, exe `detax`, 70 theorems). Checked against the BMF's own calculator (644 cases), the BMF's printed tables, GETTSIM 1.3.2 on 10,000 households and the OECD. [`RESULTS.md`](de/RESULTS.md), [`FINDINGS.md`](de/FINDINGS.md), [`HOWWRITTEN.md`](de/HOWWRITTEN.md), [`EXAMPLE.md`](de/EXAMPLE.md); `harness/` the comparison scripts; `law/2025/` the provisions as in force for 2025. |
| [`jp`](jp) | Japan: 所得税, 復興特別所得税, 住民税 (Tokyo special wards), employee social insurance and 児童手当 (`JpTax`, exe `jptax`, 162 theorems). Checked against the statute's own tables, the NTA's printed tables and worked examples, an independent calculator written from the NTA's procedure (173,000 households, every field equal) and OpenFisca-Japan. [`RESULTS.md`](jp/RESULTS.md), [`FINDINGS.md`](jp/FINDINGS.md), [`HOWWRITTEN.md`](jp/HOWWRITTEN.md), [`EXAMPLE.md`](jp/EXAMPLE.md); `referee/` and `scripts/`; [`law/`](jp/law/README.md) the statute versions used. |
| [`uk`](uk/README.md) | The UK model's results and findings ([`RESULTS.md`](uk/RESULTS.md), [`FINDINGS.md`](uk/FINDINGS.md)). The model itself, its harness and its other documents are in [`../official-checks/uk-model`](../official-checks/uk-model). |
| [`compare`](compare) | The comparison: the US and French adapters to the contract (`lean/Compare`, exe `cmptax`), the harness that runs all five models, the check of all five against OECD Taxing Wages 2026 (which found three OECD errors), and the analyses. [`RESULTS.md`](compare/RESULTS.md) explains them; [`TABLES.md`](compare/TABLES.md) has every table; `charts/` the data behind them. |
| [`loop`](loop) | A search for loopholes in each model: per country a `CATALOGUE.md` of known planning techniques, triaged and recreated with the model (268 catalogued, 192 recreated), and a `NOVEL.md` of what a bounded search found that is not documented, with the Lean files and scripts used. |
| [`refs`](refs/README.md) | The official documents and third-party data the work used and that are not copied here, with where to get them. |

## Building

Each `lean/` folder is a Lake project pinned to Lean 4 v4.35.0, core library only. With
[elan](https://github.com/leanprover/elan) installed, `lake build` in that folder builds the library, its theorems and
its executable:

| Project | Builds | Notes |
|---|---|---|
| `de/lean` | `DeTax`, `detax` | `DeTax/PapBmf.lean` checks all 644 answers of the BMF's calculator with one `#guard` |
| `jp/lean` | `JpTax`, `jptax` | |
| `compare/lean` | `Compare`, `cmptax` (`cmptax us\|fr`) | reads the US and French models from `lean-proofs/TaxCode/Individual` and `lean-proofs/FrTax` of this repository |
| `loop/us/lean` | `UsLoop`, `usloop` | reads `lean-proofs/TaxCode/Individual` |
| `loop/fr/lean` | `FrLoop`, `frloop` | reads `lean-proofs/FrTax`; its proofs use `native_decide`, as `FrTax/Loopholes.lean` does |
| `loop/uk/lean` | `UkLoop`, `uktax` | the UK model with the extension the search needed; the unchanged files are read from `lean-proofs/official-checks/uk-model/lean`; the base model's `Theorems.lean` is checked there, not here (one proof does not close over the extended input) |
| `loop/de/lean` | `LoopDe` | standalone |
| `loop/jp/lean` | `JpLoop`, `jptax` | the Japanese model with the extension the search needed; the unchanged files are read from `jp/lean` |

The projects that read other folders do so through `srcDir` in their `lakefile.toml`, so they build only inside a
checkout of this repository. No `sorry` appears anywhere. Every executable reads the contract's JSON lines on standard
input or from a file; each country's `EXAMPLE.md` shows a household and its output.

## What is not here

- Run outputs (`runs/`), logs and build outputs. The documents name the run files a figure came from (`runs/...`);
  the harness scripts regenerate them. The chart files over 250 KB are gzipped (`compare/charts/*.json.gz`).
- The official documents, statute XML and data the models were checked against, and third-party code (GETTSIM,
  OpenFisca-Japan, PolicyEngine-UK, the DGFiP's M code): [`refs/README.md`](refs/README.md) lists them.
- The scripts were run on our build machine, where the models and tools sat under `~/cmp` (this folder's layout,
  with the UK model at `~/cmp/uk`); the paths at the top of each script say where they expect them.

## What a model here does and does not show

Each model computes one year's tax for the households of the contract: the income tax in full, and employee
contributions and universal child benefits at statutory rates for an ordinary employee. It leaves out what the
contract leaves out (means-tested benefits, US state and local tax, many reliefs), and each `FINDINGS.md` lists its
own simplifications. A theorem is proved about the model; where a model and the statute differ, the model is wrong.
