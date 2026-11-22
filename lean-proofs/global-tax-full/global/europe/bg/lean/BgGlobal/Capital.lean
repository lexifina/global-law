import BgGlobal.Pit

/-!
# BG 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (ЗДДФЛ чл. 13, 33): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Данък върху капиталовите печалби (pass 6)
Source: PwC Worldwide Tax Summaries, Bulgaria, Individual - Income determination, accessed 2025-05-31 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* capital gains (residents): 10 %, annual
-/

namespace BgGlobal.Capital
open TaxKernel TaxKernel.Global

/-- ЗДДФЛ чл. 33, 48 (10 %) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 1000).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Данък върху капиталовите печалби (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "ЗДДФЛ чл. 33, 48 (10 %)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Данък върху капиталовите печалби", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["BG 1100 Данък върху капиталовите печалби: PwC WWTS Individual - Income determination, 2025-05-31 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (·.kind.isRealEstate) then ["1100 real estate gains (exemptions for one home and two other properties held five years) not modelled"] else [])
  ++ (if g.disposals.any (·.listed) then ["1100 gains on shares traded on EU/EEA regulated markets are exempt (not applied)"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 10000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0

end BgGlobal.Capital
