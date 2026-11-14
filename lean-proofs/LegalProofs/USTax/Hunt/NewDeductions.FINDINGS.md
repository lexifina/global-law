# NewDeductions: findings

File: `LegalProofs/USTax/Hunt/NewDeductions.lean` (run: `lake env lean LegalProofs/USTax/Hunt/NewDeductions.lean`,
about 22 s). Full output: `tools/hunt/out/NewDeductions/run.txt`.

A married couple, two taxable years, both under the same law with 2026 figures (Rev. Proc. 2025-32 brackets and
standard deduction as I know them; statutory dollar amounts from the text; the §199A threshold is approximate).
Objective: total two-year federal income tax against the plain filing (joint return, everything in its own year,
the larger of standard or itemized each year). Self-employment tax and the 0.9% Additional Medicare Tax are printed
beside the result, not inside it.

## Provisions encoded (text read with `sec.py`)

| Provision | What is encoded |
|---|---|
| §224 | tips deduction; $25,000 per return, not doubled on a joint return (b)(1); $100 per full $1,000 of MAGI over $150k / $300k (b)(2); business tips only up to business net income (c), with half the SE tax counted as a business deduction (§164(f)(2)); married: joint return only (f) |
| §225 | overtime; $12,500 / $25,000 joint; same phase-out; married: joint only (e) |
| §163(h)(4) | car loan interest; $10,000 per taxpayer (C)(i); $200 per $1,000 or part over $100k / $200k joint (C)(ii); debt "incurred by the taxpayer"; no joint-return requirement |
| §151(d)(5)(C) | $6,000 per person 65+, each cut by 6% of MAGI over $150k joint; married: joint only (v) |
| §164(b)(6)–(7) | $40,400 cap, 30% phase-down over $505,000, $10,000 floor; separate return: two readings (see gap 1) |
| §170(b)(1)(I), (G), (p) | 0.5% floor for itemizers; 60% ceiling; $1,000 / $2,000 non-itemizer deduction with no floor |
| §68 | 2/37 cut of itemized deductions above the start of the 37% bracket |
| §63(b), (c), (e), (f) | standard deduction, zero on a separate return if the spouse itemizes (c)(6)(A); the list of deductions a non-itemizer keeps |
| §199A(a), (b)(3)(B), (e)(1), (i) | 20% of QBI, taxable-income limit, phase-out for a no-wage business, new $400 minimum |
| §165(d) | wagering losses: 90%, up to gains, itemized |
| §1(j), §164(f), §1401, §451/§461 timing | rates, half SE tax, cash-method timing |

Moves: tips earned in own trade or business (per spouse); which spouse takes the car loan; which spouse owns the
savings; receive part of a lump of income in year 2; pay a January tax instalment in December; move gifts between
years; which spouse pays the household's deductible items (per year); separate returns (per year); itemize (per
year, per return).

## Search size

19 positions (10 households, some with a second reading of the law), 164,448 states in all, exhaustive over every
allowed sequence. Reported per family of moves; a family is listed only if it beats every family using a subset of
its moves.

## Plans that beat the plain filing

