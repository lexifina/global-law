import KiGlobal.Pit

/-!
# Kiribati 2025: corporate tax (1200): not reached

Income Tax Act 1990 (PacLII ki_ita116): text on the build server not read for rates in this pass.
-/

namespace KiGlobal.Corporate
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["session 11 year-in-force audit: Income Tax Act 1990 as enacted with amending Acts to 2009 checked; nothing later, and no 2025 version or official 2025 source reached: grade C"] else [])

#guard absent.length == 0

end KiGlobal.Corporate
