# Group B: deductions and taxable income (tax year 2025): findings

Source: `usc26.xml` (OLRC release point 119-138), read for taxable years beginning in 2025. Files:

| File | Contents |
|---|---|
| `Deductions.lean` | The provisions, copied from the statute: §63(b)–(f), §151(d)(5)(C), §224, §225, §163(h)(4), §164(b)(6)–(7), §163(h)(3) (as given), §170(b)(1)(G), §213(a), §199A(a), (b)(2)–(3), (d)(3), (e). It also holds 49 tests against IRS material. |
| `Properties.lean` | 75 theorems. About 60 hold for all inputs; the other 15 are worked counterexamples and notches. |
| `Forms.lean` | The 2025 Schedule 1-A Parts II–V and the Schedule A SALT worksheet, written line by line. Each is proved equal to the statute for all inputs. |
| `Axioms.lean` | `#print axioms` for the main theorems. Each uses only `propext`, `Classical.choice` and `Quot.sound`, or none. |

No `sorry`, `native_decide` or added axioms. Build with `lake build TaxCode.Individual.B.Axioms`.

Confidence levels: **certain** means the text is unambiguous and the result is proved; **high** means it is proved, but
saying "the statute means X" involves a reading; **medium** means it is an interpretation.

## 1. There is no §151(f); the senior deduction is §151(d)(5)(C) (certain)

Pub. L. 119-21 §70103 inserted it as §151(d)(5)(C)(i)–(v). Section 151 ends at subsection (e).

## 2. Read without its effective-date notes, the consolidated text states the 2026 law (certain)

Release point 119-138 already contains several 2025 Act changes that apply only to "taxable years beginning after
December 31, 2025". The 2025 rules therefore come from the text as it stood before the amendment:

- **§170(p).** It now says $1,000 ($2,000 joint), but for 2025 the earlier text ("beginning in 2021") applies. So
  §63(b)(4) is worth **$0 in 2025**.
- **§170(b)(1)(I) and (G)(i).** The new 0.5% floor and the rewritten (G)(i) start in 2026 (§70425(c)). For 2025, cash
  gifts are capped at 60% of AGI.
- **§199A(b)(3)(B), (d)(3) and (i).** The $75,000 / $150,000 phase-in range and the $400 minimum start in 2026
  (§70105(c)). For 2025 the range is $50,000 / $100,000, matching the Form 8995 instructions ($247,300 / $494,600).
- **§68.** The new 2/37 limit starts in 2026. In 2025 the earlier §68(f) switches §68 off, so itemized deductions are
  not limited at all.

## 3. SALT phase-down (§164(b)(7)(B))

- **Exact $300 per $1,000 (certain).**
  - `salt_step_300`: for any status other than married filing separately, with $500,000 ≤ MAGI and MAGI + $1,000 ≤
    $600,000, the cap falls by exactly $300.
  - `salt_closed_form` gives the formula: cap = $40,000 − 30% × (MAGI − $500,000).
  - One more dollar of MAGI lowers the cap by at most $1 (`salt_cap_step`), and the cap never rises with MAGI
    (`salt_cap_antitone`).
- **Where it ends (certain).** The cap is $10,000 from $600,000 on (`salt_floor`). Rounding each amount half up to the
  dollar reaches the floor $1 early (`salt_floor_rounding`).
- **Married filing separately: 15%, ending at $350,000 (high).**
  - §164(b)(6)(B) halves the limit after the 30% reduction and the $10,000 floor, so the separate-return cap falls
    $150 per $1,000 (`salt_mfs_step_150`) and reaches $5,000 only at $350,000 (`salt_mfs_floor`). At $300,000 it is
    still $12,500 (`salt_mfs_at_300k`).
  - The Schedule A worksheet halves after the reduction too: line 10 halves line 9 (`scheduleASalt_eq`, all inputs).
  - The "What's New" summaries could suggest to a reader that the reduction is 30% of a $20,000 cap.
- **Splitting income favours separate returns, and marriage is penalised (certain).**
  - The joint cap at 2m is at most twice the separate cap at m (`salt_split_ge_joint`). At m = $300,000 that is
    $10,000 joint against $25,000 from two separate returns.
  - Two unmarried people get twice what a married couple gets (`salt_marriage_penalty`).
- **Effect on itemized deductions (certain).** With taxes paid of at least $40,000, each $1,000 of AGI in the band
  removes exactly $300 of itemized deductions (`itemized_salt_step`).
- **Drafting.**
  - The §164(b)(6) heading still says "taxable years 2018 through 2025".
  - The OLRC notes a stray comma after "December 31, 2017," as "So in original".

## 4. Senior deduction (§151(d)(5)(C))

