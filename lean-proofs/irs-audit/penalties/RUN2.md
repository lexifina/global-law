# When the IRS punishes, at full scale: every reachable Tax Court opinion on penalties and additions to tax (run 2)

Run 2 of 17 November 2026. Run 1 ([RUN1.md](RUN1.md)) sampled 1,004 docket entries. This run enumerates and fetches
**every** opinion DAWSON returns for the penalty keywords, re-parses them with a new parser, reruns the Lean classifier
on all of them, and for the first time reads the **entered decisions** to see final amounts. Same standard of proof as
run 1: recompute from the statute in force for the year (`lean/Penalties.lean`, unchanged), then verify by hand before
calling anything a disagreement. A figure the court leaves to a Rule 155 computation is not counted as an IRS error.

## 1. Inventory

### 1.1 How the set was built
- **Source:** the Tax Court's DAWSON public API, no key. `opinion-search` takes `dateRange=customDates` with
  `startDate`/`endDate` as MM/DD/YYYY (ISO dates are silently ignored; an end date in the future returns 400) and
  `opinionTypes` MOP (memorandum), SOP (summary), TCOP (division, "T.C."), OST (bench opinions).
- **Queries:** 11 keywords (`6662`, `6663`, `6651`, `6654`, `6662(h)`, `6651(f)`, `6751(b)`, `"accuracy-related penalty"`,
  `"addition to tax"`, `"additions to tax"`, `"fraud penalty"`) x every year 1980-2026, all four types per query: 517
  queries. The largest single query returned **369** results, so no query came near the 5,000 cap (the splitter by type
  and half-year was ready but never needed). DAWSON's opinions start in 1995 (13 earlier).
- **Union:** 10,621 docket entries -> **8,640 opinions** after merging consolidated dockets (same citation, or same
  type/judge/date/pages/title) -> **8,605** after a second pass on the citation read from the text (35 more consolidated
  duplicates whose titles carry no citation).
- **Fetch:** `scripts/fetch2.py` with the gate in `scripts/dawson.py` (generic UA; 4 concurrent, +2 after 2 clean minutes
  up to 8; halve and pause 60 s if errors exceed 1% in a minute; stop on persistent 403). www.ustaxcourt.gov/robots.txt
  disallows only `/admin/`; the API host has none. Measured 3.0 opinions/s at 4 and 3.8-6.1/s at 8: **7,709 new PDFs in
  21 minutes, 15,418 requests, every one HTTP 200**, plus 931 reused from run 1's cache. The only non-200s of the run:
  7 x 429 on the search endpoint at 4 concurrent (the gate halved to 1; every query succeeded on retry) and, on the
  decision fetch, 403s that are access rules rather than rate limits ("Unauthorized to access private document",
  "Docket entry has been sealed"), recorded as results. Order 2020-26, 2010-19, older; no cut-off was needed.

### 1.2 Coverage

| Stage | Opinions |
|---|---|
| Opinions that exist for the keywords (DAWSON, deduplicated) | **8,605** |
| Fetched | **8,605** (100%; 4 with almost no text layer) |
| With notice-of-deficiency figures in the opinion (parsed + unparsed + penalty named without amount) | 6,040 |
| Parsed into year-records | **4,511** |
| Checked by Lean (at least one in-scope year: §6662, §6663, §6651(a)(1)/(a)(2)/(f)) | **4,132** opinions, **9,344** year-records |

| Type | Opinions (deduplicated) | Fetched | With notice figures | Parsed | Checked by Lean |
|---|---|---|---|---|---|
| MOP | 5783 | 5783 | 4152 | 3127 | 2780 |
| SOP | 1390 | 1390 | 1130 | 936 | 921 |
| TCOP | 549 | 549 | 289 | 185 | 169 |
| OST | 883 | 883 | 469 | 263 | 262 |
| all | 8605 | 8605 | 6040 | 4511 | 4132 |

| Status | Opinions |
|---|---|
| parsed | 4511 |
| no determination passage | 1582 |
| unparsed | 779 |
| penalty amount not stated | 750 |
| no amounts stated in determination | 649 |
| not a deficiency case (CDP, 6015, whistleblower) | 207 |
| no penalty in determination | 127 |
| duplicate (consolidated, same citation) | 35 |

"No determination passage" (1,582) and "no amounts stated" (649) are opinions with nothing to check: collection, §6015,
partnership-level, jurisdiction and fee cases, and modern opinions that say "determined a deficiency ... and a section
6662(a) accuracy-related penalty" without amounts. "Penalty amount not stated" (750) gives the deficiency but not the
penalty. "Unparsed" (779) has figures the parser could not align (left out, not guessed).

Inventory by filing year (MOP / SOP / TCOP / OST):

