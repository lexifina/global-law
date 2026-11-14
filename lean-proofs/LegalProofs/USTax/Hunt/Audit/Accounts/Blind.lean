import Std
/-!
Blind replication `Accounts`: §530A, §408(d)(1)-(3), §408(o), §219(a),(b),(g), §408A(c),(d)(3), §72(e).
Tax year 2040, single, age 30, active participant, MAGI $250,000. Whole dollars.
-/
namespace Legal.USTax.Hunt.Audit.Accounts.Blind

/-- Figures given in the task (indexed amounts). -/
def iraLimit : Nat := 7000          -- §219(b)(5) deductible amount
def rothLo : Nat := 150000          -- §408A(c)(3)(B)(ii)(II) as indexed
def rothHi : Nat := 165000          -- lo + $15,000, §408A(c)(3)(A)(ii)
def dedLo : Nat := 79000            -- §219(g)(3)(B)(ii) as indexed
def dedHi : Nat := 89000            -- lo + $10,000, §219(g)(2)(A)(ii)
def magi : Nat := 250000
def activeParticipant : Bool := true

/-- §219(g)(2): reduction of a dollar limitation; (B) $200 floor; (C) rounding to next lowest $10. -/
def phaseOut (limit agi lo hi : Nat) : Nat :=
  if agi ≤ lo then limit
  else if agi ≥ hi then 0
  else
    let red := (limit * (agi - lo) / (hi - lo)) / 10 * 10
    let rem := limit - red
    if rem < 200 then 200 else rem

/-- §219(b)(1),(g)(1): deduction allowable with regard to (g). Compensation assumed ≥ the deductible amount. -/
def dedWithG : Nat := if activeParticipant then phaseOut iraLimit magi dedLo dedHi else iraLimit
/-- §408(o)(2)(B)(i): nondeductible limit = deduction without (g) − deduction with (g). -/
def nondeductibleLimit : Nat := iraLimit - dedWithG
/-- §408A(c)(3)(A): Roth dollar limit after the MAGI reduction (conversion income is ignored, (c)(3)(B)(i)). -/
def rothDollarLimit : Nat := phaseOut iraLimit magi rothLo rothHi

structure State where
  cash : Nat
  tradV : Nat      -- value, individual retirement plans other than Roth and other than §530A
  tradB : Nat      -- investment in the contract (basis), same group
  trumpV : Nat     -- §530A account value
  trumpB : Nat     -- §530A investment in the contract, after §530A(d)(2)
  roth : Nat
  tTrad : Nat      -- amounts described in §408(d)(1) from the traditional group this year (conversions + cash)
  tTrump : Nat     -- same for the §530A group (§530A(h)(4): §408(d)(2) applied separately)
  contrib : Nat    -- contributions this year to non-Roth individual retirement plans (§408A(c)(2)(B))
  rothContrib : Nat
  rolled : Bool    -- §408(d)(3)(B) one 60-day rollover per 1-year period
  hasTrump : Bool
  deriving BEq, Hashable, Repr

inductive Move where
  | contribTrad (a : Nat)     -- §408(o)(1) designated nondeductible contribution, ordinary IRA
  | contribTrump (a : Nat)    -- same, into the §530A account (§530A(a); (b)(1)(C)(i),(h)(3) bind only before 18)
  | contribRoth (a : Nat)     -- §408A(c)(2),(3)
  | convTrad (a : Nat)        -- §408A(d)(3)(C) conversion of ordinary IRA
  | convTrump (a : Nat)       -- §408A(d)(3)(C) conversion of the §530A account (an IRA under §408(a), §530A(a),(b)(1))
  | distTrad (a : Nat)        -- §408(d)(1) cash distribution
  | distTrump (a : Nat)       -- §408(d)(1), allowed from the year of age 18 (§530A(d)(1))
  | rollTradToTrump (a : Nat) -- §408(d)(3)(A)(i) rollover into the §530A account
  | rollTrumpToTrad (a : Nat) -- §408(d)(3)(A)(i) rollover out of the §530A account
  deriving BEq, Hashable, Repr

