import TaxCode.Individual.Household

/-!
# Group B: deductions and taxable income, tax year 2025

Copied from 26 U.S.C. as amended through Pub. L. 119-138 (OLRC release point 119-138), read for taxable years
beginning in 2025. Where Pub. L. 119-21 (4 July 2025, "the 2025 Act") amended a provision only for taxable years
beginning after 31 December 2025 (its effective-date notes), the text in force for 2025 is the pre-amendment text;
each such case is noted on the definition.

Adjusted gross income is an input (group A computes it). Every amount is whole dollars (`Int`).

**Rounding.** The statute states no rounding for any percentage used here. The Form 1040 instructions (2025,
"Rounding Off to Whole Dollars") let filers round each amount half up to whole dollars; every percentage line below
is therefore computed with `roundDollar` (half up). Where a form line rounds differently (Schedule 1-A lines 11, 19,
28) the form's rule is the statute's own counting rule and is used exactly.

**Facts the shared `Household` lacks** are collected in `Facts` (every field defaults to the common case), and every
public function takes them as a trailing optional argument, so `standardDeduction h` etc. work as the brief asks.
-/

namespace TaxCode.Individual.B
open TaxCode.Individual

/-- Facts used by group B that `Household` does not carry. Defaults are the common case. -/
structure Facts where
  /-- §63(c)(6)(A): a married individual filing separately whose spouse itemizes. -/
  spouseItemizes : Bool := false
  /-- §63(f)(1)(B), (2)(B) via §151(b): on a separate return the spouse's age/blind amounts are allowed only if the
  spouse had no gross income and is not another taxpayer's dependent. -/
  spouseNoIncomeNotDependent : Bool := false
  /-- §151(d)(5)(C)(iv): the SSN (as defined in §24(h)(7)) of the taxpayer / spouse is on the return. -/
  headSsn : Bool := true
  spouseSsn : Bool := true
  /-- §224(e), §225(d): the SSN of the individual who received the tips / overtime is on the return. -/
  earnerSsn : Bool := true
  /-- §163(h)(4)(B)(iii): the vehicle identification number is on the return. -/
  vinReported : Bool := true
  /-- Amounts excluded under §§911, 931, 933 (added to AGI for every MAGI in this group). -/
  excludedIncome : Int := 0
  /-- §199A(b)(2)(B): W-2 wages of, and unadjusted basis of qualified property held by, the (single) business. -/
  qbiW2Wages : Int := 0
  qbiUbia : Int := 0
  /-- §199A(d)(2): the business is a specified service trade or business. -/
  qbiSstb : Bool := false
  /-- §63(e): `some true` elects to itemize, `some false` declines; `none` takes the larger. -/
  electItemize : Option Bool := none
  deriving Repr, Inhabited

/-! ## §63(c) standard deduction -/

/-- §63(c)(2)(C) as substituted by §63(c)(7)(A)(ii) (Pub. L. 119-21 §70102): "$15,750" "in any other case". Not
inflation-adjusted for 2025: §63(c)(7)(B)(i) switches §63(c)(4) off, and (B)(ii) indexes only years after 2025. -/
def basicOther : Int := 15750

/-- §63(c)(2): the basic standard deduction. (A) joint return or surviving spouse: "200 percent of the dollar amount
in effect under subparagraph (C)"; (B) head of household: $23,625 by (7)(A)(i); (C) any other case. -/
def basicStandard : Filing → Int
  | .mfj | .qss => 2 * basicOther
  | .hoh => 23625
  | .single | .mfs => basicOther

/-- §63(c)(5) as inflation-adjusted for 2025 (Rev. Proc. 2024-40 §3.15(2); Form 1040 instructions 2025, Standard
Deduction Worksheet for Dependents): "the greater of" $1,350 or $450 plus earned income. -/
def dependentFloor : Int := 1350
def dependentAddOn : Int := 450

/-- Earned income for §63(c)(5) (§32(c)(2) meaning). `Household` has no separate field; we use wages plus net
earnings from self-employment, which is what Pub. 501 (2025) Example 4 does ($7,000 wages − $3,000 business loss).
The deduction for half of SE tax and taxable scholarships are not modelled. -/
def earnedIncome (h : Household) : Int := h.wages + h.seIncome

