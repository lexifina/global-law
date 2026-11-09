import LegalProofs.USTax.Loopholes.Common

/-!
# The SALT torpedo and the business-owner's way round it (§164(b)(6)–(7))

From 2025 the cap on deducting state and local taxes is $40,000 (§164(b)(7) as added by Pub. L. 119-21 §70120), but it
shrinks by 30% of modified AGI above $500,000, down to the old $10,000. Between $500,000 and $600,000, each extra
$1,000 earned also removes $300 of deduction: at the 35% rate, an effective 45.5% marginal rate.

The cap applies to taxes an **individual** pays. A partnership or S corporation that pays the state's income tax at the
entity level (a "PTET", accepted by the IRS in Notice 2020-75 and left in place by the 2025 Act) deducts it as a business
expense, outside the cap. Two people with the same income and the same state tax: the employee deducts $10,000; the
owner, all of it.
-/

namespace Legal.USTax.Loopholes.SALT
open Legal.USTax Legal.USTax.Loopholes

/-- The 2025 cap: $40,000 less 30% of MAGI above $500,000, never below $10,000 (single and joint filers alike). -/
def saltCap (magi : Nat) : Nat := max 10000 (40000 - (magi - 500000) * 3 / 10)

/-- **The torpedo.** Anywhere inside the phase-down band, $1,000 more income removes exactly $300 of deduction. -/
theorem torpedo (x : Nat) (h₁ : 500000 ≤ x) (h₂ : x + 1000 ≤ 600000) : saltCap (x + 1000) + 300 = saltCap x := by
  unfold saltCap; omega

/-- Above $600,000 the cap is back to $10,000, whatever the income. -/
theorem floor_above (x : Nat) (h : 600000 ≤ x) : saltCap x = 10000 := by
  unfold saltCap; omega

/-- Income tax for a single employee itemising: state tax `stateTax`, other itemised deductions `other`. -/
def employeeTax (wages stateTax other : Nat) : Nat :=
  scheduleTax .single (wages - max (stdDeduction .single) (min stateTax (saltCap wages) + other))

/-- A California or New York earner: state tax 10% of income, $35,000 of other itemised deductions. -/
def earner (wages : Nat) : Nat := employeeTax wages (wages / 10) 35000

/-- **45.5%, certified.** For each of the hundred $1,000 steps from $500,000 to $600,000, federal income tax rises by
$455 (the rounding of the rate schedule can move a step by a dollar). -/
theorem torpedo_band :
    (List.range 100).all (fun i => let a := earner (500000 + 1000 * i); let b := earner (501000 + 1000 * i);
      454 ≤ b - a ∧ b - a ≤ 456) = true := by decide

/-- **The owner's exemption.** $1 million of income, $100,000 of state income tax. The employee deducts $10,000 of it;
the S-corporation owner whose company pays the tax deducts all $100,000 before the income reaches the return. -/
def ownerTax (income stateTax other : Nat) : Nat :=
  scheduleTax .single (income - stateTax - max (stdDeduction .single) other)

theorem ptet_saves : earner 1000000 - ownerTax 1000000 100000 35000 = 33300 := by decide

end Legal.USTax.Loopholes.SALT
