import EeTax.Basic

/-! # Kernel theorems instantiated for Estonia, and Estonia's own properties (no `sorry`) -/

namespace EeTax
open TaxKernel

/-! ## The flat schedule (§ 4(1)) -/

theorem sched_progressive : sched.progressive = true := by decide
theorem sched_mono : Monotone' sched.ticks := Schedule.ticks_mono_of_progressive _ sched_progressive
theorem sched_convex : Convex sched.ticks := Schedule.ticks_convex _ sched_progressive
theorem sched_no_jump {x y : Int} (h : x ≤ y) : sched.ticks y - sched.ticks x ≤ sched.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ sched_progressive h).2
theorem sched_le_22 {x : Int} (h : 0 ≤ x) : sched.ticks x ≤ 2200 * x := by
  have := Schedule.ticks_le_maxRate_mul _ sched_progressive h
  have e : sched.maxRate = 2200 := by decide
  rwa [e] at this
/-- Individual assessment: a couple splitting income could never pay less under a flat schedule than separately
(`splitting_le_separate`), and with a flat rate splitting gains nothing at all (`split_flat_eq`). -/
theorem split_ok (a b : Int) : splitting sched.ticks a b ≤ separate sched.ticks a b :=
  splitting_le_separate _ sched_convex sched_mono a b
/-- Above zero the flat schedule is exactly linear: 22 % of every cent. -/
theorem sched_linear {x : Int} (h : 0 ≤ x) : sched.ticks x = 2200 * x := by
  have := Schedule.ticks_const_rate sched 0 2200 x.toNat (fun i h1 _ => by
    simp only [sched, Schedule.flat, Schedule.rate, bandsRate, rate]; split <;> omega)
  have e : ((x.toNat : Nat) : Int) = x := Int.toNat_of_nonneg h
  have z : sched.ticks 0 = 0 := by decide
  rw [e, z] at this; simp only [Int.zero_add] at this; omega

/-! ## The basic exemption taper (§ 23(2)): the "tax hump" -/

theorem exemption_wf : basicExemption.WellFormed := by unfold Taper.WellFormed basicExemption; decide
theorem monthly_wf : monthlyExemption.WellFormed := by unfold Taper.WellFormed monthlyExemption; decide
theorem exemption_antitone {x y : Int} (h : x ≤ y) : basicExemption.amount y ≤ basicExemption.amount x :=
  Taper.amount_antitone _ exemption_wf h
theorem exemption_le_full (x : Int) : basicExemption.amount x ≤ 784800 :=
  Taper.amount_le_full _ exemption_wf x
/-- The band ends at 25 200 euro (2 520 000 cents). -/
theorem exemption_bandEnd : basicExemption.bandEnd = 2520000 := by decide
theorem exemption_zero_above {x : Int} (h : 2520000 ≤ x) : basicExemption.amount x = 0 := by
  simp only [Taper.amount, Taper.reduction, basicExemption, divR, pos]; omega
theorem exemption_full_below {x : Int} (h : x ≤ 1440000) : basicExemption.amount x = 784800 := by
  simp only [Taper.amount, Taper.reduction, basicExemption, divR, pos]; omega

/-- **The hump band's marginal rate** (kernel `Taper.taper_marginal`): for income x in the band (14 400 euro ≤ x,
x + 1.50 euro ≤ 25 200 euro) that is fully taxable (interest, rent, pension below pension age, …), 150 more cents of
income raise the tax ticks by 22 % × (150 + 109): an effective marginal rate of 22 % × 259/150 = 37.99 %. -/
theorem hump_marginal {inc : Int} (h1 : 1440000 ≤ inc) (h2 : inc + 150 < 2520000) :
    sched.ticks (taxableAfter (basicExemption.amount (inc + 150)) (inc + 150))
      - sched.ticks (taxableAfter (basicExemption.amount inc) inc) = 2200 * (150 + 109) := by
  have hw := exemption_wf
  have hin : basicExemption.floor < basicExemption.amount (inc + basicExemption.den) := by
    simp only [basicExemption, Taper.amount, Taper.reduction, divR, pos]; omega
  have hpos : basicExemption.amount inc ≤ inc := by
    have := Taper.amount_le_full basicExemption hw inc; simp only [basicExemption] at this ⊢; omega
  have := Taper.taper_marginal basicExemption hw sched 2200 h1 hin hpos (by
    intro i hi1 _
    simp only [basicExemption, Taper.amount, Taper.reduction, divR, taxableAfter, pos] at hi1
    simp only [Schedule.rate, sched, Schedule.flat, bandsRate, rate]
    split <;> omega)
  simpa [basicExemption] using this

/-- 37.99 % > 22 %: the band's effective marginal rate exceeds the statutory rate. -/
theorem hump_gt_rate : (2200 : Int) * 150 < 2200 * (150 + 109) := Taper.taper_marginal_gt 2200 150 109 (by decide) (by decide)

/-- Monthly withholding exemption = annual exemption / 12 up to cent rounding: for every monthly payment w,
12 × (monthly exemption at w) is between the annual exemption at 12 w and that plus 11 cents. -/
theorem monthly_even_bounds (w : Int) :
    basicExemption.amount (12 * w) ≤ 12 * monthlyExemption.amount w ∧
    12 * monthlyExemption.amount w ≤ basicExemption.amount (12 * w) + 11 := by
  simp only [Taper.amount, Taper.reduction, basicExemption, monthlyExemption, divR, pos]
  omega

/-! ## Contributions -/

theorem flat160_linear {w : Int} (h : 0 ≤ w) : (Schedule.flat 160).ticks w = 160 * w := by
  have := Schedule.ticks_const_rate (Schedule.flat 160) 0 160 w.toNat (fun i h1 _ => by
    simp only [Schedule.flat, Schedule.rate, bandsRate]; split <;> omega)
  have e : ((w.toNat : Nat) : Int) = w := Int.toNat_of_nonneg h
  have z : (Schedule.flat 160).ticks 0 = 0 := by decide
  rw [e, z] at this; simp only [Int.zero_add] at this; omega

/-- The employee's unemployment insurance is exactly 1.6 % of the wage (no floor, no ceiling). -/
theorem ui_linear {w : Int} (h : 0 ≤ w) : uiContribution.ticks w = 160 * w := by
  simp [Contribution.ticks, Contribution.base, uiContribution, uiEmployee, show ¬ w < 0 by omega, flat160_linear h]

end EeTax
