# RED: NewDeductions, plan 1 (separate returns, $300k + $300k, SALT under the word-for-word reading)

Claimed: $11,024 of income tax saved over two years. Verdict: **holds on the text**, and the Findings file is wrong
about the authority: the IRS worksheet uses the word-for-word computation, not the halve-first one.

Files here: `red_gen.py` builds each `Red*.lean` from `Orig.copy.lean` (the original, unedited) plus a `.tail`;
`red_t7.py`; `red_web/` (text of the 2025 Schedule A instructions as retrieved). Every Lean file was run with
`lake env lean`; longest run 2 min 6 s (RedT6).

## T1 Text fidelity: partial

The words. (7)(A) defines "applicable limitation amount" (ALA) as one number, $40,400 for 2026. (7)(B)(i): "the
applicable limitation amount shall be reduced by 30 percent of the excess (if any) of the taxpayer's modified adjusted
gross income over the threshold amount (half the threshold amount in the case of a married individual filing a
separate return)". (7)(B)(iii): the reduction "shall not result in the applicable limitation amount being less than
$10,000". (6)(B): taxes "shall not exceed the applicable limitation amount (half the applicable limitation amount in
the case of a married individual filing a separate return)".

- The thing reduced in (i) and floored in (iii) is the ALA, the defined term. Nothing in (7) halves the ALA; the only
  halving of it is in (6)(B), which takes half of "the applicable limitation amount", that is, of whatever (7)
  produces. The grammar supports one order: reduce, floor, then halve. Separate filer: half of max(10,000, 40,400 −
  0.3 × (MAGI − 252,500)) = $13,075 at $300,000.
- The two parentheticals do different jobs and do not conflict: (i) halves the *threshold* (where the reduction
  starts), (6)(B) halves the *result*. Neither halves the 30% reduction, so per separate return the phase-down runs at
  15 cents per dollar.
- The halve-first computation needs "applicable limitation amount" in (7)(B)(i) to mean "half the applicable
  limitation amount", which the wording of (6)(B) rules out. If one forces it anyway, the floor in clause (iii) is
  still $10,000 as written (nothing halves it once (6)(B) has been spent): limit max(10,000, 20,200 − 14,250) =
  $10,000, and the plan still saves **$6,720** (RedT1b). The model's "IRS" branch ($20,200 − 30%, floor $5,000 →
  $5,950) matches no ordering of the words: it uses the (6)(B) halving twice (once on the cap before the reduction,
  once on the floor).

Divergences found (encoding against text):

1. `saltLiteral` is a switch set by the author, and positions 7L/7bL exist only to turn it on. The search did not
   find the reading; it found only that, given the reading, separate returns win. The claim rests on the parse above,
   not on the search.
2. The default branch is labelled "the IRS worksheet". It is not (see T8). The default is *less* generous than both
   the text and the IRS, so every default-branch figure with a separate filer over $252,500 is understated (plan 2:
   $7,464 printed, $7,866 on the worksheet computation; positions 1, 5, 6, 10 likewise).
