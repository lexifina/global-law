import R4Common

/-! # SN 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace SnGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "SN CGI annoté janvier 2025 (complete code, Livres I-III): no tax on net wealth; the full text has no 'fortune' or 'patrimoine net' charging provision" }]

#guard absentList.length == 1

end SnGlobal
