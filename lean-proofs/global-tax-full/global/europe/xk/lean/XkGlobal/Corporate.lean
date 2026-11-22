import XkGlobal.Pit

/-!
# XK 2025: Tatimi në të ardhurat e korporatave (1200) and withholding on payments abroad

Source: PwC Worldwide Tax Summaries, Kosovo, Corporate - Taxes on corporate income, accessed 2025-06-24 (Wayback capture; `xk/law/pwc_cit_wb2025.html`); Corporate - Withholding taxes, accessed 2025-06-24 (Wayback capture; `xk/law/pwc_wht_wb2025.html`); sha256 in `law/SHA256SUMS`.
* CIT 10 % (PwC page reviewed 22 January 2025); small taxpayers: 3 % of gross income (trade, transport, agriculture, similar), 9 % of quarterly gross income (services)
* WHT: interest, royalties 10 %; rent 9 %; services of non-residents 5 %; dividends none


## 1200 Withholding tax (dividends, services): dividend, services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Kosovo, Corporate - Withholding taxes, accessed 2025-06-24 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty rates: dividends 0 %, interest 10 %, royalties 10 %; services provided by non-residents 5 %


## 1200 CIT and withholding: 2025 text read (06/L-105), A (gap pass, grade C)
Source: Gazeta Zyrtare e Republikës së Kosovës: Ligji nr. 06/L-105 për tatimin në të ardhurat e korporatave neni 7 and the withholding articles (commit 94aeb29291); Ligji nr. 05/L-037 për TVSH neni 26 (commit e9e51ada36, in force 1.9.2015), acts as enacted read from lexifina/kosovo-law.
* neni 7: corporate income tax 10 %
* withholding: interest 10 %, royalties 10 %, rent 9 %, services of non-residents 5 %; no line for dividends
-/

namespace XkGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Tatimi në të ardhurat e korporatave",   sched := Schedule.flat 1000 }

def wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Ligji për tatimin në të ardhurat e korporatave: 10 % (statute read, gap pass)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (statute read, gap pass)" }] }

def citStatute : String := "Ligji Nr. 06/L-105 për tatimin në të ardhurat e korporatave (10 %)"

/-- Ligji për tatimin në të ardhurat e korporatave (withholding on non-residents) -/
def p8wht2 : Wht :=
  { name := "Withholding tax (dividends, services)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Law on CIT: dividends paid to non-residents bear no withholding (0 %)" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 500, statute := "Law on CIT: services provided by non-residents 5 %" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Tatimi në të ardhurat e korporatave", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Withholding tax (dividends, services) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["XK 1200: PwC, last reviewed 22 January 2025", "XK 1200 withholding pass 8 (dividend, services): 2025-06-24 (grade B)", "XK gap pass: 1200 CIT and withholding: 2025 text read (06/L-105), A"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 10000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 100000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 5000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 5000

end XkGlobal.Corporate
