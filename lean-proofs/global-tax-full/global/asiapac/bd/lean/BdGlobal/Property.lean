import BdGlobal.Pit

/-!
# Bangladesh 2025: stamp duty on conveyances (4400); holding tax not reached
(B.) Stamp Act 1899 (Bangladesh) Schedule I art. 23: conveyance 1.5 % of the value. Registration fee (1 %) and the ITA s. 125
advance tax by location not modelled; holding tax (City Corporation Act 2009): C.
-/

namespace BdGlobal.Property
open TaxKernel TaxKernel.Global

def duty0 : TransferDuty :=
  { name := "Stamp duty on conveyances (1.5 %)", sched := Schedule.flat 150, kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "Stamp Act 1899 Sch. I art. 23 (Bangladesh)" (level := .central) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard duty0.amount { kind := .land, price := 1000000 } == 15000

end BdGlobal.Property
