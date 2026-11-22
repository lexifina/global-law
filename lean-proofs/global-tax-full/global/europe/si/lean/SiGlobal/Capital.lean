import SiGlobal.Pit

/-!
# SI 2025: Capital family not reached (grade C)

* 1100 Gains of individuals on shares and property (disposals) (ZDoh-2 96-97. člen): tried the gains provisions were not read in the P3 pass (the 1.x model may tax the household's own `capitalGains`; the extra disposals are not routed); would unlock: the act's gains articles as in force 2025 (holding periods, main-home exemption, rate or routing into the 1.x model)


## 1100 Dohodnina od dobička iz kapitala (pass 6)
Source: PwC Worldwide Tax Summaries, Slovenia, Individual - Income determination, accessed 2025-07-11 (Wayback capture; `law/pwc_indincome_wb2025.txt`).
* final tax by holding period: 0-5 years 25 %; 5-10 20 %; 10-15 15 %; > 15 years 0 %
-/

namespace SiGlobal.Capital
open TaxKernel TaxKernel.Global

/-- ZDoh-2 97. člen (25 % to 5 years, 20 %, 15 %, 0 % after 15 years) -/
def p6cgSecSel (d : Disposal) : Bool := (d.kind.isShares || d.kind == .bonds) && d.heldMonths < 180
def p6cgSecBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgSecSel).map (·.gain)))) BP
def p6cgSecRate (m : Nat) : Int := if m < 60 then 2500 else if m < 120 then 2000 else if m < 180 then 1500 else 0
def p6cgSecTaxD (ds : List Disposal) : Int :=
  let t := isum ((ds.filter p6cgSecSel).map fun d => p6cgSecRate d.heldMonths * d.gain)
  if t > 0 then divR .down t BP else 0
def p6cgReSel (d : Disposal) : Bool := d.kind.isRealEstate && d.heldMonths < 180
def p6cgReBase (ds : List Disposal) : Int := divR .down (10000 * pos (isum ((ds.filter p6cgReSel).map (·.gain)))) BP
def p6cgReRate (m : Nat) : Int := if m < 60 then 2500 else if m < 120 then 2000 else if m < 180 then 1500 else 0
def p6cgReTaxD (ds : List Disposal) : Int :=
  let t := isum ((ds.filter p6cgReSel).map fun d => p6cgReRate d.heldMonths * d.gain)
  if t > 0 then divR .down t BP else 0
def p6cgCharges (g : CanonGlobal) : List Charge :=
  if g.disposals.isEmpty then [] else
  [charge .pit "Dohodnina od dobička iz kapitala (securities)" (isum ((g.disposals.filter p6cgSecSel).map (·.gain))) (fun _ => p6cgSecBase g.disposals) (fun _ => p6cgSecTaxD g.disposals) (event := "disposals 2025") (statute := "ZDoh-2 97. člen (25 % to 5 years, 20 %, 15 %, 0 % after 15 years)"),  charge .pit "Dohodnina od dobička iz kapitala (real estate)" (isum ((g.disposals.filter p6cgReSel).map (·.gain))) (fun _ => p6cgReBase g.disposals) (fun _ => p6cgReTaxD g.disposals) (event := "disposals 2025") (statute := "ZDoh-2 97. člen (25 % to 5 years, 20 %, 15 %, 0 % after 15 years)")]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1100 Dohodnina od dobička iz kapitala", covers := [],
     run := fun args g prev =>
       p6cgCharges g }]

def absent : List Absent :=
  []

def notes : List String := ["SI 1100 Dohodnina od dobička iz kapitala: PwC WWTS Individual - Income determination, 2025-07-11 (Wayback capture) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.any (fun d => d.heldMonths >= 60 && d.heldMonths < 180) then ["1100 pass 7: each disposal is taxed at its holding-period rate (25/20/15 %) and losses offset at their own rates; the act's loss rules (ZDoh-2 98. člen) were not read"] else [])
  ++ (if g.disposals.any (fun d => !(d.kind.isShares || d.kind == .bonds || d.kind.isRealEstate)) then ["1100 gains on other assets (business, vehicles, other) not modelled"] else [])

#guard p6cgSecTaxD [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }] == 25000
#guard p6cgSecTaxD [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 72 }] == 20000
#guard p6cgSecTaxD [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 150 }] == 15000
#guard p6cgSecTaxD [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 12 }, { kind := .listedShares, proceeds := 50000, cost := 100000, heldMonths := 72 }] == 15000
#guard p6cgSecBase [{ kind := .listedShares, proceeds := 150000, cost := 50000, heldMonths := 180 }] == 0
#guard p6cgReTaxD [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 12 }] == 25000
#guard p6cgReTaxD [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 72 }] == 20000
#guard p6cgReTaxD [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 150 }] == 15000
#guard p6cgReTaxD [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 12 }, { kind := .realEstate, proceeds := 50000, cost := 100000, heldMonths := 72 }] == 15000
#guard p6cgReBase [{ kind := .realEstate, proceeds := 150000, cost := 50000, heldMonths := 180 }] == 0

end SiGlobal.Capital
