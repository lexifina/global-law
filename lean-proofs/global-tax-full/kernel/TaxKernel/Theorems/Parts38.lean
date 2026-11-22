import TaxKernel.Theorems.Schedule
import TaxKernel.Theorems.Parts
import TaxKernel.Multiplier
import TaxKernel.Family

/-!
# Generic theorems about the parts added in 1.2 (multipliers, average-rate tax, credit allocation, child scales,
# income attribution, low-band allowances, stepped tapers)

No `sorry`. Conditions on concrete parameters are discharged by `decide` / `omega` in the country files.
-/

set_option linter.deprecated false

namespace TaxKernel

/-! ## Lists of amounts -/

theorem foldl_add_init (l : List Int) (a : Int) : l.foldl (· + ·) a = a + l.foldl (· + ·) 0 := by
  induction l generalizing a with
  | nil => simp
  | cons x l ih =>
    simp only [List.foldl]
    rw [ih (a + x), ih (0 + x)]
    omega

theorem sumInts_nil : sumInts [] = 0 := rfl

theorem sumInts_cons (a : Int) (l : List Int) : sumInts (a :: l) = a + sumInts l := by
  unfold sumInts
  simp only [List.foldl]
  rw [foldl_add_init]
  omega

/-! ## Multipliers -/

/-- A multiplier with a non-negative rate and a monotone rounding rule is monotone in the base tax. -/
theorem Multiplier.amount_mono (m : Multiplier) (hr : 0 ≤ m.rate) (hs : 0 < m.round.step)
    (hm : m.round.mode.isMonotoneMode) {a b : Int} (h : a ≤ b) : m.amount a ≤ m.amount b :=
  Rule.ofTicks_mono _ hs hm (mul_le_mul_rate hr h)

/-- Charging an income at the average rate the tariff reaches on that same income gives the tariff. -/
theorem atAverageRate_self (f : Int → Int) {x : Int} (hx : 0 < x) : atAverageRate .down f x x = f x := by
  unfold atAverageRate
  rw [if_neg (by omega)]
  simp only [divR]
  exact Int.mul_ediv_cancel (f x) (by omega)

/-- Rate splitting with divisor 2 on an even income is splitting: twice the tariff on half. -/
theorem rateSplitting_two (f : Int → Int) {k : Int} (hk : 0 < k) : rateSplitting .down f 20000 (2 * k) = 2 * f k := by
  unfold rateSplitting
  have e : 2 * k * BP / 20000 = k := by
    unfold BP
    have : 2 * k * 10000 = k * 20000 := by omega
    rw [this]; exact Int.mul_ediv_cancel k (by decide)
  rw [e, atAverageRate, if_neg (by omega)]
  simp only [divR]
  have : f k * (2 * k) = (2 * f k) * k := by
    rw [← Int.mul_assoc, Int.mul_comm (f k) 2]
  rw [this]
  exact Int.mul_ediv_cancel _ (by omega)

/-- A credit allocated in order is never used for more than its amount. -/
theorem allocateOrdered_total_le (v : Int) (ts : List Int) : sumInts (allocateOrdered v ts) ≤ pos v := by
  induction ts generalizing v with
  | nil => simp only [allocateOrdered, sumInts_nil]; exact pos_nonneg v
  | cons t rest ih =>
    simp only [allocateOrdered]
    rw [sumInts_cons]
    have := ih (v - min (pos t) (pos v))
    have ht := pos_nonneg t
    unfold pos at *
    omega

/-- …and never for more than the tax it is set against. -/
theorem allocateOrdered_head_le (v t : Int) (rest : List Int) :
    (allocateOrdered v (t :: rest)).head? = some (min (pos t) (pos v)) := by
  simp [allocateOrdered]

/-! ## Income attribution, low-band allowance, spill -/

/-- Attribution between spouses moves income; it does not create or remove any. -/
theorem attributeIncome_sum (a b pct cap : Int) :
    (attributeIncome a b pct cap).1 + (attributeIncome a b pct cap).2 = a + b := by
  simp only [attributeIncome]; omega

theorem attributedAmount_bounds (a b pct cap : Int) :
    0 ≤ attributedAmount a b pct cap ∧ attributedAmount a b pct cap ≤ pos cap := by
  unfold attributedAmount
  generalize pct * (a + b) / BP - b = q
  unfold pos; omega

