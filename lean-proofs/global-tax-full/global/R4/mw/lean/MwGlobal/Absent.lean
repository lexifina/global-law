import R4Common

/-! # MW 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace MwGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .sscEmployer, why := "MW has no public social-insurance fund: the Pension Act 2023 s. 12 (1) requires 'a minimum of ten per cent by the employer' to a mandatory occupational pension scheme, i.e. individual accounts in privately managed funds (SSPTW: 'Mandatory individual account system'); a compulsory payment to a private fund is not a tax (OECD) and is not modelled. Sickness, maternity and work injury are employer-liability systems through private carriers." }]

#guard absentList.length == 1

end MwGlobal
