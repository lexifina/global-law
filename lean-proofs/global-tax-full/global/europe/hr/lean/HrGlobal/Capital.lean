import HrGlobal.Pit

/-!
# HR 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (Zakon o porezu na dohodak čl. 67): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Porez na dohodak od kapitalnih dobitaka (pass 6)
Source: PwC Worldwide Tax Summaries, Croatia, Individual - Income determination, accessed 2025-07-14 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* capital gains on financial assets disposed of within 2 years of acquisition: 12 %; exempt after 2 years and between spouses / close family
-/

namespace HrGlobal.Capital
open TaxKernel TaxKernel.Global

/-- Zakon o porezu na dohodak (capital gains on financial assets 12 %; exempt after two years of holding) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds) && d.heldMonths < 24
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 1200).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Porez na dohodak od kapitalnih dobitaka (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "Zakon o porezu na dohodak (capital gains on financial assets 12 %; exempt after two years of holding)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Porez na dohodak od kapitalnih dobitaka", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["HR 1100 Porez na dohodak od kapitalnih dobitaka: PwC WWTS Individual - Income determination, 2025-07-14 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (·.kind.isRealEstate) then ["1100 1100 real estate gains (income from property, taxable within 2 years) not modelled: the B source gives no rate"] else [])
  ++ (if !g.disposals.isEmpty then ["1100 the B source's family-transfer exemption is not applied (disposals are taken as sales to third parties)"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 12000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 24 }] == 0
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0

end HrGlobal.Capital
