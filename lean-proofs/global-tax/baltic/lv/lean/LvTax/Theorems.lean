import LvTax.Basic

/-!
# Kernel theorems instantiated for Latvia, and Latvia's own properties

* the 25,5 / 33 % schedule is progressive, monotone, convex, has no jump, never exceeds 33 % (kernel §5);
* `iin_ticks_eq`: the schedule in closed form; `iin_closed`: with deductions `d ≤ 105 300` the tax of
  income `g ≥ 105 300` is 25,5 % (105 300 − d) + 33 % (g − 105 300) (3. panta 2.4 daļa, 15. panta 15. daļa);
  `iin_eq_lowband`: for such deductions Latvia's rule is the kernel's `taxAfterLowBand`; `deduction_worth_255`:
  one more euro of deduction is worth exactly 25,5 % at any income;
* `deductions_at_lowest_rate`: Latvia's way of giving deductions (at 25,5 % first) never costs less than taking
  them off the top of the taxable income (kernel `lowBand_le_zeroBand`), and `lowband_cost` gives the difference
  for a high earner exactly: 7,5 % of the deductions that the "taxable income" reading would put in the 33 % band;
* `withholding_gap`: monthly withholding at a flat 25,5 % leaves 7,5 % of every euro above 105 300 to the annual
  return (15. panta 3. daļa vs 2. daļa);
* `iin_flat_below`: below the maximum object the tax is exactly 25,5 % of income less deductions.
-/

namespace LvTax
open TaxKernel

theorem iin_progressive : iinSched.progressive = true := by decide
theorem iin_mono : Monotone' iinSched.ticks := Schedule.ticks_mono_of_progressive _ iin_progressive
theorem iin_convex : Convex iinSched.ticks := Schedule.ticks_convex _ iin_progressive
theorem iin_no_jump {x y : Int} (h : x ≤ y) : iinSched.ticks y - iinSched.ticks x ≤ iinSched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ iin_progressive h).2
theorem iin_le_top {x : Int} (h : 0 ≤ x) : iinSched.ticks x ≤ 3300 * x := by
  have := Schedule.ticks_le_maxRate_mul _ iin_progressive h
  have e : iinSched.maxRate = 3300 := by decide
  rwa [e] at this
theorem iin_marginal (x : Int) : iinSched.ticks (x + 1) - iinSched.ticks x = iinSched.rate x :=
  Schedule.ticks_succ _ x
theorem iin_split_ok (a b : Int) : splitting iinSched.ticks a b ≤ separate iinSched.ticks a b :=
  splitting_le_separate _ iin_convex iin_mono a b

/-- The schedule in closed form (cents × bp). -/
theorem iin_ticks_eq (x : Int) :
    iinSched.ticks x = 2550 * pos (min x 10530000 - 0) + 3300 * pos (x - 10530000) := by
  simp [Schedule.ticks, iinSched, Schedule.ofList, bandsTicks]

/-- Up to deductions of 105 300 euro, Latvia's rule is the kernel's allowance given at the lowest rates. -/
theorem iin_eq_lowband {d g : Int} (hd : 0 ≤ d) (hdm : d ≤ 10530000) (hg : 0 ≤ g) :
    iinTicks d g = taxAfterLowBand iinSched (min d g) g := by
  unfold iinTicks taxAfterLowBand lowBandReduction
  simp only [iin_ticks_eq]
  simp only [pos, wageRate]
  omega

/-- Every euro of deduction is worth 25,5 %, at any income (3. panta 2.4 daļa, 15. panta 15. daļa). -/
theorem deduction_worth_255 {d g : Int} (hd : 0 ≤ d) (hdg : d + 1 ≤ g) (hpos : wageRate * (d + 1) ≤ iinSched.ticks g) :
    iinTicks d g - iinTicks (d + 1) g = 2550 := by
  unfold iinTicks
  simp only [pos, wageRate] at *
  omega

/-- With `0 ≤ d ≤ 105 300 ≤ g`: 25,5 % × (105 300 − d) + 33 % × (g − 105 300). -/
theorem iin_closed {d g : Int} (hd : 0 ≤ d) (hdm : d ≤ 10530000) (hg : 10530000 ≤ g) :
    iinTicks d g = 2550 * (10530000 - d) + 3300 * (g - 10530000) := by
  unfold iinTicks
  rw [iin_ticks_eq]
  simp only [pos, wageRate]
  omega

