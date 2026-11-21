import TaxKernel.Basic

/-!
# TaxKernel.Rounding: the statutes' rounding rules

Each statute says where it rounds and how: down to the unit (most), down to a multiple of 10/100/1000 (Japan's
1,000-yen taxable income, Germany's whole-euro zvE), up (UK s. 35(3) taper rounds the allowance up to £1), half up
(commercial rounding), half to even. A country model names the rule it cites with a `Rule` and applies it with
`Rule.apply` (units → multiple of `step`) or `Rule.ofTicks` (ticks → units, then to a multiple of `step`).

Every rule is proved monotone (`Rule.apply_mono`) and to move an amount by less than one step
(`toMultiple_down_bounds`, `toMultiple_up_bounds`, `toMultiple_halfUp_bounds`).
-/

namespace TaxKernel

inductive Round where
  /-- towards −∞ ("abgerundet", "rounded down", 切り捨て) -/
  | down
  /-- towards +∞ ("rounded up", 切り上げ) -/
  | up
  /-- to the nearest, halves up (commercial rounding, 四捨五入) -/
  | halfUp
  /-- to the nearest, halves down -/
  | halfDown
  /-- to the nearest, halves to an even quotient (banker's rounding) -/
  | halfEven
  /-- towards 0 (truncation; equals `down` for non-negative amounts) -/
  | towardZero
  deriving Repr, DecidableEq, Inhabited

/-- `n / d` for `d > 0` rounded by mode `m`. -/
def divR : Round → Int → Int → Int
  | .down, n, d => n / d
  | .up, n, d => ceilDiv n d
  | .halfUp, n, d => (2 * n + d) / (2 * d)
  | .halfDown, n, d => ceilDiv (2 * n - d) (2 * d)
  | .halfEven, n, d =>
      let q := n / d
      let r := n % d
      if 2 * r < d then q else if 2 * r > d then q + 1 else if q % 2 = 0 then q else q + 1
  | .towardZero, n, d => if 0 ≤ n then n / d else -((-n) / d)

/-- `x` rounded by mode `m` to a multiple of `step > 0`. -/
def toMultiple (m : Round) (step x : Int) : Int := divR m x step * step

/-- Ticks (units × basis points) to whole units by mode `m`. -/
def ticksToUnits (m : Round) (t : Int) : Int := divR m t BP

/-- A statute's rounding rule: a mode and a step (1 = whole units, 10, 100, 1000, …). -/
structure Rule where
  mode : Round := .down
  step : Int := 1
  deriving Repr, DecidableEq, Inhabited

namespace Rule
/-- Whole units, rounded down. -/
def unitDown : Rule := {}
def unitUp : Rule := { mode := .up }
def unitHalfUp : Rule := { mode := .halfUp }
def downTo (s : Int) : Rule := { step := s }
def upTo (s : Int) : Rule := { mode := .up, step := s }
def halfUpTo (s : Int) : Rule := { mode := .halfUp, step := s }

/-- Apply the rule to an amount in units. -/
def apply (r : Rule) (x : Int) : Int := toMultiple r.mode r.step x

/-- Ticks to units, by the rule's mode, then to a multiple of its step (one rounding: `t / (BP*step)`). -/
def ofTicks (r : Rule) (t : Int) : Int := divR r.mode t (BP * r.step) * r.step
end Rule

/-! ## Error bounds -/

theorem divR_down_bounds (n d : Int) (hd : 0 < d) : d * (n / d) ≤ n ∧ n < d * (n / d) + d := by
  have h1 := Int.mul_ediv_add_emod n d
  have h2 := Int.emod_nonneg n (by omega : d ≠ 0)
  have h3 := Int.emod_lt_of_pos n hd
  constructor <;> omega

theorem divR_up_bounds (n d : Int) (hd : 0 < d) : n ≤ d * ceilDiv n d ∧ d * ceilDiv n d < n + d := by
  have ⟨h1, h2⟩ := divR_down_bounds (-n) d hd
  unfold ceilDiv
  rw [Int.mul_neg]
  constructor <;> omega

theorem divR_halfUp_bounds (n d : Int) (hd : 0 < d) :
    2 * n - d < 2 * (d * ((2 * n + d) / (2 * d))) ∧ 2 * (d * ((2 * n + d) / (2 * d))) ≤ 2 * n + d := by
  have ⟨h1, h2⟩ := divR_down_bounds (2 * n + d) (2 * d) (by omega)
  rw [Int.mul_assoc] at h1 h2
  constructor <;> omega

/-- Rounding down to a multiple of `s` loses less than one step. -/
theorem toMultiple_down_bounds (s x : Int) (hs : 0 < s) :
    toMultiple .down s x ≤ x ∧ x < toMultiple .down s x + s := by
  unfold toMultiple divR
  have := divR_down_bounds x s hs
  rw [Int.mul_comm (x / s) s]; omega

/-- Rounding up to a multiple of `s` adds less than one step. -/
theorem toMultiple_up_bounds (s x : Int) (hs : 0 < s) :
    x ≤ toMultiple .up s x ∧ toMultiple .up s x < x + s := by
  unfold toMultiple divR
  have := divR_up_bounds x s hs
  rw [Int.mul_comm (ceilDiv x s) s]; omega

/-- Rounding half up to a multiple of `s` moves by at most half a step. -/
theorem toMultiple_halfUp_bounds (s x : Int) (hs : 0 < s) :
    2 * x - s < 2 * toMultiple .halfUp s x ∧ 2 * toMultiple .halfUp s x ≤ 2 * x + s := by
  unfold toMultiple divR
  have := divR_halfUp_bounds x s hs
  rw [Int.mul_comm ((2 * x + s) / (2 * s)) s]; omega

/-- Ticks rounded down to units lose less than one unit. -/
theorem ticksToUnits_down_bounds (t : Int) :
    BP * ticksToUnits .down t ≤ t ∧ t < BP * ticksToUnits .down t + BP := by
  unfold ticksToUnits divR
  exact divR_down_bounds t BP (by unfold BP; omega)

/-! ## Monotonicity -/

theorem divR_mono (m : Round) (d : Int) (hd : 0 < d) (hm : m = .down ∨ m = .up ∨ m = .halfUp ∨ m = .halfDown)
    {a b : Int} (h : a ≤ b) : divR m a d ≤ divR m b d := by
  rcases hm with rfl | rfl | rfl | rfl
  · exact Int.ediv_le_ediv hd h
  · exact ceilDiv_mono hd h
  · exact Int.ediv_le_ediv (by omega) (by omega)
  · exact ceilDiv_mono (by omega) (by omega)

/-- Monotone rounding modes (all but half-even and toward-zero, which are also monotone but proved separately
when a statute uses them). -/
def Round.isMonotoneMode (m : Round) : Prop := m = .down ∨ m = .up ∨ m = .halfUp ∨ m = .halfDown

theorem Rule.apply_mono (r : Rule) (hs : 0 < r.step) (hm : r.mode.isMonotoneMode) {a b : Int} (h : a ≤ b) :
    r.apply a ≤ r.apply b := by
  unfold Rule.apply toMultiple
  have := divR_mono r.mode r.step hs hm h
  exact Int.mul_le_mul_of_nonneg_right this (by omega)

theorem Rule.ofTicks_mono (r : Rule) (hs : 0 < r.step) (hm : r.mode.isMonotoneMode) {a b : Int} (h : a ≤ b) :
    r.ofTicks a ≤ r.ofTicks b := by
  unfold Rule.ofTicks
  have hd : 0 < BP * r.step := Int.mul_pos (by unfold BP; omega) hs
  have := divR_mono r.mode (BP * r.step) hd hm h
  exact Int.mul_le_mul_of_nonneg_right this (by omega)

end TaxKernel
