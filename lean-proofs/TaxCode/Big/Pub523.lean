/-!
# Pub. 523 (2025) Worksheet 1 against §121(b)(2)(B), (c) and Reg. §1.121-3(g)(2) Example 2

Publication text (Pub. 523 (2025), created Feb 27, 2026, p. 8, https://www.irs.gov/pub/irs-pdf/p523.pdf), Worksheet 1
"Find Your Exclusion Limit", Section A, row "Married filing jointly": eligible for $500,000 if "Both spouses meet the
residence and look-back requirements and one or both spouses meet the ownership requirement"; otherwise "Determine if
either spouse is eligible for the full limit as a single person. If not, determine if either spouse is eligible for a
partial exclusion." Section B ("Complete this section only if you have determined that you aren't eligible for the
maximum exclusion but are eligible for a partial exclusion"): Step 2 "divide ... by 730 (if using days) or 24 (if
using months)"; Step 3 "Multiply the result from Step 2 by $250,000"; Step 4 "Repeat Steps 1–3 for your spouse and add
the two results". Section C "Your exclusion limit is $___".

Statute: §121(b)(2)(B) "If such spouses do not meet the requirements of subparagraph (A), the limitation under paragraph
(1) shall be the sum of the limitations under paragraph (1) to which each spouse would be entitled if such spouses had
not been married"; §121(c)(1)-(2) reduced limitation (shorter period / 2 years) when the sale is by reason of a change
of place of employment, health or unforeseen circumstances. Reg. §1.121-2(a)(3)(ii): "the sum of each spouse's
limitation amount determined on a separate basis as if they had not been married". Reg. §1.121-3(g)(2) Example 2: H
meets the requirements, W used the house one year, sale due to W's job change: "H and W are eligible to exclude up to
$375,000 of gain ($250,000 + $125,000)".

Model (months, amounts ×24 so the fraction is exact): each spouse is `full` (meets the tests alone), `part t` (does not,
sale is for a qualifying reason, shortest period t < 24 months) or `none`; the couple does not meet (b)(2)(A).
-/

namespace TaxCode.Big.Pub523

inductive Sp where
  | full
  | part (t : Nat)
  | none

/-- One spouse's separate limitation ×24 (§121(b)(1), (c)(1)). -/
def sep : Sp → Nat
  | .full => 24 * 250000
  | .part t => min t 24 * 250000
  | .none => 0

def isFull : Sp → Bool
  | .full => true
  | _ => false

/-- Statute and Reg. §1.121-2(a)(3)(ii): the sum of the separate limitations. -/
def statute (a b : Sp) : Nat := sep a + sep b

/-- Worksheet 1 (MFJ row, couple not at $500,000): the full single limit if either spouse has it; only "If not" the
Section B partial amounts, added. -/
def worksheet (a b : Sp) : Nat := if isFull a || isFull b then 24 * 250000 else sep a + sep b

/-- Reg. §1.121-3(g)(2) Example 2 (W: 12 months): statute $375,000, worksheet $250,000. -/
example : statute .full (.part 12) = 24 * 375000 ∧ worksheet .full (.part 12) = 24 * 250000 := by decide

/-- The worksheet never exceeds the statute; the gap is exactly the partial spouse's reduced amount when the other
spouse is fully eligible. -/
theorem gap (a b : Sp) :
    worksheet a b ≤ statute a b ∧
    statute a b - worksheet a b =
      (match a, b with
       | .full, .part t => min t 24 * 250000
       | .part t, .full => min t 24 * 250000
       | .full, .full => 24 * 250000
       | _, _ => 0) := by
  cases a <;> cases b <;> simp [worksheet, statute, sep, isFull] <;> omega

/-- Exact affected set (outside (b)(2)(A), where both full is impossible): one spouse fully eligible and the other
eligible for a positive reduced amount. Max with t ≤ 23 months: $239,583.33 (×24 = 5,750,000); in days (729/730)
$249,657.53. -/
theorem gap_le (t : Nat) (ht : t < 24) :
    statute .full (.part t) - worksheet .full (.part t) ≤ 23 * 250000 ∧
    (0 < statute .full (.part t) - worksheet .full (.part t) ↔ 0 < t) := by
  simp [worksheet, statute, sep, isFull]; omega

end TaxCode.Big.Pub523

#print axioms TaxCode.Big.Pub523.gap
#print axioms TaxCode.Big.Pub523.gap_le
