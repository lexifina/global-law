import TaxCode.Individual.B.Deductions

/-!
# Form 8995 (2025) against §199A below the threshold

Form text: Form 8995 (2025) "Qualified Business Income Deduction Simplified Computation" lines 2–5 and 10–15 (used when
taxable income before the deduction is at or below $197,300 / $394,600 joint). Lines 6–9 (REIT/PTP) and the loss
carryforwards (lines 3, 16, 17) are left at zero: the model has none.

Statute: §199A(a), (b)(1)–(3)(A) (wage limit "without regard to" below the threshold), via
`TaxCode.Individual.B.qbiDeduction`. One qualified business, not an SSTB (an SSTB is fully allowed below the
threshold anyway, §199A(d)(3)(A)), QBI ≥ 0.
-/

namespace TaxCode.Forms.Form8995
open TaxCode.Individual TaxCode.Individual.B

/-- Lines 2, 4 ("Combine lines 2 and 3. If zero or less, enter -0-"), 5 ("Multiply line 4 by 20%"), 10 (= line 5
with no REIT/PTP), 11 (taxable income before the deduction), 12 (net capital gain plus qualified dividends), 13
("Subtract line 12 from line 11. If zero or less, enter -0-"), 14 ("Multiply line 13 by 20%"), 15 ("the smaller of
line 10 or line 14"). Rounded to whole dollars as the model rounds each 20% amount. -/
def l15 (qbi l11 l12 : Int) : Int :=
  let l4 := max 0 qbi
  let l10 := roundDollar (20 * l4) 100
  let l13 := max 0 (l11 - l12)
  let l14 := roundDollar (20 * l13) 100
  min l10 l14

/-- **Line 15 is the §199A deduction for every QBI ≥ 0 and taxable income at or below the threshold.** -/
theorem l15_eq_statute (h : Household) (t g : Int) (hq : 0 ≤ h.qbi) (ht : t ≤ qbiThreshold h.filing) :
    l15 h.qbi t g = qbiDeduction h t g {} := by
  unfold l15 qbiDeduction qbiComponent qbiPhase
  simp only [Bool.false_eq_true, ↓reduceIte, ht]
  unfold roundDollar; omega

end TaxCode.Forms.Form8995

#print axioms TaxCode.Forms.Form8995.l15_eq_statute
