# 2025 IRS forms vs the statute, proved in Lean (`TaxCode/Forms/`)

Build: `lake build TaxCode.Forms.All` (the `TaxCode` lean_lib covers the folder). No `sorry`, no `native_decide`; `#print axioms` on every
headline theorem shows only `propext`, `Classical.choice`, `Quot.sound`. Large tables: a per-row Boolean test proved
sound once for all rows, then evaluated by the kernel (`decide +kernel`).
Sources: the 2025 PDFs from https://www.irs.gov/forms-instructions (2025 editions from https://www.irs.gov/pub/irs-prior/
where irs.gov now serves 2026; 2026 drafts from https://www.irs.gov/draft-tax-forms). Tables parsed from the PDF text by `tools/forms/parse_tax_table.py` and
`parse_eic_table.py` (only the first three Tax Table lines, printed vertically, are read by hand).

| # | Form line | Statute | Equal for all inputs? | Direction | Proved bound | Who | Reg/notice | Published? | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Sch 8812 lines 16a-17, 27 (CLW B 2, 13) | §24(h)(5), (d)(1)(A) | No | form more | excess = pos(line 27 - child credit after phase-out) exactly; max = min($500 x other dependents, $1,700 x children), attained for every n, k (`actc_difference_exact`, `actc_excess_le`, `actc_excess_attained`) | >= 1 other dependent, phase-out reduction > $500 x children | none | yes ("$200 vs $700"); exact set/max new | high |
| 2 | Sch 8812 line 2b (Form 2555 lines 45 and 50) | §24(b)(1) "amount excluded ... under section 911" | No when line 50 != line 44 | either: form lower by <= $50 per $1,000-or-fraction of (line 50 - line 44), higher by same of (line 44 - line 50) (`l12_diff_2555`; examples $1,250 v $2,200, $2,900 v $1,400) | +-$50 x ceil(gap/1000) | self-employed abroad near $200k/$400k with children | none found | same root cause known for Sch 1-A and 8962 (Schedule1A.md 3-4, Credits.md 5); not seen for §24 (1 search) | medium |
| 3 | Sch 8812 Part I, CLW A/B, Part II-B, PR route | §24(a)-(d), (k)(2)(B), §26(a) | Yes (no other dependent, no 2555): line 27 = §24(d); CLW A line 2 + line 14 + later credits = §26(a) aggregate (`actc_eq_no_others`, `nonref_eq`, `l12_eq_statute`) | - | - | - | - | - | high |
| 4 | Sch D Tax Worksheet 1-47 (no Form 4952) | §1(h)(1)(A)-(F), (3), (4), (6), (11), §1(j)(5) | Yes, all inputs >= 0, exact schedule (`w47_eq_statute`, L13..L42); line 47 <= ordinary tax (`w47_le`); = QDCG worksheet without 25%/28% gain (`schD_eq_qdcg`) | - | - | - | - | - | high |
| 5 | Sch D TW line 22 / QDCG line 9 (0% amount) | §1(h)(1)(B)(ii) "taxable income reduced by the adjusted net capital gain" (no floor) | Only under the floored reading. Literal (B) exceeds line 22 by exactly min(ANCG - TI, TI - 0% ceiling) when ANCG > TI (`literalB_excess`); single, $70,000 qualified dividends, TI $54,250: literal $0, worksheet $885 (`literal_differs`) | literal gives less tax | <= 15% x (TI - ceiling) | gains exceed taxable income, TI over the 0% ceiling | worksheet floors; no reg | not found (1 search) | low (a court would likely floor) |
| 6 | 2025 Tax Table (2,062 printed rows) | §1(j), §3 | No (by design) | both | exact maxima, every column: +$6.00 / -$4.78 vs exact §1(j); +$6 / -$5 vs rounded; attained at $99,950 / $99,999 (`table_bounds`, `table_bounds_rounded`); printed rows = midpoint rule (`rows_midpoint`) | under $100k | §3 | +-$6 shape known (model had <= $6) | high |
| 7 | Tax Computation Worksheet (>= $100,000) | §1(j) | Yes to the cent, 20 printed subtraction amounts (`tcw_eq_statute`) | - | - | - | - | - | high |
| 8 | 2025 EIC Table (1,374 rows x 8 + starred footnotes) | §32(a)-(b) | No (§32(f) bands) | both | exact maxima per column: over $2.575/$10/$12/$13.50 (0/1/2/3+), under $2.89 (single 0) / $2.88 (MFJ 0) / $7.66 / $9.60 / $11.05; all attained (`table_bounds`, `table_bounds_attained`); printed = model rule (`printed_eq_model_rule`) | all | §32(f) | rounding | high |
| 9 | EIC Worksheet A | §32(a)(2) | Yes up to row 8 bounds, all earned income/AGI >= 0 (`worksheetA_bounds`) | - | - | - | - | - | high |
| 10 | EIC Step 2 investment income | §32(i)(2)(A),(B),(D) | Yes (no rents/passive) (`investment_income_eq`) | - | - | - | - | - | high |
| 11 | 1040 instr. line 27 "Special rule for separated spouses"; Pub 596 Rule 3 | §32(d)(2)(B)(iii)(II) + §121(d)(3)(C) | Grid finding PROVED: form is a strict subset (`sepForm_le`); excluded set exactly: not apart all last 6 months, not same household at year end, holds a §121(d)(3)(C) instrument, and not (state-law legal separation with a written agreement or maintenance decree), incl. support-decree-only (`sep_difference`) | form less | whole credit, <= $8,046 | separated parents without state-law legal separation | none | grid (Credits.md 3); no text comparison found (1 search) | medium |
| 12 | SS Benefits Worksheet 1-18 | §86 | Yes within its domain (`worksheet_eq_statute`); omits §135/137/911/931/933 add-backs but the line 6a/6b Exception (top of p. 32) sends those filers to Pub 915. No finding | - | misuse only: <= 85% of excluded (`worksheet_le_statute`) | - | - | - | high |
| 13 | Schedule SE 3-13 | §§1401(a),(b)(1), 1402(a)(12),(b) | Yes exactly (`l12_eq_statute`, `l13_eq_statute`) | - | - | - | - | - | high |
| 14 | Form 8959 1-13, 18 | §3101(b)(2), §1401(b)(2) | Yes exactly (`l18_eq_statute`) | - | - | - | - | - | high |
| 15 | Form 6251 4-7, Exemption Worksheet, MFS line 4 (no gains/AMTFTC) | §55(b)(1)(A), (d) | Yes (`l7_eq_statute`, `note_ok`) | - | - | - | - | - | high |
| 16 | Form 8960 line 5a (Form 1040 line 7a loss) | §1411(c)(1)(A)(iii) "net gain" | No | form less tax | <= 3.8% x loss <= $114 ($57 MFS) (`loss_effect`) | net capital loss + NIIT | Reg. §1.1411-4(d)(2) and Ex. 1 allow the §1211(b) loss (read on eCFR) | explained by reg | high |
| 17 | Form 8960 line 13 | §1411(d) | Yes, uses 2555 line 42 net of disallowed deductions, unlike row 2 (`eq_no_loss`) | - | - | - | - | - | high |
| 18 | Form 8995 2-15 (one business, no REIT/PTP, below threshold) | §199A(a), (b)(2)(A), (b)(3)(A) | Yes (`l15_eq_statute`) | - | - | - | - | - | high |
| 19 | Std deduction chart (14 printed amounts), worksheet for dependents | §63(c)(2),(5),(7), (f) | Yes (`chart_eq_statute`, `depWorksheet_eq`) | - | - | - | - | - | high |
| 20 | IRA Deduction Worksheet line 7 | §219(g)(2)(A)-(C) | Yes for all MAGI in range, 4 limit/range pairs: deduction up to $10 = reduction down to $10 (`iraL7_eq`). QSS $146,000 on line 2 is the model's known finding (A/FINDINGS 2) | - | - | QSS | Pub 590-A | in model | high |
| 21 | Student Loan Interest Worksheet line 7 (3 decimals) | §221(b)(2)(B) | rounding only, <= $1.25 (example `sli_example`; general bound not proved) | either | - | - | stated rounding | n/a | high |
| 22 | Sch 1-A lines 3/31 MAGI (2555 lines 45, 50) | §§151(d)(5)(C)(iii)(II), 224, 225, 163(h)(4) | No: `magi_gap`, `senior_gap` (<= 6% of gap + $1), `tips_gap` ($100 per whole $1,000), `car_gap` ($200 per $1,000 or part); grid examples as theorems | either | as stated | self-employed abroad | none | already found (Schedule1A.md 3-4) | medium |
| 23 | Form 8880 line 4 (inherited IRA distributions excluded) | §25B(d)(2)(A) | No: form >= statute, excess <= rate x distribution and <= $1,000/person (`saver_inherited`) | form more | $1,000/person | nonspouse beneficiaries | none | already found (Credits.md 7) | medium |
| 24 | Form 2441 lines 4/5 deemed income for unmarried student/disabled | §21(d)(1)-(2) | No: statute 0, form up to $3,000/$6,000 of expenses (`cdcc_unmarried_student`) | form more | 35% x $3,000/$6,000 before tax limit | unmarried students | none | already found (Credits.md 6) | low-medium |
| 25 | Form 1040 lines 11b-22, §63(e) | §63(a),(b),(d),(e), §26(a) | Yes: line 15 = `B.taxableIncome` for every household/election (`l15_eq`); line 22 floor never binds (`l22_eq`); larger deduction minimises line 15 (`default_minimises_l15`) | - | - | - | - | - | high |

## Not covered / open

- Form 8839, Form 8962 PTC amounts, Form 2441 Worksheet A prior-year expenses (Credits.md 1, 2, 4, 8, 10): no
  adoption model; PTC and prior-year CDCC not formalised here.
- Sch 8812 / Form 2555 caution "If you file Form 2555, you cannot claim the ACTC" vs §24(d)(3) "elects to exclude":
  a filer with only a §911(c)(4) housing deduction may be barred by the form but not the statute. Open (needs Reg.
  §1.911-7 on whether the deduction requires an election).
- §24(k)(3)(C)(ii)(II): American Samoa residents get the Puerto Rico rule absent an approved plan; the form names only
  Puerto Rico. 2025 plan status not checked.
- Form 6251 Part III, Form 8995-A, Form 4952 elections, worksheets with the Tax Table instead of the exact schedule
  (bounded separately by row 6); §1(h)(1)(A)/(F) with negative intermediate amounts.
- 2026 drafts fetched; Schedule 8812 2026 has the same structure and amounts, so rows 1-3 carry over by inspection
  (not re-proved).
