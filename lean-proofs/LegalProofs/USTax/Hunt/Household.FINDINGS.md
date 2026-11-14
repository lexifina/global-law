# Household: findings

File: `LegalProofs/USTax/Hunt/Household.lean` (run: `lake env lean LegalProofs/USTax/Hunt/Household.lean`, about 65 s).
Last output: `tools/hunt/out/Household/run3.txt`.

Bottom line: one CANDIDATE (the refundable adoption amount for two unmarried adopters), four VARIANTs of known
planning under 2025/2026 law, the rest KNOWN. Nothing else novel turned up.

## Provisions encoded

Rules are for 2026 (Pub. L. 119-21 amendments in force); indexed dollar figures are the 2025 ones, except the §36B
percentage table (2026, Rev. Proc. 2025-25) and the poverty line (2025 guideline, which §36B(d)(3)(B) applies to 2026
coverage).

| Provision | What is encoded |
|---|---|
| §1(a)-(d), §63(c)(2),(7) | rate tables and standard deduction by status |
| §2(b)(1)(A),(B), (b)(3)(B), §2(c), §7703(a),(b) | head of household through a child, a dependent, or a parent in a separate home; not through a §152(d)(2)(H) dependent; married person living apart with a child treated as unmarried |
| §6013(a) | joint or separate return |
| §152(c)(1),(4), (d)(1),(2)(C),(G),(H), (e)(1)-(2) | either parent may claim a child both live with; elder as qualifying relative of the child, the in-law, or an unrelated household member; release by the custodial parent |
| §24(a),(b),(d),(h)(2)-(6) | $2,200 / $500, phaseout, refundable part (15% of earned income over $2,500, $1,700 cap, three-child alternative) |
| §32(a),(b),(c)(1)(A),(c)(3),(d),(i) | table, childless age rule, qualifying child without regard to §152(e), joint-return rule and separated-spouse rule, investment income limit |
| §21(a)(2),(b)(1)(A),(c),(d),(e)(2),(e)(5) as amended | 50/35/20% schedule, dollar limit less §129 exclusion, earned income limit, custodial parent rule |
| §129(a)(2),(b),(e)(2) as amended | $7,500 ($3,750 married separate), earned income limit |
| §25A(b),(d),(g)(3),(g)(6),(i) | American Opportunity credit, who may take it, phaseout, 40% refundable |
| §25B(a)-(d) | saver's credit tiers by status, $2,000 per person |
| §36B(b)(2),(b)(3)(A),(c)(1)(A),(C), (d)(1),(2) | 100%-400% band, family size = §151 deductions, joint-return rule |
| §23(a),(b)(1),(b)(2),(a)(4),(f)(1) | limit, phaseout, $5,000 refundable, joint-return rule |
| §1(g)(1),(4),(5), §63(c)(5) | child's own return, parental rate, limited standard deduction |
| §151(d)(5)(C), §224, §225 | senior deduction, tips, overtime, with their joint-return requirements |
| §402(g), §219, §408A (limits only) | deferral lowers wages and earned income; IRA lowers AGI only; Roth lowers neither |

Not encoded: §6433 (starts 2027), Lifetime Learning credit, §23 carryforward, itemizing, payroll tax as part of the
objective, Medicaid/CHIP, state tax.

## Search size

Eight households (H1-H8), each as unmarried and as married: 16 searches, 39,706 lawful plans in all (largest 10,528,
depth up to 12 single-choice changes from the default). Cliff scan: A's wages $0-$200,000 in $1 resolution on five
households. Plans are grouped by which kinds of choice they use; a family is listed only if it beats every family
using a subset of its choices.

## Plans

Dollar effect is household income tax net of credits against the default filing, one year. "Pre-tax" plans defer tax
rather than remove it, so the best plan without retirement saving is reported separately.

