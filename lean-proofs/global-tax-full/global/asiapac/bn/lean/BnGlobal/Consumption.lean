import BnGlobal.Pit

/-!
# Brunei 2025: consumption taxes (P1, first pass)

First pass (R3, 2026-11-21): VAT/GST (not levied) (grade B); Excise duties (grade C). Statutes, what was tried and what would unlock each are in results/taxes/Consumption.json.
-/

namespace BnGlobal.Consumption
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .vat, why := "no GST or VAT Act in the Laws of Brunei (AGC laws index, cmp20/world/B15-no-pit/bn/law/agc_brulaw.html)" }]

def notes : List String := ["BN P1: consumption taxes not modelled in the first pass"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty && g.company.sales.isEmpty then [] else ["consumption taxes of Brunei not modelled in the first pass (see results/taxes/Consumption.json)"]

#guard absent.length == 1

end BnGlobal.Consumption
