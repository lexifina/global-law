/-!
# High Income Child Benefit Charge: the total of child benefit is rounded down before the percentage

ITEPA 2003 s. 681C(1): the charge is "the appropriate percentage of the total of" the child benefit amounts.
s. 681C(3): "If— (a) the total of the amounts mentioned in paragraphs (a) and (b) of subsection (1), or the amount
of the charge determined under that subsection, is not a whole number of pounds, or (b) the percentage determined
under subsection (2)(b) is not a whole number, it is to be rounded down to the nearest whole number."

So the charge is ⌊ ⌊total⌋ × p / 100 ⌋. GOV.UK's calculator (alphagov/smart-answers,
`lib/smart_answer/calculators/child_benefit_tax_calculator.rb`, line 79) computes
`(benefits_claimed_amount * (percent_tax_charge / 100.0)).floor`, i.e. ⌊ total × p / 100 ⌋ with the total in pence.
Whenever the pence of the total push the product over a whole pound, it shows £1 more.

All amounts in pence; proofs by kernel computation (`decide`). Lean 4 core only.
-/

namespace HicbcTotal

/-- Child benefit for a full 2025-26 year: 52 weeks (Mondays 7 April 2025 … 30 March 2026) at £26.05 for the
eldest child and £17.25 for each other child (S.I. 2025/292). In pence. -/
def cbPence (children : Nat) : Nat := 52 * (2605 + 1725 * (children - 1))

/-- s. 681C(1), (3)(a): pounds. -/
def statuteCharge (children pct : Nat) : Nat := (cbPence children / 100) * pct / 100

/-- The calculator's formula on the unrounded total (pounds). -/
def shownCharge (children pct : Nat) : Nat := cbPence children * pct / 10000

theorem totals : (cbPence 1, cbPence 2, cbPence 3, cbPence 4) = (135460, 225160, 314860, 404560) := by decide

/-- One child, adjusted net income £62,200 to £62,399 (11 %): £1,354 × 11 % = £148.94 → £148;
the calculator: £1,354.60 × 11 % = £149.006 → £149. -/
theorem one_child_11pc : statuteCharge 1 11 = 148 ∧ shownCharge 1 11 = 149 := by decide

/-- Two children, £79,800 to £79,999 (99 %): £2,251 × 99 % = £2,228.49 → £2,228; the calculator £2,229. -/
theorem two_children_99pc : statuteCharge 2 99 = 2228 ∧ shownCharge 2 99 = 2229 := by decide

/-- The general rule, 1 to 4 children and every percentage 0 … 100: the calculator is never below the statute and
never more than £1 above it. -/
theorem at_most_one_pound_more :
    ∀ n, n < 5 → 1 ≤ n → ∀ p, p < 101 →
      statuteCharge n p ≤ shownCharge n p ∧ shownCharge n p ≤ statuteCharge n p + 1 := by decide

/-- How many of the 101 percentages give £1 more, for 1, 2, 3 and 4 children. -/
theorem counts :
    ((List.range 101).filter (fun p => shownCharge 1 p ≠ statuteCharge 1 p)).length = 31 ∧
    ((List.range 101).filter (fun p => shownCharge 2 p ≠ statuteCharge 2 p)).length = 30 ∧
    ((List.range 101).filter (fun p => shownCharge 3 p ≠ statuteCharge 3 p)).length = 27 ∧
    ((List.range 101).filter (fun p => shownCharge 4 p ≠ statuteCharge 4 p)).length = 28 := by decide

end HicbcTotal
