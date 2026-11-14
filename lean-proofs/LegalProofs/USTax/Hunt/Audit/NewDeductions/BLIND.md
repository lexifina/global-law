# Blind replication: NewDeductions

Run: `lake env lean LegalProofs/USTax/Hunt/Audit/NewDeductions/Blind.lean` (from `lean-proofs/`). Money in cents.

## Provisions encoded
- §164(a)(1),(3): State and local real property and income taxes deductible when paid. Each spouse's $25,000.
- §164(b)(5): sales-tax election read; not a move here (the position has no sales tax figure).
- §164(b)(6)(B): aggregate taxes "shall not exceed the applicable limitation amount (half the applicable
  limitation amount in the case of a married individual filing a separate return)".
- §164(b)(7)(A)(ii): applicable limitation amount for 2026 = $40,400.
- §164(b)(7)(B)(i): that amount "shall be reduced by 30 percent of the excess (if any)" of MAGI over the threshold
  "(half the threshold amount in the case of a married individual filing a separate return)"; (ii)(II) threshold
  2026 = $505,000; (iii) reduction "shall not result in the applicable limitation amount being less than $10,000";
  (iv) MAGI = AGI here (no §911/931/933 amounts).
- §63(a),(b)(1),(e)(1): itemize by election, otherwise AGI minus standard deduction.
- §63(c)(6)(A): separate filer's standard deduction is zero where either spouse itemizes.
- §63(c)(2),(7): standard deduction 2026 as given: $32,200 joint, $16,100 separate.
- §6013(a): spouses "may" file one joint return; separate returns otherwise.
- §1(j)(2)(A),(D),(3)(B): 2026 tables. Joint: 10% to 24,800; 12% to 100,800; 22% to 211,400; 24% to 403,550;
  32% to 512,450; 35% to 768,700; 37% above. Separate: 12,400; 50,400; 105,700; 201,775; 256,225; 384,350.

## The cap function (written before the search)
Three named readings of (6)(B) + (7):

| Reading | joint @ $600,000 | separate @ $300,000 | separate @ $260,000 | separate @ $400,000 |
|---|---|---|---|---|
| R1 `textOrder`: half of max(40,400 − 30%·(MAGI − 252,500), 10,000) | $11,900 | $13,075 | $19,075 | $5,000 |
| R2 `halveFirstHalfFloor`: max(20,200 − 30%·excess, 5,000) | $11,900 | $5,950 | $17,950 | $5,000 |
| R3 `halveFirstFullFloor`: max(20,200 − 30%·excess, 10,000) | $11,900 | $10,000 | $17,950 | $10,000 |

**Which the words support best: R1.** Paragraph (7) defines one "applicable limitation amount" ($40,400), and
(7)(B)(i) and (iii) operate on that defined amount: it is reduced, and it may not fall below $10,000. The only
separate-return adjustment in (7) is to the *threshold*. The halving sits in (6)(B) and is expressed as "half
the applicable limitation amount", i.e. half of the amount (7) produces after its own reduction and floor. Nothing
in (7) says the $40,400 or the $10,000 is halved before the reduction. R2 needs the reader to halve the $40,400
before (7)(B) and also halve the $10,000 floor, neither of which the text states; R3 halves early but keeps the
written floor. R2 is the reading under which separate returns give exactly half the joint result at every income
(the symmetric rule, and from memory, unverified here, the way the limit is administered on forms), so it is a
real competing reading, not a straw man.

## Search
State = (filing status, itemize flags). Moves: `fileJoint`, `fileSeparate` (§6013(a)); `itemizeJoint`, `itemizeA`,
`itemizeB` (§63(e)). BFS, deduped with `Std.HashSet`: 7 positions, 6 terminal, per reading (run three times).

Baseline (joint return): standard $136,268.50; itemized (SALT $11,900 + interest $24,000 = $35,900) $134,973.50.
Baseline taken as the better joint return: **$134,973.50**.

| Plan | R1 | R2 | R3 |
|---|---|---|---|
| Separate, both itemize | **$129,986.00** (gain $4,987.50) | $134,973.50 (gain $0) | $132,138.50 (gain $2,835.00) |
| Joint, itemize | $134,973.50 | $134,973.50 | $134,973.50 |
| Joint, standard / Separate, both standard | $136,268.50 | $136,268.50 | $136,268.50 |
| Separate, one itemizes | $138,762.25 | $141,256.00 | $139,838.50 |

Mechanism under R1: each separate return may take $13,075 of SALT (total $26,150) against $11,900 on the joint
return; $14,250 more deduction at 35% = $4,987.50. The 2026 separate brackets are exactly half the joint ones in
this range, so the whole gain is the cap. Against the joint-standard return the gain would be $6,282.50.

## Judgment calls
1. Order of operations in §164(b)(6)(B)/(7): three readings run; R1 best supported by the words; the result is
   reading-dependent (gain $4,987.50 / $0 / $2,835).
2. Baseline "joint return" taken as the better of joint-standard and joint-itemized.
3. Mortgage interest treated as fully deductible to the spouse who paid it (§163 not in the list).
4. Each spouse deducts only the tax that spouse paid; wages are each spouse's own income (no community property).
5. 2026 bracket and standard deduction figures taken as supplied/known, not derived from §1(f).
6. §164(b)(6) heading says "2018 through 2025" but the operative words say "beginning after December 31, 2017"
   and (7)(A)(ii) gives a 2026 figure; applied to 2026.

## Silences
- (7) does not say whether the $40,400 and the $10,000 floor are halved for a separate return; only the threshold is.
- (7)(B) "the taxpayer's modified adjusted gross income" on a separate return: text does not say to combine spouses'
  income; each spouse's own MAGI used.
- §164 does not say which spouse may deduct tax on jointly owned property or jointly assessed tax; the position says
  each paid from own funds.
- §68 (overall limit on itemized deductions) and AMT are outside the list and not encoded; taxable income here is
  below the 37% bracket on every return.
- §63(e)(3) (changing the election later, spouse consistency) not modelled as a move.
