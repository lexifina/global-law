import SkGlobal.Pit
import TaxKernel.Global2

/-!
# SK 2025: Daň z príjmov právnickej osoby (1200) and withholding on payments abroad

Source: Slov-Lex (official) static consolidation in force from 1 January 2025 of zákon 595/2003 Z. z. o dani z príjmov (`sk/law/dp_20250101.html`); sha256 in `law/SHA256SUMS`.
* § 15 písm. b): "1a. 10 % pre daňovníka, ktorý dosiahol za zdaňovacie obdobie zdaniteľné príjmy (výnosy) neprevyšujúce sumu 100 000 eur, 1b. 21 % pre daňovníka neuvedeného v bode 1a. alebo bode 1c., 1c. 24 % pre daňovníka, ktorý dosiahol ... prevyšujúce sumu 5 000 000 eur"

## FT review (2026-11-21, third pass): the 24 % band
Same consolidation (`sk/law/dp_20250101.txt`), **§ 15 písm. b) bod 1c.**: "24 % pre daňovníka, ktorý dosiahol za
zdaňovacie obdobie zdaniteľné príjmy (výnosy) prevyšujúce sumu 5 000 000 eur". The model cited 1c but applied 21 %
(1b) to every taxpayer above the 1a threshold. Taxable revenues are read as the company's turnover, as for 1a.


## 1200 Daň vyberaná zrážkou (úroky, licenčné poplatky): dividend, interest, royalty (pass 8, grade A)
Source: Zákon o dani z príjmov 595/2003 Z.z., Slov-Lex znenie od 1.1.2025 (`sk/law/dp_20250101.txt`).
* § 43 (1): "Daň sa vyberá zrážkou vo výške a) 7 % z príjmov podľa odseku 3 písm. r) a s) ..., b) 19 % z príjmov podľa odsekov 2 a 3 ..., c) 35 %" to non-cooperative states
* § 43 (2): withheld on income of non-residents under § 16 (1) c) to e) items 1, 2, 4, 10, 12 and on interest from loans and credits


## 1200 Daň vyberaná zrážkou (služby, dividendy právnickým osobám): dividend, services (pass 9, grade A)
Source: Zákon o dani z príjmov 595/2003 Z.z., Slov-Lex znenie od 1.1.2025 (`sk/law/dp_20250101.txt`).
* § 16 ods. 1 písm. c): Slovak-source income of non-residents includes services, among them commercial, technical or other advisory, management and intermediation, provided in the territory of the Slovak Republic, even without a permanent establishment
* § 43 ods. 2: the tax on income under § 16 ods. 1 písm. c) to e) items 1, 2, 4, 10 and 12 is collected by withholding; § 43 ods. 1 písm. b): "19 % z príjmov podľa odsekov 2 a 3"
* § 12 ods. 7 písm. c): "Predmetom dane nie je ... podiel na zisku (dividenda)" of a company, except where paid to or from a taxpayer of a non-cooperative state


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p8wht -> p10skSw)
Source: Zákon o dani z príjmov 595/2003 Z. z., Slov-Lex (`sk/law/dp_20250101.txt`).
* § 43 ods. 1 písm. c): "35 % z príjmov podľa odsekov 2 a 3, ak sú tieto príjmy vyplatené, poukázané alebo pripísané daňovníkovi nespolupracujúceho štátu podľa § 2 písm. x)"
* the nonCooperative flag of the payment is read as a non-cooperative state of § 2 písm. x)
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p9wht2 -> p10skSw2)
Source: ZDP SK (`sk/law/dp_20250101.txt`).
* § 12 ods. 7 písm. c): a dividend paid to a legal entity is not subject unless paid to a taxpayer of a non-cooperative state, where § 43 ods. 1 písm. c) takes 35 %
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate
-/

namespace SkGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Daň z príjmov právnickej osoby",   sched := Schedule.flat 2100,   smallTurnover := 100000,   smallSched := Schedule.flat 1000 }

def citStatute : String := "zákon 595/2003 Z. z. § 15 písm. b) bod 1a (10 %), 1b (21 %), 1c (24 %)"

/-- § 15 písm. b) bod 1c.: 24 % where taxable revenues exceed 5 000 000 eur (FT review, third pass) -/
def citLarge : CorpRegime :=
  { name := "Daň z príjmov právnickej osoby",   sched := Schedule.flat 2400 }

/-- zákon 595/2003 Z.z. § 16 ods. 1 písm. e), § 43 ods. 1-3 -/
def p8wht : Wht :=
  { name := "Daň vyberaná zrážkou (úroky, licenčné poplatky)", rules := [
    { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1900, statute := "zákon 595/2003 § 43 ods. 1 písm. b), ods. 2: 19 % on interest on loans and credits" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1900, statute := "zákon 595/2003 § 16 ods. 1 písm. e) body 1-2, § 43 ods. 1 písm. b), ods. 2: 19 % on royalties" },   { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 700, statute := "zákon 595/2003 § 43 ods. 1 písm. a), ods. 3 písm. r): 7 % on dividends paid to individuals" }] }

