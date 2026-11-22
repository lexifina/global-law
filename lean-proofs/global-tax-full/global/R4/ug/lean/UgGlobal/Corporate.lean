import R4Common

/-!
# Uganda 2025: corporate income tax (1200) and withholding (generated from `R4/specs/ug.json`)

Source: Income Tax Act Cap. 338 (ULII, 23 December 2024: `cmp20/world/B10-anglophone-africa/ug/law/ita_2024-12-23.txt`). VAT: URA guide pages (Wayback captures of ura.go.ug/en/value-added-tax-vat/ 2025-09-04 and thetaxman.ura.go.ug); excise: Excise Duty Act 2014 ULII consolidation at 2023-12-31 (Wayback 2025-05-21) and the Excise Duty (Amendment) Act 2024 (parliament.go.ug CMIS PDF); saved in `cmp20/global/R4/fetch/ug8/` with SHA256SUMS.

Third Schedule Part III: "1. The income tax rate applicable to companies, other than mining companies, for the purposes of section 7 is 30%." Interest of group members is capped at thirty percent of tax EBITDA (s. 25 (3)-(4), excess carried forward three years): not applied (the company input does not say whether it belongs to a group).

Third Schedule Part IV: "1. The withholding tax rate applicable under section 81, 82, 83 or 84 excluding interest on Government securities is 15%." (s. 82: dividends, interest, royalties, natural resource payments, management charges to non-residents).
-/

namespace UgGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Income tax (companies)", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 300000
def whtR : Wht :=
  { name := "Non-resident withholding tax",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "ITA Third Schedule Part IV para 1 (15 %)" },
              { kind := .interest, rateBp := 1500, statute := "ITA Third Schedule Part IV para 1 (15 %)" },
              { kind := .royalty, rateBp := 1500, statute := "ITA Third Schedule Part IV para 1 (15 %)" },
              { kind := .services, rateBp := 1500, statute := "ITA Third Schedule Part IV para 1 (15 %)" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Income tax (companies)", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "ITA Cap. 338 Third Schedule Part III para 1 (30 %)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["ITA s. 25 (3): interest of group members capped at 30 % of tax EBITDA (group membership not an input): not applied", "mining companies' formula rate not applied"]

end UgGlobal
