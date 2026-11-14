# Blind replication: Household (adoption credit, two adults, one child)

Run: `lake env lean LegalProofs/USTax/Hunt/Audit/Household/Blind.lean` (output saved in `run.out`).

## Position

A (wages $38,000) and B (wages $34,000) live together and jointly adopt one child (not special needs). $20,000 of
qualified adoption expenses, all paid in the year the adoption becomes final. Run married and unmarried.

## Provisions encoded

| Provision | What was encoded |
|---|---|
| §23(a)(1) | Credit = qualified adoption expenses "paid or incurred by the taxpayer": each person's credit follows what that person paid. |
| §23(a)(2)(B) | Expenses paid in the year the adoption becomes final are allowed that year. (a)(2)(A) is not reached. |
| §23(a)(3) | Not reached (not special needs). |
| §23(a)(4) | "So much of the credit allowed under paragraph (1) as does not exceed $5,000" is a subpart C (refundable) credit: the first $5,000 of each taxpayer's credit is cash. |
| §23(b)(1) | $17,280 (2025) cap on expenses "with respect to the adoption of a child by the taxpayer": applied per taxpayer. |
| §23(b)(2) | Phase-out by AGI: encoded as not reached (AGI $38,000 / $34,000 / $72,000). |
| §23(b)(3) | No other deduction, credit or grant in the position; no effect. |
| §23(c) | Nonrefundable part over the §26(a) limit is carried forward; reported separately, not as cash. Five-year limit not modelled (one year only). |
| §23(d) | Expenses taken as qualified; child eligible; (d)(1)(C) (spouse's child) does not apply. |
| §23(e), (g), (h) | Foreign adoption, basis: not reached. (h): indexed limit given; (h)(3) indexes the $5,000 only for years after 2025, so $5,000 as in the text. |
| §23(f)(1) + §21(e)(2)–(4) | Married at year end: credit "only if" a joint return. (e)(3) and (e)(4) need separation or a spouse absent from the household for the last six months; the two live together, so neither applies. |
| §23(f)(2) | TIN assumed included. |
| §23(i) | Authorises regulations treating unmarried co-adopters as one taxpayer for the amounts in (a)(3), (b)(1) and §137(b)(1). It is a grant of power, not a rule. Encoded as a separate variant. |
| §137(a),(b) | Read. No employer program in the position; no move. |
| §7703 | Married status tested at year end; (b) cannot apply (spouse is a member of the household). |
| §6013(a) | A married couple "may" file jointly; unmarried people cannot. |
| §26(a) | Nonrefundable credits limited to regular tax liability (no §27, no §55 in the position). |
| §1(j), §63 | 2025 brackets and the given standard deductions; tax computed from the rate schedule, not tax tables. |

## Moves

1. `split k`: A pays $k thousand, B pays the rest (k = 0..20).
2. `claim`: who claims the child as a dependent (A, B, nobody).
3. Filing: married: `fileJoint` or `fileSeparate`. Unmarried: each `single`, or `hoh` for the one who claims the child.
4. Shared-limit variant only: `alloc`, the division of the one $17,280 between A and B ($1,000 steps and the full amount).

## Search size

Exhaustive. 126 (married) + 105 (unmarried, text only) + 1,995 (unmarried, shared-limit variant) = 2,226 distinct
terminal positions.

## Results

Objective: combined income tax, less nonrefundable credit used, less refundable credit. Negative = net cash received.

### Married

| Plan | Net | Carryforward |
|---|---|---|
| Joint return, any split (baseline and best) | -$5,000.00 | $7,897.00 |
| Separate returns | +$4,383.00 | $0 |

Tax before credit on the joint return is $4,383. Nothing beats the baseline: on a joint return the split and the
dependent claim change nothing.

### Unmarried, statute text only

| Plan | Net | Carryforward |
|---|---|---|
| Baseline: A pays all, B claims child and files head of household | -$3,962.50 | $9,848.50 |
| Baseline without head of household (both single) | -$3,048.50 | $9,848.50 |
| **Best: A pays $7k–$13k, B the rest; A claims child and files head of household, B single** | **-$10,000.00** | **$6,611.00** |
| Runner-up: same split band ($8k–$13k), B claims child and files head of household | -$10,000.00 | $6,531.00 |
| Runner-up: both single, A pays $8k–$13k | -$10,000.00 | $5,617.00 |
| Edge: A pays $14k, B head of household | -$9,962.50 | $6,568.50 |

Gain over the baseline: **$6,037.50** in cash ($6,951.50 against the both-single baseline), with $3,237.50 less
carryforward. Each person who pays at least $5,000 gets a separate $5,000 refundable amount; each person's remaining
credit wipes out that person's tax. Outside the $7k–$13k band one person's credit is too small to cover their tax or
their $5,000.

Against the married couple: the unmarried pair is $5,000 better off in cash.

### Unmarried, variant: one $17,280 shared under a §23(i) regulation

Same best plan, net -$10,000.00, carryforward $3,891.00 (e.g. A pays $9k, limit divided $9,000 / $8,280). The gain
of $6,037.50 survives, because §23(i) names (a)(3) and (b)(1) but not the (a)(4) refundable amount.

## Judgment calls

1. Unmarried co-adopters are two taxpayers under the statute's words, each with a $17,280 cap and a $5,000
   refundable amount. §23(i) only empowers regulations; any such regulation is outside the text given. Shown as a variant.
2. In the variant the shared amount is divisible freely between the two (the text gives no division rule).
3. A married couple on a joint return is one "taxpayer": one cap, one $5,000.
4. Head of household is open to the unmarried adult who claims the child (never both). §2(b) and §152 were not in
   the reading list; it is assumed the claimant furnishes over half the household cost and the child meets the
   residence test in the adoption year.
5. The baseline is the best one-payer position (other moves optimised), so the gain isolates the split.
6. The refundable $5,000 is taken first out of the credit, before the §26(a) limit, as (a)(4) is worded.
7. Tax from the rate schedule to the cent; no tax-table rounding.

## Silences

- §23 does not say how co-adopters who are not spouses share the (b)(1) amount or the (a)(4) amount; (i) leaves it
  to regulations and does not mention (a)(4).
- §23 does not require the child to be the taxpayer's dependent, so the dependent claim matters only through filing status.
- Nothing in the listed text says whether money given by one adult to the other to pay expenses is "paid by" the giver
  or the payer; the split is taken as who actually pays.
- §23(c) does not say whether the refundable part reduces the carryforward base beyond the words "the portion ...
  allowed under this subpart"; read as written (refundable part excluded from the carryforward).
- §26 ordering among other credits: none in the position.
