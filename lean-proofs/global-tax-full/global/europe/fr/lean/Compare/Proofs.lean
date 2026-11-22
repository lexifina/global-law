import Compare.Us
import Compare.Fr

/-!
# Properties of the comparison's own additions, proved for every input

The country models carry their own theorems (`TaxCode.Individual.*`, `FrTax.Theorems`, `FrTax.Loopholes`, and the
UK, German and Japanese agents' files). This file proves what the cross-system table needs and the models do not
state: properties of the contributions and benefits this comparison added to the US and French models. Lean 4 core only; no `sorry`, no `native_decide`.
-/

namespace Compare.Proofs
open FrTax Compare.Fr

/-! ## United States: employee FICA (§3101(a), (b)(1)) -/

/-- FICA never falls when wages rise. -/
theorem fica_mono (a b : Int) (h : a ≤ b) : Compare.Us.fica a ≤ Compare.Us.fica b := by
  unfold Compare.Us.fica Compare.Us.oasdi Compare.Us.hospital TaxCode.Individual.roundDollar Compare.Us.wageBase
  have h1 : max 0 (min a 176100) ≤ max 0 (min b 176100) := by omega
  have h2 : max 0 a ≤ max 0 b := by omega
  have e1 := Int.ediv_le_ediv (show (0 : Int) < 2 * 1000 by decide) (show 2 * (62 * max 0 (min a 176100)) + 1000 ≤ 2 * (62 * max 0 (min b 176100)) + 1000 by omega)
  have e2 := Int.ediv_le_ediv (show (0 : Int) < 2 * 10000 by decide) (show 2 * (145 * max 0 a) + 10000 ≤ 2 * (145 * max 0 b) + 10000 by omega)
  omega

/-- Above the wage base only the 1.45 % hospital insurance grows: $1,000 more pay adds exactly $14.50, so $14 or
$15 after rounding (the 6.2 % part is fixed at $10,918). -/
theorem fica_above_base (w : Int) (h : 176100 ≤ w) :
    Compare.Us.oasdi w = 10918 ∧ Compare.Us.oasdi (w + 1000) = 10918 := by
  unfold Compare.Us.oasdi TaxCode.Individual.roundDollar Compare.Us.wageBase
  constructor <;> omega

/-! ## France: contributions on pay -/

/-- The contribution d'équilibre technique is nil up to the PASS... -/
theorem cet_zero_below (g : Int) (h : g ≤ pass) : (contrib g).cet = 0 := by
  have : ¬ (max 0 g > pass) := by unfold pass at *; omega
  simp only [contrib, contribP, this, ite_false]

/-- ... and one euro above it costs 65.94 € at once: the notch the scan finds at 47 101 €. -/
theorem cet_notch : (contrib 47100).cet = 0 ∧ (contrib 47101).cet = 6594 := by decide

/-- The pension contributions plafonnées stop at the PASS: above it one more euro of pay adds no vieillesse
plafonnée and no tranche-1 AGIRC-ARRCO. -/
theorem plafonnee_flat_above (g : Int) (h : pass ≤ g) :
    (contrib g).vieillessePlaf = (contrib pass).vieillessePlaf ∧ (contrib g).agircT1 = (contrib pass).agircT1 := by
  have hm : min (max 0 g) pass = pass := by unfold pass at *; omega
  simp only [contrib, contribP, hm]
  decide

/-! ## France: the allocations familiales withdraw one euro per euro of resources in the smoothing band -/

/-- Between the two ceilings (two children, no age supplement), a month's allocation is the tier-2 amount plus the
complement of D521-1, II. -/
theorem month_tier2 (bmaf r : Int) (h1 : ceiling1 2 < r) (h2 : r ≤ ceiling2 2) :
    month bmaf r 2 0 = monthly bmaf 2 2 0 + max 0 ((100 * ceiling1 2 + 12 * monthly bmaf 2 2 0 - 100 * r) / 12) := by
  have n1 : ¬ (r ≤ ceiling1 2) := by omega
  simp only [month, monthC, if_neg n1, if_pos h2]
  rfl

/-- In a month of the band above the first ceiling (two children, no age supplement), twelve more euros of annual
resources take exactly one euro (100 cents) off that month's allocation: across the twelve months of a year, twelve
euros of resources cost twelve euros of allocations, a 100 % withdrawal rate (CSS art. D521-1, II). -/
theorem af_band_slope (bmaf r : Int)
    (h1 : ceiling1 2 < r) (h2 : r + 12 ≤ ceiling2 2)
    (h3 : 100 * (r + 12) ≤ 100 * ceiling1 2 + 12 * monthly bmaf 2 2 0) :
    month bmaf (r + 12) 2 0 = month bmaf r 2 0 - 100 := by
  rw [month_tier2 bmaf (r + 12) (by omega) h2, month_tier2 bmaf r h1 (by omega)]
  generalize monthly bmaf 2 2 0 = m at *
  generalize ceiling1 2 = c at *
  omega

/-! ## France: the scale's marginal rate (income 2025), for one part and for a couple's two parts -/

/-- One part (a single person): one more euro of taxable income adds at most one euro of scale tax. -/
theorem scale_step_single_2025 (r : Int) (hr : 0 ≤ r) : scaleTax p2025 (r + 1) 4 ≤ scaleTax p2025 r 4 + 1 := by
  simp only [scaleTax, rnd, pos, p2025]
  omega

/-- One part: over any 100 euros the scale takes at most 45 euros (plus one of rounding), and it never falls. -/
theorem scale_45_single_2025 (r : Int) (hr : 0 ≤ r) :
    scaleTax p2025 r 4 ≤ scaleTax p2025 (r + 100) 4 ∧ scaleTax p2025 (r + 100) 4 ≤ scaleTax p2025 r 4 + 46 := by
  simp only [scaleTax, rnd, pos, p2025]
  omega

/-- Two parts (a married couple without children): the same bounds. -/
theorem scale_45_couple_2025 (r : Int) (hr : 0 ≤ r) :
    scaleTax p2025 r 8 ≤ scaleTax p2025 (r + 100) 8 ∧ scaleTax p2025 (r + 100) 8 ≤ scaleTax p2025 r 8 + 46 := by
  simp only [scaleTax, rnd, pos, p2025]
  omega

/-- The 45 % rate is reached: from 1 000 000 € to 1 000 100 € of taxable income, one part pays 45 € more. -/
theorem scale_top_single_2025 : scaleTax p2025 1000100 4 - scaleTax p2025 1000000 4 = 45 := by decide

end Compare.Proofs

-- Axioms check (expected: none beyond propext, Classical.choice, Quot.sound)
#print axioms Compare.Proofs.fica_mono
#print axioms Compare.Proofs.cet_zero_below
#print axioms Compare.Proofs.cet_notch
#print axioms Compare.Proofs.plafonnee_flat_above
#print axioms Compare.Proofs.af_band_slope
#print axioms Compare.Proofs.scale_45_single_2025
#print axioms Compare.Proofs.scale_45_couple_2025
