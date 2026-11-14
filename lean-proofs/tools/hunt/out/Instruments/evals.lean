
/-! ### Runs -/

#eval search (top := 3) (dip stockWorld 50000 true "A1 stock: dip and recovery, other ST gains 50k")
#eval search (top := 3) (dip3 digitalWorld 50000 true "A2 digital: dip and recovery, other ST gains 50k")
#eval search (top := 2) (dip3 digitalWorld 50000 false "A3 digital: dip and recovery, statute only")
#eval search (top := 2) (exit stockWorld2 true "A4 stock (fund + future): appreciated, exit wanted")
#eval search (top := 2) (exitWindow stockWorld2 true "A5 stock (fund + future): exit wanted, 85 days of exposure tolerated")
#eval search (top := 2) (exit stockWorld true "A6 stock with a second, not identical fund: exit wanted")
#eval search (top := 2) (exit digitalWorld true "A7 digital: appreciated, exit wanted")
#eval search (top := 2) (exit digitalWorld false "A8 digital: exit wanted, statute only")
#eval search (top := 2) (shortHorizon stockWorld 0 true "A9 stock: exposure wanted for 10 months")
#eval search (top := 2) (upDown stockWorld true "A10 stock: up 30 in year 1, down 25 in year 2")
#eval search (top := 3) (flat stockWorld 130 50000 0 true "B1 no exposure, market up 30, other ST gains 50k")
#eval search (top := 2) (flat stockWorld 75 50000 0 true "B2 no exposure, market down 25, other ST gains 50k")
#eval search (top := 2) (flat stockWorld 130 50000 50000 true "B3 no exposure, market up 30, other ST and LT gains 50k")
#eval search (top := 2) (flat stockWorld 130 50000 0 false "B4 no exposure, market up 30, statute only")
#eval search (top := 10) (distScen distWorld 50000 0 "C1 distributions, other ST gains 50k")
#eval search (top := 3) (exDate 50000 "C2 three days around a capital gain dividend, other ST gains 50k")
#eval search (top := 2) (lieuScen2 false "C3 capital loss + interest income; no regulations under 263(h)(4)(B)")
#eval search (top := 2) (lieuScen2 true "C4 capital loss + interest income; any hedge suspends the 263(h) period")

/-! ### Fixed plans, for the findings -/

-- the same straddle (long future, short FundB, opened day 5, closed in January) when the market rises and when it falls
#eval check (flat stockWorld 130 50000 0 true "B1") "nothing" [[], [], [], []]
#eval check (flat stockWorld 130 50000 0 true "B1") "long future + short FundB, closed day 385"
  [["buy IndexFuture", "short FundB"], [], ["sell IndexFuture", "cover FundB"], []]
#eval check (flat stockWorld 75 50000 0 true "B2") "long future + short FundB, closed day 385"
  [["buy IndexFuture", "short FundB"], [], ["sell IndexFuture", "cover FundB"], []]
#eval check (flat stockWorld 130 50000 0 true "B1") "the same, both legs closed on 31 December of year 1"
  [["buy IndexFuture", "short FundB"], ["sell IndexFuture", "cover FundB"], [], []]
#eval check (flat stockWorld 130 50000 50000 true "B3") "long future + short FundB, closed day 385"
  [["buy IndexFuture", "short FundB"], [], ["sell IndexFuture", "cover FundB"], []]
#eval check (flat stockWorld 130 50000 0 true "B1") "long future + short FundA (same class), closed day 385"
  [["buy IndexFuture", "short FundA"], [], ["sell IndexFuture", "cover FundA"], []]
-- a capital gain dividend of 10,000 on day 130
#eval check (exDate 50000 "C2") "hold FundA" [[], [], [], [], [], [], []]
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold day 130"
  [["sell FundA", "buy GainFund"], ["sell GainFund", "buy FundA"], [], [], [], [], []]
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold day 162"
  [["sell FundA", "buy GainFund"], [], [], ["sell GainFund", "buy FundA"], [], [], []]
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold day 330 (201 days)"
  [["sell FundA", "buy GainFund"], [], [], [], ["sell GainFund", "buy FundA"], [], []]
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold and rebought day 130, sold day 162"
  [["sell FundA", "buy GainFund"], ["buy GainFund", "sell GainFund"], [], ["sell GainFund", "buy FundA"], [], [], []]
#eval check (exDate 50000 "C2") "GainFund bought day 129, sold and rebought day 130, sold day 131"
  [["sell FundA", "buy GainFund"], ["buy GainFund", "sell GainFund"], ["sell GainFund", "buy FundA"], [], [], [], []]

end Legal.USTax.Hunt.Instruments
