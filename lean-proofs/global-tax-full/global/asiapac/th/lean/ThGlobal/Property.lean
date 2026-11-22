import ThGlobal.Pit

/-!
# Thailand 2025: land and building tax; transfer stamp duty and specific business tax (4100, 4400)
(B.) Land and Building Tax Act B.E. 2562 + Royal Decree rates: residential other than the main home 0.02 % to 50 m, 0.03 % to
75 m, 0.05 % to 100 m, 0.1 % above (homes modelled with this scale); commercial 0.3 % to 50 m, 0.4 % to 200 m, 0.5 % to 1 bn,
0.6 % to 5 bn, 0.7 % above. Seller side (`sellerF`): Revenue Code Ch. 5 specific business tax 3.3 % (3 % + local 10 %) of the
proceeds when sold within 5 years, else Ch. 6 stamp duty 0.5 %.
-/

namespace ThGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "Land and building tax (residential)", sched := (Schedule.ofList [(0, 2), (50000000, 3), (75000000, 5), (100000000, 10)]), ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.home] }

def prop1 : PropertyTax :=
  { name := "Land and building tax (commercial)", sched := (Schedule.ofList [(0, 30), (50000000, 40), (200000000, 50), (1000000000, 60), (5000000000, 70)]), ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.realEstate] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "Land and Building Tax Act B.E. 2562 s. 37; Royal Decree (rates)" (level := .local)
      ++ prop1.charges g.assets "Land and Building Tax Act B.E. 2562 s. 37; Royal Decree (rates)" (level := .local) }

def sellerF : Family :=
  { name := "4400 SBT / stamp duty on property sales", covers := [.transactions],
    run := fun _ g _ => (g.disposals.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
      if d.heldMonths < 60 then charge .transactions "Specific business tax (3.3 %)" d.proceeds pos (fun b => divR .down (330 * b) BP) (event := s!"disposal {i + 1}") (statute := "Revenue Code s. 91/2 (6), 91/6")
      else charge .transactions "Stamp duty on transfer (0.5 %)" d.proceeds pos (fun b => divR .down (50 * b) BP) (event := s!"disposal {i + 1}") (statute := "Revenue Code Ch. 6, Schedule item 1") }

def families : List Family := [fam0, sellerF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .home) then ["main-home exemption to 50 m baht and the 2% Land Code transfer fee not modelled"] else [])

#guard prop0.amount { kind := .home, value := 60000000 } == 10000 + 3000

end ThGlobal.Property
