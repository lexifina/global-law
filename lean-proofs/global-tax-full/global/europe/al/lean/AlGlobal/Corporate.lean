import AlGlobal.Pit

/-!
# AL 2025: Tatimi mbi fitimin (1200) and withholding on payments abroad

Source: PwC Worldwide Tax Summaries, Albania, Corporate - Taxes on corporate income, accessed 2025-07-08 (Wayback capture; `al/law/pwc_cit_wb2025.html`); the official act (qbz.gov.al ELI) is served by a script-only page; sha256 in `law/SHA256SUMS`.
* CIT 15 % (PwC page reviewed 30 June 2025)
* 5 % CIT: software production / development registered by 31.12.2023, to 31.12.2025; agricultural co-operation and agro-tourism 5 % to 2029


## 1200 Withholding tax (services): services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Albania, Corporate - Withholding taxes, accessed 2026-11-21 (live page; `law/pwc_wht_live.txt`).
* 15 % of the gross fee for technical or managerial services, installation, assembly or supervision; also on pay to managers and board members
-/

namespace AlGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Tatimi mbi fitimin",   sched := Schedule.flat 1500 }

def wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 800, statute := "Ligji 29/2023: 8 % on dividends (PwC)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "15 % (PwC)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "15 % (PwC)" }] }

def citStatute : String := "Ligji 29/2023 «Për tatimin mbi të ardhurat» (15 %)"

/-- Ligji për tatimin mbi të ardhurat (withholding on non-residents) -/
def p8wht2 : Wht :=
  { name := "Withholding tax (services)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "Law on income tax: 15 % of the gross fee for technical or managerial services, installation, assembly or supervision" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Tatimi mbi fitimin", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Withholding tax (services) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["AL 1200: PwC, last reviewed 30 June 2025", "AL 1200 withholding pass 8 (services): 2026-11-21 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as technical or management services; others not separated"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 15000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 150000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 8000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 15000

end AlGlobal.Corporate
