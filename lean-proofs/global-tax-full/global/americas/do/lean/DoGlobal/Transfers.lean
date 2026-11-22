import DoGlobal.Pit

/-!
# DO 2025: Transfers family — no dated statute text reached (grade C)

* Transfer, stamp and recurrent property taxes (Ley 288-04 (transferencia 3 %); IPI (Ley 18-88)): tried not read in this pass (texts not local); would unlock: the acts and the 2025 municipal rates.
-/

namespace DoGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon DoGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Transfer, stamp and recurrent property taxes: statute not reached in a dated form (grade C): not computed"


end DoGlobal.Transfers
