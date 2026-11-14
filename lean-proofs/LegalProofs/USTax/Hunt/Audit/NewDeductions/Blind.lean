import Std
/-! Blind replication `NewDeductions`. Self-contained. All money in cents (Nat).
Provisions: §164(a), §164(b)(5)-(7), §63(a)-(c),(e), §6013(a), §1(j) (2026 tables). -/
namespace Legal.USTax.Hunt.Audit.NewDeductions.Blind

def usd (d : Nat) : Nat := d * 100
def showUsd (c : Nat) : String :=
  let r := c % 100
  s!"${c / 100}." ++ (if r < 10 then s!"0{r}" else s!"{r}")

inductive Filing | joint | separate deriving BEq, Hashable, Repr, DecidableEq

/-- Orders of operation for §164(b)(6)(B) + (7). -/
inductive Reading
  /-- R1 text order: (7)(A) fixes the "applicable limitation amount" ($40,400); (7)(B)(i) reduces
      *that amount* by 30% of MAGI over the threshold (half threshold if separate); (7)(B)(iii)
      floors *that amount* at $10,000; then (6)(B) caps the taxes at the amount, "half the
      applicable limitation amount" for a separate return. -/
  | textOrder
  /-- R2 halve first, and halve the floor too: separate = max($20,200 − 30%·excess, $5,000). -/
  | halveFirstHalfFloor
  /-- R3 halve first, floor as written: separate = max($20,200 − 30%·excess, $10,000). -/
  | halveFirstFullFloor
  deriving BEq, Hashable, Repr, DecidableEq

def ala2026 : Nat := usd 40400          -- §164(b)(7)(A)(ii)
def threshold2026 : Nat := usd 505000   -- §164(b)(7)(B)(ii)(II)
def floorAmt : Nat := usd 10000         -- §164(b)(7)(B)(iii)

/-- "The most State and local tax that may be taken into account", by filing status and MAGI. -/
def saltCap (r : Reading) (f : Filing) (magi : Nat) : Nat :=
  let thr := match f with | .joint => threshold2026 | .separate => threshold2026 / 2  -- (7)(B)(i) parenthetical
  let reduction := (magi - thr) * 30 / 100                                            -- (7)(B)(i); Nat sub = "excess (if any)"
  match f, r with
  | .joint, _ => max (ala2026 - reduction) floorAmt
  | .separate, .textOrder =>
      let ala := max (ala2026 - reduction) floorAmt       -- (7)(A),(B)(i),(B)(iii): the defined amount
      ala / 2                                             -- (6)(B) parenthetical: half of that amount
  | .separate, .halveFirstHalfFloor => max (ala2026 / 2 - reduction) (floorAmt / 2)
  | .separate, .halveFirstFullFloor => max (ala2026 / 2 - reduction) floorAmt

/-! ### §1(j) 2026 tables (figures as supplied/known): (upper bound, rate%) -/
def bracketsJoint : List (Nat × Nat) :=
  [(24800,10),(100800,12),(211400,22),(403550,24),(512450,32),(768700,35)]
def bracketsSeparate : List (Nat × Nat) :=
  [(12400,10),(50400,12),(105700,22),(201775,24),(256225,32),(384350,35)]

def taxOn (bs : List (Nat × Nat)) (ti : Nat) : Nat := Id.run do
  let mut lo := 0
  let mut tax := 0
  for (hiD, rate) in bs do
    let hi := usd hiD
    if ti > lo then tax := tax + (min ti hi - lo) * rate / 100
    lo := hi
  if ti > lo then tax := tax + (ti - lo) * 37 / 100
  return tax

def stdDed : Filing → Nat | .joint => usd 32200 | .separate => usd 16100

/-! ### Position -/
def wagesEach := usd 300000
def saltPaidEach := usd 25000      -- State income + real property tax, §164(a)(1),(3)
def mortgageEach := usd 12000      -- given; deductibility assumed (outside the provision list)

/-- Tax on one return. `otherItemizes` only matters for separate returns (§63(c)(6)(A)). -/
def returnTax (r : Reading) (f : Filing) (agi saltPaid mortgage : Nat) (itemize otherItemizes : Bool) : Nat :=
  let ti :=
    if itemize then                                   -- §63(a), §63(e)(1)
      agi - (min saltPaid (saltCap r f agi) + mortgage)
    else                                              -- §63(b)(1)
      let sd := if f == .separate && otherItemizes then 0 else stdDed f   -- §63(c)(6)(A)
      agi - sd
  taxOn (match f with | .joint => bracketsJoint | .separate => bracketsSeparate) ti

