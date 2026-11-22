import InGlobal.Pit

/-!
# India: no estate duty, gift tax or wealth tax (4300, 4200)

Estate duty abolished 1985 (Estate Duty (Amendment) Act 1985); Gift-tax Act 1958 not applicable to gifts from 1998-10-01 (gifts from non-relatives are income, s. 56 (2) (x)); wealth tax abolished from AY 2016-17 (Finance Act 2015). Grade B.
-/

namespace InGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "Estate duty abolished 1985; gift tax not applicable from 1998-10-01 (gifts from non-relatives taxed as income, s. 56 (2) (x)); grade B" },
   { oecd := .wealth, why := "Wealth-tax Act abolished from AY 2016-17 (Finance Act 2015); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 2

end InGlobal.Transfers
