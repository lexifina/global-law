import TaxCode.Individual.D.Basic

/-!
# §24 Child tax credit, tax year 2025 (as amended by Pub. L. 119-21 §70104)

Source: 26 U.S.C. §24, OLRC release point 119-138. Pub. L. 119-21 §70104(f): the 2025 Act's amendments to §24 "shall
apply to taxable years beginning after December 31, 2024", so for 2025:
* §24(h)(2): "$2,200" per qualifying child (substituted for $2,000 by §70104(a)(2));
* §24(h)(4)(A): $500 for each other dependent;
* §24(h)(3): threshold $400,000 joint return, $200,000 any other case;
* §24(b)(1): reduced "by $50 for each $1,000 (or fraction thereof)" of MAGI over the threshold;
* §24(h)(5) and (i)(1): refundable portion at most $1,400, indexed from 2017 and rounded down to $100: $1,700 for
  2025 (Rev. Proc. 2024-40 §3.05);
* §24(h)(6): earned-income threshold $2,500 for §24(d)(1)(B)(i) (15 percent);
* §24(h)(7) as rewritten by §70104(b): an SSN is needed for the child AND for the taxpayer (on a joint return, at
  least one spouse). A child kept out by (h)(7) is an "other dependent" under (h)(4)(C).

The statute and Schedule 8812 differ on the refundable cap (see `actcForm`, `form_exceeds_statute`).
-/

namespace TaxCode.Individual.D
open TaxCode.Individual

/-- §24(h)(2): "$2,200" per qualifying child (2025). -/
def ctcPerChild : Int := 2200
/-- §24(h)(4)(A): "increased by $500 for each dependent" other than a qualifying child. -/
def odcPerDependent : Int := 500
/-- §24(h)(5) as indexed by §24(i)(1),(3): $1,700 (Rev. Proc. 2024-40 §3.05). -/
def actcPerChildCap : Int := 1700
/-- §24(h)(6): "$2,500" substituted for "$3,000" in §24(d)(1)(B)(i). -/
def actcEarnedFloor : Int := 2500
/-- §24(d)(1)(B)(i): "15 percent". -/
def actcRateBp : Int := 1500

/-- §24(h)(3): "$400,000 in the case of a joint return ($200,000 in any other case)". A qualifying surviving spouse
files jointly with nobody, so gets $200,000. -/
def ctcThreshold : Filing → Int
  | .mfj => 400000
  | _ => 200000

/-- §24(b)(1): "$50 for each $1,000 (or fraction thereof) by which the taxpayer's modified adjusted gross income
exceeds the threshold amount". -/
def ctcReduction (f : Filing) (magi : Int) : Int := 50 * ceilDiv (pos (magi - ctcThreshold f)) 1000

/-- Who counts for what, after the SSN rules. -/
structure CtcCounts where
  children : Int  -- qualifying children (§24(c)) for whom the $2,200 is allowed
  others : Int    -- dependents for whom only the $500 of §24(h)(4) is allowed
  deriving Repr, DecidableEq

/-- §24(h)(7)(A) and (h)(4)(C). Without the taxpayer's SSN (`taxpayerSSN = false`; on a joint return, neither spouse
has one) no child gets the $2,200, and every child "with respect to whom a credit is not allowed ... by reason of
paragraph (7)" is treated as an other dependent. The same happens to a child without an SSN. -/
def ctcCounts (taxpayerSSN : Bool) (childrenWithSSN childrenWithoutSSN otherDependents : Nat) : CtcCounts :=
  if taxpayerSSN then ⟨childrenWithSSN, childrenWithoutSSN + otherDependents⟩
  else ⟨0, childrenWithSSN + childrenWithoutSSN + otherDependents⟩

/-- §24(a) with (h)(2) and (h)(4): the credit before the phase-out. -/
def ctcTentative (c : CtcCounts) : Int := ctcPerChild * c.children + odcPerDependent * c.others

/-- §24(b)(1): the credit after the phase-out ("but not below zero"). This is Schedule 8812 line 12. -/
def ctcAfterPhaseout (f : Filing) (magi : Int) (c : CtcCounts) : Int :=
  pos (ctcTentative c - ctcReduction f magi)

