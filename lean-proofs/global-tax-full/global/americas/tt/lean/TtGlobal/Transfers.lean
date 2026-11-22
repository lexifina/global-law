import TtGlobal.Pit

/-!
# TT 2025: Transfers family — no dated statute text reached (grade C)

* Transfer, stamp and recurrent property taxes (Stamp Duty Act Chap. 76:01; Property Tax Act): tried not read in this pass (texts not local); would unlock: the acts and the 2025 municipal rates.
-/

namespace TtGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon TtGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Transfer, stamp and recurrent property taxes: statute not reached in a dated form (grade C): not computed"


end TtGlobal.Transfers