/-- Basis carried by a rollover of `r`: pro rata, §72(e)(8)(B) "as of the time of the distribution" (judgment call). -/
def carry (r v b t : Nat) : Nat := if v + t = 0 then 0 else min b (r * b / (v + t))

def step (s : State) : Move → Option State
  | .contribTrad a =>
    -- §219(b)(1): total cannot exceed the deductible amount; §408(o)(2)(A): nondeductible ≤ nondeductible limit
    -- (dedWithG of it could instead be deducted; here dedWithG = 0, so every dollar is basis)
    if a > 0 ∧ a ≤ s.cash ∧ s.contrib + s.rothContrib + a ≤ iraLimit
        ∧ s.contrib + a ≤ nondeductibleLimit + dedWithG then
      some { s with cash := s.cash - a, tradV := s.tradV + a, tradB := s.tradB + a, contrib := s.contrib + a }
    else none
  | .contribTrump a =>
    if s.hasTrump ∧ a > 0 ∧ a ≤ s.cash ∧ s.contrib + s.rothContrib + a ≤ iraLimit
        ∧ s.contrib + a ≤ nondeductibleLimit + dedWithG then
      some { s with cash := s.cash - a, trumpV := s.trumpV + a, trumpB := s.trumpB + a, contrib := s.contrib + a }
    else none
  | .contribRoth a =>
    -- §408A(c)(2): limit less contributions to other plans; (c)(3): not above the reduced dollar limit
    if a > 0 ∧ a ≤ s.cash ∧ s.rothContrib + a ≤ min (iraLimit - s.contrib) rothDollarLimit then
      some { s with cash := s.cash - a, roth := s.roth + a, rothContrib := s.rothContrib + a }
    else none
  | .convTrad a =>
    if a > 0 ∧ a ≤ s.tradV then
      some { s with tradV := s.tradV - a, roth := s.roth + a, tTrad := s.tTrad + a }
    else none
  | .convTrump a =>
    if s.hasTrump ∧ a > 0 ∧ a ≤ s.trumpV then
      some { s with trumpV := s.trumpV - a, roth := s.roth + a, tTrump := s.tTrump + a }
    else none
  | .distTrad a =>
    if a > 0 ∧ a ≤ s.tradV then
      some { s with tradV := s.tradV - a, cash := s.cash + a, tTrad := s.tTrad + a }
    else none
  | .distTrump a =>
    if s.hasTrump ∧ a > 0 ∧ a ≤ s.trumpV then
      some { s with trumpV := s.trumpV - a, cash := s.cash + a, tTrump := s.tTrump + a }
    else none
  | .rollTradToTrump a =>
    if s.hasTrump ∧ !s.rolled ∧ a > 0 ∧ a ≤ s.tradV then
      let c := carry a s.tradV s.tradB s.tTrad
      some { s with tradV := s.tradV - a, tradB := s.tradB - c, trumpV := s.trumpV + a,
                    trumpB := s.trumpB + c, rolled := true }
    else none
  | .rollTrumpToTrad a =>
    if s.hasTrump ∧ !s.rolled ∧ a > 0 ∧ a ≤ s.trumpV then
      let c := carry a s.trumpV s.trumpB s.tTrump
      some { s with trumpV := s.trumpV - a, trumpB := s.trumpB - c, tradV := s.tradV + a,
                    tradB := s.tradB + c, rolled := true }
    else none

/-- §408(d)(1),(2) with §72(e)(8)(B): one contract per group, one distribution per year, measured at year end,
value increased by the year's distributions. Excluded share = basis / (year-end value + distributions). -/
def incomeGroup (v b t : Nat) : Nat := if t = 0 then 0 else t - min t (t * b / (v + t))
def income (s : State) : Nat := incomeGroup s.tradV s.tradB s.tTrad + incomeGroup s.trumpV s.trumpB s.tTrump
def net (s : State) : Int := (s.roth : Int) - (income s : Int)

