import R4Common

/-! # BF 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace BfGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "BF CGI 2023 (complete code held): no tax on net wealth; full-text search for 'impôt sur la fortune', 'impôt sur le patrimoine', 'patrimoine net', 'fortune' finds only the UEMOA double-tax convention annexed" }]

#guard absentList.length == 1

end BfGlobal
