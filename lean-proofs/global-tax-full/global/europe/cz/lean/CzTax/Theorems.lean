import CzTax.Withholding

/-!
# Theorems for all inputs (no `sorry`, no `native_decide`)

Generic kernel properties instantiated for § 16 ZDP, the Czech claims the statute makes (the bonus never exceeds the
child amount, the 23 % threshold, the roundings), and the withholding-versus-annual comparison.
-/

namespace CzTax

/-! ## § 16: the schedule -/

theorem tax16Cents_mono {a b : Int} (h : a ≤ b) : tax16Cents a ≤ tax16Cents b := by
  unfold tax16Cents threshold23 avgWage rateLow rateHigh pos; omega

theorem tax16_mono {a b : Int} (h : a ≤ b) : tax16 a ≤ tax16 b := by
  unfold tax16; exact cdiv_mono 100 (by decide) (tax16Cents_mono h)

theorem tax16_zero : tax16 0 = 0 := by decide

/-- No jump: one more crown of base adds 15 or 23 hundredths of a crown, never more, never less than 0. -/
theorem tax16Cents_step (b : Int) (hb : 0 ≤ b) :
    tax16Cents (b + 1) - tax16Cents b = (if b < 1676052 then 15 else 23) := by
  unfold tax16Cents threshold23 avgWage rateLow rateHigh pos; split <;> omega

/-- The 23 % rate starts exactly at 36 × the 2025 average wage: below it every crown is taxed at 15 %. -/
theorem marginal_15_below (b : Int) (h0 : 0 ≤ b) (h : b + 1 ≤ 1676052) : tax16Cents (b + 1) - tax16Cents b = 15 := by
  unfold tax16Cents threshold23 avgWage rateLow rateHigh pos; omega

theorem marginal_23_above (b : Int) (h : 1676052 ≤ b) : tax16Cents (b + 1) - tax16Cents b = 23 := by
  unfold tax16Cents threshold23 avgWage rateLow rateHigh pos; omega

/-- The tax never exceeds 23 % of the base, and is at least 15 % of it. -/
theorem tax16_bounds (b : Int) (hb : 0 ≤ b) : 15 * b ≤ tax16Cents b ∧ tax16Cents b ≤ 23 * b := by
  unfold tax16Cents threshold23 avgWage rateLow rateHigh pos; omega

/-- § 16 odst. 2 + daňový řád § 146: on a base rounded to the hundred, the tax is exact below the threshold
(15 % of a multiple of 100 is a whole number of crowns), so the rounding up only acts above it. -/
theorem tax16_exact_below (b : Int) (hb : 0 ≤ b) (h : b ≤ 1676052) (h100 : b % 100 = 0) :
    tax16 (b) * 100 = 15 * b := by
  unfold tax16 tax16Cents cdiv threshold23 avgWage rateLow rateHigh pos; omega

/-- The base rounding costs at most 99 crowns of base, i.e. at most 22,77 crowns of tax, and never adds tax. -/
theorem roundBase_saving (x : Int) (hx : 0 ≤ x) :
    tax16 (roundBase x) ≤ tax16 x ∧ tax16 x - tax16 (roundBase x) ≤ 23 := by
  unfold tax16 roundBase floorTo tax16Cents cdiv threshold23 avgWage rateLow rateHigh pos; omega

/-! ## § 35ba, § 35c: credits and the bonus -/

/-- § 35c odst. 3: the bonus never exceeds the child amount claimed, and the sleva part plus the bonus never
exceed it either (the statute's "maximální výše daňového bonusu" is therefore the zvýhodnění itself). -/
theorem bonus_le_childCredit (t : TaxIn) :
    (computeTax t).childSleva + (computeTax t).bonus ≤ pos t.childCredits := by
  unfold computeTax; exact credit_total_le _ _ _ _

theorem bonus_le_childCredit' (t : TaxIn) : (computeTax t).bonus ≤ pos t.childCredits := by
  have h := bonus_le_childCredit t
  have h2 : 0 ≤ (computeTax t).childSleva := by unfold computeTax; exact creditUsed_nonneg _ _
  omega

/-- The bonus notch of § 35c odst. 4 (6 × minimum wage = 124 800 Kč of § 6/§ 7 income): one crown of wage more
turns a nil tax into a 15 204 Kč payment for a parent of one child. -/
theorem bonus_notch_124800 :
    (computeTax { wages := 124799, childCredits := 15204 }).finalTax = 0 ∧
    (computeTax { wages := 124800, childCredits := 15204 }).finalTax = -15204 := by decide

/-- The sleva na manžela is all-or-nothing at 68 000 Kč of the spouse's own income (§ 35bb odst. 2 písm. b)): for an
earner of 600 000 Kč the tax differs by the whole 24 840 Kč. -/
theorem spouse_credit_value :
    (computeTax { wages := 600000 }).finalTax - (computeTax { wages := 600000, spouseCredit := true }).finalTax
      = 24840 := by decide

/-! ## Withholding (§ 38h) against the annual tax (§ 16) -/

/-- Before any credit, twelve monthly zálohy on the same wage never collect less than the annual tax: the monthly
base is rounded **up** to the hundred (§ 38h odst. 1), the annual base **down** (§ 16 odst. 2), and the monthly
threshold is exactly 1/12 of the annual one. -/
theorem withholding_ge_annual (m : Int) (hm : 0 ≤ m) : tax16 (roundBase (12 * m)) ≤ 12 * zaloha m := by
  unfold tax16 roundBase floorTo zaloha monthBase ceilTo tax16Cents cdiv threshold23 monthlyThreshold23 avgWage
    rateLow rateHigh pos
  dsimp only
  split <;> omega

/-- … and over-collect by at most 312 Kč a year (12 roundings of the base up to 99 Kč at 23 %, plus 12 roundings
of the záloha up to the crown, plus the annual base rounding down). -/
theorem withholding_excess_le (m : Int) (hm : 0 ≤ m) : 12 * zaloha m - tax16 (roundBase (12 * m)) ≤ 312 := by
  unfold tax16 roundBase floorTo zaloha monthBase ceilTo tax16Cents cdiv threshold23 monthlyThreshold23 avgWage
    rateLow rateHigh pos
  dsimp only
  split <;> omega

end CzTax
