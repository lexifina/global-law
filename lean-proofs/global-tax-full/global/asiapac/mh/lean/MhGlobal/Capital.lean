import MhGlobal.Pit

/-!
# Marshall Islands 2025: no tax on individuals' capital income or gains (1100, cited)

Income Tax Act 1989 (48 MIRC Ch. 1, consolidated to P.L. 2025-34, `cmp20/world/B14-pacific/mh/law/1989-0050_5.txt`) charges
wages and salaries (Part II), gross revenues of businesses (Part III, § 109) and non-residents' service fees (Part VI,
§ 117): interest, dividends and gains of individuals are not charged. The Net Profit Tax Act 2025 applies from tax years
beginning 1 October 2026 (§ 749 (2)).
-/

namespace MhGlobal.Capital
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 0

end MhGlobal.Capital
