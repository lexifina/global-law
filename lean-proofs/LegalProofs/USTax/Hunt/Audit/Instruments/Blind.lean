import Std
/-!
Blind replication, name `Instruments`.
Provisions encoded (26 U.S.C.): §852(b)(3)(B)-(D), §852(b)(4), §246(c)(3)-(4), §1091, §1223, §1222,
§1211(b), §1212(b), §1(h) (rate difference only) and §1411.
Self-contained; `import Std` only.
-/
namespace Legal.USTax.Hunt.Audit.Instruments.Blind

/-- Encoding choices that the text leaves open; the search is run under each. -/
structure Config where
  sixMonths : Nat      -- "6 months" in days of the model (§852(b)(4)(A)(ii), (C)(ii))
  oneYear : Nat        -- "1 year" (§1222)
  soldCounts : Bool    -- §1091(a): does an acquisition of a lot already sold again still disallow the loss?
  selfCounts : Bool    -- §1091(a): does the purchase of the very lot sold count as the "acquisition"?
  carryRci : Bool      -- does the §852(b)(4)(A) long-term taint follow a wash-sale loss into the new shares?
  deriving Repr

def exDay : Nat := 10          -- the fund goes ex-dividend on day 10
def lastDay : Nat := 250
def lotShares : Int := 1000
def divPerLot : Int := 10000   -- $10 a share capital gain dividend
def otherSTCG : Int := 10000   -- short-term gain already realised this year
def startCash : Int := 200000
def priceOn (d : Nat) : Int := if d < exDay then 100 else 90

structure Lot where
  acq : Nat          -- day of acquisition
  basis : Int        -- adjusted basis of the whole lot (§1091(d) adjustments included)
  tack : Nat         -- days tacked on by §1223(3)
  div : Int          -- capital gain dividend received with respect to these shares (§852(b)(3)(B))
  taint : Int        -- only under `carryRci`: inherited loss that stays long-term
  used : Bool        -- this acquisition has already "resulted in the nondeductibility" of one loss
  deriving BEq, Hashable, Repr

/-- A loss allowed so far that a purchase within the next 30 days would still disallow (§1091(a)). -/
structure OpenLoss where
  day : Nat
  amt : Int
  lt : Int
  st : Int
  held : Nat
  deriving BEq, Hashable, Repr

structure State where
  day : Nat
  cash : Int
  lots : List Lot
  open_ : List OpenLoss
  soldAcq : List (Nat × Bool)   -- acquisition days (≤30 days old) of lots already sold, and whether used
  stcg : Int                    -- from trades in the fund (the $10,000 from other sales is added in the tax)
  stcl : Int
  ltcg : Int
  ltcl : Int
  lost : Int                    -- loss disallowed with no share left to carry the basis
  buys : Nat
  deriving BEq, Hashable, Repr

inductive Act where
  | buy
  | sell (i : Nat)
  deriving BEq, Hashable, Repr

/-- One move: on day `day`, buy 1,000 shares or sell the i-th lot held. -/
structure Move where
  day : Nat
  act : Act
  deriving BEq, Hashable, Repr

def init : State :=
  { day := 1, cash := startCash, lots := [], open_ := [], soldAcq := [],
    stcg := 0, stcl := 0, ltcg := 0, ltcl := 0, lost := 0, buys := 0 }

/-- Move the calendar forward. On crossing into day 10 every share bought before day 10 and still held
receives the capital gain dividend, which §852(b)(3)(B) treats as gain on a capital asset held > 1 year. -/
def advance (s : State) (d : Nat) : State :=
  let s :=
    if s.day < exDay ∧ exDay ≤ d then
      let n : Int := s.lots.length
      { s with lots := s.lots.map (fun l => { l with div := l.div + divPerLot }),
               cash := s.cash + n * divPerLot, ltcg := s.ltcg + n * divPerLot }
    else s
  { s with day := d,
           open_ := s.open_.filter (fun o => d - o.day ≤ 30),
           soldAcq := s.soldAcq.filter (fun p => d - p.1 ≤ 30) }