/-- §63(c)(5): the basic standard deduction of a dependent "shall not exceed the greater of" (A) $500 [$1,350] or
(B) $250 [$450] plus earned income. -/
def basicStandardFor (h : Household) : Int :=
  if h.canBeClaimedAsDependent then
    min (basicStandard h.filing) (max dependentFloor (dependentAddOn + earnedIncome h))
  else basicStandard h.filing

/-- §63(f)(3): "$750" for "an individual who is not married and is not a surviving spouse", otherwise $600; 2025
amounts $2,000 / $1,600 (Rev. Proc. 2024-40 §3.15(3); Form 1040 instructions 2025, chart for people born before
January 2, 1961, or blind). Marital status per §63(g)/§7703: a head of household is unmarried. -/
def additionalUnit : Filing → Int
  | .single | .hoh => 2000
  | .mfj | .mfs | .qss => 1600

/-- §63(f)(1)(A)/(2)(A): the taxpayer "has attained age 65 before the close of his taxable year" / "is blind". -/
def personBoxes (p : Person) : Int := (if p.age ≥ 65 then 1 else 0) + (if p.blind then 1 else 0)

/-- Number of §63(f) additional amounts. The spouse's amounts ((f)(1)(B), (2)(B)) need "an additional exemption
... allowable to the taxpayer for such spouse under section 151(b)"; §151(b) gives one only on a separate return for a
spouse with no gross income who is nobody's dependent. On a joint return both spouses are "the taxpayer" and each
counts under (A) (Treas. Reg. §1.151-1(b); Form 1040 chart). -/
def additionalCount (h : Household) (f : Facts := {}) : Int :=
  personBoxes h.head +
    match h.spouse with
    | none => 0
    | some s =>
      match h.filing with
      | .mfj => personBoxes s
      | .mfs => if f.spouseNoIncomeNotDependent then personBoxes s else 0
      | _ => 0

/-- §63(c)(3): the additional standard deduction. -/
def additionalStandard (h : Household) (f : Facts := {}) : Int := additionalCount h f * additionalUnit h.filing

/-- §63(c)(1): basic plus additional; §63(c)(6)(A): zero for "a married individual filing a separate return where
either spouse itemizes deductions" (here: the other spouse itemizes; this spouse electing to itemize is handled by
`deduction`). §63(c)(6)(B)–(D) (nonresident aliens, short years, estates) are not modelled. -/
def standardDeduction (h : Household) (f : Facts := {}) : Int :=
  if h.filing = .mfs ∧ f.spouseItemizes = true then 0
  else basicStandardFor h + additionalStandard h f

/-! ## Modified AGI (§151(d)(5)(C)(iii)(II), §163(h)(4)(C)(ii)(II), §164(b)(7)(B)(iv), §224(b)(2)(B), §225(b)(2)(B))

All five definitions are word for word the same: AGI "increased by any amount excluded from gross income under section
911, 931, or 933". -/
def magi (agi : Int) (f : Facts := {}) : Int := agi + f.excludedIncome

/-! ## §151(d)(5)(C) enhanced deduction for seniors (Pub. L. 119-21 §70103)

The brief calls this §151(f); the Act inserted it as §151(d)(5)(C) and there is no §151(f). -/

/-- §151(d)(5)(C)(iii)(I): "$75,000 ($150,000 in the case of a joint return)". -/
def seniorThreshold : Filing → Int
  | .mfj => 150000
  | _ => 75000

/-- §151(d)(5)(C)(i), (iii)(I): "the $6,000 amount ... shall be reduced (but not below zero) by 6 percent of so much
of the taxpayer's modified adjusted gross income as exceeds" the threshold. Schedule 1-A (2025) lines 31–35. -/
def seniorPerPerson (filing : Filing) (m : Int) : Int :=
  max 0 (6000 - roundDollar (6 * max 0 (m - seniorThreshold filing)) 100)

