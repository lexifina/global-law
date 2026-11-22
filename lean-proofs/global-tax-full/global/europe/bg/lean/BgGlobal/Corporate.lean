import BgGlobal.Pit

/-!
# BG 2025: Корпоративен данък (1200) and withholding on payments abroad

Source: Закон за корпоративното подоходно облагане, lex.bg (private publisher of the consolidated text with the amendment notes), `bg/law/zkpo.html`; sha256 in `law/SHA256SUMS`.
* чл. 20: "Данъчната ставка на корпоративния данък е 10 на сто."


## 1200 withholding on payments abroad (pass 6)
Source: PwC Worldwide Tax Summaries, Bulgaria, Corporate - Withholding taxes, accessed 2025-04-19 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty WHT: dividends / liquidation proceeds 5 %; interest 10 %; royalties 10 % (also technical services, rents, franchising, management fees)


## 1200 Данък при източника (технически услуги): services (pass 8, grade B)
Source: Закон за корпоративното подоходно облагане (`bg/law/zkpo.txt`); PwC Worldwide Tax Summaries, Bulgaria, Corporate - Withholding taxes, accessed 2025-04-19 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* чл. 12 (5) т. 4: "възнаграждения за технически услуги" paid by Bulgarian payers are Bulgarian-source income; чл. 195 (1): withheld on such income of foreign legal entities without a place of business
* § 1 т. 9: technical services are installation of tangible assets and services of a consulting nature and market research
-/

namespace BgGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Корпоративен данък",   sched := Schedule.flat 1000 }

def citStatute : String := "Закон за корпоративното подоходно облагане чл. 20 (10 на сто)"

/-- ЗКПО чл. 194-195, 200 (dividends 5 %, interest and royalties 10 %) -/
def p6wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 500, statute := "ЗКПО чл. 194-195, 200 (dividends 5 %, interest and royalties 10 %)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "ЗКПО чл. 194-195, 200 (dividends 5 %, interest and royalties 10 %)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "ЗКПО чл. 194-195, 200 (dividends 5 %, interest and royalties 10 %)" }] }

/-- ЗКПО чл. 12 (5) т. 4, чл. 195 (1), § 1 т. 9 ДР; rate 10 % as for the other чл. 195 income -/
def p8wht : Wht :=
  { name := "Данък при източника (технически услуги)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "ЗКПО чл. 12 (5) т. 4, чл. 195 (1), § 1 т. 9 ДР: fees for technical services (installation, consulting, marketing research) of Bulgarian source, 10 %" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Корпоративен данък", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 withholding on payments abroad (pass 6)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p6wht.charges g.company else []) },
   { name := "1200 Данък при източника (технически услуги) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["BG 1200: lex.bg current text (2026-11); чл. 20 has no amendment note", "BG 1200 withholding: PwC WWTS Corporate - Withholding taxes, 2025-04-19 (Wayback capture) (grade B)", "BG 1200 withholding pass 8 (services): ЗКПО as on lex.bg (`bg/law/zkpo.txt`); rate: PwC Worldwide Tax Summaries, Bulgaria, Corporate - Withholding taxes, accessed 2025-04-19 (Wayback capture; `law/pwc_wht_wb2025.txt`) (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company then ["1200 withholding: EU parent-subsidiary / interest-royalty exemptions and the higher tax-haven rates not modelled"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as technical services (§ 1 т. 9 ДР); other services bear none"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 10000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 100000
#guard p6wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 5000
#guard p6wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p6wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 10000

end BgGlobal.Corporate
