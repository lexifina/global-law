/-!
# TaxKernel.Basic: units and the arithmetic every part uses

Conventions (the same as the five existing models):
* **Money** is `Int` in whole units of the statute's own unit of account (euro, pound, yen, cents if the statute
  computes in cents). Plain `Int` everywhere, no type synonyms in signatures, so `omega` sees every amount.
* **Rates** are `Int` in **basis points** (2000 = 20 %, 875 = 8.75 %, 3935 = 39.35 %).
* **Ticks**: tax before rounding is `Int` in units × basis points (1/10000 of a unit). `Rounding` turns ticks
  into units by the statute's own rule.
-/

namespace TaxKernel

/-- Basis points in one whole (100 %). -/
def BP : Int := 10000

/-- The positive part, `max 0 x`. -/
def pos (x : Int) : Int := max 0 x

/-- `x` clamped into `[lo, hi]` (assumes `lo ≤ hi`; otherwise `hi` wins). -/
def clamp (lo hi x : Int) : Int := min hi (max lo x)

/-- Length of the part of `[a, b]` that lies in `[lo, hi]` (0 if they do not meet). -/
def overlap (a b lo hi : Int) : Int := pos (min b hi - max a lo)

/-- Length of the part of `[a, b]` that lies above `lo`. -/
def above (a b lo : Int) : Int := pos (b - max a lo)

/-- `⌈a / b⌉` for `b > 0` (Lean's `Int` division rounds towards −∞ for a positive divisor). -/
def ceilDiv (a b : Int) : Int := -((-a) / b)

/-- `rate` (basis points) applied to `x` units, in ticks. -/
def ticksOf (rate x : Int) : Int := rate * x

theorem pos_nonneg (x : Int) : 0 ≤ pos x := by unfold pos; omega
theorem pos_of_nonneg {x : Int} (h : 0 ≤ x) : pos x = x := by unfold pos; omega
theorem pos_of_nonpos {x : Int} (h : x ≤ 0) : pos x = 0 := by unfold pos; omega
theorem pos_mono {a b : Int} (h : a ≤ b) : pos a ≤ pos b := by unfold pos; omega
theorem le_pos (x : Int) : x ≤ pos x := by unfold pos; omega
theorem pos_sub_le {a b : Int} (h : a ≤ b) : pos b - pos a ≤ b - a := by unfold pos; omega
theorem overlap_nonneg (a b lo hi : Int) : 0 ≤ overlap a b lo hi := pos_nonneg _
theorem above_nonneg (a b lo : Int) : 0 ≤ above a b lo := pos_nonneg _

theorem ceilDiv_mono {a a' b : Int} (hb : 0 < b) (h : a ≤ a') : ceilDiv a b ≤ ceilDiv a' b := by
  unfold ceilDiv
  have : (-a') / b ≤ (-a) / b := Int.ediv_le_ediv hb (by omega)
  omega

/-- Multiplying by a non-negative rate preserves order (the step every monotonicity proof needs). -/
theorem mul_le_mul_rate {r a b : Int} (hr : 0 ≤ r) (h : a ≤ b) : r * a ≤ r * b :=
  Int.mul_le_mul_of_nonneg_left h hr

theorem mul_nonneg' {r a : Int} (hr : 0 ≤ r) (ha : 0 ≤ a) : 0 ≤ r * a := Int.mul_nonneg hr ha

end TaxKernel
