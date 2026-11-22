import TaxCode.Individual.D.Basic

/-!
# §21 Child and dependent care credit, tax year 2025 (and the 2026 rule)

Source: 26 U.S.C. §21 (OLRC 119-138). The OLRC text of §21(a)(2) is the 2025 Act's version (50%, stepping to 35%,
then to 20%), but Pub. L. 119-21 §70405(b): "shall apply to taxable years beginning after December 31, 2025". For
2025 the prior text applies, quoted in the OLRC amendment note: "35 percent reduced (but not below 20 percent) by 1
percentage point for each $2,000 (or fraction thereof) by which the taxpayer's adjusted gross income for the taxable
year exceeds $15,000." Neither text is indexed. Dollar limits §21(c): $3,000 (one qualifying individual) / $6,000
(two or more), reduced by §129 exclusions; earned-income limit §21(d).

Rates are whole percentage points here (the statute steps by whole points).
-/

namespace TaxCode.Individual.D
open TaxCode.Individual

/-- §21(a)(2) as in force for 2025. -/
def cdccPercent2025 (agi : Int) : Int := max 20 (35 - ceilDiv (pos (agi - 15000)) 2000)

/-- §21(a)(2) as amended by Pub. L. 119-21 §70405 (2026 on): "50 percent— (A) reduced (but not below 35 percent) by 1
percentage point for each $2,000 or fraction thereof by which ... adjusted gross income ... exceeds $15,000, and (B)
further reduced (but not below 20 percent) by 1 percentage point for each $2,000 ($4,000 in the case of a joint
return) or fraction thereof by which ... adjusted gross income ... exceeds $75,000 ($150,000 in the case of a joint
return)." -/
def cdccPercent2026 (joint : Bool) (agi : Int) : Int :=
  let a := max 35 (50 - ceilDiv (pos (agi - 15000)) 2000)
  max 20 (a - ceilDiv (pos (agi - (if joint then 150000 else 75000))) (if joint then 4000 else 2000))

/-- §21(c): "$3,000 if there is 1 qualifying individual", "$6,000 if there are 2 or more", "reduced by the aggregate
amount excludable from gross income under section 129". -/
def cdccDollarLimit (qualifying : Nat) (excluded129 : Int) : Int :=
  pos ((if qualifying = 0 then 0 else if qualifying = 1 then 3000 else 6000) - pos excluded129)

/-- §21(c) and (d)(1): expenses taken into account. Married: "the lesser of such individual's earned income or the
earned income of his spouse" (§21(d)(2) deemed income for a student/incapable spouse is folded into `earnedSpouse`). -/
def cdccExpenses (qualifying : Nat) (expenses excluded129 earnedHead earnedSpouse : Int) (married : Bool) : Int :=
  pos (min (min expenses (cdccDollarLimit qualifying excluded129))
    (if married then min earnedHead earnedSpouse else earnedHead))

/-- The 2025 credit. §21(e)(2): married taxpayers must file jointly (the living-apart exception of §21(e)(4) is not
modelled). Form 2441 line 11 multiplies by the decimal; we round to the nearest dollar. -/
def cdcc2025 (f : Filing) (qualifying : Nat) (expenses excluded129 earnedHead earnedSpouse agi : Int) : Int :=
  if f = .mfs then 0 else
  roundDollar (cdccExpenses qualifying expenses excluded129 earnedHead earnedSpouse (f == .mfj) *
    cdccPercent2025 agi) 100

def cdcc2026 (f : Filing) (qualifying : Nat) (expenses excluded129 earnedHead earnedSpouse agi : Int) : Int :=
  if f = .mfs then 0 else
  roundDollar (cdccExpenses qualifying expenses excluded129 earnedHead earnedSpouse (f == .mfj) *
    cdccPercent2026 (f == .mfj) agi) 100

/-- §21(b)(1)(A)/(B): a dependent under 13, or one incapable of self-care living with the taxpayer more than half
the year. (A spouse incapable of self-care, §21(b)(1)(C), is not in `Household`.) -/
def isCareIndividual (d : Dependent) : Bool := d.age < 13 || (d.disabled && d.monthsWithTaxpayer > 6)

def careIndividuals (h : Household) : Nat := (h.dependents.filter isCareIndividual).length

/-! ## Tests -/

-- Form 2441 instructions (2025), Worksheet A line 12 table ("2024 adjusted gross income ... decimal amount", the
-- same §21(a)(2) text): "$0 — $15,000 0.35", "15,000 — 17,000 0.34", "17,000 — 19,000 0.33", ... "41,000 — 43,000
-- 0.21", "43,000 — No limit 0.20" (each band "Over ... But not over").
#guard cdccPercent2025 0 = 35 ∧ cdccPercent2025 15000 = 35 ∧ cdccPercent2025 15001 = 34 ∧
  cdccPercent2025 17000 = 34 ∧ cdccPercent2025 17001 = 33 ∧ cdccPercent2025 19000 = 33
#guard (List.range 14).all fun i =>
  let lo : Int := 15000 + 2000 * i
  cdccPercent2025 (lo + 1) = 34 - i ∧ cdccPercent2025 (lo + 2000) = 34 - i
#guard cdccPercent2025 41001 = 21 ∧ cdccPercent2025 43000 = 21 ∧ cdccPercent2025 43001 = 20 ∧
  cdccPercent2025 1000000 = 20
