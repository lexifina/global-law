import HrGlobal.Pit

/-!
# HR 2025: Porez na dobit (1200) and withholding on payments abroad

Source: Narodne novine (official gazette) amending acts NN 138/2020 and NN 114/2023 (`hr/law/nn2020_138_2627_dobit.html`, `nn2023_114_1613_dobit.html`); the article's full wording from the unofficial consolidated text of zakon.hr (to NN 53/26; zakon.hr refuses scripts, read through a research agent), no official consolidation; sha256 in `law/SHA256SUMS`.
* čl. 28 st. 1 (consolidated): "Porez na dobit plaća se na utvrđenu poreznu osnovicu po stopi: 1. 10% ako su u poreznom razdoblju ostvareni prihodi do 1.000.000,00 eura, ili 2. 18% ako su u poreznom razdoblju ostvareni prihodi jednaki ili veći od 1.000.000,00 eura."
* NN 114/2023: "U članku 28. stavku 1. točki 1. riječi: »995.421,06 eura« zamjenjuju se riječima: 1.000.000,00 eura«. U točki 2. riječi: »995.421,06 eura« zamjenjuju se riječima: »1.000.000,00 eura«."
* NN 138/2020: "U članku 28. točki 1. riječi: »12%« zamjenjuju se riječima: »10%«."


## 1200 withholding on payments abroad (pass 6)
Source: PwC Worldwide Tax Summaries, Croatia, Corporate - Withholding taxes, accessed 2025-05-14 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty WHT to foreign legal entities: dividends 10 %; interest 15 %; royalties / IP fees 15 %


## 1200 Porez po odbitku (usluge): services (pass 8, grade B)
Source: Zakon o izmjenama Zakona o porezu na dobit, NN 114/2023 (`hr/law/nn2023_114_1613_dobit.txt`); PwC Worldwide Tax Summaries, Croatia, Corporate - Withholding taxes, accessed 2025-05-14 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* NN 114/2023 čl. 31 st. 12: 25 % on market research, tax and business consulting and audit services when paid to persons in states listed by the EU as non-cooperative and without a treaty
* PwC: these services are within Croatian withholding only in that case
-/

namespace HrGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Porez na dobit",   sched := Schedule.flat 1800,   smallTurnover := 999999,   smallSched := Schedule.flat 1000 }

def citStatute : String := "Zakon o porezu na dobit čl. 28 st. 1 (10 % if revenue below 1.000.000,00 eura, 18 % otherwise); NN 138/2020 (12 -> 10 %), NN 114/2023 čl. 8 (threshold 1.000.000,00 eura from 1.1.2024)"

/-- Zakon o porezu na dobit čl. 31 (dividends 10 %, interest and royalties 15 %) -/
def p6wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Zakon o porezu na dobit čl. 31 (dividends 10 %, interest and royalties 15 %)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "Zakon o porezu na dobit čl. 31 (dividends 10 %, interest and royalties 15 %)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "Zakon o porezu na dobit čl. 31 (dividends 10 %, interest and royalties 15 %)" }] }

/-- Zakon o porezu na dobit čl. 31 (izmjena NN 114/2023, st. 12) -/
def p8wht2 : Wht :=
  { name := "Porez po odbitku (usluge)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Zakon o porezu na dobit čl. 31 (NN 114/2023): consulting, market research and audit services bear withholding (25 %) only when paid to EU non-cooperative jurisdictions; none otherwise" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Porez na dobit", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 withholding on payments abroad (pass 6)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p6wht.charges g.company else []) },
   { name := "1200 Porez po odbitku (usluge) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["HR 1200: NN 114/2023 (tax periods from 1.1.2024); full article via the unofficial consolidation", "HR 1200 withholding: PwC WWTS Corporate - Withholding taxes, 2025-05-14 (Wayback capture) (grade B)", "HR 1200 withholding pass 8 (services): NN 114/2023; 2025-05-14 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company then ["1200 withholding: EU parent-subsidiary / interest-royalty exemptions and the higher tax-haven rates not modelled"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as paid to a cooperative jurisdiction (0); 25 % for EU-listed non-cooperative jurisdictions not applied"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 18000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 180000
#guard cit.citTax { profit := 100000, turnover := 999999 } == 10000
#guard cit.citTax { profit := 100000, turnover := 1000000 } == 18000
#guard p6wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p6wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p6wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end HrGlobal.Corporate
