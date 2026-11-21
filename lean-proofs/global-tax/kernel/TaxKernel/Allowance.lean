import TaxKernel.Rounding

/-!
# TaxKernel.Allowance: fixed and withdrawn (tapered) allowances

A `Taper` is an amount `full` that is withdrawn by `num/den` of the excess of an income measure over `start`,
never below `floor`. The reduction is rounded by `round` (the statute's rule; UK ITA 2007 s. 35(3) rounds the
allowance *up* to £1, i.e. the reduction *down*):

    -- UK personal allowance 2025-26 (ITA 2007 s. 35(1)-(2)): £12,570, reduced by one-half of the excess over £100,000
    def ukPA : Taper := { full := 12570, start := 100000, num := 1, den := 2 }

A fixed allowance is `Taper.fixed a` (no withdrawal). Phase-outs of deductions, exemptions and zero-rate bands
are the same object. `Taper.amount t inc` is the allowance at income measure `inc`; `taxableAfter` deducts it.

Generic theorems (`TaxKernel.Theorems.Taper`): `amount_le_full`, `floor_le_amount`, `amount_antitone`
(more income never raises the allowance), `amount_step` (inside the band, `den` more units of income remove exactly
`num` of allowance), and `taper_marginal` (inside the band, a schedule with constant rate `r` charges
`r * (den + num)` on `den` more units: the effective marginal rate is `r * (1 + num/den)`, above the schedule's).
-/

namespace TaxKernel

structure Taper where
  /-- the allowance before withdrawal (units) -/
  full : Int
  /-- the income measure above which it is withdrawn -/
  start : Int := 0
  /-- withdrawal fraction `num/den` of the excess (UK: 1/2; `num := 0` for a fixed allowance) -/
  num : Int := 0
  den : Int := 1
  /-- the allowance never falls below this -/
  floor : Int := 0
  /-- rounding of the reduction `num * excess / den` -/
  round : Round := .down
  deriving Repr, DecidableEq, Inhabited

namespace Taper

/-- An allowance that is never withdrawn. -/
def fixed (a : Int) : Taper := { full := a }

/-- The reduction at income measure `inc` (before the floor). -/
def reduction (t : Taper) (inc : Int) : Int := divR t.round (t.num * pos (inc - t.start)) t.den

/-- The allowance at income measure `inc`. -/
def amount (t : Taper) (inc : Int) : Int := max t.floor (t.full - t.reduction inc)

/-- The income measure at which the allowance first reaches its floor (round-down reduction): the end of the
taper band. For `num > 0`. -/
def bandEnd (t : Taper) : Int := t.start + ceilDiv ((t.full - t.floor) * t.den) t.num

/-- The usual conditions: `0 < den`, `0 ≤ num`, `floor ≤ full`, round-down reduction. -/
def WellFormed (t : Taper) : Prop := 0 < t.den ∧ 0 ≤ t.num ∧ t.floor ≤ t.full ∧ t.round = .down

end Taper

/-- Income left after an allowance (never negative). -/
def taxableAfter (allowance income : Int) : Int := pos (income - allowance)

/-- The allowance actually used: no more than the income it is set against. -/
def usedAllowance (allowance income : Int) : Int := min (pos allowance) (pos income)

/-- What is left of an allowance after setting it against `income` (to transfer to a spouse, carry forward, …). -/
def unusedAllowance (allowance income : Int) : Int := pos (allowance - pos income)

/-- A deduction capped at `cap` units and at `pct` basis points of a base (e.g. pension contributions limited to
the lower of an amount and a share of earnings). `cap < 0` means no cap. -/
def cappedDeduction (claimed cap pct base : Int) : Int :=
  let byPct := pct * pos base / BP
  let c := min (pos claimed) byPct
  if cap < 0 then c else min c cap

end TaxKernel
