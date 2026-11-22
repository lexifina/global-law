import PhGlobal.Pit

/-!
# Philippines 2025 (Metro Manila): real property tax, documentary stamp tax, local transfer tax (4100, 4400)
(B.) RA 7160 s. 233-235: Metro Manila cities 2 % + Special Education Fund 1 % of the assessed value; s. 218: assessment level
for residential land/buildings 20 % of market value (modelled: 3 % × 20 %). NIRC s. 196: DST on conveyances 1.5 %; RA 7160
s. 135: transfer tax in Metro Manila 0.75 %.
-/

namespace PhGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "Real property tax + SEF (3 % of 20 % assessed)", sched := Schedule.flat 300, ratioNum := 20, ratioDen := 100, exempt := 0, kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "RA 7160 ss. 218, 233, 235" (level := .local) }

def duty0 : TransferDuty :=
  { name := "Documentary stamp tax on conveyances (1.5 %)", sched := Schedule.flat 150, kinds := [.home, .realEstate, .land] }

def duty1 : TransferDuty :=
  { name := "Local transfer tax (Metro Manila 0.75 %)", sched := Schedule.flat 75, kinds := [.home, .realEstate, .land] }

def fam1 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "NIRC s. 196" (level := .central)
      ++ duty1.charges g.purchases "RA 7160 s. 135" (level := .local) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard prop0.amount { kind := .home, value := 5000000 } == 30000
#guard duty0.amount { kind := .home, price := 1000000 } == 15000

end PhGlobal.Property
