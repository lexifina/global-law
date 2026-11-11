import TaxCode.Individual.Household

/-!
# Tax Court library: shared helpers

The rules in this folder are the individual-income-tax rules that U.S. Tax Court cases most often turn on, written
from the statute **as it stood for each tax year 2016–2024**, so that a court's findings of fact can be encoded and its
holdings recomputed.

Conventions (as in `TaxCode/Individual`):
* amounts are whole dollars (`Int`); rates are basis points (1/10,000) unless a docstring says otherwise;
* forms round each computed line to the nearest dollar, half up (`roundDollar`);
* a "fact" is something a court finds; a rule is a function from facts to a legal consequence.
-/

namespace Legal.USTax.TaxCourt
open TaxCode.Individual

export TaxCode.Individual (Filing roundDollar)

/-- The positive part: "the excess (if any)", "but not below zero". -/
def pos (x : Int) : Int := max 0 x

/-- `⌈x / d⌉` for `x ≥ 0`, `d > 0`: the number of steps of `d` "or fraction thereof" in `x`. -/
def ceilDiv (x d : Int) : Int := (x + d - 1) / d

/-- `rate` basis points of `x`, rounded to the nearest dollar. -/
def pctRound (x rate : Int) : Int := roundDollar (x * rate) 10000

theorem pos_nonneg (x : Int) : 0 ≤ pos x := by unfold pos; omega

/-! ## Dates -/

/-- A calendar date. -/
structure Date where
  y : Int
  m : Int
  d : Int
  deriving Repr, DecidableEq, Inhabited

/-- Days since a fixed epoch (proleptic Gregorian, March-based years; valid for years ≥ 1). -/
def Date.days (dt : Date) : Int :=
  let y := if dt.m ≤ 2 then dt.y - 1 else dt.y
  let mp := (dt.m + 9) % 12
  let doy := (153 * mp + 2) / 5 + dt.d - 1
  365 * y + y / 4 - y / 100 + y / 400 + doy

def Date.le (a b : Date) : Bool := a.days ≤ b.days

/-- Days from `a` to `b` (negative if `b` is earlier). -/
def daysBetween (a b : Date) : Int := b.days - a.days

/-- "For each month or fraction thereof" from `start` (exclusive) to `stop`: zero if `stop` is on or before `start`;
otherwise the number of whole months elapsed, plus one if any part of a further month has elapsed. A month runs from a
day of one month to the same day of the next (a period ending 15 May counted from 15 April is one month). -/
def monthsOrFraction (start stop : Date) : Int :=
  if stop.days ≤ start.days then 0
  else
    let k := (stop.y - start.y) * 12 + (stop.m - start.m)
    if stop.d > start.d then k + 1 else k

#guard monthsOrFraction ⟨2018, 4, 17⟩ ⟨2018, 4, 17⟩ = 0
#guard monthsOrFraction ⟨2018, 4, 17⟩ ⟨2018, 4, 18⟩ = 1
#guard monthsOrFraction ⟨2018, 4, 17⟩ ⟨2018, 5, 17⟩ = 1
#guard monthsOrFraction ⟨2018, 4, 17⟩ ⟨2018, 5, 18⟩ = 2
#guard monthsOrFraction ⟨2018, 4, 17⟩ ⟨2019, 1, 2⟩ = 9
#guard daysBetween ⟨2020, 2, 28⟩ ⟨2020, 3, 1⟩ = 2
#guard daysBetween ⟨2019, 2, 28⟩ ⟨2019, 3, 1⟩ = 1
#guard daysBetween ⟨2016, 1, 1⟩ ⟨2017, 1, 1⟩ = 366

/-- The number of days in calendar year `y` (for "more than one-half of the taxable year"). -/
def daysInYear (y : Int) : Int := daysBetween ⟨y, 1, 1⟩ ⟨y + 1, 1, 1⟩

end Legal.USTax.TaxCourt