| Year | Opinions | MOP / SOP / TCOP / OST | Fetched | Parsed | Checked |
|---|---|---|---|---|---|
| 1986 | 1 | 0 / 0 / 1 / 0 | 1 | 0 | 0 |
| 1988 | 1 | 0 / 0 / 1 / 0 | 1 | 1 | 0 |
| 1991 | 2 | 2 / 0 / 0 / 0 | 2 | 0 | 0 |
| 1992 | 2 | 2 / 0 / 0 / 0 | 2 | 1 | 0 |
| 1994 | 3 | 3 / 0 / 0 / 0 | 3 | 1 | 0 |
| 1995 | 119 | 116 / 0 / 3 / 0 | 119 | 88 | 52 |
| 1996 | 392 | 379 / 0 / 13 / 0 | 392 | 278 | 193 |
| 1997 | 399 | 381 / 0 / 18 / 0 | 399 | 286 | 220 |
| 1998 | 313 | 289 / 0 / 24 / 0 | 313 | 230 | 198 |
| 1999 | 274 | 251 / 0 / 23 / 0 | 274 | 205 | 180 |
| 2000 | 256 | 226 / 0 / 30 / 0 | 256 | 170 | 149 |
| 2001 | 282 | 187 / 77 / 18 / 0 | 282 | 204 | 190 |
| 2002 | 285 | 186 / 74 / 25 / 0 | 285 | 202 | 192 |
| 2003 | 273 | 203 / 56 / 14 / 0 | 273 | 168 | 155 |
| 2004 | 233 | 145 / 72 / 16 / 0 | 233 | 140 | 130 |
| 2005 | 265 | 179 / 72 / 14 / 0 | 265 | 146 | 144 |
| 2006 | 266 | 169 / 78 / 19 / 0 | 266 | 125 | 117 |
| 2007 | 330 | 228 / 88 / 14 / 0 | 330 | 122 | 116 |
| 2008 | 342 | 196 / 76 / 15 / 55 | 342 | 115 | 108 |
| 2009 | 351 | 182 / 80 / 18 / 71 | 351 | 127 | 115 |
| 2010 | 366 | 173 / 94 / 24 / 75 | 366 | 168 | 160 |
| 2011 | 363 | 180 / 69 / 28 / 86 | 363 | 159 | 145 |
| 2012 | 414 | 241 / 66 / 25 / 82 | 414 | 190 | 189 |
| 2013 | 374 | 206 / 67 / 18 / 83 | 374 | 182 | 182 |
| 2014 | 328 | 180 / 73 / 24 / 51 | 328 | 172 | 172 |
| 2015 | 278 | 167 / 40 / 13 / 58 | 278 | 130 | 129 |
| 2016 | 291 | 155 / 57 / 23 / 56 | 291 | 151 | 150 |
| 2017 | 301 | 177 / 55 / 26 / 43 | 301 | 148 | 147 |
| 2018 | 261 | 160 / 38 / 16 / 47 | 261 | 132 | 132 |
| 2019 | 185 | 104 / 29 / 15 / 37 | 185 | 86 | 85 |
| 2020 | 169 | 113 / 21 / 12 / 23 | 169 | 62 | 62 |
| 2021 | 167 | 103 / 30 / 10 / 24 | 167 | 73 | 73 |
| 2022 | 147 | 102 / 19 / 6 / 20 | 147 | 54 | 53 |
| 2023 | 177 | 109 / 23 / 14 / 31 | 177 | 50 | 50 |
| 2024 | 143 | 98 / 21 / 8 / 16 | 143 | 54 | 54 |
| 2025 | 139 | 101 / 10 / 14 / 14 | 139 | 49 | 48 |
| 2026 | 113 | 90 / 5 / 7 / 11 | 113 | 42 | 42 |

### 1.3 Parser accuracy (hand-checked)
- **Opinions (notice figures):** seeded random sample of 36 parsed opinions (seed 20261118, `data2/eval_sample_ids.json`),
  each read against its determination passage: 35 unique (one consolidated duplicate, which led to the citation dedupe
  above); **75 penalty year-records, 74 correct (98.7%)**; 34 of 35 opinions entirely correct. The error: T.C. Memo.
  1995-527 took $12,152 of unreported alimony as the deficiency (its $359.20 penalty was right). One opinion missed two
  fiscal-year rows (T.C. Memo. 1997-147, Dura-Craft); one added a spurious record without a penalty.
- **Run 1's 136 unparsed opinions:** 36 now parse, 61 carry no amounts or are not deficiency cases, 36 remain unparsed.
- **Parser errors concentrate in flagged rows** (section 3.1): 11 of the 54 flagged opinions sampled, almost all
  consolidated cases with several petitioners or tables whose text layer reverses the header order.
- **Decision documents:** after fixes prompted by a first sample of 8, a fresh sample of 10 entered decisions: 9 exactly
  right, 1 OCR-damaged amount ("$4 , 245 . 0 0" read as $4; fixed and rerun).

## 2. What changed in the method
- `scripts/enum2.py`, `inventory2.py`, `fetch2.py`, `dawson.py`: enumeration, dedupe and the adaptive fetch above.
- `scripts/extract2.py` and `scripts/parse2.py` (8 processes each): bench-opinion line numbers stripped; length-preserving
  OCR normalisation ("Sec . 666 2", "6651 ( a)(1)", "$ 45,848", "85,95 7"); tables read by **column position** under the
  header labels (blank cells no longer shift values), prose lines excluded from headers, a bare "Penalty" column resolved
  from the determination sentence; a new prose parser for "deficiencies of $A and $B and penalties of $C and $D for 2012
  and 2013, respectively" and "a $X deficiency and a $Y accuracy-related penalty", sentence by sentence for consolidated
  petitioners; page stamps, dates and amended-answer sentences cut; candidate parses ranked (position table >
  respectively-prose > old table > old prose); new statuses for opinions without amounts.
