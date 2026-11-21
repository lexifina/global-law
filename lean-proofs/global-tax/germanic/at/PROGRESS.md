# AT (Austria, Veranlagung 2025): progress

Owner: AT worker (germanic family). Contracts: `~/cmp20/CONTRACT38.md` + `~/cmp20/CONTRACT20.md`. Updated: 2026-11-19 (final).

## Status: done (7/7)

| Step | What | Status / files |
|---|---|---|
| 1 | Model `lean/` (lib AtTax, exe attax, on TaxKernel) | DONE: tariff, Familienbonus, AVAB/AEAB, VAB+Zuschlag, PAB, refunds (§ 33 Abs. 8), Kindermehrbetrag, 13th/14th salary (§ 67, § 41 Abs. 4), KESt + Regelbesteuerungsoption, Gewinnfreibetrag, Veranlagungsfreibetrag, Spenden; ASVG/AMPFG/AK/WBF, pension KV, GSVG; FLAG |
| 2 | Validation | DONE: OECD 48/56 within 1 € (55/56 with `--oecd`, F2); BMF Brutto-Netto-Rechner 120 cases (employees 90/90 to the cent; pensioners explained by F5, 30/30 with `--bmf-pension-april`); BMF Kindermehrbetrag limits 4 cases (F6); Eurostat sanity 41/52 |
| 3 | Proofs | DONE: `lean/AtTax/Theorems.lean`, no sorry |
| 4 | Known loopholes | DONE: `CATALOGUE.md` (24 / 16 / 8), `harness/recreate.py`, `runs/recreate.json` |
| 5 | New loopholes | DONE: `NOVEL.md` (N1 Kindermehrbetrag partner cliff; N2 lead); kernel scanners `results/search/SUMMARY.md` |
| 6 | Gov / statute errors | DONE: FINDINGS F2, F3, F5, F6, F17 (gov), F7, F12, F13 (statute) |
| 7 | `USEFUL.md` | DONE |

## How to run
* Build: `cd ~/cmp20/germanic/at/lean && export PATH=$HOME/.elan/bin:$PATH && lake build`
* Exe: `.lake/build/bin/attax [--oecd] [--withholding] [--kmb-literal] [--payments=12|13|14] [--fbp=a1|a2|half]
  [--bmf-pension-april] [--no-gfb] [--no-vfb] [--no-regel]` (contract JSONL; household extensions `atPayments`,
  `atChildrenInEducation`). Detail lines: CGTC, CGITLETC, taxCents, socialCents, benefitsCents, tariffTax, …
* OECD: `python3 ~/cmp20/germanic/oecd/check.py AT [--args=--oecd]`
* BMF calculator: `python3 harness/bmf_grid.py [--offline] [--args "--bmf-pension-april"]` (cache `refs/bmf_bnr/`)
* Catalogue + owner-manager: `python3 harness/recreate.py`; kernel scanners:
  `cd ~/cmp20/harness/search && python3 run_all.py AT --out ~/cmp20/germanic/at/results/search`
* Local working copy on the laptop scratchpad was pushed with `sync.sh`; lean1 is canonical.

## Model choices (documented in the Lean docstrings)
14 payments by default; children under 18 get Familienbeihilfe (18-23 with `atChildrenInEducation`); FB recipient for
§ 33 Abs. 7 lit. b = second adult; Kindermehrbetrag per the BMF reading (F7); Freigrenze of § 41 Abs. 4 on the gross
amount (F8); AV rate on Sonderzahlungen from the instalment; WBF 0,5 % (Land laws not read; OECD agrees); GSVG
Versicherungsgrenze applied to all self-employed; interest = bank deposits (25 %).

## Open (if anyone resumes)
* Not modelled: Pendlerpauschale/-euro, Unterhaltsabsetzbetrag, § 68 supplements, Sachbezüge, investment GFB,
  Selbständigenvorsorge 1,53 %, Ausgleichszulage KV 5,1 %, Kirchenbeitrag, außergewöhnliche Belastungen.
* N2 (pensioner couple 51,8 %) novelty not searched (web searches left: 2).
* Eurostat CTGG 5 581,40 € for two children not reproduced (sanity referee only).
