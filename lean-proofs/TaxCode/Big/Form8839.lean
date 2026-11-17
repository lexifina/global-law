/-!
# Form 8839 (2025) lines 11a-13: the refundable $5,000, per child (form) or per taxpayer (statute)

Form text (Form 8839 (2025), created 9/2/25, p. 1): line 11a "Subtract line 10 from line 6" (one column per child);
11b "Enter the smaller of the amount on line 11a or $5,000" (per column); 11c "Add the amounts on line 11b"; 12 "Add
the amounts on line 11a"; 13 "Refundable adoption credit. Enter the amount from line 11(c)"; 14 "Subtract line 13
from line 12". Instructions for Form 8839 (2025), p. 1 What's New: "The amount of the refundable credit portion is
determined separately for each eligible child"; p. 7 Line 13: "The refundable credit amount is determined per
eligible child. The amounts per child are then added together". The 2026 draft instructions (Nov 9, 2026, p. 1) keep
this with $5,120.

Statute: §23(a)(1) "there shall be allowed as a credit ... the amount of the qualified adoption expenses paid or
incurred by the taxpayer"; §23(a)(4) (Pub. L. 119-21 §70402): "So much of the credit allowed under paragraph (1) as
does not exceed $5,000 shall be treated as a credit allowed under subpart C". The per-child limits are in (a)(3) and
(b)(1) ("with respect to the adoption of a child"); (a)(4) has no such words. §23(c)(1): the nonrefundable part over
the §26 limit carries forward five years.

Model: three columns (the form's three; more children use a continuation sheet), each line 11a amount ≥ 0.
-/

namespace TaxCode.Big.Form8839

def formRefund (a b c : Int) : Int := min a 5000 + min b 5000 + min c 5000
def statRefund (a b c : Int) : Int := min (a + b + c) 5000

theorem gap_nonneg (a b c : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    0 ≤ formRefund a b c - statRefund a b c := by unfold formRefund statRefund; omega

/-- **Exact affected set**: the form refunds more iff at least two children have a positive line 11a and the
total is over $5,000. -/
theorem gap_pos_iff (a b c : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    0 < formRefund a b c - statRefund a b c ↔
      5000 < a + b + c ∧ ((0 < a ∧ 0 < b) ∨ (0 < a ∧ 0 < c) ∨ (0 < b ∧ 0 < c)) := by
  unfold formRefund statRefund; omega

/-- Max: $5,000 per child after the first ($10,000 on one three-child form). -/
theorem gap_le (a b c : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    formRefund a b c - statRefund a b c ≤ 10000 ∧
    (c = 0 → formRefund a b c - statRefund a b c ≤ 5000) := by
  unfold formRefund statRefund; omega

/-- Attained: three children at the $17,280 maximum: form refunds $15,000, the statute $5,000. -/
example : formRefund 17280 17280 17280 = 15000 ∧ statRefund 17280 17280 17280 = 5000 := by decide

/-- Line 18 (nonrefundable this year) with credit limit `L` ≥ 0 and carryforward `cf` ≥ 0: min(line 12 − refund + cf, L). -/
def nonref (total refund cf L : Int) : Int := min (max 0 (total - refund) + cf) L

/-- With enough tax (L covers what is left) the year's total credit is the same either way: only the split
between refund and nonrefundable credit moves. With no tax (L = 0) the whole gap is refund now against
carryforward (lost if unused after five years, §23(c)(2)). -/
theorem year_total (a b c cf L : Int) (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) (hcf : 0 ≤ cf) :
    (a + b + c - statRefund a b c + cf ≤ L →
      formRefund a b c + nonref (a + b + c) (formRefund a b c) cf L
        = statRefund a b c + nonref (a + b + c) (statRefund a b c) cf L) ∧
    (L = 0 →
      (formRefund a b c + nonref (a + b + c) (formRefund a b c) cf L)
        - (statRefund a b c + nonref (a + b + c) (statRefund a b c) cf L)
        = formRefund a b c - statRefund a b c) := by
  unfold formRefund statRefund nonref; omega

end TaxCode.Big.Form8839

#print axioms TaxCode.Big.Form8839.gap_pos_iff
#print axioms TaxCode.Big.Form8839.year_total
