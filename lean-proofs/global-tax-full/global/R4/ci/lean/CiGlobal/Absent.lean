import R4Common

/-! # CI 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace CiGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "CI CGI 2025 (complete DGI online code): no tax on net wealth; full-text search for 'impôt sur la fortune', 'patrimoine net', 'impôt de solidarité sur la fortune' finds nothing (the 'impôt sur le patrimoine foncier' is a recurrent property tax, P5)" }]

#guard absentList.length == 1

end CiGlobal
