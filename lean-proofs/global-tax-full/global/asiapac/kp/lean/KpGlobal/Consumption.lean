import KpGlobal.Pit

/-!
# North Korea (DPRK) 2025: consumption taxes (P1, first pass)

First pass (R3, 2026-11-21): Taxes on goods and services (not levied) (grade B); Excises (not levied) (grade B). Statutes, what was tried and what would unlock each are in results/taxes/Consumption.json.
-/

namespace KpGlobal.Consumption
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .vat, why := "taxes abolished from 1 April 1974 (Supreme People Assembly decision of 21 March 1974 on the complete abolition of taxes)" },
   { oecd := .excise, why := "no taxes on goods are levied (1974 abolition)" },
   { oecd := .salesTax, why := "no taxes on goods are levied (1974 abolition)" }]

def notes : List String := ["KP P1: consumption taxes not modelled in the first pass"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty && g.company.sales.isEmpty then [] else ["consumption taxes of North Korea (DPRK) not modelled in the first pass (see results/taxes/Consumption.json)"]

#guard absent.length == 3

end KpGlobal.Consumption
