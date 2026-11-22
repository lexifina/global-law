import R4Common

/-! # NE 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace NeGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "NE: the general tax code held (CGI-2013-MAJ-LF2022.txt) has no charging provision on net wealth (full-text search 'impôt sur la fortune / le patrimoine', 'patrimoine net'); edition as held, later finance laws not all checked" }]

#guard absentList.length == 1

end NeGlobal
