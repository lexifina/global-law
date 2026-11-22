import ZaTax.Legacy
import TaxKernel.Global2

/-! # ZA 2025: capital gains tax stacked on the income tax (fourteenth pass; kernel 2.5.0 `Stack`, request R4-13-1)

Income Tax Act 58 of 1962 s. 26A includes the taxable capital gain in taxable income; Eighth Schedule para 5 (1): annual
exclusion R40 000 for a natural person; para 10 (a): inclusion rate 40 % for a natural person; para 45 (1): R2 000 000
of the gain on a primary residence disregarded. The tax is the 1.x model's own income tax with the included amount less
without (marginal rate, rebates unchanged). `into := .selfEmployment`: the 1.x model (`ZaTax.personTI`) adds
`selfEmployment` in full to the person's taxable income, checked by the `#guard`s below on this model.
Not modelled (listed in the P3 entry): personal-use assets (para 53), the death-year exclusion R300 000 (para 5 (2)),
the R1 800 000 small-business exclusion (para 57), losses carried forward (para 7), trusts and companies (80 %). -/

namespace ZaGlobal
open Lean TaxKernel TaxKernel.Global

def zaCgt : StackRule :=
  { name := "Capital gains tax (taxable capital gain in taxable income)",
    statute := "Income Tax Act 58 of 1962 s. 26A; Eighth Schedule para 5 (1) (annual exclusion R40 000), para 10 (a) (inclusion rate 40 % for a natural person), para 45 (1) (primary residence: R2 000 000 of the gain disregarded); rates: s. 5 (1) and the Rates and Monetary Amounts Act (1.x model)",
    gainKinds := [.home, .realEstate, .land, .listedShares, .unlistedShares, .bonds, .business, .other],
    gainRule := { mainHomeExempt := true, mainHomeCap := 2000000 },
    exclusion := { amount := 40000 }, pool := .person, inclusionBp := 4000, into := .selfEmployment }

def stackBase : GlobalModel := GlobalModel.ofCountry ZaTax.country
def stackProbe : GlobalModel := stackBase.withStack [zaCgt]

def stackLine (s : String) : CanonGlobal :=
  match Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

def stackDue (g : CanonGlobal) : List Int :=
  ((stackProbe.computeGlobal [] g).charges.filter (·.tax == zaCgt.name)).map (·.due)

-- single, age 40, wages R600 000, listed shares sold at a gain of R240 000: (240 000 − 40 000) × 40 % = 80 000
-- included; 2025/26 table: tax(680 000) − tax(600 000) = (179 147 + 39 % × 7 000) − (121 475 + 36 % × 87 200)
-- = 181 877 − 152 867 = 29 010 (the primary rebate cancels)
def zs1 : CanonGlobal := stackLine
  "{\"id\":\"z\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"z\",\"adults\":[{\"age\":40,\"wages\":600000}]},\"disposals\":[{\"kind\":\"listedShares\",\"proceeds\":500000,\"cost\":260000}]}"
#guard stackDue zs1 == [29010]
-- the hand form: the 1.x tax with 80 000 more self-employment income less without
#guard stackedTax (fun c => jsonIncomeTax (stackBase.pit [] c)) zs1.household { rentalIncome := 80000 } == 29010
-- a gain below the exclusion: a computed 0
def zs2 : CanonGlobal := stackLine
  "{\"id\":\"z\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"z\",\"adults\":[{\"age\":40,\"wages\":600000}]},\"disposals\":[{\"kind\":\"listedShares\",\"proceeds\":50000,\"cost\":20000}]}"
#guard stackDue zs2 == [0]
-- primary residence: gain 2 500 000, R2 000 000 disregarded: (500 000 − 40 000) × 40 % = 184 000 included;
-- tax(784 000) − tax(600 000) = (179 147 + 39 % × 111 000) − 152 867 = 222 437 − 152 867 = 69 570
def zs3 : CanonGlobal := stackLine
  "{\"id\":\"z\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"z\",\"adults\":[{\"age\":40,\"wages\":600000}]},\"disposals\":[{\"kind\":\"home\",\"proceeds\":4000000,\"cost\":1500000,\"mainHome\":true}]}"
#guard stackDue zs3 == [69570]
-- the 1.x line is untouched
#guard (stackProbe.computeGlobal [] zs1).pit == (stackBase.computeGlobal [] zs1).pit

end ZaGlobal