/-- §24(d)(1)(A) as limited by §24(h)(5): "the credit which would be allowed under this section without regard to
this subsection and the limitation under section 26(a)", applied "without regard to paragraph (4)" (no $500 credits)
and at most $1,700 per qualifying child. -/
def actcCapA (f : Filing) (magi : Int) (c : CtcCounts) : Int :=
  min (pos (ctcPerChild * c.children - ctcReduction f magi)) (actcPerChildCap * c.children)

/-- §24(d)(1)(B): the amount by which the §26(a) limitation would be increased: the greater of (i) 15% of earned
income over $2,500 and (ii) for 3 or more qualifying children, social security taxes over the earned income credit.
Rounded to the nearest dollar as Schedule 8812 line 20 is. -/
def actcEarnedAmount (c : CtcCounts) (earned ssTaxes eic : Int) : Int :=
  max (pctRound (pos (earned - actcEarnedFloor)) actcRateBp) (if 3 ≤ c.children then pos (ssTaxes - eic) else 0)

/-- §24(a) as limited by §26(a): the nonrefundable part used, given the tax left after the credits the forms apply
first (Credit Limit Worksheet A, line 3). -/
def ctcNonrefundable (f : Filing) (magi : Int) (c : CtcCounts) (taxLeft : Int) : Int :=
  min (ctcAfterPhaseout f magi c) (pos taxLeft)

/-- §24(d)(1) by the statute: the lesser of (A) [capped by (h)(5)] and (B), where (B) — the increase in the credits
allowed if the §26(a) limitation were raised by the earned-income amount — is at most the credit left unused.
`foreign911` is §24(d)(3): no refundable credit for a taxpayer who elects §911. -/
def actcStatute (f : Filing) (magi : Int) (c : CtcCounts) (taxLeft earned ssTaxes eic : Int)
    (foreign911 : Bool := false) : Int :=
  if foreign911 then 0 else
  min (actcCapA f magi c)
    (min (actcEarnedAmount c earned ssTaxes eic) (ctcAfterPhaseout f magi c - ctcNonrefundable f magi c taxLeft))

/-- Schedule 8812 (2025) Part II-A as the instructions describe it (Credit Limit Worksheet B lines 1–2, 12–13; Schedule
8812 lines 16a, 16b, 17, 27): the cap is "number of qualifying children ... × $1,700" against the UNUSED COMBINED
credit (line 12 minus line 14), with no separate cap by the child-only credit after the phase-out. -/
def actcForm (f : Filing) (magi : Int) (c : CtcCounts) (taxLeft earned ssTaxes eic : Int) : Int :=
  min (min (ctcAfterPhaseout f magi c - ctcNonrefundable f magi c taxLeft) (actcPerChildCap * c.children))
    (actcEarnedAmount c earned ssTaxes eic)

/-! ## From a household -/

/-- A dependent who is a §24(c) qualifying child: under 17 at the end of the year (§24(c)(1)) and a §152(c) qualifying
child (lived with the taxpayer more than half the year; the age test of §152(c)(3) is implied by being under 17). -/
def isCtcChild (d : Dependent) : Bool := d.age < 17 && d.monthsWithTaxpayer > 6

/-- Counts from the household's dependents. `Household` has no field for the taxpayer's own SSN, so it is an
argument. -/
def householdCtcCounts (h : Household) (taxpayerSSN : Bool := true) : CtcCounts :=
  let kids := h.dependents.filter isCtcChild
  let withSSN := (kids.filter (·.ssn)).length
  ctcCounts taxpayerSSN withSSN (kids.length - withSSN) (h.dependents.length - kids.length)

/-! ## Tests -/

-- Rev. Proc. 2024-40 §3.05: "the amount used in § 24(d)(1)(A) ... is $1,700"; Schedule 8812 instructions (2025):
-- "CTC maximum is $2,200 per qualifying child", income limits "$400,000" joint, "$200,000" all others.
#guard actcPerChildCap = 1700 ∧ ctcPerChild = 2200
#guard ctcThreshold .mfj = 400000 ∧ ctcThreshold .single = 200000 ∧ ctcThreshold .hoh = 200000
-- Credit Limit Worksheet B line 6 (2025 instructions): "Check whether line 2 is $5,100 or more" — three children.
#guard actcPerChildCap * 3 = 5100
-- Schedule 8812 instructions (2025), Example 1: a child who turned 17 on 30 Dec 2025 is not a CTC child; she is
-- still a dependent, so she gets the $500 credit for other dependents.
#guard householdCtcCounts { filing := .single, head := ⟨40, false⟩, dependents := [{ age := 17 }] } = ⟨0, 1⟩
#guard ctcTentative (householdCtcCounts { filing := .single, head := ⟨40, false⟩, dependents := [{ age := 17 }] })
  = 500
