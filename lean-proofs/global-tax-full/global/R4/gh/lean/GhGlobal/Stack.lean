import GhTax.Legacy
import TaxKernel.Global2

/-! # GH 2025: gains from the realisation of investment assets, stacked on the income tax, with the 25 % election
(nineteenth pass; kernel 2.7.0 `StackRule.electFlatBp`, request R4-18-3)

Income Tax Act 2015 (Act 896) s. 6 (1) (a) (ii): an individual's income from an investment includes "a gain from the
realisation of an investment asset as calculated under Part IV"; s. 35 (1): the gain is the amount received less the
cost of the asset. s. 133 "investment asset": "(a) includes a capital asset held as part of an investment being shares or
securities in a company, a beneficial interest in a trust or an interest in land or buildings, but excludes the primary
private residence of an individual, provided the residence has been owned by the individual continuously for the three
years before disposal and lived in on a daily basis for at least two of those three years". s. 7 (exempt amounts) has no
item on such gains in the held text. First Schedule para 1 (3) as substituted by the Income Tax (Amendment) Act 2023
(Act 1094) s. 13 (a): "Where the chargeable income of an individual includes a gain from the realisation of an
investment asset, less any loss from the realisation of an investment asset not charged elsewhere, the individual may
elect that the gain ... is taxed at the rate of twenty-five per cent"; para 1 (5): the remainder at the para 1 (1)
rates (as substituted by Act 1111, assent 29 December 2023, which replaced para 1 (1) only). The charge is the lower of
the 1.x income tax with the gain less without and 25 % of the gain (the election is the individual's: a taxpayer elects
when it lowers the tax). `into := .selfEmployment`: the 1.x model (`GhTax.person`) adds `selfEmployment` in full to the
assessable income, checked by the `#guard`s below.
Not modelled (listed in the P3 entry): the residence's three-year ownership and two-year occupation conditions (a
disposal marked `mainHome` is taken as meeting them), interests in trusts, bonds and other securities not of a company,
losses carried to other years, non-resident individuals (para 1 (2), 25 % flat), gains in a business (Part IV
business assets). -/

namespace GhGlobal
open Lean TaxKernel TaxKernel.Global

def ghGains : StackRule :=
  { name := "Income tax on gains from the realisation of investment assets (individuals; 25 % election)",
    statute := "Income Tax Act 2015 (Act 896) s. 6 (1) (a) (ii), s. 35 (1), s. 133 'investment asset' (primary private residence excluded); First Schedule para 1 (3) as substituted by Act 1094 (2023) s. 13 (a): election for 25 % on the gain, the lower of the two applied [text version: Act 896 as enacted (gazetted OCR) with Act 1094 (2023), Act 1111 (assent 29 December 2023: para 1 (1) only) and Act 1134 (2025: withholding only); amending Acts 2016-2020 not all held (flag)]",
    gainKinds := [.home, .realEstate, .land, .listedShares, .unlistedShares],
    gainRule := { mainHomeExempt := true },
    pool := .person, into := .selfEmployment, electFlatBp := 2500 }

def stackBase : GlobalModel := GlobalModel.ofCountry GhTax.country
def stackProbe : GlobalModel := stackBase.withStack [ghGains]

def stackLine (s : String) : CanonGlobal :=
  match Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

def stackDue (g : CanonGlobal) : List Int :=
  ((stackProbe.computeGlobal [] g).charges.filter (·.tax == ghGains.name)).map (·.due)

-- single, age 40, self-employment 300 000 (no SSNIT on it, no relief): Act 1111 bands give 73 244; a gain of 50 000 on
-- listed shares stacks at 30 % = 15 000; the election gives 25 % × 50 000 = 12 500: the lower, 12 500
def gs1 : CanonGlobal := stackLine
  "{\"id\":\"g\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"g\",\"adults\":[{\"age\":40,\"selfEmployment\":300000}]},\"disposals\":[{\"kind\":\"listedShares\",\"proceeds\":150000,\"cost\":100000}]}"
#guard stackDue gs1 == [12500]
-- without the election the stacked tax would be 15 000 (a self-employment of 350 000 gives 88 244 = 73 244 + 15 000)
def gs1b : CanonGlobal := stackLine
  "{\"id\":\"g\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"g\",\"adults\":[{\"age\":40,\"selfEmployment\":350000}]}}"
def gs1a : CanonGlobal := stackLine
  "{\"id\":\"g\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"g\",\"adults\":[{\"age\":40,\"selfEmployment\":300000}]}}"
#guard jsonIncomeTax (stackBase.computeGlobal [] gs1b).pit - jsonIncomeTax (stackBase.computeGlobal [] gs1a).pit == 15000
-- no other income, a gain of 20 000 on land: the scale gives 66 + 156 + 17,5 % × 11 240 = 2 189 < 25 % × 20 000 = 5 000
def gs2 : CanonGlobal := stackLine
  "{\"id\":\"g\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"g\",\"adults\":[{\"age\":40}]},\"disposals\":[{\"kind\":\"land\",\"proceeds\":70000,\"cost\":50000}]}"
#guard stackDue gs2 == [2189]
-- the primary private residence is not an investment asset: a computed 0
def gs3 : CanonGlobal := stackLine
  "{\"id\":\"g\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"g\",\"adults\":[{\"age\":40,\"selfEmployment\":300000}]},\"disposals\":[{\"kind\":\"home\",\"proceeds\":900000,\"cost\":400000,\"mainHome\":true}]}"
#guard stackDue gs3 == [0]
-- the 1.x line is untouched
#guard (stackProbe.computeGlobal [] gs1).pit == (stackBase.computeGlobal [] gs1).pit

end GhGlobal
