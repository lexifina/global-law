import EsGlobal.Pit
import TaxKernel.Global2

/-!
# ES 2025: Impuesto sobre Sociedades (1200) and withholding on payments abroad

Source: BOE legislación consolidada: Ley 27/2014 del Impuesto sobre Sociedades (`es/law/lis.html`), RDLeg 5/2004 TRLIRNR (`es/law/trlirnr.html`); current texts with BOE amendment notes; sha256 in `law/SHA256SUMS`.
* LIS art. 29.1: "El tipo general de gravamen para los contribuyentes de este Impuesto será el 25 por ciento"
* DT cuadragésima cuarta 1: "Con efectos para los períodos impositivos que se inicien dentro del año 2025": entities with turnover "inferior a 1 millón de euros": "i) ... entre 0 y 50.000 euros, al tipo del 21 por ciento. ii) Por la parte de base imponible restante, al tipo del 22 por ciento"; "b) Las entidades que cumplan las previsiones previstas en el artículo 101 de esta ley tributarán al 24 %"
* art. 26.1: compensation "con el límite del 70 por ciento de la base imponible previa"; "En todo caso, se podrán compensar ... hasta el importe de 1 millón de euros"
* art. 21: exemption of dividends from holdings of at least 5 % (95 % in effect after the 5 % of art. 21.10, not quoted)
* TRLIRNR art. 25.1: "a) Con carácter general el 24 por 100"; "f) El 19 por ciento cuando se trate de" dividends, interest and gains
* DT cuadragésima cuarta 1 b): "Las entidades que cumplan las previsiones previstas en el artículo 101 de esta ley tributarán al 24 %, salvo que deban tributar a un tipo diferente del general." (added by Ley 7/2024 disp. final 8.8, "con efectos para los períodos impositivos que se inicien a partir de 1 de enero de 2025"); art. 101.1: importe neto de la cifra de negocios of the previous period below 10 millones de euros


## 1200 IRNR retención (servicios): services (pass 8, grade A)
Source: Texto refundido de la Ley del IRNR, BOE consolidado (`es/law/trlirnr.txt`).
* art. 25.1 a): "Con carácter general el 24 por 100"; 19 por ciento for residents of another EU/EEA state with effective exchange of information
* art. 24.2: for services, technical assistance and installation work the base is income less personnel and material costs


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: wht -> p10esSw)
Source: TRLIRNR, BOE texto consolidado (`es/law/trlirnr.txt`).
* art. 25.1 a): "Con carácter general el 24 por 100. No obstante, el tipo de gravamen será el 19 por ciento cuando se trate de contribuyentes residentes en otro Estado miembro de la Unión Europea o del Espacio Económico Europeo con el que exista un efectivo intercambio de información tributaria"
* art. 14.1 c): interest obtained without a permanent establishment by residents of another EU member state or EEA state (EEA: with effective exchange of information) is exempt
* the euEea flag of the payment is read as residence in such a state; art. 14.1 h) (parent-subsidiary) stays out of scope
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p8wht2 -> p10esSw2)
Source: TRLIRNR, BOE texto consolidado (`es/law/trlirnr.txt`).
* services fall under the general rate of art. 25.1 a): 24 %, 19 % for EU/EEA residents
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate
-/

namespace EsGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Impuesto sobre Sociedades",   sched := Schedule.flat 2500,   smallTurnover := 999999,   smallSched := Schedule.ofList [(0, 2100), (50000, 2200)],   lossFull := 1000000,   lossExcessBp := 7000,   participationBp := 9500,   participationMinBp := 500 }

def wht : Wht :=
  { name := "Impuesto sobre la Renta de no Residentes (retención)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1900, statute := "TRLIRNR art. 25.1 f): 19 por ciento" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1900, statute := "TRLIRNR art. 25.1 f): 19 por ciento" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2400, statute := "TRLIRNR art. 25.1 a): con carácter general el 24 por 100" }] }

/-- LIS DT 44.ª 1 b): entidades de reducida dimensión (art. 101: turnover of the previous period below 10 millones) at 24 % in 2025. -/
def citErd : CorpRegime := { cit with name := "Impuesto sobre Sociedades (entidad de reducida dimensión)", sched := Schedule.flat 2400, smallSched := Schedule.flat 2400 }
/-- The scale in force for a company of turnover `t`: below 1 millón DT 44.ª 1 a), below 10 millones 1 b), else art. 29.1. -/
def citFor (t : Int) : CorpRegime := if 1000000 ≤ t ∧ t < 10000000 then citErd else cit

