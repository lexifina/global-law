import PtGlobal.Pit

/-!
# PT 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (CIRS art. 10, 43, 72 (28 %)): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Mais-valias mobiliárias (taxa especial) (pass 6)
Source: PwC Worldwide Tax Summaries, Portugal, Individual - Income determination, accessed 2025-06-03 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* securities: 28 % (50 % of the gain for unlisted micro / small company shares)
* from 2023: net gain on securities held < 365 days aggregated where taxable income ≥ EUR 83 696
-/

namespace PtGlobal.Capital
open TaxKernel TaxKernel.Global

/-- CIRS art. 72.º (28 %) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds)
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecTax (b : Int) : Int := (Schedule.flat 2800).tax {} b
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Mais-valias mobiliárias (taxa especial) (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTax (p6cgSecBase g.disposals)) (event := "disposals 2025") (statute := "CIRS art. 72.º (28 %)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Mais-valias mobiliárias (taxa especial)", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["PT 1100 Mais-valias mobiliárias (taxa especial): PwC WWTS Individual - Income determination, 2025-06-03 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (·.kind.isRealEstate) then ["1100 real estate gains (50 % added to income at progressive rates; reinvestment relief for the home) not modelled"] else [])
  ++ (if g.disposals.any (fun d => d.heldMonths < 12) then ["1100 short-term gains of high earners are aggregated at progressive rates (not modelled)"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTax (p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }]) == 28000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 50000, cost := 150000 }] == 0

end PtGlobal.Capital
