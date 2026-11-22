import AuGlobal.Pit
import TaxKernel.Global2

/-!
# Australia 2024-25: capital gains of individuals stacked on the 1.x income tax (1100, kernel 2.5.0 `StackRule`)

Income Tax Assessment Act 1997, compilation in force on 1 July 2025 (legislation.gov.au C2004A05138, epub volume 3,
`au/law/fedleg/itaa1997_20250701_vol3.html`):
* **s. 102-5 (1)**: assessable income includes the net capital gain: capital gains less capital losses (step 1), less
  earlier net capital losses (step 2), then the discount percentage on discount capital gains (step 3).
* **s. 115-25 (1)**: a discount capital gain needs a CGT asset acquired at least 12 months before the CGT event;
  **s. 115-100 (a) (i)**: 50 % for an individual (not a foreign or temporary resident, ss. 115-105, 115-110).
* **s. 118-5 (a)**: a gain on a car, motor cycle or similar vehicle is disregarded (vehicles are left out of the rule);
  **s. 118-110 (1)**: a dwelling that was the individual's main residence throughout the ownership period: disregarded.
The included amount enters the owner's taxable income through the 1.x field `selfEmployment` (AuTax.Person: added in
full to taxable income, like the net capital gain), so the Income Tax Rates Act 1986 scale, the Medicare levy and the
offsets of the 1.x model apply. The 1.x model's own `capitalGains` input (always halved) is not used by this rule.
Not modelled: carried-forward net capital losses (step 2), the order of losses against discount gains (losses here
reduce each kind's gains before the discount is applied per disposal), small business concessions (Div 152), foreign
and temporary residents.
-/

namespace AuGlobal.Stack
open TaxKernel TaxKernel.Global

def cgt : StackRule :=
  { name := "Capital gains tax (net capital gain in assessable income)",
    statute := "ITAA 1997 s. 102-5 (1), s. 115-25 (1), s. 115-100 (a) (i) (50 % discount), s. 118-5 (a), s. 118-110 (1); rates: Income Tax Rates Act 1986 (1.x model)",
    gainKinds := [.home, .realEstate, .land, .listedShares, .unlistedShares, .bonds, .business, .other],
    gainRule := { longAfterMonths := 12, inclusionShortBp := 10000, inclusionLongBp := 5000, mainHomeExempt := true },
    into := .selfEmployment }

def rules : List StackRule := [cgt]

#guard cgt.gainRule.inclusionLongBp == 5000
#guard !(cgt.gainKinds.contains .vehicle)

end AuGlobal.Stack
