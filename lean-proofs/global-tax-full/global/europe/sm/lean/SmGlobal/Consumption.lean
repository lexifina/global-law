import SmGlobal.Pit

/-!
# SM 2025: Consumption family not reached (grade C)

* 5111 VAT (Imposta generale sulle importazioni / imposta monofase (Legge 22 dicembre 1972 n. 40 and later)): tried consigliograndeegenerale.sm not fetched; Global law (the 1.x source) not used (coordinator, 2026-11-21); would unlock: the San Marino import tax law in force 2025
* 5121 Excise duties (imposte speciali di consumo): tried not reached in the P1 pass; would unlock: the excise act's 2025 rate articles


## 5111 VAT still grade C (pass 9)
* San Marino has no VAT: imports bear the single-stage imposta monofase; its act was not fetched
* would unlock: the imposta monofase law and its rate decrees
-/

namespace SmGlobal.Consumption
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty || g.entity == .company then ["5111 VAT: not modelled (grade C: consigliograndeegenerale.sm not fetched; Global law (the 1.x source) not used (coordinator, 2026-11-21))"] else [])
  ++ (if !g.consumption.isEmpty || g.entity == .company then ["5121 Excise duties: not modelled (grade C: not reached in the P1 pass)"] else [])


end SmGlobal.Consumption
