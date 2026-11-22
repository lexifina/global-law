import R4Common

/-! # CM 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace CmGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "CM CGI 2024 (édition held) (complete code held): no tax on net wealth; full-text search for 'impôt sur la fortune', 'impôt sur le patrimoine', 'patrimoine net' finds no charging provision" }]

#guard absentList.length == 1

end CmGlobal
