import R4Common

/-! # MG 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace MgGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "MG CGI (LFI 2025, complete code): no tax on net wealth; 'fortune' occurs only in the family-income and information-duty provisions" }]

#guard absentList.length == 1

end MgGlobal
