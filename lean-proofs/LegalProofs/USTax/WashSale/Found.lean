import LegalProofs.USTax.WashSale.Search

/-!
# What the wash-sale search found, re-checked

For each market, the plan the search returned (the largest loss recognised while staying invested, then the least
capital), re-run by the kernel, beside the plain sell-and-buy-back that the rule catches.
-/

namespace Legal.USTax.WashSale.Found
open Legal.USTax.WashSale Legal.USTax.WashSale.Search

def summary (b : Option Book) : Option (Int × Int) := b.map fun b => (b.recognized, b.disallowed)

/-- Selling the index fund and buying it back the same day: the $3,000 loss is disallowed and moved into the new
unit's basis. -/
theorem fund_same_day : summary (execute M [⟨40, 0, false⟩, ⟨40, 0, true⟩] (start [0, 1])) = some (0, 3000) := by decide

/-- **Switching to a fund that tracks a different index of the same market:** the whole loss is recognised, and the
investor is never out of the market. -/
theorem fund_switch : summary (execute M [⟨40, 0, false⟩, ⟨40, 1, true⟩] (start [0, 1])) = some (-3000, 0) := by decide

/-- **A single stock has no substitute, so the search doubles up:** buy a second share, wait 31 days, sell the old
one. The loss is recognised (`outside_window`), at the cost of holding twice the position for a month. -/
theorem stock_double_up : summary (execute M [⟨40, 2, true⟩, ⟨71, 2, false⟩] (start [2])) = some (-4000, 0) := by decide

/-- Selling the stock and buying it back the same day: disallowed. -/
theorem stock_same_day : summary (execute M [⟨40, 2, false⟩, ⟨40, 2, true⟩] (start [2])) = some (0, 4000) := by decide

/-- **Bitcoin is not a security, so the rule does not reach it** (`outside_scope`): sell and buy back on the same day
and the whole $5,000 loss counts. -/
theorem bitcoin_same_day : summary (execute M [⟨40, 3, true⟩, ⟨40, 3, false⟩] (start [3, 4])) = some (-5000, 0) := by
  decide

/-- The same trade in the bitcoin ETF, whose shares are securities, is caught. -/
theorem etf_same_day : summary (execute M [⟨40, 4, true⟩, ⟨40, 4, false⟩] ⟨[⟨4, 1004, 0, 10000⟩], [], [], 0, 0, 0, 0⟩) =
    some (0, 5000) := by decide

end Legal.USTax.WashSale.Found
