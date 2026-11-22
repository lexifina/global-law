import NlGlobal.Pit
import TaxKernel.Global2

/-!
# NL 2025: Vennootschapsbelasting (1200) and withholding on payments abroad

Source: wetten.overheid.nl, versions geldend 2025: Wet op de vennootschapsbelasting 1969 (`nl/law/vpb_g2025.html`), Wet op de dividendbelasting 1965 (`nl/law/divbel_g2025.html`); sha256 in `law/SHA256SUMS`.
* Wet Vpb art. 22: bracket table "€ 200.000 | 19%", above "25,8%"
* Wet DB art. 5: "De belasting bedraagt 15% van de opbrengst"

## FT review (2026-11-21, third pass): loss offset
Same wetten.overheid.nl text (g=2025-07-01, `nl/law/vpb_g2025.txt`), **art. 20 lid 2**: "Een verlies wordt verrekend met
de belastbare winsten ... van het voorafgaande jaar en de volgende jaren ... Daarbij vindt verrekening in een jaar
slechts plaats tot een bedrag van € 1.000.000 vermeerderd met 50% van de belastbare winst ... van dat jaar nadat die
winst ... is verminderd met een bedrag van € 1.000.000." The model offset losses in full.


## 1200 Bronbelasting (rente, royalty's): interest, royalty (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Netherlands, Corporate - Withholding taxes, accessed 2025-03-08 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty: interest and royalties 0 %, or 25,8 % in the conditional cases (related recipient in a low-tax or listed jurisdiction, abuse)


## 1200 Geen bronheffing op dienstvergoedingen (lichamen): services (pass 9, grade A)
Source: Wet op de vennootschapsbelasting 1969, wetten.overheid.nl, geldend van 01-01-2025 t/m 31-12-2025 (`nl/law/vpb_g2025.txt`).
* art. 17 lid 1: "Ten aanzien van buitenlandse belastingplichtigen wordt de belasting geheven naar het belastbare Nederlandse bedrag"
* art. 17 lid 3: the Dutch income is the sum of a. profit of an enterprise carried on with a permanent establishment or representative in the Netherlands, b. income from an abusive substantial interest, c. BES profit; a service fee of a foreign company without a Dutch establishment is none of these
* the Wet bronbelasting 2021 reaches interest, royalties and (from 2024) dividends only


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p8wht -> p10nlSw)
Source: Wet bronbelasting 2021 (BWBR0042952), wetten.overheid.nl, geldig op 01-07-2025 (`nl/law/wbb2021_g2025.txt`).
* art. 2.1 lid 1 a: liable is a body entitled to interest or royalties (art. 3.1) that is established in a low-tax jurisdiction; art. 1.2: a related body is one in which the payer has a kwalificerend belang (or which has one in the payer); a low-tax jurisdiction taxes profits at less than 9 % or appears on the Union list of jurisdictions that do not cooperate
* art. 4.1: "De belasting bedraagt het hoogste percentage, bedoeld in artikel 22 van de Wet op de vennootschapsbelasting 1969": 25,8 % in 2025
* the kwalificerend belang is read as a stake of at least 50 % (minStakeBp 5000); the lowTax flag as a jurisdiction on the ministerial list; dividends (art. 3.1 c, with dividendbelasting set off) are not modelled
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate


## 1200 Geen bronheffing op dienstvergoedingen (natuurlijke personen): services (pass 10, grade A)
Source: Wet inkomstenbelasting 2001 (BWBR0011353), wetten.overheid.nl, geldig op 01-07-2025 (`nl/law/ib2001_g2025.txt`).
* art. 7.1: the income tax of a buitenlandse belastingplichtige is levied on taxable income from work and home in the Netherlands, from a substantial interest in a Dutch company and from savings and investments in the Netherlands
* art. 7.2 lid 2: income from work and home in the Netherlands is the profit of a Dutch enterprise (permanent establishment or representative), wages for work done in the Netherlands, results from other work in the Netherlands and the listed benefits: all assessed, none withheld by the payer of a fee
* art. 7.2 lid 3: a performing artist or athlete of a non-treaty state on a short engagement is deemed to have a permanent establishment (loonbelasting artiestenregeling): not modelled
-/

namespace NlGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Vennootschapsbelasting",   sched := Schedule.ofList [(0, 1900), (200000, 2580)],   lossFull := 1000000, lossExcessBp := 5000 }

def wht : Wht :=
  { name := "Dividendbelasting", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "Wet op de dividendbelasting 1965 art. 5: 15%" }] }

def citStatute : String := "Wet Vpb 1969 art. 22 lid 1 (19 % tot € 200.000, 25,8 %); art. 20 lid 2 (verliesverrekening tot € 1.000.000 + 50 %)"

