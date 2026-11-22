import LkGlobal.Pit

/-!
# Sri Lanka 2025: property taxes not reached (4100, 4400)

Local authority rates and the provincial stamp duty on transfers (Western Province ~4 %): rates not reached (C).
-/

namespace LkGlobal.Property
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 0

end LkGlobal.Property
