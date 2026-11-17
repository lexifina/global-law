# IRS guidance against the statute: coverage and results

Audit of 17 November 2026. Method: harvest the IRS's published material, extract the claims that can be checked,
recompute each from the statute in force for the year (Lean 4, exact natural-number arithmetic; the US Code history in
[lexifina/united-states-law](https://github.com/lexifina/united-states-law)), verify every flag by hand
([FINDINGS.md](FINDINGS.md)), and list what failed verification ([REJECTED.md](REJECTED.md)). Fetching was polite:
sequential or a few requests at a time, a pause between requests, a generic user agent, robots.txt respected; every
request is logged in `cache/_status.tsv`.

## Headline numbers
- **First pass: 437,684 published figures checked** against the statute across 8 of the 12 collections: 416,245 by Lean programs (`lean/`),
  21,439 by exact Python scripts (named in the table); plus 532,531 Code citations checked mechanically.
- **Second pass: about 468,400 further figures checked** in sources the first pass did not reach (Cumulative
  Bulletins 1986-1995, the annual 26 CFR editions, written determinations, IRS software and others; see below).
- **14 verified departures** (FINDINGS.md Part A: A1-A7 from the first pass, A8-A14 from the second), of which 1 is material (A1: the March 2012 section 382
  long-term tax-exempt rate, 3.55% instead of 3.47%, kept for ownership changes on 1-20 March 2012 by the IRS's
  own correction); plus 15 earlier verified departures inside the same collections (Part B).
- **29 candidate flags or classes rejected** after verification (REJECTED.md), 5 of them errors in our own first pass.
- Where the IRS computes by formula, it is almost always right: 247,352 Tax Table entries (30 years), 129,579 EIC
  Table cells (15 years), 22,080 interest factors, 6,038 rate rows, 153 retirement limits, 14,512 actuarial factors and 639 of 657 indexed
  amounts all match the statute. The departures are misprints, carried-over figures and readings.

## Coverage by collection (first pass)

| # | Collection | Found (inventory) | Fetched / held | With checkable claims | Claims checked | Flags | Verified | Out of reach, and why |
|---|---|---|---|---|---|---|---|---|
| 1 | Revenue Rulings (incl. modified/revoked/superseded) | 1,453 in the IRB 1996-2026 (57 modified, 17 revoked, 8 superseded, 11 obsoleted by later items) | 1,453 (582 as PDF text before 2004) | 370 AFR rulings + 125 section 6621 rulings + 30 covered-compensation rulings | 43,404: AFR rows 6,038 compounding, 3,795 multiples, 697 s382, 674 s42, 342 s7520, 26 s642(c)(5); s6621 106 short-term rates, 507 statutory rates, 22,080 interest factors; 7,997 rows of the historical rate tables (each period's rate against the statute, the same period across rulings, and the Rev. Proc. 95-17 factor table cited; Python, `q6621/history_tables.py`); covered compensation: 1,136 year-on-year Table I identities, 17 rulings 2005-2024 (Python, exact; afr/covered_comp.py) | 8 | 5 (A1, A4 x4) | pre-1996 rulings (not on irs.gov; Cumulative Bulletins); 14 AFR months not parsed (gaps in the corpus); 15 pre-2004 s6621 rulings (PDF text); covered-compensation tables checked only year on year (the absolute check needs the Social Security wage-base history; ssa.gov refused the fetcher) |
| 2 | Revenue Procedures | 1,697 in the IRB (352 modified, 227 superseded, 13 revoked, 15 obsoleted) + Rev. Proc. 2013-35 and 2026-35 fetched (missing from the corpus) | 1,699 | 33 annual inflation revenue procedures (tax years 1997-2027) | 657 indexed amounts (incl. 70 AMT amounts 2013-2024) + 21 derived amounts + 587 rate-schedule thresholds cross-checked with Form 1040 instructions | 19 | 19 amounts in 4 findings (A2, A3, A6, A7) | the 1997-2003 procedures are PDF text with interleaved columns (fewer items parsed); items not modelled: EITC parameters (checked through the EIC Table instead), §179, phase-outs before 2018; 2018-2022 rerun from ALFRED vintages |
| 3 | Notices | 2,467 in the IRB (191 modified, 179 obsoleted, 45 superseded) | 2,467 | 20 retirement-plan limit notices (2005-2026); 230 pension segment-rate notices | 621: 153 limits (§§415(b), 415(c), 402(g), 401(a)(17), 416(i), 414(q), 414(v), 408(p)); 315 monthly segment rates = the yield-curve averages, 54 24-month averages (§430(h)(2)(D)), 99 30-year Treasury permissible ranges (`cola/segment_rates.py`) | 0 | 0 (B10 from earlier work) | pre-2005 limits were news releases (not in the IRB) |
| 4 | Announcements | 2,074 in the IRB (373 of them correct errors in earlier items) | 2,074 | printed tables (APA and pre-filing agreement reports, lists) | 200: 148 row totals and 52 cumulative APA counts (all add up); 165 column totals attempted, 56 differences all unreviewed parse artifacts (REJECTED 18); citations (with collections 1-3, REJECTED 17) | 0 | 0 | few amounts set by formula |
| 5 | Private Letter Rulings | irs.gov/pub/irs-wd, numbered by year, week and sequence; 16 sample weeks probed (2000, 2010, 2020, 2025): 494 documents, about 2,600 a year in 2000, 2,100 in 2010, 750 in 2020, 950 in 2025 (all kinds together; third-party count of the whole series: about 42,000) | 494 sampled (`wd/probe.json`, `wd/classified.json`): 199 letter rulings by their text, 156 other or unclassified, 119 scanned images without text | 2 sampled documents state a statutory amount (under §121 and §42(l)(3)), both correct | 2 | 0 | 0 | fact-specific; no full listing (irs.gov/downloads/irs-wd returned 403; the written-determinations search page is disallowed by robots.txt), so no complete harvest |
| 6 | Technical Advice Memoranda | in the same irs-wd series (see 5) | 6 identified in the sample | none | 0 | 0 | 0 | as 5 |
| 7 | Chief Counsel Advice | in the same irs-wd series (see 5) | 14 identified in the sample | none | 0 | 0 | 0 | as 5 |
| 8 | Treasury Regulations (proposed, temporary, final) | 26 CFR in force: 6,235 section files (eCFR, [lexifina/united-states-cfr-law](https://github.com/lexifina/united-states-cfr-law)); IRB: 1,306 Treasury decisions, 1,114 proposed rules | all | actuarial tables in §20.2031-7 and §20.2031-7A; every section (citations) | 14,512 actuarial factors: Table B 3,000, Table J 250, Table K 250 (Lean, `lean/Audit/Actuarial.lean`), Table S examples 12 (2010CM), historical Table S 11,000 (80CNSMT and 90CM, from the life tables printed in the regulation; Python, `cfr/table_s_hist.py`); 111,455 Code citations checked against the current Title 26: 5,264 cite 345 section numbers that no longer exist (67 with a recorded repeal) | 0 | 0 (stale citations listed, not counted, REJECTED 14) | worked examples in prose not modelled; unitrust Tables D and F (§1.664-4) not checked (their formulas are images in the eCFR text); Federal Register preambles not held |
| 9 | Internal Revenue Manual | 1,777 sections listed on the 26 part pages of irs.gov/irm (17 Nov 2026) | 1,777 (all; `irm/txt`) | IRM 20.1.2.3.7.4 minimum-penalty table; IRC citations | 10 penalty amounts (vs Rev. Procs and §6651(j)); 51,833 (1,041 cite 128 section numbers absent from the current Title 26, mostly TEFRA partnership rules kept for pre-2018 years; REJECTED 15) IRC citations | 1 | 1 (A5, a reading) | interest-rate tables are on SERP (internal), not in the public IRM |
| 10 | Publications and forms (all revisions) | irs-pdf / irs-prior listings return 403 (bot protection): no full inventory | 81 PDFs fetched (Form 1040 instructions and Tax Table booklets 1995-2025, revenue-ruling and bulletin PDFs) + 195 IRS files from earlier work | Tax Table, Tax Rate Schedules, EIC Table | 247,352 Tax Table entries (1995-2024), 739 schedule base amounts, 129,579 EIC cells (2009-2010, 2012-2024) | 0 | 0 new (B1-B9, B11 from earlier work) | publications' worked examples and prose amounts not modelled here; the 2011 EIC table not parsed (values split from their rows in both text modes) |
| 11 | Legal memoranda and determinations (FSA, GCM, AOD, determination letters) | not inventoried | 0 | - | 0 | 0 | 0 | the index pages are disallowed by irs.gov robots.txt (`/*/actions-on-decisions`, `/*/chief-counsel-notices`, `/*/written-determinations`) and the download listings return 403 |
| 12 | Historical material (pre-1996 rulings, Cumulative Bulletins, withdrawn guidance) | pre-1996: not held; 1996-2003 bulletins (PDF text in the corpus); superseded actuarial tables in 26 CFR 20.2031-7A | 3,336 pre-2004 IRB items in the corpus (2,522 rulings, procedures, notices and announcements; 814 regulation documents), as PDF text | AFR rulings 1996-2003, Rev. Procs 1996-2003, Tax Tables 1995-2003, Table S 1989-2009 | 2,969 AFR checks + 48 indexed amounts + 74,232 Tax Table entries + 11,000 Table S factors (all counted under 1, 2, 8 and 10 as well) | 0 | 0 | the Cumulative Bulletins before 1996 are not on irs.gov; HathiTrust and Wayback not attempted (bot protection); modified, revoked and superseded items from 1996 on are covered in 1-4 |

## What each check is (Lean files under `lean/`)
- `afr/Run.lean`: every monthly AFR ruling 1996-2026: one rate per row across compounding periods; 110-175% rows
  from the semiannual AFR (§1274(b)(2)(B)); §382(f)(1) highest of three months; §42(b) 70%/30% present value at 72%
  of the average mid/long rate; §7520 120% of the mid-term rate to the nearest 0.2%; §642(c)(5) deemed rate.
- `q6621/Run.lean`: the quarterly section 6621 rulings: daily-compounded short-term rate rounded per §6621(b)(3)
  from the AFR ruling of the month after; the statutory add-ons by period (Pub. L. 105-206 change from 1999); every
  Appendix A interest factor (1+r/365 or 366)^n - 1 to 9 decimals.
- `Audit/IndexRun.lean`: inflation adjustment of each amount from its base year and the statute's rounding rule, CPI-U
  (12 months to August) through 2017, C-CPI-U as first published from 2018 (`Audit/Alfred.lean`, ALFRED vintages of
  28 September; 2027 from 11 months because BLS never published October 2025).
- `Audit/ColaRun.lean`: §415(d) CPI-U third-quarter ratio from the base quarter, increase rounded down, never reduced.
- `Audit/TaxTables.lean`: every Tax Table entry = the tax by that year's rate schedule on the row's midpoint, rounded
  to the dollar; every schedule base amount = the tax at its threshold.
- `Audit/EicTables.lean`: every EIC Table cell = the credit at the band midpoint with the statutory percentages and the
  year's revenue-procedure amounts (the rule proved for 2025 by the earlier work).
- `flags/AfrFlags.lean`: kernel-checked statements for findings A1 and A4.

## Inputs the scripts do not fetch
- ALFRED vintages of C-CPI-U and CPI-U (`src/alfred/`): downloaded separately from
  [ALFRED](https://alfred.stlouisfed.org/) (series SUUR0000SA0 and CPIAUCNS, one file per vintage), because ALFRED did
  not answer the fetcher. The values used are written into `lean/Audit/Alfred.lean`.
- CPI-W from the BLS API v1 (`data/cpiw_*.json`, five requests); CPI-U and earlier C-CPI-U vintages from the BLS API
  (`CPI_DIR`, default `~/docs/data/cpi`).

## Second pass: further sources

The second pass ran its downloads for a fixed period and stopped at a set time; nothing was fetched after it. Not
fetched for that reason: written determinations 1996-2003 and 2004 weeks 44-53; irs-lafa from 2000 to 2020 week 4; the
Wayback CDX inventory beyond page 6 of 65 (CDX answered 503 and was stopped).

- About **468,400 further figures checked** (372,900 Table S factors in the 20 annual 26 CFR editions 1997-2016; 83,997
  factors of the IRS's own 2010CM/2000CM Tables S and B; 6,254 Cumulative Bulletin AFR cells against the IRB editions;
  1,481 AFR checks and 47 s6621 checks on the 1986-1995 Bulletins in Lean; 1,680 Pub 15-T cells; 236 Pub 15 / Notice
  1036 table steps; 697 IRS-Public software constants; 866 statutory amounts and 2,444 post-repeal citations in 25,918
  written determinations and Chief Counsel documents; SOI, Pubs 501/17 and exemption amounts).
- **7 verified departures, A8-A14** ([FINDINGS.md](FINDINGS.md)): two AFR misprints in the 1986 and 1987 Bulletins, a
  stale 2026 constant shown to users by the IRS Tax Withholding Estimator, a wrong married-couple exemption in an SOI
  historical table, and four letter rulings that misstate the Code (repealed sections cited, GST exemption misstated).
  None is material; none was found in any IRS correction (the 178 live forms-and-publications changes, 244 Federal
  Register correction notices).
- **10 more items rejected** (REJECTED.md 20-29).

| # | Collection / source | Exists | Fetched | With text | Checked | Verified findings | Notes |
|---|---|---|---|---|---|---|---|
| 5-7 | Written determinations, irs-wd (PLR, TAM, CCA, FSA) | not known (no index: robots bars the listing pages); enumeration 2421 of 3286 week-schemes: complete for 2005-2026; partial [2004]; not enumerated 1996-2003 (time limit) | 33374 PDFs | 25642 with text, 7732 scanned images (no OCR engine) | 25918 classified; citations to repealed sections: 2444 candidates; amounts: {'GST exemption': 527, 'basic exclusion': 331, 'annual exclusion': 8} | A10, A13, A14 | 1996-2003 and 2004 weeks 44-53 not fetched (time limit); 7,732 scanned letters unchecked (no OCR) |
| 11 | Chief Counsel: irs-ccdm, irs-utl, irs-lafa, irs-aod, lanoa, irs-counsel | by name only (no listing; CDX blocked by 503) | irs-ccdm 145, irs-utl 0, irs-lafa 29, irs-aod 72, lanoa 32, irs-counsel 0 | 276 | kinds and citations with 5-7 (checks.json) | 0 | enumerated by name: ccdm 1998-2026, utl/lanoa am-YYYY-NNN, aod 1995-2026; irs-lafa weekly enumeration done for 1999 weeks 1-32 and 2020 week 5 to 2026 only; 1999 weeks 33-53 and 2000-2020 week 4 not enumerated (time limit); irs-counsel and /pub/foia not reached (no file names without a listing) |
| 12 | Cumulative Bulletins 1919-2008 (GovInfo GOVPUB T22) | 90 distinct packages (cb_packages.tsv: 92 rows, 2 duplicates) | 90 complete | 90 (GovInfo OCR layer; usable, see `src/govinfo/usability.json`) | AFR 99 monthly rulings 1986-1995: conversion and s382 996/6, labelled multiples and s42 478/1 (pass/fail); s6621 19 quarterly rulings 47/0; personal exemption 1990-1996 7/7; citations 1995 only (the Code history starts with the 1994 edition) | A8, A9 | 1919-1983 volumes: inventory only (pre-1986 Codes out of scope); 1985 AFR rulings not parsed (OCR layout) |
| 8 | 26 CFR annual editions 1997-2016 (GovInfo bulk; title 26 absent from the 1996 folder) | 20 | 20 | XML | Table S (80CNSMT, 90CM) in every edition: 372900 factors, 29 off (one precision tie, REJECTED 26) | 0 | other tables (1.72-9, RMD) not parsed |
| 13 | Other IRS material | see notes | prior-year pubs 414 PDFs; actuarial files 48; ATS/e-file 357; SOI 218; changes list 178 items; FR corrections 244 (151 texts); IRS-Public 4 repos | all | actuarial Tables S (2010CM, 2000CM) and B: 83997 factors, 0 off; Pub 15-T 2020-2026: 1680 cells, 0 off; Pub 15 Table 7 1995-2019: 128 row steps, 0 off; IRS-Public constants: TWE 419, EITC Assistant 99, Direct File 175, 4 Direct File scenario tax snapshots; Pubs 501/17 standard deduction charts 86 cells, 0 off; SOI Historical Table 23 150 cells, 6 off (2 = A12; 4 = 2001 bracket cells, footnoted design) | A11, A12 | ATS PDFs carry inputs only (computed lines blank: nothing to recompute); U(1) formula not recovered; irs-sgml not fetched (no names without CDX) |
