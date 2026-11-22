import NoGlobal.Pit

/-!
# NO 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (Skatteloven § 5-1, 9-2 (22 %, oppjustert aksjeinntekt)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Gevinst på aksjer (oppjustert 1,72 x 22 %) (pass 6)
Source: PwC Worldwide Tax Summaries, Norway, Individual - Income determination, accessed 2025-08-03 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* shares: gain x 1,72 x 22 % = 37,84 % effective; ordinary capital income 22 %
-/

namespace NoGlobal.Capital
open TaxKernel TaxKernel.Global

/-- Skatteloven § 10-31 (oppjusteringsfaktor 1,72) and § 15-1 (22 %): 37,84 % on gains on shares -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 3784).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Gevinst på aksjer (oppjustert 1,72 x 22 %) (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "Skatteloven § 10-31 (oppjusteringsfaktor 1,72) and § 15-1 (22 %): 37,84 % on gains on shares")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Gevinst på aksjer (oppjustert 1,72 x 22 %)", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["NO 1100 Gevinst på aksjer (oppjustert 1,72 x 22 %): PwC WWTS Individual - Income determination, 2025-08-03 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (·.kind.isRealEstate) then ["1100 gains on real property (22 %, home exempt after one year of ownership and use) not modelled: the conditions are not in the B source"] else [])
  ++ (if g.disposals.any (·.kind == .bonds) then ["1100 bonds are ordinary capital income at 22 %, taken here at the share rate"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 37840
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0

end NoGlobal.Capital
