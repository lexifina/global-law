import RoGlobal.Pit
import TaxKernel.Global2

/-!
# RO 2025: Impozit pe profit (1200) and withholding on payments abroad

Source: Codul fiscal art. 17 as in force on 2025-03-01, the copy kept by the 1.x model (`ro/law/art-017_2025-03-01.txt`, a Global law record read before the MCP stop, pointing to legislatie.just.ro DetaliiDocument/171282); sha256 in `law/SHA256SUMS`.
* art. 17: "Cota de impozit pe profit care se aplică asupra profitului impozabil este de 16%"


## 1200 Impozit pe veniturile nerezidenților: dividend, interest, royalty, services (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Romania, Corporate - Withholding taxes, accessed 2025-06-24 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* 16 % on interest, royalties, services rendered in Romania and management/consultancy services wherever rendered; dividends to non-residents 10 %; 50 % to states without exchange of information (not applied)


## 1200 Impozit pe veniturile obținute din România de nerezidenți: dividend, interest, royalty, services (pass 9, grade A)
Source: Codul fiscal (Legea nr. 227/2015), consolidated text via the Internet Archive, 2025-05-02 (`ro/law/cf_wb20250502.txt`).
* art. 224 (1): the tax due by non-residents on income obtained from Romania "se calculează, se reține, se declară și se plătește la bugetul de stat de către plătitorii de venituri"
* art. 224 (4): "b) 10% pentru veniturile din dividende"; "d) 16% în cazul oricăror altor venituri impozabile obținute din România"; c) 50% for payments to accounts in states without an information-exchange instrument (artificial transactions); c^1) 10% for individuals resident in the EU or a treaty state
* art. 223 (1): Romanian-source income includes dividends, interest and royalties from a resident, management or consultancy services from a resident (i) and services performed in Romania except international transport (k)


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p9wht -> p10roSw)
Source: Codul fiscal (Legea 227/2015), text via the Internet Archive 2025-05-02 (`ro/law/cf_wb20250502.txt`).
* art. 224 alin. (4) lit. c^1): "10% în cazul veniturilor impozabile enumerate la art. 223 alin. (1) lit. b)-i) și k)-p) obținute din România de persoane fizice rezidente într-un stat membru al Uniunii Europene sau într-un stat cu care România are încheiată o convenție de evitare a dublei impuneri"
* either fact suffices (two rules: euEea true, treaty true); the euEea flag also covers the EEA states outside the EU, all of which are read as treaty states
* lit. c): 50 % on payments to a state without an information-exchange instrument applies only to transactions qualified as artificial (art. 11 alin. (3)): not in the input, not modelled
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate
-/

namespace RoGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Impozit pe profit",   sched := Schedule.flat 1600 }

def citStatute : String := "Codul fiscal (Legea nr. 227/2015) art. 17 (16 %)"

/-- Codul fiscal art. 223-224 -/
def p8wht : Wht :=
  { name := "Impozit pe veniturile nerezidenților", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Codul fiscal art. 224 (4): dividends 10 % (2025)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1600, statute := "Codul fiscal art. 223, 224 (4): interest 16 %" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1600, statute := "Codul fiscal art. 223, 224 (4): royalties 16 %" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1600, statute := "Codul fiscal art. 223 (2): services rendered in Romania and management/consultancy services 16 %" }] }

/-- Legea 227/2015 privind Codul fiscal art. 223 (1), art. 224 (1), (4) -/
def p9wht : Wht :=
  { name := "Impozit pe veniturile obținute din România de nerezidenți", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Codul fiscal art. 223 (1) a), art. 224 (4) b): 10% on dividends (OUG 156/2024, dividends distributed after 1.1.2025)" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1600, statute := "Codul fiscal art. 223 (1) b), art. 224 (4) d): 16% on interest from a resident" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1600, statute := "Codul fiscal art. 223 (1) d), art. 224 (4) d): 16% on royalties from a resident" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1600, statute := "Codul fiscal art. 223 (1) i), k), art. 224 (4) d): 16% on management or consultancy services from a resident and on services performed in Romania" }] }

