import UaGlobal.Pit

/-!
# UA 2025: Податок на прибуток підприємств (1200) and withholding on payments abroad

Source: Податковий кодекс України, zakon.rada.gov.ua via Internet Archive 2025-06-20 (`ua/law/ptk_wb20250620.txt`); sha256 in `law/SHA256SUMS`.
* п. 136.1: "Базова (основна) ставка податку становить 18 відсотків"
* п.п. 141.4.2: income of a non-resident is taxed at source "15 відсотків (крім доходів, зазначених у підпунктах 141.4.4-141.4.5 ...)"


## 1200 Податок на доходи нерезидентів (послуги): services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Ukraine, Corporate - Withholding taxes, accessed 2025-06-24 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* 15 % on passive income and on other payments including engineering services, lease, agency and brokerage fees; 6 % on freight
-/

namespace UaGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Податок на прибуток підприємств",   sched := Schedule.flat 1800 }

def wht : Wht :=
  { name := "Податок з доходів нерезидентів", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ПКУ п.п. 141.4.2: 15 відсотків" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ПКУ п.п. 141.4.2: 15 відсотків" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ПКУ п.п. 141.4.2: 15 відсотків" }] }

def citStatute : String := "Податковий кодекс п. 136.1 (18 %)"

/-- Податковий кодекс України п. 141.4.1-141.4.2 -/
def p8wht2 : Wht :=
  { name := "Податок на доходи нерезидентів (послуги)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "Податковий кодекс п. 141.4.2: 15 % on Ukrainian-source income of non-residents including engineering services" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Податок на прибуток підприємств", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Податок на доходи нерезидентів (послуги) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["UA 1200: zakon.rada.gov.ua via Internet Archive 2025-06-20", "UA 1200 withholding pass 8 (services): 2025-06-24 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as engineering services; services outside the list bear none"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 18000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 180000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 15000

end UaGlobal.Corporate
