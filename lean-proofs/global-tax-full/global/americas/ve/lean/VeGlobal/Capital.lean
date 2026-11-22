import VeGlobal.Pit

/-!
# VE 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).
-/

namespace VeGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon VeGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

def families : List Family := [capF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := stackUnsupported g

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0

end VeGlobal.Capital
