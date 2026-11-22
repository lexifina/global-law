import NrGlobal.Pit

/-!
# Nauru 2025: no tax on individuals' capital income or gains (1100, cited)

Employment and Services Tax Act 2014 (`cmp20/world/B14-pacific/nr/law/gl_esta2014.txt`) taxes employment income (s. 11) and
services fees (s. 12) only; the Business Tax Act 2016 (RONLAW Service 6, `nr/law/nr_bta2016_serv6.txt`) taxes businesses
and the non-resident tax on interest, royalties and insurance premiums (s. 13): resident individuals' interest, dividends and
gains outside a business are not charged.
-/

namespace NrGlobal.Capital
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 0

end NrGlobal.Capital
