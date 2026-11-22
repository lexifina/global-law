import GyGlobal.Pit

/-!
# GY 2025: Transfers family — no dated statute text reached (grade C)

* Transfer, stamp and recurrent property taxes (Stamp Duty Act; Property Tax Act (net property)): tried not read in this pass (texts not local); would unlock: the acts and the 2025 municipal rates.
-/

namespace GyGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon GyGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Transfer, stamp and recurrent property taxes: statute not reached in a dated form (grade C): not computed"


end GyGlobal.Transfers