structure State where
  filing : Option Filing := none
  itemJ : Bool := false
  itemA : Bool := false
  itemB : Bool := false
  deriving BEq, Hashable, Repr

inductive Move
  | fileJoint        -- §6013(a) "may make a single return jointly"
  | fileSeparate     -- §6013(a) permissive; §1(d)/(j)(2)(D)
  | itemizeJoint     -- §63(e)
  | itemizeA         -- §63(e)
  | itemizeB         -- §63(e)
  deriving BEq, Hashable, Repr

def allMoves : List Move := [.fileJoint, .fileSeparate, .itemizeJoint, .itemizeA, .itemizeB]

def step (s : State) : Move → Option State
  | .fileJoint => if s.filing.isNone then some { s with filing := some .joint } else none
  | .fileSeparate => if s.filing.isNone then some { s with filing := some .separate } else none
  | .itemizeJoint => if s.filing == some .joint && !s.itemJ then some { s with itemJ := true } else none
  | .itemizeA => if s.filing == some .separate && !s.itemA then some { s with itemA := true } else none
  | .itemizeB => if s.filing == some .separate && !s.itemB then some { s with itemB := true } else none

def value (r : Reading) (s : State) : Option Nat :=
  match s.filing with
  | none => none
  | some .joint =>
      some (returnTax r .joint (2*wagesEach) (2*saltPaidEach) (2*mortgageEach) s.itemJ false)
  | some .separate =>
      some (returnTax r .separate wagesEach saltPaidEach mortgageEach s.itemA s.itemB
          + returnTax r .separate wagesEach saltPaidEach mortgageEach s.itemB s.itemA)

/-- BFS over move sequences, deduped on state. Returns (state, first plan reaching it). -/
def search : List (State × List Move) := Id.run do
  let mut seen : Std.HashSet State := {}
  let s0 : State := {}
  seen := seen.insert s0
  let mut frontier : List (State × List Move) := [(s0, [])]
  let mut all : List (State × List Move) := [(s0, [])]
  for _ in [0:4] do
    let mut next : List (State × List Move) := []
    for (s, p) in frontier do
      for m in allMoves do
        match step s m with
        | some s' =>
          if !seen.contains s' then
            seen := seen.insert s'
            next := next ++ [(s', p ++ [m])]
        | none => pure ()
    all := all ++ next
    frontier := next
  return all

def report (r : Reading) : IO Unit := do
  IO.println s!"\n=== Reading {repr r} ==="
  let base := (value r { filing := some .joint }).getD 0
  let baseI := (value r { filing := some .joint, itemJ := true }).getD 0
  IO.println s!"baseline joint, standard: {showUsd base}; joint, itemized: {showUsd baseI}"
  let baseline := min base baseI
  IO.println s!"baseline (best joint return): {showUsd baseline}"
  let res := search.filterMap (fun (s, p) => (value r s).map (fun v => (v, p)))
  let sorted := res.toArray.qsort (fun a b => a.1 < b.1)
  IO.println s!"positions searched: {search.length}, terminal (filed): {res.length}"
  for (v, p) in sorted do
    let d : Int := (baseline : Int) - (v : Int)
    IO.println s!"  {showUsd v}  gain vs baseline (cents) {d}  {repr p}"

def main : IO Unit := do
  IO.println "--- SALT cap function (before any search) ---"
  for r in [Reading.textOrder, .halveFirstHalfFloor, .halveFirstFullFloor] do
    IO.println s!"{repr r}: joint@600k={showUsd (saltCap r .joint (usd 600000))}  sep@300k={showUsd (saltCap r .separate (usd 300000))}  sep@260k={showUsd (saltCap r .separate (usd 260000))}  sep@400k={showUsd (saltCap r .separate (usd 400000))}"
  for r in [Reading.textOrder, .halveFirstHalfFloor, .halveFirstFullFloor] do report r

#eval main
end Legal.USTax.Hunt.Audit.NewDeductions.Blind
