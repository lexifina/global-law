# Group A findings: income and adjusted gross income (tax year 2025)

Files: `SocialSecurity.lean` (§86), `SelfEmployment.lean` (§§1401–1402, §164(f), additional Medicare tax), `Adjustments.lean`
(§62(a)(2)(D), §219, §221, §223), `AGI.lean` (§61, §62 assembly, the circularity, §1411), `Tests.lean`. No `sorry`, no
`native_decide`; axioms are only propext, Classical.choice and Quot.sound.

Sources: the statute is `usc26.xml` (OLRC 119-138). Examples come from the 2025 Pub 915, Pub 590-A, Pub 970 ch. 4 and the
Form 8959 instructions, read as HTML on irs.gov. There is no official self-employment tax example (the 2025 Schedule SE
instructions could not be read) and no individual §1411 example.

## Circularity

§86(b)(2) MAGI includes the §219 deduction. §219(g)(3)(A) MAGI is "after application of section 86" and "without regard
to ... 221 ... or the deduction allowable under this section". §221(b)(2)(C) MAGI is after §§86 and 219.

The model follows the Pub 590-A Appendix B / Pub 915 order:
1. Taxable benefits with no IRA deduction.
2. The IRA deduction from that MAGI.
3. Taxable benefits again, with the IRA deduction subtracted.
4. The student loan deduction.
5. AGI.

Proved:
- Under the simultaneous reading (the IRA deduction `x` must equal `iraMap x`), the fixed point is not unique. With
  $49,850 of wages and $50,000 of benefits, both $0 and $200 are fixed points (`ira_two_fixed_points`).
- The IRS answer need not be a fixed point. With $45,000 of wages the worksheet sequence gives $6,230, while $7,000 is a
  fixed point (`worksheet_not_fixed_point`).
- Every fixed point is at least the IRS answer (`worksheet_ira_le_every_fixed_point`).
- With no active participant there is exactly one fixed point (`fixed_point_unique_of_not_covered`).
- `magi221_le_magi219` and `ss_le_ss0`.

The statute is ambiguous here (confidence: medium-high). The IRS reading is the consistent one; the literal reading
favours the taxpayer.

## Findings

1. **§1401(b)(2)(B) cites the wrong section.** It reduces the threshold by wages taken into account under "section
   3121(b)(2)", the exclusion for domestic service by students in college clubs, which imposes no tax. It must mean
   §3101(b)(2), and Form 8959 applies it that way. Confidence: high (checked against the OLRC text).
2. **Qualifying surviving spouses are treated inconsistently.**
   - §1411(b)(1) gives a $250,000 threshold; §§3101(b)(2) and 1401(b)(2) give $200,000 (`qss_thresholds_differ`).
   - Under §219(g)(3)(B) the statute gives the non-joint $79,000 amount, but Pub 590-A Table 1-2 gives the joint
     $126,000–$146,000 range. At $100,000 of MAGI that is $0 against $7,000 (`qss_ira_statute_vs_irs`).
   - Confidence: high.
3. **Pub 590-A Worksheet 1-2 Example 1 appears unrounded.** It shows $6,825, while the statute's $10 rounding and the
   worksheet's own rule both give $6,830. Confidence: medium (read through a summarising fetch; check the PDF).
4. **The statute and Worksheet 1-2 agree.** The statute's round-down of the reduction equals the worksheet's round-up of
   the remaining amount with a $200 minimum, for every MAGI in range and all four 2025 pairs (`worksheet12_eq_*`).
5. **Cliffs and notches.**
   - The §219(g)(2)(B) $200 floor ends in a $200 cliff (`ira_200_cliff`). Elsewhere one dollar of MAGI removes at most
     $10 (`reducedLimit_step_7000`).
   - The §1402(b)(2) notch: $433 of profit owes $0 and $434 owes $61 (`seTax_notch`). Above the floor, one dollar adds
     at most $1 (`seTaxCore_marginal`).
   - §86 is continuous.
