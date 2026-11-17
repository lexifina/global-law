# Candidate flags rejected after verification

Each item: what the first-pass check reported, and why it is not a departure from the statute. Paths are relative to
this folder.

## Readings where the IRS's method fits the words
1. **Section 7520 rate, 16 months (1996-2025)** (`afr/lean_out.tsv`, check `s7520`): 120% of the printed annual
   mid-term AFR, rounded to the nearest 0.2%, differs from the IRS's rate (e.g. Rev. Rul. 2001-7: 1.2 x 5.07% = 6.08% ->
   6.0%; IRS 6.2%). The IRS rounds its printed "120% AFR" mid-term annual figure (120% of the semiannual AFR, stated
   with annual compounding): that rule reproduces 341 of 342 months (the other is the 2018-32 misprint, finding A4).
   Reg. §20.7520-1(b)(1)(i): "120 percent of the applicable Federal mid-term rate, compounded annually" fits the IRS's
   order of operations; the statute's "Federal midterm rate" is itself a semiannual rate (§1274). Not an error.
2. **110%-175% AFR rows**: computed from the annual AFR, 1,563 of 3,795 differ; computed from the semiannual AFR
   (the statutory base, §1274(b)(2)(B)) all 3,795 match. The IRS uses the right base.
3. **Minimum failure-to-file penalty $330 for returns due in 2021** (Rev. Proc. 2019-44, November 2019): the SECURE Act
   (Pub. L. 116-94, 20 December 2019) raised the amount to $435 for returns due after 2019, a month after the revenue
   procedure; the next one (Rev. Proc. 2020-45) uses $435. Statute changed after publication.
4. **2025 standard deduction $30,000 / $22,500 / $15,000** (Rev. Proc. 2024-40): Pub. L. 119-21 (July 2025) set
   $31,500 / $23,625 / $15,750 retroactively; Rev. Proc. 2025-32 restates them. Statute changed after publication.
5. **2003 rate-schedule thresholds $14,000 and $56,800 (joint) missing from Rev. Proc. 2002-70**: the Jobs and Growth
   Act of 2003 (Pub. L. 108-27, May 2003) changed the 2003 brackets retroactively; the 2003 Form 1040 instructions
   follow the amended statute. Not an error.

## Not errors of substance (presentation or rounding stated by the IRS)
6. **2001 Schedule Y-2 base amounts $12,196.88 and $44,153.38**: exact values $12,196.875 and $44,153.375, printed to
   the cent. Half-cent rounding.
7. **Four Appendix A interest-factor tables** (Rev. Ruls. 2011-12, 2012-16, 2016-28, 2019-21) appear under a
   "365 Day Year" heading in the bulletin text but hold 366-day factors (e.g. 1 day at 0.5%: 0.000013661 = 0.005/366);
   with 366 days every factor checks. Heading only, in a leap-year table.
