import R4Common.Basic
import TaxKernel.Global2

/-! # R4Common → kernel 2.1 (API.md §4e.1): the region's excise and minimum-tax parts as kernel `ExciseRule` /
`MinimumTax` (value before excise and VAT; OHADA minimum with floor, cap, rounding step), field for field. -/

namespace R4
open TaxKernel TaxKernel.Global

def Exc.toRule (e : Exc) : ExciseRule :=
  { good := e.good, name := e.name, perUnitNum := e.perUnitNum, perUnitDen := e.perUnitDen, onPureAlcohol := e.onPureAlcohol, minNum := e.minNum, minDen := e.minDen, minAbvBp := e.minAbvBp, maxAbvBp := e.maxAbvBp, imported := e.imported, statute := e.statute, adValoremBp := e.advBp, valueBase := .beforeTax, vatBp := e.vatBp }

def MinTax.toMinimum (m : MinTax) : MinimumTax :=
  { bp := m.bp, onAssets := m.onAssets, fixed := m.fixed, floor := m.floor, cap := m.cap }

/-- The kernel 2.1 corporate rule for a regime, an OHADA minimum and a rounding step. -/
def corpRule (r : CorpRegime) (m : MinTax) (step : Int) : CorpRule := { regime := r, minTax := some m.toMinimum, step := step }

end R4
