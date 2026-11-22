import HuGlobal.Pit

/-!
# HU 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Itv. 19. § (vagyonszerzési illeték 4 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Htv. építményadó (Budapest)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)


## 4400 Visszterhes vagyonátruházási illeték (ingatlan) (pass 6)
Source: Itv., net.jogtar.hu `docid=99000093.tv` (`hu/law/itv.txt`).
* 19. § (1): "ingatlan ... megszerzése esetén ingatlanonként 1 milliárd forintig 4%, a forgalmi érték ezt meghaladó része után 2%, de ingatlanonként legfeljebb 200 millió forint"

* **4100 Recurrent property tax (pass 6 note, grade C)**: Htv. építményadó (Budapest): építményadó / telekadó levied at each municipality's discretion up to the caps of the Htv.; Budapest district decrees not read (pass 6 note (PwC WWTS 2025 captures on disk))
-/

namespace HuGlobal.Property
open TaxKernel TaxKernel.Global

/-- Itv. 19. § (1) (4 % to HUF 1 billion per property, 2 % above, at most HUF 200 million) -/
def p6vagyon : TransferDuty := { name := "Visszterhes vagyonátruházási illeték (ingatlan)", sched := Schedule.ofList [(0, 400), (1000000000, 200)], kinds := [.home, .realEstate, .land] }
/-- the duty per purchase, at most 200000000 -/
def p6vagyonCap (p : Purchase) : Int := min 200000000 (p6vagyon.amount p)
def p6vagyonCharges (ps : List Purchase) : List Charge :=
  (ps.zipIdx.filter fun (p, _) => p6vagyon.kinds.contains p.kind).map fun (p, i) =>
    charge .transactions p6vagyon.name p.price (fun _ => p6vagyon.base p) (fun _ => p6vagyonCap p) (event := s!"purchase {i + 1}") (statute := "Itv. 19. § (1) (4 % to HUF 1 billion per property, 2 % above, at most HUF 200 million)")

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "4400 Visszterhes vagyonátruházási illeték (ingatlan)", covers := [.transactions],
     run := fun args g prev =>
       p6vagyonCharges g.purchases }]

def absent : List Absent :=
  []

def notes : List String := ["HU 4400 Visszterhes vagyonátruházási illeték (ingatlan): net.jogtar.hu current text (fetched 2026-11-21) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty then ["4400 the base is the market value (forgalmi érték): the price stands in; first-home and young-buyer reliefs (26. §) and the home-swap credit (21. §) not applied"] else [])

#guard p6vagyonCap { kind := .home, price := 200000 } == 8000
#guard p6vagyonCap { kind := .home, price := 2000000 } == 80000
#guard p6vagyonCap { kind := .home, price := 10000000000000 } == 200000000
#guard p6vagyonCap { kind := .vehicle, price := 100000 } == 0

end HuGlobal.Property
