import R4Common

/-! # BJ 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace BjGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "BJ CGI 2023 (complete code held): no tax on net wealth; full-text search for 'impôt sur la fortune', 'impôt sur le patrimoine', 'patrimoine net' finds no charging provision" }]

#guard absentList.length == 1

end BjGlobal