/-- §151(d)(5)(C)(ii): qualified individuals — (I) the taxpayer aged 65, (II) "in the case of a joint return" the
spouse aged 65; (iv) each needs an SSN on the return; (v) a married individual must file jointly. -/
def seniorCount (h : Household) (f : Facts := {}) : Int :=
  if h.filing = .mfs then 0 else
    (if h.head.age ≥ 65 ∧ f.headSsn = true then 1 else 0) +
    (match h.spouse with
     | some s => if h.filing = .mfj ∧ s.age ≥ 65 ∧ f.spouseSsn = true then 1 else 0
     | none => 0)

/-- §151(d)(5)(C): "a deduction in an amount equal to $6,000 for each qualified individual", each reduced. -/
def seniorDeduction (h : Household) (m : Int) (f : Facts := {}) : Int :=
  seniorCount h f * seniorPerPerson h.filing m

/-! ## §224 qualified tips (Pub. L. 119-21 §70201) -/

/-- §224(b)(2)(A): "$150,000 ($300,000 in the case of a joint return)"; the same for §225. -/
def tipsThreshold : Filing → Int
  | .mfj => 300000
  | _ => 150000

/-- §224(b)(2)(A), §225(b)(2)(A): "$100 for each $1,000 by which" MAGI exceeds the threshold. "For each $1,000"
counts whole thousands only; Schedule 1-A lines 11/19: "decrease the result to the next lower whole number". -/
def tipsReduction (filing : Filing) (m : Int) : Int := 100 * (max 0 (m - tipsThreshold filing) / 1000)

/-- §224(a), (b)(1) ("shall not exceed $25,000" — per return, not per spouse), (b)(2), (e) SSN, (f) joint return
if married. Qualified tips (§224(c), (d)) are taken as given in `Household.qualifiedTips`. -/
def tipsDeduction (h : Household) (m : Int) (f : Facts := {}) : Int :=
  if h.filing = .mfs ∨ f.earnerSsn = false then 0
  else max 0 (min (max 0 h.qualifiedTips) 25000 - tipsReduction h.filing m)

/-! ## §225 qualified overtime compensation (Pub. L. 119-21 §70202) -/

/-- §225(c)(1): the overtime pay "in excess of the regular rate". For time-and-a-half pay that is one third of the
overtime pay; Schedule 1-A instructions (2025) Examples 1, 4, 5 divide total overtime pay by 3. -/
def premiumOfTimeAndHalf (overtimePay : Int) : Int := overtimePay / 3

/-- Schedule 1-A instructions (2025) Examples 2–3: if the employer pays more than time-and-a-half, only the FLSA
"half" counts: half the regular-rate pay for the overtime hours. -/
def premiumOfRegularPay (regularPayForOvertimeHours : Int) : Int := regularPayForOvertimeHours / 2

/-- §225(b)(1): "$12,500 ($25,000 in the case of a joint return)". -/
def overtimeCap : Filing → Int
  | .mfj => 25000
  | _ => 12500

/-- §225(a), (b), (d) SSN, (e) joint return if married. -/
def overtimeDeduction (h : Household) (m : Int) (f : Facts := {}) : Int :=
  if h.filing = .mfs ∨ f.earnerSsn = false then 0
  else max 0 (min (max 0 h.qualifiedOvertime) (overtimeCap h.filing) - tipsReduction h.filing m)

/-! ## §163(h)(4) qualified passenger vehicle loan interest (Pub. L. 119-21 §70203) -/

/-- §163(h)(4)(C)(ii)(I): "$100,000 ($200,000 in the case of a joint return)". No joint-return requirement, so a
separate return uses $100,000. -/
def carThreshold : Filing → Int
  | .mfj => 200000
  | _ => 100000

/-- §163(h)(4)(C)(ii)(I): "$200 for each $1,000 (or portion thereof)". Schedule 1-A line 28: "increase the result
to the next higher whole number". -/
def carReduction (filing : Filing) (m : Int) : Int := 200 * ((max 0 (m - carThreshold filing) + 999) / 1000)

/-- §163(h)(4)(C)(i) $10,000 per return, (C)(ii), (B)(iii) VIN. The interest is taken as given (the vehicle, lien,
date, U.S.-assembly and related-party conditions of (B), (D), (E) are not modelled). -/
def carLoanDeduction (h : Household) (m : Int) (f : Facts := {}) : Int :=
  if f.vinReported = false then 0
  else max 0 (min (max 0 h.carLoanInterest) 10000 - carReduction h.filing m)

