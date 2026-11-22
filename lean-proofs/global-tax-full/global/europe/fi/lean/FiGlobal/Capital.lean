import FiGlobal.Pit

/-!
# FI 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (Tuloverolaki 45-50 §): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Luovutusvoittovero (pääomatulo) (pass 6)
Source: PwC Worldwide Tax Summaries, Finland, Individual - Income determination, accessed 2025-07-18 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* capital income 30 % to EUR 30 000, 34 % above
* permanent family home used ≥ 2 years: exempt
* de minimis: total sale prices in the year ≤ EUR 1 000 exempt
-/

namespace FiGlobal.Capital
open TaxKernel TaxKernel.Global

/-- Tuloverolaki 45-50 § (capital income 30 % to EUR 30 000, 34 % above; home used two years exempt) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.ofList [(0, 3000), (30000, 3400)]).tax {} b
def p6cgReSel (d : Disposal) : Bool := d.kind.isRealEstate && !d.mainHome
def p6cgReBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgReSel).map (·.gain)))) BP
def p6cgReTax (b : Int) : Int := (Schedule.ofList [(0, 3000), (30000, 3400)]).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Luovutusvoittovero (pääomatulo) (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "Tuloverolaki 45-50 § (capital income 30 % to EUR 30 000, 34 % above; home used two years exempt)"),  charge .pit "Luovutusvoittovero (pääomatulo) (real estate)" (isum ((g.disposals.filter p6cgReSel).map (·.gain))) (fun _ => p6cgReBase g.disposals) (fun _ => p6cgReTax (p6cgReBase g.disposals)) (event := "disposals 2025") (statute := "Tuloverolaki 45-50 § (capital income 30 % to EUR 30 000, 34 % above; home used two years exempt)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Luovutusvoittovero (pääomatulo)", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["FI 1100 Luovutusvoittovero (pääomatulo): PwC WWTS Individual - Income determination, 2025-07-18 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.disposals.isEmpty then ["1100 the 30 000 band is shared with other capital income (dividends, interest) in the 1.x model: applied to the disposals alone; the EUR 1 000 de-minimis and the deemed acquisition cost (20 %/40 %) not applied; securities and real estate gains each run through the scale separately"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 32800
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0
#guard p6cgReTax (p6cgReBase [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 32800
#guard p6cgReBase [{ kind := .home, proceeds := 150000, cost := 50000, mainHome := true }] == 0
#guard p6cgReBase [{ kind := .realEstate, proceeds := 50000, cost := 150000 }] == 0

end FiGlobal.Capital
