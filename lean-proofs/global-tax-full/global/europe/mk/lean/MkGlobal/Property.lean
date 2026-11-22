import MkGlobal.Pit

/-!
# MK 2025: Property family not reached (grade C)

* 4400 Real-estate transfer and stamp duties (Закон за даноците на имот (данок на промет 2-4 %)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)
* 4100 Recurrent property tax (данок на имот (Скопје)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)

* **4100 Recurrent property tax (pass 6 note, grade C)**: данок на имот (Скопје): данок на имот: 0,10-0,20 % of market value as each municipality sets; Skopje decision not read (pass 6 note (PwC WWTS 2025 captures on disk))

* **4400 Real-estate transfer and stamp duties (pass 6 note, grade C)**: Закон за даноците на имот (данок на промет 2-4 %): данок на промет на недвижности: 2-4 % set by each municipal council, paid by the seller; Skopje decision not read (pass 6 note (PwC WWTS 2025 captures on disk))
-/

namespace MkGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)"] else [])
  ++ (if !g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate) then ["4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)"] else [])


end MkGlobal.Property