- `scripts/check2.py`: the same Lean classifier (`lean/Run.lean` over `lean/Penalties.lean`) as 8 parallel shards; keys
  normalised (`6663(a)`, `6654(a)`, OCR `6651(aX1)`, the named §6662 grounds (c)/(d)/(e)/(g) at 20%); a bare "§6651(a)"
  stays out of scope, as in run 1.
- `scripts/buckets2.py`: every flagged row put in a provisional bucket before hand verification.
- `scripts/decisions2.py`, `scripts/dec_parse2.py`: docket entries and decision documents; final figures parsed and run
  through the same Lean classifier.
- `lean/Verified2.lean`: one kernel-checked statement per verified item below (`#print axioms`: none).

## 3. Results

### 3.1 Opinion level (4,132 opinions with checkable figures), in run 1's classes

| Class | Opinions | Share | Basis |
|---|---|---|---|
| **IRS figure agrees with Lean**: statutory rate x stated deficiency (20%, 40%, 75%; §6651(a)(1) 25% or 22.5% after (c)(1); §6651(f) 75%) on every checked year | **2,255** | **54.6%** | automatic |
| **Consistent with Lean**: within the rate (penalty on part of the deficiency) | **1,467** | **35.5%** | automatic |
| Excess of at most $5 or 0.5% of the bound (rounding, or a marginally larger underpayment) | 51 | 1.2% | 7 of 7 sampled read correctly, all small (+$3.40, +$4.00, +$22.50 on $6,846 ...) |
| 40% amount under a generic "§6662" label (gross valuation misstatement: lawful) | 13 | 0.3% | 5 of 5 sampled verified (T.C. Memo. 2014-26, 2014-47, 2024-62, 2012-327, 2020-133) |
| §6651(a)(1) above 25% with a late return in the opinion (§6665(b)(1) pattern) | 68 | 1.6% | 9 of 9 read correctly; late-return arithmetic confirmed where read in full; one exception (V2) |
| §6651(a)(1) above 25%, no late return found in the text | 30 | 0.7% | 5 sampled: 2 reduced or conceded by the IRS before decision, 3 left to Rule 155 |
| Other excess, decision under Rule 155 | 57 | 1.4% | 7 sampled: 2 parser errors, 1 alternative pleading, 1 within a 20/40% mix, 3 real excesses left to Rule 155 |
| Other excess, decided otherwise | 47 | 1.1% | 9 sampled: 5 parser errors, 1 conceded, 3 real (one an opinion misprint, resolved by the entered decision) |
| Gross excess (penalty 2x its bound or more) | 143 | 3.5% | 12 sampled: 4 parser errors, 2 explained, 1 §6665(b)(1), 5 inconsistent figures as printed |
| (c)(1) check | 1 | 0.0% | |

Read through their samples, about a fifth of the 410 flagged opinions are parser errors (estimate ~90, concentrated in
the gross-excess and decided-otherwise buckets), another fifth have a lawful or already-corrected explanation, and the
rest are real excesses as printed, most of them left to a Rule 155 computation or carrying the §6665(b)(1) pattern.
Verified excesses that are neither explained, corrected nor left to Rule 155 remain rare: the items in section 4.

### 3.2 Year-record level (Lean labels before hand verification)

| Check | Label | Rows |
|---|---|---|
| 6651a1 | FLAG: 6651(a)(1) exceeds 25% of deficiency | 2 |
| 6651a1 | FLAG: 6651(a)(1) exceeds 25% of deficiency and is not the minimum | 200 |
| 6651a1 | agrees: 22.5% of deficiency (25% less (c)(1) reduction) | 265 |
| 6651a1 | agrees: 25% of deficiency (maximum) | 908 |
| 6651a1 | agrees: §6651(a) minimum | 3 |
| 6651a1 | consistent: within 25% of deficiency | 1407 |
| 6651a2 | FLAG: 6651(a)(2)/(3) exceeds 25% of deficiency | 14 |
| 6651a2 | consistent: within 25% of deficiency | 492 |
| 6651f | FLAG: 6651(f) exceeds 75% of deficiency | 11 |
| 6651f | agrees: 75% of deficiency (maximum) | 106 |
| 6651f | consistent: within 75% of deficiency | 199 |
| 6654 | not checkable: needs installment dates and payments | 1721 |
| acc | FLAG: 6662(a) amount is 40% of deficiency | 27 |
| acc | FLAG: 6662(a) exceeds 20% of deficiency | 222 |
| acc | FLAG: 6662(h) exceeds 40% of deficiency | 4 |
| acc | FLAG: 6663 exceeds 75% of deficiency | 38 |
| acc | FLAG: portions overlap (sum of implied bases exceeds deficiency) | 54 |
| acc | agrees: 20% of deficiency | 4204 |
| acc | agrees: 40% of deficiency | 36 |
| acc | agrees: 75% of deficiency | 502 |
| acc | agrees: mixed rates on disjoint portions summing to the deficiency | 52 |
| acc | consistent: 20% of part of the deficiency | 622 |
| acc | consistent: 40% of part of the deficiency | 9 |
| acc | consistent: 75% of part of the deficiency | 86 |
| acc | consistent: mixed rates on disjoint portions within the deficiency | 28 |
| c1 | CHECK: (a)(1) at 25% alongside (a)(2) - (c)(1) reduction? | 1 |
| other | out of scope: 6651(a) | 534 |
| other | out of scope: 6653 | 37 |
| other | out of scope: 6653(a) | 144 |
| other | out of scope: 6653(a)(1) | 287 |
| other | out of scope: 6653(a)(1)(A) | 109 |
| other | out of scope: 6653(a)(1)(B) | 9 |
| other | out of scope: 6653(a)(1)(a) | 1 |
| other | out of scope: 6653(a)(2) | 14 |
| other | out of scope: 6653(b) | 115 |
| other | out of scope: 6653(b)(1) | 142 |
| other | out of scope: 6653(b)(1)(A) | 64 |
| other | out of scope: 6653(b)(1)(B) | 2 |
| other | out of scope: 6653(b)(2) | 2 |
| other | out of scope: 6655(a) | 5 |
| other | out of scope: 6659 | 112 |
| other | out of scope: 6659(a) | 9 |
| other | out of scope: 6661 | 376 |
| other | out of scope: 6661(a) | 77 |
| other | out of scope: 6662A | 12 |
| other | out of scope: 6673 | 5 |
| other | out of scope: 6673(a) | 3 |
| other | out of scope: 6673(a)(1) | 2 |