- **Bounds and shape (certain).** Each qualified person's $6,000 stays between $0 and $6,000 and never rises with MAGI,
  falling exactly $6 per $100 inside the band (`senior_rate`).
- **Two seniors face 12% (certain).**
  - The reduction applies to each $6,000, so a joint return with two qualified individuals loses up to 12 cents per
    dollar (`seniorDeduction_step`, `senior_two_at_200k`). Schedule 1-A agrees.
  - Both amounts are gone at $250,000 joint and $175,000 single. Rounding makes the end $8 early (`senior_gone`,
    `senior_end_exact`).
- **How it fits with the standard deduction (certain).**
  - The senior deduction is a §151 deduction, so itemizers keep it. The §63(f) age amount exists only inside the
    standard deduction, so a 70-year-old who itemizes keeps the $6,000 but loses the $2,000 (`senior_itemizer`).
  - Outside separate returns, the number of people qualifying never exceeds the number of §63(f) boxes
    (`senior_within_63f`).
  - A separate filer gets §63(f) but no senior deduction (`senior_mfs_counterexample`).
- **A senior who can be claimed as a dependent still gets the full $6,000 (medium).** The deduction has no dependency
  condition, unlike the §151(d)(2) exemption amount (`senior_dependent`). The IRS material neither confirms nor denies
  this.
- **Surviving spouses.** The qualifying-surviving-spouse status uses the $75,000 threshold, because only "a joint return"
  gets $150,000.

## 5. Tips (§224), overtime (§225), car-loan interest (§163(h)(4)): notches

- **Two counting rules in one Act (certain).** §§224 and 225 reduce "$100 for each $1,000", which rounds down.
  §163(h)(4) reduces "$200 for each $1,000 (or portion thereof)", which rounds up. Schedule 1-A follows each rule
  exactly (Parts II–V, proved). Being $1 over costs $0 of tips deduction but $200 of car deduction (`steps_differ`).
- **One dollar costs $100 or $200 (certain).**
  - Tips: $25,000 at $150,999, $24,900 at $151,000 (`tips_notch`).
  - Car: $10,000 at $100,000, $9,800 at $100,001 (`car_notch`).
  - For all inputs the loss per extra dollar is at most $100 (tips, overtime) or $200 (car), and over any span d at
    most d/10 + $100 (`tips_average`).
- **The car deduction ends $999 early (certain).** It reaches zero at $149,001 single / $249,001 joint (`car_gone`).
- **Caps treat married couples differently (certain).**
  - Tips: $25,000 per return whatever the status, so two single tipped workers can deduct $50,000 but share $25,000
    once married ("not a per spouse limit", Schedule 1-A instructions).
  - Overtime: the cap doubles for a joint return.
  - Car loan interest: the cap stays $10,000 but the threshold doubles.
  - Phase-outs end at $400,000 / $550,000 for tips (`tips_gone`) and $275,000 / $550,000 for overtime
    (`overtime_gone`).
- **The SSN rule has no antecedent (high).** §§224(e)(1) and 225(d)(1) require "such individual's social security
  number", but no individual is mentioned earlier in either subsection.
- **Overtime premium.** Only the FLSA-required half counts, consistent with "required".
- **Separate returns.** A married person filing separately may take the car-loan deduction (threshold $100,000). Tips,
  overtime and the senior deduction are barred on separate returns.

## 6. More than $1 of deductions lost per $1 of income: yes (certain)

- **Taxable income before §199A never falls when AGI rises** (`taxableBeforeQbi_mono`, all households).
  - One dollar of AGI raises it by at most $405 (`taxableBeforeQbi_step`): the dollar itself, $2 of SALT and medical
    rounding, and $402 from the four new deductions.
- **Worked notches.**
  - +$201 for a single filer with car-loan interest at $100,000 (`notch_car`).
  - +$201 for a joint return with $25,000 of tips and $25,000 of overtime at $301,000 (`notch_tips_overtime`).
  - The car band and the tips/overtime band never overlap, so in practice the jump peaks at about $202.
- **The §199A phase-in can cost more than $1 per $1, without limit.**
  - +$3 per $1 with $537,300 of QBI and no employees (`notch_qbi`).
  - +$21 per $1 with $5,000,000 of QBI (`notch_qbi_large`).
- **Taxable income still never falls when AGI rises**, for every household without a specified service trade or
  business (`taxableIncome_mono`). The phase-in has no cliff at the end of the band (`qbiPhase_continuous_at_end`).
- For specified service businesses this is not proved. A numeric search found no counterexample.

## 7. Medical expenses with negative AGI (§213(a)) (high)

With negative AGI the 7.5% floor is negative, so the deduction exceeds the expenses: $1,000 at AGI −$100,000 gives
$8,500 (`medical_exceeds_expenses`). This has no practical effect. With AGI ≥ 0 the deduction never exceeds the
expenses (`medical_le`).

