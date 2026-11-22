import IdGlobal.Pit

/-!
# Indonesia 2025: no inheritance, gift or wealth tax (4300, 4200)

Inheritances are excluded from income (UU PPh Pasal 4 (3) b); gifts between first-degree relatives likewise (Pasal 4 (3) a 2). No net wealth tax. Grade B.
-/

namespace IdGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "No inheritance or gift tax: UU PPh Pasal 4 (3) a-b excludes them from income; grade B" },
   { oecd := .wealth, why := "No net wealth tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 2

end IdGlobal.Transfers
