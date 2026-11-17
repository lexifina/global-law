# IRS material that departs from the statute: verified findings

Audit of 17 November 2026. Every finding below passed the same bar: recomputed from the statute
text in force for the year (US Code history, `tools/usc_at.sh`), the published figure read from the IRS's own
document, guidance that could change the result searched for in the IRB corpus (`src/irs-guidance`, a clone of
[lexifina/united-states-irs-guidance-law](https://github.com/lexifina/united-states-irs-guidance-law): 10,111 items
1996-2026, with their "effects" trailers), and effective dates checked. Lean files are in `lean/`; the recomputations
run with `lean --run` / `lake env lean --run`; the statements in `lean/flags/AfrFlags.lean` are kernel-checked
(`#print axioms`: none). Confidence: high = arithmetic against unambiguous words; medium = the words admit the IRS's
reading only with strain; low = a reading question.

Ranked by impact (dollars per affected taxpayer, and how many are affected). Part A is new in this audit; Part B lists
the earlier verified findings that fall inside the 12 collections.

## Ranking of Part A by impact
1. A1 - March 2012 s382 long-term tax-exempt rate 3.55% for 3.47% (material; kept for 1-20 March 2012 ownership changes).
2. A2 - 2026 head-of-household standard deduction $24,150 for $24,175 (every HoH filer, $25 of deduction).
3. A3 - estates and trusts first bracket 2026/2027 $3,300/$3,400 for $3,250/$3,350.
4. A6 - wage-levy exemption and disability-trust exemption 2019-2026 rounded the wrong way.
5. A5 - penalty minimums carrying the previous year's adjustment, repeated in the IRM.
6. A7 - Rev. Proc. 2009-21 (Bulletin edition) joint no-child EIC threshold $21,420 for $12,470 (up to $457).
7. A11 - Tax Withholding Estimator 2026: qualifying-relative income limit $5,200 for $5,300, shown to users.
8. A9 - Rev. Rul. 87-68 (C.B. 1987-2): long-term 120% AFR monthly 9.97% for 9.87%.
9. A4 - monthly federal rates misprinted in the official IRB (2014, 2018).
10. A8 - Rev. Rul. 86-94 (C.B. 1986-2): long-term 110% AFR monthly 7.96% for 7.98%.
11. A12 - SOI Historical Table 23: married couple's exemptions 2016-2017 $8,010 for $8,100 (statistics).
12. A13 - PLRs 201602001 and 201432008 misstate the s2631(a) GST exemption ($5,012,000; $1,000,0000).
13. A14 - PLR 202116006 cites s2057(b)(7) for s2056(b)(7) and s2011(a) for s2611(a).
14. A10 - PLRs 202219006-008 cite repealed s30(d)(1)(A) for s30D(d)(1)(A).
New or corrected: A8-A14 appear in no IRS correction found (forms-and-publications changes list, 178 live items;
Federal Register IRS corrections, 244; later Bulletins 1986-2008 searched for A8/A9). All are new.

## Part A: found in this audit

### A1. March 2012 long-term tax-exempt rate for section 382: 3.55% where the statute gives 3.47%
- **Document**: Rev. Rul. 2012-9, 2012-11 I.R.B. 475 (https://www.irs.gov/irb/2012-11_IRB; `src/irs-guidance/rev-rul/2012/2012-009.md`).
  Table 3: "Long-term tax-exempt rate for ownership changes during the current month (the highest of the adjusted
  federal long-term rates for the current month and the prior two months.) | 3.55%". Table 2: "Long-term adjusted AFR
  | | 3.47% | | 2.95% | | 2.94% | | 2.93%".
- **Statute**: 26 U.S.C. §382(f)(1): "The long-term tax-exempt rate shall be the highest of the adjusted Federal
  long-term rates in effect for any month in the 3-calendar-month period ending with the calendar month in which the
  change date occurs." The IRS's own adjusted federal long-term rates: January 2012 3.47% (Rev. Rul. 2012-2),
  February 3.26% (Rev. Rul. 2012-7), March 2.97% (Rev. Rul. 2012-9, Table 3).
- **Lean**: `lean/afr/Run.lean`, check `s382_max3`: fails here and nowhere else in 350 months 1996-2026.
  `AfrFlags.rr2012_9_s382`: max(2.97, 3.26, 3.47) = 3.47, not 3.55. `rr2012_9_table2`: no single rate gives the
  printed Table 2 row; `rr2012_12_table2`: the corrected 2.97% is consistent. 3.55% is December 2011's rate, outside
  the three-month window.
- **IRS response**: Rev. Rul. 2012-12, 2012-15 I.R.B. (https://www.irs.gov/irb/2012-15_IRB) corrects both rates, then:
  "Under the authority of section 7805(b), the corrected rates will not be applied adversely with respect to debt
  instruments issued on or before March 20, 2012, or to ownership changes that occurred on or before March 20, 2012."
  So for ownership changes on 1-20 March 2012 the non-statutory 3.55% still governs.
- **Who and how much**: loss corporations with an ownership change on 1-20 March 2012. The annual section 382
  limitation (value of the old loss corporation x the rate) is 2.3% higher: $800,000 more loss usable each year per
  $1 billion of value, for the life of the carryforwards. Also section 1288 tax-exempt OID for obligations issued on
  1-20 March 2012 (Table 2 rate 3.47% instead of 2.97%).
- **Verification**: re-read from the bulletin text and the IRS's correction; §382(f)(1) unchanged throughout. The
  check found this error without being told of it; it is the only §382 departure in 30 years. Confidence high.

### A2. 2026 head-of-household standard deduction: $24,150; the statute gives $24,175 (re-derived)
- **Document**: Rev. Proc. 2025-32 §4 (`src/irs-guidance/rev-proc/2025/2025-032.md`): "Heads of Households (§ 1(j)(2)(B))
  | $24,150".
- **Statute**: §63(c)(7)(A)(i) (Pub. L. 119-21) substitutes "$23,625" for "$4,400"; §63(c)(7)(B)(ii): the $23,625
  amount "shall ... be increased by" the cost-of-living adjustment from 2024, and "If any increase under this clause
  is not a multiple of $50, such increase shall be rounded to the next lowest multiple of $50." $23,625 plus a multiple
  of $50 ends in 25 or 75, so $24,150 cannot come out; the August 2025 C-CPI-U gives $24,175.
- **Lean**: `lean/Audit/IndexRun.lean`: `std_hoh 2026 FAIL statute 24175 published 24150`. The IRS figure is 150% of
  the single amount ($16,100). Kernel-checked: `lean/Audit/Flags2.lean` `hoh2026_impossible` (23,625 + 50k is never
  24,150) and `hoh2026_statute` (= 24,175). For 2027 (Rev. Proc. 2026-35) the IRS's $24,925 matches the statute.
- **Who and how much**: every head-of-household filer taking the standard deduction in 2026: $25 less deduction, at
  most $9.25 of tax. Confidence high. First found by the indexing work in [TaxCode/Indexing](../TaxCode/Indexing/FINDINGS.md) (F1); re-derived here
  independently.

### A3. Estates and trusts, first rate-table threshold, 2026 and 2027: $3,300 and $3,400; the words give $3,250 and $3,350
- **Documents**: Rev. Proc. 2025-32 §4.01 Table 5 ($3,300); Rev. Proc. 2026-35 §3.01 Table 5 ($3,400;
  https://www.irs.gov/pub/irs-drop/rp-26-35.pdf).
- **Statute**: §1(j)(3)(B)(i) (as amended by Pub. L. 119-21): "solely for purposes of determining the dollar amounts at
  which any rate bracket higher than 12 percent ends and at which any rate bracket higher than 22 percent begins,
  subsection (f)(3) shall be applied by substituting 'calendar year 2017' for 'calendar year 2016'". The estate
  table's $2,550 is where the 24% bracket begins, so the 2017 base applies: $3,250 (2026), $3,350 (2027). The IRS used
  2016. For 2019-2025 (all amounts on the 2017 base under the earlier text) every threshold matches.
- **Lean**: `IndexRun.lean`, `br_est_1` 2026 and 2027 FAIL; the other 238 thresholds 2019-2027 pass. Kernel-checked:
  `Flags2.est2026` (2017 base: $3,250; 2016 base: $3,300).
- **Size**: at most $50 x (24% - 10%) = $7 per estate or trust. Confidence medium: the clause reads as written for the
  individual tables, where the end of the 12% bracket is also the start of the 22% one. 2026 was first found by
  the indexing work (F3); 2027 is new.

### A4. Misprinted monthly federal rates in the official Internal Revenue Bulletin
Each printed row must be one rate stated for four compounding periods; `conv` fails for 4 of 6,038 rows, and in each
case the IRS's own advance release of the ruling has the consistent figure.

| Ruling (bulletin) | Row | Bulletin prints | Advance release | Lean (kernel-checked) |
|---|---|---|---|---|
| Rev. Rul. 2014-22, Sept. 2014 (I.R.B. 2014-37, irb14-37.pdf) | long-term adjusted AFR, annual | 2.49% | 2.94% (rr-14-22.pdf) | `rr2014_22_table2` |
| Rev. Rul. 2014-26, Oct. 2014 (I.R.B. 2014-41, irb14-41.pdf) | long-term 110% AFR, monthly | 3.1% | 3.14% (rr-14-26.pdf) | `rr2014_26_lt110` |
| Rev. Rul. 2014-31, Dec. 2014 (I.R.B. 2014-50, irb14-50.pdf) | short-term 130% AFR, monthly | .47% | .44% (rr-14-31.pdf) | `rr2014_31_st130` |
| Rev. Rul. 2018-21, Aug. 2018 (I.R.B. 2018-32 web edition, https://www.irs.gov/irb/2018-32_IRB) | §7520 rate | .4% | 3.4% (rr-18-21.pdf and the PDF bulletin irb18-32.pdf) | `rr2018_21_7520` |

No later bulletin corrects them (each ruling number searched in the IRB corpus). The scripts keep their copies in `cache/www.irs.gov/pub/`.
Size: small (one month's rate for below-market loans, sale-leasebacks, OID); the §7520 misprint, if used, would value
annuities and remainders at 0.4% instead of 3.4%. Confidence high.

### A5. Penalty amounts carry the previous year's inflation adjustment, and the IRM repeats them (extends earlier F2)
- **Documents**: the failure-to-file minimum in Rev. Procs. 2020-45 to 2026-35: returns required to be filed in 2022
  $435, 2023 $450, 2024 $485, 2025 $510, 2026 $525, 2027 $535, 2028 $555. IRM 20.1.2.3.7.4(1)
  (https://www.irs.gov/irm/part20/irm_20-001-002r) prints the same amounts by return due date.
- **Statute**: §6651(j)(1): "In the case of any return required to be filed in a calendar year beginning after 2020,
  the $435 dollar amount ... shall be increased by ... the cost-of-living adjustment determined under section 1(f)(3)
  for the calendar year, determined by substituting 'calendar year 2019'"; (j)(2) rounds down to $5.
- **Recomputed** (ALFRED first-published C-CPI-U, `src/alfred`): adjusting for the calendar year in which the return is
  due gives 2022 $450, 2023 $485, 2024 $510, 2025 $525, 2026 $535, 2027 $555. Every published amount equals the
  literal amount for the year before: the same one-year lag as the 98 penalty amounts of the earlier work.
- **Size**: favours filers ($15-$20 lower minimum penalty). Confidence low-medium: "for the calendar year" can be read
  as the IRS does; the position dates from Rev. Proc. 2016-11.

### A6. Wage-levy exemption and disability-trust exemption 2019-2026: the IRS rounds the adjusted amount, the statute the increase (extends earlier B12 back to 2019)
- **Documents**: the annual Rev. Procs. (e.g. Rev. Proc. 2021-45 §3.50: "the dollar amount used to calculate the amount
  determined under § 6334(d)(4)(B) is $4,400"; Rev. Proc. 2018-57 §3.35: "the amount of the deduction under
  § 642(b)(2)(C)(i) is $4,200"). Published: levy 2019-2027 $4,150, 4,300, 4,300, 4,400, 4,700, 5,000, 5,100, 5,300,
  5,450; disability trust the same except 2019 $4,200.
- **Statute**: §6334(d)(4)(C): the $4,150 amount "shall be increased by" the C-CPI-U adjustment from 2017; "If any
  increase determined under the preceding sentence is not a multiple of $100, such increase shall be rounded to the
  next lowest multiple of $100." §642(b)(2)(C)(iii)(II): the trust's $4,150 "shall be increased in the same manner as
  provided in section 6334(d)(4)(C)". So every amount must end in 50.
- **Recomputed** (`IndexRun.lean`, first-published C-CPI-U from ALFRED for 2019-2022): 2019 $4,150, 2020 4,250, 2021
  4,250, 2022 4,450, 2023 4,750, 2024 5,050, 2025 5,150, 2026 5,250, 2027 5,450. Published differs by $50 in 15 of 18
  item-years (higher in 2020, 2021, 2026 and the 2019 trust figure; lower in 2022-2025); 2027 matches (the IRS
  switched methods). In 2019 the IRS gave two different figures for what the statute makes one amount.
- **Who and how much**: taxpayers under a continuous wage levy (exempt weekly amount per dependent off by about
  $1 = $50/52) and qualified disability trusts ($50 of deduction, at most $18.50 of tax). Confidence high (the
  rounding words are unambiguous). 2023-2026 were found by the indexing work (F1); 2019-2022 are new here.

### A7. Rev. Proc. 2009-21: 2009 earned income credit phase-out threshold for joint filers without children printed as $21,420; the statute gives $12,470
- **Correction (re-read 2026-11-17)**: the $21,420 is in the Bulletin edition only (I.R.B. 2009-16, irb09-16.pdf/txt line 4267). The advance release rp-09-21.pdf prints $12,470 in the no-child column, consistent with the statute. So this is a Bulletin misprint, like A4.
- **Document**: Rev. Proc. 2009-21, §3.06 (I.R.B. 2009-16, https://www.irs.gov/irb/2009-16_IRB; PDF bulletin irb09-16.pdf
  text line 4267; advance release https://www.irs.gov/pub/irs-drop/rp-09-21.pdf): "Threshold Phaseout Amount (Married
  Filing Jointly) | $21,420 | $21,420 | $21,420 | $21,420" - the last column is "None" (no qualifying children). The
  same table prints the completed phase-out for that column as $18,440, below the printed threshold.
- **Statute**: §32(b)(2)(B) and §32(b)(3)(B)(i) as amended by Pub. L. 111-5 (ARRA) for 2009: "The dollar amount in
  effect under paragraph (2)(B) shall be $5,000"; the no-child phase-out amount ($5,280, base 1995) is $7,470 for 2009
  in the same revenue procedure. Joint threshold: $7,470 + $5,000 = $12,470; completed phase-out $12,470 + $457/7.65% =
  $18,443.86 -> $18,440, the figure the IRS printed. $21,420 is the children columns' figure repeated.
- **Lean**: `lean/Audit/EicTables.lean`: with the revenue procedure's $21,420 the 2009 EIC Table fails in 118 cells of
  the married-no-child column; with $12,470 all 7,705 cells of the 2009 table match (`tables/eic_gen_2009.py`,
  `Audit/EicTables2009.lean`). So the Form 1040 instructions follow the statute and the revenue procedure does not.
- **Who and how much**: anyone computing the 2009 credit from the revenue procedure (software, practitioners) for a
  married couple without children with income between $12,470 and $18,440: up to the whole $457 credit. Taxpayers using
  the IRS table were unaffected. Never corrected (no later item names Rev. Proc. 2009-21). Confidence high.

### A8. Rev. Rul. 86-94 (federal rates for August 1986): long-term 110% AFR, monthly compounding, printed 7.96%; the rate gives 7.98%
- **Document**: Rev. Rul. 86-94, 1986-2 C.B. 147 (GovInfo GOVPUB-T22-1286c5320d83f63528466d064ff9ef02, PDF part 2,
  page 157; page image [`verify/cb1986_p157-157.png`](verify/cb1986_p157-157.png)): "110% AFR 8.27% 8.11% 8.03% 7.96%" (long-term).
- **Statute**: §1274(d)(1) and the ruling's own method: one rate per row, expressed for each compounding period. From the
  semiannual 8.11% (110% of 7.37%): monthly 12((1+.0811/2)^(1/6)-1) = 7.976% -> 7.98%; from the annual 8.27%: 7.97%;
  from the quarterly 8.03%: 7.98%. No reading gives 7.96%. Every other row of the table converts exactly.
- **Lean**: `lean/afr/RunCB.lean` `conv` (the same check as for A4): FAIL for this row only (afr/lean_out_cb.tsv); the
  110% semiannual figure passes `mult` (RunCBMult.lean).
- **Who and how much**: 2 basis points on a monthly-compounding long-term 110% rate (used for §1274 safe-harbour
  sale-leaseback and §7872 loans that month). Small. No correcting item found in the 1986-1995 Bulletins. Confidence:
  high on the page (image read by hand), OCR not involved.

### A9. Rev. Rul. 87-68 (federal rates for August 1987): long-term 120% AFR, monthly compounding, printed 9.97%; the rate gives 9.87%
- **Document**: Rev. Rul. 87-68, 1987-2 C.B. 213 (GOVPUB-T22-aea199473486be343141837068bc0f08, PDF part 2, page 225;
  image [`verify/cb1987_p225-0225.png`](verify/cb1987_p225-0225.png)): "120% AFR 10.33% 10.08% 9.96% 9.97%". The monthly figure is above the
  quarterly one, which compounding cannot produce.
- **Statute**: as A8. From the semiannual 10.08%: monthly 9.875% -> 9.87% (from the annual 10.33%: 9.88%). The
  printed 9.97% is a transposed digit.
- **Lean**: `conv` FAIL for this row only; `mult` passes for 120% of the semiannual AFR (8.40% -> 10.08%).
- **Who and how much**: 10 basis points on the monthly long-term 120% rate for August 1987 (the §483/§1274 test rate
  for some sale-leasebacks). No correction found in the 1987-1995 Bulletins. Confidence high.

### A10. Private letter rulings 202219006, 202219007 and 202219008 cite a repealed section: "§ 30(d)(1)(A)" for the original-use rule of §30D(d)(1)(A)
- **Document**: PLRs 202219006-008 (release date 13 May 2022; https://www.irs.gov/pub/irs-wd/202219006.pdf, fetched
  again 17 Nov 2026): "For a taxpayer to obtain this credit, § 30(d)(1)(A) requires that the 'original use' of the
  qualifying vehicle commence with that taxpayer", in a discussion of §30D (the letters cite §30D(a), (b), (d)(1)).
- **Statute**: §30 was repealed by Pub. L. 113-295 (19 Dec 2014; US Code history). The original-use rule is
  §30D(d)(1)(A); the sentence before it names "subsections (d)(1)(C) through (d)(1)(F)" of §30D.
- **Check**: `wd/check_docs.py` (citation to a section repealed before the document's release date), read by hand.
- **Who and how much**: a citation typo in three identical letters; no amount affected. Confidence high.

### A11. IRS Tax Withholding Estimator (2026 code): qualifying-relative gross income limit $5,200; for 2026 it is $5,300
- **Document**: github.com/IRS-Public/tax-withholding-estimator, `src/main/resources/twe/facts/ctcOdc.xml`, fact
  `/odcDependentGrossIncomeThreshold` = $5,200, tagged `<TaxYear>2025</TaxYear>` (main branch, last commit 22 Oct 2026;
  raw file fetched again 17 Nov 2026). It is shown to users in the credits flow: "Has a gross income less than $5,200"
  (`flow/credits.xml` line 217, English and Spanish). All 123 other year-tagged facts are for 2026.
- **Statute and guidance**: §152(d)(1)(B) with §151(d); Rev. Proc. 2025-32 §3.23 (rp-25-32.pdf, fetched again): "For
  taxable years beginning in 2026, the exemption amount referred to in § 152(d)(1)(B) is $5,300." ($5,200 is the 2025
  amount.)
- **Check**: `public/twe_vs_revproc.py` (every TWE dollar constant >= $1,000 looked up in Rev. Proc. 2025-32: 317 found,
  this one wrong, the rest statutory, SSA or Pub 15-T figures).
- **Who and how much**: users estimating 2026 withholding with a relative earning $5,200-$5,299 are told the relative
  does not qualify for the $500 credit for other dependents. Small. Confidence high.

### A12. SOI Historical Table 23: married couple's personal exemptions for 2016 and 2017 printed as $8,010; the statute gives $8,100
- **Document**: IRS Statistics of Income, Historical Table 23 "U.S. Individual Income Tax: Personal Exemptions and
  Lowest and Highest Bracket Tax Rates, and Tax Base for Regular Tax, Tax Years 1913-2018"
  (https://www.irs.gov/pub/irs-soi/histab23.xls, last modified 13 Jan 2021, fetched 17 Nov 2026), rows 2016 and 2017:
  single persons $4,050, married couple **$8,010**, dependents $4,050.
- **Statute**: §151(b) (an exemption for the taxpayer and one for the spouse on a joint return) and §151(d), the
  exemption amount $4,050 for 2016 and 2017 (Rev. Proc. 2015-53 §3.24, Rev. Proc. 2016-55 §3.24; indexing/published.json).
  Two exemptions: $8,100. The table's own 2014 and 2015 rows are exactly twice the single amount ($7,900, $8,000).
- **Check**: `soi/histab23_check.py` (62 cells 1998-2018 against the verified amounts; these 2 differ).
- **Who and how much**: a statistical table, not a rule: anyone using the IRS's historical series (researchers,
  tax-history datasets) gets $90 less per couple for 2016-2017. Small. Confidence high.

### A13. Private letter rulings 201602001 and 201432008 misstate the section 2631(a) GST exemption they quote: "$5,012,000" and "$1,000,0000"
- **Documents**: PLR 201602001 (release date 8 Jan 2016): "Section 2631(a), as effective in the year at issue, provided
  that ... every individual shall be allowed a GST exemption of **$5,012,000** (adjusted for inflation under
  § 2631(c))". PLR 201432008 (release date 8 Aug 2014): "Section 2631(a), as in effect for the year at issue, provides
  that ... every individual shall be allowed a GST exemption of **$1,000,0000**". Both fetched again from
  https://www.irs.gov/pub/irs-wd/ on 17 Nov 2026.
- **Statute**: §2631(a) as enacted (Pub. L. 99-514) and until 2003: "a GST exemption of $1,000,000", indexed under
  §2631(c) from 1999 ($1,010,000 to $1,120,000 for 1999-2003); from 2004 §2631(c) makes the exemption equal to the
  §2010(c) basic exclusion amount ($1,500,000 ... $5,000,000 for 2011, $5,120,000 for 2012, $5,250,000 for 2013, ...).
  No year has $5,012,000, and the statute never printed it; "$1,000,0000" is $10,000,000 as written, ten times the
  statutory figure.
- **Check**: `wd/amounts_scan.py` (219 GST-exemption amounts in the harvested letters: these 2 are not a value the
  statute ever set; the other 8 candidates are unified-credit amounts, 5-and-5 powers and an annuity exclusion, all
  correct).
- **Who and how much**: typos in the statement of law in two letters (the rulings grant §2642(g) extensions; the
  outcomes do not turn on the figure). Small. Confidence high.

### A14. Private letter ruling 202116006 cites two wrong (repealed) sections when stating the law: "§ 2057(b)(7)" for §2056(b)(7) and "§ 2011(a)" for §2611(a)
- **Document**: PLR 202116006 (release date 23 Apr 2021; https://www.irs.gov/pub/irs-wd/202116006.pdf, fetched again
  17 Nov 2026): "Section 2044(b) provides that § 2044(a) applies to any property if a deduction was allowed with respect
  to the transfer of such property to the decedent under **§ 2057(b)(7)** and § 2519 did not apply ..."; "A
  generation-skipping transfer is defined under **§ 2011(a)** as (1) a taxable distribution, (2) a taxable
  termination, and (3) a direct skip."
- **Statute**: §2044(b)(1)(A) refers to "section 2056 by reason of subsection (b)(7) thereof" (the QTIP marital
  deduction); the three kinds of generation-skipping transfer are defined in §2611(a). §2057 (family-owned business
  deduction) and §2011 (state death tax credit) were struck by Pub. L. 113-295 (19 Dec 2014; US Code history) and never
  said either thing.
- **Check**: `wd/check_docs.py` (citations to sections repealed before release; 1,801 such citations in 17,451 letters,
  all others legitimate: REJECTED 22 and 29), read by hand.
- **Who and how much**: citation typos in the statement of law; the ruling (a §2642(g) extension) does not depend on
  them. Small. Confidence high.

## Part B: earlier verified findings inside the 12 collections (not re-derived here unless noted)

Lean and notes: [TaxCode/Big/](../TaxCode/Big) (B1-B3, B6, B7, B10), [TaxCode/Forms/](../TaxCode/Forms/FINDINGS.md)
(B5, B9, B11), [TaxCode/Forms/Reported/](../TaxCode/Forms/Reported) (B4, B8) and
[TaxCode/Indexing/](../TaxCode/Indexing/FINDINGS.md) (B12-B15); each was re-checked the same way.

| # | Document (collection) | Departure | Most per filer | Confidence |
|---|---|---|---|---|
| B1 | Pub. 523 (2025) Worksheet 1 (10) | joint filers with one spouse on a partial exclusion: the worksheet stops at $250,000; §121(b)(2)(B) and Reg. §1.121-3(g)(2) Ex. 2 add the other spouse's reduced amount | about $59,400 tax | medium-high |
| B2 | 2026 draft Form 6251 lines 1a-4 (10) | AMT income keeps the §68 reduction; §56(b)(1)(E) "Section 68 shall not apply" | $15,135 per $1M of itemized deductions | high (draft) |
| B3 | Pub. 936 (2025) Table 1 (10) | one interest ratio across pre-2018 and later mortgages; §163(h)(3)(F)(i)(IV) | $7,400-$14,800 tax | medium-high |
| B4 | 2018 Schedule D Tax Worksheet, original edition (10) | 28%/§1250 gain path misreads §1(h); the IRS corrected it in May 2019 | $11,288 over / $7,752 under (joint) | high |
| B5 | Form 1040 instr. line 27, Pub. 596, Pub. 3524 (10) | separated-spouse EIC test narrower than §32(d)(2)(B)(iii)(II) with §121(d)(3)(C) | $8,046 | medium |
| B6 | Schedule 1-A (2025) SSTB tips (10) | relief wider than §224(d)(2)(B), resting on Notice 2025-69's non-enforcement | $6,000 tax | high (as a reading) |
| B7 | Form 8839 (2025) lines 11b-13 (10) | refundable $5,000 per child; §23(a)(4) has one $5,000 | $5,000 per extra child (timing) | medium |
| B8 | Pub. 525 (2020-2023) Worksheet 2a line 4 (10) | "go to line 5" drops taxable refunds when the SALT cap does not bind; fixed in the 2024 edition | the whole refund | high |
| B9 | Schedule 8812 lines 16a-17, 27 (10) | refundable child credit above §24(h)(5) | min($500 x other dependents, $1,700 x children) | high |
| B10 | Form 8889 line 3 (10), following Notice 2008-52 (3) | "greater of" rule ignores "solely by reason of" in §223(b)(8)(A)(ii) | $1,441 / $663 tax | high (text) |
| B11 | Schedule 8812 line 2b (10) | Form 2555 lines 45/50 instead of "the amount excluded" (§24(b)(1)) | ±$50 per $1,000 | medium |
| B12 | Rev. Procs. 2022-38 to 2025-32 (2) | the adjusted amount rounded where the statute rounds the increase: §7702B(d) per diem, §213(d)(10) $375 tier (levy and §642(b) re-derived and extended in A6) | a few dollars each | high |
| B13 | Rev. Proc. 2022-38 (2) | 2023 qualifying-relative income limit $4,700; the IRS's own method gives $4,800 | dependency at the margin | medium-high |
| B14 | Rev. Procs. 2022-38, 2023-34, 2024-40 (2) | MFS 15% capital-gains breakpoint $25 below half the joint amount | $1.25 | medium |
| B15 | Rev. Procs. 2023-34, 2025-32 (2) | text errors: "filed in 2024" (should be 2025), "August 1, 2026" (2027), "$191,150" (should be $191,950) | none (typos) | high |