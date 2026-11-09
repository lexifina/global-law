import LegalProofs.USTax.Model

/-!
# The rate schedule never takes more than the extra dollar

For every filing status and every taxable income, one more dollar of taxable income raises the schedule tax by at
most one dollar; so income tax from the schedule alone can never make a household worse off for earning more.
Proved for all incomes, not tested: `omega` decides the linear arithmetic after the closed form is unfolded.
-/

set_option maxRecDepth 200000

namespace Legal.USTax

/-- 1 when `x` lies in the bracket `[lo, hi)`, else 0. -/
def ind (lo hi x : Nat) : Nat := if lo ≤ x ∧ x < hi then 1 else 0

/-- One more dollar adds a band's rate exactly when `x` is inside that band. -/
theorem band_succ (r lo hi x : Nat) (h : lo ≤ hi) : band r lo hi (x + 1) = band r lo hi x + r * ind lo hi x := by
  unfold band ind
  by_cases hc : lo ≤ x ∧ x < hi
  · rw [ite_eq_left_iff.mpr (fun h' => absurd hc h'), Nat.min_eq_left (by omega), Nat.min_eq_left (by omega),
      show x + 1 - lo = x - lo + 1 by omega, Nat.mul_succ, Nat.mul_one]
  · rw [ite_eq_right_iff.mpr (fun h' => absurd h' hc), Nat.mul_zero, Nat.add_zero]
    by_cases hx : x < lo
    · rw [show x + 1 - lo = 0 by omega, show x - lo = 0 by omega, Nat.add_zero]
    · rw [Nat.min_eq_right (by omega), Nat.min_eq_right (by omega), Nat.add_zero]

theorem top_succ (f x : Nat) : 37 * (x + 1 - f) = 37 * (x - f) + 37 * (if f ≤ x then 1 else 0) := by
  split
  · rw [show x + 1 - f = x - f + 1 by omega, Nat.mul_succ, Nat.mul_one]
  · rw [show x + 1 - f = 0 by omega, show x - f = 0 by omega]

/-- At most one bracket contains `x`. -/
theorem one_bracket (a b c d e f x : Nat) (h : a ≤ b ∧ b ≤ c ∧ c ≤ d ∧ d ≤ e ∧ e ≤ f) :
    ind 0 a x + ind a b x + ind b c x + ind c d x + ind d e x + ind e f x + (if f ≤ x then 1 else 0) ≤ 1 := by
  unfold ind
  repeat' split
  all_goals omega

/-- For any schedule with ordered edges, one more dollar adds at most the top rate (37 hundredths). -/
theorem sched_step (a b c d e f x : Nat) (h : a ≤ b ∧ b ≤ c ∧ c ≤ d ∧ d ≤ e ∧ e ≤ f) :
    sched a b c d e f (x + 1) ≤ sched a b c d e f x + 37 := by
  have h1 := one_bracket a b c d e f x h
  unfold sched
  rw [band_succ 10 0 a x (Nat.zero_le _), band_succ 12 a b x h.1, band_succ 22 b c x h.2.1,
    band_succ 24 c d x h.2.2.1, band_succ 32 d e x h.2.2.2.1, band_succ 35 e f x h.2.2.2.2, top_succ f x]
  generalize ind 0 a x = i0 at *
  generalize ind a b x = i1 at *
  generalize ind b c x = i2 at *
  generalize ind c d x = i3 at *
  generalize ind d e x = i4 at *
  generalize ind e f x = i5 at *
  generalize (if f ≤ x then 1 else 0) = i6 at *
  omega

theorem sched_mono (a b c d e f x : Nat) (h : a ≤ b ∧ b ≤ c ∧ c ≤ d ∧ d ≤ e ∧ e ≤ f) :
    sched a b c d e f x ≤ sched a b c d e f (x + 1) := by
  unfold sched
  rw [band_succ 10 0 a x (Nat.zero_le _), band_succ 12 a b x h.1, band_succ 22 b c x h.2.1,
    band_succ 24 c d x h.2.2.1, band_succ 32 d e x h.2.2.2.1, band_succ 35 e f x h.2.2.2.2, top_succ f x]
  omega

/-- The (unrounded) 2025 schedule rises by at most 37 hundredths of a dollar per dollar, for every filing status. -/
theorem schedule100_step (s : Status) (x : Nat) : schedule100 s (x + 1) ≤ schedule100 s x + 37 := by
  cases s
  · exact sched_step _ _ _ _ _ _ x (by decide)
  · exact sched_step _ _ _ _ _ _ x (by decide)
  · exact sched_step _ _ _ _ _ _ x (by decide)

/-- **No bracket cliff.** One more dollar of taxable income costs at most one dollar of schedule tax. -/
theorem scheduleTax_step (s : Status) (x : Nat) : scheduleTax s (x + 1) ≤ scheduleTax s x + 1 := by
  have h := schedule100_step s x
  unfold scheduleTax
  omega

/-- And the schedule is monotone: more taxable income never means less tax. -/
theorem schedule100_mono (s : Status) (x : Nat) : schedule100 s x ≤ schedule100 s (x + 1) := by
  cases s
  · exact sched_mono _ _ _ _ _ _ x (by decide)
  · exact sched_mono _ _ _ _ _ _ x (by decide)
  · exact sched_mono _ _ _ _ _ _ x (by decide)

end Legal.USTax