/-- Days counted for §852(b)(4): §246(c)(3)(A) counts the day of disposition, not of acquisition;
§246(c)(3)(B) switches off the §1223(3) tacking; §852(b)(4)(C)(ii) ignores every day more than
6 months after the ex-dividend date. §246(c)(4) reductions are zero: the position has no options,
short sales or other positions. -/
def rciDays (c : Config) (l : Lot) (d : Nat) : Nat := (min d (exDay + c.sixMonths)) - l.acq

/-- Split of an allowed loss into (long-term, short-term). §1222(2),(4); §852(b)(4)(A). -/
def lossChar (c : Config) (l : Lot) (d : Nat) (loss : Int) : Int × Int :=
  if d - l.acq + l.tack > c.oneYear then (loss, 0)
  else
    let own := if l.div > 0 ∧ rciDays c l d ≤ c.sixMonths then l.div else 0
    let lt := min loss (own + l.taint)
    (lt, loss - lt)

def removeIdx {α} : List α → Nat → List α
  | [], _ => []
  | _ :: t, 0 => t
  | h :: t, n+1 => h :: removeIdx t n

def findIx {α} (p : α → Bool) : List α → Nat → Option Nat
  | [], _ => none
  | h :: t, n => if p h then some n else findIx p t (n+1)

def modifyIdx {α} (f : α → α) : List α → Nat → List α
  | [], _ => []
  | h :: t, 0 => f h :: t
  | h :: t, n+1 => h :: modifyIdx f t n

def step (c : Config) (s : State) (m : Move) : Option State :=
  if m.day < s.day ∨ m.day > lastDay then none else
  let s := advance s m.day
  let d := m.day
  let price := priceOn d * lotShares
  match m.act with
  | .buy =>
    if s.cash < price ∨ s.buys ≥ 4 then none else
    let s := { s with cash := s.cash - price, buys := s.buys + 1 }
    -- §1091(a): an acquisition within 30 days after a loss sale disallows that loss;
    -- §1091(d): the new shares take the old basis adjusted by the price difference;
    -- §1223(3): and the old holding period.
    match s.open_ with
    | o :: rest =>
      some { s with open_ := rest, stcl := s.stcl - o.st, ltcl := s.ltcl - o.lt,
                    lots := s.lots ++ [{ acq := d, basis := price + o.amt, tack := o.held, div := 0,
                                         taint := if c.carryRci then o.lt else 0, used := true }] }
    | [] =>
      some { s with lots := s.lots ++ [{ acq := d, basis := price, tack := 0, div := 0, taint := 0, used := false }] }
  | .sell i =>
    match s.lots[i]? with
    | none => none
    | some l =>
      let rest := removeIdx s.lots i
      let gl := price - l.basis
      let held := d - l.acq + l.tack
      let s := { s with cash := s.cash + price, lots := rest }
      let sold2 := (l.acq, l.used) :: s.soldAcq
      if gl ≥ 0 then
        -- §1222(1),(3)
        if held > c.oneYear then some { s with ltcg := s.ltcg + gl, soldAcq := sold2 }
        else some { s with stcg := s.stcg + gl, soldAcq := sold2 }
      else
        let loss := -gl
        let (lt, st) := lossChar c l d loss
        -- §1091(a): acquisition of substantially identical stock in the 30 days before (or on) the sale date
        if c.selfCounts ∧ d - l.acq ≤ 30 ∧ !l.used then
          -- the lot sold is treated as its own replacement: loss disallowed, nothing left to carry basis
          some { s with lost := s.lost + loss, soldAcq := (l.acq, true) :: s.soldAcq }
        else
        match findIx (fun (r : Lot) => d - r.acq ≤ 30 && !r.used) rest 0 with
        | some j =>
          some { s with lots := modifyIdx (fun r => { r with basis := r.basis + loss, tack := r.tack + held, used := true,
                                                             taint := r.taint + (if c.carryRci then lt else 0) }) rest j,
                        soldAcq := sold2 }
        | none =>
          match (if c.soldCounts then findIx (fun (p : Nat × Bool) => d - p.1 ≤ 30 && !p.2) s.soldAcq 0 else none) with
          | some j =>
            some { s with lost := s.lost + loss,
                          soldAcq := (l.acq, l.used) :: modifyIdx (fun p => (p.1, true)) s.soldAcq j }
          | none =>
            some { s with stcl := s.stcl + st, ltcl := s.ltcl + lt, soldAcq := sold2,
                          open_ := s.open_ ++ [{ day := d, amt := loss, lt := lt, st := st, held := held }] }

