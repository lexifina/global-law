import TaxKernel.Schedule

/-!
# TaxKernel.Tariff (added in 1.2): tariffs printed as columns rather than as bands

Many statutes print the tariff as a table whose rows give, for income from `lo`, a **fixed amount plus a rate on the
excess** ("column III + column IV % of the excess over column I": NL Wet IB art. 2.10, BE/LU-style tables), or as a
**rate on the whole income minus a subtraction** (MT Income Tax Act Cap. 123 art. 56: "Rate … Subtract …"). Both
equal a band `Schedule` only if the printed amounts are exactly the schedule's cumulative tax; when the statute rounds
the printed amount, the literal tariff can fall where the band sum rises (the NL finding of the 20-country phase,
INBOX 2026-11-19). Stating the table literally lets a country prove or refute that it equals the band schedule.

* `CumRow {lo base rate}`: from `lo`, tax = `base` + `rate` (bp) × (x − lo) (ticks: `base * BP + rate * (x − lo)`).
* `SubRow {lo rate subtract}`: from `lo`, tax = `rate` × x − `subtract` (ticks: `rate * x − subtract * BP`).
* `cumTicks rows x`, `subTicks rows x`: the row is the last one with `lo ≤ x` (rows lowest first; 0 below the first).
* `Schedule.cumRows s`: the column form of a band schedule (base = the band sum at each threshold, in ticks / BP,
  rounded down): build the statute's table from the bands and compare.
* Checks (`Bool`, so a concrete table is proved or refuted by `decide` / `#guard`):
  `cumAgrees rows s xs tol` (the literal table is within `tol` ticks of the band schedule at every probe in `xs`),
  `cumMonoAt rows xs` (the literal tax never falls between consecutive probes), and the same for `SubRow`.
-/

namespace TaxKernel

structure CumRow where
  lo : Int
  /-- tax at `lo`, units (the printed column) -/
  base : Int
  /-- bp on the excess over `lo` -/
  rate : Int
  deriving Repr, DecidableEq, Inhabited

structure SubRow where
  lo : Int
  /-- bp on the whole income -/
  rate : Int
  /-- units subtracted -/
  subtract : Int
  deriving Repr, DecidableEq, Inhabited

/-- The last row with `lo ≤ x` (rows lowest first). -/
def lastRowLe {α : Type} (lo : α → Int) : List α → Int → Option α
  | [], _ => none
  | r :: rest, x => if lo r ≤ x then (match lastRowLe lo rest x with | some r' => some r' | none => some r) else none

def cumTicks (rows : List CumRow) (x : Int) : Int :=
  match lastRowLe CumRow.lo rows x with
  | some r => r.base * BP + r.rate * (x - r.lo)
  | none => 0

def subTicks (rows : List SubRow) (x : Int) : Int :=
  match lastRowLe SubRow.lo rows x with
  | some r => r.rate * x - r.subtract * BP
  | none => 0

/-- The column form of a band schedule: at each threshold, the band sum there (units, rounded down) and the band rate. -/
def Schedule.cumRows (s : Schedule) : List CumRow :=
  s.bands.map fun b => { lo := b.lo, base := s.ticks b.lo / BP, rate := b.rate }

/-- The literal table is within `tol` ticks of the schedule at every probe. -/
def cumAgrees (rows : List CumRow) (s : Schedule) (xs : List Int) (tol : Int := 0) : Bool :=
  xs.all fun x => decide (cumTicks rows x - s.ticks x ≤ tol) && decide (s.ticks x - cumTicks rows x ≤ tol)

def subAgrees (rows : List SubRow) (s : Schedule) (xs : List Int) (tol : Int := 0) : Bool :=
  xs.all fun x => decide (subTicks rows x - s.ticks x ≤ tol) && decide (s.ticks x - subTicks rows x ≤ tol)

/-- Never falls between consecutive probes (probes in increasing order). -/
def monoAt (f : Int → Int) : List Int → Bool
  | [] => true
  | [_] => true
  | x :: y :: rest => decide (f x ≤ f y) && monoAt f (y :: rest)

def cumMonoAt (rows : List CumRow) (xs : List Int) : Bool := monoAt (cumTicks rows) xs
def subMonoAt (rows : List SubRow) (xs : List Int) : Bool := monoAt (subTicks rows) xs

/-- Each row's first unit against the previous row's formula: the jumps of the literal table at its thresholds
(ticks; 0 = continuous). A negative jump is a point where the literal tax falls. -/
def cumJumps (rows : List CumRow) : List (Int × Int) :=
  rows.map fun r => (r.lo, cumTicks rows r.lo - cumTicks (rows.filter fun q => q.lo < r.lo) r.lo)

def subJumps (rows : List SubRow) : List (Int × Int) :=
  rows.map fun r => (r.lo, subTicks rows r.lo - subTicks (rows.filter fun q => q.lo < r.lo) r.lo)

end TaxKernel
