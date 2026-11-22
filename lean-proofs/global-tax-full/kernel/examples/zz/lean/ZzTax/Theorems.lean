import ZzTax.Basic

/-! # The kernel's one-liners instantiated for the toy country (the pattern for real countries) -/

namespace ZzTax
open TaxKernel

theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive
theorem sched_no_jump {x y : Int} (h : x ≤ y) : sched.ticks y - sched.ticks x ≤ sched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ sched_progressive h).2
theorem sched_le_top {x : Int} (h : 0 ≤ x) : sched.ticks x ≤ 4500 * x := by
  have := Schedule.ticks_le_maxRate_mul _ sched_progressive h
  have e : sched.maxRate = 4500 := by decide
  rwa [e] at this
theorem split_ok (a b : Int) : splitting sched.ticks a b ≤ separate sched.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b
theorem allowance_wf : allowance.WellFormed := by unfold Taper.WellFormed allowance; decide
theorem allowance_antitone {x y : Int} (h : x ≤ y) : allowance.amount y ≤ allowance.amount x :=
  Taper.amount_antitone _ allowance_wf h
/-- The toy's taper band: 2 more units of income between 100,000 and 124,000 cost 40 % × 3 = 1.2 units (60 %). -/
theorem taper_60 {inc : Int} (h1 : 100000 ≤ inc) (h2 : inc + 2 ≤ 123998) :
    sched.ticks (taxableAfter (allowance.amount (inc + 2)) (inc + 2))
      - sched.ticks (taxableAfter (allowance.amount inc) inc) = 4000 * 3 := by
  have hw := allowance_wf
  have hin : allowance.floor < allowance.amount (inc + allowance.den) := by
    simp only [allowance, Taper.amount, Taper.reduction, divR, pos]; omega
  have hpos : allowance.amount inc ≤ inc := by
    have := Taper.amount_le_full allowance hw inc; simp only [allowance] at this ⊢; omega
  have := Taper.taper_marginal allowance hw sched 4000 h1 hin hpos (by
    intro i hi1 hi2
    simp only [allowance, Taper.amount, Taper.reduction, divR, taxableAfter, pos] at hi1 hi2
    simp only [Schedule.rate, sched, Schedule.ofList, bandsRate, List.map]
    split <;> split <;> omega)
  simpa [allowance] using this
theorem soli_mono : Monotone' (fun x => x + soli.amount x) :=
  Surcharge.withSurcharge_mono soli (by decide) (by decide) (by decide) (by unfold Round.isMonotoneMode soli; decide)
    id (fun _ _ h => h)
theorem soli_notch : soli.ticks 1001 - soli.ticks 1000 = 500 * 1001 := by
  have := Surcharge.exempt_notch soli rfl (by decide); simpa [soli] using this
theorem pension_above_ceiling {x : Int} (h : 90000 ≤ x) : pension.ticks x = 800 * 90000 := by
  have := Contribution.ticks_above_ceiling pension (by decide) h (by simp [pension, Contribution.flatCapped]; omega)
  rw [this]; decide

end ZzTax