/-- Tax in thousandths of a dollar. §1222(5)-(11) netting; §1(h) 20% on net capital gain, 37% otherwise;
§1411 3.8% on both; §1211(b) lets up to $3,000 of net loss offset other income. -/
def taxMilli (s : State) : Int :=
  let st := otherSTCG + s.stcg - s.stcl
  let lt := s.ltcg - s.ltcl
  if st ≥ 0 ∧ lt ≥ 0 then 408 * st + 238 * lt
  else
    let net := st + lt
    if net ≥ 0 then (if lt ≥ 0 then 238 * net else 408 * net)
    else -370 * (min 3000 (-net))

def valueMilli (s : State) : Int := s.cash * 1000 - taxMilli s

structure Outcome where
  value : Int
  stcg : Int
  stcl : Int
  ltcg : Int
  ltcl : Int
  lost : Int
  deriving BEq, Hashable, Repr

def outcomeOf (s : State) : Outcome :=
  { value := valueMilli s, stcg := otherSTCG + s.stcg, stcl := s.stcl, ltcg := s.ltcg, ltcl := s.ltcl, lost := s.lost }

/-- Natural days of the position: start, the days round the ex-dividend day, the 30/31-day wash-sale
boundaries after them, the 6-month boundaries, and year end. -/
def days (c : Config) : List Nat :=
  let sm := c.sixMonths
  let raw := [1, 8, 9, 10, 11, 39, 40, 41, 42, 70, 71, 72, 73, 1 + sm, 2 + sm, 8 + sm, 9 + sm, 10 + sm, 11 + sm, 42 + sm, 250]
  ((raw.filter (· ≤ lastDay)).eraseDups).mergeSort (· ≤ ·)

def movesFrom (c : Config) (s : State) : List Move :=
  ((days c).filter (· ≥ s.day)).flatMap fun d =>
    ⟨d, .buy⟩ :: (List.range s.lots.length).map (fun i => ⟨d, .sell i⟩)

structure Result where
  positions : Nat
  outcomes : Std.HashMap Outcome (List Move)

def search (c : Config) (depth : Nat) : Result := Id.run do
  let mut visited : Std.HashSet State := {}
  visited := visited.insert init
  let mut frontier : Array (State × List Move) := #[(init, [])]
  let mut outs : Std.HashMap Outcome (List Move) := {}
  outs := outs.insert (outcomeOf init) []
  for _ in [0:depth] do
    let mut next : Array (State × List Move) := #[]
    for (s, path) in frontier do
      for m in movesFrom c s do
        match step c s m with
        | none => pure ()
        | some s2 =>
          if !visited.contains s2 then
            visited := visited.insert s2
            let p := m :: path
            next := next.push (s2, p)
            if s2.lots.isEmpty then
              let o := outcomeOf s2
              if !outs.contains o then outs := outs.insert o p
    frontier := next
  return { positions := visited.size, outcomes := outs }

def showMove (m : Move) : String :=
  match m.act with
  | .buy => s!"day {m.day}: buy 1000"
  | .sell i => s!"day {m.day}: sell lot {i}"

