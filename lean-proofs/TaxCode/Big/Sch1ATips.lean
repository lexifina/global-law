/-!
# Schedule 1-A (2025) Part II (tips) and Part III (overtime) against §§224, 225 and Notice 2025-69

Form/instructions: 2025 Instructions for Form 1040, Instructions for Schedule 1-A, p. 102 (TIP): "Until the issuance of
final regulations determining whether a trade or business is an SSTB for purposes of this deduction, and for taxable
years beginning before the date the final regulations ..., the IRS will treat employees and self-employed individuals
as having received tips in the course of a trade or business that is not an SSTB if the employee is in an occupation
that customarily and regularly received tips on or before December 31, 2024 ... see Notice 2025-69." pp. 106-108:
overtime worked out from pay statements by a "reasonable method" (for example total overtime pay ÷ 3).

Statute: §224(d)(2)(B): qualified tips exclude any amount unless "the trade or business in the course of which the
individual receives such amount is not a specified service trade or business (as defined in section 199A(d)(2))";
§224(d)(2)(C) lets the Secretary add requirements, not remove one. §224(b)(1) $25,000 cap; §224(b)(2) $100 per $1,000
of MAGI over $150,000 ($300,000 joint). §225(a): overtime "included on statements furnished to the individual pursuant
to section 6041(d)(4) or 6051(a)(19)"; §225(b) $12,500 ($25,000 joint), same phase-out.

Notice 2025-69 §III.A.1 (pp. 14-16): the SSTB rule is relieved "for purposes of IRS enforcement and administration"
until final SSTB regulations; §III.A.1 and §III.B.2 (pp. 12-13, 21-22): for 2025 the statement requirement is "satisfied
if the employee's cash tips [qualified overtime compensation] are properly reported on the employee's Form W-2 ...
without regard to the requirements of section 6051(a)(18) [(a)(19)]".
-/

namespace TaxCode.Big.Sch1ATips

/-- §224(b)/§225(b) deduction for an amount `q`, cap `cap`, threshold `thr`: min(q, cap) less $100 for each full
$1,000 of MAGI over the threshold, not below zero (Schedule 1-A lines 6-13 / 15-21). -/
def ded (cap thr q magi : Int) : Int := max 0 (min q cap - 100 * (max 0 (magi - thr) / 1000))

/-- Statute: tips received in the course of an SSTB are not qualified tips (§224(d)(2)(B)). -/
def statTips (sstb : Bool) (tips magi thr : Int) : Int := if sstb then 0 else ded 25000 thr tips magi
/-- Form (2025, Notice 2025-69 relief): a listed tipped occupation is treated as not in an SSTB. -/
def formTips (_sstb : Bool) (tips magi thr : Int) : Int := ded 25000 thr tips magi

/-- The difference is the whole deduction for an SSTB tip earner and zero otherwise. -/
theorem tips_gap (sstb : Bool) (tips magi thr : Int) :
    formTips sstb tips magi thr - statTips sstb tips magi thr = if sstb then ded 25000 thr tips magi else 0 := by
  unfold formTips statTips; cases sstb <;> simp <;> omega

/-- Exact affected set: an SSTB tip earner whose allowed amount survives the phase-out. -/
theorem tips_gap_pos_iff (sstb : Bool) (tips magi thr : Int) :
    0 < formTips sstb tips magi thr - statTips sstb tips magi thr ↔
      sstb = true ∧ 100 * (max 0 (magi - thr) / 1000) < min tips 25000 := by
  rw [tips_gap]; unfold ded; cases sstb <;> simp <;> omega

/-- Max $25,000 of deduction per return, attained by any SSTB earner with ≥ $25,000 of tips and MAGI ≤ threshold. -/
theorem tips_gap_le (sstb : Bool) (tips magi thr : Int) :
    formTips sstb tips magi thr - statTips sstb tips magi thr ≤ 25000 := by
  rw [tips_gap]; unfold ded; cases sstb <;> simp <;> omega

theorem tips_gap_attained (tips magi thr : Int) (ht : 25000 ≤ tips) (hm : magi ≤ thr) :
    formTips true tips magi thr - statTips true tips magi thr = 25000 := by
  rw [tips_gap]; unfold ded; simp; omega

