# Blind replication: Accounts

Encoding: `Blind.lean` (run: `lake env lean LegalProofs/USTax/Hunt/Audit/Accounts/Blind.lean`, about 13 s).

## Position
Tax year 2040, single, age 30, active participant (plan takes no roll-ins), MAGI $250,000, cash $100,000,
traditional IRA $100,000 (basis 0), section 530A account $20,000 (investment in the contract $12,000). No growth.
Objective: Roth IRA balance at year end minus income included in gross income by the moves.

## Provisions encoded
- 530A(a): the account is treated as a 408(a) IRA except as 530A provides.
- 530A(b)(1)(C), (c)(1)-(3), (d)(1), (h)(1), (h)(3): every restriction there is worded "before the calendar year in
  which the beneficiary attains age 18". At 30 none binds: distributions allowed, 408(d) applies, contributions count
  against the ordinary IRA limit, 219 not denied by 530A.
- 530A(d)(2): investment in the contract excludes general, 6434 and 128 contributions (taken as already reflected
  in the $12,000 given).
- 530A(h)(4): 408(d)(2) applied separately to 530A accounts and to other individual retirement plans. No age limit
  in the words. Encoded as two separate section 72 pools.
- 530A(e): "qualified rollover contribution" (whole balance, 530A to 530A). Not a move here: one account only.
- 408(d)(1), (d)(2)(A)-(C), 72(e)(2)(B), (e)(5)(D)(iii), (e)(8)(A)-(B): per pool, excluded share =
  basis / (year-end value + distributions in the year); all distributions in the year are one distribution.
- 408(d)(3)(A)(i), (B), (D): 60-day rollover between IRAs, partial allowed, one per 1-year period.
  (d)(3)(A)(ii)/(H) (roll to an employer plan, income first) is unavailable: the plan takes no roll-ins.
- 219(a), (b)(1), (b)(5), (g)(1)-(3): deduction limit $7,000, phased out $79,000-$89,000; at $250,000 it is $0.
- 408(o)(1)-(2): nondeductible limit = $7,000 - $0 = $7,000.
- 408A(c)(2), (c)(3): Roth contribution limit phased out $150,000-$165,000; at $250,000 it is $0. Conversion
  income is ignored for this test ((c)(3)(B)(i)). (c)(5)(B)(i): conversions do not count against the limit.
- 408A(d)(3)(A)(i), (C): conversion of an individual retirement plan other than a Roth IRA; include what would be
  includible if it were not rolled over.

## Judgment calls
1. A 530A account can take an ordinary nondeductible contribution after the year the beneficiary turns 18. Read
   from 530A(a) plus the fact that (b)(1)(C)(i), (c) and (h)(3) only speak to earlier years.
2. A 530A account can be converted to a Roth IRA under 408A(d)(3)(C): it is an IRA "not designated as a Roth IRA"
   (530A(b)(1)), so it is an individual retirement plan other than a Roth IRA. 408A(e) was not on the reading list.
3. 530A(h)(4) separation continues after age 18 and applies to conversion income (408A(d)(3)(A)(i) asks what would
   be includible under 408(d)(1)-(2)).
4. A rollover between the two pools carries basis pro rata (72(e)(8)(B) ratio at the time of the rollover).
5. Compensation is at least $7,000 (MAGI $250,000); the taxpayer had no IRA rollover in the preceding 12 months.
6. Conversions are not counted under the 408(d)(3)(B) one-per-year rule.
7. Contributions above the limit are not modelled as moves (408(o)(2)(A) "shall not exceed"; 4973 not read).
8. Whole dollars, excluded amounts rounded down.

## Silences
- 530A says nothing on contributions to the account after age 18 (no bar, no express permission).
- 530A says nothing on whether the account keeps separate (h)(4) treatment once ordinary contributions go in.
- 408(d)(3) does not say which part of a partial IRA-to-IRA rollover is basis ((H) covers employer plans only).
- 408(d)(2) does not say how its year-end computation treats a rollover between two separately-applied pools.
- Nothing read says whether a 530A account must be converted whole or may be converted in part.

## Search
Breadth-first, depth 4, 9 move kinds, amounts {1000, 7000, 8000, 12000, 19000, 20000, 27000, 100000, 107000, whole
balance}. With the 530A account: 97,750 positions, 64,947 distinct (Roth, income) outcomes. Baseline (b): 2,754
positions.

## Result (value = Roth - included income)
- Baseline (a), do nothing: Roth $0, income $0, value $0.
- Baseline (b), no 530A account: best value $7,000: contribute $7,000 nondeductible, convert all $107,000
  (Roth $107,000, income $100,000). Converting only $7,000 gives Roth $7,000, income $6,542, value $458.
- Best with the 530A account: value $19,000. Lowest-income plan: contribute $7,000 nondeductible to the 530A
  account, convert the whole account: Roth $27,000, income $8,000. The pre-tax IRA is left alone and does not
  dilute the basis because of 530A(h)(4).
- Tied at $19,000 (every dollar of pre-tax IRA converted adds $1 of Roth and $1 of income): up to Roth $127,000,
  income $108,000 (contribute $7,000 to either account, convert both in full).
- Gain: $19,000 over (a); $12,000 over (b). At equal value the plan needs $8,000 of income where (b) needs $100,000.
- The $19,000 ceiling is total basis ($12,000 + $7,000). No sequence created basis or made income disappear.

## Runner-up families
- Convert the 530A account without contributing: Roth $20,000, income $8,000, value $12,000.
- Any rollover between the pools before converting: value $18,835-$18,994 (basis stranded or diluted).
- Cash distributions: lower value (income with no Roth).
- Direct Roth contribution: not available (limit $0).