6. **The tax torpedo is exact** (`taxableSS40_torpedo`).
   - In the 85% zone each extra dollar of other income adds 85 cents of taxable benefits, so $100 of wages adds $185 of
     AGI.
   - Taxable benefits never exceed 85% of benefits (`taxableSS40_le_85`), nor 50% below the adjusted base amount
     (`taxableSS40_le_half`).
   - Married filing separately and living together has no 50% zone (`taxableSS40_mfs_together`).
7. **Pub 915 Worksheet 1 equals §86 for all inputs**, including the lived-together path (`worksheet1_eq_statute`,
   `worksheet1_mfs_together`).
8. **The additional Medicare tax** equals 0.9% × max(0, wages + self-employment income − threshold)
   (`additionalMedicare_combined`).
9. **Minor points.**
   - §221(b)(2)(C) is missing a comma ("85(c) 911"); the official text has a "So in original" note.
   - §221(c) says "is allowed" where Pub 970 says "claimed".
   - Whether Reg. §1.1411-4(d) allows the $3,000 capital loss in net investment income is unverified (low confidence).

## Rounding

- §86 is exact in fortieths of a dollar, rounded once; Pub 915 rounds each line.
- Self-employment tax and the additional Medicare tax are exact in ten-thousandths, rounded once.
- §219 uses the $10 round-down.
- §221 rounds the reduction to the nearest dollar.
- NIIT rounds to the nearest dollar.

## Not modelled, and gaps in `Household`

- **Living apart:** there is no field for whether a married-filing-separately couple lived apart; a `livedApart`
  argument stands in for it.
- **Who earned what:** there is no per-spouse split of self-employment income, IRA contributions, active-participant
  status or educator expenses.
- **Wages:** W-2 box 1 is used where the statute reads boxes 3 and 5.
- **Missing income items:** RRTA compensation and §135 savings bond interest.
- **Rules not modelled:**
  - §86(d)(2)(B), (d)(3) and (e);
  - §223 limits;
  - §219(f)(6) and §408(o);
  - Schedule SE optional methods;
  - NIIT on rents, royalties and passive income, allocable deductions, and the §1411(d) add-back;
  - the other §62(a) adjustments.
- **Figures cited, not re-read:** the $176,100 wage base and the $300 educator limit.

## Independent review (step 4)

The reviewer had not written this group.
- **No wrong figures or formulas** were found in the modelled scope. The §86/§219/§221 ordering, the self-employment
  computation and the §1401(b)(2)(B) citation error (from Pub. L. 111-148 §9015(b)(1)) are all confirmed.
- **New tests and theorems were added** because some earlier ones were too weak (a function returning 0 would also pass
  them):
  - self-employment tax: `seTaxCore_below_base`, `seTaxCore_straddle`, and tests `se_100k`, `se_100k_wages`,
    `se_100k_over_base`, which are hand-computed;
  - NIIT tests from the IRS NIIT Q&A: `niit_bc_tax`, `niit_19_tax`, `niit_20_tax`, `niit_loss_tax`;
  - `sli_boundaries` for the student loan deduction.
- **Upgraded:**
  - Finding 3 (Pub 590-A Example 1 prints $6,825 although its own rounding rule gives $6,830) is now high confidence.
  - The NIIT capital-loss treatment is confirmed by Reg. §1.1411-4(d)(2): "net gain may not be less than zero".
- **Downgraded:** the $200 IRA floor cliff and the $400 self-employment notch are deliberate design, not drafting
  errors.
- **Withdrawn:** the §221(c) "is allowed / claimed" point.
- **Known differences from IRS software**, all caused by fields `Household` lacks:
  - qualifying-surviving-spouse IRA range;
  - one active-participant flag per joint return;
  - self-employment income assigned to the head;
  - W-2 box 1 used instead of boxes 3 and 5;
  - married filing separately assumed to have lived together.