-- Instructions (2025): "A qualifying child without a valid SSN cannot be used for the CTC or ACTC" — ODC instead.
#guard householdCtcCounts { filing := .mfj, head := ⟨40, false⟩, dependents := [{ age := 5, ssn := false }] } = ⟨0, 1⟩
-- §24(b)(1) "or fraction thereof": $1 over the threshold costs a full $50.
#guard ctcReduction .single 200000 = 0 ∧ ctcReduction .single 200001 = 50 ∧ ctcReduction .single 201000 = 50
  ∧ ctcReduction .single 201001 = 100
-- One child, single: fully phased out once 44 steps are used, i.e. above $243,000.
#guard ctcAfterPhaseout .single 243000 ⟨1, 0⟩ = 50 ∧ ctcAfterPhaseout .single 243001 ⟨1, 0⟩ = 0

/-! ## Properties -/

/-- The phase-out never pushes the credit below zero nor above the tentative credit. -/
theorem ctc_bounds (f : Filing) (magi : Int) (c : CtcCounts) (h1 : 0 ≤ c.children) (h2 : 0 ≤ c.others) :
    0 ≤ ctcAfterPhaseout f magi c ∧ ctcAfterPhaseout f magi c ≤ ctcTentative c := by
  have : 0 ≤ ctcReduction f magi := by unfold ctcReduction ceilDiv pos; omega
  unfold ctcAfterPhaseout ctcTentative ctcPerChild odcPerDependent pos; omega

theorem ctcReduction_mono (f : Filing) (m : Int) : ctcReduction f m ≤ ctcReduction f (m + 1) := by
  unfold ctcReduction ceilDiv pos; omega

/-- Monotone: more MAGI never increases the credit. -/
theorem ctc_antitone (f : Filing) (m : Int) (c : CtcCounts) :
    ctcAfterPhaseout f (m + 1) c ≤ ctcAfterPhaseout f m c := by
  have := ctcReduction_mono f m
  unfold ctcAfterPhaseout pos; omega

/-- **Notch.** One dollar of MAGI costs at most $50 of credit, and the very first dollar over the threshold costs
exactly $50 whenever $50 of credit is left: a $1 raise loses $50 (a 5,000% marginal rate on that dollar). -/
theorem ctc_step_le_50 (f : Filing) (m : Int) (c : CtcCounts) :
    ctcAfterPhaseout f m c - ctcAfterPhaseout f (m + 1) c ≤ 50 := by
  unfold ctcAfterPhaseout ctcReduction ceilDiv pos; omega

theorem ctc_notch_at_threshold (f : Filing) (c : CtcCounts) (h : 50 ≤ ctcTentative c) :
    ctcAfterPhaseout f (ctcThreshold f) c - ctcAfterPhaseout f (ctcThreshold f + 1) c = 50 := by
  unfold ctcAfterPhaseout ctcReduction ceilDiv pos; omega

/-- The refundable part never exceeds $1,700 per qualifying child, and is never negative. -/
theorem actc_le_cap (f : Filing) (magi : Int) (c : CtcCounts) (t e s k : Int) (b : Bool) (hc : 0 ≤ c.children) :
    0 ≤ actcStatute f magi c t e s k b ∧ actcStatute f magi c t e s k b ≤ actcPerChildCap * c.children := by
  unfold actcStatute actcCapA actcEarnedAmount ctcNonrefundable ctcAfterPhaseout pctRound roundDollar pos
    actcPerChildCap
  split <;> omega