3. The household's property tax, instalment, mortgage interest and gifts all go to spouse A. Paid from joint funds
   they are each spouse's as to half. Fixed in RedT1: the plan gives **$9,974**, not $11,024. The other $1,050 is
   plan 3 (0.5% floor measured on one spouse's AGI), a different mechanism that needs one spouse to make all the
   gifts. The SALT part does not depend on allocation: each spouse's own withheld State tax ($19,000) exceeds $13,075.
4. No AMT (§56(b)(1)(A)(ii) disallows SALT). Checked in `red_t7.py` with 2026 amounts: tentative minimum tax $55,067
   and $61,927 against regular tax $60,618 and $69,193. No AMT; the gain stands.
5. Year 2 uses 2026 amounts; (7)(A)(iii) and (B)(ii)(III) raise both by 1% for 2027. Small.
6. Left out for separate filers, checked by hand for these facts (two wage earners, $300k each, no children): Roth
   and deductible IRA, student loan interest and education credits are already gone at $600k joint; Additional
   Medicare Tax and NIIT thresholds halve, same total for equal earners; capital loss limit $1,500 each, same total;
   child tax credit phase-out ($400k/$200k) same total. Real losses the model omits: the §21 dependent care credit
   (none on a separate return; about $1,200 a year if they pay for child care), State return consequences (most
   States follow federal status), the cost of two returns. None removes the gain for the modelled couple.
7. Range: with equal earners the gain exists only for MAGI between $252,500 and about $353,833 each (peak near
   $303,167: $12,600 each against $10,000 joint) and only if each spouse has State and local tax above the limit.

Strict re-run (RedT1, allocation fixed): plan survives at $9,974; under the halve-first computation the same plan
saves $2.

## T2 Close the gap: pass

Words added to (7)(B)(i): "(and, in the case of a married individual filing a separate return, such reduction shall
be applied to half the applicable limitation amount, and clause (iii) shall be applied by substituting '$5,000')".
Edit: the literal branch of `cap` deleted (RedT2). With the flag on: baseline $270,646 (unchanged), separate returns
save $1,052 (was $11,024); best overall $2,381. The $1,052 is plan 3, not SALT; with the allocation of T1 it is $2.
Position 7bL falls to the 7b figures ($7,464). This edit is identical to setting the flag to false, which the
original run already printed.

## T3 Ablation: pass

RedT3, position 7L. Remove separate returns in year 1: $5,512. In year 2: $5,512. Both: nothing but gift bunching
($1,855). Remove A's itemize election, year 1 or year 2: $5,512 (baseline moves to $270,891 because the plain filing
itemizes). Remove B's itemize election, year 1 or 2: $6,448 (the year without it still saves $936 because A alone
itemizes). No move is decoration, but the "two-year plan" is one one-year plan run twice ($5,512 a year); the
two-year frame adds nothing. Keep only the plan's six moves: 36 positions, $11,024, same figure.

## T4 Earlier law: pass

RedT4: §164(b)(6) as before Pub. L. 119-21 ("$10,000 ($5,000 in the case of a married individual filing a separate
return)"), rest 2026 law: baseline $271,136, separate returns save $210 (the 2026 0.5% charity floor, not SALT).
RedT4b, also without the 2026 changes to §170(b)(1)(I), §170(p) and §68: baseline $269,876, separate returns save
nothing; only gift bunching ($1,470, long known).

## T5 Free lunch: pass

RedT5, unmodified rules, 18 runs over 10 households plus a zero-income household with large payments: 0 positions
with a violation of: wages, tips, other income, wagering gains, SALT paid, mortgage interest, gifts and car interest
each conserved across returns and years; taxable income ≤ AGI; tax ≤ tax on AGI; every deduction ≤ the amount paid
or earned; taxable income never below AGI less the allowed items (no dollar deducted twice); no standard deduction
on a separate return whose spouse itemizes; SALT deducted ≤ SALT paid and ≤ $40,400 / $20,200. Zero income gives
zero tax, never less. The one "limit exceeded" is the finding itself: the couple deduct $26,150 on two separate
returns where a joint return allows $11,900. The checks were not mutation-tested (no bug was injected to see them
fire).

## T6 Kernel: pass

RedT6, all `by decide +kernel` or ordinary tactic proofs; `#print axioms` shows only `propext`, `Classical.choice`,
`Quot.sound` (no `sorryAx`, no `Lean.ofReduceBool`).

