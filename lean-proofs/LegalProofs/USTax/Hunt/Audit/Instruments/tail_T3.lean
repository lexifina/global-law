-- T3: ablation. `exOut` forces GainFund to be gone on leaving day 162, so the six-month hold cannot stand in.
def exOut (nm : String) : Sc := { exDate 50000 nm with clearBy := some (1, 3) }
#eval best (exOut "T3 all rules")
-- rules the plan uses, one at a time (search + the fixed plan)
#eval best { exOut "T3 no §1091(a)" with noWash := true }
#eval check { exOut "T3 no §1091(a)" with noWash := true } "PLAN" PLAN
#eval best { exOut "T3 no §1091(d) basis" with noBasis := true }
#eval check { exOut "T3 no §1091(d) basis" with noBasis := true } "PLAN" PLAN
#eval best { exOut "T3 no §1223(3) tacking" with noTack := true }
#eval check { exOut "T3 no §1223(3) tacking" with noTack := true } "PLAN" PLAN
#eval best { exOut "T3 no §852(b)(3)(B)" with cgdOrd := true }
#eval check { exOut "T3 no §852(b)(3)(B)" with cgdOrd := true } "PLAN" PLAN
#eval check { exOut "T3 no §852(b)(3)(B)" with cgdOrd := true } "hold FundA" NONE
#eval best { exOut "T3 no §852(b)(4)(A)" with no852b4 := true }
#eval check { exOut "T3 no §852(b)(4)(A)" with no852b4 := true } "sold day 130, nothing else" SELL1
-- trades the plan uses, one at a time
#eval best { exOut "T3 ban buy GainFund" with ban := ["buy GainFund"] }
#eval best { exOut "T3 ban sell GainFund" with ban := ["sell GainFund", "deliver GainFund"] }
#eval best { exOut "T3 ban sell FundA" with ban := ["sell FundA", "deliver FundA"] }
#eval best { exOut "T3 ban buy FundA" with ban := ["buy FundA"] }
#eval best { exOut "T3 ban buy FundA + buy DivStock + shorts" with ban := ["buy FundA", "buy DivStock", "short FundA", "short DivStock", "short GainFund"] }
#eval best { exOut "T3 no second lot of a held instrument" with oneLot := true }
#eval check { exOut "T3 no second lot" with oneLot := true } "PLAN" PLAN
#eval best { exOut "T3 one lot at a time (maxLots 1)" with maxLots := 1 }
-- every trade the plan does not use removed: must still be found, same figure
def unused : List String := ["buy DivStock", "sell DivStock", "deliver DivStock", "cover DivStock", "short DivStock",
  "short FundA", "cover FundA", "deliver FundA", "short GainFund", "cover GainFund", "deliver GainFund"]
#eval best { exOut "T3 only the plan's four kinds of trade" with ban := unused }
#eval best { exOut "T3 only the plan's four kinds, world without DivStock" with ban := unused, world := distWorld1.extract 0 2 }
-- no dividend at all: nothing to find
#eval best { exOut "T3 GainFund pays nothing" with world := distWorld1.map fun i => { i with dist := [] } }