/-! ## Tax value. 2025 single rate schedule (Rev. Proc. 2024-40 as amended by Pub. L. 119-21: 10% to $11,925, 12% to
$48,475, 22% to $103,350, 24% to $197,300, 32% to $250,525, 35% to $626,350, 37% above), in cents of taxable income ×
100 (tax in 1/100 cent). -/

def tax25 (ti : Int) : Int :=
  let x := max 0 ti
  if x ≤ 11925 then 10 * x
  else if x ≤ 48475 then 119250 + 12 * (x - 11925)
  else if x ≤ 103350 then 557850 + 22 * (x - 48475)
  else if x ≤ 197300 then 1765100 + 24 * (x - 103350)
  else if x ≤ 250525 then 4019900 + 32 * (x - 197300)
  else if x ≤ 626350 then 5723100 + 35 * (x - 250525)
  else 18876975 + 37 * (x - 626350)

/-- Tax saved (in cents) by a deduction `d` from taxable income `ti` (before the deduction). -/
def saved (ti d : Int) : Int := tax25 ti - tax25 (ti - d)

/-- Single musician (SSTB), MAGI $150,000, standard deduction $15,750, $25,000 of tips: the relief is worth exactly
$6,000 of tax (24% bracket). -/
example : saved (150000 - 15750) (formTips true 25000 150000 150000 - statTips true 25000 150000 150000) = 600000 := by
  decide

theorem saved_le24 (ti d : Int) (hd : 0 ≤ d) (h : ti ≤ 197300) : saved ti d ≤ 24 * d := by
  unfold saved tax25; simp only; repeat' split
  all_goals omega

theorem saved_le32 (ti d : Int) (hd : 0 ≤ d) (h : ti ≤ 250525) : saved ti d ≤ 32 * d := by
  unfold saved tax25; simp only; repeat' split
  all_goals omega

theorem saved_le37 (ti d : Int) (hd : 0 ≤ d) : saved ti d ≤ 37 * d := by
  unfold saved tax25; simp only; repeat' split
  all_goals omega

/-- **For every single 2025 filer with the standard deduction or more (other deductions D ≥ $15,750), the relief
saves at most $6,000 of income tax**: in the 24% bracket the cap is $25,000; to reach 32% MAGI must exceed $213,050,
which has cut the deduction to $18,700 or less; to reach 35% the cut leaves $13,400 or less. -/
theorem saved_le (magi D tips : Int) (hD : 15750 ≤ D) :
    saved (magi - D) (formTips true tips magi 150000 - statTips true tips magi 150000) ≤ 600000 := by
  rw [tips_gap]; simp only [↓reduceIte]
  have h0 : 0 ≤ ded 25000 150000 tips magi := by unfold ded; omega
  have hb : ded 25000 150000 tips magi ≤ max 0 (25000 - 100 * (max 0 (magi - 150000) / 1000)) := by
    unfold ded; omega
  generalize ded 25000 150000 tips magi = d at *
  by_cases h1 : magi - D ≤ 197300
  · have := saved_le24 (magi - D) d h0 h1; omega
  by_cases h2 : magi - D ≤ 250525
  · have := saved_le32 (magi - D) d h0 h2; omega
  · have := saved_le37 (magi - D) d h0; omega

/-! ## Overtime: what the statement requirement means decides whether there is a gap at all. -/

/-- "Separately stated" reading (House report H. Rept. 119-106 p. 1503, cited in Notice 2025-69 fn. 4): only the
amount separately shown on a statement counts. -/
def statOtSeparate (stated magi : Int) : Int := ded 12500 150000 stated magi
/-- Notice/form reading: the overtime is "included on" the W-2 because it is inside box 1; the amount is the
qualified overtime the taxpayer works out (`actual`). -/
def formOt (actual magi : Int) : Int := ded 12500 150000 actual magi

/-- Under the "included in box 1" reading the form is the statute; under the separately-stated reading the gap for a
2025 employee with no box 14 entry (stated = 0) is the whole deduction, at most $12,500 single. -/
theorem ot_gap (actual magi : Int) :
    formOt actual magi - statOtSeparate 0 magi = ded 12500 150000 actual magi ∧
    formOt actual magi - statOtSeparate 0 magi ≤ 12500 := by
  unfold formOt statOtSeparate ded; omega

end TaxCode.Big.Sch1ATips

#print axioms TaxCode.Big.Sch1ATips.tips_gap_pos_iff
#print axioms TaxCode.Big.Sch1ATips.saved_le
