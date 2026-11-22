import NzGlobal.Pit
import TaxKernel.Global2

/-!
# New Zealand 2025-26: bright-line test for residential land stacked on the 1.x income tax (1100, kernel 2.5.0)

Income Tax Act 2007, Part C subpart CB, version as at 1 July 2026 (legislation.govt.nz `act/public/2007/97/en/latest/
parts/DLM1512389/`, Wayback 20260714104121; `nz/law/wb/ita2007_partCB_wb20260714.html`; the live site answers 202
to scripts). The 2-year test applies to disposals from 1 July 2024 (Taxation (Annual Rates for 2023-24, Multinational
Tax, and Remedial Matters) Act 2024), so the same text governs 2025:
* **s. CB 6A (1)**: an amount derived from disposing of residential land is income if the bright-line end date is
  within 2 years of the bright-line start date ((2): normally the date the transfer to the person was registered).
* **s. CB 16A (1)**: not if the land was used predominantly, for most of the bright-line period, for the person's main
  home ((3): not more than twice in 2 years, no regular pattern).
* Cost of the land is deductible (s. DB 23, not read here): the income is the gain (proceeds less cost and costs).
The gain enters taxable income through the 1.x household field `rentalIncome` (NzTax: taxed in full at the s. RA/Sch. 1
scale; no ACC earners' levy, which `selfEmployment` would attract). The 1.x model splits household fields equally
between adults: for a couple the gain is shared, not taxed on the owner alone (flagged).
Not modelled: ring-fenced bright-line losses (s. EL 20), rollover relief, `realEstate` other than residential land
(taken as residential), the main-home limits of s. CB 16A (3).
-/

namespace NzGlobal.Stack
open TaxKernel TaxKernel.Global

def brightLine : StackRule :=
  { name := "Bright-line test: residential land sold within 2 years (income)",
    statute := "Income Tax Act 2007 s. CB 6A (1), (2); s. CB 16A (1) (main home); rates: Sch. 1 Part A (1.x model)",
    gainKinds := [.home, .realEstate, .land],
    gainRule := { exemptAfterMonths := 24, mainHomeExempt := true },
    into := .rentalIncome }

def rules : List StackRule := [brightLine]

#guard brightLine.gainRule.exemptAfterMonths == 24

end NzGlobal.Stack