/-! ## Itemized deductions -/

/-- §164(b)(7)(A)(i): the applicable limitation amount for 2025, $40,000. -/
def saltBase : Int := 40000

/-- §164(b)(7)(B)(ii)(I): threshold $500,000; (B)(i) "half the threshold amount in the case of a married individual
filing a separate return". -/
def saltThreshold : Filing → Int
  | .mfs => 250000
  | _ => 500000

/-- §164(b)(7)(B)(i), (iii): the applicable limitation amount, "reduced by 30 percent of the excess (if any)" of MAGI
over the threshold, but "not ... less than $10,000". Schedule A instructions 2025, SALT worksheet lines 1–9. -/
def saltLimitAmount (filing : Filing) (m : Int) : Int :=
  max 10000 (saltBase - roundDollar (3 * max 0 (m - saltThreshold filing)) 10)

/-- §164(b)(6)(B): taxes "shall not exceed the applicable limitation amount (half the applicable limitation amount in
the case of a married individual filing a separate return)". The halving comes after the reduction and the $10,000
floor, so for a separate return the cap falls by 15% (not 30%) of the excess and bottoms out at $5,000 at MAGI
$350,000. Worksheet line 10 halves line 9 in exactly this order. -/
def saltCap (filing : Filing) (m : Int) : Int :=
  if filing = .mfs then roundDollar (saltLimitAmount filing m) 2 else saltLimitAmount filing m

/-- §164(a)(1)–(3), (b)(5) taxes paid, capped by §164(b)(6)(B). (Foreign real property tax, (b)(6)(A), and
trade-or-business taxes are outside `Household.stateLocalTaxes`.) -/
def saltDeduction (h : Household) (m : Int) : Int := min (max 0 h.stateLocalTaxes) (saltCap h.filing m)

/-- §163(h)(2)(D), (3): qualified residence interest, taken as given (the $750,000 acquisition-debt limit of
§163(h)(3)(F) is not modelled). -/
def mortgageDeduction (h : Household) : Int := max 0 h.mortgageInterest

/-- §170(b)(1)(G)(i) as in force for 2025 (the pre-Pub. L. 119-21 text; the 2025 Act's rewrite of (G)(i), the new
0.5% floor (b)(1)(I) and the §170(p) increase all apply only to years after 2025, §70424(b), §70425(c)): cash to a
(b)(1)(A) organization may not exceed "60 percent of the taxpayer's contribution base", the contribution base being
AGI (§170(b)(1)(H), NOL carrybacks ignored). Carryovers (§170(d)) are not modelled. -/
def charityDeduction (h : Household) (agi : Int) : Int :=
  min (max 0 h.charitableCash) (max 0 (roundDollar (60 * agi) 100))

/-- §213(a): medical expenses "to the extent that such expenses exceed 7.5 percent of adjusted gross income".
Copied literally: with a negative AGI the floor is negative (see `Properties.medical_exceeds_expenses`). -/
def medicalDeduction (h : Household) (agi : Int) : Int :=
  max 0 (max 0 h.medicalExpenses - roundDollar (75 * agi) 1000)

/-- §63(d): itemized deductions — those allowed by the chapter other than above-the-line deductions and those listed
in §63(b) (so the §151, §199A, §224, §225 and §163(h)(4) deductions are not itemized). §68 does not apply in 2025: the
pre-2025-Act §68(f) suspended it for 2018–2025, and the new §68 (2/37 limitation) applies after 2025. -/
def itemized (h : Household) (agi : Int) (f : Facts := {}) : Int :=
  saltDeduction h (magi agi f) + mortgageDeduction h + charityDeduction h agi + medicalDeduction h agi

/-- §63(b)(4): the §170(p) deduction for non-itemizers. In force for 2025 is the text before Pub. L. 119-21 §70424,
which allowed it only "In the case of any taxable year beginning in 2021"; the $1,000/$2,000 version starts in 2026.
So it is zero for 2025 (the consolidated text, read without its notes, wrongly suggests otherwise). -/
def nonItemizerCharity (_h : Household) : Int := 0

