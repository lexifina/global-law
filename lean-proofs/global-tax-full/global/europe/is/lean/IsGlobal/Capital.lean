import IsGlobal.Pit

/-!
# IS 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (Lög nr. 90/2003 (fjármagnstekjuskattur)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Fjármagnstekjuskattur af söluhagnaði (pass 6)
Source: PwC Worldwide Tax Summaries, Iceland, Individual - Income determination, accessed 2025-06-11 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* private property gains: capital income 22 %
* exempt: residential property owned > 2 years; private movables
-/

namespace IsGlobal.Capital
open TaxKernel TaxKernel.Global

/-- lög nr. 90/2003 um tekjuskatt (fjármagnstekjur 22 %; residential property owned over two years exempt) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 2200).tax {} b
def p6cgReSel (d : Disposal) : Bool := d.kind.isRealEstate && d.heldMonths < 24
def p6cgReBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgReSel).map (·.gain)))) BP
def p6cgReTax (b : Int) : Int := (Schedule.flat 2200).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Fjármagnstekjuskattur af söluhagnaði (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "lög nr. 90/2003 um tekjuskatt (fjármagnstekjur 22 %; residential property owned over two years exempt)"),  charge .pit "Fjármagnstekjuskattur af söluhagnaði (real estate)" (isum ((g.disposals.filter p6cgReSel).map (·.gain))) (fun _ => p6cgReBase g.disposals) (fun _ => p6cgReTax (p6cgReBase g.disposals)) (event := "disposals 2025") (statute := "lög nr. 90/2003 um tekjuskatt (fjármagnstekjur 22 %; residential property owned over two years exempt)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Fjármagnstekjuskattur af söluhagnaði", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["IS 1100 Fjármagnstekjuskattur af söluhagnaði: PwC WWTS Individual - Income determination, 2025-06-11 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.kind == .realEstate || d.kind == .land) then ["1100 the two-year exemption is applied to all real estate (it is for residential property only)"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 22000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0
#guard p6cgReTax (p6cgReBase [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 22000
#guard p6cgReBase [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 24 }] == 0
#guard p6cgReBase [{ kind := .realEstate, proceeds := 50000, cost := 150000 }] == 0

end IsGlobal.Capital
