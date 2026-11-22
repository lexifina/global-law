import VaGlobal.Pit

/-!
# VA 2025: Corporate family not reached (grade C)

* 1200 Corporate income tax (Vatican City State: no corporate income tax (absence not yet cited)): tried no provision found stating the absence; would unlock: a provision establishing the State's fiscal regime
* 1200 Withholding on payments abroad (statutory withholding on dividends, interest, royalties): tried no provision found stating the absence; would unlock: a provision establishing the State's fiscal regime


## 1200 withholding still grade C (pass 9)
* no Vatican text on taxation was found on official sites in pass 9
* would unlock: an official Vatican City State text stating that no income or withholding tax is levied
-/

namespace VaGlobal.Corporate
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["1200 Corporate income tax: not modelled (grade C: no provision found stating the absence)"] else [])
  ++ (if g.entity == .company then ["1200 Withholding on payments abroad: not modelled (grade C: no provision found stating the absence)"] else [])


end VaGlobal.Corporate
