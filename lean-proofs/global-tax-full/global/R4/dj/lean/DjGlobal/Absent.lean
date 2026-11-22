import R4Common

/-! # DJ 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace DjGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "DJ CGI 2008 recast (complete text): no tax on net wealth; the only occurrence of 'fortune' is in a penal provision (helping to hide 'la fortune d'autrui' from tax); no 'patrimoine net' (later finance laws not read)" }]

#guard absentList.length == 1

end DjGlobal
