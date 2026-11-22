import CYTax.Basic

/-! # Kernel one-liners instantiated for Cyprus, and properties the statutes claim -/

namespace CYTax
open TaxKernel

/-! ## ITL Second Schedule 1(β) (2025) and 1(γ) (2026): progressive, monotone, convex, no jump, ≤ 35 % -/
theorem scale_progressive : scale2025.progressive = true := by decide
theorem scale_ratesNonneg' : scale2025.RatesNonneg := (Schedule.progressive_parts scale_progressive).2.2.1
theorem scale_losNonneg' : scale2025.LosNonneg := (Schedule.progressive_parts scale_progressive).2.2.2
theorem scale_mono : Monotone' scale2025.ticks := Schedule.ticks_mono_of_progressive _ scale_progressive
theorem scale_convex : Convex scale2025.ticks := Schedule.ticks_convex _ scale_progressive
theorem scale_marginal (x : Int) : scale2025.ticks (x + 1) - scale2025.ticks x = scale2025.rate x :=
  Schedule.ticks_succ _ x
theorem scale_no_jump {x y : Int} (h : x ≤ y) :
    scale2025.ticks y - scale2025.ticks x ≤ scale2025.maxRate * (y - x) :=
  (Schedule.ticks_lipschitz_of_progressive _ scale_progressive h).2
theorem scale_le_top {x : Int} (h : 0 ≤ x) : scale2025.ticks x ≤ 3500 * x := by
  have := Schedule.ticks_le_maxRate_mul _ scale_progressive h
  have e : scale2025.maxRate = 3500 := by decide
  rwa [e] at this
theorem scale_rate_le_top (x : Int) : scale2025.rate x ≤ 3500 := by
  have := Schedule.rate_le_max _ scale_progressive x
  have e : scale2025.maxRate = 3500 := by decide
  rwa [e] at this
/-- "Για κάθε ευρώ μέχρι €19.500 0%": no tax on a taxable income up to 19.500,00 €. -/
theorem scale_zero_band {x : Int} (h : x ≤ 1950000) : scale2025.ticks x = 0 := by
  by_cases h0 : x ≤ 0
  · exact Schedule.ticks_of_nonpos _ scale_losNonneg' h0
  · have hm := scale_mono x 1950000 h
    have hn := Schedule.ticks_nonneg scale2025 scale_ratesNonneg' scale_losNonneg' x
    have hz : scale2025.ticks 1950000 = 0 := by decide
    omega
theorem scale26_progressive : scale2026.progressive = true := by decide
theorem scale26_mono : Monotone' scale2026.ticks := Schedule.ticks_mono_of_progressive _ scale26_progressive
theorem scale26_convex : Convex scale2026.ticks := Schedule.ticks_convex _ scale26_progressive

/-- Individual taxation (no joint return): for the convex Cyprus scale two separate assessments never cost more
than one aggregated return would (kernel `separate_le_joint`): Cyprus has no marriage penalty in income tax. -/
theorem separate_le_aggregated {a b : Int} (ha : 0 ≤ a) (hb : 0 ≤ b) :
    separate scale2025.ticks a b ≤ joint scale2025.ticks a b :=
  separate_le_joint _ scale_convex (Schedule.ticks_zero _ scale_losNonneg') ha hb

/-! ## Contributions: ceilings and caps -/
/-- SIL: above the 2025 ceiling (66.612 €) the employee contribution is constant (5.861,86 € at 8,8 %). -/
theorem si_above_ceiling {w : Int} (h : siCeiling ≤ w) : siEmployee {} w = 586186 := by
  unfold siEmployee
  simp only [show siCeilingFor ({} : Opts).year = siCeiling by decide,
    show siEmployeeRateFor ({} : Opts).year ({} : Opts).statuteSI = siEmployeeRate by decide]
  rw [show min (pos w) siCeiling = siCeiling by simp only [pos, siCeiling] at h ⊢; omega]
  decide
/-- GESY art. 19(4): the four bases never exceed €180.000 together. -/
theorem gesy_cap (w s p inc : Int) :
    let b := gesyBases w s p inc
    b.1 + b.2.1 + b.2.2.1 + b.2.2.2 ≤ gesyCap := by
  simp only [gesyBases, pos, gesyCap]; omega
/-- ITL art. 14 proviso (ii): the deduction never exceeds one fifth of the income before it, and is never
negative when the contributions are not. -/
theorem art14_le_fifth (o : Opts) (x : Person) : 5 * (person o x).art14 ≤ (person o x).ti0 := by
  have h1 : (person o x).art14 = min (person o x).art14Claim (person o x).art14Cap := rfl
  have h2 : (person o x).art14Cap = (person o x).ti0 * 1 / 5 := rfl
  have h3 : (person o x).ti0 =
      pos ((x.w - exemption x.ex x.w) + x.s + x.p + (x.r - mulBp x.r rentDeduction) - pos x.c) := rfl
  have h4 : 0 ≤ (person o x).ti0 := by rw [h3]; exact Int.le_max_left _ _
  have h5 := Int.min_le_right (person o x).art14Claim (person o x).art14Cap
  omega
/-- ITL art. 8(21Α): the exemption is at most 8.550 € whatever the remuneration. -/
theorem ex21A_le_cap (w : Int) : exemption "21A" w ≤ ex21ACap := by
  show (if ("21A" == "21A") = true then min (mulBp w ex21ARate) ex21ACap else _) ≤ ex21ACap
  rw [ite_cond_eq_true _ _ (by decide)]; exact Int.min_le_right _ _

end CYTax
