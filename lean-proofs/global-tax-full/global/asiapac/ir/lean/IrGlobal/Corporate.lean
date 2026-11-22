import IrGlobal.Pit

/-!
# Iran 2025 (1404): corporate income tax: not reached

Direct Taxes Act art. 105 (25 %) and the withholding articles: no official text reached from the build server (rc.majlis.ir / the 1.x rescue folders).
-/

namespace IrGlobal.Corporate
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 0

end IrGlobal.Corporate
