import CnhkGlobal.Pit

/-!
# Hong Kong: no estate duty, gift or wealth tax (4300, 4200)

Estate duty abolished for deaths from 2006-02-11 (Revenue (Abolition of Estate Duty) Ordinance 2005, No. 21 of 2005); no gift or wealth tax. MPF contributions are paid to private trustees (non-tax, OECD). Grade B.
-/

namespace CnhkGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "Estate duty abolished from 2006-02-11 (Ordinance No. 21 of 2005); no gift tax; grade B" },
   { oecd := .wealth, why := "No net wealth tax; grade B" },
   { oecd := .sscEmployer, why := "MPF contributions (Cap. 485, 5 %) go to private trustees: non-tax under OECD rules; grade B" },
   { oecd := .payroll, why := "No payroll tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 4

end CnhkGlobal.Transfers
