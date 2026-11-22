import SeGlobal.Pit

/-!
# SE 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (Inkomstskattelagen 41-52 kap. (30 %, 22/30 bostad)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Kapitalvinstskatt (inkomst av kapital) (pass 6)
Source: PwC Worldwide Tax Summaries, Sweden, Individual - Income determination, accessed 2025-06-24 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* shares / other investments: capital income 30 %
* private real property, tenant-owner flats: 22 % effective; deferral on a replacement home (not modelled)
-/

namespace SeGlobal.Capital
open TaxKernel TaxKernel.Global

/-- Inkomstskattelagen 41-48 kap., 65 kap. 7 § (30 %; private real property 22/30 of the gain = 22 %) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 3000).tax {} b
def p6cgReSel (d : Disposal) : Bool := d.kind.isRealEstate
def p6cgReBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgReSel).map (·.gain)))) BP
def p6cgReTax (b : Int) : Int := (Schedule.flat 2200).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Kapitalvinstskatt (inkomst av kapital) (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "Inkomstskattelagen 41-48 kap., 65 kap. 7 § (30 %; private real property 22/30 of the gain = 22 %)"),  charge .pit "Kapitalvinstskatt (inkomst av kapital) (real estate)" (isum ((g.disposals.filter p6cgReSel).map (·.gain))) (fun _ => p6cgReBase g.disposals) (fun _ => p6cgReTax (p6cgReBase g.disposals)) (event := "disposals 2025") (statute := "Inkomstskattelagen 41-48 kap., 65 kap. 7 § (30 %; private real property 22/30 of the gain = 22 %)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Kapitalvinstskatt (inkomst av kapital)", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["SE 1100 Kapitalvinstskatt (inkomst av kapital): PwC WWTS Individual - Income determination, 2025-06-24 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (·.kind.isRealEstate) then ["1100 the deferral (uppskov) on buying a replacement home is not applied; losses on real property count 50 %/70 % (not modelled)"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 30000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0
#guard p6cgReTax (p6cgReBase [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 22000
#guard p6cgReBase [{ kind := .realEstate, proceeds := 50000, cost := 150000 }] == 0

end SeGlobal.Capital
