import HtGlobal.Pit

/-!
# HT 2025: Transfers family — no dated statute text reached (grade C)

* Transfer, stamp and recurrent property taxes (CFPB; droits d'enregistrement): tried not read in this pass (texts not local); would unlock: the acts and the 2025 municipal rates.
-/

namespace HtGlobal.Transfers
open TaxKernel TaxKernel.Global AmerCommon HtGlobal

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "Transfer, stamp and recurrent property taxes: statute not reached in a dated form (grade C): not computed"


end HtGlobal.Transfers
