import ByGlobal.Pit

/-!
# BY 2025: Налог на прибыль (1200) and withholding on payments abroad

Source: Налоговый кодекс Республики Беларусь, Особенная часть, pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`); sha256 in `law/SHA256SUMS`.
* ст. 184 п. 1: "Ставка налога на прибыль устанавливается в размере двадцать (20) процентов, если иное не определено" (25 % for banks and insurers, not separated)
* ст. 192 п. 1: "1.3. десять (10) процентов – по доходам, указанным в подпункте 1.2 пункта 1 статьи 189" (debt obligations); "1.4. двадцать пять (25) процентов – по доходам, указанным в подпункте 1.4" (dividends); "1.5. пятнадцать (15) процентов – по другим доходам" (royalties, ст. 189 п. 1.3)


## 1200 Налог на доходы иностранных организаций (услуги): services (pass 9, grade A)
Source: Налоговый кодекс Республики Беларусь, Особенная часть, pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`).
* ст. 189 п. 1 пп. 1.12: income of a foreign organisation without a permanent establishment from works and services: 1.12.1 consulting, accounting, audit, marketing, legal, engineering; 1.12.5 management; 1.12.6 staffing; 1.12.10 advertising; 1.12.11 installation and maintenance; 1.12.13 any service to a related party
* ст. 192 п. 1 пп. 1.5: "пятнадцать (15) процентов – по другим доходам, указанным в пункте 1 статьи 189"


## 1200 Подоходный налог с физических лиц (налоговый агент: услуги нерезидентам): services (pass 10, grade A)
Source: Налоговый кодекс Республики Беларусь, Особенная часть, pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`).
* ст. 197 п. 1 пп. 1.6: remuneration for work performed or services rendered received from Belarusian organisations is income from Belarusian sources
* ст. 214 п. 1: "Ставка подоходного налога с физических лиц устанавливается в размере тринадцать (13) процентов", unless the article provides otherwise
* ст. 216 п. 1: Belarusian organisations are tax agents that compute and pay the tax on income they pay
-/

namespace ByGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Налог на прибыль",   sched := Schedule.flat 2000 }

def wht : Wht :=
  { name := "Налог на доходы иностранных организаций", rules := [
    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "НК ст. 192 п. 1.3 (ст. 189 п. 1.2): 10 %" },   { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 2500, statute := "НК ст. 192 п. 1.4 (ст. 189 п. 1.4): 25 %" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "НК ст. 192 п. 1.5 (ст. 189 п. 1.3): 15 %" }] }

def citStatute : String := "Налоговый кодекс ст. 184 п. 1 (20 %)"

/-- Налоговый кодекс, Особенная часть, ст. 189 п. 1 пп. 1.12, ст. 192 п. 1 пп. 1.5 -/
def p9wht2 : Wht :=
  { name := "Налог на доходы иностранных организаций (услуги)", rules := [
    { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 1500, statute := "НК ст. 189 п. 1 пп. 1.12, ст. 192 п. 1 пп. 1.5: 15 % on consulting, accounting, audit, marketing, legal, engineering, management and other listed services" }] }

/-- Налоговый кодекс, Особенная часть, гл. 17: ст. 197 п. 1 пп. 1.6, ст. 214 п. 1, ст. 216 п. 1 -/
def p10whti : Wht :=
  { name := "Подоходный налог с физических лиц (налоговый агент: услуги нерезидентам)", rules := [
    { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 1300, statute := "НК ст. 197 п. 1 пп. 1.6, ст. 214 п. 1, ст. 216 п. 1: remuneration for services received from a Belarusian organisation is Belarusian-source income; the organisation withholds 13 %" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Налог на прибыль", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Налог на доходы иностранных организаций (услуги) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9wht2.charges g.company else []) },
   { name := "1200 Подоходный налог с физических лиц (налоговый агент: услуги нерезидентам) (pass 10)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10whti.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["BY 1200: pravo.by via Internet Archive 2025-06-14", "BY 1200 withholding pass 9 (services; companies): pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`) (grade A)", "BY 1200 withholding pass 10 (services; individuals): pravo.by via Internet Archive 2025-06-14 (`by/law/pravo_tc_sp_wb20250614.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && p.toCompany) then ["1200 withholding: services are taken as one of the kinds listed in ст. 189 п. 1 пп. 1.12 (other services to unrelated parties bear none)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && !p.toCompany) then ["1200 withholding: a non-resident individual is taken as acting outside an individual-entrepreneur registration in Belarus (13 %, not the 20 % of ст. 214 п. 3)"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 20000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 200000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p10whti.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 13000

end ByGlobal.Corporate