/-- Wet bronbelasting 2021 (conditional withholding on interest and royalties) -/
def p8wht : Wht :=
  { name := "Bronbelasting (rente, royalty's)", rules := [
    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Wet bronbelasting 2021: interest bears 25,8 % only when paid to a related entity in a low-tax or listed jurisdiction (or in abuse cases): none otherwise" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Wet bronbelasting 2021: royalties bear 25,8 % only when paid to a related entity in a low-tax or listed jurisdiction (or in abuse cases): none otherwise" }] }

/-- Wet op de vennootschapsbelasting 1969 art. 17 lid 1-3 -/
def p9wht2 : Wht :=
  { name := "Geen bronheffing op dienstvergoedingen (lichamen)", rules := [
    { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "Wet Vpb 1969 art. 17 lid 3: the Dutch income of a foreign company is profit of a Dutch enterprise (permanent establishment), an abusive substantial interest or BES profit: none on fees for services" }] }

/-- p8wht with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10nlSw : StateWht :=
  { name := p8wht.name, rules := [
     { rule := { kind := .interest, toCompany := some true, minStakeBp := 5000, rateBp := 2580, statute := "Wet bronbelasting 2021 art. 1.2 lid 1 (gelieerd, laagbelastende jurisdictie), 2.1 lid 1 a, 3.1, 4.1: 25,8 % (highest Vpb rate, art. 22 Wet Vpb 1969) on interest to a related body established in a low-tax jurisdiction" }, tests := [.lowTax true], ifUnknown := .general },    { rule := { kind := .royalty, toCompany := some true, minStakeBp := 5000, rateBp := 2580, statute := "Wet bronbelasting 2021 art. 1.2 lid 1 (gelieerd, laagbelastende jurisdictie), 2.1 lid 1 a, 3.1, 4.1: 25,8 % (highest Vpb rate, art. 22 Wet Vpb 1969) on royaltys to a related body established in a low-tax jurisdiction" }, tests := [.lowTax true], ifUnknown := .general }] ++ p8wht.rules.map StateRule.plain, round := p8wht.round }

/-- Wet inkomstenbelasting 2001 art. 7.1, 7.2 -/
def p10whti : Wht :=
  { name := "Geen bronheffing op dienstvergoedingen (natuurlijke personen)", rules := [
    { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 0, statute := "Wet IB 2001 art. 7.1, 7.2: a non-resident individual is assessed on Dutch income (profit of a Dutch enterprise, wages for work in the Netherlands, results from other work in the Netherlands); no tax is withheld on a fee for services" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Vennootschapsbelasting", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Bronbelasting (rente, royalty's) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10nlSw.charges g else []) },
   { name := "1200 Geen bronheffing op dienstvergoedingen (lichamen) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9wht2.charges g.company else []) },
   { name := "1200 Geen bronheffing op dienstvergoedingen (natuurlijke personen) (pass 10)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10whti.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["NL 1200: wetten.overheid.nl geldend 2025", "NL 1200 withholding pass 8 (interest, royalty): 2025-03-08 (grade B)", "NL 1200 withholding pass 9 (services; companies): wetten.overheid.nl, geldig op 01-07-2025 (`nl/law/vpb_g2025.txt`) (grade A)", "NL 1200 withholding by recipient state pass 10 (p8wht -> p10nlSw): wetten.overheid.nl, geldend op 1 juli 2025 (`nl/law/wbb2021_g2025.txt`)", "NL 1200 withholding pass 10 (services; individuals): wetten.overheid.nl, geldig op 1 juli 2025 (`nl/law/ib2001_g2025.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && p.toCompany) then ["1200 withholding: the recipient company is taken to have no permanent establishment in the Netherlands"] else [])
  ++ (if !(p10nlSw.notes g).isEmpty then ["1200 withholding: the 25,8 % of the Wet bronbelasting 2021 (related body in a low-tax jurisdiction) was not tested because lowTax is not given: none is booked"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && !p.toCompany) then ["1200 withholding: the recipient is taken as performing the services outside the Netherlands or without a Dutch enterprise; artists and athletes of non-treaty states (art. 7.2 lid 3; loonbelasting) are not separated"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 19000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 244400
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
-- art. 20 lid 2: profit 3 m, losses 10 m: offset 1 m + 50 % x 2 m = 2 m; taxable 1 m
#guard cit.citTax { profit := 3000000, lossesForward := 10000000 } == 244400
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard (p10nlSw.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } { lowTax := some true } 0).due == 25800
#guard (p10nlSw.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 0
#guard (p10nlSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 6000 } { lowTax := some false } 0).due == 0
#guard (p10nlSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 1000 } { lowTax := some true } 0).due == 0
#guard p10whti.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end NlGlobal.Corporate
