import XkGlobal.Pit

/-!
# XK 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Ligji për tatimin në pronë (no transfer tax)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (Ligji për tatimin në pronë (Prishtinë)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: Ligji për tatimin në pronë (Prishtinë): property tax set by each municipality; Prishtina rate not read (pass 6 note (PwC WWTS 2025 captures on disk))

* **4400 Real-estate transfer and stamp duties (pass 6 note, grade C)**: Ligji për tatimin në pronë (no transfer tax): property transaction fee at municipal level, EUR 150 per unit (100 m2 of building, 1 ha of land): area inputs are not in the model (pass 6 note (PwC WWTS 2025 captures on disk))
-/

namespace XkGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])


end XkGlobal.Property
