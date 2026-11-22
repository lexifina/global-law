import VaGlobal.Pit

/-!
# VA 2025: Consumption family not reached (grade C)

* 5111 VAT (Vatican City State: no VAT (absence not yet cited)): tried no provision found stating the absence; the 1.x model cites only pension and labour texts; would unlock: a Vatican provision or Lateran-treaty financial convention establishing the fiscal regime of goods sold in the State
* 5121 Excise duties (excise: none known (not cited)): tried not reached in the P1 pass; would unlock: the excise act's 2025 rate articles
-/

namespace VaGlobal.Consumption
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty || g.entity == .company then ["5111 VAT: not modelled (grade C: no provision found stating the absence; the 1.x model cites only pension and labour texts)"] else [])
  ++ (if !g.consumption.isEmpty || g.entity == .company then ["5121 Excise duties: not modelled (grade C: not reached in the P1 pass)"] else [])


end VaGlobal.Consumption
