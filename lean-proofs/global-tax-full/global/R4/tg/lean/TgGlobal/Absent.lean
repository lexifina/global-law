import R4Common

/-! # TG 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace TgGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "TG CGI-LPF édition 2025 (complete code): no tax on net wealth; 'fortune' occurs only incidentally (art. on declarations, LPF)" }]

#guard absentList.length == 1

end TgGlobal