No year-record shows the IRS using a wrong *rate*: every exact match is at a statutory percentage, and 126 records at
exactly 22.5% (§6651(c)(1) applied) plus 158 at 25% show the late-filing interaction handled.

### 3.3 Year-level rates

| Year | Checked | Agree (exact rate) | Within the rate | Flagged (any) | Flagged excluding rounding/40% label |
|---|---|---|---|---|---|
| 1995 | 52 | 46.2% | 50.0% | 3.8% | 1.9% |
| 1996 | 193 | 50.8% | 36.3% | 13.0% | 11.4% |
| 1997 | 220 | 47.7% | 40.0% | 12.3% | 10.5% |
| 1998 | 198 | 58.6% | 34.8% | 6.6% | 4.5% |
| 1999 | 180 | 53.9% | 37.2% | 8.9% | 7.8% |
| 2000 | 149 | 59.1% | 34.2% | 6.7% | 6.0% |
| 2001 | 190 | 55.8% | 35.8% | 8.4% | 7.4% |
| 2002 | 192 | 42.2% | 47.4% | 10.4% | 9.4% |
| 2003 | 155 | 49.0% | 41.3% | 9.7% | 8.4% |
| 2004 | 130 | 40.0% | 50.8% | 9.2% | 6.9% |
| 2005 | 144 | 41.0% | 47.9% | 11.1% | 9.7% |
| 2006 | 117 | 53.0% | 41.0% | 6.0% | 6.0% |
| 2007 | 116 | 50.9% | 35.3% | 13.8% | 10.3% |
| 2008 | 108 | 49.1% | 38.0% | 13.0% | 11.1% |
| 2009 | 115 | 51.3% | 33.9% | 14.8% | 11.3% |
| 2010 | 160 | 60.6% | 30.6% | 8.8% | 8.8% |
| 2011 | 145 | 64.8% | 25.5% | 9.7% | 6.2% |
| 2012 | 189 | 56.6% | 35.4% | 7.9% | 6.9% |
| 2013 | 182 | 61.5% | 25.8% | 12.6% | 10.4% |
| 2014 | 172 | 57.6% | 32.0% | 10.5% | 7.0% |
| 2015 | 129 | 66.7% | 23.3% | 10.1% | 7.8% |
| 2016 | 150 | 63.3% | 29.3% | 7.3% | 7.3% |
| 2017 | 147 | 56.5% | 34.7% | 8.8% | 8.8% |
| 2018 | 132 | 63.6% | 28.8% | 7.6% | 6.8% |
| 2019 | 85 | 56.5% | 32.9% | 10.6% | 10.6% |
| 2020 | 62 | 58.1% | 35.5% | 6.5% | 3.2% |
| 2021 | 73 | 57.5% | 27.4% | 15.1% | 12.3% |
| 2022 | 53 | 56.6% | 32.1% | 11.3% | 7.5% |
| 2023 | 50 | 64.0% | 24.0% | 12.0% | 10.0% |
| 2024 | 54 | 51.9% | 38.9% | 9.3% | 7.4% |
| 2025 | 48 | 47.9% | 39.6% | 12.5% | 12.5% |
| 2026 | 42 | 57.1% | 28.6% | 14.3% | 14.3% |

By decade:

| Decade | Checked | Agree | Within | Flagged |
|---|---|---|---|---|
| 1990s | 843 | 52.2% | 38.0% | 9.8% |
| 2000s | 1416 | 49.1% | 40.8% | 10.1% |
| 2010s | 1491 | 60.7% | 29.9% | 9.4% |
| 2020s | 382 | 56.3% | 32.2% | 11.5% |

Agreement rises from about half in 1995-2009 to about 60% from 2010, mostly because later notices put the penalty on the
whole deficiency more often (the "within the rate" share falls from ~40% to ~30%). The flagged share is flat at 7-12% a
year before removing parser errors; no year stands out.

### 3.4 Substantial understatement (§6662(d)(1)(A))
All 61 opinions that use "substantial understatement" and have a §6662 year with a deficiency of $5,000 or less were read.
Most describe the rule, state the IRS's contention, concern another (larger) year, or hold conditionally ("insofar as the
Rule 155 computations show a substantial understatement"), and those apply the test correctly. Two new court
misstatements (V1, V8), besides run 1's Ni (115 T.C. No. 37). For larger deficiencies the 10% limb still cannot be
checked: the tax required to be shown is rarely stated.

