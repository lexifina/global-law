import KnGlobal.Pit

/-!
# KN 2025: Transfers family — no dated statute text reached (grade C)

* Transfer, stamp and recurrent property taxes (Stamp Act; Property Tax Act): tried not read in this pass (texts not local); would unlock: the acts and the 2025 municipal rates.
-/

namespace KnGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon KnGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Transfer, stamp and recurrent property taxes: statute not reached in a dated form (grade C): not computed"


end KnGlobal.Transfers
