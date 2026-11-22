import BdGlobal.Pit

/-!
# Bangladesh: net wealth surcharge (4200) not modelled; no estate tax

Finance Ordinance 2025: surcharge on income tax for net wealth above Tk 4 crore (10-35 %): depends on the income tax and the declared net wealth (C). Gift Tax Act 1990: status in 2025 not confirmed (C). No estate duty. No social security contributions (registry).
-/

namespace BdGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "No social security contributions in Bangladesh (registry: not levied); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end BdGlobal.Transfers
