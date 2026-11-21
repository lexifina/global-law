# Global tax in Lean

Personal income tax for 197 jurisdictions, written in [Lean 4](https://lean-lang.org) from each country's own law:
one shared tax kernel, and on top of it one small model per country. Each model takes a household (wages, other
income, a spouse, children) and returns the income tax, the employee's social contributions and the net income, with
the statute behind every rule cited next to it in the source. Lean checks every model, and proves properties of the
kernel once for all countries.

The work and what it found are described in the blog post
[Formalizing the tax code globally](https://lexifina.com/blog/formalizing-tax-code-globally).

- **Kernel** ([`kernel/`](kernel/)): the parts that tax systems share: bracket schedules, allowances, credits and
  their phase-outs, surcharges, social contribution ceilings, family units (individual, joint, splitting, family
  quotient), rounding rules. [`kernel/API.md`](kernel/API.md) documents every part.
- **192 country packages** in this folder, each its own Lake project that depends on the kernel: the 33 countries
  added in the first two rounds (in eight regional families) and 159 more from the world round (in 15 batches).
- **5 earlier models** (United States, France, United Kingdom, Germany, Japan) were written before the kernel existed.
  They are already published in this repository and are linked from the index below rather than copied: the US model
  in [`../TaxCode`](../TaxCode/), the French one in [`../FrTax`](../FrTax/), the UK one in
  [`../official-checks/uk-model`](../official-checks/uk-model/) and the German and Japanese ones in
  [`../five-tax-systems`](../five-tax-systems/). The comparison harness ran them through the same household format.

About 55,369 lines of country Lean (2,205 theorems) in 981 files, plus 2,939 lines of kernel. Lean's core library
only: no Mathlib, no `sorry`.

## Building

Install [elan](https://github.com/leanprover/elan); every project pins Lean 4 v4.35.0 in `lean-toolchain`. Each
country's `lean/` folder is a Lake project that finds the kernel by a relative path, so keep the folder layout as it
is:

```sh
cd kernel && lake build              # the kernel (and `lake build kfid` for the UK and German fidelity check)
cd ../anglo/au/lean && lake build    # one country: the library, its theorems and its executable
./build_all.sh                       # the kernel and all 192 country packages
```

A country's executable (`.lake/build/bin/<cc>tax`) reads one household per JSON line on standard input and writes one
result per line. Building a package also checks its theorems and its `#guard` tests, so a successful `lake build` is
the check.

## Layout

| Path | What it holds |
|---|---|
| [`kernel/`](kernel/) | `TaxKernel` (the shared parts, generic theorems in `TaxKernel/Theorems`, the `World` and `World2` parts added for the world round), [`API.md`](kernel/API.md), `Fidelity/` (the UK and German rules re-expressed with kernel parts and checked against the original models; [`RESULTS.md`](kernel/Fidelity/RESULTS.md)), `audit/` (the axioms every generic theorem uses, with Lean's printed answer in `*.out`), `examples/` (`zz/`, the toy country API.md walks through, and short uses of the kernel's parts) |
| `anglo/` `nordic/` `continental/` `emerging/` `germanic/` `baltic/` `central/` `southeast/` | The 33 countries of the first two rounds, one folder per country code |
| `world/B01-oecd5/` ... `world/B15-no-pit/` | The 159 countries of the world round, by batch |
| [`report/`](report/) | Cross-country syntheses of the first rounds: [`CROSS.md`](report/CROSS.md) and [`USEFUL20.md`](report/USEFUL20.md) (20 countries), [`CROSS38.md`](report/CROSS38.md) and [`USEFUL38.md`](report/USEFUL38.md) (38 countries) |
| [`world/loopholes/`](world/loopholes/) | The world loophole round: [`CROSS_WORLD.md`](world/loopholes/CROSS_WORLD.md), [`USEFUL_WORLD.md`](world/loopholes/USEFUL_WORLD.md), [`BLOG_LOOPHOLES.md`](world/loopholes/BLOG_LOOPHOLES.md) |
| [`TESTING.md`](TESTING.md) | The testing protocol: development and holdout sets, freezes, scoring, what counts as a fix |
| [`tests/FINAL_WORLD.md`](tests/FINAL_WORLD.md) | The final test results of the world round (aggregates; no test cases) |

Each country folder holds:

| File | What it is |
|---|---|
| `lean/` | The model: `<Cc>Tax/Params.lean` (the year's amounts, each with its citation), `Basic.lean` (the rules), `Theorems.lean`, often `Checks.lean` or `Verify.lean` (`#guard` tests against worked examples and the loophole round's checks), `Main.lean` (the executable) |
| `FINDINGS.md` | What the model found: loopholes, cliffs, errors in official material, faults in the statute, each with its evidence |
| `PROGRESS.md`, `USEFUL.md` | The build log, and the findings ranked by how useful they are |
| `results/summary.json` | One-record summary: year, access grade, Lean size, kernel parts used, validation, counts of findings |
| `SOURCES.md` | The law texts and official pages the model was built from: file name, SHA-256 and the address recorded for it |

## How each model was built

- **statute**: the act and the year's amounts are available as dated official law; the model follows them.
- **statute, partly official tables**: the act is available but some of the year's amounts sit in a finance law or
  notice that could not be reached, so those amounts come from the tax authority's published tables, cited as such
  and flagged in the source.
- **stated gap**: no current official text could be reached. The model is built from the latest reachable official
  text and says which version it uses, or, where nothing could be reached, returns "unsupported" for every household.

World-round grades: 76 statute, 78 statute with official tables, 5 stated gap.

## How the models were tested

Each package's own `#guard` tests and theorems run on every build. Beyond that, each model was scored against outside
referees, kept apart as development and holdout sets under [`TESTING.md`](TESTING.md): OECD Taxing Wages, the OECD Tax
Database, TaxBEN and Eurostat for the first 38 countries; open-source tax and payroll software, official calculators
and published tax tables for the world round. 164 of the 197 have at least one outside referee. The test data,
the holdout sets and the software are not in this repository (see below).

In the index, "referee set" means one referee scored in statute mode, and "exact of" counts cases where the model's
figure matched to the unit, development and holdout cases together.

## Index

| Country | Code | Folder | Built from | Tested against |
|---|---|---|---|---|
| Afghanistan | AF | [`world/B11-south-asia/af`](world/B11-south-asia/af/) | statute, partly official tables | software and datasets: 2 referee sets, 286 of 1,502 exact |
| Albania | AL | [`world/B04-europe-rest/al`](world/B04-europe-rest/al/) | statute | software: 2 referee sets, 1,849 of 6,000 exact |
| Algeria | DZ | [`world/B06-mena/dz`](world/B06-mena/dz/) | statute | software and datasets: 5 referee sets, 1,672 of 2,376 exact |
| Andorra | AD | [`world/B04-europe-rest/ad`](world/B04-europe-rest/ad/) | statute | software and datasets: 2 referee sets, 370 of 3,012 exact |
| Angola | AO | [`world/B09-southern-africa/ao`](world/B09-southern-africa/ao/) | statute, partly official tables | software: 1 referee set, 222 of 400 exact |
| Antigua and Barbuda | AG | [`world/B15-no-pit/ag`](world/B15-no-pit/ag/) | statute, partly official tables; no personal income tax | none (own `#guard` checks and theorems only) |
| Argentina | AR | [`world/B02-g20/ar`](world/B02-g20/ar/) | statute, partly official tables | software: 1 referee set, 759 of 3,000 exact |
| Armenia | AM | [`world/B05-former-ussr/am`](world/B05-former-ussr/am/) | statute | datasets: 1 referee set, 6 of 12 exact |
| Australia | AU | [`anglo/au`](anglo/au/) | statute | OECD/Eurostat + 8 other: 15 referee sets, 29,841 of 33,124 exact |
| Austria | AT | [`germanic/at`](germanic/at/) | statute | OECD/Eurostat + 1 other: 11 referee sets, 9,253 of 12,211 exact |
| Azerbaijan | AZ | [`world/B05-former-ussr/az`](world/B05-former-ussr/az/) | statute | datasets: 1 referee set, 123 of 800 exact |
| Bahamas | BS | [`world/B15-no-pit/bs`](world/B15-no-pit/bs/) | statute, partly official tables; no personal income tax | none (own `#guard` checks and theorems only) |
| Bahrain | BH | [`world/B15-no-pit/bh`](world/B15-no-pit/bh/) | statute, partly official tables; no personal income tax | none (own `#guard` checks and theorems only) |
| Bangladesh | BD | [`world/B11-south-asia/bd`](world/B11-south-asia/bd/) | statute | software: 5 referee sets, 4,946 of 6,400 exact |
| Barbados | BB | [`world/B13-caribbean/bb`](world/B13-caribbean/bb/) | statute, partly official tables | software and datasets: 3 referee sets, 386 of 1,159 exact |
| Belarus | BY | [`world/B05-former-ussr/by`](world/B05-former-ussr/by/) | statute | none (own `#guard` checks and theorems only) |
| Belgium | BE | [`germanic/be`](germanic/be/) | statute | OECD/Eurostat + 2 other: 13 referee sets, 4,509 of 13,419 exact |
| Belize | BZ | [`world/B13-caribbean/bz`](world/B13-caribbean/bz/) | statute | datasets: 1 referee set, 400 of 400 exact |
| Benin | BJ | [`world/B07-west-africa-fr-pt/bj`](world/B07-west-africa-fr-pt/bj/) | statute, partly official tables | software: 2 referee sets, 400 of 800 exact |
| Bhutan | BT | [`world/B11-south-asia/bt`](world/B11-south-asia/bt/) | statute | software and datasets: 3 referee sets, 115 of 3,699 exact |
| Bolivia | BO | [`world/B12-latin-america/bo`](world/B12-latin-america/bo/) | statute, partly official tables | software: 1 referee set, 627 of 3,000 exact |
| Bosnia and Herzegovina | BA | [`world/B04-europe-rest/ba`](world/B04-europe-rest/ba/) | statute | software: 1 referee set, 1,916 of 3,000 exact |
| Botswana | BW | [`world/B09-southern-africa/bw`](world/B09-southern-africa/bw/) | statute, partly official tables | software and datasets: 3 referee sets, 1,899 of 1,974 exact |
| Brazil | BR | [`world/B02-g20/br`](world/B02-g20/br/) | statute | software: 6 referee sets, 6,839 of 9,000 exact |
| Brunei | BN | [`world/B15-no-pit/bn`](world/B15-no-pit/bn/) | statute; no personal income tax | software and datasets: 2 referee sets, 396 of 405 exact |
| Bulgaria | BG | [`southeast/bg`](southeast/bg/) | statute | OECD/Eurostat + 1 other: 5 referee sets, 4,812 of 6,192 exact |
| Burkina Faso | BF | [`world/B07-west-africa-fr-pt/bf`](world/B07-west-africa-fr-pt/bf/) | statute, partly official tables | software: 2 referee sets, 132 of 1,200 exact |
| Burundi | BI | [`world/B08-central-africa-fr/bi`](world/B08-central-africa-fr/bi/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Cabo Verde | CV | [`world/B07-west-africa-fr-pt/cv`](world/B07-west-africa-fr-pt/cv/) | statute, partly official tables | software: 2 referee sets, 70 of 800 exact |
| Cambodia | KH | [`world/B03-asia-east-se/kh`](world/B03-asia-east-se/kh/) | statute | software and datasets: 8 referee sets, 1,801 of 12,002 exact |
| Cameroon | CM | [`world/B08-central-africa-fr/cm`](world/B08-central-africa-fr/cm/) | statute | software and datasets: 5 referee sets, 4,009 of 11,527 exact |
| Canada | CA | [`anglo/ca`](anglo/ca/) | statute | OECD/Eurostat + 2 other: 10 referee sets, 19,797 of 27,608 exact |
| Central African Republic | CF | [`world/B08-central-africa-fr/cf`](world/B08-central-africa-fr/cf/) | statute, partly official tables | software: 1 referee set, 90 of 400 exact |
| Chad | TD | [`world/B08-central-africa-fr/td`](world/B08-central-africa-fr/td/) | statute, partly official tables | software: 1 referee set, 76 of 400 exact |
| Chile | CL | [`world/B01-oecd5/cl`](world/B01-oecd5/cl/) | statute, partly official tables | software and datasets: 8 referee sets, 2,308 of 8,070 exact |
| China | CN | [`world/B02-g20/cn`](world/B02-g20/cn/) | statute | software: 44 referee sets, 32,021 of 67,500 exact |
| Colombia | CO | [`world/B01-oecd5/co`](world/B01-oecd5/co/) | statute, partly official tables | software and datasets: 9 referee sets, 4,862 of 12,171 exact |
| Comoros | KM | [`world/B08-central-africa-fr/km`](world/B08-central-africa-fr/km/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Congo | CG | [`world/B08-central-africa-fr/cg`](world/B08-central-africa-fr/cg/) | statute, partly official tables | software: 1 referee set, 94 of 400 exact |
| Costa Rica | CR | [`world/B01-oecd5/cr`](world/B01-oecd5/cr/) | statute | software and datasets: 7 referee sets, 5,033 of 8,772 exact |
| Cote d'Ivoire | CI | [`world/B07-west-africa-fr-pt/ci`](world/B07-west-africa-fr-pt/ci/) | statute | software: 2 referee sets, 284 of 800 exact |
| Croatia | HR | [`central/hr`](central/hr/) | statute | OECD/Eurostat + 2 other: 6 referee sets, 7,270 of 8,844 exact |
| Cuba | CU | [`world/B13-caribbean/cu`](world/B13-caribbean/cu/) | statute, partly official tables | software: 3 referee sets, 481 of 9,000 exact |
| Cyprus | CY | [`southeast/cy`](southeast/cy/) | statute | OECD/Eurostat + 2 other: 6 referee sets, 6,152 of 6,592 exact |
| Czechia | CZ | [`emerging/cz`](emerging/cz/) | statute | OECD/Eurostat + 2 other: 13 referee sets, 5,232 of 15,215 exact |
| DR Congo | CD | [`world/B08-central-africa-fr/cd`](world/B08-central-africa-fr/cd/) | statute, partly official tables | software: 1 referee set, 46 of 400 exact |
| Denmark | DK | [`nordic/dk`](nordic/dk/) | statute | OECD/Eurostat + 3 other: 11 referee sets, 6,897 of 15,133 exact |
| Djibouti | DJ | [`world/B08-central-africa-fr/dj`](world/B08-central-africa-fr/dj/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Dominica | DM | [`world/B13-caribbean/dm`](world/B13-caribbean/dm/) | statute, partly official tables | software and datasets: 2 referee sets, 273 of 3,941 exact |
| Dominican Republic | DO | [`world/B13-caribbean/do`](world/B13-caribbean/do/) | statute, partly official tables | software and datasets: 14 referee sets, 5,425 of 27,916 exact |
| Ecuador | EC | [`world/B12-latin-america/ec`](world/B12-latin-america/ec/) | statute | none (own `#guard` checks and theorems only) |
| Egypt | EG | [`world/B02-g20/eg`](world/B02-g20/eg/) | statute | software: 3 referee sets, 153 of 1,200 exact |
| El Salvador | SV | [`world/B12-latin-america/sv`](world/B12-latin-america/sv/) | statute, partly official tables | software: 2 referee sets, 4,975 of 6,000 exact |
| Equatorial Guinea | GQ | [`world/B08-central-africa-fr/gq`](world/B08-central-africa-fr/gq/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Eritrea | ER | [`world/B10-anglophone-africa/er`](world/B10-anglophone-africa/er/) | stated gap (no model: no accessible statute) | none (own `#guard` checks and theorems only) |
| Estonia | EE | [`baltic/ee`](baltic/ee/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 7,498 of 12,213 exact |
| Eswatini | SZ | [`world/B09-southern-africa/sz`](world/B09-southern-africa/sz/) | statute, partly official tables | software and datasets: 2 referee sets, 509 of 800 exact |
| Ethiopia | ET | [`world/B10-anglophone-africa/et`](world/B10-anglophone-africa/et/) | statute | software: 6 referee sets, 735 of 13,200 exact |
| Fiji | FJ | [`world/B14-pacific/fj`](world/B14-pacific/fj/) | statute | software and datasets: 6 referee sets, 7,566 of 11,300 exact |
| Finland | FI | [`baltic/fi`](baltic/fi/) | statute | OECD/Eurostat + 1 other: 11 referee sets, 6,045 of 12,199 exact |
| France | FR | [`FrTax`](../FrTax/) | statute (Code général des impôts, income 2025); pre-kernel model | OECD/Eurostat + 3 other: 14 referee sets, 12,837 of 19,186 exact |
| Gabon | GA | [`world/B08-central-africa-fr/ga`](world/B08-central-africa-fr/ga/) | statute | none (own `#guard` checks and theorems only) |
| Gambia | GM | [`world/B10-anglophone-africa/gm`](world/B10-anglophone-africa/gm/) | stated gap (no model: no accessible statute) | none (own `#guard` checks and theorems only) |
| Georgia | GE | [`world/B05-former-ussr/ge`](world/B05-former-ussr/ge/) | statute | software and datasets: 4 referee sets, 3,416 of 6,405 exact |
| Germany | DE | [`five-tax-systems/de`](../five-tax-systems/de/) | statute (EStG, SolZG, VZ 2025); pre-kernel model | OECD/Eurostat + 4 other: 15 referee sets, 25,745 of 29,803 exact |
| Ghana | GH | [`world/B10-anglophone-africa/gh`](world/B10-anglophone-africa/gh/) | statute | software: 5 referee sets, 455 of 10,200 exact |
| Greece | GR | [`southeast/gr`](southeast/gr/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 10,300 of 12,223 exact |
| Grenada | GD | [`world/B13-caribbean/gd`](world/B13-caribbean/gd/) | statute | software and datasets: 2 referee sets, 322 of 3,004 exact |
| Guatemala | GT | [`world/B12-latin-america/gt`](world/B12-latin-america/gt/) | statute, partly official tables | software: 3 referee sets, 1,780 of 3,800 exact |
| Guinea | GN | [`world/B07-west-africa-fr-pt/gn`](world/B07-west-africa-fr-pt/gn/) | statute, partly official tables | software: 1 referee set, 0 of 400 exact |
| Guinea-Bissau | GW | [`world/B07-west-africa-fr-pt/gw`](world/B07-west-africa-fr-pt/gw/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Guyana | GY | [`world/B13-caribbean/gy`](world/B13-caribbean/gy/) | statute, partly official tables | software and datasets: 2 referee sets, 1,169 of 1,900 exact |
| Haiti | HT | [`world/B13-caribbean/ht`](world/B13-caribbean/ht/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Holy See | VA | [`world/B15-no-pit/va`](world/B15-no-pit/va/) | statute, partly official tables; no personal income tax | none (own `#guard` checks and theorems only) |
| Honduras | HN | [`world/B12-latin-america/hn`](world/B12-latin-america/hn/) | statute | software and datasets: 2 referee sets, 2,839 of 4,500 exact |
| Hungary | HU | [`central/hu`](central/hu/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 11,502 of 12,210 exact |
| Iceland | IS | [`baltic/is`](baltic/is/) | statute | OECD/Eurostat: 7 referee sets, 997 of 6,089 exact |
| India | IN | [`world/B02-g20/in`](world/B02-g20/in/) | statute, partly official tables | software: 21 referee sets, 13,598 of 30,780 exact |
| Indonesia | ID | [`world/B02-g20/id`](world/B02-g20/id/) | statute | software and datasets: 12 referee sets, 6,398 of 21,401 exact |
| Iran | IR | [`world/B06-mena/ir`](world/B06-mena/ir/) | statute, partly official tables | software: 4 referee sets, 1,466 of 3,100 exact |
| Iraq | IQ | [`world/B06-mena/iq`](world/B06-mena/iq/) | statute, partly official tables | software and datasets: 2 referee sets, 509 of 2,011 exact |
| Ireland | IE | [`anglo/ie`](anglo/ie/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 6,567 of 12,248 exact |
| Israel | IL | [`world/B01-oecd5/il`](world/B01-oecd5/il/) | statute, partly official tables | software and datasets: 9 referee sets, 4,335 of 9,661 exact |
| Italy | IT | [`continental/it`](continental/it/) | statute | OECD/Eurostat + 1 other: 11 referee sets, 8,095 of 12,198 exact |
| Jamaica | JM | [`world/B13-caribbean/jm`](world/B13-caribbean/jm/) | statute, partly official tables | software: 3 referee sets, 1,826 of 3,962 exact |
| Japan | JP | [`five-tax-systems/jp`](../five-tax-systems/jp/) | statute (所得税法 and related acts, 令和7年分); pre-kernel model | OECD/Eurostat + 6 other: 13 referee sets, 2,184 of 27,170 exact |
| Jordan | JO | [`world/B06-mena/jo`](world/B06-mena/jo/) | statute, partly official tables | software and datasets: 3 referee sets, 995 of 1,200 exact |
| Kazakhstan | KZ | [`world/B05-former-ussr/kz`](world/B05-former-ussr/kz/) | statute | software: 3 referee sets, 2,755 of 5,614 exact |
| Kenya | KE | [`world/B10-anglophone-africa/ke`](world/B10-anglophone-africa/ke/) | statute | software: 5 referee sets, 246 of 5,000 exact |
| Kiribati | KI | [`world/B14-pacific/ki`](world/B14-pacific/ki/) | stated gap (no model: no accessible statute) | none (own `#guard` checks and theorems only) |
| Kosovo | XK | [`world/B04-europe-rest/xk`](world/B04-europe-rest/xk/) | statute | software and datasets: 3 referee sets, 6,398 of 6,400 exact |
| Kuwait | KW | [`world/B15-no-pit/kw`](world/B15-no-pit/kw/) | statute, partly official tables; no personal income tax | software and datasets: 3 referee sets, 111 of 3,005 exact |
| Kyrgyzstan | KG | [`world/B05-former-ussr/kg`](world/B05-former-ussr/kg/) | statute, partly official tables | software and datasets: 2 referee sets, 1,382 of 3,002 exact |
| Laos | LA | [`world/B03-asia-east-se/la`](world/B03-asia-east-se/la/) | statute | software: 1 referee set, 51 of 3,000 exact |
| Latvia | LV | [`baltic/lv`](baltic/lv/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 11,106 of 12,214 exact |
| Lebanon | LB | [`world/B06-mena/lb`](world/B06-mena/lb/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Lesotho | LS | [`world/B09-southern-africa/ls`](world/B09-southern-africa/ls/) | statute, partly official tables | software: 2 referee sets, 800 of 800 exact |
| Liberia | LR | [`world/B10-anglophone-africa/lr`](world/B10-anglophone-africa/lr/) | statute | software: 1 referee set, 56 of 400 exact |
| Libya | LY | [`world/B06-mena/ly`](world/B06-mena/ly/) | statute, partly official tables | software: 1 referee set, 0 of 800 exact |
| Liechtenstein | LI | [`world/B04-europe-rest/li`](world/B04-europe-rest/li/) | statute, partly official tables | datasets: 1 referee set, 12 of 12 exact |
| Lithuania | LT | [`baltic/lt`](baltic/lt/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 10,521 of 12,217 exact |
| Luxembourg | LU | [`germanic/lu`](germanic/lu/) | statute | OECD/Eurostat + 2 other: 13 referee sets, 6,612 of 16,759 exact |
| Madagascar | MG | [`world/B08-central-africa-fr/mg`](world/B08-central-africa-fr/mg/) | statute | software: 1 referee set, 0 of 400 exact |
| Malawi | MW | [`world/B09-southern-africa/mw`](world/B09-southern-africa/mw/) | statute, partly official tables | software: 1 referee set, 0 of 400 exact |
| Malaysia | MY | [`world/B03-asia-east-se/my`](world/B03-asia-east-se/my/) | statute, partly official tables | software: 8 referee sets, 6,742 of 13,500 exact |
| Maldives | MV | [`world/B11-south-asia/mv`](world/B11-south-asia/mv/) | statute | software: 1 referee set, 2,998 of 3,000 exact |
| Mali | ML | [`world/B07-west-africa-fr-pt/ml`](world/B07-west-africa-fr-pt/ml/) | statute, partly official tables | software and datasets: 2 referee sets, 95 of 440 exact |
| Malta | MT | [`southeast/mt`](southeast/mt/) | statute | OECD/Eurostat + 1 other: 5 referee sets, 1,543 of 6,192 exact |
| Marshall Islands | MH | [`world/B14-pacific/mh`](world/B14-pacific/mh/) | statute | none (own `#guard` checks and theorems only) |
| Mauritania | MR | [`world/B06-mena/mr`](world/B06-mena/mr/) | statute, partly official tables | software: 2 referee sets, 208 of 800 exact |
| Mauritius | MU | [`world/B09-southern-africa/mu`](world/B09-southern-africa/mu/) | statute | software and datasets: 5 referee sets, 1,862 of 5,400 exact |
| Mexico | MX | [`emerging/mx`](emerging/mx/) | statute | OECD/Eurostat + 1 other: 8 referee sets, 2,775 of 6,107 exact |
| Micronesia | FM | [`world/B14-pacific/fm`](world/B14-pacific/fm/) | statute | none (own `#guard` checks and theorems only) |
| Moldova | MD | [`world/B05-former-ussr/md`](world/B05-former-ussr/md/) | statute | software: 1 referee set, 0 of 400 exact |
| Monaco | MC | [`world/B15-no-pit/mc`](world/B15-no-pit/mc/) | statute, partly official tables; no personal income tax | software: 3 referee sets, 263 of 4,500 exact |
| Mongolia | MN | [`world/B03-asia-east-se/mn`](world/B03-asia-east-se/mn/) | statute | software: 5 referee sets, 1,035 of 10,200 exact |
| Montenegro | ME | [`world/B04-europe-rest/me`](world/B04-europe-rest/me/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Morocco | MA | [`world/B06-mena/ma`](world/B06-mena/ma/) | statute, partly official tables | software and datasets: 5 referee sets, 1,053 of 3,101 exact |
| Mozambique | MZ | [`world/B09-southern-africa/mz`](world/B09-southern-africa/mz/) | statute, partly official tables | datasets: 1 referee set, 40 of 80 exact |
| Myanmar | MM | [`world/B03-asia-east-se/mm`](world/B03-asia-east-se/mm/) | statute, partly official tables | software: 1 referee set, 278 of 400 exact |
| Namibia | NA | [`world/B09-southern-africa/na`](world/B09-southern-africa/na/) | statute | software: 2 referee sets, 400 of 800 exact |
| Nauru | NR | [`world/B14-pacific/nr`](world/B14-pacific/nr/) | statute | none (own `#guard` checks and theorems only) |
| Nepal | NP | [`world/B11-south-asia/np`](world/B11-south-asia/np/) | statute | software: 8 referee sets, 6,752 of 16,500 exact |
| Netherlands | NL | [`continental/nl`](continental/nl/) | statute | OECD/Eurostat + 1 other: 11 referee sets, 5,121 of 12,153 exact |
| New Zealand | NZ | [`anglo/nz`](anglo/nz/) | statute | OECD/Eurostat + 2 other: 9 referee sets, 7,926 of 11,203 exact |
| Nicaragua | NI | [`world/B12-latin-america/ni`](world/B12-latin-america/ni/) | statute, partly official tables | software: 8 referee sets, 15,863 of 16,600 exact |
| Niger | NE | [`world/B07-west-africa-fr-pt/ne`](world/B07-west-africa-fr-pt/ne/) | statute, partly official tables | software: 1 referee set, 1 of 400 exact |
| Nigeria | NG | [`world/B02-g20/ng`](world/B02-g20/ng/) | statute | software: 10 referee sets, 3,348 of 15,100 exact |
| North Korea | KP | [`world/B15-no-pit/kp`](world/B15-no-pit/kp/) | statute, partly official tables; no personal income tax | none (own `#guard` checks and theorems only) |
| North Macedonia | MK | [`world/B04-europe-rest/mk`](world/B04-europe-rest/mk/) | statute, partly official tables | software and datasets: 2 referee sets, 159 of 2,197 exact |
| Norway | NO | [`nordic/no`](nordic/no/) | statute | OECD/Eurostat: 8 referee sets, 3,900 of 6,021 exact |
| Oman | OM | [`world/B15-no-pit/om`](world/B15-no-pit/om/) | statute; no personal income tax | software: 2 referee sets, 291 of 800 exact |
| Pakistan | PK | [`world/B11-south-asia/pk`](world/B11-south-asia/pk/) | statute | software: 11 referee sets, 14,033 of 16,500 exact |
| Palau | PW | [`world/B14-pacific/pw`](world/B14-pacific/pw/) | statute | datasets: 1 referee set, 15 of 15 exact |
| Palestine | PS | [`world/B06-mena/ps`](world/B06-mena/ps/) | statute | software: 1 referee set, 0 of 1,500 exact |
| Panama | PA | [`world/B12-latin-america/pa`](world/B12-latin-america/pa/) | statute, partly official tables | software: 3 referee sets, 95 of 3,800 exact |
| Papua New Guinea | PG | [`world/B14-pacific/pg`](world/B14-pacific/pg/) | statute | software: 2 referee sets, 2,780 of 3,000 exact |
| Paraguay | PY | [`world/B12-latin-america/py`](world/B12-latin-america/py/) | statute | software: 2 referee sets, 224 of 1,900 exact |
| Peru | PE | [`world/B12-latin-america/pe`](world/B12-latin-america/pe/) | statute | software: 2 referee sets, 3,000 of 3,000 exact |
| Philippines | PH | [`world/B03-asia-east-se/ph`](world/B03-asia-east-se/ph/) | statute | software and datasets: 24 referee sets, 21,032 of 36,810 exact |
| Poland | PL | [`emerging/pl`](emerging/pl/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 8,435 of 12,217 exact |
| Portugal | PT | [`continental/pt`](continental/pt/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 9,857 of 12,213 exact |
| Qatar | QA | [`world/B15-no-pit/qa`](world/B15-no-pit/qa/) | statute; no personal income tax | software: 2 referee sets, 1,738 of 1,900 exact |
| Romania | RO | [`southeast/ro`](southeast/ro/) | statute | OECD/Eurostat + 2 other: 6 referee sets, 3,520 of 8,230 exact |
| Russia | RU | [`world/B02-g20/ru`](world/B02-g20/ru/) | statute | software and datasets: 15 referee sets, 15,654 of 19,506 exact |
| Rwanda | RW | [`world/B10-anglophone-africa/rw`](world/B10-anglophone-africa/rw/) | statute | software and datasets: 7 referee sets, 2,054 of 10,604 exact |
| Saint Kitts and Nevis | KN | [`world/B15-no-pit/kn`](world/B15-no-pit/kn/) | statute; no personal income tax | software and datasets: 3 referee sets, 2,338 of 6,005 exact |
| Saint Lucia | LC | [`world/B13-caribbean/lc`](world/B13-caribbean/lc/) | statute | software and datasets: 2 referee sets, 1,567 of 3,400 exact |
| Saint Vincent and the Grenadines | VC | [`world/B13-caribbean/vc`](world/B13-caribbean/vc/) | stated gap (no model: no accessible statute) | none (own `#guard` checks and theorems only) |
| Samoa | WS | [`world/B14-pacific/ws`](world/B14-pacific/ws/) | statute | software and datasets: 2 referee sets, 474 of 1,050 exact |
| San Marino | SM | [`world/B04-europe-rest/sm`](world/B04-europe-rest/sm/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Sao Tome and Principe | ST | [`world/B07-west-africa-fr-pt/st`](world/B07-west-africa-fr-pt/st/) | stated gap (latest reachable text) | none (own `#guard` checks and theorems only) |
| Saudi Arabia | SA | [`world/B15-no-pit/sa`](world/B15-no-pit/sa/) | statute, partly official tables; no personal income tax | software: 5 referee sets, 1,790 of 5,300 exact |
| Senegal | SN | [`world/B07-west-africa-fr-pt/sn`](world/B07-west-africa-fr-pt/sn/) | statute | software: 2 referee sets, 1,556 of 1,900 exact |
| Serbia | RS | [`world/B04-europe-rest/rs`](world/B04-europe-rest/rs/) | statute, partly official tables | software: 2 referee sets, 741 of 4,884 exact |
| Seychelles | SC | [`world/B09-southern-africa/sc`](world/B09-southern-africa/sc/) | statute | software and datasets: 3 referee sets, 800 of 1,200 exact |
| Sierra Leone | SL | [`world/B10-anglophone-africa/sl`](world/B10-anglophone-africa/sl/) | statute | software: 4 referee sets, 9,125 of 12,000 exact |
| Singapore | SG | [`world/B03-asia-east-se/sg`](world/B03-asia-east-se/sg/) | statute, partly official tables | software: 5 referee sets, 5,523 of 11,009 exact |
| Slovakia | SK | [`central/sk`](central/sk/) | statute | OECD/Eurostat + 2 other: 13 referee sets, 8,747 of 12,228 exact |
| Slovenia | SI | [`central/si`](central/si/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 8,002 of 12,221 exact |
| Solomon Islands | SB | [`world/B14-pacific/sb`](world/B14-pacific/sb/) | statute | datasets: 1 referee set, 1,032 of 1,032 exact |
| Somalia | SO | [`world/B10-anglophone-africa/so`](world/B10-anglophone-africa/so/) | statute | datasets: 1 referee set, 3 of 3 exact |
| South Africa | ZA | [`world/B02-g20/za`](world/B02-g20/za/) | statute, partly official tables | software and datasets: 10 referee sets, 20,917 of 23,516 exact |
| South Korea | KR | [`emerging/kr`](emerging/kr/) | statute | OECD/Eurostat + 2 other: 10 referee sets, 8,508 of 14,709 exact |
| South Sudan | SS | [`world/B10-anglophone-africa/ss`](world/B10-anglophone-africa/ss/) | statute | software: 1 referee set, 5 of 3,000 exact |
| Spain | ES | [`continental/es`](continental/es/) | statute | OECD/Eurostat + 1 other: 12 referee sets, 3,760 of 10,230 exact |
| Sri Lanka | LK | [`world/B11-south-asia/lk`](world/B11-south-asia/lk/) | statute | software and datasets: 10 referee sets, 15,406 of 15,904 exact |
| Sudan | SD | [`world/B10-anglophone-africa/sd`](world/B10-anglophone-africa/sd/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Suriname | SR | [`world/B13-caribbean/sr`](world/B13-caribbean/sr/) | statute, partly official tables | software: 3 referee sets, 1,684 of 3,800 exact |
| Sweden | SE | [`nordic/se`](nordic/se/) | statute | OECD/Eurostat + 2 other: 12 referee sets, 12,208 of 18,861 exact |
| Switzerland | CH | [`germanic/ch`](germanic/ch/) | statute | OECD/Eurostat: 8 referee sets, 1,440 of 6,130 exact |
| Syria | SY | [`world/B06-mena/sy`](world/B06-mena/sy/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Taiwan | TW | [`world/B02-g20/tw`](world/B02-g20/tw/) | statute | software and datasets: 5 referee sets, 4,222 of 6,280 exact |
| Tajikistan | TJ | [`world/B05-former-ussr/tj`](world/B05-former-ussr/tj/) | statute | software and datasets: 2 referee sets, 468 of 800 exact |
| Tanzania | TZ | [`world/B10-anglophone-africa/tz`](world/B10-anglophone-africa/tz/) | statute | software and datasets: 6 referee sets, 4,951 of 9,810 exact |
| Thailand | TH | [`world/B03-asia-east-se/th`](world/B03-asia-east-se/th/) | statute | software: 6 referee sets, 6,377 of 10,500 exact |
| Timor-Leste | TL | [`world/B03-asia-east-se/tl`](world/B03-asia-east-se/tl/) | statute | none (own `#guard` checks and theorems only) |
| Togo | TG | [`world/B07-west-africa-fr-pt/tg`](world/B07-west-africa-fr-pt/tg/) | statute, partly official tables | software: 4 referee sets, 157 of 3,100 exact |
| Tonga | TO | [`world/B14-pacific/to`](world/B14-pacific/to/) | statute, partly official tables | datasets: 1 referee set, 169 of 1,500 exact |
| Trinidad and Tobago | TT | [`world/B13-caribbean/tt`](world/B13-caribbean/tt/) | statute | software: 1 referee set, 2,933 of 3,225 exact |
| Tunisia | TN | [`world/B06-mena/tn`](world/B06-mena/tn/) | statute, partly official tables | software: 3 referee sets, 2,664 of 4,200 exact |
| Turkiye | TR | [`world/B01-oecd5/tr`](world/B01-oecd5/tr/) | statute | software and datasets: 10 referee sets, 7,634 of 8,639 exact |
| Turkmenistan | TM | [`world/B05-former-ussr/tm`](world/B05-former-ussr/tm/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Tuvalu | TV | [`world/B14-pacific/tv`](world/B14-pacific/tv/) | statute | none (own `#guard` checks and theorems only) |
| Uganda | UG | [`world/B10-anglophone-africa/ug`](world/B10-anglophone-africa/ug/) | statute | software and datasets: 4 referee sets, 1,056 of 1,602 exact |
| Ukraine | UA | [`world/B05-former-ussr/ua`](world/B05-former-ussr/ua/) | statute | software: 3 referee sets, 1,398 of 1,600 exact |
| United Arab Emirates | AE | [`world/B15-no-pit/ae`](world/B15-no-pit/ae/) | statute, partly official tables; no personal income tax | software: 8 referee sets, 6,062 of 12,000 exact |
| United Kingdom | UK | [`official-checks/uk-model`](../official-checks/uk-model/) | statute (2025-26); pre-kernel model | OECD/Eurostat + 2 other: 11 referee sets, 16,887 of 19,616 exact |
| United States | US | [`TaxCode/Individual`](../TaxCode/Individual/) | statute (Internal Revenue Code, tax year 2025); pre-kernel model | OECD/Eurostat + 5 other: 11 referee sets, 128,050 of 135,638 exact |
| Uruguay | UY | [`world/B12-latin-america/uy`](world/B12-latin-america/uy/) | statute, partly official tables | software and datasets: 2 referee sets, 1,322 of 3,800 exact |
| Uzbekistan | UZ | [`world/B05-former-ussr/uz`](world/B05-former-ussr/uz/) | statute | software: 1 referee set, 367 of 3,000 exact |
| Vanuatu | VU | [`world/B15-no-pit/vu`](world/B15-no-pit/vu/) | statute; no personal income tax | none (own `#guard` checks and theorems only) |
| Venezuela | VE | [`world/B12-latin-america/ve`](world/B12-latin-america/ve/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Viet Nam | VN | [`world/B03-asia-east-se/vn`](world/B03-asia-east-se/vn/) | statute, partly official tables | software: 15 referee sets, 7,565 of 43,500 exact |
| Yemen | YE | [`world/B06-mena/ye`](world/B06-mena/ye/) | statute, partly official tables | none (own `#guard` checks and theorems only) |
| Zambia | ZM | [`world/B09-southern-africa/zm`](world/B09-southern-africa/zm/) | statute, partly official tables | software and datasets: 4 referee sets, 797 of 6,401 exact |
| Zimbabwe | ZW | [`world/B09-southern-africa/zw`](world/B09-southern-africa/zw/) | statute, partly official tables | datasets: 1 referee set, 19 of 19 exact |

## What is not here, and why

- **The law texts.** Every rule cites its provision in the Lean source, and each country's `SOURCES.md` lists the
  files the model was built from with their SHA-256 and recorded address. The texts themselves are left out: some were
  read from secondary hosts, and many publishers do not allow redistribution. The statutes of most countries are in
  this repository's country submodules (`lexifina/<country>-law`).
- **The test data.** The referee datasets, the generated grids of households, the holdout sets and the per-case
  ledger are left out, so the holdout sets stay usable and because much of the data belongs to its publishers. Only
  aggregate results are published ([`tests/FINAL_WORLD.md`](tests/FINAL_WORLD.md) and each `summary.json`).
- **Third-party software.** The open-source tax and payroll programs the models were tested against, and their
  outputs, are not copied: many have no licence.
- **Harness and scratch.** The Python harness that ran the models on the referees, build output and working files.

## Licence and citation

Like the rest of this repository, the Lean code and documents here are dedicated to the public domain under
[CC0 1.0](../../LICENSE.md). The law they encode is not covered by that dedication.

To cite this work, name the commit you used:

```bibtex
@misc{lexifina_global_tax_lean_2026,
  author       = {{Lexifina}},
  title        = {Global tax in {Lean}: a shared tax kernel and personal income tax models for 197 jurisdictions},
  year         = {2026},
  howpublished = {\url{https://github.com/lexifina/global-law/tree/main/lean-proofs/global-tax}},
  note         = {Commit <sha>. See also https://lexifina.com/blog/formalizing-tax-code-globally}
}
```

In text: Lexifina (2026), *Global tax in Lean*, github.com/lexifina/global-law, `lean-proofs/global-tax`, commit
`<sha>`.