-- §21(c): one child, $5,000 paid, AGI $50,000, both spouses working: $3,000 × 20% = $600.
#guard cdcc2025 .mfj 1 5000 0 60000 40000 100000 = 600
-- Form 2441 instructions (2025) Credit Limit Worksheet: the credit is limited to tax minus the foreign tax credit;
-- that ordering is in `Ordering.lean`.

/-! ## Properties -/

/-- The 2025 percentage stays between 20 and 35 and never rises with AGI. -/
theorem cdcc2025_pct_bounds (agi : Int) : 20 ≤ cdccPercent2025 agi ∧ cdccPercent2025 agi ≤ 35 := by
  unfold cdccPercent2025 ceilDiv pos; omega

theorem cdcc2025_pct_antitone (agi : Int) : cdccPercent2025 (agi + 1) ≤ cdccPercent2025 agi := by
  unfold cdccPercent2025 ceilDiv pos; omega

theorem cdcc2026_pct_bounds (j : Bool) (agi : Int) : 20 ≤ cdccPercent2026 j agi ∧ cdccPercent2026 j agi ≤ 50 := by
  unfold cdccPercent2026 ceilDiv pos; cases j <;> simp <;> omega

theorem cdcc2026_pct_antitone (j : Bool) (agi : Int) : cdccPercent2026 j (agi + 1) ≤ cdccPercent2026 j agi := by
  unfold cdccPercent2026 ceilDiv pos; cases j <;> simp <;> omega

/-- The 2025 Act only raises the rate: for every AGI and filing status, the 2026 percentage is at least the 2025
one (and 15 points higher at low incomes). -/
theorem cdcc2026_ge_2025 (j : Bool) (agi : Int) : cdccPercent2025 agi ≤ cdccPercent2026 j agi := by
  unfold cdccPercent2025 cdccPercent2026 ceilDiv pos; cases j <;> simp <;> omega

/-- The credit never exceeds 35% of $6,000 = $2,100 (2025), and is never negative. -/
theorem cdcc2025_bounds (f : Filing) (n : Nat) (e x eh es agi : Int) :
    0 ≤ cdcc2025 f n e x eh es agi ∧ cdcc2025 f n e x eh es agi ≤ 2100 := by
  have hp := cdcc2025_pct_bounds agi
  unfold cdcc2025
  split
  · omega
  · have h0 : 0 ≤ cdccExpenses n e x eh es (f == .mfj) := pos_nonneg _
    have h1 : cdccExpenses n e x eh es (f == .mfj) ≤ 6000 := by
      unfold cdccExpenses cdccDollarLimit pos; split <;> split <;> omega
    have : cdccExpenses n e x eh es (f == .mfj) * cdccPercent2025 agi ≤ 6000 * 35 :=
      Int.mul_le_mul h1 hp.2 (by omega) (by omega)
    have : 0 ≤ cdccExpenses n e x eh es (f == .mfj) * cdccPercent2025 agi := Int.mul_nonneg h0 (by omega)
    unfold roundDollar; omega

/-- **Notch.** Each $2,000 step "or fraction thereof" means the first dollar of a step costs a full point: with two
children and $6,000 of expenses, AGI $15,001 instead of $15,000 costs $60 of credit (2025). -/
theorem cdcc2025_notch :
    cdcc2025 .mfj 2 6000 0 50000 50000 15000 = 2100 ∧ cdcc2025 .mfj 2 6000 0 50000 50000 15001 = 2040 := by
  decide

/-- One dollar of AGI never costs more than one percentage point of $6,000, i.e. $60. -/
theorem cdcc2025_step_le_60 (f : Filing) (n : Nat) (e x eh es agi : Int) :
    cdcc2025 f n e x eh es agi - cdcc2025 f n e x eh es (agi + 1) ≤ 60 := by
  have hp := cdcc2025_pct_antitone agi
  have hq : cdccPercent2025 agi - cdccPercent2025 (agi + 1) ≤ 1 := by unfold cdccPercent2025 ceilDiv pos; omega
  unfold cdcc2025
  split
  · omega
  · generalize hE : cdccExpenses n e x eh es (f == .mfj) = E
    have h0 : 0 ≤ E := hE ▸ pos_nonneg _
    have h1 : E ≤ 6000 := by
      rw [← hE]; unfold cdccExpenses cdccDollarLimit pos; split <;> split <;> omega
    generalize cdccPercent2025 agi = p at *
    generalize cdccPercent2025 (agi + 1) = q at *
    have : E * p - E * q ≤ 6000 := by
      rw [← Int.mul_sub]
      by_cases hpq : p - q = 0
      · rw [hpq, Int.mul_zero]; omega
      · have : p - q = 1 := by omega
        rw [this, Int.mul_one]; exact h1
    unfold roundDollar; omega

/-- The 2026 rule still steps: $15,001 instead of $15,000 costs one point (50% → 49%) = $60 on $6,000. -/
theorem cdcc2026_notch :
    cdcc2026 .mfj 2 6000 0 50000 50000 15000 = 3000 ∧ cdcc2026 .mfj 2 6000 0 50000 50000 15001 = 2940 := by
  decide

end TaxCode.Individual.D
