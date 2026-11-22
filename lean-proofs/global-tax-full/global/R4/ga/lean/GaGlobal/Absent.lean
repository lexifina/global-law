import R4Common

/-! # GA 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace GaGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "GA CGI 2025 (complete code): no tax on net wealth; 'fortune'/'patrimoine' occur only in income-tax and registration contexts" }]

#guard absentList.length == 1

end GaGlobal
