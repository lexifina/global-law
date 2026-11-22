import MdGlobal.Pit

/-!
# MD 2025: Impozitul pe venit (persoane juridice) (1200) and withholding on payments abroad

Source: PwC Worldwide Tax Summaries, Moldova, Corporate - Taxes on corporate income, accessed 2025-07-08 (Wayback capture; `md/law/pwc_cit_wb2025.html`); legis.md refuses scripts (403), no Wayback copy of the Code; sha256 in `law/SHA256SUMS`.
* CIT 12 % (PwC page reviewed 2 July 2025); farming enterprises 7 %; optional 4 % regime on aggregated income for SMEs not registered for VAT


## 1200 withholding on payments abroad (pass 6)
Source: PwC Worldwide Tax Summaries, Moldova, Corporate - Withholding taxes, accessed 2025-06-24 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty WHT: dividends 6 % (15 % in some cases, not modelled); interest 12 %; royalties 12 %


## 1200 Impozit reținut la sursă (servicii): services (pass 9, grade B)
Source: PwC Worldwide Tax Summaries, Moldova, Corporate - Withholding taxes, accessed 2025-06-24 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* payments to non-residents: dividends 6 %; all other Moldovan-source income 12 %
-/

namespace MdGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Impozitul pe venit (persoane juridice)",   sched := Schedule.flat 1200 }

def citStatute : String := "Codul fiscal nr. 1163/1997 art. 15 lit. b) (12 %)"

/-- Codul fiscal art. 71, 72, 73 (dividends 6 %; interest and royalties 12 %) -/
def p6wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 600, statute := "Codul fiscal art. 71, 72, 73 (dividends 6 %; interest and royalties 12 %)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1200, statute := "Codul fiscal art. 71, 72, 73 (dividends 6 %; interest and royalties 12 %)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1200, statute := "Codul fiscal art. 71, 72, 73 (dividends 6 %; interest and royalties 12 %)" }] }

/-- Codul fiscal nr. 1163/1997 art. 71, 73 (non-residents) -/
def p9wht2 : Wht :=
  { name := "Impozit reținut la sursă (servicii)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1200, statute := "Codul fiscal art. 71, 73: 12 % on other Moldovan-source income of non-residents, services included" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Impozitul pe venit (persoane juridice)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 withholding on payments abroad (pass 6)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p6wht.charges g.company else []) },
   { name := "1200 Impozit reținut la sursă (servicii) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["MD 1200: PwC, last reviewed 2 July 2025", "MD 1200 withholding: PwC WWTS Corporate - Withholding taxes, 2025-06-24 (Wayback capture) (grade B)", "MD 1200 withholding pass 9 (services; all recipients): 2025-06-24 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company then ["1200 withholding: EU parent-subsidiary / interest-royalty exemptions and the higher tax-haven rates not modelled"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as Moldovan-source income (art. 71) taxed at the general 12 % rate"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 12000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 120000
#guard p6wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 6000
#guard p6wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 12000
#guard p6wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 12000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 12000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 12000

end MdGlobal.Corporate
