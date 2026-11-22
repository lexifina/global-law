import IrGlobal.Pit

/-!
# Iran 2025: consumption taxes (P1, first pass)

First pass (R3, 2026-11-21): Value added tax (10 % in 1404) (grade C); Taxes on cigarettes, fuel and soft drinks under the VAT Law (grade C). Statutes, what was tried and what would unlock each are in results/taxes/Consumption.json.
-/

namespace IrGlobal.Consumption
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := ["IR P1: consumption taxes not modelled in the first pass"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty && g.company.sales.isEmpty then [] else ["consumption taxes of Iran not modelled in the first pass (see results/taxes/Consumption.json)"]

#guard absent.length == 0

end IrGlobal.Consumption
