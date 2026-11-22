import R4Common

/-!
# Mauritius 2025: income tax on companies (1200) and withholding

Source: Income Tax Act 1995, MRA consolidation (`cmp20/world/B09-southern-africa/mu/law/ITAConsolidated.txt`).

* First Schedule Part IV: "Rate of income tax 15 per cent" (companies; Part II 3 % and Part III 5 % on the first
  1.5 billion rupees are for the activities listed in s. 44A-type provisions, not the default).
* Fourth Schedule (withholding): "1. Interest 10 per cent; 2. Royalties – (a) a resident 10 per cent (b) a
  non-resident 15 per cent"; payments to service providers 3 % (residents only); dividends are exempt income, no
  withholding.
-/

namespace MuGlobal
open TaxKernel TaxKernel.Global

def it : CorpRegime := { name := "Income tax (companies)", sched := Schedule.flat 1500 }

def wht : Wht :=
  { name := "Tax deduction at source",
    rules := [{ kind := .interest, rateBp := 1500, statute := "ITA s. 111B (a), 111C (1), (4), Sixth Schedule item 1 (15 %; MRA consolidation up to Finance Act 2026)" },
              { kind := .royalty, rateBp := 1500, statute := "ITA s. 111B (b), 111C (4), Sixth Schedule item 2 (b) (15 %, non-resident)" },
              { kind := .services, rateBp := 1000, statute := "ITA s. 111B (h) (payments by a person other than an individual to a non-resident for services rendered in Mauritius), Sixth Schedule item 8 (10 %)" },
              WhtRule.zero .dividend "ITA Second Schedule Part II Sub-Part B item 1 (a): dividends paid by a company resident in Mauritius are exempt income; no withholding"] }

def corporate : Family := R4.corpFamily "income tax (companies)" it {} "ITA First Schedule Part IV (15 %)" wht

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Corporate Climate Responsibility Levy and the Fair Share Contribution on companies (Finance Acts 2024-2025): not modelled",
   "ITA First Schedule Parts II-III reduced rates (3 % / 5 %) for listed activities: not applied",
   "withholding (thirteenth pass): interest 15 % as printed in Sixth Schedule item 1 of the consolidation up to FA 2026 (the earlier 10 % of FA 2010 / FA 2012 is superseded; the amending note for 15 % was not located: flag); services 10 % apply to services rendered in Mauritius only (s. 111B (h))"]

#guard R4.corpTax it {} { profit := 1000000 } == 150000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 0

end MuGlobal
