import GrGlobal.Pit

/-!
# GR 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (ΚΦΕ ν. 4172/2013 άρθρο 42): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Φόρος υπεραξίας από μεταβίβαση μετοχών (pass 6)
Source: PwC Worldwide Tax Summaries, Greece, Individual - Income determination, accessed 2025-07-22 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* unlisted shares 15 %; listed shares 15 % for holdings ≥ 0,5 % (else exempt, conditions)
* listed-share sales duty 0,2 % of gross proceeds (4400, not modelled)
-/

namespace GrGlobal.Capital
open TaxKernel TaxKernel.Global

/-- ΚΦΕ (ν. 4172/2013) άρθρο 42 (15 %) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 1500).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Φόρος υπεραξίας από μεταβίβαση μετοχών (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "ΚΦΕ (ν. 4172/2013) άρθρο 42 (15 %)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Φόρος υπεραξίας από μεταβίβαση μετοχών", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["GR 1100 Φόρος υπεραξίας από μεταβίβαση μετοχών: PwC WWTS Individual - Income determination, 2025-07-22 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.listed && d.stakeBp < 50) then ["1100 listed shares below a 0,5 % holding are taken as taxed (the exemption's conditions are not modelled)"] else [])
  ++ (if g.disposals.any (·.kind.isRealEstate) then ["1100 real estate gains (tax suspended) not modelled"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 15000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0

end GrGlobal.Capital
