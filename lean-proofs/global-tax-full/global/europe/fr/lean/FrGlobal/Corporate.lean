import FrGlobal.Pit
import TaxKernel.Global2

/-!
# FR 2025: Impôt sur les sociétés (1200) and withholding on payments abroad

Source: CGI article copies of the 1.x French model (`fr/law/y2025/219.md` version 2026-02-21, `209.md` version 2023-12-31, `216.md` version 2023-12-31; Légifrance blocked); sha256 in `law/SHA256SUMS`.
* art. 219 I: "Le taux normal de l'impôt est fixé à 25 %"; b: 15 % up to "42 500 € de bénéfice imposable par période de douze mois" for companies with turnover under "10 000 000" €
* art. 209 I: losses deductible up to "1 000 000 € majoré de 50 % du montant correspondant au bénéfice imposable dudit exercice excédant ce premier montant"
* art. 216: the exempt dividends bear a share of costs of "5 % du produit total des participations" (holding ≥ 5 %, art. 145, not read)


## 1200 Retenue à la source (art. 182 B): royalty, services (pass 8, grade A)
Source: Code général des impôts art. 182 B, Légifrance, Wayback capture 2024-12-01 (`fr/law/cgi_182B_wb.txt`).
* I: withholding on sums paid by a debtor operating in France to persons without a permanent establishment there: b. inventors' and copyright income and products of industrial or commercial property; c. "Les sommes payées en rémunération des prestations de toute nature fournies ou utilisées en France"
* II: "Le taux de la retenue est celui prévu au deuxième alinéa du I de l'article 219" (25 %); III: 75 % for non-cooperative states (not applied)


## 1200 Retenue / prélèvement (dividendes, intérêts): dividend, interest (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, France, Corporate - Withholding taxes, accessed 2025-06-16 (Wayback capture; `law/pwc_wht_wb2025.txt`); CGI art. 125 A, Légifrance Wayback 2024-12-07 (`fr/law/cgi_125A_wb.txt`).
* dividends: 25 % to companies (0 % under the parent-subsidiary rules), 12,8 % to individuals (art. 187)
* interest: no withholding since 1 March 2010 except payments to non-cooperative states (art. 125 A III: prélèvement on payments to those states)


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p8wht -> p10frSw)
Source: CGI art. 182 B (`fr/law/cgi_182B_wb.txt`).
* art. 182 B III: "Le taux de la retenue est porté à 75 % lorsque les sommes et produits, autres que les salaires, mentionnés au I sont payés à des personnes domiciliées ou établies dans un Etat ou territoire non coopératif au sens de l'article 238-0 A" (except those of its 2 bis 2°), save where the payer proves the operations are real
* the nonCooperative flag is read as a state or territory on the art. 238-0 A list (other than 2 bis 2°); the safe-harbour proof is not in the input
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate


## 1200 withholding by the recipient's state (pass 10, kernel 2.4.0 StateWht: p8wht2 -> p10frSw2)
Source: CGI art. 125 A (`fr/law/cgi_125A_wb.txt`).
* art. 125 A III: the prélèvement applies at 75 % to interest paid outside France in a non-cooperative state or territory; other interest paid to non-residents bears none
* dividends to non-cooperative states (CGI art. 119 bis 2, 75 %) are not modelled: the article's 2025 text is not on disk
* an absent recipient fact books the general rate and lists the payment as unsupported (ifUnknown := .general); never a silent conditional rate
-/

namespace FrGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Impôt sur les sociétés",   sched := Schedule.flat 2500,   smallTurnover := 9999999,   smallSched := Schedule.ofList [(0, 1500), (42500, 2500)],   lossFull := 1000000,   lossExcessBp := 5000,   participationBp := 9500,   participationMinBp := 500 }

def citStatute : String := "CGI art. 219 I (25 %; b: 15 % jusqu'à 42 500 €, CA < 10 M€), art. 209 I (1 000 000 € + 50 %), art. 216 (quote-part 5 %)"

/-- CGI art. 182 B I b et c, II -/
def p8wht : Wht :=
  { name := "Retenue à la source (art. 182 B)", rules := [
    { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2500, statute := "CGI art. 182 B I b, II (taux de l'art. 219 I, 25 %)" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 2500, statute := "CGI art. 182 B I c, II: 25 % on services of any kind provided or used in France" }] }

