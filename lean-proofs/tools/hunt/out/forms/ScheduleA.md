# Schedule A and related forms: where form and statute differ

Statute: Title 26 through Pub. L. 119-138 (`tools/hunt/sec.py`). Forms: irs.gov 2025 revisions and 2026 drafts. Model and grid: `ScheduleA/compare.py` (42,137 points), output `ScheduleA/grid.json`; form texts in `ScheduleA/*.txt`.

## Differences, largest first

### 1. Schedule A line 5e and State and Local Tax Deduction Worksheet (2025; same wording on the 2026 draft face)

- Form: Schedule A line 5e and State and Local Tax Deduction Worksheet (2025; same wording on the 2026 draft face): the half limit and half threshold go to filing status "married filing separately" only
- Statute: 164(b)(6)(B), (7)(B)(i): "a married individual filing a separate return". Section 164 does not refer to 7703, and 7703(b) (married, living apart, treated as not married) applies only "for purposes of those provisions of this title which refer to this subsection"; 2(c) covers Part I only. Read literally, a married person who lives apart and files as head of household is still a married individual filing a separate return.
- Direction: form gives more
- Example: 2026, head of household under 7703(b), MAGI $375,000, SALT paid $45,000: form $40,400; literal statute $5,000 (half of the $10,000 floor after phasedown from half threshold $252,500). 2025, MAGI under $250,000, SALT $30,000: form $30,000, statute $20,000.
- Size and who: deduction gap up to $20,000 (2025) / $20,200 (2026) below the half threshold, up to $35,000 / $35,400 between the half and full thresholds; tax up to about $12,000. Affects married people living apart who file as head of household and pay more than $20,000 of state and local tax (more than $5,000 at high income).
- Explained by: nothing found; no regulation or notice under 164(b)(6). Other sections say it expressly (63(g), 55(d)(1), 1411(b)(2), 3101(b)(2)(B), 1(d)).
- Published: not found (1 search)
- Confidence: medium: the text is clear, but the form follows practice since 2018 and a court could read "married" with 7703

### 2. Form 6251 (2026 draft) lines 1a, 1b, 2a, 3 and draft instructions (Nov 6, 2026)

- Form: Form 6251 (2026 draft) lines 1a, 1b, 2a, 3 and draft instructions (Nov 6, 2026): line 1a starts from Form 1040 line 14, which contains line 12e = Schedule A line 18, the itemized deductions after the new overall limitation; no line and no instruction takes the limitation back out
- Statute: 56(b)(1)(E): "Section 68 shall not apply" in determining alternative minimum taxable income; 68(a) reduction is 2/37 of the lesser of itemized deductions or taxable income over the 37% bracket start
- Direction: statute gives more
- Example: Single, AGI $1,400,000, itemized deductions $100,000 (of which $10,000 taxes): section 68 reduction $5,405. Statute AMTI $1,310,000; form AMTI $1,315,405.
- Size and who: AMTI too high by the whole section 68 reduction (5.405% of itemized deductions for those well into the 37% bracket); at 28% that is $1,514 of AMT per $100,000 of itemized deductions ($15,135 on $1,000,000). Affects itemizers in the 37% bracket who owe AMT (large ISO exercises, private activity bond interest, etc.), and their minimum tax credit.
- Explained by: nothing; the draft instructions do not mention section 68. Before 2018 Form 6251 had a line for this (2017 line 6).
- Published: not found (1 search)
- Confidence: high on the draft text; the 2026 Schedule A instructions (Itemized Deductions Worksheet) are not posted, but line 18 of the draft form is plainly the limited amount

### 3. Schedule A (2026 draft) lines 11-15

- Form: Schedule A (2026 draft) lines 11-15: line 13 = line 6 of a "Charitable Contribution Limitation Worksheet" on this year's gifts, line 14 "Carryover from prior year", line 15 = 13 + 14. Pub. 505 (2026) Worksheet 2-5 shows the 6 lines: gifts (cash + other) minus 0.5% of AGI
- Statute: 170(b)(1)(I): contributions "otherwise allowable (without regard to this subparagraph)" are allowed only to the extent their aggregate exceeds 0.5% of the contribution base, so the floor comes after the percentage limits and covers carryovers, which 170(d)(1)(A) treats as paid in the later year; 170(d)(1)(C) adds the floor amount back to the carryover only in a year a limit is exceeded
- Direction: form gives more
- Example: (a) AGI $2,000,000, no gifts this year, $50,000 carryover: form $50,000, statute $40,000. (b) AGI $2,000,000, cash gifts $1,500,000: form min($1,490,000, 60% limit) = $1,200,000, statute $1,200,000 - $10,000 = $1,190,000 (the $10,000 joins the carryover).
- Size and who: up to 0.5% of AGI of deduction in the year ($5,000 per $1,000,000 of AGI; $1,850 tax at 37%). Affects donors using a carryover in a year of small gifts, and donors over a percentage limit (for them a timing difference).
- Explained by: not known: the 2026 Schedule A instructions and 2026 Pub. 526 are not posted, so the worksheet text and the line 14 instruction could still cure it
- Published: not found (1 search)
- Confidence: low to medium: inferred from the face of the draft form and Pub. 505

### 4. State and Local Tax Deduction Worksheet (2025) lines 3b-3d, 4