## 8. Standard deduction details

- **§63(f)(1)(B) on joint returns (medium).** Read literally, a joint return's spouse gets no age or blind amount,
  because §151(b) gives a spouse exemption only "if a joint return is not made". The IRS charts treat both spouses as
  the taxpayer (Treas. Reg. §1.151-1(b)), and that is how it is modelled.
- **2025 amounts.** §63(c)(7)(A) puts them in the text ($15,750 / $23,625; joint is 200% = $31,500). All 2025 chart
  values are reproduced.
- **Dependents.** The §63(c)(5) limit cuts only the basic amount; §63(f) amounts are added on top (Pub. 501 Example 3).

## 9. §199A thresholds on separate returns (high)

The threshold is not halved for separate returns, so a couple filing separately gets 2 × $197,300, the same as filing
jointly (confirmed by the Form 8995 instructions). The OLRC footnote at §199A(e)(4)(A), "7704(a)" ("probably should be
7704(b)"), is a known drafting error.

## 10. Rounding (low)

The statute states no rounding for 6%, 30%, 60%, 7.5% or 20%. Every percentage is rounded half up to the dollar, which
the Form 1040 instructions allow. Form 1040 line 15 floors taxable income at zero; the statute allows it to go
negative.

## Tests

There are 49 tests in `Deductions.lean`, plus 5 form-equivalence proofs in `Forms.lean`. Sources:
- **Form 1040 instructions 2025:** standard deduction charts, p. 35.
- **Pub. 501 (2025):** Examples 1–3 and Dependents Examples 1–4.
- **Schedule 1-A and its instructions:** senior maxima, the separate-return and SSN bars, overtime Examples 1–5, the
  tips cap, and the overtime and car caps.
- **Schedule A instructions:** line 5e and the SALT worksheet.
- **Pub. 526:** Examples 1–2.
- **Form 8995 instructions:** the SSTB band.

No official numeric example was found for the SALT phase-down, medical expenses, the tips, overtime or car phase-outs,
or a partial senior phase-out. The line-by-line form proofs stand in for those.

## Not modelled

- **§63:** (c)(6)(B)–(D); indexing for other years; net qualified disaster losses.
- **§151(d)(5)(C):** deaths during the year, and exact birth dates.
- **§§224, 225 and 163(h)(4):** occupation, FLSA status and vehicle tests; amounts are taken as given.
- **§164:** foreign real property taxes, and the choice between sales and income tax.
- **§163(h)(3):** acquisition-debt limits.
- **§170:** non-cash categories and carryovers.
- **§213:** what counts as medical care.
- **§199A:** more than one business, aggregation, REIT and PTP income, cooperatives, loss carryforwards, and trusts.
- **§67, casualty losses, gambling losses.**

## Fields the shared `Household` lacks (supplied through `Facts`)

- whether the other spouse itemizes (separate returns), and whether a separate-return spouse has no income;
- per-person SSNs, and which spouse earned the tips or overtime;
- whether the VIN is on the return;
- §§911, 931 and 933 excluded income;
- the business's W-2 wages, property basis and SSTB status;
- an explicit itemizing election;
- separate earned income, and birth dates.

## Independent review (step 4)

The reviewer had not written this group.
- **No errors in the definitions.** Checked against `usc26.xml`: §§63(b)–(f), 151(d)(5)(C), 164(b)(6)–(7),
  170(b)(1)(G)/(H)/(I) and (p), 199A(a), (b)(3), (d)(3), (e)(2) and (i), 224, 225, 163(h)(4) and 68.
- **2026 law in the OLRC text: all four claims confirmed** by the effective-date notes: §70424(b), §70425(c), §70105(c)
  and §70111(c).
- **SALT for married filing separately ($150 per $1,000, floor at $350,000): raised to certain.** The remark that IRS
  summaries might mislead readers is withdrawn as speculation.
- **Downgraded:**
  - The "SSN rule has no antecedent" finding, from high to low. "The individual" in §§224(a) and 225(a) supplies one.
  - The negative-AGI medical finding, from high to medium.
  - The "$1 early" SALT end and the "$8 early" senior end. Both are artefacts of the model's optional half-up rounding,
    not of the statute.
- **Example corrected:** `notch_qbi_large` uses mortgage interest above the §163(h)(3)(F) limit, which is unrealistic.
  The claim itself stands (taxable income could fall in the band through an NOL instead).
- **Added theorems:** `qbiPhase_midpoint` and `sstbShare_midpoint` pin down the §199A phase-in formula. Many earlier
  bounds and monotonicity theorems would also hold for a deduction that always returns 0.
- **Verified against IRS sources:** Pub. 501 examples, the 2025 Schedule 1-A, the Schedule A worksheet and the Form 8995
  thresholds.
