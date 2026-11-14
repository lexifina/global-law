-- T4: earlier law. §852(b)(4) said "less than 31 days" until the Deficit Reduction Act of 1984 made it 6 months.
def ex (nm : String) : Sc := exDate 50000 nm
def exOut (nm : String) : Sc := { exDate 50000 nm with clearBy := some (1, 3) }
#eval check { ex "T4 pre-1984 (30 days)" with six := 30 } "hold FundA" NONE
#eval check { ex "T4 pre-1984 (30 days)" with six := 30 } "sold day 162, no wash (33 days)" SELL33
#eval check { ex "T4 pre-1984 (30 days)" with six := 30 } "PLAN" PLAN
#eval check { ex "T4 pre-1984 (30 days)" with six := 30 } "sold day 130" SELL1
#eval best { exOut "T4 pre-1984, out by day 162, wash sales off" with six := 30, noWash := true }
#eval best { exOut "T4 current, out by day 162, wash sales off" with noWash := true }
