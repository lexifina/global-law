import FjGlobal.Pit

/-!
# Fiji 2025: provident fund contributions are non-tax (2200)

Fiji National Provident Fund Act 2011 (18 % in all) credits members' individual accounts: a compulsory saving, non-tax under OECD Revenue Statistics (as CPF). No other employer social security contribution or payroll tax found (registry). Grade B.
-/

namespace FjGlobal.Social
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "Fiji National Provident Fund Act 2011 (18 % in all): provident fund credited to members' accounts, non-tax (OECD); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end FjGlobal.Social
