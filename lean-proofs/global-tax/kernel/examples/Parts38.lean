import TaxKernel

/-!
# The 1.2 parts on toy numbers (not statutes): how each is called, checked by `#guard`

Run: `cd ~/cmp20/kernel && lake env lean examples/Parts38.lean` (no output = every check holds).
-/

open TaxKernel

-- Multipliers on a simple tax of 1,000 (a canton at 98 %, a city at 119 %)
def toyKanton : Multiplier := { name := "canton", rate := 9800 }
def toyStadt : Multiplier := { name := "city", rate := 11900 }
#guard applyMultipliers [toyKanton, toyStadt] 1000 = [("canton", 980), ("city", 1190)]
#guard multipliedTotal [toyKanton, toyStadt] 1000 = 2170

-- Tax at an average rate: a 20 % flat tariff above 10,000; the rate reached on 50,000 (16 %) applied to 40,000
def toyTariff (x : Int) : Int := (Schedule.flatAbove 10000 2000).tax Rule.unitDown x
#guard atAverageRate .down toyTariff 50000 40000 = 6400
#guard averageRateScaled toyTariff 50000 10000 = 1600
-- rate splitting: divisor 2 = splitting (theorem `rateSplitting_two`); divisor 1.9 takes the rate higher up: more tax than full splitting
#guard rateSplitting .down toyTariff 20000 60000 = 2 * toyTariff 30000
#guard rateSplitting .down toyTariff 19000 60000 = 8198

-- A credit of 700 against taxes of 500 then 400: in order 500 + 200; in proportion 389 + 311
#guard allocateOrdered 700 [500, 400] = [500, 200]
#guard allocateProportional 700 [500, 400] = [389, 311]

-- Child scales
#guard perChildByRank [100, 140, 200] 4 = 640
#guard perChildByCount [50, 100, 150] 2 = 200
#guard familyTotal [1000, 2500, 5500] 3000 5 = 11500

-- Attribution: 30 % of (60,000 + 0) to the spouse, capped at 12,000
#guard attributeIncome 60000 0 3000 12000 = (48000, 12000)
#guard attributeIncome 60000 20000 3000 12000 = (56000, 24000)

-- Low-band reduction vs zero band on a 25 % / 40 % / 50 % schedule, allowance 10,000, income 60,000 (ticks)
def toySched : Schedule := Schedule.ofList [(0, 2500), (15000, 4000), (40000, 5000)]
#guard toySched.ticks 60000 - lowBandReduction toySched 10000 = 212500000
#guard toySched.ticks (60000 - 10000) = 187500000

-- Spill: allowance 30,000 against income 10,000; the unused 20,000 at 15 % is worth 3,000 against contributions
#guard spillAllowance 30000 10000 1500 = (0, 3000)

-- Stepped vs proportional withdrawal: 777 reduced by 20 per complete 1,000 above 12,000
def toyStep : SteppedTaper := { full := 777, start := 12000, perStep := 20, step := 1000 }
#guard toyStep.amount 13999 = 757
#guard toyStep.amount 14000 = 737
#guard toyStep.toTaper.amount 13999 = 738

-- Tariff columns: a 10 % / 20 % band schedule printed as "amount at the threshold + rate on the excess" with the
-- amount rounded down to whole units falls by 0.2 units at the threshold (the NL pattern); the exact columns do not
def toyBands : Schedule := Schedule.ofList [(0, 1000), (333, 2000)]
def toyColsRounded : List CumRow := [{ lo := 0, base := 0, rate := 1000 }, { lo := 333, base := 33, rate := 2000 }]
#guard toyBands.cumRows = toyColsRounded
#guard cumMonoAt toyColsRounded [332, 333] = false
#guard cumTicks toyColsRounded 333 - toyBands.ticks 333 = -3000
#guard cumAgrees toyColsRounded toyBands [0, 100, 332, 333, 1000] 3000
-- Malta-style "rate × income − subtract": 20 % above 10,000 written as 20 % of all income minus 2,000
def toySub : List SubRow := [{ lo := 0, rate := 0, subtract := 0 }, { lo := 10000, rate := 2000, subtract := 2000 }]
#guard subAgrees toySub (Schedule.flatAbove 10000 2000) [0, 5000, 10000, 10001, 50000]
#guard subJumps toySub = [(0, 0), (10000, 0)]