### 3.5 §6665(b)(1): late-filing additions computed on tax already reported on a late return
A §6651(a)(1) addition above 25% of the deficiency needs a base larger than the deficiency, which for a late filer is tax
shown on the late return and not paid. §6665(b)(1) brings an addition into the deficiency procedure only "to that portion
of such addition which is attributable to a deficiency". At notice level: 68 opinions with a late return in the text plus
part of the 30 without (89 + 42 rows). New in this run: **the pattern survives into entered decisions.** 39 §6651(a)(1)
rows in public decision documents exceed 25% of the entered deficiency (decision-parser errors among them); verified in
the documents: T.C. Memo. 2021-46, T.C. Memo. 2025-80, docket 1024-08S (V7). The same holds for §6651(a)(2) (T.C. Memo.
2015-101). A question of scope (what a notice and a Tax Court decision may carry), not arithmetic. Confidence: high on
the arithmetic, medium on the legal characterisation.

### 3.6 §6751(b) (written supervisory approval; tagged, not formalised)

| Filed | Opinions | Mention 6751(b) | IRS met (phrase) | IRS failed (phrase) | Both phrases |
|---|---|---|---|---|---|
| 1995-2006 | 3357 | 0 | 0 | 0 | 0 |
| 2007-2016 | 3437 | 7 | 2 | 1 | 3 |
| 2017-2020 | 916 | 300 | 143 | 6 | 37 |
| 2021-2026 | 886 | 372 | 217 | 19 | 43 |