/-! ## §63(e) the deduction taken, and the §63(b) deductions taken by everyone -/

/-- §63(e)(1): itemized deductions are allowed only on election; absent an explicit choice the household takes the
larger (which is what minimises taxable income, since all other terms are the same either way). -/
def deduction (h : Household) (agi : Int) (f : Facts := {}) : Int :=
  match f.electItemize with
  | some true => itemized h agi f
  | some false => standardDeduction h f
  | none => max (standardDeduction h f) (itemized h agi f)

/-- §63(b)(2), (5), (6), (7) and, for itemizers, §63(a) with §63(d)(2): the senior, tips, overtime and car-loan
deductions are subtracted whether or not the household itemizes (Schedule 1-A, Form 1040 line 13b). -/
def belowTheLine (h : Household) (agi : Int) (f : Facts := {}) : Int :=
  let m := magi agi f
  seniorDeduction h m f + tipsDeduction h m f + overtimeDeduction h m f + carLoanDeduction h m f

/-- Taxable income before the §199A deduction (Form 8995 line 11: Form 1040 line 11 minus lines 12e and 13b). -/
def taxableBeforeQbi (h : Household) (agi : Int) (f : Facts := {}) : Int :=
  agi - deduction h agi f - belowTheLine h agi f - nonItemizerCharity h

/-! ## §199A qualified business income deduction (2025 law) -/

/-- §199A(e)(2): threshold amount for 2025, $197,300 ($394,600 joint) — Rev. Proc. 2024-40 §3.27; Form 1040
instructions 2025, line 13a; Form 8995 instructions 2025. The statute's base is "$157,500 (200 percent of such amount in
the case of a joint return)", so a separate return uses $197,300. -/
def qbiThreshold : Filing → Int
  | .mfj => 394600
  | _ => 197300

/-- §199A(b)(3)(B), (d)(3) as in force for 2025: phase-in range "$50,000 ($100,000 in the case of a joint return)".
Pub. L. 119-21 §70105(a) widens it to $75,000/$150,000 only for years after 2025 (§70105(c)). Form 8995 instructions
2025 give the 2025 ends $247,300 / $494,600. -/
def qbiRange : Filing → Int
  | .mfj => 100000
  | _ => 50000

/-- §199A(d)(3)(B): the SSTB applicable percentage, applied to an amount `x` (QBI, W-2 wages or UBIA): 100% reduced
by the ratio of (taxable income − threshold) to the range; zero at or beyond the end of the range. -/
def sstbShare (filing : Filing) (ti x : Int) : Int :=
  if ti ≤ qbiThreshold filing then x
  else if ti < qbiThreshold filing + qbiRange filing then
    x * (qbiThreshold filing + qbiRange filing - ti) / qbiRange filing
  else 0

/-- §199A(b)(3): how the wage/property limit applies at taxable income `ti`, given (2)(A) amount `a` and (2)(B) amount
`b`. (3)(A): at or below the threshold "without regard to subparagraph (B)"; (3)(B): inside the range, if `b < a`,
"without regard to subparagraph (B)" and reducing `a` by (a − b) × (ti − threshold) / range; beyond, the lesser. -/
def qbiPhase (filing : Filing) (ti a b : Int) : Int :=
  if ti ≤ qbiThreshold filing then a
  else if ti ≤ qbiThreshold filing + qbiRange filing ∧ b < a then
    a - roundDollar ((a - b) * (ti - qbiThreshold filing)) (qbiRange filing)
  else min a b

/-- §199A(b)(2) for one qualified trade or business: (A) 20% of QBI; (B) the greater of 50% of W-2 wages or 25% of
W-2 wages plus 2.5% of UBIA; phased in by `qbiPhase`. -/
def qbiComponent (filing : Filing) (ti qbi w2 ubia : Int) : Int :=
  qbiPhase filing ti (roundDollar (20 * qbi) 100)
    (max (roundDollar (50 * w2) 100) (roundDollar (25 * w2) 100 + roundDollar (25 * ubia) 1000))

