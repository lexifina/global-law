import VaGlobal.Pit

/-!
# VA 2025: Social family not reached (grade C)

* 2200 Employer social contributions and payroll taxes (Fondo Pensioni (Vatican employer contributions)): tried not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts); would unlock: the act's 2025 employer rates and ceilings (official consolidation or the 1.x model's parameters with quotes)
-/

namespace VaGlobal.Social
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if (g.entity == .company && g.company.payroll > 0) || g.household.adults.any (fun a => 0 < a.wages) then ["2200 Employer social contributions and payroll taxes: not modelled (grade C: not read in the P4 pass (no dated employer rates with quotes in the 1.x model or fetched texts))"] else [])


end VaGlobal.Social
