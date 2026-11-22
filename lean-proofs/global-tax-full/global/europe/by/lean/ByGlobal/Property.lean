import ByGlobal.Pit

/-!
# BY 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (государственная пошлина (no real-estate transfer tax as such)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (НК РБ гл. 25 налог на недвижимость): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)
-/

namespace ByGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])


end ByGlobal.Property
