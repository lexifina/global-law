import NrGlobal.Pit

/-!
# Nauru 2025: provident fund contributions are non-tax (2200)

Nauru Superannuation Act 2018 (employer share) credits members' individual accounts: a compulsory saving, non-tax under OECD Revenue Statistics (as CPF). No other employer social security contribution or payroll tax found (registry). Grade B.
-/

namespace NrGlobal.Social
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "Nauru Superannuation Act 2018 (employer share): provident fund credited to members' accounts, non-tax (OECD); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end NrGlobal.Social
