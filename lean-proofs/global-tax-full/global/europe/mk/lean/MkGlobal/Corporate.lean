import MkGlobal.Pit

/-!
# MK 2025: Данок на добивка (1200) and withholding on payments abroad

Source: PwC Worldwide Tax Summaries, North Macedonia, Corporate - Taxes on corporate income, accessed 2025-05-21 (Wayback capture; `mk/law/pwc_cit_wb2025.html`); Corporate - Withholding taxes, accessed 2025-05-14 (Wayback capture; `mk/law/pwc_wht_wb2025.html`); sha256 in `law/SHA256SUMS`.
* CIT 10 % (PwC page reviewed 18 February 2025)
* WHT 10 % on listed income paid abroad (dividends, interest, royalties, ...)


## 1200 Данок по одбивка (технички услуги): services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, North Macedonia, Corporate - Withholding taxes, accessed 2025-05-14 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* 10 % on gross income from royalties and from technical services (managerial, technical, consulting)


## 1200 данок на добивка и данок по одбивка: 2025 text read (чл. 2, 21-22), A (gap pass, grade C)
Source: Службен весник на РСМ, Закон за данокот на добивка (112/2014 и измени) чл. 2 и 21-22, acts as published read from lexifina/north-macedonia-law (commit 214405c00).
* чл. 2: profit tax 10 %
* чл. 21-22: 10 % withheld on dividends, interest, royalties and management, consulting and technical services paid to foreign legal persons
-/

namespace MkGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Данок на добивка",   sched := Schedule.flat 1000 }

def wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Закон за данокот на добивка: 10 % (statute read, gap pass)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (statute read, gap pass)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (statute read, gap pass)" }] }

def citStatute : String := "Закон за данокот на добивка (10 %)"

/-- Закон за данокот на добивка (withholding on non-residents) -/
def p8wht2 : Wht :=
  { name := "Данок по одбивка (технички услуги)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Закон за данокот на добивка: 10 % on fees for managerial, technical and consulting services" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Данок на добивка", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Данок по одбивка (технички услуги) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["MK 1200: PwC, last reviewed 18 February 2025", "MK 1200 withholding pass 8 (services): 2025-05-14 (grade B)", "MK gap pass: 1200 данок на добивка и данок по одбивка: 2025 text read (чл. 2, 21-22), A"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as managerial, technical or consulting services"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 10000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 100000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 10000

end MkGlobal.Corporate
