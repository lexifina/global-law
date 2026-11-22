import R4Common

/-! # LS 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace LsGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .sscEmployer, why := "LS old-age pension is universal and tax-financed ('Employer: None. Government: The total cost'); sickness/maternity cash benefits are employer liability; work injury is an employer-liability system through a private carrier. No public-fund employer contribution. Secondary source (2019)." }]

#guard absentList.length == 1

end LsGlobal