| # | Household | Moves | Effect | Provisions combined | Class | What could defeat it |
|---|---|---|---|---|---|---|
| 1 | H6 unmarried, joint adoption, $20,000 expenses, wages 38k/34k | each adult pays half the expenses | +$6,951 (alone); +$7,990 with the child and home moved to B | §23(a)(4) $5,000 refundable is per taxpayer; §23(b)(1) limit shared | **CANDIDATE** | see below |
| 2 | H8 unmarried, B at $80,000 (above 400% for one), A's parent lives with them | B, not A, supports and claims A's parent | +$5,232 for B (the rest of the $18,087 printed is plan 3's trap undone) | §152(d)(2)(H) + §36B(d)(1): family size 2 moves B's 400% line from $62,600 to $84,600 | VARIANT | B must really provide over half of the parent's support all year; parent must live there all year; §152(f)(3) local law; parent's gross income under the exemption amount. No anti-abuse rule in §36B for family size. Household-size planning is published; the unrelated-partner route is not something I found written up |
| 3 | H3 unmarried, both tipped, A pays for parent's separate home | child claimed by B and B keeps up the shared home; A stays head of household through the parent | +$1,633 | §2(b)(1)(B) for A, §2(b)(1)(A) for B, §224 $25,000 per return | VARIANT | Each needs to furnish over half the cost of a different household; IRS will ask for proof. Each rule is in Pub. 501; two heads of household in one couple is the combination |
| 4 | H3/H1/H2/H7 married vs unmarried | not marrying | $318 to $9,326 a year across H1-H7; in H8 marrying saves $529 | §224(b)(1) cap not doubled on a joint return; §32, §36B, §23(a)(4), §129 per return | VARIANT (tips, adoption: 2025 law) / KNOWN (the rest) | none: status at year end, §7703(a) |
| 5 | H4 married, living apart | spouse with the children files as head of household and keeps §§21, 32, 36B, 224, 225, 151(d)(5)(C) on a separate return | in default | §7703(b) switches off every "joint return if married" rule in the 2025 provisions for that spouse only | VARIANT | the other spouse gets none of them |
| 6 | H1, H2, H7 unmarried | lower earner claims one or all children | +$2,487 to +$5,574 | §152(c)(4), §32 | KNOWN (unmarried parents choosing the claimant) | parents must both live with the child; only one may use each child |
| 7 | H5 unmarried | parent under $80,000 claims the student | +$2,500 | §25A(d), §152(c)(4) | KNOWN | - |
| 8 | H1, H4 | dependent-care exclusion, one per unmarried parent for own child | +$84 to +$2,189 | §129(a)(2), §21(c) | KNOWN | - |
| 9 | all | pre-tax saving sized to an income line (saver's tier, EIC range, 400% line) | +$900 to +$11,375 | §§25B, 32, 36B, 24 on AGI | KNOWN (AGI management) | deferral, not removal, of the income tax part |
| 10 | H4 unmarried | custodial parent releases both children | +$318 on top of plan 9; worse alone | §152(e), §36B(d)(1), §24 | KNOWN (Form 8332) | - |

### Plan 1, attacked

Text: §23(a)(4) says "so much of the credit allowed under paragraph (1) as does not exceed $5,000" is refundable. The
unit is the taxpayer's credit for the year. Two unmarried people who adopt the same child are two taxpayers. The
$17,280 limit is shared between them (Notice 97-9; 2025 Form 8839 instructions: "must be divided between the two of
you"), and the model keeps that. Nothing found divides the $5,000. The 2025 Form 8839 instructions say the refundable
amount "is determined per eligible child" on each filer's form, with no instruction to split it with another filer.
So the form as published gives each of two co-adopters up to $5,000 for one child; a married couple gets $5,000.

What could defeat it:
- IRS guidance extending the Notice 97-9 division to the refundable amount (it would have to read "per child, across
  taxpayers" into (a)(4); the text does not say that).
- The gain is partly timing. The nonrefundable part carries forward five years (§23(c)), which the model counts as
  lost. The permanent gain is the second $5,000 only for households whose carryforward would expire unused, which is
  the low-tax household the refundable part was written for (here both adults' tax is absorbed by §24 first).
- Both must be adoptive parents and each must actually pay expenses; not available where state law does not allow
  joint or second-parent adoption by unmarried people.
- §7701(o) does not reach a choice of who pays a real expense.

Sources checked (5 searches): IRS adoption credit page, 2025 Instructions for Form 8839, NATP and other summaries.
None discusses two unmarried adopters and the refundable amount.

## Traps found

- **Claiming a dependent can cost the whole premium credit.** H8 default: A ($20,000) claims the parent, family size
  2, poverty line $21,150, income below 100%, credit zero (§36B(c)(1)(A)); $12,780 lost. Real only where the adult
  is not Medicaid-eligible (non-expansion States).
- **Marriage with two tipped workers**: joint cap $25,000 for both (§224(b)(1)); H3 taxable income 35,500 joint
  against 5,750 on two returns.
- **Married filing separately** loses §§21, 23, 25A, 32, 36B, 151(d)(5)(C), 224, 225 at once; no separate-return plan
  beat the joint return in any household living together.
- **Elective deferral and §129 exclusion lower earned income**, an IRA deduction does not: in the EIC phase-in and the
  §24(d) 15% range a deferral loses credit that the IRA keeps (the search picks IRA/Roth for the low earner in H1, H6).

## Cliffs ($1 more of A's wages costs more than $1, default filing)

| Where | Cost | Provision |
|---|---|---|
| H2 married, household income $150,601 (400% for five) | $9,901 | §36B(c)(1)(A) |
| H4, A single at $62,601 | $366 | §36B(c)(1)(A) |
| H2 married, household income 133% of poverty | $521 | §36B(b)(3)(A) table: 2.10% below 133%, 3.14% at it |
| H1 married with $2,000 Roth each, AGI $79,001 | $400 | §25B(b)(1)(D) |
| H1 married, every $4,000 of AGI from $150,001 | $60 | §21(a)(2)(B), 1 point on $6,000 |
| H2 married, same | $30 | §21(a)(2)(B) on $3,000 |
| H3, every $1,000 of AGI over $150,000 | $25 | §224(b)(2), $100 of deduction |

The $7-$12 §36B points in the output are rounding in the model's percentage interpolation, and the H3 point at
$46,000 is the default switching which adult claims the child; neither is a statutory cliff.

## Drafting gaps noticed (not from the search unless said)

1. §23(a)(4): the $5,000 is per taxpayer-year in the text, per child in the IRS form. On the text one return adopting
   two children gets $5,000; two unmarried adopters of one child get $10,000 (plan 1).
2. §21(a)(2)(A): the 50% rate applies at AGI up to $15,000, but the credit is nonrefundable and the smallest standard
   deduction is $15,750, so no non-itemizing filer can use the 50% rate. First usable rate: 49% single, 45% head of
   household, 41% joint. (Arithmetic from the figures in the file.)
3. §224(b)(1) has no joint-return doubling while §225(b)(1) has; §224(f) then forces married tipped workers onto the
   one return.
4. §152(c)(4)(B) only resolves two parents who both claim; it does not say who may claim when they agree, so for
   parents living together the claimant is a free choice for §§2(b), 21, 24, 32, 36B together.
5. §1(g)(5)(A) names "the custodial parent" for unmarried parents and has no rule for unmarried parents who live
   together; the model uses the greater taxable income.
6. §36B(d)(1) counts every §151 dependent in family size, including one who cannot enroll (Medicare) and one related
   only through §152(d)(2)(H); each adds $22,000 to the 400% line (plan 2).
