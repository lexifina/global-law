import R4Common

/-!
# Liberia 2025: corporate income tax (1200) and withholding (generated from `R4/specs/lr.json`)

Sources: Consolidated Liberia Revenue Code as amended 2020 (`cmp20/world/B10-anglophone-africa/lr/law/REVENUE-CODE-LIBERIA-REVENUE-CODE-AMENDEMENT-2020-min.txt`) and the Tax Amendment Act of December 2024 (approved 17 December 2024; OCR of `world/B10-anglophone-africa/lr/law/TAX-AMENDMENT-ACT-OF-DECEMBER-2024-AMENDING-THE-LIBERIA-CONSOLIDATED-REVENUE-CODE-AS-AMENDED.pdf`: it amends ss. 50, 55, 74, 203, 204, 211, 602, 702, 704, 741, 806 and 905 and leaves s. 200 as the 2020 consolidation prints it; not the later Tax Amendment Act of December 2025, `LRC-Amendment-December-2025.pdf`, approved 2026). Pass 10 (GST): Liberia Revenue Code as amended (2020 consolidation, `world/B10-anglophone-africa/lr/law/REVENUE-CODE-LIBERIA-REVENUE-CODE-AMENDEMENT-2020-min.txt`) Part III Chapter 10 s. 1000-1002, 1021-1022 (the sections are in the text body, not only the table of contents); Tax Amendment Act of 2024 amending certain portions of Chapters 8 and 10 (approved 17 Dec 2024, printed 20 Dec 2024, OCR `TAX-AMENDMENT-ACT-OF-2024-AMENDING-CERTAIN-PORTIONS-…_ocr.txt`). The December 2024 excise schedule was read on the page image (p. 12 of the Tax Amendment Act of December 2024): US$ per litre, imported / local columns. The LRC Amendment of December 2025 (services tax 13 %) applies from 2026.

LRC (2020): "(C) For income of other legal persons, a regular tax of 25% or a minimum tax of 2% of gross income, whichever is greater. (i) If the minimum tax applies, the excess of the minimum tax over the regular tax is creditable against regular tax due for the next succeeding tax year." The December 2024 amendment keeps "25 percent or a minimum tax of 2 percent of gross income, whichever is greater" (gross income taken as the turnover).

LRC: a payor to a "nonresident for services rendered is required to withhold tax at the rate of 15 percent of the amount of the payment" (Board fees, management fees, commissions). Dividend, interest and royalty rates to nonresidents not located in the OCR. Twelfth pass (kernel 2.3.0 grade-C withholding): dividend 15 %: LRC s. 806 (b) (15 %, payments to nonresidents); interest 15 %: LRC s. 806 (b) (15 %, payments to nonresidents); royalty 15 %: LRC s. 806 (b) (15 %, royalties and license fees to nonresidents)
-/

namespace LrGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Income tax (legal persons)", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 200, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2500249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 20000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 400000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 8000000
def whtR : Wht :=
  { name := "Withholding on payments to nonresidents",
    rules := [{ kind := .services, rateBp := 1500, statute := "LRC s. 906 (15 %, nonresident services)" },
              { kind := .dividend, rateBp := 1500, statute := "LRC s. 806 (b) (15 %, payments to nonresidents)" },
              { kind := .interest, rateBp := 1500, statute := "LRC s. 806 (b) (15 %, payments to nonresidents)" },
              { kind := .royalty, rateBp := 1500, statute := "LRC s. 806 (b) (15 %, royalties and license fees to nonresidents)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Income tax (legal persons)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "LRC s. 200 rates (C) (25 % or 2 % of gross income, whichever is greater), confirmed by the Tax Amendment Act of December 2024" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["LRC: the excess of the minimum tax over the regular tax is a credit for the next year (not tracked)", "gross income taken as the turnover"]

end LrGlobal
