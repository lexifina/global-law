import R4Common

/-! # ZM 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace ZmGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "ZM: no net wealth tax. ZRA's list of the taxes it administers (turnover tax, PAYE, VAT, income tax, withholding tax, presumptive tax, property transfer tax, excise duty, base tax, insurance premium levy, mineral royalty) has none" }]

#guard absentList.length == 1

end ZmGlobal
