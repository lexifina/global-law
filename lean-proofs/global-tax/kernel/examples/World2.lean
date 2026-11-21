import TaxKernel.World2

/-!
# The 1.4 parts on toy numbers (not statutes), checked by `#guard`

Run: `cd ~/cmp20/kernel && lake env lean examples/World2.lean` (no output = every check holds).
-/

open TaxKernel

-- Column tariff: up to 100 a 0 % band to 50 then 10 %; up to 200 a flat 10 % (the zero band withdrawn); above, 20 %
def colA : Schedule := Schedule.ofList [(0, 0), (50, 1000)]
def colB : Schedule := Schedule.flat 1000
def colC : Schedule := Schedule.flat 2000
def toyCols : List (Int × Schedule) := [(100, colA), (200, colB)]
#guard columnTicks toyCols colC 100 = 50000
#guard columnTicks toyCols colC 101 = 101000
#guard columnTicks toyCols colC 201 = 402000
-- the notches sit at the column limits: 5 units of tax at 100 -> 101, 20.1 at 200 -> 201 (ticks / 10000)
#guard columnJumps toyCols colC = [(100, 50000), (200, 201000)]

-- Indexed amounts: coefficient 1.4567, rounded half up
#guard indexAmount .halfUp 14567 10000 1000 = 1457
#guard indexChain .halfUp [(11, 10), (11, 10)] 1000 = 1210
#guard indexReproduces .halfUp 14567 10000 [(1000, 1457), (2000, 2913)]
#guard (colA.indexed .halfUp 14567 10000).bands.map Band.lo = [0, 73]
