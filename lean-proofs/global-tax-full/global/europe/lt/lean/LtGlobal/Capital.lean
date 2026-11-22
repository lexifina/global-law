import LtGlobal.Pit

/-!
# LT 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (GPMĮ 17 str. (gains)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 GPM nuo turto pardavimo pajamų (pass 6)
Source: PwC Worldwide Tax Summaries, Lithuania, Individual - Income determination, accessed 2025-08-10 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* gain = price - acquisition price: 15 % to EUR 253 065 (2025), 20 % above
* exempt: financial-instrument gains ≤ EUR 500 a year; EEA housing with declared residence (conditions)
-/

namespace LtGlobal.Capital
open TaxKernel TaxKernel.Global

/-- Gyventojų pajamų mokesčio įstatymas 6 str. (15 % to EUR 253 065 for 2025, 20 % above); 17 str. exemptions -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.ofList [(0, 1500), (253065, 2000)]).tax {} b
def p6cgReSel (d : Disposal) : Bool := d.kind.isRealEstate && !d.mainHome
def p6cgReBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgReSel).map (·.gain)))) BP
def p6cgReTax (b : Int) : Int := (Schedule.ofList [(0, 1500), (253065, 2000)]).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "GPM nuo turto pardavimo pajamų (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "Gyventojų pajamų mokesčio įstatymas 6 str. (15 % to EUR 253 065 for 2025, 20 % above); 17 str. exemptions"),  charge .pit "GPM nuo turto pardavimo pajamų (real estate)" (isum ((g.disposals.filter p6cgReSel).map (·.gain))) (fun _ => p6cgReBase g.disposals) (fun _ => p6cgReTax (p6cgReBase g.disposals)) (event := "disposals 2025") (statute := "Gyventojų pajamų mokesčio įstatymas 6 str. (15 % to EUR 253 065 for 2025, 20 % above); 17 str. exemptions")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 GPM nuo turto pardavimo pajamų", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["LT 1100 GPM nuo turto pardavimo pajamų: PwC WWTS Individual - Income determination, 2025-08-10 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.disposals.isEmpty then ["1100 the EUR 253 065 band is applied to each class of disposals alone (it is shared with other income); the EUR 500 exemption is not applied; the declared-residence conditions are taken as met for a main home"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 15000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0
#guard p6cgReTax (p6cgReBase [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 15000
#guard p6cgReBase [{ kind := .home, proceeds := 150000, cost := 50000, mainHome := true }] == 0
#guard p6cgReBase [{ kind := .realEstate, proceeds := 50000, cost := 150000 }] == 0

end LtGlobal.Capital
