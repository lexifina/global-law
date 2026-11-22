import SgGlobal.Pit

/-!
# Singapore: no estate duty, capital gains or wealth tax (4300, 4200, 1100 gains)

Estate duty abolished for deaths from 2008-02-15 (Estate Duty (Abolition) Act 2008); no gift or wealth tax; no capital gains tax and dividends (one-tier, ITA s. 13 (1) (za)) and bank interest (s. 13 (1) (zh)) of individuals exempt. Grade B.
-/

namespace SgGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "Estate duty abolished for deaths from 2008-02-15 (Estate Duty (Abolition) Act 2008); grade B" },
   { oecd := .wealth, why := "No net wealth tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 2

end SgGlobal.Transfers
