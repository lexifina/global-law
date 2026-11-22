import FmGlobal.Pit

/-!
# Micronesia (FSM) 2025: no national tax on individuals' capital income or gains (1100, cited)

FSM Code Title 54 ch. 1 (2014 codification, `cmp20/world/B14-pacific/fm/law/T54_Ch01_SubChpI_2014.txt`, `..._SubChpII_2014.txt`)
charges "a tax of six percent upon the first $11,000 and ten percent upon the amount over ... of all wages and salaries"
(§ 112) and the tax on gross revenues of businesses (§ 141): interest, dividends and gains of individuals are not charged.
-/

namespace FmGlobal.Capital
open TaxKernel TaxKernel.Global

def families : List Family := []

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard absent.length == 0

end FmGlobal.Capital
