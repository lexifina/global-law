-- T0: the copy with every knob at its default reproduces final.txt (C2 search + check lines)
#eval search (top := 3) (exDate 50000 "C2 three days around a capital gain dividend, other ST gains 50k")
#eval check (exDate 50000 "C2") "hold FundA" NONE
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold day 130" SELL1
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold day 162" SELL33
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold day 330 (201 days)" HOLD201
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold and rebought day 130, sold day 162" PLAN
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold and rebought day 130, sold day 131"
  [["sell FundA", "buy GainFund"], ["buy GainFund", "sell GainFund"], ["sell GainFund", "buy FundA"], [], [], [], []]
