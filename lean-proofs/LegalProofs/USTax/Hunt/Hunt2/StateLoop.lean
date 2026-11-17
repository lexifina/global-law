import Std

/-!
# Federal <-> state loop: federal deduction of state income tax, state deduction of federal income tax

Rules:
* §164(a)(3), §164(b)(6) as amended by Pub. L. 119-21 §70120 (`sec.py 164 b 6`): state income tax is deductible by
  an itemizer, up to the applicable limitation ($40,000 for 2025, reduced by 30% of modified AGI over $500,000, not
  below $10,000). For a cash-method individual the tax deducted is the tax *paid* in the year (§461, Treas. Reg.
  §1.461-1(a)(1)).
* Alabama, Ala. Code §40-18-15(a)(2) and r. 810-3-15-.20: deduction of the federal income tax liability for the
  year (after credits shown as payments). Missouri §143.171 (35%..0% of federal tax by Missouri AGI, capped $5,000 /
  $10,000) and Oregon ORS 316.800 (capped, phased out by AGI) are the same shape with smaller slopes. Louisiana
  (repealed by Acts 2021 No. 39 from 2022), Montana (SB 399, from 2024) and Iowa no longer allow it (Iowa: see
  conformity table; marked unverified there).

The loop closes only when the taxpayer pays in the year the state tax the year produces (withholding or a December
estimate). Then `S = st (F)` and `F = fed (S)`: the state tax falls by at most 5% (Alabama's top rate) of any rise in
federal tax, and federal tax falls by at most 37% of any rise in state tax paid (and by nothing once the SALT
limitation binds or the taxpayer takes the standard deduction). The product is below 2%, so the loop has one
answer to within rounding; there is no second consistent answer and no free choice. Below: the generic statement.
-/

namespace Legal.USTax.Hunt.Hunt2.StateLoop

/-- `st` is the state tax as a function of the federal tax, `fed` the federal tax as a function of state tax paid.
Slopes in basis points, each map rounded to the dollar (the `+ 1`). -/
structure Loop where
  st  : Int → Int
  fed : Int → Int
  /-- state tax: nonincreasing in federal tax, slope at most 5% (Ala. Code §40-18-15(a)(2), 5% top rate) -/
  st_lip : ∀ a b, a ≤ b → st b ≤ st a ∧ st a - st b ≤ (500 * (b - a)) / 10000 + 1
  /-- federal tax: nonincreasing in state tax paid, slope at most 37% (§1(j), §164(b)(6)) -/
  fed_lip : ∀ a b, a ≤ b → fed b ≤ fed a ∧ fed a - fed b ≤ (3700 * (b - a)) / 10000 + 1

/-- Any two joint answers (state tax paid = state tax due, federal tax computed from it) differ by at most $2 of
state tax and $2 of federal tax: the loop has one answer up to rounding. -/
theorem loop_unique (L : Loop) (S1 S2 : Int)
    (h1 : S1 = L.st (L.fed S1)) (h2 : S2 = L.st (L.fed S2)) (hle : S1 ≤ S2) :
    S2 - S1 ≤ 2 ∧ L.fed S1 - L.fed S2 ≤ 2 := by
  have ⟨f1, f2⟩ := L.fed_lip S1 S2 hle
  have ⟨s1, s2⟩ := L.st_lip (L.fed S2) (L.fed S1) f1
  omega

/-- Iterating from "nothing paid" moves the state tax by at most 5% x 37% of the previous move plus rounding:
the PolicyEngine iteration (tools/hunt/out/Hunt2/alloop.txt) settles in 2-4 rounds. -/
theorem loop_contracts (L : Loop) (a b : Int) (hle : a ≤ b) :
    L.st (L.fed b) - L.st (L.fed a) ≤ (500 * ((3700 * (b - a)) / 10000 + 1)) / 10000 + 1 ∧
    L.st (L.fed a) ≤ L.st (L.fed b) := by
  have ⟨f1, f2⟩ := L.fed_lip a b hle
  have ⟨s1, s2⟩ := L.st_lip (L.fed b) (L.fed a) f1
  constructor
  · have : (500 * (L.fed a - L.fed b)) / 10000 ≤ (500 * ((3700 * (b - a)) / 10000 + 1)) / 10000 := by
      apply Int.ediv_le_ediv (by decide); omega
    omega
  · exact s1

/-- A concrete instance: Alabama 5% on income over the brackets less the federal tax; federal 24% bracket for an
itemizer whose state tax stays under the SALT limitation `cap`. -/
def alSt (base F : Int) : Int := (500 * (base - F)) / 10000
def fedIt (f0 cap S : Int) : Int := f0 - (2400 * min S cap) / 10000

def alLoop (base f0 cap : Int) (hcap : 0 ≤ cap) : Loop where
  st := alSt base
  fed := fedIt f0 cap
  st_lip := by intro a b h; unfold alSt; constructor <;> omega
  fed_lip := by intro a b h; unfold fedIt; constructor <;> omega

end Legal.USTax.Hunt.Hunt2.StateLoop

open Legal.USTax.Hunt.Hunt2.StateLoop in
#print axioms loop_unique
open Legal.USTax.Hunt.Hunt2.StateLoop in
#print axioms loop_contracts
open Legal.USTax.Hunt.Hunt2.StateLoop in
#print axioms alLoop