| # | Plan (household) | 2-yr income tax saved | Provisions combined | Class | What could defeat it |
|---|---|---|---|---|---|
| 1 | Separate returns, equal earners $300k + $300k, each deducts SALT under the word-for-word reading of §164(b)(7)(B) | $11,024 ($11,495 with gifts bunched) | §164(b)(6)(B), (7)(B)(i), (iii); §6013 | CANDIDATE (a reading of the text, not a transaction) | The IRS worksheet takes the 30% off the halved cap; under that computation the gain is $0 from SALT. A taxpayer would be filing against the form instructions; a technical correction is likely. No source found that states the word-for-word reading. |
| 2 | Separate returns, $350k + $250k, the spouse under $252,500 pays the property tax, instalment, mortgage and gifts | $7,464 (IRS computation); $5,752 without changing who pays | §164(b)(6)–(7), §63(c)(6), §1(d) | VARIANT | Payment must come from that spouse's own funds and that spouse must be liable for the tax (owner of the home); State return may have to follow the federal status; loss of Roth IRA contribution room and other separate-filer limits not modelled. Disappears at $400k + $200k (bracket cost exceeds the gain). Mechanics are in published IRS-style examples; sources found say separate filing "usually hurts", none sets out this plan. |
| 3 | Separate returns so that one spouse alone gives: the 0.5% floor is measured on that spouse's AGI only ($300k + $300k, $8,000 a year) | $1,052; $2,381 with gifts bunched into the separate year | §170(b)(1)(I), (H); §6013 | CANDIDATE (small) | Same funds/ownership point as plan 2; anything else lost by filing separately. No source found describing it; searches returned only the rule that each separate filer uses their own AGI. |
| 4 | Separate returns with the car loan in the name of the spouse under $100k ($165k + $95k; joint MAGI is past the joint phase-out) | $2,648, less $540 more Additional Medicare Tax | §163(h)(4)(B)(i), (C); absence of a joint-return rule that §§224(f), 225(e), 151(d)(5)(C)(v) all have | VARIANT | Prop. Reg. §1.163-16 (final rules reported effective 9 Nov 2026, not read): sources agree on $10,000 per separate return; one source says separate filers do not qualify at all. Borrower must be the spouse who pays. |
| 5 | Same, plus the under-$100k spouse does not own the savings / the gambling spouse's gross winnings stay off that return ($90k + $90k, $80k won and lost) | $3,278 (position 9) | §163(h)(4)(C)(ii), §165(d), §61 | VARIANT | As plan 4. A CPA article already suggests separate filing for a gambler's spouse (for IRMAA). |
| 6 | Alternate years: itemize one year with two years of gifts, standard deduction plus the $2,000 no-floor gift the other | $1,280–$2,135 | §170(p), §170(b)(1)(I), §63 | KNOWN (bunching), in its 2026 form | Nothing; needs the gifts to be movable. |
| 7 | Split a retirement withdrawal evenly over two years (both 65+) | $2,858 | §151(d)(5)(C)(iii), §1 | KNOWN (income smoothing around the senior deduction phase-out) | Nothing. |
| 8 | Tipped worker treats tips as own business: tips deducted under §224 and the remainder gets §199A | $648–$2,608 income tax, but $3,886–$6,738 more SE tax | §224(c), §199A, §164(f) | Not a plan: loses money once §1401 is counted | Worker status is a matter of fact, not election. |

## Traps found

- §224(b)(1): the $25,000 tips cap is per return and not doubled for a joint return (§225 is doubled). Two tipped
  spouses with $52,000 of tips deduct $25,000, and §224(f) bars separate returns.
- §165(d): a break-even gambler has 10% of losses as taxable income, the gross winnings raise MAGI for every
  phase-out (car loan, senior, tips, overtime, SALT), and the loss is only available by itemizing.
- §63(c)(6)(A) with §63(b): on separate returns, if one spouse itemizes the other's standard deduction is zero, but
  that spouse may still decline to itemize and keep the §63(b) deductions (car loan, §170(p), §199A).
- Car loan interest: on a joint return the deduction is gone at $250,000 MAGI ($10,000 of interest); a bonus of
  $1 over a $1,000 step costs $200 of deduction ("or portion thereof").
- Senior deduction: each $6,000 is cut separately, so a two-senior couple loses 12 cents of deduction per dollar.
- §68 does not reach the §63(b) deductions; nothing in the search turned that into a saving.

## Drafting gaps noticed

1. §164(b)(7)(B) and separate returns: (i) reduces "the applicable limitation amount" by 30% of MAGI over half the
   threshold, (iii) floors it at $10,000, and (6)(B) then gives a separate filer half of it. Read in that order the
   phase-down runs at half speed for separate filers ($300k MAGI: $13,075, against $5,950 on the IRS worksheet).
2. §163(h)(4) has no married-must-file-jointly rule and no separate-return threshold; the three sibling provisions
   have the rule.
3. §170(p) says "$1,000 ($2,000 in the case of a joint return)": nothing for a separate filer whose spouse itemizes.
4. §199A(c)(3) does not say whether the §224 deduction for business tips is a deduction of the business. The model
   runs both readings (difference $1,200 in position 2); not checked against guidance.
5. §199A(i): the $400 minimum is per taxpayer, so one per joint return; it overrides the taxable-income limit.

## Sources checked (6 searches, standard mode)

SALT separate-filer cap and phase-down (two searches: secondary sources and tax-software worksheets all use
$20,000 less 30% of the excess, floor $5,000); car loan interest on separate returns (per-return $10,000 reported
from the proposed regulations; threshold for separate filers reported inconsistently); gambling and separate filing
(monacocpa.cpa article on married couples); 0.5% floor on separate returns (no source on the one-spouse-gives
point); separate filing as a SALT plan (not found as a published plan). No IRS primary source was retrieved.

## Not modelled

Children and credits, capital gains, AMT, NIIT, Social Security benefit taxation, IRA/Roth limits for separate
filers, State tax, community property, carryovers. Any of these can outweigh plans 2–5 for a given household.
