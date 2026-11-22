import NzGlobal.Pit

/-!
# New Zealand: no estate duty, gift duty, wealth tax, stamp duty, payroll tax or social security contributions

Estate duty abolished 1992; gift duty abolished from 2011-10-01 (Taxation (Tax Administration and Remedial Matters) Act 2011); stamp duty on land abolished 1999 (Stamp and Cheque Duties Act 1971 Part 1 repealed). ACC levies are recorded by the OECD as non-tax compulsory payments; KiwiSaver employer contributions go to private schemes. Council rates (Local Government (Rating) Act 2002): C. Grade B.
-/

namespace NzGlobal.Transfers
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  [{ oecd := .estate, why := "Estate duty abolished 1992, gift duty from 2011-10-01; grade B" },
   { oecd := .wealth, why := "No net wealth tax; grade B" },
   { oecd := .transactions, why := "Stamp duty on land abolished 1999; no securities transaction tax; grade B" },
   { oecd := .sscEmployer, why := "No social security contributions; ACC levies are non-tax compulsory payments in OECD Revenue Statistics; grade B" },
   { oecd := .payroll, why := "No payroll tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 5

end NzGlobal.Transfers