/-- p9wht with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10roSw : StateWht :=
  { name := p9wht.name, rules := [
     { rule := { kind := .interest, toCompany := some false, minStakeBp := 0, rateBp := 1000, statute := "Codul fiscal art. 224 alin. (4) lit. c^1): 10 % on income of art. 223 alin. (1) lit. b)-i), k)-p) of individuals resident in an EU member state or a state with a double-tax convention with Romania" }, tests := [.euEea true], ifUnknown := .general },    { rule := { kind := .interest, toCompany := some false, minStakeBp := 0, rateBp := 1000, statute := "Codul fiscal art. 224 alin. (4) lit. c^1): 10 % on income of art. 223 alin. (1) lit. b)-i), k)-p) of individuals resident in an EU member state or a state with a double-tax convention with Romania" }, tests := [.treaty true], ifUnknown := .general },    { rule := { kind := .royalty, toCompany := some false, minStakeBp := 0, rateBp := 1000, statute := "Codul fiscal art. 224 alin. (4) lit. c^1): 10 % on income of art. 223 alin. (1) lit. b)-i), k)-p) of individuals resident in an EU member state or a state with a double-tax convention with Romania" }, tests := [.euEea true], ifUnknown := .general },    { rule := { kind := .royalty, toCompany := some false, minStakeBp := 0, rateBp := 1000, statute := "Codul fiscal art. 224 alin. (4) lit. c^1): 10 % on income of art. 223 alin. (1) lit. b)-i), k)-p) of individuals resident in an EU member state or a state with a double-tax convention with Romania" }, tests := [.treaty true], ifUnknown := .general },    { rule := { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 1000, statute := "Codul fiscal art. 224 alin. (4) lit. c^1): 10 % on income of art. 223 alin. (1) lit. b)-i), k)-p) of individuals resident in an EU member state or a state with a double-tax convention with Romania" }, tests := [.euEea true], ifUnknown := .general },    { rule := { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 1000, statute := "Codul fiscal art. 224 alin. (4) lit. c^1): 10 % on income of art. 223 alin. (1) lit. b)-i), k)-p) of individuals resident in an EU member state or a state with a double-tax convention with Romania" }, tests := [.treaty true], ifUnknown := .general }] ++ p9wht.rules.map StateRule.plain, round := p9wht.round }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Impozit pe profit", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Impozit pe veniturile obținute din România de nerezidenți (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10roSw.charges g else []) }]

def absent : List Absent :=
  []

def notes : List String := ["RO 1200: art. 17 as in force 2025-03-01 (unchanged since 2016)", "RO 1200 withholding pass 9 (dividend, interest, royalty, services; all recipients): Internet Archive capture 2025-05-02 of the consolidated Code (`ro/law/cf_wb20250502.txt`) (grade A)", "RO 1200 withholding by recipient state pass 10 (p9wht -> p10roSw): Internet Archive 2025-05-02 (`ro/law/cf_wb20250502.txt`)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as management or consultancy services or services performed in Romania (art. 223 (1) i), k))"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => !p.toCompany) then ["1200 withholding: the 10% rate for individuals resident in the EU or a treaty state (art. 224 (4) c^1)) is not applied: the input does not give the recipient's state"] else [])
  ++ (if g.entity == .company && !g.company.paymentsAbroad.isEmpty then ["1200 withholding: the 50% rate (art. 224 (4) c)) and the EU directive exemptions are not applied"] else [])
  ++ (if !(p10roSw.notes g).isEmpty then ["1200 withholding: the 10 % of Codul fiscal art. 224 alin. (4) lit. c^1) (individual resident in the EU or a treaty state) was not tested because euEea and treaty are not given: 16 % is booked"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 16000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 160000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 10000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 16000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 16000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 16000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 16000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 16000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 16000
#guard p9wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p9wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 10000
#guard p9wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 16000
#guard p9wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 16000
#guard p9wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 16000
#guard p9wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 16000
#guard p9wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 16000
#guard p9wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 16000
#guard (p10roSw.chargeOf { kind := .interest, amount := 100000, toCompany := false, stakeBp := 6000 } { euEea := some true } 0).due == 10000
#guard (p10roSw.chargeOf { kind := .interest, amount := 100000, toCompany := false, stakeBp := 6000 } { euEea := some false, treaty := some true } 0).due == 10000
#guard (p10roSw.chargeOf { kind := .interest, amount := 100000, toCompany := false, stakeBp := 6000 } {  } 0).due == 16000
#guard (p10roSw.chargeOf { kind := .services, amount := 100000, toCompany := true, stakeBp := 6000 } { euEea := some true } 0).due == 16000

end RoGlobal.Corporate