- `plan_literal`: the six moves are legal and cost $259,622. `plain_literal`, `plain_closed`: $270,646.
- `plan_closed`: the same plan under the closed-gap rule costs $269,594. `salt_literal` = 13,075, `salt_closed` = 5,950.
- `closed_gap_no_plan`: for **every** list of the model's moves, of any length, the closed-gap two-year tax is above
  $259,622 (in fact at least $268,265). Proved by induction on the list (`run_mem`, `run_len`, `step_rank`: rank
  strictly rises and is at most 15, so every sequence lands in the positions of `reach … 15`) plus a kernel check of
  all those positions (`closed_floor`). State not cut down. Moves are those of `moves equalEarners` (the search's own
  list, three gift amounts).
- `literal_floor`: under the word-for-word reading nothing is below $259,151.

## T7 Independent arithmetic: pass

`red_t7.py`, from the statute text with exact fractions: baseline $270,646; plan $259,622; gain $11,024. Agrees to
the dollar. Also: payments split equally $9,974; halve-first $1,052; third reading $6,720; AMT excess $0.

## T8 Outside the statute: partial (the Findings' authority statement is false)

7 searches (standard), plus direct fetches from irs.gov.

- **Instructions for Schedule A (Form 1040) (2025)**, State and Local Tax Deduction Worksheet, line 5e
  (https://www.irs.gov/instructions/i1040sca; the early-release draft PDF has the same lines): "Yes. Enter $40,000
  … 5. Enter $500,000 ($250,000 if married filing separately) … 7. Multiply line 6 by 30% (0.30) 8. Subtract line 7
  from line 1 9. Enter the larger of the amount on line 8 or $10,000 10. State and local tax deduction. Enter the
  smaller of the amount on line 9 (half the amount on line 9 if married filing separately) or the amount from
  Schedule A, line 5d". Line 1 has no separate-filer figure. This is reduce, floor, halve: the word-for-word reading.
  A separate filer at $300,000 for 2025 gets half of (40,000 − 15,000) = $12,500 on the IRS's own worksheet.
- **Publication 17 (2025)** (https://www.irs.gov/publications/p17): "The overall limit is reduced if your modified
  adjusted gross income is more than $500,000 ($250,000 if married filing separately) but will not be reduced below
  $10,000 ($5,000 if married filing separately). For more information, see the Instructions for Schedule A". No
  computation; consistent with the worksheet.
- fedratecalc.com calculator page (https://fedratecalc.com/salt-deduction-calculator/, rules checked October 28,
  2026; read through a summarising fetch): "the full amount becomes $40,000 − $15,000 = $25,000, and the cap is half
  of that, $12,500". It does not compare separate with joint filing.
- Secondary summaries (CRS RL32781, firm alerts) give only "$20,000 / $250,000 / not below $5,000" and work no
  separate-filer example. No source found that sets out filing separately to slow the phase-down. No technical
  correction found.
- Not retrieved: the Joint Committee on Taxation's general explanation (JCS-1-26, jct.gov returns 403 to automated
  clients); Senate Finance section-by-section (403); any 2026 Schedule A instructions (the "dft" PDF on irs.gov is
  the 2025 draft); tax-software worksheets.

So nothing closes the plan, and the computation it needs is already the published IRS one. The Findings' statements
"The IRS worksheet takes the 30% off the halved cap" and "A taxpayer would be filing against the form instructions"
are wrong.

## Weaknesses, ranked

1. The Findings misstate the IRS worksheet. The plan is not a contested reading; it is the form. The class
   "CANDIDATE (a reading of the text)" with "filing against the form instructions" is wrong, and the model's default
   branch (used for every other plan) is not the IRS computation.
2. The reading was supplied by a flag, not found by the search (T1, item 1). The search's only contribution is
   "separate beats joint given the reading".
3. $1,050 of the $11,024 is a different plan and depends on one spouse paying all gifts; the SALT gain is $9,974
   ($4,987 a year).
4. JCT explanation not read; if it describes a halve-first intent, a technical correction or a changed 2026
   worksheet is possible. The 2026 worksheet was not found.
5. Narrow range ($252,500 to about $353,800 each for equal earners); the §21 credit, State-return effects and filing
   costs are outside the model.
