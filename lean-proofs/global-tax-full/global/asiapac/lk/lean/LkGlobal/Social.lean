import LkGlobal.Pit

/-!
# Sri Lanka: EPF and ETF are provident funds (non-tax) (2200)

EPF Act No. 15 of 1958 (employer 12 %) and ETF Act No. 46 of 1980 (employer 3 %) credit members' accounts: non-tax under OECD rules (as CPF). Grade B.
-/

namespace LkGlobal.Social
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .sscEmployer, why := "EPF (12 %) and ETF (3 %) are provident funds credited to members: non-tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 1

end LkGlobal.Social
