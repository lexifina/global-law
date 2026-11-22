import R4Common

/-!
# Zambia 2025: corporate income tax (1200) and withholding (generated from `R4/specs/zm.json`)

Zambia Revenue Authority, 'Tax information' page (`cmp20/global/R4/fetch/zm8/`, live copy of 2026-11-21 and Wayback capture of 2025-05-16, SHA256SUMS); Income Tax (Amendment) Acts 2023-2025 (`cmp20/world/B09-southern-africa/zm/law/`). The consolidated Income Tax, VAT and Customs and Excise Acts are not held. Pass 9: amendment Acts from parliament.gov.zm (/acts-of-parliament → /node/<n> → sites/default/files/documents/acts/*.pdf): Customs and Excise (Amendment) Acts No. 25 of 2022, No. 25 of 2023, No. 24 of 2024 (in operation 1 Jan 2025) and No. 11 of 2025 (published 19 Aug 2025); Income Tax (Amendment) Acts No. 17 of 2018, No. 15 of 2019, No. 43 of 2021, No. 24 of 2022, No. 22 of 2023, No. 22 of 2024 (1 Jan 2025) and No. 10 of 2025 (published 19 Aug 2025). Texts and SHA256SUMS in `R4/fetch/zm9/` (pdftotext -layout). The consolidated Acts (Cap. 322, Cap. 323) are not held: only rates whose figure and unit are printed in an amending Act are modelled.

ZRA, Tax information, Income Tax (worked example): a taxable income of K1 250 000 at the 30 % rate gives K375 000; the page adds that some sectors have other rates set in the Charging Schedule (agriculture 10 %). The Income Tax (Amendment) Act 2024 s. 15 amends paragraph 5 of the Charging Schedule for sector items (e.g. copper-cathode products 20 %), not the general rate. Grade B: guide, not the Act; the sentence is on the live page (2026), not in the 2025-05-16 capture.

Act No. 17 of 2018 s. 17 (c): "in paragraph 6 (1) ... by the deletion of item (b) and the substitution therefor of the following: (b) the rate of twenty percent for— (i) dividends payable to non-residents; and (ii) payments to non-resident contractors"; Act No. 15 of 2019 s. 11: "(x) tax required to be deducted from the payment of interest, except interest on Treasury Bills and Government bonds to a non-resident, shall be at the rate of twenty percent."; Act No. 43 of 2021: "(iii) by the renumbering of item (x) as item (ix)"; Act No. 10 of 2025 s. 4: "(ix) tax required to be deducted from the payment of interest to a non resident, shall be at the rate of twenty percent." Thirteenth pass (kernel 2.3.0 grade-C withholding): royalty 20 %: ITA Cap. 323 Charging Schedule para 7 (royalties to non-residents 20 %, final), per the ZRA leaflet 'Withholding Taxes' (2023, Wayback capture 2023-08-04, `R4/fetch/p13/zm_wht_leaflet_2023.pdf`: royalties 15 % for residents, 20 % for non-residents, final for non-residents); amending Acts 2023-2025 held do not touch the item (official secondary, B)
-/

namespace ZmGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Corporate income tax", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 300000
def whtR : Wht :=
  { name := "Withholding tax on payments to non-residents",
    rules := [{ kind := .dividend, rateBp := 2000, statute := "Charging Schedule para 6 (1) (b) (i) (Act 17/2018): 20 %" },
              { kind := .services, rateBp := 2000, statute := "Charging Schedule para 6 (1) (b) (ii) (Act 17/2018): non-resident contractors 20 %" },
              { kind := .interest, rateBp := 2000, statute := "Charging Schedule para 7 item (ix) (Acts 15/2019, 43/2021, 10/2025): 20 %" },
              { kind := .royalty, rateBp := 2000, statute := "ITA Cap. 323 Charging Schedule para 7 (royalties to non-residents 20 %, final), per the ZRA leaflet 'Withholding Taxes' (2023, Wayback capture 2023-08-04, `R4/fetch/p13/zm_wht_leaflet_2023.pdf`: royalties 15 % for residents, 20 % for non-residents, final for non-residents); amending Acts 2023-2025 held do not touch the item (official secondary, B)" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 200000
#guard whtR.amount { kind := .services, amount := 1000000 } == 200000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 200000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 200000
def corporate : Family :=
  { name := "1200 Corporate income tax", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Income Tax Act Cap. 323 Charging Schedule (company rate 30 %), per the Zambia Revenue Authority guide (official secondary, live page 2026-11-21); the Income Tax (Amendment) Acts 2023 and 2024 amend only sector items of the Charging Schedule" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["sector rates (agriculture 10 %, mining, manufacturing of copper products, banks) and the turnover tax regime are not modelled", "Income Tax (Amendment) Act No. 10 of 2025 (published 19 Aug 2025) adds s. 14A, a minimum alternative tax of 1 % of turnover (Charging Schedule para 8) credited against income tax for five years; not modelled (regulations under s. 14A (6), application to the 2025 charge year not established)", "royalties to non-residents 20 % (ZRA leaflet 2023, B); management or consultancy fees to non-residents (s. 82A, 20 % final per the same leaflet) fall under the services rule (20 %)"]

end ZmGlobal
