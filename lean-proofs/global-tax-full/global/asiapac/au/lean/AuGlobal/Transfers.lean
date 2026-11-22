import AuGlobal.Pit

/-!
# Australia: no estate, gift or wealth tax (4300, 4200)

Federal estate and gift duty abolished for deaths from 1979-07-01 (Estate Duty Assessment Amendment Act 1978); states abolished theirs by 1982. Grade B.
-/

namespace AuGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "Estate and gift duty abolished (federal 1979, states by 1982); grade B" },
   { oecd := .wealth, why := "No net wealth tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 2

end AuGlobal.Transfers
