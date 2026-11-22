import VnGlobal.Pit

/-!
# Viet Nam 2025: non-agricultural land use tax and the registration fee (4100, 4400)
(B.) Luật thuế SDĐPNN 48/2010 art. 7: 0.03 % of the land value within the quota (0.07 %, 0.15 % above); Nghị định 10/2022/ND-CP
art. 8: registration fee on houses and land 0.5 % of the value.
-/

namespace VnGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "Thuế sử dụng đất phi nông nghiệp (0.03 %)", sched := Schedule.flat 3, ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.land, .home] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "Luật 48/2010/QH12 art. 7" (level := .local) }

def duty0 : TransferDuty :=
  { name := "Lệ phí trước bạ (0.5 %)", sched := Schedule.flat 50, higherOfAssessed := true, kinds := [.home, .realEstate, .land] }

def fam1 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "Nghị định 10/2022/ND-CP art. 8" (level := .central) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard duty0.amount { kind := .home, price := 1000000000 } == 5000000

end VnGlobal.Property
