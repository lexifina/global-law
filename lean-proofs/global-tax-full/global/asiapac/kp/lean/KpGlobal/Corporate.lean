import KpGlobal.Pit

/-!
# DPRK 2025: tax on foreign-invested businesses (1200): not reached

The DPRK levies no tax on its citizens; the Law on Taxation of Foreign-invested Businesses and Foreign Individuals (1993, amended) charges enterprise income tax (25 %, Rason 14 %) on foreign-invested businesses only. No official text reached.
-/

namespace KpGlobal.Corporate
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 0

end KpGlobal.Corporate
