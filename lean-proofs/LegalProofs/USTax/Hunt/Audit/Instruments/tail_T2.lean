-- T2: close the gap. Words added to §852(b)(4)(A): after "on the sale or exchange of such share" insert
-- "(or of any stock or securities the basis of which is determined under section 1091(d) by reference to such share)".
def ex (nm : String) : Sc := exDate 50000 nm
def exOut (nm : String) : Sc := { exDate 50000 nm with clearBy := some (1, 3) }   -- out of GainFund by day 162
#eval check (ex "T2 open") "hold FundA" NONE
#eval check { ex "T2 closed" with taintFix := true } "hold FundA" NONE
#eval check (ex "T2 open") "PLAN" PLAN
#eval check { ex "T2 closed" with taintFix := true } "PLAN" PLAN
#eval check { ex "T2 closed" with taintFix := true } "hold 201 days" HOLD201
#eval check { ex "T2 closed" with taintFix := true } "sold day 162, no wash" SELL33
#eval check { ex "T2 closed" with taintFix := true } "sold day 130 into FundA, GainFund rebought day 131, sold day 162"
  [["sell FundA", "buy GainFund"], ["sell GainFund", "buy FundA"], ["sell FundA", "buy GainFund"], ["sell GainFund", "buy FundA"], [], [], []]
-- whole search, GainFund must be gone on leaving day 162: open vs closed
#eval best (exOut "T2 search, out by day 162, open")
#eval best { exOut "T2 search, out by day 162, closed" with taintFix := true }
-- whole search without that constraint: the six-month hold is untouched by the fix
#eval best (ex "T2 search, open")
#eval best { ex "T2 search, closed" with taintFix := true }
-- baselines elsewhere must not move
#eval best (distScen distWorld 50000 0 "C1 open")
#eval best { distScen distWorld 50000 0 "C1 closed" with taintFix := true }
#eval best (dip stockWorld 50000 true "A1 open")
#eval best { dip stockWorld 50000 true "A1 closed" with taintFix := true }
