# Tax Court penalties and additions to tax, checked against the statute

Every opinion the US Tax Court's own database returns on IRS penalties, read for the figures the IRS determined, with
each figure checked against a Lean model of the penalty provisions as in force for the year, and, where the court has
published it, the decision finally entered. Run on 17 November 2026.

- [RUN2.md](RUN2.md): the full run, every reachable opinion (8,605), with the entered decisions. The main report.
- [RUN1.md](RUN1.md): the first run, a seeded sample of 1,004 docket entries, with the map of what is public about IRS
  sanctions (exemption revocations, practitioner discipline, criminal cases, TIGTA audits) and how reachable it is.

## What was checked

The IRS's determination is printed at the start of most opinions: by tax year, the deficiency and each penalty or
addition to tax. [lean/Penalties.lean](lean/Penalties.lean) writes the rules from the Code's text as in force (US
Code history in [lexifina/united-states-law](https://github.com/lexifina/united-states-law)), money in cents:

- [§6662](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section6662&num=0&edition=prelim)
  accuracy-related penalty, 20% (40% under (h)), with the substantial-understatement test of (d)(1);
- [§6663](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section6663&num=0&edition=prelim)
  fraud penalty, 75%;
- [§6651](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section6651&num=0&edition=prelim)
  additions for late filing and late payment, with the (c)(1) reduction, the (f) fraud rate and the minimum;
- [§6654](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section6654&num=0&edition=prelim)
  (counted, not checked: it needs installment dates and payments) and
  [§6665(b)(1)](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title26-section6665&num=0&edition=prelim)
  (which part of an addition the deficiency procedure reaches).

[lean/Run.lean](lean/Run.lean) labels each year-record: *agrees* (the statutory rate on the whole deficiency),
*consistent* (within the rate), or *FLAG* (above it). Every verified disagreement is restated as a kernel-checked
theorem in [lean/Verified.lean](lean/Verified.lean) (run 1) and [lean/Verified2.lean](lean/Verified2.lean) (run 2).

## Results (run 2)

- **8,605 opinions** (memorandum, summary, division and bench opinions, 1995-2026, plus 13 earlier), all fetched;
  **4,132** have figures Lean can check: **9,344 year-records**.
- **The IRS's rates are right.** In 54.6% of the opinions the penalty is exactly the statutory rate on the deficiency,
  in 35.5% it is within it (a penalty on part of the deficiency), and no year-record shows a wrong rate; the
  §6651(c)(1) reduction is applied where it should be.
- **The flagged tenth is mostly explained.** Of the 410 opinions above the bound, about a fifth are parser errors and
  another fifth have a lawful or already-corrected explanation (40% valuation penalties under a "§6662" label, larger
  underpayments than deficiencies, alternative pleadings); most of the rest are left to a Rule 155 computation.
- **Entered decisions usually cut the penalty.** Of the §6662(a) penalties followed to the entered decision, 348 were
  dropped, 325 reduced and 106 entered unchanged (51 increased, mostly after amended answers).
- **Verified disagreements** (RUN2.md section 4): two courts holding an understatement under $5,000 "substantial"
  (T.C. Summary Opinions 2005-96 and 2006-108); a 30% late-filing addition sustained against a non-filer, where the cap
  is 25% (T.C. Memo. 2006-253); an entered §6662 penalty of 33% of the entered deficiency (docket 2257-13); printed
  figures that no rate fits (T.C. Memo. 1996-260, 2001-6, 2013-282); and a recurring pattern, now visible in entered
  decisions, of late-filing additions charged on tax the taxpayer had already reported on a late return, which
  §6665(b)(1) keeps outside the deficiency procedure (T.C. Memo. 2021-46, 2025-80 and others).

## Reproduce

The scripts fetch the opinions and decisions themselves from the court's public
[DAWSON](https://dawson.ustaxcourt.gov) API (no key), politely: a generic user agent, 4 concurrent requests rising to 8
only after clean minutes, halving and pausing on errors, stopping on a persistent 403, and logging every request in
`cache/_status.tsv`. They need Python 3, `pdftotext` (poppler) and Lean 4 through elan.

```sh
cd lean-proofs/irs-audit && export IRS_AUDIT=$PWD
(cd penalties/lean && lake build)          # builds the classifier the scripts call (lean/.lake/build/bin/run)
python3 penalties/scripts/enum2.py         # every opinion for the 11 keywords, year by year
python3 penalties/scripts/inventory2.py    # docket entries -> opinions (consolidated cases merged)
python3 penalties/scripts/fetch2.py        # the opinion PDFs
python3 penalties/scripts/extract2.py      # text layers
python3 penalties/scripts/parse2.py        # the determination: deficiency and penalties by year
python3 penalties/scripts/check2.py        # Lean labels -> data2/classified.tsv, flags.json
python3 penalties/scripts/buckets2.py      # provisional buckets for the flags
python3 penalties/scripts/decisions2.py    # docket entries and decision documents
python3 penalties/scripts/dec_parse2.py    # final figures through the same classifier
python3 penalties/scripts/stats2.py        # the tables of RUN2.md
```

`view2.py`, `vflag2.py` and `vfinal2.py` print the passages read in hand verification. Run 1 used `fetch.py`,
`parse.py`, `check.py` and `stats.py`; `fad.py` and `opr.py` read the exemption determinations and practitioner
announcements from the IRS material of [../](../README.md). From `lean-proofs/`, `lake build TaxCourtPenalties`
checks the model and the theorems, and `lake env lean --run irs-audit/penalties/lean/Run.lean ROWS.tsv OUT.tsv` runs
the classifier on `irs-audit/penalties/data2/rows.tsv` (it gives `classified.tsv`, in a different row order).

Published data: the parsed records, Lean labels, flags and final figures in `data/` (run 1) and `data2/` (run 2; the
larger files gzipped). Not published: the PDFs and their text, and the practitioners' names in run 1's `opr.json`.

## Limits

- **Keyword universe.** The set is every opinion DAWSON's search returns for 11 penalty keywords; DAWSON holds almost
  nothing before 1995.
- **Parser.** 779 opinions with figures could not be aligned and were left out; on a random sample 98.7% of penalty
  records were right, but errors concentrate in flagged rows, so flagged buckets are verified by sample.
- **Deficiency, not underpayment.** The penalty base is the underpayment; opinions state the deficiency. An excess over
  rate x deficiency is a signal, not proof, until read.
- **Final amounts** are public only for decisions entered with a file (from about 2009-2011); party computations and
  most stipulated decisions are private.
- **Not formalised:** §6751(b) supervisory approval (tagged by phrase only) and §6654.
- **Not used:** CourtListener (needs an account), the Caselaw Access Project's bulk files (barred by robots.txt).