def start (withTrump : Bool) : State :=
  { cash := 100000, tradV := 100000, tradB := 0, trumpV := if withTrump then 20000 else 0,
    trumpB := if withTrump then 12000 else 0, roth := 0, tTrad := 0, tTrump := 0, contrib := 0,
    rothContrib := 0, rolled := false, hasTrump := withTrump }

/-- Amounts: natural values of the position, plus the whole current balance of the source. -/
def amounts : List Nat := [1000, 7000, 8000, 12000, 19000, 20000, 27000, 100000, 107000]

def movesFrom (s : State) : List Move :=
  let am (bal : Nat) := (bal :: amounts).eraseDups
  (amounts.map .contribTrad) ++ (amounts.map .contribTrump) ++ (amounts.map .contribRoth)
  ++ ((am s.tradV).map .convTrad) ++ ((am s.trumpV).map .convTrump)
  ++ ((am s.tradV).map .distTrad) ++ ((am s.trumpV).map .distTrump)
  ++ ((am s.tradV).map .rollTradToTrump) ++ ((am s.trumpV).map .rollTrumpToTrad)

def search (s0 : State) (depth : Nat) : Array (State × List Move) := Id.run do
  let mut seen : Std.HashSet State := (∅ : Std.HashSet State).insert s0
  let mut all : Array (State × List Move) := #[(s0, [])]
  let mut frontier : Array (State × List Move) := #[(s0, [])]
  for _ in [0:depth] do
    let mut next : Array (State × List Move) := #[]
    for (s, p) in frontier do
      for m in movesFrom s do
        match step s m with
        | none => pure ()
        | some t =>
          if !seen.contains t then
            seen := seen.insert t
            next := next.push (t, m :: p)
    all := all ++ next
    frontier := next
  return all

/-- One line per distinct (Roth, income) outcome, shortest plan first found, sorted by net then lower income. -/
def report (label : String) (withTrump : Bool) (depth top : Nat) : IO Unit := do
  let all := search (start withTrump) depth
  let mut fam : Std.HashMap (Nat × Nat) (List Move) := {}
  for (s, p) in all do
    let k := (s.roth, income s)
    if !fam.contains k then fam := fam.insert k p.reverse
  let arr := fam.toArray.qsort (fun a b =>
    let na : Int := (a.1.1 : Int) - a.1.2
    let nb : Int := (b.1.1 : Int) - b.1.2
    na > nb || (na == nb && a.1.2 < b.1.2))
  IO.println s!"== {label}: positions {all.size}, distinct (Roth, income) outcomes {arr.size}"
  -- collapse to one line per net value: the lowest-income plan and the highest-Roth plan at that net
  let mut lastNet : Option Int := none
  let mut shown := 0
  let mut hiRoth : Option ((Nat × Nat) × List Move) := none
  for (k, p) in arr.toList do
    let n : Int := (k.1 : Int) - k.2
    if lastNet != some n then
      if let some (hk, hp) := hiRoth then
        IO.println s!"    highest-Roth tie: roth {hk.1} income {hk.2} moves {reprStr hp}"
      if shown ≥ top then
        hiRoth := none
        break
      IO.println s!"net {n}  roth {k.1}  income {k.2}  moves {reprStr p}"
      lastNet := some n
      shown := shown + 1
      hiRoth := none
    else
      match hiRoth with
      | none => hiRoth := some (k, p)
      | some (hk, _) => if k.1 > hk.1 then hiRoth := some (k, p)

#eval IO.println s!"dedWithG {dedWithG} nondeductibleLimit {nondeductibleLimit} rothDollarLimit {rothDollarLimit}"
#eval report "with 530A account" true 4 8
#eval report "baseline (b): no 530A account" false 4 6
#eval IO.println s!"baseline (a) do nothing: net {net (start true)} roth {(start true).roth} income {income (start true)}"

end Legal.USTax.Hunt.Audit.Accounts.Blind