8. **Section 642(c)(5) deemed rate for 2021 (2.2%)**: the check fails only because it reads the August 2018 section 7520
   rate as 0.4% (finding A4's misprint); with 3.4% the rule gives 2.2%.
9. **IRM 20.1.2.3.7.4 "After 12/31/2026: $535"**: Rev. Proc. 2026-35 (5 Nov 2026) sets $555 for returns due in 2028;
   the IRM page predates it and its note says amounts are updated by revenue procedure. Watch, not flag.

## Errors in the first pass (ours), corrected before counting
10. **Basic exclusion amount 2015 ($5,430,000) and 2023 ($12,920,000)**: the first spec rounded down; §2010(c)(3)(B)
    says "rounded to the nearest multiple of $10,000". With nearest rounding all 16 years match.
11. **EIC investment-income limit 2023-2027**: the first spec used base 2021; §32(j)(1)(B)(iii) (Pub. L. 117-2) says
    "calendar year 2020". With 2020 all match.
12. **AFR parse artifacts**: four 2003 rulings (value printed before its label in the PDF text), Rev. Rul. 2015-7
    (value printed without "%"), Rev. Rul. 2021-1 (".6%"), Rev. Rul. 1996-27 ("8%"): all pass once read correctly.
13. **1995-1996 Tax Table rows taken from the EIC table** on the same pages (first parse): with the ordering filter
    (joint <= single <= separate) every row of both years matches.

## Classes counted but not treated as departures
14. **Regulations citing Code sections that no longer exist** (`cfr/xref.json`): 5,264 citations in 26 CFR to 345
    section numbers absent from the current Title 26 (67 with a repeal recorded in the US Code history, e.g. §902 and
    §1201 by Pub. L. 115-97, §809 by Pub. L. 108-218). Most regulations of this kind govern years before the repeal and
    stay in the CFR for that reason; a stale citation is not by itself a departure from the statute.
15. **IRM citations to repealed sections** (`irm/xref.json`): same reasoning (e.g. IRC 6697, repealed by Pub. L.
    111-325, still in an IRM list of assessable penalties; IRC 902 marked as repealed in the IRM's own text).
16. **2020 EIC Table row $3,200-$3,250** (`tables/eic_out.txt`): the parser took the Tax Table row printed later on the
    same page; the EIC row itself (i1040gi--2020.txt line 3089: 247, 1,097, 1,290, 1,451, 247, 1,097, 1,290, 1,451)
    equals the rule in all eight columns. Parse artifact.
17. **Citations to repealed sections in current rulings, procedures, notices and announcements**
    (`inventory/guidance_xref.json`): 592 item-section pairs in items no later item modifies, supersedes, revokes or
    obsoletes; 204 items cite a section the US Code history shows repealed before the item was published. A read of the
    25 latest: section numbers of other laws (Administrative Procedure Act §553, Paperwork Reduction Act 44 U.S.C. §3507,
    SECURE Act §114), section numbers of the revenue procedure itself ("section 30 of this revenue procedure"),
    obsolescence notices that list guidance under repealed sections on purpose (Notice 2025-36, Notice 2026-58), and
    no-rule lists that keep pre-repeal sections for open years (Rev. Proc. 2026-3: §199, §1551). None is a departure.
18. **Column totals in printed tables** (`inventory/table_totals.json`): 56 of 165 "Total" rows differ from the sum of
    the rows the parser grouped above them. The two inspected (Rev. Proc. 2015-14 inventory example, Rev. Proc.
    2016-51 EPCRS Table 1) are parse artifacts: negatives printed as "<100,000>", footnote digits fused to amounts
    ("$7501" = $750 + note 1). Not reviewed one by one, not counted. The row totals (148) and the APA reports'
    cumulative counts (52) all add up.
19. **Section 7702(f)(11) average for the 60 months ending 31 Dec 2021** (Rev. Rul. 2022-1, Table 7: 1.72%): first
    flagged because the corpus lacks the January 2017 ruling; with Rev. Rul. 2017-2 (rr-17-02.pdf, mid-term 1.97%) the
    average is 1.7155% -> 1.72%. All six averages (2019-2024 periods) match. Resolved, not a flag.

## Cumulative Bulletins, written determinations, IRS software and annual CFR editions
20. **Cumulative Bulletin AFR rows that fail only through OCR** (`afr/lean_out_cb.tsv`): Rev. Rul. 89-39 (two rows,
    "160" and "126" for 11.60% and 11.26%), August 1991 ("176" for 11.76%), December 1991 ("198" for 11.98%): the
    OCR dropped a digit; the digits restored, each row converts exactly. Not flags.
21. **Positional checks on CB AFR tables** (s42 for Rev. Ruls. 89-92, 92-67, 93-19; 67 positional multiples): the
    parser took rows by position while OCR had broken or relabelled rows ("1l0%", "110070", "Mi d-Term"). Replaced by
    checks on the printed row labels (`afr/gen_lean_cb_mult.py`): 436 of 437 multiples and all 42 s42 pairs pass;
    the one left is the OCR row of item 20. Not flags.
22. **Written determinations citing sections repealed before release** (`wd/checks.json`): 125 of 126 are legitimate
    (TEFRA §§6221-6234 for pre-2018 years, §1022 for 2010 estates, §§54A/54F bonds issued earlier, §902 for pre-2018
    years, 1939-Code §28 in a history of §565, §2210 history, the Form 982 title "Section 1082 Basis Adjustment", §1034
    for pre-1997 sales). The remaining one is finding A10.
23. **Citations in the 1987-1995 Cumulative Bulletins** (`src/govinfo/cb_cites.json`): the Title 26 history records
    most sections only from the 1994 edition (dated 1995-01-04), so 1987-1994 volumes cannot be checked for repealed
    sections; the 304 "added later" flags are reused section numbers (§§6676, 23, 2057, 91, 646 existed earlier with
    other content), §530 of the Revenue Act of 1978, and OCR splits ("685 I" for 6851). Not flags.
24. **IRS-Public constants that differ from the guidance by design**: EITC Assistant and TWE `hsaTotalDeductibleAmountMax`
    (= the HDHP out-of-pocket maximum, family: $15,000/$16,100/$16,600/$17,000 for 2023-2026) and doubled IRA limits
    ($15,000-$17,200) are self-described simplifications ("We are agnostic to filing status so double ..."); TWE facts
    still tagged 2025 for unchanged statutory amounts (elderly credit limits, $2,000 Schedule 3 line 6g, 365 days).
    Not flags.
25. **Table U(1) 2010CM (unitrust remainder factors)**: 10,794 of 11,000 printed factors differ from my
    reconstruction (Sum (1-k)^(t+1) d/l x 1/(1-k/2)) by under 0.01% relative, growing with the payout rate: that formula
    is not the one in Reg. 1.664-4(e) (the formula is printed as an image). Not checked, not flags.
26. **Table S (90CM), age 46 at 6.4%, printed .18110 in every annual 26 CFR edition 2001-2016** (`cfr/annual_table_s.py`,
    29 identical cells): the exact rational value is 0.1810949974, 2.6 x 10^-9 below the rounding tie, so exact
    arithmetic gives .18109. Any computation with ordinary floating point (the IRS's, and this audit's first Table S check) lands on .18110.
    A precision tie, not a departure; the other 372,871 factors in the 20 editions match exactly.
27. **2025 standard deduction in Pubs 501 and 17 ($15,750 / $31,500 / $23,625)**: differs from Rev. Proc. 2024-40
    ($15,000 / $30,000 / $22,500) because Pub. L. 119-21 §70102 raised the 2025 amounts after the revenue procedure;
    the publications follow the amended §63(c)(7). Not a flag.
28. **Written-determination amount candidates** (`wd/amounts_scan.py`): unified-credit amounts ($192,800, $345,800),
    "5 and 5" powers ($5,000) and an annuity exclusion ($3,186.93) caught by the pattern; all correct. The two real
    misstatements are finding A13.
29. **Post-repeal citations at scale** (`wd/checks.json`, final pass: 2,444 in 25,918 written determinations and Chief
    Counsel documents with text; reviewed by section): §1022 (1,425: 2010 estates'
    carryover-basis elections), §2210, §§54A/54AA/54C/54F bonds, ETI §§941-943 and §114, FSC §§921-927, §29 (for years
    before its 2006 redesignation as §45K, said so in the letters), §809, §§551/556, TEFRA, §1071 (a 1966 ruling
    described), 42 U.S.C. §418, Pub. L. 105-34 §1056, §2011 as a trust formula from an old will, PUHCA §§1081-1083 (transition),
    §199 for pre-2018 years (GLAM AM-2020-007), §§552-554 foreign personal holding companies, §§1246-1247, §1491 history,
    §2033A legislative history, Bankruptcy Code §§341 and 554 written "B.C. §": legitimate. Departures:
    A10 and A14.
