import TaxKernel.World

/-!
# The 1.3 world parts on toy numbers (not statutes): how each is called, checked by `#guard`

Run: `cd cmp20/kernel && lake env lean examples/World.lean` (no output = every check holds).
-/

open TaxKernel

-- Indexed unit: thresholds printed in thousandths of a unit worth 50,000 money units (a UVT/UTM-style unit)
def toyUnits : Schedule := Schedule.ofUnits [(0, 0), (95000, 1900), (150000, 2800)] .halfUp 1000 50000
#guard toyUnits.bands.map Band.lo = [0, 4750000, 7500000]
#guard toyUnits.bands.map Band.rate = [0, 1900, 2800]
#guard unitsToMoney .halfUp 1000 50000 1500 = 75000
#guard moneyToUnits .down 1000 50000 75000 = 1500
-- a tax computed in units (19 % above 95 units), converted back half up
#guard viaUnits (fun u => pos (u - 95000) * 19 / 100) .down .halfUp 1000 50000 6000000 = 237500

-- Schedular: wages taxed 10 % flat, rent 15 %; annual overlay 20 % above 1,000 on the sum
def toyCedulas : List Cedula :=
  [{ name := "salary", base := 10000, tax := fun b => b / 10 }, { name := "rent", base := 2000, tax := fun b => b * 15 / 100 }]
def toyGlobal (x : Int) : Int := (Schedule.flatAbove 1000 2000).tax Rule.unitDown x
#guard cedularTotal toyCedulas = 1300
#guard cedularBase toyCedulas = 12000
#guard cedularDetail toyCedulas = [("salary", 1000), ("rent", 300)]
#guard overlayTax toyGlobal toyCedulas true = 900      -- 2,200 global less 1,300 already paid
#guard overlayTax toyGlobal toyCedulas false = 2200
#guard cedularTotal toyCedulas + overlayTax toyGlobal toyCedulas true = max 1300 2200

-- Zakat: 2.5 % of the whole base once it reaches a nisab of 6,000
#guard (zakat 6000 250).amount 5999 = 0
#guard (zakat 6000 250).amount 6000 = 150
#guard (zakat 6000 250).amount 10000 = 250

-- Territorial: foreign income left out
#guard sourceBase true 1000 500 = 1000
#guard sourceBase false 1000 500 = 1500

-- The tax on a minimum wage of 20,000 exempt, on a 15 % flat tax
def toyFlat (x : Int) : Int := (Schedule.flat 1500).tax Rule.unitDown x
#guard exemptTaxOf toyFlat 20000 15000 = 0
#guard exemptTaxOf toyFlat 20000 30000 = 1500

-- Cumulative withholding over three months on cumulative bases 1,000 / 2,500 / 4,000
#guard cumWithholdings toyFlat 0 [1000, 2500, 4000] = [150, 225, 225]
#guard listSum (cumWithholdings toyFlat 0 [1000, 2500, 4000]) = toyFlat 4000
