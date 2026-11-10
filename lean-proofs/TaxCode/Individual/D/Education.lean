import TaxCode.Individual.D.Basic

/-!
# §25A American opportunity and lifetime learning credits, tax year 2025

Source: 26 U.S.C. §25A (OLRC 119-138). Pub. L. 119-21 §70606 rewrote §25A(g)(1) (SSN requirement) only "for taxable
years beginning after December 31, 2025", so for 2025 the earlier TIN rule applies (not modelled). The MAGI limits of
§25A(d) ($80,000–$90,000; $160,000–$180,000 joint) are not indexed since Pub. L. 116-260 §104; Form 8863
instructions (2025) repeat them: "between $80,000 and $90,000 ($160,000 and $180,000 if you file a joint return)".

* §25A(b)(1): "100 percent of so much of the qualified tuition and related expenses ... as does not exceed $2,000,
  plus (B) 25 percent of such expenses so paid as exceeds $2,000 but does not exceed $4,000" — per eligible student.
* §25A(c)(1): Lifetime learning credit "20 percent of so much of the qualified tuition and related expenses ... as
  does not exceed $10,000" — per taxpayer.
* §25A(d)(1): each credit "reduced ... by the amount which bears the same ratio to each such credit ... as (A) the
  excess of MAGI over $80,000 ($160,000 joint) bears to (B) $10,000 ($20,000 joint)".
* §25A(i): "Forty percent" of the AOTC (after (d)) is refundable, except for a child to whom §1(g) applies.
* §25A(g)(6): married individuals must file jointly.
-/

namespace TaxCode.Individual.D
open TaxCode.Individual

/-- §25A(b)(1), one student. Form 8863 line 28 multiplies by 25%; rounded to the nearest dollar. -/
def aotcPerStudent (q : Int) : Int := min (pos q) 2000 + pctRound (pos (min q 4000 - 2000)) 2500

/-- Sum over eligible students (each list entry is one student's adjusted qualified expenses). -/
def aotcTentative (students : List Int) : Int := (students.map aotcPerStudent).sum

/-- §25A(c)(1). -/
def llcTentative (expenses : Int) : Int := pctRound (min (pos expenses) 10000) 2000

def eduLower (joint : Bool) : Int := if joint then 160000 else 80000
def eduRange (joint : Bool) : Int := if joint then 20000 else 10000

/-- §25A(d)(1) exactly (rounded once to the nearest dollar): credit × (lower + range − MAGI) / range, clamped. -/
def eduPhaseStatute (joint : Bool) (magi credit : Int) : Int :=
  roundDollar (credit * max 0 (min (eduLower joint + eduRange joint - magi) (eduRange joint))) (eduRange joint)

/-- Form 8863 lines 2–7 (and 11–17): "divide line 5 by line 6. Enter the result as a decimal (rounded to at least
three places)" — we round to exactly three places — then multiply the credit by that decimal. -/
def eduPhaseForm (joint : Bool) (magi credit : Int) : Int :=
  let f := roundDollar (1000 * max 0 (min (eduLower joint + eduRange joint - magi) (eduRange joint))) (eduRange joint)
  roundDollar (credit * f) 1000

structure EduResult where
  aotcRefundable : Int
  aotcNonrefundable : Int
  llc : Int
  deriving Repr, DecidableEq

/-- Both credits for 2025. `kiddie` is §25A(i)'s last sentence (a child to whom §1(g) applies: no refundable part).
Refundable part = 40% of the AOTC after the phase-out (Form 8863 line 8), rest nonrefundable. -/
def education2025 (f : Filing) (magi : Int) (aotcStudents : List Int) (llcExpenses : Int) (kiddie : Bool := false) :
    EduResult :=
  if f = .mfs then ⟨0, 0, 0⟩ else
  let j := f == .mfj
  let aotc := eduPhaseStatute j magi (aotcTentative aotcStudents)
  let refundable := if kiddie then 0 else pctRound aotc 4000
  ⟨refundable, aotc - refundable, eduPhaseStatute j magi (llcTentative llcExpenses)⟩

/-! ## Tests -/

-- §25A(b)(1): $4,000 of expenses gives the maximum $2,500; $2,000 gives $2,000.
#guard aotcPerStudent 4000 = 2500 ∧ aotcPerStudent 2000 = 2000 ∧ aotcPerStudent 10000 = 2500 ∧ aotcPerStudent 3000 = 2250
-- Form 8863 instructions (2025), "Example. You paid $8,000 tuition ... claimed a lifetime learning credit of $1,600
-- ($8,000 qualified education expense paid x 20% (0.20)). ... You must refigure your 2025 lifetime learning credit
-- using $6,600 ... The refigured credit is $1,320 and your tax liability increased by $280."
#guard llcTentative 8000 = 1600 ∧ llcTentative 6600 = 1320 ∧ llcTentative 8000 - llcTentative 6600 = 280
-- Form 8863 instructions (2025): no credit if MAGI is "$90,000 or more ($180,000 or more if you file a joint
-- return)"; full credit at or below $80,000 / $160,000.
#guard eduPhaseStatute false 90000 2500 = 0 ∧ eduPhaseStatute true 180000 2500 = 0 ∧
  eduPhaseStatute false 80000 2500 = 2500 ∧ eduPhaseStatute true 160000 2500 = 2500
