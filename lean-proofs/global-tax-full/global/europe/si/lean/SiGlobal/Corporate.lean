import SiGlobal.Pit

/-!
# SI 2025: Davek od dohodkov pravnih oseb (1200) and withholding on payments abroad

Source: Zakon o obnovi, razvoju in zagotavljanju finančnih sredstev (ZORZFS), Uradni list RS 131/2023, uradni-list.si (official) as captured by the Internet Archive on 2025-04-11 (`si/law/zorzfs_ul131_2023_wb.html`); sha256 in `law/SHA256SUMS`.
* 64. člen (1): "Ne glede na 60. člen ZDDPO-2 se davek plačuje po stopnji 22 odstotkov od davčne osnove za leta 2024, 2025, 2026, 2027 in 2028."


## 1200 withholding on payments abroad (pass 6)
Source: PwC Worldwide Tax Summaries, Slovenia, Corporate - Withholding taxes, accessed 2025-06-17 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty WHT 15 %: dividends, interest, royalties; EU directive relief (parent-subsidiary, interest-royalty)


## 1200 Davčni odtegljaj (storitve): services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Slovenia, Corporate - Withholding taxes, accessed 2025-06-17 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* withholding on services (of a consulting, marketing, administrative, staffing, information or legal kind) only when paid to listed low-tax states (average CIT up to 12,5 %)
-/

namespace SiGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Davek od dohodkov pravnih oseb",   sched := Schedule.flat 2200 }

def citStatute : String := "ZORZFS (Uradni list RS 131/2023) 64. člen (1): 22 % for 2024-2028, notwithstanding ZDDPO-2 60. člen"

/-- ZDDPO-2 70. člen (15 %) -/
def p6wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ZDDPO-2 70. člen (15 %)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ZDDPO-2 70. člen (15 %)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ZDDPO-2 70. člen (15 %)" }] }

/-- ZDDPO-2 čl. 70 (withholding on services) -/
def p8wht2 : Wht :=
  { name := "Davčni odtegljaj (storitve)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "ZDDPO-2 čl. 70: service fees bear withholding only when paid to states with an average CIT rate up to 12,5 % (listed): none otherwise" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Davek od dohodkov pravnih oseb", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 withholding on payments abroad (pass 6)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p6wht.charges g.company else []) },
   { name := "1200 Davčni odtegljaj (storitve) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["SI 1200: ZORZFS as published 22.12.2023 (later amendments of 64. člen not checked)", "SI 1200 withholding: PwC WWTS Corporate - Withholding taxes, 2025-06-17 (Wayback capture) (grade B)", "SI 1200 withholding pass 8 (services): 2025-06-17 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company then ["1200 withholding: EU parent-subsidiary / interest-royalty exemptions and the higher tax-haven rates not modelled"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as paid to a state not on the low-tax list"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 22000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 220000
#guard p6wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p6wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p6wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end SiGlobal.Corporate