/-- CGI art. 119 bis 1-2, 125 A III, 187 -/
def p8wht2 : Wht :=
  { name := "Retenue / prélèvement (dividendes, intérêts)", rules := [
    { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 2500, statute := "CGI art. 119 bis 2, art. 219 I: 25 % on dividends to non-resident companies" },   { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 1280, statute := "CGI art. 187 1-2°: 12,8 % on dividends to non-resident individuals" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "CGI art. 125 A III, art. 119 bis 1: interest paid abroad is exempt, except to non-cooperative states" }] }

/-- p8wht with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10frSw : StateWht :=
  { name := p8wht.name, rules := [
     { rule := { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 7500, statute := "CGI art. 182 B III: 75 % where paid to persons whose domicile or establishment is in a state or territory listed as non-cooperative (art. 238-0 A, other than those of its 2 bis 2°), unless the payer shows the payments are not artificial" }, tests := [.nonCooperative true], ifUnknown := .general },    { rule := { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 7500, statute := "CGI art. 182 B III: 75 % where paid to persons whose domicile or establishment is in a state or territory listed as non-cooperative (art. 238-0 A, other than those of its 2 bis 2°), unless the payer shows the payments are not artificial" }, tests := [.nonCooperative true], ifUnknown := .general }] ++ p8wht.rules.map StateRule.plain, round := p8wht.round }

/-- p8wht2 with the recipient-state rules (kernel 2.4.0 StateWht; an absent fact books the general rate) -/
def p10frSw2 : StateWht :=
  { name := p8wht2.name, rules := [
     { rule := { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 7500, statute := "CGI art. 125 A III: 75 % on interest paid outside France in a non-cooperative state or territory (art. 238-0 A)" }, tests := [.nonCooperative true], ifUnknown := .general }] ++ p8wht2.rules.map StateRule.plain, round := p8wht2.round }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Impôt sur les sociétés", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Retenue à la source (art. 182 B) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10frSw.charges g else []) },
   { name := "1200 Retenue / prélèvement (dividendes, intérêts) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10frSw2.charges g else []) }]

def absent : List Absent :=
  []

def notes : List String := ["FR 1200: CGI copies (219 in its 2026-02-21 version; 209, 216 versions in force 2025)", "FR 1200 withholding pass 8 (royalty, services): Légifrance, Wayback capture 2024-12-01 (`fr/law/cgi_182B_wb.txt`) (grade A)", "FR 1200 withholding pass 8 (dividend, interest): 2025-06-16 (grade B)", "FR 1200 withholding by recipient state pass 10 (p8wht -> p10frSw): Légifrance via the Internet Archive (`fr/law/cgi_182B_wb.txt`)", "FR 1200 withholding by recipient state pass 10 (p8wht2 -> p10frSw2): Légifrance via the Internet Archive (`fr/law/cgi_125A_wb.txt`)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as provided or used in France"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .royalty) then ["1200 withholding: the art. 182 B exemption for EU associated companies (art. 182 B II bis) not applied"] else [])
  ++ (if !(p10frSw.notes g).isEmpty then ["1200 withholding: the 75 % of CGI art. 182 B III (non-cooperative state or territory) was not tested because nonCooperative is not given: 25 % is booked"] else [])
  ++ (if !(p10frSw2.notes g).isEmpty then ["1200 withholding: the 75 % of CGI art. 125 A III on interest (non-cooperative state or territory) was not tested because nonCooperative is not given: none is booked"] else [])

#guard cit.citTax { profit := 100000, turnover := 29999997 } == 25000
#guard cit.citTax { profit := 1000000, turnover := 29999997 } == 250000
#guard cit.citTax { profit := 100000, turnover := 9999999 } == 20750
#guard cit.citTax { profit := 100000, turnover := 10000000 } == 25000
#guard cit.citTax { profit := 3000000, lossesForward := 5000000, turnover := 29999997 } == 250000
#guard cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 500 } == 620000
#guard cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 499 } == 1000000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 25000
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 12800
#guard p8wht2.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht2.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard (p10frSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 6000 } { nonCooperative := some true } 0).due == 75000
#guard (p10frSw.chargeOf { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 25000
#guard (p10frSw2.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } { nonCooperative := some true } 0).due == 75000
#guard (p10frSw2.chargeOf { kind := .interest, amount := 100000, toCompany := true, stakeBp := 6000 } {  } 0).due == 0

end FrGlobal.Corporate
