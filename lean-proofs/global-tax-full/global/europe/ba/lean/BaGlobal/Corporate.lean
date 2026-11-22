import BaGlobal.Pit

/-!
# BA 2025: Porez na dobit (Federacija BiH) (1200) and withholding on payments abroad

Source: PwC Worldwide Tax Summaries, Bosnia and Herzegovina, Corporate - Taxes on corporate income, accessed 2026-11-21 (live page reviewed 23 September 2026, no 2025 capture; `ba/law/pwc_cit_live.html`); Corporate - Withholding taxes, accessed 2025-07-18 (Wayback capture; `ba/law/pwc_wht_wb2025.html`); sha256 in `law/SHA256SUMS`.
* CIT 10 % in each of the Federation of BiH, Republika Srpska and Brčko District
* WHT (FBiH): dividends 5 %; interest, royalties, other 10 %; Republika Srpska 10 % (PwC page reviewed 6 February 2025)


## 1200 Porez po odbitku (usluge, FBiH): services (pass 9, grade B)
Source: PwC Worldwide Tax Summaries, Bosnia and Herzegovina, Corporate - Withholding taxes, accessed 2025-07-18 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* FBiH: tax is withheld at 10 % on fees for management, technical and educational services, market research, tax advice, audit and consulting paid to non-resident legal entities (5 % on dividends; 10 % on interest and royalties)
* other service fees are within the tax only when the recipient's state has no treaty with Bosnia and Herzegovina; Republika Srpska and Brčko District each withhold 10 % on their own lists


## 1200 services of non-resident individuals (pass 18, grade B)
Source: PwC Worldwide Tax Summaries, Bosnia and Herzegovina, its page on taxes on personal income (individuals), Internet Archive 2025-02-16 (`ba/law/pwc_indpit_wb20250216.*`), facts only.
* Zakon o porezu na dohodak FBiH (PwC 2025: a non-resident pays FBiH income tax on independent activity only through a permanent place of business there; dependent activity in FBiH and income from property, royalties and capital investments in FBiH are taxed): a fee for services paid to a non-resident individual who has no fixed base there is not taxed (cited 0 rule)
-/

namespace BaGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Porez na dobit (Federacija BiH)",   sched := Schedule.flat 1000 }

def wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 500, statute := "Zakon o porezu na dobit FBiH: 5 % on dividends (PwC 2025)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (PwC 2025)" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "10 % (PwC 2025)" }] }

def citStatute : String := "Zakon o porezu na dobit (FBiH; also Republika Srpska and Brčko District): 10 %"

/-- Zakon o porezu na dobit Federacije BiH (porez po odbitku) -/
def p9wht2 : Wht :=
  { name := "Porez po odbitku (usluge, FBiH)", rules := [
    { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 1000, statute := "Zakon o porezu na dobit FBiH: 10 % withheld on management, technical, educational and consulting service fees paid to non-residents" },   -- p18 services to individuals: cited 0 (no fixed base)
    { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 0, statute := "Zakon o porezu na dohodak FBiH: services of a non-resident individual without a fixed base or permanent place of business are not taxed (cited 0)" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Porez na dobit (Federacija BiH)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Porez po odbitku (usluge, FBiH) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["BA 1200: PwC (CIT page reviewed 2026: the 10 % in all three entities is long-standing; WHT page reviewed February 2025)", "BA 1200 withholding pass 9 (services; companies): 2025-07-18 (grade B)", "BA 1200 pass 18: services of non-resident individuals not taxed without a fixed base (PwC 2025-02-16, grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && p.toCompany) then ["1200 withholding: services are taken as management, technical or consulting services (other services only for non-treaty residents)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && !p.toCompany) then ["1200 withholding: services of a non-resident individual booked at a cited 0 (no fixed base or permanent place of business taken)"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 10000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 100000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 5000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard (p9wht2.ruleFor { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 }).isSome

end BaGlobal.Corporate
