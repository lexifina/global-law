import TaxKernel
import EeTax.Model

/-!
# Monthly withholding (TuMS § 41-43) against the annual return (§ 44, § 46)

The employer withholds 22 % each month from the payment less the employee's unemployment insurance (§ 42(5)) and
II-pillar payment (§ 42(6)) and, on the employee's written application to ONE payer (§ 42(2)), less the monthly
exemption of § 42(1) computed on that month's payment alone: 654 – 654/900 × (payment – 1200). The annual return
recomputes the § 23 exemption on the year's whole income. For a payment stream that is the same every month the two
agree to within rounding (`Theorems.monthly_even_bounds`); otherwise the annual return gives a refund or a bill.
-/

namespace EeTax
open TaxKernel

/-- One month's withholding on a wage payment `w` (cents) by the payer holding the exemption application. -/
def monthWithheld (applyEx : Bool) (p2rate w : Int) : Int :=
  let ui := uiContribution.amount w
  let p2 := pct p2rate w
  let ex := if applyEx then min (monthlyExemption.amount w) (pos (w - ui - p2)) else 0
  tax22 (pos (w - ui - p2 - ex))

/-- The year's withholding for a list of monthly payments from the one payer. -/
def yearWithheld (applyEx : Bool) (p2rate : Int) (ws : List Int) : Int :=
  ws.foldl (fun acc w => acc + monthWithheld applyEx p2rate w) 0

/-- The annual liability for the same wages and nothing else. -/
def yearAnnual (p2rate : Int) (ws : List Int) : Int :=
  let tot := ws.foldl (· + ·) 0
  -- unemployment insurance and II pillar are withheld per payment; summed per month as the payer does
  let ui := ws.foldl (fun acc w => acc + uiContribution.amount w) 0
  let p2 := ws.foldl (fun acc w => acc + pct p2rate w) 0
  let ex := basicExemption.amount tot
  tax22 (pos (tot - ui - p2 - ex))

/-- Refund (positive) or bill (negative) on the annual return. -/
def yearSettlement (p2rate : Int) (ws : List Int) : Int := yearWithheld true p2rate ws - yearAnnual p2rate ws

/-- Monthly withholding for an even stream of `annual` cents, via the kernel's `perPeriod` (12 equal months). -/
def evenWithheld (p2rate annual : Int) : Int := perPeriod 12 (monthWithheld true p2rate) annual

end EeTax
