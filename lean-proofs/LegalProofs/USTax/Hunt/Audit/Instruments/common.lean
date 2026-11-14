
/-! ### Audit helpers (shared by every Red*.lean) -/

def PLAN : List (List String) :=
  [["sell FundA", "buy GainFund"], ["buy GainFund", "sell GainFund"], [], ["sell GainFund", "buy FundA"], [], [], []]
def HOLD201 : List (List String) :=
  [["sell FundA", "buy GainFund"], [], [], [], ["sell GainFund", "buy FundA"], [], []]
def SELL33 : List (List String) :=
  [["sell FundA", "buy GainFund"], [], [], ["sell GainFund", "buy FundA"], [], [], []]
def SELL1 : List (List String) :=
  [["sell FundA", "buy GainFund"], ["sell GainFund", "buy FundA"], [], [], [], [], []]
def NONE : List (List String) := [[], [], [], [], [], [], []]

/-- Best tax (everything sold) over every final position, and the plain-plan tax. -/
def best (sc : Sc) : IO Unit := do
  let (visited, frontier) := explore sc false
  let mut base : Option (Nat × Int) := none
  for (s, path) in (explore sc true).2 do
    if base.all (fun b => path.length < b.1) then base := some (path.length, bestTax sc (liquidate sc s))
  let mut bst : Option (Int × Path) := none
  for (s, path) in frontier do
    let tl := bestTax sc (liquidate sc s)
    if bst.all (fun b => tl < b.1 || (tl == b.1 && path.length < b.2.length)) then bst := some (tl, path)
  let bl := (base.getD (0, 0)).2
  match bst with
  | some (tl, path) =>
    IO.println s!"{sc.name}: positions {visited}, finals {frontier.size}, plain ${bl}, best ${tl}, saves ${bl - tl}"
    for (_, txt) in path.reverse do IO.println s!"     {txt}"
  | none => IO.println s!"{sc.name}: no final position"

