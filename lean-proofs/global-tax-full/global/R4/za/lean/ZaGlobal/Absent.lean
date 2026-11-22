import R4Common

/-! # ZA 2025: headings not levied, each with the provision or absence evidence (gen_pkgs.py) -/

namespace ZaGlobal
open TaxKernel TaxKernel.Global

def absentList : List Absent :=
  [{ oecd := .wealth, why := "ZA: no national net wealth tax. SARS's list of the taxes it administers (19: air passenger tax, capital gains tax, corporate and personal income tax, dividends tax, donations tax, estate duty, IOPC levy, mineral and petroleum royalty, PAYE, provisional tax, securities transfer tax, skills development levy, transfer duty, turnover tax, UIF, VAT, withholding taxes on interest and royalties) has none (municipal rates on property are 4100)" }]

#guard absentList.length == 1

end ZaGlobal
