import DKTax.Household

/-!
# Official worked examples (referee b): Skatteministeriet, 2023

* "Skatteberegningseksempel for en ugift skatteyder i 2023" (svmn.dk/tal-og-metode/satser/skatte-og-afgiftsberegning/
  skatteberegningseksempel-for-en-ugift-skatteyder-i-2023, 07-08-2023; copy `refs/web/…ugift…txt`), Tabel 1-4, 6.
* "Skatteberegningseksempel for et ægtepar i 2023" (…/skatteberegningseksempel-for-et-aegtepar-i-2023), Tabel 1-5, 7.

Both live in Ballerup (kommuneskat 25,50 %, kirkeskat 0,72 %) and are church members. The befordringsfradrag
(with the low-income tillæg of 2.458 kr. computed in the example, "[46]") is an input. Ejendomsværdiskat is a
separate tax and not modelled. Each `#guard` compares the model with a printed figure, in øre (ticks / 100),
allowing 1 øre for the example's own rounding. Where the example contradicts itself the comment says which
printed figure is used (FINDINGS F8).
-/

namespace DKTax.Tests
open DKTax TaxKernel

def ballerup : Opts := { munRate7 := 2550000, churchRate7 := 72000, church := true }

def ugift : PIn :=
  { wages := 750000, atpOwn := 1136, atpEmployer := 2272, ownPension := 42750, employerPension := 85500,
    groupLife := 1800, ratepension := 60900, interestIncome := 15000, interestExpense := 45000,
    union := 6000, commute := 10000, aktie := 80000 }

def ugiftB : PBase := personBase p2023 false ugift
def ugiftR : PRes := (computeTaxes p2023 ballerup false [ugiftB]).headD default

def near (ticks oere : Int) : Bool := (ticks / 100 - oere).natAbs ≤ 1

#guard ugiftB.am == 56489                          -- [5]
#guard ugiftB.personal == 590525                   -- [8]/[9] "Personlig indkomst"
#guard ugiftB.bf == 45600 && ugiftB.job == 2700    -- [13], [14]
#guard ugiftB.pensDed == 9348                      -- [15] = 12 pct. of 77.900
#guard ugiftB.lmf == 73648                         -- [22]
#guard ugiftB.taxable == 486877                    -- [26]
#guard near (ugiftR.gross.mun + ugiftR.gross.ch) 12765915     -- [47] 127.659,15
#guard near (ugiftR.final.mun + ugiftR.final.ch) 11507355     -- [49] 115.073,55 (after personfradrag)
#guard near ugiftR.nedslag11 240000                           -- [51] 2.400,00
#guard near ugiftR.bundGross 7121732                          -- [53] 71.217,32
#guard near (ugiftR.bundGross - p2023.bundRate * p2023.pf) 6542852  -- [55] 65.428,52 (after personfradrag)
#guard near ugiftR.topPersonal 313779                         -- [65] 3.137,79
#guard ugiftR.topCapital == 0                                 -- [66]
-- [68] Samlet indkomstskat 181.239,85 = kommune/kirke after pf − § 11 nedslag + bundskat after pf + topskat
#guard near (ugiftR.final.mun + ugiftR.final.ch + ugiftR.final.bund + ugiftR.final.top) 18123985
#guard near (ugiftR.ak27 + ugiftR.ak42) 2476500               -- [73] 24.765,00

/-- The married couple: spouse 2 earns 350.000 kr., pays ATP 1.006 kr. -/
def aegt1 : PIn := ugift
def aegt2 : PIn :=
  { wages := 350000, atpOwn := 1006, atpEmployer := 2012, ownPension := 19950, employerPension := 39900,
    interestIncome := 7500, interestExpense := 2500, union := 6000, akasse := 7000, commute := 8000 + 2458,
    aktie := 40000 }
def aegtB : List PBase := [personBase p2023 false aegt1, personBase p2023 false aegt2]
def aegtR : List PRes := computeTaxes p2023 ballerup true aegtB
def r1 : PRes := aegtR.headD default
def r2 : PRes := aegtR[1]!

#guard (aegtB[1]!).am == 26323                     -- [5] spouse 2
#guard (aegtB[1]!).personal == 302721              -- [9] (the example's [24] prints 302.712: a typo, F8)
#guard (aegtB[1]!).bf == 41739                     -- [14]
#guard (aegtB[1]!).pensDed == 6941                 -- [16]
#guard (aegtB[1]!).lmf == 74838                    -- [23]
#guard r1.taxable == 486877 && r2.taxable == 232883  -- [27]
#guard near r1.nedslag11 200000                    -- [52] 2.000,00 (−30.000 + 5.000 = −25.000)
#guard near r2.bundGross 3650815                   -- [54] 36.508,15
#guard near (r1.final.mun + r1.final.ch + r1.final.bund + r1.final.top) 18163985   -- [72] 181.639,85
#guard near (r2.final.mun + r2.final.ch + r2.final.bund + r2.final.top) 7919568    -- [72] 79.195,68
#guard near (r1.ak27 + r1.ak42) 2193000            -- [79] 21.930,00 (threshold transfer 18.900)
#guard near (r2.ak27 + r2.ak42) 1080000            -- [79] 10.800,00

end DKTax.Tests