/-- Below the maximum object every euro of income above the deductions is taxed at exactly 25,5 %. -/
theorem iin_flat_below {d g : Int} (hd : 0 ≤ d) (hdg : d ≤ g) (hg : g ≤ 10530000) :
    iinTicks d g = 2550 * (g - d) := by
  unfold iinTicks
  rw [iin_ticks_eq]
  simp only [pos, wageRate]
  omega

/-- Kernel `lowBand_le_zeroBand`: taking the deductions off the top (taxable income = g − d through the schedule)
never costs more than Latvia's rule. -/
theorem deductions_at_lowest_rate {d g : Int} (hd : 0 ≤ d) (hdm : d ≤ 10530000) (hdg : d ≤ g) :
    iinSched.ticks (g - d) ≤ iinTicks d g := by
  rw [iin_eq_lowband hd hdm (by omega), show min d g = d by omega]
  have := lowBand_le_zeroBand iinSched iin_progressive hd hdg
  unfold taxAfterLowBand
  simp only [pos] at *
  omega

/-- The difference exactly, for income above the maximum object: 7,5 % of the part of the deductions that the
"taxable income above 105 300" reading would have taken out of the 33 % band, `min d (g − 105 300)` (FINDINGS F8:
VID's information material states that reading). -/
theorem lowband_cost {d g : Int} (hd : 0 ≤ d) (hdm : d ≤ 10530000) (hg : 10530000 ≤ g) :
    iinTicks d g - iinSched.ticks (g - d) = 750 * min d (g - 10530000) := by
  rw [iin_closed hd hdm hg, iin_ticks_eq]
  simp only [pos]
  omega

/-- Withholding at a flat 25,5 % (15. panta 3. daļa) against the annual 25,5 / 33 % (2. daļa), same deductions:
the annual return adds 7,5 % of the income above 105 300 euro. -/
theorem withholding_gap {d g : Int} (hd : 0 ≤ d) (hdm : d ≤ 10530000) (hg : 10530000 ≤ g) :
    iinTicks d g - wageRate * (g - d) = 750 * (g - 10530000) := by
  rw [iin_closed hd hdm hg]
  simp only [wageRate]
  omega

/-- The family benefit is not income-tested; the fourth child raises it from 225 to 400 euro a month (VSPL 6(2.2)). -/
theorem fvp_steps : fvpMonth 1 = 2500 ∧ fvpMonth 2 = 10000 ∧ fvpMonth 3 = 22500 ∧ fvpMonth 4 = 40000 ∧
    fvpMonth 5 = 50000 := by decide

/-- The additional rate has no notch: 3 % of the excess only (15.1 pants). -/
theorem surtax_no_jump (x : Int) : surtaxRate * pos (x + 1 - surtaxThreshold) - surtaxRate * pos (x - surtaxThreshold) ≤ 300 := by
  simp only [surtaxRate, pos]; omega

/-- Kernel `Contribution.ticks_above_ceiling`: the employee's VSAOI stops at the maximum object... -/
theorem vsaoi_capped {w : Int} (h : 10530000 ≤ w) :
    (Contribution.flatCapped "VSAOI" eeRate maxObject).ticks w = 1050 * 10530000 := by
  have := Contribution.ticks_above_ceiling (Contribution.flatCapped "VSAOI" eeRate maxObject) (by decide)
    (x := w) (by simp [Contribution.flatCapped, maxObject, eur]; omega)
    (by simp [Contribution.flatCapped]; omega)
  rw [this]; decide

/-- ... but the solidarity tax takes the same 10,5 % from the employee above it (Solidaritātes nodokļa likums 6.2
pants: the overpayment is refunded to the employer only), so the employee has no ceiling at all. -/
theorem employee_no_ceiling {w : Int} (h : 10530000 ≤ w) :
    (Contribution.flatCapped "VSAOI" eeRate maxObject).ticks w + eeRate * pos (w - maxObject) = eeRate * w := by
  rw [vsaoi_capped h]; simp only [eeRate, maxObject, eur, pos]; omega

/-- Kernel `Surcharge.ticks_mono`: the 3 % additional rate never falls as income rises. -/
theorem surtax_mono {x y : Int} (h : x ≤ y) : surtax.ticks x ≤ surtax.ticks y :=
  Surcharge.ticks_mono surtax (by decide) (by decide) h

end LvTax
