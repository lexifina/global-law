import PwGlobal.Pit

/-!
# Palau 2025: no tax on resident individuals' capital income or gains (1100, cited)

Palau National Code Title 40 as amended by RPPL 11-11 (`cmp20/world/B14-pacific/pw/law/RPPL-11-11.txt`) charges wages and
salaries (§ 1101: 6 %, 10 %, 12 %), the business profits tax of PGST-registered persons (§ 1421), non-residents' interest,
royalties, technical fees and insurance premiums (§ 1422) and international transport (§ 1423): resident individuals'
interest, dividends and gains outside a business are not charged.
-/

namespace PwGlobal.Capital
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 0

end PwGlobal.Capital
