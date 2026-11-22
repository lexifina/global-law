import PkGlobal.Pit

/-!
# Pakistan: no estate, gift or net wealth tax (4300, 4200)

Wealth tax abolished 2001 (Finance Act 2001); no estate duty since 1979. ITO s. 7E (deemed income on immovable property) is an income tax (1100). Grade B.
-/

namespace PkGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "No estate or gift tax in Pakistan (estate duty abolished 1979); grade B" },
   { oecd := .wealth, why := "Wealth Tax Act 1963 abolished 2001; ITO s. 7E deemed income is classed 1100; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 2

end PkGlobal.Transfers
