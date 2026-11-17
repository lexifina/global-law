# IRS guidance checked against the statute

An audit, run on 17 November 2026, of what the IRS publishes against the words of the Internal Revenue Code in force
for each year. The IRS's figures (rates, inflation-adjusted amounts, tables, actuarial factors, penalty minimums) and
its citations of the Code were harvested from its own sites, recomputed from Title 26 in Lean 4 or in exact Python,
and every disagreement was read by hand in the IRS's document before it was counted.

[penalties/](penalties/README.md) applies the same method to the sanctions the IRS imposes, as the Tax Court's opinions
and entered decisions record them.

## Results

- **About 906,000 published figures checked.** A first pass over 12 collections (revenue rulings, revenue
  procedures, notices, announcements, letter rulings, technical advice, Chief Counsel advice, regulations, the Internal
  Revenue Manual, publications and forms, legal memoranda, historical material) checked 437,684 figures; a second pass
  over sources the first did not reach (the Cumulative Bulletins 1986-1995, the annual 26 CFR editions 1997-2016,
  25,918 written determinations, the IRS's open-source tax software, Statistics of Income tables, withholding tables)
  checked about 468,400 more. 532,531 citations of the Code were checked as well.
- **Where the IRS computes by formula, it is almost always right.** 247,352 Tax Table entries (30 years), 129,579 EIC
  Table cells, 22,080 interest factors, 6,038 rate rows, 14,512 actuarial factors (and 372,900 more in the annual CFR
  editions), 153 retirement limits and 639 of 657 indexed amounts all match the statute.
- **14 verified departures** ([FINDINGS.md](FINDINGS.md), Part A), one of them material:

| # | Document | Printed | The statute gives |
|---|---|---|---|
| A1 | Rev. Rul. 2012-9: March 2012 long-term tax-exempt rate for §382 | 3.55% | 3.47% (§382(f)(1)); kept for ownership changes on 1-20 March 2012 |
| A2 | Rev. Proc. 2025-32: 2026 head-of-household standard deduction | $24,150 | $24,175 (§63(c)(7)(B)(ii)) |
| A3 | Rev. Procs. 2025-32, 2026-35: estates and trusts, first bracket, 2026 and 2027 | $3,300, $3,400 | $3,250, $3,350 (§1(j)(3)(B)(i)) |
| A4 | Four monthly AFR rulings, Bulletin editions (2014, 2018) | e.g. §7520 rate .4% | 3.4% (the advance release) |
| A5 | Failure-to-file minimum, Rev. Procs. 2020-45 to 2026-35 and the IRM | a year's lag | §6651(j) (a reading) |
| A6 | Wage-levy and disability-trust exemptions 2019-2026 | rounded amount | §6334(d)(4)(C) rounds the increase |
| A7 | Rev. Proc. 2009-21 (Bulletin edition): joint no-child EIC threshold | $21,420 | $12,470 |
| A8, A9 | Rev. Ruls. 86-94 and 87-68 (Cumulative Bulletins) | 7.96%, 9.97% | 7.98%, 9.87% |
| A10, A14 | Letter rulings 202219006-008 and 202116006 | repealed sections cited | §30D(d)(1)(A); §2056(b)(7), §2611(a) |
| A11 | Tax Withholding Estimator (2026 code): qualifying-relative income limit | $5,200 | $5,300 |
| A12 | SOI Historical Table 23: married couple's exemptions 2016-2017 | $8,010 | $8,100 |
| A13 | Letter rulings 201602001 and 201432008: GST exemption | $5,012,000; $1,000,0000 | no year had either |

  Part B lists 15 earlier findings in the same collections, from the form and worksheet models in
  [../TaxCode/Forms/](../TaxCode/Forms/FINDINGS.md), [../TaxCode/Big/](../TaxCode/Big) and
  [../TaxCode/Indexing/](../TaxCode/Indexing/FINDINGS.md).
- **29 candidates rejected** after verification, each with the reason ([REJECTED.md](REJECTED.md)): readings the
  words allow, statutes changed after publication, parse and OCR artifacts, and 5 errors in the audit's own first pass.

Coverage by collection, what each check does and what was out of reach: [RESULTS.md](RESULTS.md).

## How a figure is checked

1. The script for a source extracts every printed figure with its year and context into JSON.
2. A generator writes the figures and the statute's rule for that year into a Lean file, which recomputes each one with
   exact natural-number arithmetic and prints a line per figure (`PASS` or `FAIL`, with both values).
3. Each `FAIL` is read in the IRS's document, the statute is read as in force on the date (`tools/usc_at.sh SECTION
   DATE` prints a section of Title 26 from the US Code history), later guidance is searched for a correction or a
   change, and only then is it counted, rejected or explained.
4. For the findings, the decisive arithmetic is restated as theorems that the Lean kernel checks:
   [lean/Audit/Flags2.lean](lean/Audit/Flags2.lean) (A2, A3) and [lean/flags/AfrFlags.lean](lean/flags/AfrFlags.lean)
   (A1, A4).

| Check | Scripts, in order | Lean | Output |
|---|---|---|---|
| Monthly AFR rulings 1996-2026 (§§1274, 382, 42, 7520, 642(c)(5)) | `afr/parse_afr.py`, `afr/gen_lean.py` | `lean/afr/Run.lean` | `afr/lean_out.tsv.gz` |
| AFR rulings in the Cumulative Bulletins 1984-1995 | `afr/cb_afr2.py`, `afr/cb_afr_early.py`, `afr/gen_lean_cb.py`, `afr/gen_lean_cb_mult.py` | `lean/afr/RunCB.lean`, `RunCBMult.lean` | `afr/lean_out_cb*.tsv` |
| Quarterly §6621 interest rates and factors | `q6621/parse_q.py`, `q6621/gen_lean.py` (and `cb_q.py` for 1986-1995) | `lean/q6621/Run.lean`, `RunCB.lean` | `q6621/lean_out*.tsv` |
| Inflation-adjusted amounts 1997-2027 | `indexing/extract.py`, `brackets.py`, `amt.py`, `gen_lean.py` | `lean/Audit/IndexRun.lean` | `indexing/lean_out.tsv` |
| Retirement-plan limits (§415(d) and others) | `cola/extract.py`, `cola/gen_lean.py` | `lean/Audit/ColaRun.lean` | `cola/lean_out.tsv` |
| Estate and gift actuarial tables (26 CFR 20.2031-7) | `cfr/actuarial.py`, `cfr/actuarial_gen.py` | `lean/Audit/Actuarial.lean` | `cfr/actuarial_out.txt` |
| Tax Table and Tax Rate Schedules 1995-2024 | `tools/fetch.py -f tables/urls.txt`, `tables/parse_tables.py`, `tables/gen_lean.py` | `lean/Audit/TaxTables.lean` (generated) | `tables/lean_out.tsv` |
| EIC Table 2009-2024 | `tables/eic_parse.py`, `tables/eic_gen.py`, `tables/eic_gen_2009.py` | `lean/Audit/EicTables.lean`, `EicTables2009.lean` (generated) | `tables/eic_out.txt` |

The other checks are exact Python (`fractions`), named in [RESULTS.md](RESULTS.md): historical Table S, the IRS's own
actuarial files, segment rates, covered compensation, withholding tables (`withholding/`), the IRS's open-source tax
software (`public/`), SOI tables (`soi/`), standard deduction charts (`prior/`), written determinations (`wd/`), table
totals and Code citations (`inventory/`, `cfr/xref.py`, `irm/xref.py`, `src/govinfo/cb_cites.py`).

## Reproduce

Requirements: Python 3 with `requests`, `pypdf` and `openpyxl`; `pdftotext` and `pdfinfo` (poppler); git; and Lean 4
through [elan](https://github.com/leanprover/elan) (the toolchain is pinned in `../lean-toolchain`).

```sh
cd lean-proofs/irs-audit
export IRS_AUDIT=$PWD USC_HISTORY=$HOME/united-states-law     # the scripts' working folder and the Code history
git clone https://github.com/lexifina/united-states-law $USC_HISTORY
git clone https://github.com/lexifina/united-states-irs-guidance-law src/irs-guidance   # the Bulletin 1996-2026
git clone --filter=blob:none https://github.com/lexifina/united-states-cfr-law src/cfr  # 26 CFR in force
gunzip -k tables/*.json.gz afr/lean_out.tsv.gz wd/checks.json.gz                       # the larger outputs
```

The fetchers take what they need from the public sources and keep it in `cache/<host>/<path>`, logging every request
in `cache/_status.tsv` (the cache and the downloaded corpora are listed in `.gitignore`; they are not published):

- [irs.gov](https://www.irs.gov) `/pub/` (revenue rulings and procedures, Bulletins, prior-year publications and forms,
  written determinations, Chief Counsel documents, SOI tables) and [the IRM](https://www.irs.gov/irm): `tools/fetch.py`
  (sequential, 1.5 s apart, generic user agent, robots.txt respected), `tools/irs_harvest.py`, `tools/harvest_queue.py`,
  `tools/c11_harvest.py`, `irm/harvest.py`;
- [govinfo.gov](https://www.govinfo.gov): the Cumulative Bulletins (`tools/govinfo_cb.py`) and the annual 26 CFR
  editions (`tools/cfr_bulk.py`);
- the [Federal Register](https://www.federalregister.gov) API for the IRS's correction notices (`tools/fr_corrections.py`);
- the IRS's own repositories at [github.com/IRS-Public](https://github.com/IRS-Public) (`src/irs-public/clone.sh`);
- [ALFRED](https://alfred.stlouisfed.org/) for the C-CPI-U and CPI-U vintages as first published (into `src/alfred/`,
  one CSV per vintage) and the [BLS API](https://www.bls.gov/developers/) for CPI-U and CPI-W.

Each script's docstring names its inputs and outputs; `tools/final_pass.sh` shows the order for the Cumulative Bulletin
checks. The Lean run files are run from `lean-proofs/` after `lake build IrsAudit`:

```sh
lake env lean --run irs-audit/lean/afr/Run.lean > irs-audit/afr/lean_out.tsv
lake env lean --run irs-audit/lean/Audit/IndexRun.lean > irs-audit/indexing/lean_out.tsv
```

The committed run files reproduce the committed outputs byte for byte. The two largest generated files (the Tax Table
check, 2.5 MB, and the EIC Table checks, 1 MB each) are not committed: `tables/gen_lean.py`, `eic_gen.py` and
`eic_gen_2009.py` write them from `tables/*.json`. `lean/` also has its own `lakefile.toml`, which is how the scripts
use it (`cd lean && lake build Audit.Flags2`); the run files without imports also run with plain `lean --run`, as in
`tools/final_pass.sh`.

## Limits

- **The statute is modelled as written.** A departure means the printed figure differs from the words in force; the
  IRS can have a reading that the words allow with strain (A3, A5) or a reason it states elsewhere. Confidence is given
  for each finding.
- **Coverage is of what could be reached.** The IRS's download listings and several index pages refuse scripted
  clients or are barred by robots.txt, so letter rulings, technical advice and Chief Counsel advice were sampled or
  enumerated by name rather than listed; 7,732 scanned letters without a text layer were not read (no OCR); the
  Cumulative Bulletins before 1986 were inventoried only; the second pass stopped at a set time, leaving written
  determinations 1996-2003 unfetched.
- **Prose is not modelled.** Worked examples in publications and regulations, and amounts stated in running text
  outside tables, are checked only where a script extracts them.
- **Not covered yet:** the e-file assurance-testing scenarios beyond their inputs, the XML sources of forms and
  instructions, TIGTA reports, alcohol and tobacco excise rates, news releases, practice units and audit technique
  guides, and the history of the IRM. The MeF schemas and business rules are distributed only to registered software
  developers.

## Files

| Path | Contents |
|---|---|
| [FINDINGS.md](FINDINGS.md) | The 14 verified departures, with document, statute, Lean check, who is affected and confidence |
| [RESULTS.md](RESULTS.md) | Coverage by collection, the checks, the inputs |
| [REJECTED.md](REJECTED.md) | The 29 rejected candidates, and why |
| `lean/` | The Lean checks (library modules `Audit.Formula`, `Audit.CPI`, `Audit.Alfred`, `Audit.Flags2`, `flags.AfrFlags`; the rest are run files). `Audit/Formula.lean` and `Audit/CPI.lean` are copies of [../TaxCode/Indexing/](../TaxCode/Indexing) kept so the folder builds on its own |
| `afr/`, `q6621/`, `indexing/`, `cola/`, `tables/`, `cfr/`, `withholding/`, `public/`, `soi/`, `prior/`, `wd/`, `inventory/`, `irm/`, `src/govinfo/`, `src/fr/` | The scripts for each check, with their extracted figures and results (JSON and TSV) |
| `tools/` | Fetchers and harvest drivers, and `usc_at.sh` |
| `verify/` | Page images and candidate lists used in verifying A8, A9 and A11 |
| [penalties/](penalties/README.md) | Tax Court penalties and additions to tax against the statute |