/-- §199A(a): the lesser of (1) the combined QBI amount and (2) 20% of the excess (if any) of taxable income
(computed without the §199A deduction, (e)(1)) over net capital gain. A combined loss gives no deduction (it carries
forward under (c)(2); Form 8995 line 16). REIT/PTP amounts, cooperatives (b)(7), (g), several businesses and loss
carryforwards are not modelled. The §199A(i) $400 minimum deduction (Pub. L. 119-21 §70105(b)) starts in 2026. -/
def qbiDeduction (h : Household) (taxableBeforeQbi netCapGain : Int) (f : Facts := {}) : Int :=
  let q := if f.qbiSstb then sstbShare h.filing taxableBeforeQbi h.qbi else h.qbi
  let w := if f.qbiSstb then sstbShare h.filing taxableBeforeQbi f.qbiW2Wages else f.qbiW2Wages
  let u := if f.qbiSstb then sstbShare h.filing taxableBeforeQbi f.qbiUbia else f.qbiUbia
  max 0 (min (qbiComponent h.filing taxableBeforeQbi q w u)
    (roundDollar (20 * max 0 (taxableBeforeQbi - netCapGain)) 100))

/-- §1(h)(3), (11): net capital gain (net long-term gain less net short-term loss) plus qualified dividends — the
§199A(a)(2)(B) amount, which Form 8995 line 12 takes as qualified dividends plus net capital gain. -/
def netCapitalGain (h : Household) : Int :=
  max 0 (h.longTermGains + min 0 h.shortTermGains) + max 0 h.qualifiedDividends

/-- §63(a)/(b): taxable income. Form 1040 line 15 enters zero if the result is negative (the statute itself lets
taxable income be negative, which matters only for net operating losses, not modelled). -/
def taxableIncome (h : Household) (agi : Int) (f : Facts := {}) : Int :=
  let t := taxableBeforeQbi h agi f
  max 0 (t - qbiDeduction h t (netCapitalGain h) f)

/-! ## Tests against official 2025 IRS material -/

section Tests

private def p (age : Nat) (blind : Bool := false) : Person := { age := age, blind := blind }

-- Form 1040 instructions 2025, Standard Deduction Chart for Most People (line 12e) / Pub. 501 (2025) Table 6.
theorem std_single : standardDeduction { filing := .single, head := p 40 } = 15750 := by decide
theorem std_mfs : standardDeduction { filing := .mfs, head := p 40, spouse := some (p 40) } = 15750 := by decide
theorem std_hoh : standardDeduction { filing := .hoh, head := p 40 } = 23625 := by decide
theorem std_qss : standardDeduction { filing := .qss, head := p 40 } = 31500 := by decide
-- Pub. 501 (2025) p. 24, Example 1: joint, both under 65, not blind: $31,500.
theorem pub501_std_ex1 : standardDeduction { filing := .mfj, head := p 46, spouse := some (p 33) } = 31500 := by
  decide
-- Pub. 501 (2025) p. 24, Example 2: same, one spouse blind: $33,100.
theorem pub501_std_ex2 :
    standardDeduction { filing := .mfj, head := p 46, spouse := some (p 33 true) } = 33100 := by decide
-- Pub. 501 (2025) p. 24, Example 3: joint, both over 65: $34,700.
theorem pub501_std_ex3 : standardDeduction { filing := .mfj, head := p 70, spouse := some (p 68) } = 34700 := by
  decide
-- Form 1040 instructions 2025 p. 35, chart for people born before 2 January 1961 or blind.
theorem chart_single_1 : standardDeduction { filing := .single, head := p 66 } = 17750 := by decide
theorem chart_single_2 : standardDeduction { filing := .single, head := p 66 true } = 19750 := by decide
theorem chart_mfj_4 :
    standardDeduction { filing := .mfj, head := p 66 true, spouse := some (p 66 true) } = 37900 := by decide
theorem chart_mfj_3 :
    standardDeduction { filing := .mfj, head := p 66 true, spouse := some (p 66) } = 36300 := by decide