/-- **A zero band is never worth less than the same allowance given at the lowest rates** (convex schedule, no tax
on nothing): `s.ticks (x - a) ≤ s.ticks x - s.ticks a` for `0 ≤ a ≤ x`. The difference is what a higher earner
gains from the zero band (DE/AT/LU) and does not get from a low-band reduction (BE). -/
theorem lowBand_le_zeroBand (s : Schedule) (hp : s.progressive = true) {a x : Int} (ha : 0 ≤ a) (hax : a ≤ x) :
    s.ticks (x - a) ≤ s.ticks x - lowBandReduction s a := by
  have hc := Schedule.ticks_convex s hp
  have h0 : s.ticks 0 = 0 := s.ticks_zero (Schedule.progressive_parts hp).2.2.2
  have := separate_le_joint s.ticks hc h0 ha (by omega : 0 ≤ x - a)
  unfold separate joint at this
  unfold lowBandReduction
  rw [pos_of_nonneg ha]
  have e : a + (x - a) = x := by omega
  rw [e] at this
  omega

/-- With the allowance inside the income, tax after the low-band reduction is the tax on the slice above it. -/
theorem taxAfterLowBand_slice (s : Schedule) (hp : s.progressive = true) {a x : Int} (ha : 0 ≤ a) (hax : a ≤ x) :
    taxAfterLowBand s a x = s.sliceTicks a x := by
  have hm := Schedule.ticks_mono_of_progressive s hp a x hax
  unfold taxAfterLowBand lowBandReduction Schedule.sliceTicks
  rw [pos_of_nonneg ha, pos_of_nonneg (by omega)]

theorem spillAllowance_nonneg (allowance income rate : Int) (hr : 0 ≤ rate) :
    0 ≤ (spillAllowance allowance income rate).2 := by
  unfold spillAllowance unusedAllowance
  exact Int.ediv_nonneg (Int.mul_nonneg hr (pos_nonneg _)) (by decide)

/-! ## Stepped tapers -/

namespace SteppedTaper

/-- Complete steps never withdraw more than the proportional reading of the same words. -/
theorem proportional_le_stepped (t : SteppedTaper) (hw : t.WellFormed) (inc : Int) :
    t.toTaper.amount inc ≤ t.amount inc := by
  obtain ⟨hs, hp, _⟩ := hw
  unfold amount steps Taper.amount Taper.reduction toTaper
  simp only [divR]
  have he := pos_nonneg (inc - t.start)
  generalize pos (inc - t.start) = e at *
  have h1 : e / t.step * t.step ≤ e := Int.ediv_mul_le e (by omega)
  have h2 : t.perStep * (e / t.step) * t.step ≤ t.perStep * e := by
    rw [Int.mul_assoc]; exact Int.mul_le_mul_of_nonneg_left h1 hp
  have h3 : t.perStep * (e / t.step) ≤ t.perStep * e / t.step := (Int.le_ediv_iff_mul_le hs).2 h2
  omega

/-- **The staircase notch**: at the `k`-th step boundary (`k ≥ 1`), one more unit of income removes `perStep` at
once, while the amount is above its floor. -/
theorem stepped_notch (t : SteppedTaper) (hw : t.WellFormed) {k : Int} (hk : 1 ≤ k)
    (hf : t.floor ≤ t.full - t.perStep * k) :
    t.amount (t.start + k * t.step - 1) - t.amount (t.start + k * t.step) = t.perStep := by
  obtain ⟨hs, hp, _⟩ := hw
  have hks : t.step ≤ k * t.step := by
    have := Int.mul_le_mul_of_nonneg_right hk (by omega : 0 ≤ t.step); omega
  have s1 : t.steps (t.start + k * t.step - 1) = k - 1 := by
    unfold steps
    rw [pos_of_nonneg (by omega)]
    have : t.start + k * t.step - 1 - t.start = (t.step - 1) + (k - 1) * t.step := by
      rw [Int.sub_mul, Int.one_mul]; omega
    rw [this, Int.add_mul_ediv_right _ _ (by omega), Int.ediv_eq_zero_of_lt (by omega) (by omega)]
    omega
  have s2 : t.steps (t.start + k * t.step) = k := by
    unfold steps
    rw [pos_of_nonneg (by omega)]
    have : t.start + k * t.step - t.start = k * t.step := by omega
    rw [this]; exact Int.mul_ediv_cancel k (by omega)
  unfold amount
  rw [s1, s2, Int.mul_sub, Int.mul_one]
  omega

end SteppedTaper
end TaxKernel
