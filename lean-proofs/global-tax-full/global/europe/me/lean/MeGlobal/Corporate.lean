import MeGlobal.Pit

/-!
# ME 2025: Porez na dobit pravnih lica (1200) and withholding on payments abroad

Source: PwC Worldwide Tax Summaries, Montenegro, Corporate - Taxes on corporate income, accessed 2025-05-27 (Wayback capture; `me/law/pwc_cit_wb2025.html`); Corporate - Withholding taxes, accessed 2025-07-14 (Wayback capture; `me/law/pwc_wht_wb2025.html`); sha256 in `law/SHA256SUMS`.
* CIT: profit ≤ EUR 100 000: 9 %; 100 000-1 500 000: EUR 9 000 + 12 % of the excess; above: EUR 177 000 + 15 % of the excess (PwC page reviewed 25 March 2025)
* WHT 15 %: dividends, interest, royalties and other listed income; 30 % to entities in listed tax havens


## 1200 Porez po odbitku (usluge): services (pass 9, grade B)
Source: PwC Worldwide Tax Summaries, Montenegro, Corporate - Withholding taxes, accessed 2025-07-14 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* withholding at 15 % covers dividends, interest, royalties and, among services, consulting, market research and audit fees paid to non-residents


## 1200 services of non-resident individuals (pass 18, grade B)
Source: PwC Worldwide Tax Summaries, Montenegro, its page on taxes on personal income (individuals), Internet Archive 2025-03-22 (`me/law/pwc_indpit_wb20250322.*`), facts only.
* Zakon o porezu na dohodak fizičkih lica (PwC 2025: non-residents are taxed on income of a fixed base or permanent establishment in Montenegro and on royalties, interest and rent of property there): a fee for services paid to a non-resident individual who has no fixed base there is not taxed (cited 0 rule)


## 1200 porez na dobit and porez po odbitku: 2025 text read (čl. 28-29), A (gap pass, grade C)
Source: Službeni list Crne Gore, Zakon o porezu na dobit pravnih lica čl. 28 (progressive rates, from 1.1.2022) and čl. 29 (as amended by 125/2023, from 1.1.2024), acts as published read from lexifina/montenegro-law (commits 4a9ce0906, 8c5a5042a).
* čl. 28: 9 % on profit up to 100 000 EUR, 12 % from 100 000 to 1 500 000, 15 % above
* čl. 29 (125/2023): 15 % withheld from non-residents on dividends, interest, royalties, rents and fees for consulting, audit or market studies; 30 % for listed low-tax territories
-/

namespace MeGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Porez na dobit pravnih lica",   sched := Schedule.ofList [(0, 900), (100000, 1200), (1500000, 1500)] }

def wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "Zakon o porezu na dobit pravnih lica: 15 % (statute read, gap pass)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "15 % (statute read, gap pass)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "15 % (statute read, gap pass)" }] }

def citStatute : String := "Zakon o porezu na dobit pravnih lica (progressive 9 % / 12 % / 15 %)"

/-- Zakon o porezu na dobit pravnih lica (porez po odbitku) -/
def p9wht2 : Wht :=
  { name := "Porez po odbitku (usluge)", rules := [
    { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 1500, statute := "Zakon o porezu na dobit pravnih lica: 15 % withheld on consulting, market research and audit fees paid to non-residents" },   -- p18 services to individuals: cited 0 (no fixed base)
    { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 0, statute := "Zakon o porezu na dohodak fizičkih lica: services of a non-resident individual without a fixed base or permanent place of business are not taxed (cited 0)" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Porez na dobit pravnih lica", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Porez po odbitku (usluge) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["ME 1200: PwC, last reviewed 25 March 2025", "ME 1200 withholding pass 9 (services; companies): 2025-07-14 (grade B)", "ME 1200 pass 18: services of non-resident individuals not taxed without a fixed base (PwC 2025-03-22, grade B)", "ME gap pass: 1200 porez na dobit and porez po odbitku: 2025 text read (čl. 28-29), A"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && p.toCompany) then ["1200 withholding: services are taken as consulting, market research or audit services (others bear none)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && !p.toCompany) then ["1200 withholding: services of a non-resident individual booked at a cited 0 (no fixed base or permanent place of business taken)"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 9000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 117000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard (p9wht2.ruleFor { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 }).isSome

end MeGlobal.Corporate
