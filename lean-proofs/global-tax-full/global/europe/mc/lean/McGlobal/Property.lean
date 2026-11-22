import McGlobal.Pit

/-!
# MC 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (droits d'enregistrement (Ordonnance 1919/1970 tariffs, 4,5 %-7,5 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (no recurrent property tax: absence not yet cited): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)
-/

namespace McGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])


end McGlobal.Property