def dollars (v : Int) : String :=
  let neg := v < 0
  let a := v.natAbs
  let frac := a % 1000
  let pad := if frac < 10 then "00" else if frac < 100 then "0" else ""
  (if neg then "-" else "") ++ s!"{a / 1000}.{pad}{frac}"

def report (c : Config) (depth : Nat) : IO Unit := do
  let r := search c depth
  let base := valueMilli init
  IO.println s!"== sixMonths={c.sixMonths} oneYear={c.oneYear} soldCounts={c.soldCounts} selfCounts={c.selfCounts} carryRci={c.carryRci} depth={depth}"
  IO.println s!"positions={r.positions} baseline={dollars base}"
  let arr := r.outcomes.toArray.qsort (fun a b => a.1.value > b.1.value || (a.1.value == b.1.value && a.2.length < b.2.length))
  for (o, p) in arr do
    IO.println s!"value={dollars o.value} gain={dollars (o.value - base)} STCG={o.stcg} STCL={o.stcl} LTCG={o.ltcg} LTCL={o.ltcl} lostLoss={o.lost} :: {String.intercalate "; " (p.reverse.map showMove)}"

/-- Replay a plan, printing the running tallies. -/
def replay (c : Config) (ms : List Move) : IO Unit := do
  let mut s := init
  for m in ms do
    match step c s m with
    | none => IO.println s!"  illegal: {showMove m}"
    | some s2 =>
      s := s2
      IO.println s!"  {showMove m} -> cash={s.cash} lots(acq,basis,tack,div)={s.lots.map (fun l => (l.acq, l.basis, l.tack, l.div))} STCL={s.stcl} LTCG={s.ltcg} LTCL={s.ltcl} lost={s.lost}"
  IO.println s!"  tax={dollars (taxMilli s)} value={dollars (valueMilli s)}"

def cfgA : Config := { sixMonths := 183, oneYear := 365, soldCounts := true, selfCounts := false, carryRci := false }

#eval report cfgA 6
#eval report { cfgA with soldCounts := false } 6
#eval report { cfgA with selfCounts := true } 6
#eval report { cfgA with carryRci := true } 6
#eval report { cfgA with sixMonths := 125, oneYear := 250 } 6
#eval do
  IO.println "replay: hold past 6 months"
  replay cfgA [⟨9, .buy⟩, ⟨193, .sell 0⟩]
  IO.println "replay: sell inside 6 months, no repurchase"
  replay cfgA [⟨9, .buy⟩, ⟨11, .sell 0⟩]
  IO.println "replay: sell at loss, rebuy inside 30 days, sell replacement"
  replay cfgA [⟨9, .buy⟩, ⟨10, .sell 0⟩, ⟨10, .buy⟩, ⟨11, .sell 0⟩]
  IO.println "replay: two lots, sell one into the other, sell the other 31 days on"
  replay cfgA [⟨9, .buy⟩, ⟨9, .buy⟩, ⟨10, .sell 0⟩, ⟨40, .sell 0⟩]
  IO.println "replay: sell, rebuy same day, sell replacement once 30 days clear of the first purchase"
  replay cfgA [⟨1, .buy⟩, ⟨10, .sell 0⟩, ⟨10, .buy⟩, ⟨39, .sell 0⟩]
  IO.println "replay (soldCounts=false): buy day 9, sell day 10, rebuy day 10, sell day 11"
  replay { cfgA with soldCounts := false } [⟨9, .buy⟩, ⟨10, .sell 0⟩, ⟨10, .buy⟩, ⟨11, .sell 0⟩]
  IO.println "replay (carryRci=true): same plan"
  replay { cfgA with carryRci := true } [⟨1, .buy⟩, ⟨10, .sell 0⟩, ⟨10, .buy⟩, ⟨39, .sell 0⟩]

end Legal.USTax.Hunt.Audit.Instruments.Blind
