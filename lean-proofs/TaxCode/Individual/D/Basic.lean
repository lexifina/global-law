import TaxCode.Individual.Household

/-!
# Group D (credits): shared helpers

Whole dollars are `Int`. Rates are basis points (1/10000) unless a docstring says otherwise.

Rounding. The Code says almost nothing about rounding credits to whole dollars; the IRS forms tell filers to round
every line to the nearest dollar (50 cents and up rounds up). We use `roundDollar` (half up, from `Household.lean`)
for that form rounding and keep an exact, unrounded "scaled" version of a provision wherever a proof compares the
statute with the form.
-/

namespace TaxCode.Individual.D
open TaxCode.Individual

/-- The positive part, `max 0 x` ("the excess (if any)", "but not below zero"). -/
def pos (x : Int) : Int := max 0 x

/-- `⌈x / d⌉` for `x ≥ 0`, `d > 0`: the number of steps of `d` "or fraction thereof" in `x`. -/
def ceilDiv (x d : Int) : Int := (x + d - 1) / d

/-- `rate` basis points of `x`, rounded to the nearest dollar (the forms' rounding). -/
def pctRound (x rate : Int) : Int := roundDollar (x * rate) 10000

theorem pos_nonneg (x : Int) : 0 ≤ pos x := by unfold pos; omega

end TaxCode.Individual.D
