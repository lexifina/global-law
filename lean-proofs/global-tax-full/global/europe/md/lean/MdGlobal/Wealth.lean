import MdGlobal.Pit

/-!
# MD 2025: Wealth family not reached (grade C)

* 4300 Inheritance and gift tax (none recorded (not cited)): tried not read in the P6 pass; would unlock: the act's 2025 classes, allowances and tariff (or a provision showing the tax is not levied)
* 4200 Net wealth tax (none recorded): tried not read in the P6 pass; would unlock: the act's 2025 rates and allowances (or a provision showing no wealth tax is levied)
-/

namespace MdGlobal.Wealth
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4300 Inheritance and gift tax: not modelled (grade C: not read in the P6 pass)"] else [])
  ++ (if !g.transfers.isEmpty || !g.assets.isEmpty then ["4200 Net wealth tax: not modelled (grade C: not read in the P6 pass)"] else [])


end MdGlobal.Wealth
