import CnGlobal.Pit

/-!
# China 2025: no inheritance, gift or net wealth tax (4300, 4200)

No such law in force (flk.npc.gov.cn: no 遗产税 law; registry: not levied). Grade B.
-/

namespace CnGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "No inheritance or gift tax in China (no law in the national database); grade B" },
   { oecd := .wealth, why := "No net wealth tax in China; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 2

end CnGlobal.Transfers
