import CzGlobal.Pit
import TaxKernel.Global2

/-!
# CZ 2025: Daň z příjmů právnických osob (1200) and withholding on payments abroad

Source: zákon č. 586/1992 Sb., o daních z příjmů, wording in force 1 July 2025 (zakonyprolidi.cz, private publisher; `cz/law/zdp_zneni-20250701.html`); sha256 in `law/SHA256SUMS`.
* § 21 (1): "Sazba daně činí 21 %, pokud v odstavcích 2 a 3 není stanoveno jinak"
* § 36 (2): "Zvláštní sazba daně z příjmů pro poplatníky uvedené v § 2 a 17 ... činí 15 %" (35 % for residents of non-treaty states, § 36 (1))


## 1200 Srážková daň (služby): services (pass 8, grade A)
Source: Zákon o daních z příjmů 586/1992 Sb., zákony pro lidi, znění od 1.7.2025 (`cz/law/zdp_zneni-20250701.txt`).
* § 22 (1) c): Czech-source income of non-residents includes "příjmy ze služeb ... příjmy z obchodního, technického nebo jiného poradenství, řídicí a zprostředkovatelské činnosti a obdobných činností poskytovaných na území České republiky"
* § 36 (1) a) 1.: the special rate is 15 % on income under § 22 (1) c); c): 35 % for residents outside the EU/EEA without a treaty or exchange agreement


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: wht -> p10czSw)
Source: Zákon o daních z příjmů 586/1992 Sb., znění od 1. 7. 2025 (`cz/law/zdp_zneni-20250701.txt`).
* § 36 odst. 1 písm. c): "35 % z příjmů uvedených v písmenech a) a b), a to pro poplatníky, kteří nejsou daňovými rezidenty 1. jiného členského státu Evropské unie nebo dalšího státu tvořícího Evropský hospodářský prostor, nebo 2. třetího státu, se kterým má Česká republika uzavřenu mezinárodní smlouvu upravující zamezení dvojímu zdanění ... nebo ... výměnu informací"
* the rule needs both facts: euEea false and treaty false (the treaty flag is read as a treaty or tax-information agreement in force)
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p8wht2 -> p10czSw2)
Source: ZDP (`cz/law/zdp_zneni-20250701.txt`).
* services withheld under § 36 odst. 1 písm. a) bear 35 % under písm. c) for the same recipients
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate
-/

namespace CzGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Daň z příjmů právnických osob",   sched := Schedule.flat 2100 }

def wht : Wht :=
  { name := "Srážková daň (zvláštní sazba)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ZDP § 36 (2): zvláštní sazba 15 %" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ZDP § 36 (2): 15 %" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ZDP § 36 (2): 15 %" }] }

def citStatute : String := "zákon 586/1992 Sb. § 21 (1) (21 %)"

/-- ZDP § 22 odst. 1 písm. c), § 36 odst. 1 písm. a) bod 1 -/
def p8wht2 : Wht :=
  { name := "Srážková daň (služby)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "ZDP § 22 odst. 1 písm. c), § 36 odst. 1 písm. a) bod 1: 15 % on services provided in the Czech Republic (commercial, technical and other advisory, management, intermediation)" }] }

/-- wht with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10czSw : StateWht :=
  { name := wht.name, rules := [
     { rule := { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 3500, statute := "zákon 586/1992 Sb. § 36 odst. 1 písm. c): 35 % for recipients not resident in an EU/EEA state or a state with an implemented double-tax treaty or tax-information agreement" }, tests := [.euEea false, .treaty false], ifUnknown := .general },    { rule := { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 3500, statute := "zákon 586/1992 Sb. § 36 odst. 1 písm. c): 35 % for recipients not resident in an EU/EEA state or a state with an implemented double-tax treaty or tax-information agreement" }, tests := [.euEea false, .treaty false], ifUnknown := .general },    { rule := { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 3500, statute := "zákon 586/1992 Sb. § 36 odst. 1 písm. c): 35 % for recipients not resident in an EU/EEA state or a state with an implemented double-tax treaty or tax-information agreement" }, tests := [.euEea false, .treaty false], ifUnknown := .general }] ++ wht.rules.map StateRule.plain, round := wht.round }

/-- p8wht2 with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10czSw2 : StateWht :=
  { name := p8wht2.name, rules := [
     { rule := { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 3500, statute := "zákon 586/1992 Sb. § 36 odst. 1 písm. c): 35 % for recipients not resident in an EU/EEA state or a state with an implemented double-tax treaty or tax-information agreement" }, tests := [.euEea false, .treaty false], ifUnknown := .general }] ++ p8wht2.rules.map StateRule.plain, round := p8wht2.round }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Daň z příjmů právnických osob", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then p10czSw.charges g else []) },
   { name := "1200 Srážková daň (služby) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10czSw2.charges g else []) }]

def absent : List Absent :=
  []

def notes : List String := ["CZ 1200: znění k 1. 7. 2025 (zakonyprolidi.cz)", "CZ 1200 withholding pass 8 (services): zákon 586/1992 Sb., znění k 1.7.2025 (`cz/law/zdp_zneni-20250701.txt`) (grade A)", "CZ 1200 withholding by recipient state pass 10 (wht -> p10czSw): zákony pro lidi, znění od 1. 7. 2025 (`cz/law/zdp_zneni-20250701.txt`)", "CZ 1200 withholding by recipient state pass 10 (p8wht2 -> p10czSw2): zákony pro lidi, znění od 1. 7. 2025 (`cz/law/zdp_zneni-20250701.txt`)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as provided in the Czech Republic (§ 22 (1) c))"] else [])
  ++ (if !(p10czSw.notes g).isEmpty then ["1200 withholding: the 35 % of ZDP § 36 odst. 1 písm. c) (recipient outside the EU/EEA and without a treaty) was not tested because euEea or treaty is not given: 15 % is booked"] else [])
  ++ (if !(p10czSw2.notes g).isEmpty then ["1200 withholding: the 35 % of ZDP § 36 odst. 1 písm. c) on services was not tested because euEea or treaty is not given: 15 % is booked"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 21000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 210000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 15000
#guard (p10czSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 6000 } { euEea := some false, treaty := some false } 0).due == 35000
#guard (p10czSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 6000 } { euEea := some false } 0).due == 15000
#guard (p10czSw.chargeOf { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 6000 } { euEea := some true, treaty := some false } 0).due == 15000
#guard (p10czSw.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 15000
#guard (p10czSw2.chargeOf { kind := .services, amount := 100000, toCompany := true, stakeBp := 6000 } { euEea := some false, treaty := some false } 0).due == 35000
#guard (p10czSw2.chargeOf { kind := .services, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 15000

end CzGlobal.Corporate