def citStatute : String := "Ley 27/2014 art. 29.1 (25 %), DT 44.ª 1 a) (2025: 21 % / 22 % microempresas), 1 b) (24 % entidades de reducida dimensión, art. 101: cifra de negocios < 10 millones), art. 26.1 (70 %, 1 millón), art. 21 (exención 95 %)"

/-- TRLIRNR (RDLeg. 5/2004) art. 13.1 b), 24.2, 25.1 a), 31 -/
def p8wht2 : Wht :=
  { name := "IRNR retención (servicios)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 2400, statute := "TRLIRNR art. 13.1 b), 25.1 a), 31: 24 % on services provided or used in Spain (19 % for EU/EEA residents)" }] }

/-- wht with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10esSw : StateWht :=
  { name := wht.name, rules := [
     { rule := { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "TRLIRNR (RDLeg. 5/2004) art. 14.1 c): interest of residents of another EU/EEA state (EEA: with effective exchange of information) is exempt" }, tests := [.euEea true], ifUnknown := .general },    { rule := { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1900, statute := "TRLIRNR (RDLeg. 5/2004) art. 25.1 a): 19 por ciento for residents of another EU/EEA state with effective exchange of information" }, tests := [.euEea true], ifUnknown := .general }] ++ wht.rules.map StateRule.plain, round := wht.round }

/-- p8wht2 with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10esSw2 : StateWht :=
  { name := p8wht2.name, rules := [
     { rule := { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1900, statute := "TRLIRNR art. 13.1 b), 25.1 a): 19 por ciento for residents of another EU/EEA state with effective exchange of information" }, tests := [.euEea true], ifUnknown := .general }] ++ p8wht2.rules.map StateRule.plain, round := p8wht2.round }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Impuesto sobre Sociedades", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [(citFor g.company.turnover).citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then p10esSw.charges g else []) },
   { name := "1200 IRNR retención (servicios) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10esSw2.charges g else []) }]

def absent : List Absent :=
  []

def notes : List String := ["ES 1200: BOE consolidado (2025 rates by DT 44.ª)", "ES 1200 withholding pass 8 (services): BOE texto consolidado (`es/law/trlirnr.txt`) (grade A)", "ES 1200 withholding by recipient state pass 10 (wht -> p10esSw): BOE texto consolidado (`es/law/trlirnr.txt`)", "ES 1200 withholding by recipient state pass 10 (p8wht2 -> p10esSw2): BOE texto consolidado (`es/law/trlirnr.txt`)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as provided or used in Spain; the art. 24.2 net base is not applied"] else [])
  ++ (if !(p10esSw.notes g).isEmpty then ["1200 withholding: a conditional rate of TRLIRNR art. 14.1 c) / 25.1 a) (EU/EEA resident) was not tested because euEea is not given: the general rate is booked"] else [])
  ++ (if !(p10esSw2.notes g).isEmpty then ["1200 withholding: the 19 % of TRLIRNR art. 25.1 a) on services (EU/EEA resident) was not tested because euEea is not given: 24 % is booked"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 25000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 250000
#guard cit.citTax { profit := 100000, turnover := 999999 } == 21500
#guard cit.citTax { profit := 100000, turnover := 1000000 } == 25000
#guard cit.citTax { profit := 3000000, lossesForward := 5000000, turnover := 10000000 } == 150000
#guard cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 500 } == 620000
#guard cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 499 } == 1000000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 19000
#guard wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 19000
#guard wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 24000
-- turnover 5 millones: 24 % (DT 44.ª 1 b)); 10 millones: 25 % (art. 29.1); 999 999: 21 % / 22 % (1 a))
#guard (citFor 5000000).citTax { profit := 1000000, turnover := 5000000 } == 240000
#guard (citFor 1000000).citTax { profit := 100000, turnover := 1000000 } == 24000
#guard (citFor 10000000).citTax { profit := 1000000, turnover := 10000000 } == 250000
#guard (citFor 999999).citTax { profit := 100000, turnover := 999999 } == 21500
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 24000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 24000
#guard (p10esSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 6000 } { euEea := some true } 0).due == 19000
#guard (p10esSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 24000
#guard (p10esSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 6000 } { euEea := some false } 0).due == 24000
#guard (p10esSw.chargeOf { kind := .interest, amount := 100000, toCompany := false, stakeBp := 6000 } { euEea := some true } 0).due == 0
#guard (p10esSw.chargeOf { kind := .interest, amount := 100000, toCompany := false, stakeBp := 6000 } {  } 0).due == 19000
#guard (p10esSw2.chargeOf { kind := .services, amount := 100000, toCompany := true, stakeBp := 6000 } { euEea := some true } 0).due == 19000
#guard (p10esSw2.chargeOf { kind := .services, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 24000

end EsGlobal.Corporate
