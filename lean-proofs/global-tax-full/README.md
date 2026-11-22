# Global tax in Lean: every tax, 199 jurisdictions (2025)

Lean 4 models of the taxes of 199 jurisdictions for the tax year 2025: the 197 countries of the income-tax models in
[`../global-tax`](../global-tax/), plus Hong Kong and Macau. Where those models cover the personal income tax on
wages, these cover every tax heading of the OECD classification: corporate tax and withholding, capital income and
gains, social contributions, payroll taxes, property, net wealth, inheritance and gift, property transfers and stamp
duties, VAT and sales taxes, excises, customs duties, vehicle taxes and other taxes. Every jurisdiction's model is
built on one shared kernel and one master equation, and every rule cites the provision it comes from.

Each of the 197 countries' income-tax models is included unchanged, as a library the full model calls first, so
every income-tax figure is the one the published income-tax model gives. Hong Kong and Macau have no income-tax model
yet (see [What is not here yet](#what-is-not-here-yet)).

## The master equation

A model takes one **entity**, a household or a company, described by its income of each kind, its assets, the assets
it sells, the inheritances and gifts it receives, its purchases and its consumption. It returns a list of
**charges**. A charge is one tax applied to one base: the year's income, one sale, one inheritance, one purchase, the
consumption basket, one payment abroad. For every charge `c`:

```
due(c)    = schedule(relief(base)) - credit           (a credit that is not refundable never exceeds the tax)
tax(k)    = the sum of due(c) over the charges in OECD heading k
total     = the sum of tax(k) over all headings = the sum of due(c) over all charges
net       = resources + benefits - the charges the entity bears
```

`relief` is everything that turns the base into the taxable amount (allowances, exemptions, deductions, indexation),
`schedule` is the rate or band schedule, and `credit` is anything subtracted from the tax. Charges are produced in
order: first the income tax of the income-tax model, then each tax family, and each family sees every charge before
it. So a credit that crosses taxes, such as corporate tax credited against the shareholder's dividend tax, is an
ordinary input of the later family. Each charge also records its OECD heading, its level of government (central,
state, local, social security) and who bears it: the entity itself, its employer, the entity as a consumer (VAT and
excises inside prices), or the recipient of a payment it makes (tax withheld at source).

The kernel proves the equation once for every model: each charge satisfies `due = gross - credit`, the total equals
the sum of `schedule(relief(base)) - credit` over the charges, the headings add up to the total, adding a tax family
changes nothing computed before it, and the income-tax figures of the full model are exactly those of the
income-tax model (`charge_wf`, `total_eq_master`, `isum_filter_split`, `withFamily_total`, `adapter_unchanged` and
others in [`kernel/TaxKernel/Global/Master.lean`](kernel/TaxKernel/Global/Master.lean)). The rules for each kind of tax (bands, relationship classes for
inheritance tax, VAT baskets, excise rates per unit with minimums, customs tariffs, vehicle taxes, local rates) are in
[`kernel/TaxKernel/Global2/`](kernel/TaxKernel/Global2/), documented in [`kernel/API.md`](kernel/API.md) section 4e.

## Building

Install [elan](https://github.com/leanprover/elan). Every project pins Lean 4 v4.35.0 in `lean-toolchain` and uses
Lean's core library only (no Mathlib). Each jurisdiction's `lean/` folder is a Lake project that finds the kernel and
its region's shared library by relative paths, so keep the folder layout as it is.

```sh
cd kernel && lake build                     # the kernel (lake build kfid adds the UK and German fidelity check)
cd ../global/R4/za/lean && lake build       # one jurisdiction: its library, theorems, #guard tests and executable
.lake/build/bin/zaglobal --global < ../results/cases.jsonl     # prints ../results/cases_out.jsonl
```

To build everything, build the kernel first, then each jurisdiction:

```sh
(cd kernel && lake build) && for d in global/*/*/lean; do (cd "$d" && lake build) || echo "FAILED $d"; done
```

A successful `lake build` is the check: it compiles the model, proves its theorems and runs its `#guard` tests. The
executable's name is the `[[lean_exe]]` in the project's `lakefile.toml` (`zaglobal`, `frglobal`, ...). With
`--global` it reads one entity per JSON line and writes one result per line: every charge with its base, relief,
gross, credit, amount due, OECD heading, level, bearer and the statute it applies, then totals by heading and the net
position. Without `--global` it reads the household lines of the income-tax model and answers exactly as that model
does. The input and output formats are in [`kernel/API.md`](kernel/API.md), section 4e.

## Layout

| Path | What it holds |
|---|---|
| [`kernel/`](kernel/) | The shared tax kernel, version 2.9.0: `TaxKernel` (the parts the income-tax models use), `TaxKernel/Global` (the master equation and its theorems), `TaxKernel/Global2` (the parts for each kind of tax), [`API.md`](kernel/API.md), `examples/` (worked uses of every part, checked by `#guard`), `audit/` (the axioms every kernel theorem rests on, with Lean's answer in `*.out`), `Fidelity/` |
| [`global/R4/`](global/R4/) | Sub-Saharan Africa (48); `common/` holds the region's shared Lean library, `specs/` the specifications the models were generated from |
| [`global/R5/`](global/R5/) | Middle East and North Africa, with Turkey, Israel, Cyprus and the South Caucasus (24); `common/` as above |
| [`global/europe/`](global/europe/) | Europe (45); `tools/` holds the specifications and rows the models were generated from |
| [`global/americas/`](global/americas/) | The Americas and the Caribbean (35); `common/`, `tools/specs/` as above |
| [`global/asiapac/`](global/asiapac/) | Asia and the Pacific, with Central Asia (47, Hong Kong and Macau in `cn-hk`, `cn-mo`); `tools/specs/` as above |
| [`SOURCES.tsv`](SOURCES.tsv) | The official documents the models were built from: file name, size, SHA-256 and web address (the documents themselves are not included) |

Each jurisdiction's folder holds:

| File | What it is |
|---|---|
| `lean/<Cc>Global/` | The full model, one module per tax family (for example `Corporate`, `Capital`, `Social`, `Property`, `Transfers`, `Wealth`, `Consumption`, `Customs`, `Other`), `Absent.lean` (taxes the jurisdiction does not levy, each with the provision that shows it), `Model.lean` and `Main.lean` |
| `lean/<Cc>Tax/` | The income-tax model, as in `../global-tax` (`VENDORED.sha256` gives the SHA-256 of each copied file) |
| `results/summary.json` | Every tax of the jurisdiction: OECD heading, name, statute, version of the text used, grade, kernel parts, number of checks, and what is missing for a tax that is not modelled |
| `results/taxes.json` or `results/taxes/*.json` | The same list in more detail, by tax family |
| `results/cases.jsonl`, `results/cases_out.jsonl` | Worked examples (households and companies) and the model's answers |
| `PROGRESS.md`, `FINDINGS.md` | The build log, and where present, what the model found in the law |

Comments sometimes name a source file by its path in the working folders the models were built in (for example
`<cc>/law/...`, `R4/fetch/...` or `cmp20/world/...`, the last being the folders of `../global-tax`). Those folders
are not published; [`SOURCES.tsv`](SOURCES.tsv) gives the web address and SHA-256 of the official ones.

## Grades

Every tax of every jurisdiction has one grade in `results/summary.json`:

- **A**: the 2025 text of every provision the model uses was read, and the model follows it.
- **B**: the structure comes from the act, but some amounts come from an official secondary source, such as the tax
  authority's published rate tables or guides, flagged next to each such value; or one input has a default set by
  the statute.
- **C**: not modelled yet. No 2025 text could be reached, or the provisions were not read. The model returns
  "unsupported" for that tax and records what was tried and what would make it possible.
- **Not levied**: the jurisdiction does not levy this tax, and the provision that shows it is cited.
- **Framework (local rate input)**: the national law fixes how the tax works, but each municipality sets the rate
  (as with Germany's trade tax multiplier). The model computes the tax with the rate as an input.
- **Reclassified**: an item that is not a tax under the OECD classification (for example a voluntary contribution, or
  a church tax that the OECD does not count as a tax) or that duplicates a heading counted elsewhere. It is cited and
  left out of the count.

## Coverage

Counted from the 199 jurisdictions' `results/summary.json`, by the same count as the project's live coverage report.
Done = A + B + framework + not levied, as a share of all entries except the reclassified ones. The personal income tax
on wages, employee contributions and the investment income those models cover come from the income-tax models and are
complete for the 197 countries; they are not counted here.

| Tax (OECD heading) | A | B | Framework (local rate input) | Not levied | C | Reclassified | Done |
|---|---:|---:|---:|---:|---:|---:|---:|
| Corporate tax and withholding (1200) | 256 | 151 | 0 | 1 | 32 | 0 | 93 % |
| VAT / GST (5111) | 77 | 99 | 0 | 5 | 11 | 0 | 94 % |
| Employer social contributions (2200) | 99 | 141 | 0 | 8 | 34 | 0 | 88 % |
| Payroll taxes (3000) | 37 | 60 | 0 | 16 | 19 | 0 | 86 % |
| Capital income and gains, personal (1100) | 75 | 131 | 0 | 6 | 51 | 1 | 81 % |
| Inheritance and gift (4300) | 32 | 61 | 0 | 29 | 39 | 0 | 76 % |
| Net wealth (4200) | 12 | 46 | 0 | 76 | 19 | 0 | 88 % |
| Property transfer and stamp duty (4400) | 61 | 106 | 0 | 11 | 93 | 0 | 66 % |
| Excise (5121) | 94 | 65 | 0 | 1 | 92 | 0 | 63 % |
| Recurrent property tax (4100) | 41 | 47 | 9 | 0 | 81 | 0 | 54 % |
| Vehicle and use taxes (5200) | 48 | 34 | 0 | 1 | 76 | 0 | 52 % |
| Sales taxes (5112) | 4 | 3 | 0 | 25 | 11 | 0 | 74 % |
| Taxes on specific services (5126) | 1 | 2 | 0 | 0 | 2 | 0 | 60 % |
| Other taxes on specific goods (5120) | 3 | 3 | 0 | 0 | 32 | 0 | 16 % |
| Other taxes (6000) | 2 | 0 | 0 | 36 | 89 | 9 | 30 % |
| **All taxes** | **850** | **1005** | **9** | **227** | **733** | **13** | **74 %** |

"All taxes" also counts the headings not listed separately, such as self-employed contributions.

| Regional folder | A | B | Framework (local rate input) | Not levied | C | Reclassified | Done |
|---|---:|---:|---:|---:|---:|---:|---:|
| `global/R4/` (Sub-Saharan Africa) | 191 | 286 | 1 | 44 | 89 | 4 | 85 % |
| `global/R5/` (Middle East and North Africa) | 87 | 65 | 0 | 8 | 55 | 0 | 74 % |
| `global/americas/` (The Americas and the Caribbean) | 155 | 127 | 0 | 103 | 276 | 3 | 58 % |
| `global/asiapac/` (Asia and the Pacific) | 152 | 348 | 0 | 10 | 111 | 0 | 82 % |
| `global/europe/` (Europe) | 265 | 179 | 8 | 62 | 202 | 6 | 72 % |

## What is not here yet

- **Taxes not modelled.** 733 of the 2,824 tax entries (26 %) are grade C: no 2025 text was reached or it was not
  read. The gaps are largest for other taxes on specific goods, other taxes, vehicle taxes, recurrent property taxes,
  excises and property transfers, and in the Americas, where 58 % of entries are done.
- **Official secondary sources.** 1,005 entries are grade B: part of their amounts come from tax authority tables or
  guides, not from the act. Some facts are cited from commercial summaries (for example PwC Worldwide Tax Summaries)
  where no official text was found; their wording is not copied.
- **Local taxes.** Where municipalities set their own rates, the model takes the rate as an input or uses the capital
  city's rate, and says which.
- **Missing facts about the entity.** Some rules need facts the input does not hold, for example a company's balance
  sheet, its regime or its age, or all earlier gifts from the same donor. The model then applies the general rule, and
  the gap is noted in the source.
- **Known errors not yet fixed.** Property checks run over all 199 models on 21-22 November 2026 (for example, a
  raise never lowers net income, and splitting a sale or a gift into parts does not lower the tax unless the law says
  so) found 34 items, some covering several countries, where a model departs from the 2025 law or lacks a fact it
  needs. Not all of them are fixed in this snapshot. The largest: Hong Kong and Macau have no income-tax model yet,
  so their models do not tax wages (no salaries tax, no professional tax) and their household totals are too low.
  Most others are narrow, such as an exemption given once per gift where the law gives it once per year.
- **Outside checks.** The models were scored against open-source tax software and published datasets where these
  exist, mostly for VAT, and for some countries' corporate tax, employer contributions, capital gains, property
  transfers and inheritance tax. Most entries have no outside check beyond the model's own `#guard` tests. The test
  data are not in this repository.
- **The law texts** are not included (see [Sources](#sources)).

## How this snapshot was checked

- Built from scratch: the kernel, its examples and its axiom audit (no `sorry` in any theorem), and all 199
  jurisdictions; each jurisdiction with worked examples was run on `results/cases.jsonl`, and its answers were
  identical, byte for byte, to `results/cases_out.jsonl`.
- No `sorry` or `admit` anywhere. 68 uses of `native_decide` remain, all in nine files of the copied income-tax models; they
  rely on Lean's compiler as well as its kernel.
- About 75,400 lines of full-model Lean (5,287 `#guard` tests, 223 theorems) in 2,024 files, 82,700 lines of copied
  income-tax models and 13,600 lines of kernel (449 theorems, 663 `#guard` tests).

## Sources

The models cite the act, article and version they apply in the Lean source and in `results/summary.json`. The
documents themselves are not included, since many publishers do not allow redistribution. [`SOURCES.tsv`](SOURCES.tsv)
lists the official legislation, official guidance pages and Lexifina law repository extracts the models were built
from, with each file's size, SHA-256 and web address (whether the address was recorded at download or read from the
file). Pages from commercial or secondary publishers, and files with no recorded official address, are not listed.
The statutes of most countries are also in this repository's country folders (`lexifina/<country>-law`).

## Licence and citation

Like the rest of this repository, the Lean code and documents here are dedicated to the public domain under
[CC0 1.0](../../LICENSE.md). The law they encode is not covered by that dedication. Short quotations from statutes, and
from publications under CC BY 4.0 (OECD Taxing Wages 2025, the EUROMOD country reports of the European Commission's
Joint Research Centre, Eurostat), are cited where they appear and remain under their own terms.

To cite this work, name the commit you used:

```bibtex
@misc{lexifina_global_tax_full_lean_2026,
  author       = {{Lexifina}},
  title        = {Global tax in {Lean}: every tax for 199 jurisdictions on one master equation (2025)},
  year         = {2026},
  howpublished = {\url{https://github.com/lexifina/global-law/tree/main/lean-proofs/global-tax-full}},
  note         = {Commit <sha>}
}
```

## Index

Grades are counts of taxes in each jurisdiction's `results/summary.json`.

| Jurisdiction | Code | Folder | A | B | Framework | Not levied | C | Reclassified |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Afghanistan | AF | [`global/asiapac/af`](global/asiapac/af/) | 0 | 6 | 0 | 0 | 8 | 0 |
| Albania | AL | [`global/europe/al`](global/europe/al/) | 1 | 6 | 0 | 1 | 5 | 0 |
| Algeria | DZ | [`global/R5/dz`](global/R5/dz/) | 8 | 0 | 0 | 0 | 2 | 0 |
| Andorra | AD | [`global/europe/ad`](global/europe/ad/) | 4 | 1 | 0 | 0 | 7 | 0 |
| Angola | AO | [`global/R4/ao`](global/R4/ao/) | 8 | 5 | 0 | 0 | 0 | 0 |
| Antigua and Barbuda | AG | [`global/americas/ag`](global/americas/ag/) | 3 | 2 | 0 | 4 | 8 | 0 |
| Argentina | AR | [`global/americas/ar`](global/americas/ar/) | 9 | 4 | 0 | 1 | 8 | 0 |
| Armenia | AM | [`global/R5/am`](global/R5/am/) | 8 | 1 | 0 | 1 | 0 | 0 |
| Australia | AU | [`global/asiapac/au`](global/asiapac/au/) | 5 | 8 | 0 | 0 | 0 | 0 |
| Austria | AT | [`global/europe/at`](global/europe/at/) | 18 | 1 | 0 | 2 | 2 | 1 |
| Azerbaijan | AZ | [`global/R5/az`](global/R5/az/) | 6 | 2 | 0 | 0 | 0 | 0 |
| Bahamas | BS | [`global/americas/bs`](global/americas/bs/) | 0 | 4 | 0 | 7 | 7 | 0 |
| Bahrain | BH | [`global/R5/bh`](global/R5/bh/) | 1 | 6 | 0 | 1 | 1 | 0 |
| Bangladesh | BD | [`global/asiapac/bd`](global/asiapac/bd/) | 3 | 3 | 0 | 0 | 6 | 0 |
| Barbados | BB | [`global/americas/bb`](global/americas/bb/) | 2 | 3 | 0 | 6 | 6 | 0 |
| Belarus | BY | [`global/europe/by`](global/europe/by/) | 6 | 0 | 0 | 2 | 7 | 0 |
| Belgium | BE | [`global/europe/be`](global/europe/be/) | 0 | 7 | 0 | 1 | 6 | 0 |
| Belize | BZ | [`global/americas/bz`](global/americas/bz/) | 4 | 3 | 0 | 6 | 3 | 1 |
| Benin | BJ | [`global/R4/bj`](global/R4/bj/) | 0 | 16 | 0 | 3 | 1 | 0 |
| Bhutan | BT | [`global/asiapac/bt`](global/asiapac/bt/) | 2 | 7 | 0 | 0 | 3 | 0 |
| Bolivia | BO | [`global/americas/bo`](global/americas/bo/) | 4 | 5 | 0 | 1 | 10 | 0 |
| Bosnia and Herzegovina | BA | [`global/europe/ba`](global/europe/ba/) | 1 | 5 | 0 | 0 | 8 | 0 |
| Botswana | BW | [`global/R4/bw`](global/R4/bw/) | 1 | 5 | 0 | 1 | 2 | 0 |
| Brazil | BR | [`global/americas/br`](global/americas/br/) | 11 | 7 | 0 | 1 | 5 | 0 |
| Brunei | BN | [`global/asiapac/bn`](global/asiapac/bn/) | 2 | 7 | 0 | 0 | 4 | 0 |
| Bulgaria | BG | [`global/europe/bg`](global/europe/bg/) | 1 | 7 | 0 | 2 | 4 | 0 |
| Burkina Faso | BF | [`global/R4/bf`](global/R4/bf/) | 1 | 16 | 0 | 2 | 2 | 0 |
| Burundi | BI | [`global/R4/bi`](global/R4/bi/) | 0 | 10 | 0 | 0 | 0 | 0 |
| Cabo Verde | CV | [`global/R4/cv`](global/R4/cv/) | 0 | 6 | 0 | 0 | 3 | 0 |
| Cambodia | KH | [`global/asiapac/kh`](global/asiapac/kh/) | 1 | 9 | 0 | 0 | 2 | 0 |
| Cameroon | CM | [`global/R4/cm`](global/R4/cm/) | 7 | 11 | 0 | 2 | 0 | 0 |
| Canada | CA | [`global/americas/ca`](global/americas/ca/) | 10 | 5 | 0 | 0 | 8 | 0 |
| Central African Republic | CF | [`global/R4/cf`](global/R4/cf/) | 0 | 12 | 0 | 2 | 3 | 0 |
| Chad | TD | [`global/R4/td`](global/R4/td/) | 3 | 9 | 0 | 2 | 2 | 0 |
| Chile | CL | [`global/americas/cl`](global/americas/cl/) | 10 | 1 | 0 | 3 | 6 | 0 |
| China | CN | [`global/asiapac/cn`](global/asiapac/cn/) | 5 | 9 | 0 | 0 | 0 | 0 |
| Colombia | CO | [`global/americas/co`](global/americas/co/) | 13 | 3 | 0 | 0 | 9 | 0 |
| Comoros | KM | [`global/R4/km`](global/R4/km/) | 0 | 8 | 0 | 2 | 3 | 0 |
| Congo | CG | [`global/R4/cg`](global/R4/cg/) | 6 | 3 | 0 | 0 | 2 | 0 |
| Costa Rica | CR | [`global/americas/cr`](global/americas/cr/) | 7 | 2 | 0 | 3 | 7 | 0 |
| Croatia | HR | [`global/europe/hr`](global/europe/hr/) | 2 | 9 | 1 | 2 | 1 | 0 |
| Cuba | CU | [`global/americas/cu`](global/americas/cu/) | 6 | 2 | 0 | 2 | 7 | 0 |
| Cyprus | CY | [`global/R5/cy`](global/R5/cy/) | 6 | 2 | 0 | 0 | 0 | 0 |
| Czechia | CZ | [`global/europe/cz`](global/europe/cz/) | 4 | 7 | 0 | 3 | 2 | 0 |
| Cote d'Ivoire | CI | [`global/R4/ci`](global/R4/ci/) | 13 | 2 | 0 | 1 | 2 | 0 |
| DR Congo | CD | [`global/R4/cd`](global/R4/cd/) | 2 | 7 | 0 | 2 | 2 | 0 |
| Denmark | DK | [`global/europe/dk`](global/europe/dk/) | 7 | 4 | 0 | 1 | 4 | 1 |
| Djibouti | DJ | [`global/R4/dj`](global/R4/dj/) | 0 | 6 | 0 | 1 | 3 | 0 |
| Dominica | DM | [`global/americas/dm`](global/americas/dm/) | 1 | 4 | 0 | 2 | 10 | 0 |
| Dominican Republic | DO | [`global/americas/do`](global/americas/do/) | 4 | 4 | 0 | 2 | 9 | 0 |
| Ecuador | EC | [`global/americas/ec`](global/americas/ec/) | 4 | 2 | 0 | 2 | 10 | 0 |
| Egypt | EG | [`global/R5/eg`](global/R5/eg/) | 4 | 1 | 0 | 0 | 3 | 0 |
| El Salvador | SV | [`global/americas/sv`](global/americas/sv/) | 4 | 7 | 0 | 3 | 8 | 0 |
| Equatorial Guinea | GQ | [`global/R4/gq`](global/R4/gq/) | 6 | 2 | 0 | 2 | 1 | 0 |
| Eritrea | ER | [`global/R4/er`](global/R4/er/) | 0 | 0 | 0 | 0 | 6 | 0 |
| Estonia | EE | [`global/europe/ee`](global/europe/ee/) | 5 | 3 | 1 | 4 | 1 | 0 |
| Eswatini | SZ | [`global/R4/sz`](global/R4/sz/) | 1 | 7 | 0 | 1 | 0 | 0 |
| Ethiopia | ET | [`global/R4/et`](global/R4/et/) | 4 | 4 | 0 | 0 | 1 | 1 |
| Fiji | FJ | [`global/asiapac/fj`](global/asiapac/fj/) | 2 | 6 | 0 | 1 | 2 | 0 |
| Finland | FI | [`global/europe/fi`](global/europe/fi/) | 5 | 7 | 1 | 1 | 2 | 1 |
| France | FR | [`global/europe/fr`](global/europe/fr/) | 6 | 17 | 0 | 0 | 4 | 0 |
| Gabon | GA | [`global/R4/ga`](global/R4/ga/) | 13 | 4 | 0 | 2 | 2 | 0 |
| Gambia | GM | [`global/R4/gm`](global/R4/gm/) | 2 | 4 | 0 | 0 | 1 | 0 |
| Georgia | GE | [`global/R5/ge`](global/R5/ge/) | 5 | 4 | 0 | 0 | 0 | 0 |
| Germany | DE | [`global/europe/de`](global/europe/de/) | 18 | 1 | 0 | 1 | 2 | 1 |
| Ghana | GH | [`global/R4/gh`](global/R4/gh/) | 2 | 8 | 0 | 0 | 3 | 0 |
| Greece | GR | [`global/europe/gr`](global/europe/gr/) | 1 | 8 | 0 | 1 | 2 | 0 |
| Grenada | GD | [`global/americas/gd`](global/americas/gd/) | 1 | 4 | 0 | 4 | 8 | 0 |
| Guatemala | GT | [`global/americas/gt`](global/americas/gt/) | 6 | 4 | 0 | 2 | 9 | 0 |
| Guinea | GN | [`global/R4/gn`](global/R4/gn/) | 0 | 14 | 0 | 2 | 2 | 0 |
| Guinea-Bissau | GW | [`global/R4/gw`](global/R4/gw/) | 0 | 2 | 0 | 0 | 5 | 0 |
| Guyana | GY | [`global/americas/gy`](global/americas/gy/) | 2 | 3 | 0 | 4 | 9 | 0 |
| Haiti | HT | [`global/americas/ht`](global/americas/ht/) | 0 | 2 | 0 | 1 | 13 | 0 |
| Holy See | VA | [`global/europe/va`](global/europe/va/) | 0 | 0 | 0 | 0 | 12 | 0 |
| Honduras | HN | [`global/americas/hn`](global/americas/hn/) | 4 | 3 | 0 | 2 | 9 | 0 |
| Hong Kong | CN-HK | [`global/asiapac/cn-hk`](global/asiapac/cn-hk/) | 3 | 8 | 0 | 1 | 0 | 0 |
| Hungary | HU | [`global/europe/hu`](global/europe/hu/) | 4 | 6 | 0 | 1 | 4 | 0 |
| Iceland | IS | [`global/europe/is`](global/europe/is/) | 4 | 3 | 0 | 1 | 5 | 0 |
| India | IN | [`global/asiapac/in`](global/asiapac/in/) | 1 | 10 | 0 | 0 | 2 | 0 |
| Indonesia | ID | [`global/asiapac/id`](global/asiapac/id/) | 2 | 11 | 0 | 0 | 1 | 0 |
| Iran | IR | [`global/asiapac/ir`](global/asiapac/ir/) | 0 | 3 | 0 | 0 | 9 | 0 |
| Iraq | IQ | [`global/R5/iq`](global/R5/iq/) | 3 | 2 | 0 | 0 | 3 | 0 |
| Ireland | IE | [`global/europe/ie`](global/europe/ie/) | 2 | 9 | 0 | 1 | 3 | 0 |
| Israel | IL | [`global/R5/il`](global/R5/il/) | 2 | 6 | 0 | 0 | 1 | 0 |
| Italy | IT | [`global/europe/it`](global/europe/it/) | 9 | 7 | 0 | 1 | 3 | 0 |
| Jamaica | JM | [`global/americas/jm`](global/americas/jm/) | 1 | 6 | 0 | 3 | 8 | 0 |
| Japan | JP | [`global/asiapac/jp`](global/asiapac/jp/) | 15 | 4 | 0 | 0 | 0 | 0 |
| Jordan | JO | [`global/R5/jo`](global/R5/jo/) | 4 | 2 | 0 | 0 | 2 | 0 |
| Kazakhstan | KZ | [`global/asiapac/kz`](global/asiapac/kz/) | 5 | 8 | 0 | 0 | 0 | 0 |
| Kenya | KE | [`global/R4/ke`](global/R4/ke/) | 9 | 4 | 0 | 1 | 2 | 0 |
| Kiribati | KI | [`global/asiapac/ki`](global/asiapac/ki/) | 0 | 7 | 0 | 0 | 5 | 0 |
| Kosovo | XK | [`global/europe/xk`](global/europe/xk/) | 4 | 1 | 0 | 2 | 6 | 0 |
| Kuwait | KW | [`global/R5/kw`](global/R5/kw/) | 2 | 1 | 0 | 1 | 4 | 0 |
| Kyrgyzstan | KG | [`global/asiapac/kg`](global/asiapac/kg/) | 5 | 6 | 0 | 0 | 2 | 0 |
| Laos | LA | [`global/asiapac/la`](global/asiapac/la/) | 2 | 8 | 0 | 0 | 2 | 0 |
| Latvia | LV | [`global/europe/lv`](global/europe/lv/) | 8 | 3 | 1 | 3 | 1 | 0 |
| Lebanon | LB | [`global/R5/lb`](global/R5/lb/) | 4 | 2 | 0 | 0 | 3 | 0 |
| Lesotho | LS | [`global/R4/ls`](global/R4/ls/) | 1 | 4 | 0 | 1 | 1 | 0 |
| Liberia | LR | [`global/R4/lr`](global/R4/lr/) | 4 | 2 | 0 | 3 | 0 | 1 |
| Libya | LY | [`global/R5/ly`](global/R5/ly/) | 0 | 2 | 0 | 0 | 4 | 0 |
| Liechtenstein | LI | [`global/europe/li`](global/europe/li/) | 2 | 1 | 0 | 1 | 8 | 0 |
| Lithuania | LT | [`global/europe/lt`](global/europe/lt/) | 3 | 8 | 0 | 3 | 2 | 0 |
| Luxembourg | LU | [`global/europe/lu`](global/europe/lu/) | 9 | 3 | 0 | 1 | 4 | 0 |
| Macau | CN-MO | [`global/asiapac/cn-mo`](global/asiapac/cn-mo/) | 0 | 8 | 0 | 0 | 5 | 0 |
| Madagascar | MG | [`global/R4/mg`](global/R4/mg/) | 10 | 3 | 0 | 2 | 2 | 0 |
| Malawi | MW | [`global/R4/mw`](global/R4/mw/) | 2 | 3 | 0 | 1 | 1 | 0 |
| Malaysia | MY | [`global/asiapac/my`](global/asiapac/my/) | 0 | 13 | 0 | 0 | 4 | 0 |
| Maldives | MV | [`global/asiapac/mv`](global/asiapac/mv/) | 2 | 8 | 0 | 0 | 3 | 0 |
| Mali | ML | [`global/R4/ml`](global/R4/ml/) | 0 | 16 | 0 | 2 | 3 | 0 |
| Malta | MT | [`global/europe/mt`](global/europe/mt/) | 4 | 4 | 0 | 3 | 4 | 0 |
| Marshall Islands | MH | [`global/asiapac/mh`](global/asiapac/mh/) | 6 | 6 | 0 | 2 | 0 | 0 |
| Mauritania | MR | [`global/R4/mr`](global/R4/mr/) | 0 | 14 | 1 | 2 | 1 | 0 |
| Mauritius | MU | [`global/R4/mu`](global/R4/mu/) | 10 | 2 | 0 | 0 | 2 | 0 |
| Mexico | MX | [`global/americas/mx`](global/americas/mx/) | 9 | 1 | 0 | 4 | 5 | 1 |
| Micronesia | FM | [`global/asiapac/fm`](global/asiapac/fm/) | 3 | 7 | 0 | 1 | 3 | 0 |
| Moldova | MD | [`global/europe/md`](global/europe/md/) | 0 | 4 | 0 | 0 | 9 | 0 |
| Monaco | MC | [`global/europe/mc`](global/europe/mc/) | 2 | 0 | 0 | 0 | 10 | 0 |
| Mongolia | MN | [`global/asiapac/mn`](global/asiapac/mn/) | 4 | 7 | 0 | 3 | 0 | 0 |
| Montenegro | ME | [`global/europe/me`](global/europe/me/) | 5 | 2 | 0 | 0 | 7 | 0 |
| Morocco | MA | [`global/R5/ma`](global/R5/ma/) | 7 | 3 | 0 | 0 | 0 | 0 |
| Mozambique | MZ | [`global/R4/mz`](global/R4/mz/) | 4 | 3 | 0 | 0 | 1 | 0 |
| Myanmar | MM | [`global/asiapac/mm`](global/asiapac/mm/) | 2 | 8 | 0 | 0 | 3 | 0 |
| Namibia | NA | [`global/R4/na`](global/R4/na/) | 9 | 3 | 0 | 0 | 3 | 0 |
| Nauru | NR | [`global/asiapac/nr`](global/asiapac/nr/) | 6 | 8 | 0 | 0 | 0 | 0 |
| Nepal | NP | [`global/asiapac/np`](global/asiapac/np/) | 1 | 10 | 0 | 0 | 3 | 0 |
| Netherlands | NL | [`global/europe/nl`](global/europe/nl/) | 10 | 3 | 1 | 1 | 3 | 0 |
| New Zealand | NZ | [`global/asiapac/nz`](global/asiapac/nz/) | 4 | 6 | 0 | 0 | 1 | 0 |
| Nicaragua | NI | [`global/americas/ni`](global/americas/ni/) | 2 | 5 | 0 | 2 | 9 | 0 |
| Niger | NE | [`global/R4/ne`](global/R4/ne/) | 5 | 11 | 0 | 2 | 1 | 0 |
| Nigeria | NG | [`global/R4/ng`](global/R4/ng/) | 3 | 6 | 0 | 0 | 3 | 0 |
| North Korea | KP | [`global/asiapac/kp`](global/asiapac/kp/) | 0 | 9 | 0 | 0 | 3 | 0 |
| North Macedonia | MK | [`global/europe/mk`](global/europe/mk/) | 3 | 1 | 0 | 1 | 8 | 0 |
| Norway | NO | [`global/europe/no`](global/europe/no/) | 7 | 2 | 0 | 2 | 3 | 0 |
| Oman | OM | [`global/R5/om`](global/R5/om/) | 2 | 5 | 0 | 1 | 1 | 0 |
| Pakistan | PK | [`global/asiapac/pk`](global/asiapac/pk/) | 4 | 5 | 0 | 0 | 6 | 0 |
| Palau | PW | [`global/asiapac/pw`](global/asiapac/pw/) | 4 | 7 | 0 | 0 | 1 | 0 |
| Palestine | PS | [`global/R5/ps`](global/R5/ps/) | 1 | 2 | 0 | 1 | 3 | 0 |
| Panama | PA | [`global/americas/pa`](global/americas/pa/) | 2 | 4 | 0 | 3 | 10 | 0 |
| Papua New Guinea | PG | [`global/asiapac/pg`](global/asiapac/pg/) | 0 | 8 | 0 | 0 | 4 | 0 |
| Paraguay | PY | [`global/americas/py`](global/americas/py/) | 1 | 5 | 0 | 4 | 8 | 0 |
| Peru | PE | [`global/americas/pe`](global/americas/pe/) | 6 | 4 | 0 | 3 | 6 | 1 |
| Philippines | PH | [`global/asiapac/ph`](global/asiapac/ph/) | 5 | 10 | 0 | 0 | 0 | 0 |
| Poland | PL | [`global/europe/pl`](global/europe/pl/) | 14 | 3 | 1 | 1 | 2 | 0 |
| Portugal | PT | [`global/europe/pt`](global/europe/pt/) | 8 | 4 | 0 | 1 | 3 | 0 |
| Qatar | QA | [`global/R5/qa`](global/R5/qa/) | 4 | 2 | 0 | 1 | 1 | 0 |
| Romania | RO | [`global/europe/ro`](global/europe/ro/) | 5 | 1 | 1 | 4 | 2 | 0 |
| Russia | RU | [`global/europe/ru`](global/europe/ru/) | 4 | 0 | 0 | 2 | 8 | 0 |
| Rwanda | RW | [`global/R4/rw`](global/R4/rw/) | 5 | 5 | 0 | 0 | 1 | 0 |
| Saint Kitts and Nevis | KN | [`global/americas/kn`](global/americas/kn/) | 3 | 3 | 0 | 2 | 9 | 0 |
| Saint Lucia | LC | [`global/americas/lc`](global/americas/lc/) | 3 | 2 | 0 | 6 | 6 | 0 |
| Saint Vincent and the Grenadines | VC | [`global/americas/vc`](global/americas/vc/) | 2 | 4 | 0 | 2 | 9 | 0 |
| Samoa | WS | [`global/asiapac/ws`](global/asiapac/ws/) | 4 | 6 | 0 | 0 | 2 | 0 |
| San Marino | SM | [`global/europe/sm`](global/europe/sm/) | 4 | 0 | 0 | 0 | 9 | 0 |
| Sao Tome and Principe | ST | [`global/R4/st`](global/R4/st/) | 1 | 3 | 0 | 0 | 2 | 0 |
| Saudi Arabia | SA | [`global/R5/sa`](global/R5/sa/) | 4 | 5 | 0 | 1 | 1 | 0 |
| Senegal | SN | [`global/R4/sn`](global/R4/sn/) | 13 | 3 | 0 | 1 | 2 | 0 |
| Serbia | RS | [`global/europe/rs`](global/europe/rs/) | 7 | 0 | 0 | 0 | 6 | 0 |
| Seychelles | SC | [`global/R4/sc`](global/R4/sc/) | 4 | 1 | 0 | 0 | 3 | 0 |
| Sierra Leone | SL | [`global/R4/sl`](global/R4/sl/) | 4 | 5 | 0 | 0 | 0 | 0 |
| Singapore | SG | [`global/asiapac/sg`](global/asiapac/sg/) | 2 | 11 | 0 | 0 | 0 | 0 |
| Slovakia | SK | [`global/europe/sk`](global/europe/sk/) | 16 | 2 | 1 | 4 | 1 | 0 |
| Slovenia | SI | [`global/europe/si`](global/europe/si/) | 1 | 12 | 0 | 1 | 5 | 0 |
| Solomon Islands | SB | [`global/asiapac/sb`](global/asiapac/sb/) | 3 | 5 | 0 | 0 | 4 | 0 |
| Somalia | SO | [`global/R4/so`](global/R4/so/) | 2 | 0 | 0 | 0 | 3 | 0 |
| South Africa | ZA | [`global/R4/za`](global/R4/za/) | 4 | 10 | 0 | 1 | 1 | 0 |
| South Korea | KR | [`global/asiapac/kr`](global/asiapac/kr/) | 12 | 3 | 0 | 0 | 1 | 0 |
| South Sudan | SS | [`global/R4/ss`](global/R4/ss/) | 0 | 4 | 0 | 0 | 3 | 1 |
| Spain | ES | [`global/europe/es`](global/europe/es/) | 16 | 3 | 0 | 0 | 3 | 0 |
| Sri Lanka | LK | [`global/asiapac/lk`](global/asiapac/lk/) | 4 | 7 | 0 | 0 | 3 | 0 |
| Sudan | SD | [`global/R5/sd`](global/R5/sd/) | 0 | 1 | 0 | 0 | 7 | 0 |
| Suriname | SR | [`global/americas/sr`](global/americas/sr/) | 2 | 4 | 0 | 4 | 9 | 0 |
| Sweden | SE | [`global/europe/se`](global/europe/se/) | 7 | 5 | 0 | 2 | 2 | 1 |
| Switzerland | CH | [`global/europe/ch`](global/europe/ch/) | 13 | 3 | 0 | 1 | 5 | 1 |
| Syria | SY | [`global/R5/sy`](global/R5/sy/) | 0 | 1 | 0 | 0 | 9 | 0 |
| Taiwan | TW | [`global/asiapac/tw`](global/asiapac/tw/) | 8 | 7 | 0 | 0 | 1 | 0 |
| Tajikistan | TJ | [`global/asiapac/tj`](global/asiapac/tj/) | 6 | 4 | 0 | 0 | 2 | 0 |
| Tanzania | TZ | [`global/R4/tz`](global/R4/tz/) | 7 | 6 | 0 | 0 | 0 | 1 |
| Thailand | TH | [`global/asiapac/th`](global/asiapac/th/) | 3 | 11 | 0 | 1 | 0 | 0 |
| Timor-Leste | TL | [`global/asiapac/tl`](global/asiapac/tl/) | 5 | 8 | 0 | 0 | 0 | 0 |
| Togo | TG | [`global/R4/tg`](global/R4/tg/) | 13 | 2 | 0 | 2 | 1 | 0 |
| Tonga | TO | [`global/asiapac/to`](global/asiapac/to/) | 0 | 10 | 0 | 0 | 2 | 0 |
| Trinidad and Tobago | TT | [`global/americas/tt`](global/americas/tt/) | 2 | 4 | 0 | 7 | 5 | 0 |
| Tunisia | TN | [`global/R5/tn`](global/R5/tn/) | 7 | 4 | 0 | 0 | 1 | 0 |
| Turkiye | TR | [`global/R5/tr`](global/R5/tr/) | 8 | 5 | 0 | 0 | 1 | 0 |
| Turkmenistan | TM | [`global/asiapac/tm`](global/asiapac/tm/) | 0 | 8 | 0 | 0 | 4 | 0 |
| Tuvalu | TV | [`global/asiapac/tv`](global/asiapac/tv/) | 0 | 7 | 0 | 0 | 5 | 0 |
| Uganda | UG | [`global/R4/ug`](global/R4/ug/) | 5 | 5 | 0 | 0 | 1 | 0 |
| Ukraine | UA | [`global/europe/ua`](global/europe/ua/) | 5 | 2 | 0 | 2 | 5 | 0 |
| United Arab Emirates | AE | [`global/R5/ae`](global/R5/ae/) | 1 | 6 | 0 | 1 | 0 | 0 |
| United Kingdom | UK | [`global/europe/uk`](global/europe/uk/) | 10 | 4 | 0 | 2 | 2 | 0 |
| United States | US | [`global/americas/us`](global/americas/us/) | 10 | 6 | 0 | 4 | 2 | 0 |
| Uruguay | UY | [`global/americas/uy`](global/americas/uy/) | 3 | 4 | 0 | 2 | 9 | 0 |
| Uzbekistan | UZ | [`global/asiapac/uz`](global/asiapac/uz/) | 5 | 6 | 0 | 0 | 1 | 0 |
| Vanuatu | VU | [`global/asiapac/vu`](global/asiapac/vu/) | 0 | 9 | 0 | 0 | 4 | 0 |
| Venezuela | VE | [`global/americas/ve`](global/americas/ve/) | 4 | 1 | 0 | 1 | 12 | 0 |
| Viet Nam | VN | [`global/asiapac/vn`](global/asiapac/vn/) | 6 | 6 | 0 | 1 | 0 | 0 |
| Yemen | YE | [`global/R5/ye`](global/R5/ye/) | 0 | 0 | 0 | 0 | 8 | 0 |
| Zambia | ZM | [`global/R4/zm`](global/R4/zm/) | 3 | 8 | 0 | 1 | 2 | 0 |
| Zimbabwe | ZW | [`global/R4/zw`](global/R4/zw/) | 4 | 2 | 0 | 0 | 4 | 0 |
