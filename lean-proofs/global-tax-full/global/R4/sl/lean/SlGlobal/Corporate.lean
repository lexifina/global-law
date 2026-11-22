import R4Common

/-!
# Sierra Leone 2025: corporate income tax (1200) and withholding (generated from `R4/specs/sl.json`)

Sources: Income Tax Act 2000 as amended to the Finance Act 2017 (`cmp20/world/B10-anglophone-africa/sl/law/Income_Tax_Act_2000_as_amended_to_Finance_Act_2017_1_83760e046c.txt`). Finance Acts 2020 (OCR), 2023, 2024 and 2025 (`cmp20/world/B10-anglophone-africa/sl/law/`). GST Act 2009 compilation to 2016 (nra.gov.sl/tax-laws, `cmp20/global/R4/fetch/sl8/`, SHA256SUMS); Finance Acts 2017-2025 checked for s. 14.

ITA 2000 s. 5 (1): "the chargeable income of a resident company shall be taxed at the rate or rates" of the First Schedule Part III; Part III (to FA 2017): "Rates of Tax 30%". Finance Act 2020 (OCR): "(b) In part III by deleting the figure 30 and substituting it with the following new figure (25%)". Finance Act 2023 s. 6 and Finance Act 2024 s. 11 insert minimum alternate tax lines "immediately after the line relating to the 25% rate of tax for companies"; Finance Act 2026 s. 13 (a): "Part III by repealing the 25% relating to the rate of tax applicable to resident companies ... and replacing it with 30%" (2026 onwards). FA 2025 does not amend Part III.

Finance Act 2024 s. 12 (b): "Part II by repealing and replacing that part with the following new Part II - PART II (Sections 116,117,118,119,120,121,122 and 123) Rates of tax to be withheld from payments made to non-residents: ... Dividends (section 118) 15% Interest (section 119) 15% Management/professional fees 15% Rents and royalties (section 120) 15%".
-/

namespace SlGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Corporate income tax", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2500249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 250000
def whtR : Wht :=
  { name := "Withholding on payments to non-residents",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "ITA 2000 Second Schedule Part II (FA 2024): dividends 15 %" },
              { kind := .interest, rateBp := 1500, statute := "ITA 2000 Second Schedule Part II (FA 2024): interest 15 %" },
              { kind := .services, rateBp := 1500, statute := "ITA 2000 Second Schedule Part II (FA 2024): management/professional fees 15 %" },
              { kind := .royalty, rateBp := 1500, statute := "ITA 2000 Second Schedule Part II (FA 2024): rents and royalties 15 %" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Corporate income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Income Tax Act 2000 s. 5 (1) and First Schedule Part III as amended by the Finance Act 2020 (30 % replaced by 25 %); not amended by the Finance Acts 2021-2025 (FA 2026 restores 30 % from 2026)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["ITA s. 7A as replaced by the Finance Act 2024 s. 8: a company with an allowable loss for the year pays a minimum alternate tax of 2 % of turnover (First Schedule Part III as amended by FA 2024 s. 11), creditable over ten years: not modelled (the region's minimum-tax part would also apply it to profitable companies)", "the earlier rates (dividends 10 %, royalties 25 %) of the 2017 consolidation were replaced by the Finance Act 2024"]

end SlGlobal
