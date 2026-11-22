import R4Common

/-! # BW 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace BwGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .sscEmployer, why := "BW has no contributory social insurance: old-age pension is universal ('Employer Universal: None ... Government Universal: The total cost'), sickness/maternity and work injury are employer-liability systems (benefits paid directly or insured with private carriers), not contributions to a public fund. Secondary source (2019), no later statute creating a contribution found. Human Resource Development Levy is on turnover (not payroll), noted under P7." }]

#guard absentList.length == 1

end BwGlobal