theorem chart_qss_2 : standardDeduction { filing := .qss, head := p 66 true } = 34700 := by decide
theorem chart_hoh_1 : standardDeduction { filing := .hoh, head := p 66 } = 25625 := by decide
theorem chart_hoh_2 : standardDeduction { filing := .hoh, head := p 66 true } = 27625 := by decide
theorem chart_mfs_1 : standardDeduction { filing := .mfs, head := p 66, spouse := some (p 40) } = 17350 := by decide
-- Chart footnote: MFS may check the spouse's boxes if the spouse had no income and is nobody's dependent.
theorem chart_mfs_4 : standardDeduction { filing := .mfs, head := p 66 true, spouse := some (p 66 true) }
    { spouseNoIncomeNotDependent := true } = 22150 := by decide
theorem chart_mfs_2_without : standardDeduction { filing := .mfs, head := p 66, spouse := some (p 66) } = 17350 := by
  decide
-- Pub. 501 (2025) p. 23 "Persons not eligible": MFS whose spouse itemizes has a zero standard deduction.
theorem pub501_mfs_spouse_itemizes : standardDeduction { filing := .mfs, head := p 66, spouse := some (p 40) }
    { spouseItemizes := true } = 0 := by decide
-- Pub. 501 (2025) p. 24, Dependents Example 1: single, 16, wages $150, interest $780: $1,350.
theorem pub501_dep_ex1 : standardDeduction
    { filing := .single, head := p 16, canBeClaimedAsDependent := true, wages := 150, taxableInterest := 780 }
    = 1350 := by decide
-- Example 2: MFS dependent, 22, wages $3,800, interest $1,500, spouse does not itemize: $4,250.
theorem pub501_dep_ex2 : standardDeduction
    { filing := .mfs, head := p 22, spouse := some (p 22), canBeClaimedAsDependent := true, wages := 3800,
      taxableInterest := 1500 } = 4250 := by decide
-- Example 3: single dependent, 18 and blind, wages $2,900, interest $1,300: $3,350 + $2,000 = $5,350.
theorem pub501_dep_ex3 : standardDeduction
    { filing := .single, head := p 18 true, canBeClaimedAsDependent := true, wages := 2900, taxableInterest := 1300 }
    = 5350 := by decide
-- Example 4: single dependent, 18, wages $7,000, business loss $3,000, interest $500: $4,450.
theorem pub501_dep_ex4 : standardDeduction
    { filing := .single, head := p 18, canBeClaimedAsDependent := true, wages := 7000, seIncome := -3000,
      taxableInterest := 500 } = 4450 := by decide
-- Pub. 501 (2025) p. 24 "but not more than the regular standard deduction amount, generally $15,750".
theorem dep_capped : standardDeduction
    { filing := .single, head := p 20, canBeClaimedAsDependent := true, wages := 40000 } = 15750 := by decide

-- Schedule 1-A instructions 2025 p. 110 and Pub. 501 (2025): seniors' maximum $6,000 per person, $12,000 if both
-- spouses on a joint return qualify; reduced above $75,000 / $150,000 MAGI.
theorem senior_max_single : seniorDeduction { filing := .single, head := p 70 } 75000 = 6000 := by decide
theorem senior_max_joint :
    seniorDeduction { filing := .mfj, head := p 70, spouse := some (p 66) } 150000 = 12000 := by decide
theorem senior_one_spouse :
    seniorDeduction { filing := .mfj, head := p 70, spouse := some (p 60) } 100000 = 6000 := by decide
-- "If married, you must file jointly to claim this deduction" (Schedule 1-A Part V caution).
theorem senior_mfs_none : seniorDeduction { filing := .mfs, head := p 70, spouse := some (p 70) } 10000 = 0 := by
  decide
-- Schedule 1-A Part V caution: a valid SSN is required.
theorem senior_no_ssn : seniorDeduction { filing := .single, head := p 70 } 50000 { headSsn := false } = 0 := by
  decide

