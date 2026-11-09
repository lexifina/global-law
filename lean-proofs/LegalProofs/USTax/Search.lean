import LegalProofs.USTax.Model

/-!
# Searching the model for cliffs and arbitrage

Runs the model itself (the same definitions the proofs use) over every whole-dollar income, and writes what it finds to
`tools/out/`: every point where one more dollar of wages or interest leaves a household with less, the worst marginal
rates, the investment-income cliff along the wage axis, a net-income landscape for the film, and the IRA contributions
that pay back the most.

    lake env lean LegalProofs/USTax/Search.lean
-/

namespace Legal.USTax

def statusName : Status → String | .single => "single" | .mfj => "mfj" | .hoh => "hoh"

/-- Every wage `w` in `[0, maxW)` where earning one more dollar lowers net income, with the size of the drop. -/
def wageCliffs (s : Status) (kids ira interest maxW : Nat) : List (Nat × Nat) := Id.run do
  let mut out := []
  let mut prev := net ⟨s, kids, 0, interest, ira⟩
  for w in [0:maxW] do
    let nxt := net ⟨s, kids, w + 1, interest, ira⟩
    if nxt < prev then out := (w, prev - nxt) :: out
    prev := nxt
  return out.reverse

def jsonList (xs : List String) : String := "[" ++ ",".intercalate xs ++ "]"

def run : IO Unit := do
  let profiles : List (Status × Nat × Nat) :=
    [(.single, 0, 0), (.single, 1, 0), (.single, 2, 0), (.single, 3, 0), (.hoh, 1, 0), (.hoh, 2, 0), (.hoh, 3, 0),
     (.mfj, 0, 0), (.mfj, 1, 0), (.mfj, 2, 0), (.mfj, 3, 0),
     (.single, 0, 2000), (.hoh, 1, 2000), (.hoh, 2, 2000), (.mfj, 0, 4000), (.mfj, 1, 4000), (.mfj, 2, 4000)]
  -- 1. wage cliffs
  let mut rows : List String := []
  for (s, k, ira) in profiles do
    for (w, drop) in wageCliffs s k ira 0 120000 do
      rows := s!"\{\"status\":\"{statusName s}\",\"kids\":{k},\"ira\":{ira},\"wages\":{w},\"drop\":{drop}}" :: rows
  IO.FS.writeFile "tools/out/tax_wage_cliffs.json" (jsonList rows.reverse)
  -- 2. the investment-income cliff along the wage axis (interest $11,950 → $11,951)
  let mut inv : List String := []
  for (s, k, _) in profiles.filter (fun p => p.2.2 = 0) do
    for i in [0:141] do
      let w := i * 500
      let a := net ⟨s, k, w, eitcInvestmentLimit, 0⟩
      let b := net ⟨s, k, w, eitcInvestmentLimit + 1, 0⟩
      if b < a then inv := s!"\{\"status\":\"{statusName s}\",\"kids\":{k},\"wages\":{w},\"drop\":{a - b}}" :: inv
  IO.FS.writeFile "tools/out/tax_interest_cliff.json" (jsonList inv.reverse)
  -- 3. landscape for the film: single parent, two children; wages × interest
  let mut grid : List String := []
  for j in [0:121] do
    let interest := j * 125
    let mut row : List String := []
    for i in [0:181] do
      row := toString (net ⟨.single, 2, i * 400, interest, 0⟩) :: row
    grid := jsonList row.reverse :: grid
  IO.FS.writeFile "tools/out/tax_landscape.json"
    s!"\{\"wageStep\":400,\"interestStep\":125,\"rows\":{jsonList grid.reverse}}"
  -- 4. IRA arbitrage: for each wage level, the contribution with the highest payback per dollar contributed
  let mut arb : List String := []
  for (s, k) in [(Status.mfj, 0), (Status.mfj, 1), (Status.mfj, 2), (Status.hoh, 1), (Status.single, 0)] do
    for i in [0:181] do
      let w := 15000 + i * 500
      let base := net ⟨s, k, w, 0, 0⟩
      let mut best := (0, 0)
      for c in [1:81] do
        let ira := c * 100
        let gain := net ⟨s, k, w, 0, ira⟩ - base
        if gain * 1000 / ira > best.2 * 1000 / (max best.1 1) then best := (ira, gain)
      if best.1 > 0 then
        arb := s!"\{\"status\":\"{statusName s}\",\"kids\":{k},\"wages\":{w},\"ira\":{best.1},\"gain\":{best.2}}" :: arb
  IO.FS.writeFile "tools/out/tax_ira_arbitrage.json" (jsonList arb.reverse)
  IO.println s!"wage cliffs: {rows.length}; interest-cliff points: {inv.length}; arbitrage rows: {arb.length}"

#eval run

end Legal.USTax
