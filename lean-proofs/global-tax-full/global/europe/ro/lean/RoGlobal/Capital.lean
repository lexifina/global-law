import RoGlobal.Pit

/-!
# RO 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (Codul fiscal art. 94-97 (câștiguri din transferul titlurilor de valoare), art. 111): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Impozit pe câștigul din transferul titlurilor de valoare (pass 6)
Source: PwC Worldwide Tax Summaries, Romania, Individual - Income determination, accessed 2025-05-31 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* shares: net gain (price - acquisition price - broker fees) 10 %
-/

namespace RoGlobal.Capital
open TaxKernel TaxKernel.Global

/-- Codul fiscal art. 94-96 (10 % for 2025) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 1000).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Impozit pe câștigul din transferul titlurilor de valoare (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "Codul fiscal art. 94-96 (10 % for 2025)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Impozit pe câștigul din transferul titlurilor de valoare", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["RO 1100 Impozit pe câștigul din transferul titlurilor de valoare: PwC WWTS Individual - Income determination, 2025-05-31 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (·.kind.isRealEstate) then ["1100 the tax on real estate transfers (1 %/3 % of value, Codul fiscal art. 111) is not modelled"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 10000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0

end RoGlobal.Capital