-- Schedule 1-A instructions 2025 p. 107-108, overtime Examples 1-5 (premium portion).
theorem ot_ex1 : premiumOfTimeAndHalf 15000 = 5000 := by decide        -- $15,000 overtime pay -> $5,000
theorem ot_ex2 : premiumOfRegularPay 10000 = 5000 := by decide         -- double time, $10,000 regular -> $5,000
theorem ot_ex3 : premiumOfRegularPay (20000 / 2) = 5000 := by decide   -- $20,000 at double time -> $5,000
theorem ot_ex4 : premiumOfTimeAndHalf 15000 = 5000 := by decide        -- law enforcement, 14-day period
theorem ot_ex5 : premiumOfTimeAndHalf 4500 = 1500 := by decide         -- compensatory time $4,500 -> $1,500
-- Schedule 1-A instructions p. 101: "$25,000 ... regardless of your filing status"; combined, not per spouse.
theorem tips_cap_joint : tipsDeduction { filing := .mfj, head := p 30, spouse := some (p 30), qualifiedTips := 40000 }
    100000 = 25000 := by decide
-- Schedule 1-A instructions p. 105 tip Examples 1–3 (net-income limit) give line-5 amounts $500, $1,000, $1,500;
-- with MAGI below $150,000 the deduction equals line 5.
theorem tips_ex3 : tipsDeduction { filing := .single, head := p 30, qualifiedTips := 1500 } 30000 = 1500 := by decide
-- Schedule 1-A line 15: overtime cap $12,500 ($25,000 MFJ).
theorem ot_cap_single : overtimeDeduction { filing := .hoh, head := p 30, qualifiedOvertime := 20000 } 90000 = 12500 :=
  by decide
theorem ot_cap_joint : overtimeDeduction { filing := .mfj, head := p 30, qualifiedOvertime := 30000 } 90000 = 25000 :=
  by decide
-- Schedule 1-A line 24: car loan interest cap $10,000.
theorem car_cap : carLoanDeduction { filing := .mfj, head := p 30, carLoanInterest := 12000 } 150000 = 10000 := by
  decide
-- Schedule A instructions 2025, line 5e: MAGI ≤ $500,000 ($250,000 MFS): smaller of line 5d or $40,000 ($20,000).
theorem salt_flat : saltDeduction { filing := .single, head := p 50, stateLocalTaxes := 55000 } 500000 = 40000 := by
  decide
theorem salt_flat_mfs : saltDeduction { filing := .mfs, head := p 50, stateLocalTaxes := 55000 } 250000 = 20000 := by
  decide
-- SALT worksheet line 1 "No" branch: line 5d ≤ $10,000 ($5,000 MFS) is never limited, at any MAGI.
theorem salt_small : saltDeduction { filing := .mfs, head := p 50, stateLocalTaxes := 5000 } 9000000 = 5000 := by
  decide
-- Pub. 526 (2025) p. 28–29, carryover Example 1: AGI $20,000, cash $9,500 + $1,000 carryover = $10,500 < $12,000.
theorem pub526_ex1 : charityDeduction { filing := .single, head := p 50, charitableCash := 10500 } 20000 = 10500 := by
  decide
theorem pub526_ex1_limit : roundDollar (60 * 20000) 100 = 12000 := by decide
-- Pub. 526 (2025) p. 29, Example 2: AGI $24,000, cash $6,000 "fully deductible ... less than $14,400".
theorem pub526_ex2 : charityDeduction { filing := .single, head := p 50, charitableCash := 6000 } 24000 = 6000 := by
  decide
theorem pub526_ex2_limit : roundDollar (60 * 24000) 100 = 14400 := by decide
-- Form 8995 instructions 2025 p. 2 (Exceptions 1–2): SSTB fully counted up to $197,300 / $394,600, phased out up to
-- $247,300 / $494,600.
theorem qbi_band_single : qbiThreshold .single + qbiRange .single = 247300 := by decide
theorem qbi_band_joint : qbiThreshold .mfj + qbiRange .mfj = 494600 := by decide
theorem qbi_sstb_end : qbiDeduction { filing := .single, head := p 40, qbi := 100000 } 247300 0 { qbiSstb := true } = 0 :=
  by decide
theorem qbi_below : qbiDeduction { filing := .single, head := p 40, qbi := 100000 } 197300 0 { qbiSstb := true } = 20000 :=
  by decide

end Tests

end TaxCode.Individual.B