Mentions follow *Chai* (2d Cir. 2017) and *Graev* (2017): almost none before 2017, then about a third of opinions. The
phrase tags are coarse: of 6 sampled "IRS failed" tags, 3 are real (T.C. Memo. 2021-41, penalties conceded "because the
IRS did not secure timely supervisory approval"; T.C. Memo. 2021-11, stipulated; T.C. Memo. 2025-83, held) and 3 are
taxpayer arguments the court rejected (T.C. Memo. 2017-100, 2013-291, 2020-77). So about a dozen opinions in the set hold
or record a §6751(b) failure; TIGTA's 2026 report (13 of 829 docketed easement cases) remains the better measure.

Court outcome on the accuracy-related penalty, opinions with a stated §6662 amount (coarse phrase match):

| Outcome | Opinions |
|---|---|
| no holding phrase | 1562 |
| sustained in whole or part | 1004 |
| mixed | 274 |
| not sustained / conceded | 185 |

### 3.7 Final amounts: the entered decisions
Targets: every parsed opinion decided under Rule 155 and every flagged opinion, **2,561 dockets**. The public docket list
(`public-api/cases/<docket>/docket-entries`) works for all of them.

| Docket outcome | Opinions |
|---|---|
| decision document fetched | 1217 |
| decision entered, no file attached (paper era) | 1183 |
| decision private (stipulated / computation) | 90 |
| final figures parsed | 942 |
| no decision entry on the docket | 71 |
| targets | 2561 |

| Notice vs entered decision | Year-penalties |
|---|---|
| 6651(a)(1): increased | 42 |
| 6651(a)(1): not stated in decision | 79 |
| 6651(a)(1): reduced | 161 |
| 6651(a)(1): same as notice | 71 |
| 6651(a)(1): zero | 42 |
| 6651(a)(2): increased | 14 |
| 6651(a)(2): not stated in decision | 52 |
| 6651(a)(2): reduced | 30 |
| 6651(a)(2): same as notice | 22 |
| 6651(a)(2): zero | 14 |
| 6662(a): increased | 51 |
| 6662(a): not stated in decision | 360 |
| 6662(a): reduced | 325 |
| 6662(a): same as notice | 106 |
| 6662(a): zero | 348 |
| 6662(h): not stated in decision | 7 |
| 6662(h): reduced | 2 |
| 6662(h): zero | 9 |
| 6663: increased | 4 |
| 6663: not stated in decision | 35 |
| 6663: reduced | 40 |
| 6663: same as notice | 18 |
| 6663: zero | 17 |

| Lean label on the entered figures | Rows |
|---|---|
| agrees: 20% of deficiency | 247 |
| consistent: within 25% of deficiency | 213 |
| not checkable: needs installment dates and payments | 100 |
| agrees: 25% of deficiency (maximum) | 73 |
| consistent: 20% of part of the deficiency | 70 |
| out of scope: 6651(a) | 51 |
| agrees: 22.5% of deficiency (25% less (c)(1) reduction) | 42 |
| consistent: within 75% of deficiency | 42 |
| agrees: 75% of deficiency | 35 |
| FLAG: 6651(a)(1) exceeds 25% of deficiency and is not the minimum | 25 |
| FLAG: 6662(a) exceeds 20% of deficiency | 22 |
| FLAG: 6651(f) exceeds 75% of deficiency | 11 |
| consistent: 75% of part of the deficiency | 5 |
| out of scope: 6653(b)(1)(B) | 4 |
| out of scope: 6653(a) | 4 |
| out of scope: 6659 | 4 |
| FLAG: 6651(a)(2)/(3) exceeds 25% of deficiency | 4 |
| out of scope: 6653(a)(1) | 3 |
| out of scope: 6653 | 3 |
| FLAG: 6662(a) amount is 40% of deficiency | 3 |
| out of scope: 6653(a)(1)(A) | 2 |
| out of scope: 6653(a)(1)(B) | 2 |
| out of scope: 6653(a)(2) | 2 |
| out of scope: 6653(b)(1)(A) | 2 |
| out of scope: 6673(a)(1) | 2 |
| agrees: mixed rates on disjoint portions summing to the deficiency | 2 |
| CHECK: 6654 on a non-filer whose deficiency is under the (e)(1) threshold | 2 |
| FLAG: 6663 exceeds 75% of deficiency | 2 |
| agrees: §6651(a) minimum | 2 |
| out of scope: 6653(a)(25) | 1 |
| out of scope: 6661 | 1 |
| out of scope: 6653(b) | 1 |
| out of scope: 6653(b)(1)(JB) | 1 |
| out of scope: 6659(a) | 1 |
| out of scope: 6673 | 1 |
| consistent: mixed rates on disjoint portions within the deficiency | 1 |
| FLAG: 6662(h) exceeds 40% of deficiency | 1 |
| agrees: 75% of deficiency (maximum) | 1 |
| CHECK: (a)(1) at 25% alongside (a)(2) - (c)(1) reduction? | 1 |

- **Court-entered decisions are public when a file is attached:** 1,052 `DEC` (Decision Entered) and 176 `OAD` (Order and
  Decision) downloaded, plus a few `ODS`, `ODD`, `SDEC`, `ORAP`, `ODJ`.
- **Paper-era entries have no file:** 1,145 `DEC`, 477 `ACED`, 66 `OAD` and others show `isFileAttached: false`
  (decisions before roughly 2009-2011). This covers run 1's Watts, Cordes, Norton, Mansour, Chamberlin, Summary Opinion
  2003-131 and T.C. Memo. 2001-164, 2001-295, 2002-124, 2005-68, 2000-208, and V2 and V4 below.
- **Party papers are private:** Computations for Entry of Decision (`COED`, 534), agreed computations (`ACED`, 445) and
  most stipulated decisions (`SDEC`, 100) answer 403 "Unauthorized to access private document"; 3 are sealed.
- **Notice vs entered §6662(a) penalty** (same year): zero in 348 year-penalties, reduced in 325, unchanged in 106,
  increased in 51 (increases follow amended answers, and include some decision-parser errors). Many notice-level
  excesses never reach a decision.
- **Run 1's open items, where a decision is public:** T.C. Memo. 2011-9 (run 1's D7): the entered decision gives the 2004
  §6651(f) addition as **$71,949.00**, 72.5% of $99,240, not the opinion's "$371,949.00"; the opinion's table carries a
  stray leading digit (the decision's own table shows the same artefact in its §6651(a) column). T.C. Memo. 2013-133:
  entered §6663 penalties exactly 75% (2002: $324,238.50 on $432,318), so the notice-level excess was cured. T.C. Memo.
  2014-126: entered 2010 deficiency $5,438 and penalty $1,096.60, still **$9.00 above 20%**. T.C. Memo. 2025-8: no §6662
  penalty entered. T.C. Memo. 2022-94: stipulated decision private.
- **New items resolved by the decision:** T.C. Memo. 2018-79 printed "2014 20,305 5,261.00"; the entered decision says
  deficiency **$26,305**, penalty $5,261.00, exactly 20%: a misprint in the opinion. T.C. Memo. 2021-129 ($1,422 penalty
  on a $4,413 deficiency in the notice): entered deficiency $2,734, addition $254, **no penalty**. T.C. Memo. 2015-18
  (fraud penalties $47,217.75 and $65,187.75 entered on deficiencies of $2,732 and $2,941): explained in the opinion, the
  taxpayer's return "continued to falsely claim that Federal income tax of $60,225 was withheld", and overstated
  withholding credits enter the underpayment but not the deficiency (Treas. Reg. §1.6664-2(c)(1)). T.C. Memo. 2016-20
  (entered §6662 amounts of $221,930 and $203,155 on $245,760 and $122,353): the deficiencies "were based on reduced
  underpayment amounts" under a closing agreement's "rough justice adjustments".

## 4. Verified disagreements (each read in the opinion or decision; statute as in force for the year)

**V1. T.C. Summary Opinion 2005-96 (Couvillion, S.T.J.), docket 779-04; decision for respondent.** 2001: deficiency
$4,318, §6662 penalty $863 (20%). The court: "petitioners had an understatement of tax in the amount of $4,318. The amount
of tax required to be shown on the 2001 return was $6,932; thus, the amount of the understatement exceeds 10 percent of
the tax required to be shown on the return. Therefore, there was a substantial understatement of tax under section
6662(d)(1)." Footnote 9: "Because it is clear that there was a substantial understatement of tax on the 2001 return, it
is not necessary for the Court to determine whether petitioners were negligent". §6662(d)(1)(A) requires more than "the
greater of" 10% or $5,000, and $4,318 is not (`so2005_96`). Unlike Ni (run 1), the penalty rests on this ground alone. A
court error, not an IRS one (the IRS's 20% is right). Confidence high.

**V2. T.C. Memo. 2006-253 (Wherry, J.), docket 24854-04; "An appropriate decision will be entered".** 2002, no return
("petitioner admitted he never filed a Federal income tax return for 2002"): deficiency $8,716, §6651(a)(1) addition
$2,614.80. "Therefore, the Court sustains respondent's determination of the addition to tax pursuant to section
6651(a)(1)." $2,614.80 is exactly **30%** of $8,716; the maximum is 25%, $2,179 (`tcm2006_253`). With no return there is
no reported tax to explain a larger base. The decision has no attached file (paper era). Confidence: high that the
sustained figure exceeds the statute as printed.

**V3. Bench opinion, docket 2257-13 (Halpern, J.); entered decision of 25 March 2014.** "there is a deficiency in income
tax due from petitioner for the taxable year 2010, in the amount of $6,513.00; That there is an accuracy-related penalty
under I.R.C. section 6662(a) due from petitioner for the taxable year 2010, in the amount of $2,170.00". $2,170 is 33.3%
of $6,513 (20% = $1,302.60), the notice's own figure ("an accuracy-related penalty of $2,170"). Lawful only if the
underpayment exceeded the deficiency by $4,337, which neither document mentions. Confidence: high that the entered
penalty exceeds 20% of the entered deficiency; medium on error versus an unstated larger base.

**V4. T.C. Memo. 1996-260 (Colvin, J.), docket 222-94; decisions for respondent.** The table: "1990 $1,181.38
[deficiency] $6,503.94 [§6651(a)(1)] $6,607.52 [§6662(a),(c)]; 1991 -- 3,375.00 --; 1992 -- 2,404.00 --". "We conclude
that petitioners are liable for the accuracy-related penalty for 1990 under section 6662(a)." The penalty is 5.6 times the
deficiency (20% = $236.28) and the (a)(1) additions run on years with no deficiency (the §6665(b)(1) shape, as in run 1's
Chamberlin) (`tcm1996_260`). The same judge's Watts (T.C. Memo. 1999-416, run 1 D3) has the same shape: late returns,
invalid extensions, a §6662 penalty far above 20% of the deficiency, sustained without reconciliation. No decision file.
Confidence: high that the printed figures exceed the statute; low on whether the notice or the table is wrong.

**V5. T.C. Memo. 2001-6 (Gerber, J., adopting the S.T.J.), docket 12390-96.** "Accuracy-related Penalty I.R.C. Year
Deficiency Sec. 6662: 1990 $66,194 $53,620; 1992 129,526 25,905; 1993 96,884 22,048". 1992 is exactly 20%; 1990 is 81%
and 1993 22.8% (`tcm2001_6`). The opinion decides whether the petition was validly signed, so the figures are never
reconciled. Confidence: high that the printed figures are inconsistent.

**V6. T.C. Memo. 2013-282 (Gerber, J.), docket 14733-12.** "Penalties Year Deficiency Sec. 6662(a) Sec. 6663: 2007
$133,527 $784.00 $1,315.40; 2008 118,156 97,205.25 83,684.25". No rate fits 2008 (the §6662 amount alone is 82% of the
deficiency, `tcm2013_282`) and 2007's amounts are under 1%. Summary judgment; "An appropriate order will be issued".
Probably a garbled table. Confidence: high that the printed table is inconsistent.

**V7 (pattern, now in entered decisions). §6651(a)(1) additions above 25% of the entered deficiency.**
- T.C. Memo. 2021-46, docket 19567-19 (decision 30 Aug 2021): "deficiencies ... 2015 and 2016 in the amounts of
  $105,095.00 and $14,402.00 ... additions to tax ... under ... § 6651(a)(1), in the amounts of $27,593.25 and $9,850.50"
  (26.3% and **68.4%**).
- T.C. Memo. 2025-80, docket 10128-23 (order and decision 28 Oct 2025): deficiency $267,887.00, "addition to tax ...
  § 6651 (a)(1), in the amount of $84,134.25" (31.4%; 25% = $66,971.75).
- Docket 1024-08S (decision 6 Feb 2009): deficiency $10,507.00, §6651(a)(1) $2,675.00 (25.5%).
- Notice level, read in full: T.C. Memo. 1997-64, docket 10433-95 (the 1987 return was "filed on March 4, 1992" and
  "showed a tax of $4,379"; deficiency $7,954, addition $2,815, above 25% of the deficiency but under 25% of deficiency
  plus reported tax, `tcm1997_64`); T.C. Summary Opinion 2012-104, docket 30651-08 (2004 return "filed on August 14,
  2006"; $1,344 on $4,820, `so2012_104`); T.C. Memo. 2015-101, docket 12544-13 (§6651(a)(2) $54,874 on $218,403).
Consistent with run 1's D4 (Brown, T.C. Memo. 2018-91, where the court itself describes additions "computed on the basis
of the net amounts due"). Confidence: high on the arithmetic; medium that every instance is reported tax.

**V8. T.C. Summary Opinion 2006-108 (Powell, S.T.J.), docket 12423-04.** 2002: deficiency $1,296, penalty $259.20. After
quoting the $5,000 test: "Respondent has met his burden of production with respect to petitioners' substantial
understatement of income for the year at issue." $1,296 cannot exceed $5,000 (`so2006_108`). Harmless: decision for
petitioner on the penalty. Confidence high.

**V9. T.C. Memo. 2026-53 (Weiler, J.), docket 24068-22; decision under Rule 155, not yet entered.** Waimana Enterprises:
"2003 $20,746 $68,360 [§6663] $941 [§6651(a)(1)] ... 2008 2,062 2,706". The fraud penalty is 330% and 131% of the
deficiency (`tcm2026_53`). Left to Rule 155; possibly a larger underpayment (false credits, as in T.C. Memo. 2015-18),
not stated. Not counted as an IRS error.

**Smaller or unreconciled excesses (not counted as IRS errors):** T.C. Memo. 2014-126 (+$9 still in the entered
decision); T.C. Memo. 2022-37 (2013: $184,676 on $923,280, +$20); T.C. Summary Opinion 2014-28 ($1,401 on $5,618); bench
opinion 8946-12 ($6,667 on $28,330, conceded); T.C. Memo. 2009-185, 2005-184, 1998-105, 1996-216 (Rule 155).
`unreconciled_20` in `Verified2.lean` records four of them.

**Corrected before decision:** bench opinion 11519-05 ("an addition to tax ... in the amount of $139.80. Respondent
concedes that the negligence penalty should be reduced to $127"; 25% = $129.50, `bench_11519_05`); T.C. Memo. 1997-231
(§6651(a)(1) conceded); T.C. Memo. 2021-129 (penalty dropped in the entered decision).

**Explained, not errors:** 40% gross-valuation penalties under a "§6662" label (13 opinions, e.g. T.C. Memo. 2014-47,
$10,247,155 on $25,617,887; 131 T.C. No. 2; T.C. Memo. 2003-10); §6663 and §6662 pleaded in the alternative (T.C. Memo.
2000-336, 2000-93); non-qualified amended return (T.C. Memo. 2009-289); false withholding credits (T.C. Memo. 2015-18);
closing-agreement "rough justice" (T.C. Memo. 2016-20); opinion misprints corrected by the entered decision (T.C. Memo.
2018-79, 2011-9).

## 5. In short
We read every Tax Court opinion the court's own database returns on IRS penalties: 8,605 opinions from 1995 to 2026, all
fetched, 4,132 with figures a computer can check against a Lean model of the Code. In 90% of them the IRS's penalty is
exactly the statutory rate on the deficiency (55%) or within it (35%), and not one shows the IRS using a wrong rate. The
court's final decisions, public since about 2010, usually cut or drop the penalty: of the §6662 penalties we could
follow to the end, 348 were dropped and 325 reduced, against 106 entered unchanged. The errors we could prove are few and
specific: a court sustaining a "substantial understatement" penalty on a $4,318 understatement, below the statute's
$5,000 floor; a 30% late-filing addition sustained against a non-filer when the cap is 25%; and a recurring habit, now
visible in entered decisions, of charging late-filing additions on tax the taxpayer had already reported, which the Code
keeps outside the deficiency procedure.

## 6. Limits
- **Keyword universe.** "Every reachable opinion" means every opinion DAWSON's search returns for the 11 keywords. An
  opinion that discusses a penalty only in words the search does not index, or one DAWSON does not hold (pre-1995 almost
  entirely), is outside. Bench opinions are transcripts; DAWSON holds those served through it.
- **Parser.** 779 opinions with figures were not aligned (left out, not guessed). Accuracy on a random sample is 98.7% of
  penalty records, but parser errors concentrate in flagged rows (about a fifth of flagged opinions), so flagged buckets
  are reported with sample verification, not as counts of IRS errors.
- **Hand verification is by sample** for the large flag buckets (54 flagged opinions read), plus all 61
  substantial-understatement candidates, 18 entered decisions and 6 §6751(b) tags. Bucket shares are estimates.
- **Underpayment vs deficiency.** The penalty base is the underpayment; opinions and decisions state the deficiency.
  Carrybacks, non-qualified amended returns, overstated withholding credits and closing agreements make the underpayment
  larger, so an excess over rate x deficiency is an upper-bound signal, not proof.
- **Final amounts.** Decision documents are public only when entered through DAWSON with a file (from roughly 2009-2011);
  paper-era decisions have no file, and party computations and most stipulated decisions are private. 1,079 of 2,561
  targeted dockets yielded parsed final figures; the decision parser was checked on 8 + 10 documents.
- **§6654** (needs installment dates and payments) is counted, not checked; **§6651(a)(2)/(a)(3)** usually appear as "to
  be computed"; a bare "§6651(a)" label stays out of scope (107 rows), as in run 1.
- **§6751(b)** is tagged by phrase (precision about one half on a sample of 6), not formalised.
- CourtListener (token), Caselaw Access Project (robots.txt) and Pile of Law (wrong collection) remain out, as in run 1.

## Files
`scripts/` (enum2, inventory2, dawson, fetch2, extract2, parse2, check2, buckets2, decisions2, dec_parse2, stats2, view2,
vflag2, vfinal2), `lean/Verified2.lean`, `data2/` (rows.tsv, flags.json, su_candidates.json, eval_sample_ids.json,
final.json, rows_final.tsv, classified_final.tsv, stats2.md, stats2.json; gzipped: inventory.json, parsed.json,
classified.tsv, rowmeta.json, tags.json, decisions_index.json). Not published, rebuilt by the scripts: `cache/search2/`
(517 queries), `cache/pdf/` (8,640 opinions), `cache/docket/` and `cache/dec/` (docket lists and decision documents),
`cache/_status.tsv` (every request), and the text extracted from the opinions and decisions (`data2/txt/`,
`data2/lay/`, `data2/dec/`) with the 8 shard files of rows and labels.
