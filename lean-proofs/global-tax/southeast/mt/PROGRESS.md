# Malta (MT) PROGRESS
Status: done (7 of 7 steps; Eurostat household referee added). Updated 2026-11-19.
Web searches used: 1/3 (EUROMOD MT report location; a 2nd attempt failed on a usage limit and returned nothing).

Year: income of calendar 2025 = year of assessment (YA) 2026 (Cap. 123 art. 56 tables marked "§ Applicable from
year of assessment 2026", Act IX of 2025; checked in the official PDF refs/Act_2025_9.txt).

## Files
- lean/ (MtTax: Params, Model, Theorems, Findings, Main; exe mttax): 691 lines, 71 definitions, 46 theorems, 0 sorry.
- elections.json: mtSeparate (married), mtInterestDeclared (interest), mtDividendsDeclared (dividends).
  Other input fields: mtRentFinal, mtDividendsUnlisted, mtLoneParentConditions (default true), mtPartTime1/2.
- FINDINGS.md (F1-F11), CATALOGUE.md (K1-K14), USEFUL.md, results/summary.json,
  results/search/ (generic scanners, rerun on the final exe), results/owner_mt.json (harness/owner_mt.py).
- law/: statute texts (Global law) incl. diffs 2024->2025->2026 of art. 56 and art. 12; refs/: official PDFs
  (Act IX 2025, Act III 2026, L.N. 10 of 2025) as text, EUROMOD CR MT 2021-2024 (em_mt.txt), L.N. 2026 scan log.

## Steps
1. Model: done (income tax three tables + joint/separate + lone parent; interest/rent/dividends incl. imputation and
   art. 12 exemption; part-time 10 %; PRS credit; Class One/Two weekly; Children's Allowance).
2. Validation: parameter level (official Act PDF 18/18; EUROMOD 2024 system 21/21) and household level
   (Eurostat earn_nt_net 2025: 52 lines, 14 within EUR 1, 22 within 1 %; every gap explained in FINDINGS F12:
   budget tax refund, 2025 administrative SSC ceiling EUR 54.58/wk, child-allowance supplements, in-work benefit).
3. Proofs: done (kernel one-liners, table = formula, table order, joint/separate bounds, class1 cap, CA floor).
4. Known loopholes: 14 catalogued, 5 recreated blind, 6 not modelled.
5. New: F7 (lone-parent maintenance/cohabitation notch, up to EUR 850); lead F9 (art. 12 exemption + 6/7 refund).
6. Gov/statute: F1 (art. 12 thresholds stale), F2 (Act III 2026 EUR 10,270), F3 (YA 2025 notches), F4 (wording
   gaps), F5 (L.N. 10/2025 rows), F10 (EUROMOD description), F11 (2025 schedules unpublished).
7. USEFUL.md: done.

## Open issues / resume here
- 2025 administrative SSC: Eurostat shows a EUR 54.58 weekly maximum (F11); Children's Allowance 2025 amounts and
  the annual tax refund still lack a published legal text: if a 2025 schedule L.N. appears, update Params.
- Class Two on investment income (self-employed, non-occupied) not modelled; Children's Allowance supplement, COLA
  benefit, in-work benefit, school/childcare deductions not modelled.
- Check with CfR practice: parent table for each spouse under art. 50 (statute wording, EUROMOD says single), the
  F9 6/7-refund lead, and whether Class One/Two are deductible (EUROMOD says yes; art. 14 has no such deduction).
