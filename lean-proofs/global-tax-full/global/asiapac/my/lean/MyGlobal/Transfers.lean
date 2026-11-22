import MyGlobal.Pit

/-!
# Malaysia: no estate duty, gift or wealth tax (4300, 4200)

Estate duty abolished for deaths from 1991-11-01 (Estate Duty (Abolition) Act 1991). Grade B.
-/

namespace MyGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "Estate duty abolished for deaths from 1991-11-01; grade B" },
   { oecd := .wealth, why := "No net wealth tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 2

end MyGlobal.Transfers
