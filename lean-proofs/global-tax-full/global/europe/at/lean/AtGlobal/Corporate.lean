import AtGlobal.Pit

/-!
# AT 2025: Körperschaftsteuer (1200) and withholding on payments abroad

Source: RIS Bundesrecht konsolidiert, Fassung vom 01.07.2025: KStG 1988 (10004569, `at/law/kstg_2025-07-01.html`), EStG 1988 (10004570, `at/law/estg_2025-07-01.html`); sha256 in `law/SHA256SUMS`.
* KStG § 22 (1): "beträgt für das Kalenderjahr 2023 24% und für die Kalenderjahre ab 2024 23%"
* § 8 (4) Z 2: "Der Verlustabzug steht nur im Ausmaß von 75% des Gesamtbetrages der Einkünfte zu"
* § 10 (1): "Von der Körperschaftsteuer sind Beteiligungserträge befreit" (domestic participations; international Schachtelbeteiligungen from 10 %, § 10 (2), not separated)
* § 24 (4) Z 1: a Mindeststeuer "in Höhe von 5% eines Viertels der gesetzlichen Mindesthöhe des Grund- oder Stammkapitals" per quarter (GmbH: the GmbHG minimum of 10 000 euro, not read here, gives 500 euro a year)
* EStG § 27a (1) Z 2: capital income "in allen anderen Fällen einem besonderen Steuersatz von 27,5%" (KESt withheld under § 93)


## 1200 Abzugsteuer / KESt on payments abroad: interest, royalty, services (pass 8, grade A)
Source: EStG 1988, RIS Bundesrecht konsolidiert, Fassung vom 01.07.2025 (`at/law/estg_2025-07-01.txt`).
* § 100 (1): "Die Abzugsteuer gemäß § 99 beträgt 20%" (27,5 % only for § 99 (1) Z 6 and 7)
* § 99 (1) Z 3 royalties listed in § 28 (1) Z 3; Z 5 "Einkünften aus im Inland ausgeübter kaufmännischer oder technischer Beratung"
* § 98 (1) Z 5 lit. b: interest is limited-liability income only where KESt was withheld; excluded: "(Stück)Zinsen, die nicht von natürlichen Personen erzielt werden" and residents of automatic-exchange states
-/

namespace AtGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Körperschaftsteuer",   sched := Schedule.flat 2300,   lossFull := 0,   lossExcessBp := 7500,   participationBp := 10000,   participationMinBp := 0,   minFixed := 500 }

def wht : Wht :=
  { name := "withholding tax on payments abroad", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 2750, statute := "EStG 1988 § 27a (1) Z 2, § 93: KESt 27,5 %" }] }

def citStatute : String := "KStG 1988 § 22 (1) (23 % ab 2024), § 8 (4) Z 2 (75 %), § 10 (1), § 24 (4) Z 1 (Mindeststeuer)"

/-- EStG 1988 § 98 (1) Z 5 lit. b, § 99 (1) Z 3 and Z 5, § 100 (1) -/
def p8wht : Wht :=
  { name := "Abzugsteuer / KESt on payments abroad", rules := [
    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "EStG 1988 § 98 (1) Z 5 lit. b: interest of non-residents is taxable only where KESt was withheld (bank and securities interest), never for non-individuals or residents of states with automatic exchange of information: none on a company's loan interest" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "EStG 1988 § 99 (1) Z 3, § 100 (1): Abzugsteuer 20 % on royalties (§ 28 (1) Z 3)" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "EStG 1988 § 99 (1) Z 5, § 100 (1): Abzugsteuer 20 % on commercial or technical consulting carried out in Austria" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Körperschaftsteuer", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Abzugsteuer / KESt on payments abroad (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["AT 1200: RIS Fassung vom 01.07.2025", "AT 1200 withholding pass 8 (interest, royalty, services): RIS Fassung vom 01.07.2025 (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as commercial or technical consulting carried out in Austria (§ 99 (1) Z 5): other services, or consulting done abroad, bear none"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .royalty) then ["1200 withholding: § 99a exemption for royalties to associated EU companies not applied"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 23000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 230000
#guard cit.citTax { profit := 3000000, lossesForward := 5000000, turnover := 10000000 } == 172500
#guard cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 0 } == 600000
#guard cit.citTax { profit := 0, turnover := 10000000 } == 500
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 27500
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 20000

end AtGlobal.Corporate