- Form: State and Local Tax Deduction Worksheet (2025) lines 3b-3d, 4: modified AGI = AGI + Form 2555 line 45 + line 50 + Form 4563 line 15 + Puerto Rico exclusion
- Statute: 164(b)(7)(B)(iv): AGI "increased by any amount excluded from gross income under section 911, 931, or 933". Form 2555 line 45 is the exclusions less the deductions disallowed under 911(d)(6) (unlike 1411(d), nothing in 164 nets them); line 50 is the housing deduction of 911(c)(4), a deduction, not an exclusion
- Direction: form gives more (line 44 netting) / statute gives more (line 50 added)
- Example: Single, AGI $450,000, exclusions $130,000, $20,000 of deductions allocable to them, SALT $25,000: statute $16,000, form $22,000. Single, AGI $425,000, exclusions $130,000, housing deduction $15,000: statute $23,500, form $19,000.
- Size and who: 30% of Form 2555 line 44 (form more) or of line 50 (statute more), a few thousand dollars of deduction; only people abroad with modified AGI over $500,000 who still pay state and local tax
- Explained by: none; same convention as Schedule 8812 under the same words in 24(b)(1)
- Published: not searched
- Confidence: medium

### 5. Form 8995-A (2026 draft) lines 37-41

- Form: Form 8995-A (2026 draft) lines 37-41: line 39 = line 37 + line 38 (co-op deduction passed through under 199A(g)); line 41 = greater of line 39 or the $400 minimum
- Statute: 199A(i)(1): the minimum applies to "the deduction allowed under subsection (a)"; the patron's deduction is allowed separately by 199A(g)(2)(A) and limited by taxable income after the (a) deduction
- Direction: statute gives more
- Example: Co-op patron, active QBI $1,000 but subsection (a) deduction $0 (losses elsewhere), (g) deduction passed through $2,000, taxable income $60,000: statute $400 + $2,000 = $2,400; form greater of $2,000 or $400 = $2,000.
- Size and who: at most $400 of deduction (under $150 of tax); patrons of agricultural co-ops whose own deduction is under $400
- Explained by: none; 2026 instructions for Form 8995-A not posted
- Published: not searched
- Confidence: medium

### 6. Form 8960 (2026 draft instructions) Lines 9 and 10 Section 68 Limitation Worksheet line 9, Pub. 505 (2026) Worksheet 2-6 line 12, Form 1040-ES (2026)

- Form: Form 8960 (2026 draft instructions) Lines 9 and 10 Section 68 Limitation Worksheet line 9, Pub. 505 (2026) Worksheet 2-6 line 12, Form 1040-ES (2026): "Multiply by 5.4% (0.054)"
- Statute: 68(a): "reduced by 2/37" (5.4054...%)
- Direction: form gives more
- Example: Itemized deductions $1,000,000 well inside the 37% bracket: statute reduction $54,054, form $54,000. The Form 8960 example itself gives $8,378 on $155,000, which is 2/37; 0.054 gives $8,370.
- Size and who: $54 of deduction per $1,000,000 ($20 of tax); every itemizer in the 37% bracket if the Schedule A worksheet uses the same factor
- Explained by: rounding of the rate, not a stated rounding rule
- Published: not found (1 search); one adviser paper rounds the other way (5.41%)
- Confidence: high for Form 8960 and Pub. 505; the Schedule A worksheet itself is not posted

## Checked, no difference

- SALT worksheet 2025: reduce by 30% of excess, floor $10,000, then halve for separate filers (floor $5,000) = 164(b)(6)(B), (7)(B)
- Schedule A 2026 line 18 screen: AGI minus Form 1040 lines 13a, 13b against $384,350 = taxable income without 68 plus itemized deductions (68(a)(2)); 199A taxable income taken before 68 (Form 8995 line 11) = 199A(e)(1)
- Form 6251 2026 exemption: $90,100 / $140,200 / $70,100, phase-out 50% from $500,000 / $1,000,000 / $500,000 = 55(d)(4). Married-separate add-back at 50% over $640,200 matches the statute if "50 percent" replaces both "25 percent" in 55(d)(2); if only the first, the form adds up to $34,950 more AMTI (alternative reading, not counted)
- Form 8960 lines 12-17 and thresholds; Form 8959 Parts I-III (2025 and 2026 draft)
- Form 8995 2026: thresholds, $75,000 / $150,000 ranges, $400 minimum when active QBI from line 1 is at least $1,000, not capped by taxable income = 199A(i)
- 170(p): Form 1040 2026 line 12f exists; no dollar effect found from the 60% limit, which the statute keeps

## Not retrieved

- 2026 Instructions for Schedule A (the posted draft i1040sca is the 2025 one): Charitable Contribution Limitation Worksheet, Itemized Deductions Worksheet
- 2026 Pub. 526 (draft posted is 2025)
- 2026 Form 1040 instructions (line 12f, 170(p)); posted draft is 2025
- 2026 Instructions for Form 8995-A (posted draft is 2025)
- 2026 Instructions for Form 8959 (not requested)

## Notes

- Form 8960 worksheet line 1 says "taxable income reported on Form 1040, line 15, plus allowable itemized deductions". Line 15 is already after section 68; the statute starts from taxable income without section 68. The two agree only if "allowable" means the amount after the reduction. Matters only within the first dollars above the 37% bracket.
- The same worksheet applies section 68 to estates and trusts ($16,000). New section 68 says "in the case of an individual" and dropped the old exclusion for estates and trusts; 641(b) carries it over. Not a difference.
- 199A(c)(2) loss carryforward: Form 8995 tests the $1,000 on line 1 (this year's active businesses) before the carryforward on line 3. The statute does not say whether a carried loss belongs to an "active" business; treated as the same.
