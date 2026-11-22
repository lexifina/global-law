import HuGlobal.Pit

/-!
# HU 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (Szja tv. 67. § (árfolyamnyereség), 62. § (ingatlan)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Árfolyamnyereség adója (pass 6)
Source: PwC Worldwide Tax Summaries, Hungary, Individual - Income determination, accessed 2025-06-03 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* capital gains 15 %; social contribution tax 13 % may apply (conditions)
-/

namespace HuGlobal.Capital
open TaxKernel TaxKernel.Global

/-- Szja tv. 67. § (15 %) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 1500).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Árfolyamnyereség adója (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "Szja tv. 67. § (15 %)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Árfolyamnyereség adója", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["HU 1100 Árfolyamnyereség adója: PwC WWTS Individual - Income determination, 2025-06-03 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.disposals.isEmpty then ["1100 the 13 % social contribution tax (szocho) where the conditions fail is not applied"] else [])
  ++ (if g.disposals.any (·.kind.isRealEstate) then ["1100 real estate gains (15 %, reduced by holding years) not modelled: the reductions are not in the B source"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 15000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0

end HuGlobal.Capital
