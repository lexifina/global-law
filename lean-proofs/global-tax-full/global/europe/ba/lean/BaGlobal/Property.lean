import BaGlobal.Pit

/-!
# BA 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Zakon o porezu na promet nekretnina (kantonalni)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (porez na imovinu (kantonalni)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: porez na imovinu (kantonalni): property tax set by each FBiH canton (per m2 or value); Sarajevo Canton law not read (RS: 0,20 %, BD: 0,05-1 %) (pass 6 note (PwC WWTS 2025 captures on disk))

* **4400 Real-estate transfer and stamp duties (pass 6 note, grade C)**: Zakon o porezu na promet nekretnina (kantonalni): FBiH transfer tax set by each canton, at most 5 %; Sarajevo Canton law not read (none in RS and BD) (pass 6 note (PwC WWTS 2025 captures on disk))
-/

namespace BaGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])


end BaGlobal.Property
