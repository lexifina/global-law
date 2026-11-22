import CnmoGlobal.Pit

/-!
# Macao SAR 2025: consumption taxes (P1, first pass)

First pass (R3, 2026-11-21): VAT/GST/sales tax (not levied) (grade B); Imposto de consumo (tobacco, alcohol above 30 %) (grade C). Statutes, what was tried and what would unlock each are in results/taxes/Consumption.json.
-/

namespace CnmoGlobal.Consumption
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .vat, why := "no VAT or general sales tax in Macao; the Regulamento do Imposto de Consumo taxes tobacco and alcohol only" }]

def notes : List String := ["CN-MO P1: consumption taxes not modelled in the first pass"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty && g.company.sales.isEmpty then [] else ["consumption taxes of Macao SAR not modelled in the first pass (see results/taxes/Consumption.json)"]

#guard absent.length == 1

end CnmoGlobal.Consumption
