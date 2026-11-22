import SbGlobal.Pit

/-!
# Solomon Islands 2025: provident fund contributions are non-tax (2200)

National Provident Fund Act (Cap. 109) (employer 7.5 %) credits members' individual accounts: a compulsory saving, non-tax under OECD Revenue Statistics (as CPF). No other employer social security contribution or payroll tax found (registry). Grade B.
-/

namespace SbGlobal.Social
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "National Provident Fund Act (Cap. 109) (employer 7.5 %): provident fund credited to members' accounts, non-tax (OECD); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end SbGlobal.Social