#guard eduPhaseStatute false 85000 2500 = 1250 ∧ eduPhaseForm false 85000 2500 = 1250
-- 40% refundable: full AOTC $2,500 → $1,000 refundable, $1,500 nonrefundable.
#guard education2025 .single 50000 [4000] 0 = ⟨1000, 1500, 0⟩
#guard education2025 .mfs 50000 [4000] 0 = ⟨0, 0, 0⟩

/-! ## Properties -/

theorem aotcPerStudent_bounds (q : Int) : 0 ≤ aotcPerStudent q ∧ aotcPerStudent q ≤ 2500 := by
  unfold aotcPerStudent pctRound roundDollar pos; omega

/-- The phase-out keeps the credit between 0 and the tentative credit. -/
theorem eduPhase_bounds (j : Bool) (magi C : Int) (hC : 0 ≤ C) :
    0 ≤ eduPhaseStatute j magi C ∧ eduPhaseStatute j magi C ≤ C := by
  unfold eduPhaseStatute
  generalize hR : eduRange j = R
  generalize eduLower j = L
  have hR0 : 0 < R := by rw [← hR]; unfold eduRange; split <;> omega
  generalize ht : max 0 (min (L + R - magi) R) = t
  have h0 : 0 ≤ t := by omega
  have h1 : t ≤ R := by omega
  have a1 : 0 ≤ C * t := Int.mul_nonneg hC h0
  have a2 : C * t ≤ C * R := Int.mul_le_mul_of_nonneg_left h1 hC
  unfold roundDollar
  constructor
  · exact Int.ediv_nonneg (by omega) (by omega)
  · have k : (2 * (C * t) + R) / (2 * R) < C + 1 := by
      apply (Int.ediv_lt_iff_lt_mul (by omega)).2
      rw [Int.add_mul, Int.one_mul, Int.mul_left_comm C 2 R]
      omega
    omega

/-- **No cliff.** For any credit up to the range ($10,000 single, $20,000 joint: four or eight full AOTCs), one more
dollar of MAGI never costs more than one dollar of credit, and never raises it. -/
theorem eduPhase_step (j : Bool) (magi C : Int) (hC : 0 ≤ C) (hCr : C ≤ eduRange j) :
    0 ≤ eduPhaseStatute j magi C - eduPhaseStatute j (magi + 1) C ∧
    eduPhaseStatute j magi C - eduPhaseStatute j (magi + 1) C ≤ 1 := by
  unfold eduPhaseStatute
  generalize hR : eduRange j = R at *
  generalize hL : eduLower j = L
  have hR0 : 0 < R := by rw [← hR]; unfold eduRange; split <;> omega
  -- the clamped multiplier drops by 0 or 1
  generalize ht : max 0 (min (L + R - magi) R) = t
  generalize ht' : max 0 (min (L + R - (magi + 1)) R) = t'
  have hd : t' = t ∨ t' + 1 = t := by omega
  rcases hd with h | h
  · rw [h]; omega
  · rw [← h, Int.mul_add, Int.mul_one]
    unfold roundDollar
    have : 0 ≤ C * t' := Int.mul_nonneg hC (by omega)
    constructor
    · exact Int.sub_nonneg_of_le (Int.ediv_le_ediv (by omega) (by omega))
    · have := Int.add_mul_ediv_right (2 * (C * t') + R) 1 (show 2 * R ≠ 0 by omega)
      have h3 : (2 * (C * t' + C) + R) / (2 * R) ≤ (2 * (C * t') + R + 1 * (2 * R)) / (2 * R) :=
        Int.ediv_le_ediv (by omega) (by omega)
      omega

/-- Form 8863's three-decimal rounding moves a single student's full $2,500 AOTC by at most $2 from the statute's
exact ratio (single and joint), e.g. $2,498 instead of $2,496 at MAGI $80,015. -/
theorem form_vs_statute_aotc (j : Bool) (magi : Int) :
    eduPhaseForm j magi 2500 - eduPhaseStatute j magi 2500 ≤ 2 ∧
    eduPhaseStatute j magi 2500 - eduPhaseForm j magi 2500 ≤ 2 := by
  unfold eduPhaseForm eduPhaseStatute eduLower eduRange roundDollar
  cases j <;> simp only [Bool.false_eq_true, ↓reduceIte] <;> omega

theorem form_vs_statute_example : eduPhaseStatute false 80015 2500 = 2496 ∧ eduPhaseForm false 80015 2500 = 2498 := by
  decide

/-- §25A(i)'s §1(g) exception is a status cliff: the same student, same expenses, loses the $1,000 refundable part
(it becomes nonrefundable, worth nothing without tax). -/
theorem kiddie_cliff :
    (education2025 .single 20000 [4000] 0 false).aotcRefundable = 1000 ∧
    (education2025 .single 20000 [4000] 0 true).aotcRefundable = 0 := by decide

end TaxCode.Individual.D
