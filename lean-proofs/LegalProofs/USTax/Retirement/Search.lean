import LegalProofs.USTax.Retirement.Rules
import Std.Data.HashMap

/-!
# A blind search over the moves

Breadth-first search over every sequence of moves the rules allow, from one starting position, up to a depth. The
amounts tried at each step are not chosen with any plan in mind: each move is tried with every "natural" amount the
position offers (what is left of each limit, each balance, the pre-tax part, the basis, all the cash). Positions
reached twice are explored once. The search reports, for each depth, the best result found: after-tax money moved
into Roth accounts, net of any tax incurred.

    lake env lean LegalProofs/USTax/Retirement/Search.lean
-/

namespace Legal.USTax.Retirement.Search
open Legal.USTax.Retirement

def amounts (s : Acct) : List Nat :=
  [iraLimit - s.iraContrib, additionsLimit - s.additions, deferralLimit - s.deferrals, s.ira, s.ira - s.basis, s.basis,
   s.planAfterTax, s.cash].filter (· > 0) |>.eraseDups

def moves (s : Acct) : List Act :=
  (amounts s).flatMap fun a =>
    [.rothContrib a, .tradContrib a, .convert a, .rollIn a, .defer a, .afterTax a, .inPlanRoth a]

/-- The question asked of every position: how much has gone into Roth accounts **without any tax**? A position that
incurred tax scores minus that tax, so the search prefers tax-free plans and, among those, the most Roth money. -/
def score (s0 s : Acct) : Int := if s.taxed = s0.taxed then (s.roth : Int) - s0.roth else -((s.taxed - s0.taxed : Nat) : Int)

/-- Separately: the cheapest way, in tax, to get $7,000 of new money into the Roth. -/
def cheapest7000 (s0 s : Acct) : Bool := s.roth ≥ s0.roth + 7000 ∧ s0.cash ≥ s.cash + 7000

def showAct : Act → String
  | .rothContrib a => s!"Roth IRA contribution ${a}"
  | .tradContrib a => s!"traditional IRA contribution ${a}"
  | .convert a => s!"convert ${a} to Roth"
  | .rollIn a => s!"roll ${a} from IRA into 401(k)"
  | .defer a => s!"elective deferral ${a}"
  | .afterTax a => s!"after-tax 401(k) contribution ${a}"
  | .inPlanRoth a => s!"in-plan Roth rollover ${a}"

def search (magi depth : Nat) (s0 : Acct) (allowed : Act → Bool) : IO Unit := do
  let mut frontier : List (Acct × List Act) := [(s0, [])]
  let mut seen : Std.HashMap Acct Unit := {}
  let mut best : Int × Acct × List Act := (0, s0, [])
  let mut cheap : Option (Nat × List Act) := none
  for d in [1:depth + 1] do
    let mut next : List (Acct × List Act) := []
    for (s, path) in frontier do
      for m in moves s do
        if allowed m then
          match step magi s m with
          | none => pure ()
          | some s' =>
            if !seen.contains s' then
              seen := seen.insert s' ()
              next := (s', path ++ [m]) :: next
              let sc := score s0 s'
              if sc > best.1 then best := (sc, s', path ++ [m])
              if cheapest7000 s0 s' then
                let t := s'.taxed - s0.taxed
                if cheap.all (fun c => t < c.1) then cheap := some (t, path ++ [m])
    frontier := next
    IO.println s!"depth {d}: {frontier.length} new positions, {seen.size} in all; best so far {best.1}"
  let (_, s, path) := best
  IO.println s!"most Roth money at no tax: +${s.roth - s0.roth} (taxed ${s.taxed - s0.taxed})"
  for m in path do IO.println s!"  {showAct m}"
  match cheap with
  | some (t, p) => IO.println s!"cheapest way to put $7,000 of new money in the Roth: ${t} of income taxed"; for m in p do IO.println s!"  {showAct m}"
  | none => IO.println "no way to put $7,000 of new money in the Roth"

/-- A single filer earning $250,000: far above the Roth limit. $100,000 of pre-tax money in a rollover IRA from an
old job, $100,000 of savings, a 401(k) at work. -/
def start : Acct := ⟨100000, 0, 0, 0, 0, 100000, 0, 0, 0, 0, 0⟩

#eval do
  IO.println "== every move =="
  search 250000 6 start (fun _ => true)
  IO.println "== without rolling IRA money into the 401(k) =="
  search 250000 6 start (fun | .rollIn _ => false | _ => true)
  IO.println "== IRA moves only (no after-tax 401(k) money) =="
  search 250000 6 start (fun | .afterTax _ | .inPlanRoth _ => false | _ => true)
  IO.println "== IRA moves only, and no roll-in =="
  search 250000 6 start (fun | .afterTax _ | .inPlanRoth _ | .rollIn _ => false | _ => true)
  IO.println "== the same person earning $140,000 (below the Roth limit) =="
  search 140000 6 start (fun | .afterTax _ | .inPlanRoth _ => false | _ => true)

end Legal.USTax.Retirement.Search