/-- zákon 595/2003 Z.z. § 12 ods. 7 písm. c), § 16 ods. 1 písm. c), § 43 ods. 1-2 -/
def p9wht2 : Wht :=
  { name := "Daň vyberaná zrážkou (služby, dividendy právnickým osobám)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1900, statute := "zákon 595/2003 § 16 ods. 1 písm. c), § 43 ods. 1 písm. b), ods. 2: 19 % on services provided in Slovakia" },   { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "zákon 595/2003 § 12 ods. 7 písm. c): a profit share paid to a legal entity is not subject to tax (except to non-cooperative states): none" }] }

/-- p8wht with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10skSw : StateWht :=
  { name := p8wht.name, rules := [
     { rule := { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 3500, statute := "zákon 595/2003 Z. z. § 43 ods. 1 písm. c): 35 % of income paid to a taxpayer of a non-cooperative state (§ 2 písm. x))" }, tests := [.nonCooperative true], ifUnknown := .general },    { rule := { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 3500, statute := "zákon 595/2003 Z. z. § 43 ods. 1 písm. c): 35 % of income paid to a taxpayer of a non-cooperative state (§ 2 písm. x))" }, tests := [.nonCooperative true], ifUnknown := .general },    { rule := { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 3500, statute := "zákon 595/2003 Z. z. § 43 ods. 1 písm. c): 35 % of income paid to a taxpayer of a non-cooperative state (§ 2 písm. x))" }, tests := [.nonCooperative true], ifUnknown := .general }] ++ p8wht.rules.map StateRule.plain, round := p8wht.round }

/-- p9wht2 with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10skSw2 : StateWht :=
  { name := p9wht2.name, rules := [
     { rule := { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 3500, statute := "zákon 595/2003 Z. z. § 43 ods. 1 písm. c): 35 % of income paid to a taxpayer of a non-cooperative state (§ 2 písm. x))" }, tests := [.nonCooperative true], ifUnknown := .general },    { rule := { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 3500, statute := "zákon 595/2003 Z. z. § 12 ods. 7 písm. c) (a profit share paid to a non-cooperative state is subject), § 43 ods. 1 písm. c): 35 %" }, tests := [.nonCooperative true], ifUnknown := .general }] ++ p9wht2.rules.map StateRule.plain, round := p9wht2.round }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Daň z príjmov právnickej osoby", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [(if g.company.turnover > 5000000 then citLarge else cit).citCharge g.company citStatute] else []) },
   { name := "1200 Daň vyberaná zrážkou (úroky, licenčné poplatky) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10skSw.charges g else []) },
   { name := "1200 Daň vyberaná zrážkou (služby, dividendy právnickým osobám) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10skSw2.charges g else []) }]

def absent : List Absent :=
  []

def notes : List String := ["SK 1200: Slov-Lex znenie od 1. 1. 2025", "SK 1200 withholding pass 8 (dividend, interest, royalty): znenie od 1.1.2025 (`sk/law/dp_20250101.txt`) (grade A)", "SK 1200 withholding pass 9 (dividend, services; companies): znenie od 1.1.2025 (`sk/law/dp_20250101.txt`) (grade A)", "SK 1200 withholding by recipient state pass 10 (p8wht -> p10skSw): Slov-Lex, znenie od 1. 1. 2025 (`sk/law/dp_20250101.txt`)", "SK 1200 withholding by recipient state pass 10 (p9wht2 -> p10skSw2): Slov-Lex, znenie od 1. 1. 2025 (`sk/law/dp_20250101.txt`)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest || p.kind == .royalty) then ["1200 withholding: the EU exemption (§ 13 ods. 1 písm. e)) not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as provided in Slovakia (§ 16 ods. 1 písm. c))"] else [])
  ++ (if !(p10skSw.notes g).isEmpty then ["1200 withholding: the 35 % of § 43 ods. 1 písm. c) (non-cooperative state) was not tested because nonCooperative is not given: the general rate is booked"] else [])
  ++ (if !(p10skSw2.notes g).isEmpty then ["1200 withholding: the 35 % on services and dividends to a non-cooperative state (§ 12 ods. 7 písm. c), § 43 ods. 1 písm. c)) was not tested because nonCooperative is not given: the general rate is booked"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 21000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 210000
#guard cit.citTax { profit := 100000, turnover := 100000 } == 10000
#guard cit.citTax { profit := 100000, turnover := 100001 } == 21000
#guard citLarge.citTax { profit := 1000000, turnover := 5000001 } == 240000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 19000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 19000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 19000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 19000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 7000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 19000
#guard p9wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 19000
#guard p9wht2.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard (p10skSw.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } { nonCooperative := some true } 0).due == 35000
#guard (p10skSw.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 19000
#guard (p10skSw.chargeOf { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 6000 } { nonCooperative := some true } 0).due == 35000
#guard (p10skSw.chargeOf { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 6000 } { nonCooperative := some false } 0).due == 7000
#guard (p10skSw2.chargeOf { kind := .services, amount := 100000, toCompany := true, stakeBp := 6000 } { nonCooperative := some true } 0).due == 35000
#guard (p10skSw2.chargeOf { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 6000 } { nonCooperative := some true } 0).due == 35000
#guard (p10skSw2.chargeOf { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 0

end SkGlobal.Corporate
