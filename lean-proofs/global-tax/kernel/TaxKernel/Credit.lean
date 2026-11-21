import TaxKernel.Allowance

/-!
# TaxKernel.Credit: tax credits (refundable and not), with phase-in and income-tested withdrawal

A credit is subtracted from tax, not from income. `Credit.value c earn inc` is its amount for earnings `earn`
(the phase-in base) and income measure `inc` (the withdrawal base):

    value = min (phase-in) (taper)
    phase-in = full                          if inRate = 0
             = min full (inRate * earn / BP)  otherwise (US EITC-style)
    taper = max floor (full − num/den · (inc − start)⁺)   (the `Taper` of `Allowance`)

Non-refundable credits reduce tax to no less than 0; refundable credits are paid out (tax may go negative):
`applyCredits tax nonref ref = max 0 (tax − Σ nonref) − Σ ref`. The order matters where a statute names one
(ITA 2007 s. 26 orders reliefs; IRC credits are ordered by §26); `applyCreditsOrdered` applies a list in order,
each non-refundable credit limited to the tax left.

Generic theorems (`TaxKernel.Theorems.Credit`): `applyCredits_nonneg_of_no_refund`, `value_le_full`,
`value_antitone_inc` (withdrawal never raises the credit), and the withdrawal band raises the marginal rate by
`num/den` exactly as a taper does.
-/

namespace TaxKernel

structure Credit where
  /-- maximum amount (units) -/
  full : Int
  /-- phase-in rate on earnings, bp (0: no phase-in, the full amount from the first unit) -/
  inRate : Int := 0
  /-- withdrawal: start, fraction `num/den`, floor, rounding (as `Taper`) -/
  start : Int := 0
  num : Int := 0
  den : Int := 1
  floor : Int := 0
  round : Round := .down
  refundable : Bool := false
  deriving Repr, DecidableEq, Inhabited

namespace Credit

def taper (c : Credit) : Taper :=
  { full := c.full, start := c.start, num := c.num, den := c.den, floor := c.floor, round := c.round }

def phaseIn (c : Credit) (earn : Int) : Int :=
  if c.inRate = 0 then c.full else min c.full (c.inRate * pos earn / BP)

/-- The credit for earnings `earn` and withdrawal income `inc`. -/
def value (c : Credit) (earn inc : Int) : Int := min (c.phaseIn earn) (c.taper.amount inc)

end Credit

def sumInts (l : List Int) : Int := l.foldl (· + ·) 0

/-- Tax after non-refundable credits (to no less than 0) and then refundable ones (paid out). -/
def applyCredits (tax : Int) (nonref ref : List Int) : Int :=
  max 0 (tax - sumInts nonref) - sumInts ref

/-- Apply credits one at a time in the statute's order: a non-refundable one is limited to the tax left, a
refundable one is taken in full. Returns the tax after all of them (negative = paid out). -/
def applyCreditsOrdered (tax : Int) : List (Int × Bool) → Int
  | [] => tax
  | (v, false) :: rest => applyCreditsOrdered (tax - min (pos tax) (pos v)) rest
  | (v, true) :: rest => applyCreditsOrdered (tax - v) rest

/-- How much of a non-refundable credit `v` is used against tax `t ≥ 0` (the rest is wasted unless the statute
lets it transfer or carry forward: a frequent design difference). -/
def usedCredit (t v : Int) : Int := min (pos t) (pos v)

end TaxKernel
