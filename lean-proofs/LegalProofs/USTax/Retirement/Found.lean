import LegalProofs.USTax.Retirement.Theorems

/-!
# What the search found, re-checked

The search (`Search.lean`) was given only the moves in `Rules.lean` and a starting position: a single filer earning
$250,000, $100,000 of pre-tax money in an old rollover IRA, $100,000 of savings, a 401(k) at work. It was not told
about any planning technique. These are the plans it returned, re-checked by the kernel, set against the theorems that
say they cannot be improved on.
-/

set_option maxRecDepth 100000

namespace Legal.USTax.Retirement.Found
open Legal.USTax.Retirement

def start : Acct := ⟨100000, 0, 0, 0, 0, 100000, 0, 0, 0, 0, 0⟩

/-- The plan the search found with every move available: $77,000 into Roth accounts, no tax. -/
def best : List Act := [.afterTax 70000, .tradContrib 7000, .rollIn 100000, .inPlanRoth 70000, .convert 7000]

theorem best_works : (run 250000 start best).map (fun s => (s.roth, s.taxed)) = some (77000, 0) := by decide

/-- At $250,000 the Roth contribution limit itself is zero. -/
theorem limit_is_zero : rothLimit 250000 = 0 := by decide

/-- **$77,000 is the most.** By `roth_ceiling`, no sequence of moves of any length from this position puts more into
Roth accounts at no tax. The search's plan reaches the ceiling, so it is optimal. -/
theorem best_is_optimal (acts : List Act) (s' : Acct) (h : run 250000 start acts = some s') (notax : s'.taxed = 0) :
    s'.roth ≤ 77000 := by
  have := roth_ceiling 250000 acts start s' (by unfold WF; decide) (by decide) (by decide) h
  simp [start, iraLimit, additionsLimit] at this; omega

/-- **The same $7,000 without the roll-in.** The search's cheapest IRA-only route: contribute and convert. The pro-rata
rule taxes $6,543 of the $7,000, because the conversion is deemed to come from all $107,000 in the IRAs. -/
theorem without_roll_in :
    (run 250000 start [.tradContrib 7000, .convert 7000]).map (fun s => (s.roth, s.taxed)) = some (7000, 6543) := by
  decide

/-- And by `no_escape`, splitting, reordering or repeating conversions cannot change that: without moving money into
the 401(k), all $100,000 of pre-tax money is taxed on its way to the Roth. -/
theorem every_pretax_dollar (acts : List Act) (ha : acts.all noPlanIn = true) (s' : Acct)
    (h : run 250000 start acts = some s') (empty : s'.ira = 0) : s'.taxed = 100000 + s'.deducted := by
  have := no_escape 250000 acts ha start s' (by unfold WF; decide) h empty
  simp [start] at this; omega

end Legal.USTax.Retirement.Found
