import TaxKernel.Rounding

/-!
# TaxKernel.Schedule: progressive brackets

A schedule is a list of bands `⟨lo, rate⟩`: income above `lo` (up to the next band's `lo`) is charged at `rate`
basis points. Write them in the statute's order, lowest threshold first, e.g. the UK 2025-26 rates on taxable
income (ITA 2007 s. 10; FA 2025 s. 1–2):

    Schedule.ofList [(0, 2000), (37700, 4000), (125140, 4500)]

or with upper limits as many statutes print them (Canada ITA s. 117(2): 15 % up to $57,375, …):

    Schedule.ofUpper [(57375, 1500), (114750, 2050), (177882, 2600), (253414, 2900)] 3300

`Schedule.ticks s x` is the exact tax on `x` in ticks (units × bp); `Schedule.tax s rule x` rounds it by the
statute's rule. `Schedule.rate s x` is the marginal rate on the unit `(x, x+1]`.

Generic theorems (`TaxKernel.Theorems.Schedule`): `ticks_mono` (non-negative rates ⇒ monotone),
`ticks_succ` (the increment from `x` to `x+1` is exactly `rate s x`, for every list of bands),
`rate_le_of_sorted` / `ticks_lipschitz` (no jump: tax rises by at most the top rate per unit),
`ticks_le_maxRate_mul` (tax ≤ max rate × income), `ticks_zero` (tax of 0 is 0), `ticks_convex` (non-decreasing
rates ⇒ convex, the condition of the splitting theorem).
-/

namespace TaxKernel

structure Band where
  /-- income above this threshold (units) is charged at `rate` up to the next band's threshold -/
  lo : Int
  /-- basis points -/
  rate : Int
  deriving Repr, DecidableEq, Inhabited

/-- Exact tax of the bands on income `x`, in ticks. Each band charges `rate` on the part of `[lo, next.lo]`
below `x`; the last band is open above. -/
def bandsTicks : List Band → Int → Int
  | [], _ => 0
  | [b], x => b.rate * pos (x - b.lo)
  | b :: c :: rest, x => b.rate * pos (min x c.lo - b.lo) + bandsTicks (c :: rest) x

/-- The marginal rate of the bands on the unit `(x, x+1]`: the rate of the band with `lo ≤ x < next.lo`. -/
def bandsRate : List Band → Int → Int
  | [], _ => 0
  | [b], x => if b.lo ≤ x then b.rate else 0
  | b :: c :: rest, x => (if b.lo ≤ x ∧ x < c.lo then b.rate else 0) + bandsRate (c :: rest) x

/-- Thresholds strictly increasing (a `Bool`, so concrete schedules are checked by `decide`). -/
def bandsSorted : List Band → Bool
  | [] => true
  | [_] => true
  | b :: c :: rest => decide (b.lo < c.lo) && bandsSorted (c :: rest)

/-- Rates do not fall from one band to the next. -/
def ratesMono : List Band → Bool
  | [] => true
  | [_] => true
  | b :: c :: rest => decide (b.rate ≤ c.rate) && ratesMono (c :: rest)

structure Schedule where
  bands : List Band
  deriving Repr, DecidableEq, Inhabited

namespace Schedule

/-- From `(threshold, rate bp)` pairs, lowest threshold first. -/
def ofList (l : List (Int × Int)) : Schedule := ⟨l.map fun (t, r) => ⟨t, r⟩⟩

/-- From `(upper limit, rate bp)` pairs (the rate applies up to the limit) and the rate above the last limit;
the first band starts at 0. -/
def ofUpper (l : List (Int × Int)) (top : Int) : Schedule :=
  let los := 0 :: l.map Prod.fst
  let rates := l.map Prod.snd ++ [top]
  ⟨(los.zip rates).map fun (t, r) => ⟨t, r⟩⟩

/-- One rate on everything above 0. -/
def flat (rate : Int) : Schedule := ⟨[⟨0, rate⟩]⟩

/-- One rate above a threshold (0 below). -/
def flatAbove (lo rate : Int) : Schedule := ⟨[⟨0, 0⟩, ⟨lo, rate⟩]⟩

def ticks (s : Schedule) (x : Int) : Int := bandsTicks s.bands x

/-- The tax in units, rounded by the statute's rule. -/
def tax (s : Schedule) (r : Rule) (x : Int) : Int := r.ofTicks (s.ticks x)

/-- Marginal rate (bp) on the unit `(x, x+1]`. -/
def rate (s : Schedule) (x : Int) : Int := bandsRate s.bands x

/-- The tax on the slice `[a, b]` of income (stacking: e.g. savings charged on top of other income). -/
def sliceTicks (s : Schedule) (a b : Int) : Int := s.ticks b - s.ticks a

/-- The rate of the last band (0 for an empty schedule). -/
def topRate (s : Schedule) : Int := (s.bands.getLast?.map Band.rate).getD 0

/-- The largest rate (at least 0). -/
def maxRate (s : Schedule) : Int := s.bands.foldl (fun m b => max m b.rate) 0

/-- Shift every threshold by `f` (indexation, or a personal allowance written into the schedule). -/
def mapLo (s : Schedule) (f : Int → Int) : Schedule := ⟨s.bands.map fun b => { b with lo := f b.lo }⟩

/-- A zero-rate band of width `a` in front (a tax-free allowance folded into the schedule). -/
def withZeroBand (s : Schedule) (a : Int) : Schedule := ⟨⟨0, 0⟩ :: s.bands.map fun b => { b with lo := b.lo + a }⟩

/-- Conditions the generic theorems use. -/
def Sorted (s : Schedule) : Prop := bandsSorted s.bands = true
def RatesNonneg (s : Schedule) : Prop := ∀ b ∈ s.bands, 0 ≤ b.rate
def RatesLe (s : Schedule) (r : Int) : Prop := ∀ b ∈ s.bands, b.rate ≤ r
def LosNonneg (s : Schedule) : Prop := ∀ b ∈ s.bands, 0 ≤ b.lo

/-- Sorted thresholds, non-negative and non-decreasing rates, every threshold ≥ 0: an ordinary progressive
schedule. A `Bool`, so a concrete schedule's `progressive = true` is proved by `decide` (or `rfl`). -/
def progressive (s : Schedule) : Bool :=
  bandsSorted s.bands && ratesMono s.bands && s.bands.all (fun b => decide (0 ≤ b.rate))
    && s.bands.all (fun b => decide (0 ≤ b.lo))

end Schedule
end TaxKernel
