/-!
# Basic arithmetic for the UK income tax

Money is held in whole **pence** (`Int`). Incomes arrive in whole pounds (the canonical household and the Self
Assessment return both use whole pounds) and are multiplied by 100; pence are needed because Gift Aid is "grossed
up by reference to the basic rate" (ITA 2007 s. 58(2), s. 415), so a £1 gift is £1.25 gross.

Rates are in **basis points** (2000 = 20 %, 875 = 8.75 %, 3935 = 39.35 %). Tax is first computed exactly in
**ticks**, one ten-thousandth of a penny: an amount in pence times a rate in basis points. The Income Tax Acts
contain no general rounding rule for the liability; the Act rounds only where it says so:

* ITA 2007 s. 35(3): a tapered personal allowance that "would otherwise not be a multiple of £1, it is to be
  rounded up to the nearest amount which is a multiple of £1";
* ITA 2007 s. 55B(5): the marriage-allowance transferable amount is rounded up to a multiple of £10;
* ITEPA 2003 s. 681C(3): the child benefit total, the charge and the percentage of the high income child benefit
  charge are "rounded down to the nearest whole number".

A liability is reported in pence, rounded down (`ticksToPence`); the only rates that leave fractions of a penny
on whole pounds are 8.75 % and 33.75 %.
-/

namespace UkTax

/-! Units. Money is `Int` in whole pence; tax before rounding is `Int` in ticks (one ten-thousandth of a penny,
pence × basis points). Plain `Int` everywhere (no type synonyms), so that `omega` sees every amount. -/

/-- The positive part, `max 0 x`. -/
def pos (x : Int) : Int := max 0 x

/-- Length of the part of `[a, b]` that lies in `[lo, hi]` (0 if they do not meet). -/
def overlap (a b lo hi : Int) : Int := pos (min b hi - max a lo)

/-- Length of the part of `[a, b]` that lies above `lo`. -/
def above (a b lo : Int) : Int := pos (b - max a lo)

/-- `⌈a / b⌉` for `b > 0` (Lean's `Int` division rounds towards −∞ for a positive divisor). -/
def ceilDiv (a b : Int) : Int := -((-a) / b)

/-- Ticks to whole pence, rounded down. -/
def ticksToPence (t : Int) : Int := t / 10000

/-- Pounds to pence. -/
def gbp (x : Int) : Int := 100 * x

theorem pos_nonneg (x : Int) : 0 ≤ pos x := by unfold pos; omega

theorem pos_mono {a b : Int} (h : a ≤ b) : pos a ≤ pos b := by unfold pos; omega

theorem overlap_nonneg (a b lo hi : Int) : 0 ≤ overlap a b lo hi := pos_nonneg _

theorem above_nonneg (a b lo : Int) : 0 ≤ above a b lo := pos_nonneg _

/-- Rounding down to the penny is monotone. -/
theorem ticksToPence_mono {a b : Int} (h : a ≤ b) : ticksToPence a ≤ ticksToPence b := by
  unfold ticksToPence; exact Int.ediv_le_ediv (by omega) h

theorem ceilDiv_mono {a a' b : Int} (hb : 0 < b) (h : a ≤ a') : ceilDiv a b ≤ ceilDiv a' b := by
  unfold ceilDiv
  have : (-a') / b ≤ (-a) / b := Int.ediv_le_ediv hb (by omega)
  omega

end UkTax
