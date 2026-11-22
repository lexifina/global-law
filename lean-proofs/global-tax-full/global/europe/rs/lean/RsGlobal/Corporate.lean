import RsGlobal.Pit

/-!
# RS 2025: Porez na dobit pravnih lica (1200) and withholding on payments abroad

Source: Zakon o porezu na dobit pravnih lica, consolidated text published by Paragraf (private publisher; the official Pravno-informacioni sistem is script-only), `rs/law/pdpl.html`; sha256 in `law/SHA256SUMS`.
* čl. 39: "Stopa poreza na dobit pravnih lica je proporcionalna i jednoobrazna. Stopa poreza na dobit pravnih lica iznosi 15%."


## 1200 withholding on payments abroad (pass 6)
Source: PwC Worldwide Tax Summaries, Serbia, Corporate - Withholding taxes, accessed 2025-07-15 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty WHT 20 %: dividends, interest, royalties, some services, rents; 25 %: interest, royalties to listed tax havens


## 1200 Porez po odbitku (usluge): services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Serbia, Corporate - Withholding taxes, accessed 2025-07-15 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* 20 % on dividends, royalties, interest and on market research, accounting, audit and legal/business consulting fees; 25 % to tax havens


## 1200 porez na dobit and porez po odbitku: 2025 text read (čl. 39-40), A (gap pass, grade C)
Source: Službeni glasnik RS, official consolidations (pravno-informacioni-sistem.rs) read from lexifina/serbia-law: Zakon o porezu na dodatu vrednost `zakon/2004/84-25/clan-023.md` (version of 1.7.2018, unchanged to 2026), Zakon o porezu na dobit pravnih lica čl. 39-40 (commit a90dae4616).
* čl. 39: the rate of corporate income tax is 15 %
* čl. 40: 20 % withheld on dividends, shares in profit, royalties, interest, rents and market-research, accounting, audit and consulting services paid to non-residents; 25 % on payments to preferential-tax jurisdictions
-/

namespace RsGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Porez na dobit pravnih lica",   sched := Schedule.flat 1500 }

def citStatute : String := "Zakon o porezu na dobit pravnih lica čl. 39 (15 %)"

/-- Zakon o porezu na dobit pravnih lica čl. 40 (20 %; 25 % to listed tax havens) -/
def p6wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "Zakon o porezu na dobit pravnih lica čl. 40 (20 %; 25 % to listed tax havens)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "Zakon o porezu na dobit pravnih lica čl. 40 (20 %; 25 % to listed tax havens)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "Zakon o porezu na dobit pravnih lica čl. 40 (20 %; 25 % to listed tax havens)" }] }

/-- Zakon o porezu na dobit pravnih lica čl. 40 (withholding) -/
def p8wht2 : Wht :=
  { name := "Porez po odbitku (usluge)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "Zakon o porezu na dobit pravnih lica: 20 % on market research, accounting, audit and legal or business consulting services" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Porez na dobit pravnih lica", covers := [.cit],
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

def notes : List String := ["RS 1200: Paragraf consolidated text, current at fetch (2026-11)", "RS 1200 withholding: PwC WWTS Corporate - Withholding taxes, 2025-07-15 (Wayback capture) (grade B)", "RS 1200 withholding pass 8 (services): 2025-07-15 (grade B)", "RS gap pass: 1200 porez na dobit and porez po odbitku: 2025 text read (čl. 39-40), A"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company then ["1200 withholding: EU parent-subsidiary / interest-royalty exemptions and the higher tax-haven rates not modelled"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as the listed consulting/audit services; the 25 % tax-haven rate is not applied"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 15000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 150000
#guard p6wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p6wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p6wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 20000

end RsGlobal.Corporate