/-- **The split never exceeds the credit.** Nonrefundable part plus refundable part is at most the credit after
the phase-out, hence at most $2,200 per child plus $500 per other dependent. Same for the form's version. -/
theorem ctc_split_le (f : Filing) (magi : Int) (c : CtcCounts) (t e s k : Int) (b : Bool)
    (h1 : 0 ≤ c.children) (h2 : 0 ≤ c.others) :
    ctcNonrefundable f magi c t + actcStatute f magi c t e s k b ≤ ctcAfterPhaseout f magi c ∧
    ctcNonrefundable f magi c t + actcForm f magi c t e s k ≤ ctcAfterPhaseout f magi c ∧
    ctcAfterPhaseout f magi c ≤ ctcPerChild * c.children + odcPerDependent * c.others := by
  have hb := ctc_bounds f magi c h1 h2
  unfold ctcTentative at hb
  unfold actcStatute actcForm actcCapA actcEarnedAmount ctcNonrefundable pctRound roundDollar pos
    ctcPerChild odcPerDependent actcPerChildCap at *
  split <;> omega

/-- The statute's refundable credit is also capped by the CHILD credit after the phase-out (§24(h)(5): (d)(1)(A)
"applied without regard to paragraph (4)"). -/
theorem actc_le_child_credit (f : Filing) (magi : Int) (c : CtcCounts) (t e s k : Int) (b : Bool) :
    actcStatute f magi c t e s k b ≤ pos (ctcPerChild * c.children - ctcReduction f magi) := by
  unfold actcStatute actcCapA pos; split <;> omega

/-- The form never gives less than the statute (absent §911) ... -/
theorem form_ge_statute (f : Filing) (magi : Int) (c : CtcCounts) (t e s k : Int) :
    actcStatute f magi c t e s k false ≤ actcForm f magi c t e s k := by
  unfold actcStatute actcForm actcCapA; simp only [Bool.false_eq_true, ↓reduceIte]; unfold pos; omega

/-- ... and can give more. Single, one qualifying child and one other dependent, MAGI $240,000 (reduction $2,000),
no tax left after a foreign tax credit, earned income $240,000. Statute: the child credit after the phase-out is
$200, so the refundable credit is $200. Schedule 8812: unused combined credit $700 against a $1,700 cap: $700. -/
theorem form_exceeds_statute :
    actcStatute .single 240000 ⟨1, 1⟩ 0 240000 0 0 = 200 ∧ actcForm .single 240000 ⟨1, 1⟩ 0 240000 0 0 = 700 := by
  decide

/-- §24(h)(7)(A)(i): without the taxpayer's SSN, two children are worth $1,000 instead of $4,400. -/
theorem taxpayer_ssn_cost :
    ctcTentative (ctcCounts true 2 0 0) = 4400 ∧ ctcTentative (ctcCounts false 2 0 0) = 1000 := by decide

/-- (Review) The statute and Schedule 8812 agree whenever there is no other dependent: the departure in
`form_exceeds_statute` comes only from the $500 credits of §24(h)(4), which (h)(5) excludes from (d)(1)(A) and the
form does not. -/
theorem actc_statute_eq_form_no_others (f : Filing) (magi : Int) (n : Int) (t e s k : Int) :
    actcStatute f magi ⟨n, 0⟩ t e s k false = actcForm f magi ⟨n, 0⟩ t e s k := by
  unfold actcStatute actcForm actcCapA ctcNonrefundable ctcAfterPhaseout ctcTentative odcPerDependent pos
  simp only [Bool.false_eq_true, ↓reduceIte]
  omega

/-- (Review) A lower bound, so that a function returning 0 cannot satisfy the ACTC theorems: with no tax left and an
earned-income amount at least the (d)(1)(A) cap, the whole cap is refundable. -/
theorem actc_full (f : Filing) (magi : Int) (c : CtcCounts) (t e s k : Int) (h1 : 0 ≤ c.children) (h2 : 0 ≤ c.others)
    (ht : t ≤ 0) (he : actcCapA f magi c ≤ actcEarnedAmount c e s k) :
    actcStatute f magi c t e s k false = actcCapA f magi c := by
  have hr : 0 ≤ ctcReduction f magi := by unfold ctcReduction ceilDiv pos; omega
  unfold actcStatute ctcNonrefundable ctcAfterPhaseout ctcTentative
  simp only [Bool.false_eq_true, ↓reduceIte]
  generalize actcEarnedAmount c e s k = X at *
  unfold actcCapA at *
  generalize ctcReduction f magi = R at *
  unfold odcPerDependent ctcPerChild actcPerChildCap pos at *
  omega

end TaxCode.Individual.D
