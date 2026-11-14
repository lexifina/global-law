-- T1: strict reading. `strict` adds §852(b)(4)(C)(ii) and the §1.1091-1(d) matching order.
def ex (nm : String) : Sc := exDate 50000 nm
#eval check { ex "T1 strict" with strict := true } "hold FundA" NONE
#eval check { ex "T1 strict" with strict := true } "PLAN" PLAN
#eval check { ex "T1 strict" with strict := true } "sold day 162, no wash" SELL33
#eval check { ex "T1 strict" with strict := true } "hold 201 days" HOLD201
#eval best { ex "T1 strict, search" with strict := true }
-- "6 months" counted as 181 / 184 / 190 days
#eval check { ex "T1 six=181" with strict := true, six := 181 } "PLAN" PLAN
#eval check { ex "T1 six=184" with strict := true, six := 184 } "PLAN" PLAN
#eval check { ex "T1 six=200" with strict := true, six := 200 } "PLAN" PLAN
#eval check { ex "T1 six=200" with strict := true, six := 200 } "hold 201 days" HOLD201
#eval check { ex "T1 six=201" with strict := true, six := 201 } "hold 201 days" HOLD201
#eval check { ex "T1 six=201" with strict := true, six := 201 } "PLAN" PLAN
-- the same-day sale and repurchase replaced by forms that change the position:
-- (a) out of GainFund into FundA for one day, back on day 131 (acquisition AFTER the loss sale)
#eval check { ex "T1 strict" with strict := true } "sold day 130 into FundA, GainFund rebought day 131, sold day 162"
  [["sell FundA", "buy GainFund"], ["sell GainFund", "buy FundA"], ["sell FundA", "buy GainFund"], ["sell GainFund", "buy FundA"], [], [], []]
-- (b) double up on the ex-date (two units for a day), sell the old lot on day 131
def exDouble : Sc := { ex "T1 strict, double-up" with strict := true, expo := #[[1], [2], [1], [1], [1], [1], [1]] }
#eval check exDouble "second lot bought day 130, first lot sold day 131, second sold day 162"
  [["sell FundA", "buy GainFund"], ["buy GainFund"], ["sell GainFund"], ["sell GainFund", "buy FundA"], [], [], []]
#eval check exDouble "hold FundA" NONE
-- the day-162 exit moved inside 30 days of the replacement purchase (day 131 only date available): model's strict §1091(a)
#eval check { ex "T1 strict" with strict := true } "PLAN but final sale day 131"
  [["sell FundA", "buy GainFund"], ["buy GainFund", "sell GainFund"], ["sell GainFund", "buy FundA"], [], [], [], []]
-- does the plan need other short-term gain?  none: the ST loss is worth only $3,000 a year
#eval check { exDate 0 "T1 g=0" with strict := true } "hold FundA" NONE
#eval check { exDate 0 "T1 g=0" with strict := true } "PLAN" PLAN
#eval check { exDate 5000 "T1 g=5000" with strict := true } "hold FundA" NONE
#eval check { exDate 5000 "T1 g=5000" with strict := true } "PLAN" PLAN
-- taxpayer who also has long-term gains elsewhere (the usual case): same?
#eval check { exDate 50000 "T1 gLT=50000" with strict := true, gLT := [50000, 50000] } "hold FundA" NONE
#eval check { exDate 50000 "T1 gLT=50000" with strict := true, gLT := [50000, 50000] } "PLAN" PLAN
