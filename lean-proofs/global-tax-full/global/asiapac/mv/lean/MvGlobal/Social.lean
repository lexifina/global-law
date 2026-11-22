import MvGlobal.Pit

/-!
# Maldives 2025: provident fund contributions are non-tax (2200)

Pension Act (Law 8/2009, Maldives Retirement Pension Scheme) (7 % + 7 %) credits members' individual accounts: a compulsory saving, non-tax under OECD Revenue Statistics (as CPF). No other employer social security contribution or payroll tax found (registry). Grade B.
-/

namespace MvGlobal.Social
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "Pension Act (Law 8/2009, Maldives Retirement Pension Scheme) (7 % + 7 %): provident fund credited to members' accounts, non-tax (OECD); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end MvGlobal.Social
