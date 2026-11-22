import CnmoGlobal.Pit

/-!
# Macao 2025: complementary tax on income (1200): not reached

Regulamento do Imposto Complementar de Rendimentos (Lei n.º 21/78/M) and the 2025 budget law (12 % above MOP 600,000) were not fetched (bo.io.gov.mo not tried in this pass).
-/

namespace CnmoGlobal.Corporate
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 0

end CnmoGlobal.Corporate
