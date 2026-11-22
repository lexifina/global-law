import EcGlobal.Pit

/-!
# EC 2025: Property family — no dated statute text reached (grade C)

* Inheritance, gift and wealth taxes (LRTI (herencias, legados y donaciones: impuesto a la renta)): tried not read in this pass; would unlock: the act's 2025 text.
-/

namespace EcGlobal.Property
open TaxKernel TaxKernel.Global AmerCommon EcGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Inheritance, gift and wealth taxes: statute not reached in a dated form (grade C): not computed"


end EcGlobal.Property
