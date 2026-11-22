import GtGlobal.Pit

/-!
# GT 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (Decreto 431 (herencias, legados y donaciones)): tried not read in this pass; would unlock: the act's 2025 text.
-/

namespace GtGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon GtGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end GtGlobal.Property
