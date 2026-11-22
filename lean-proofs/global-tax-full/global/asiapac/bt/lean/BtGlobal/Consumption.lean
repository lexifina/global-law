import BtGlobal.Pit

/-!
# Bhutan 2025: consumption taxes (P1, first pass)

First pass (R3, 2026-11-21): Sales tax (to 31 Dec 2025) (grade C); Excise and green tax (grade C). Statutes, what was tried and what would unlock each are in results/taxes/Consumption.json.
-/

namespace BtGlobal.Consumption
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := ["BT P1: consumption taxes not modelled in the first pass"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty && g.company.sales.isEmpty then [] else ["consumption taxes of Bhutan not modelled in the first pass (see results/taxes/Consumption.json)"]

#guard absent.length == 0

end BtGlobal.Consumption
