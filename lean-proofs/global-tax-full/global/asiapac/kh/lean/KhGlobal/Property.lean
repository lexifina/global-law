import KhGlobal.Pit

/-!
# Cambodia 2025: tax on immovable property and registration tax on transfers (4100, 4400)
(B: Khmer OCR not searched for these articles.) Law on Financial Management 2010: tax on immovable property 0.1 % of the value
above 100 m riel. Law on Taxation 2023: registration tax 4 % on transfers of immovable property.
-/

namespace KhGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "Tax on immovable property (0.1 %)", sched := Schedule.flat 10, ratioNum := 1, ratioDen := 1, exempt := 100000000, kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "Law on Financial Management 2010 (tax on immovable property)" (level := .local) }

def duty0 : TransferDuty :=
  { name := "Registration tax (4 %)", sched := Schedule.flat 400, kinds := [.home, .realEstate, .land] }

def fam1 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "Law on Taxation 2023 (registration tax)" (level := .central) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard prop0.amount { kind := .home, value := 300000000 } == 200000
#guard duty0.amount { kind := .home, price := 1000000 } == 40000

end KhGlobal.Property
