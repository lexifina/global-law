import PtGlobal.Pit

/-!
# PT 2025: Imposto sobre o Rendimento das Pessoas Coletivas (1200) and withholding on payments abroad

Source: Lei n.º 45-A/2024 (Orçamento do Estado para 2025), Diário da República PDF kept by the 1.x model (`pt/law/Lei_45_A_2024.pdf`), which restates CIRC art. 87.º; sha256 in `law/SHA256SUMS`.
* CIRC art. 87.º: "1 - A taxa do IRC é de 20 %, exceto nos casos previstos nos números seguintes. 2 - No caso de sujeitos passivos que ... sejam qualificados como pequena ou média empresa ... a taxa de IRC aplicável aos primeiros 50 000 € de matéria coletável é de 16 %, aplicando-se a taxa prevista no número anterior ao excedente"

## FT review (2026-11-21, second pass): derrama estadual (CIRC art. 87.º-A)
Source: Portal das Finanças, CIRC art. 87.º-A, Wayback capture 2025-04-19
(`web.archive.org/web/20250419222655id_/https://info.portaldasfinancas.gov.pt/pt/informacao_fiscal/codigos_tributarios/CIRC_2R/Pages/irc87a.aspx`,
saved as `pt/law/circ87a_2025-04-19.html`; the same wording live in 2026):
* n.º 1: "Sobre a parte do lucro tributável superior a (euro) 1 500 000 ... incidem as taxas adicionais constantes da
  tabela seguinte: (Redação da Lei n.º 114/2017 ...) De mais de 1500 000 até 7 500 000 ... 3; De mais de 7 500 000 até
  35 000 000 ... 5; Superior a 35 000 000 ... 9"; n.º 2 b) (in our words): above EUR 1 500 000 the profit is split into a slice of EUR 6 000 000 at 3 %, a slice of EUR 27 500 000 at 5 % and the rest above EUR 35 000 000 at 9 %
* The base is the *lucro tributável* (before the deduction of tax losses, which gives the matéria coletável): the
  charge's base and relieved base are the profit before losses. A central-government tax (level central).


## 1200 Retenção na fonte de IRC (não residentes): dividend, interest, royalty, services (pass 8, grade A)
Source: Código do IRC art. 4.º, 87.º, 94.º, Portal das Finanças (`pt/law/irc4.txt`, `pt/law/irc87.txt`, `pt/law/irc94.txt`).
* art. 87.º n.º 4: for entities without seat, management or PE in Portugal "a taxa do IRC é de 25%"
* art. 94.º n.º 1: withholding on industrial/intellectual property income (a), capital income (c) and "outras prestações de serviços realizados ou utilizados em território português" (g); n.º 3 b): definitive for non-residents without a PE
* art. 4.º n.º 3 c) 7): services performed or used in Portugal, except transport, communications and financial activities


## 1200 Retenção na fonte de IRS (não residentes): dividend, interest, royalty, services (pass 9, grade A)
Source: Código do IRS art. 71.º, Portal das Finanças (`pt/law/cirs71.txt`).
* n.º 1: "Estão sujeitos a retenção na fonte a título definitivo, à taxa liberatória de 28 %: a) Os rendimentos de capitais obtidos em território português, por residentes ou não residentes" paid by entities with organised accounts
* n.º 4: "à taxa liberatória de 25 %" for non-residents: a) employment income and all business and professional income, even from isolated acts
* n.º 17: 35 % on capital income paid to residents of listed low-tax jurisdictions (not applied)
-/

namespace PtGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Imposto sobre o Rendimento das Pessoas Coletivas",   sched := Schedule.flat 2000,   smallTurnover := 50000000,   smallSched := Schedule.ofList [(0, 1600), (50000, 2000)] }

def citStatute : String := "CIRC art. 87.º n.º 1 (20 %), n.º 2 (16 % sobre os primeiros 50 000 €, PME), na redação da Lei n.º 45-A/2024 (OE 2025)"

/-- CIRC art. 87.º-A (derrama estadual): 3 % / 5 % / 9 % on the lucro tributável above 1.5 m / 7.5 m / 35 m €. -/
def derramaEstadual : Schedule := Schedule.ofList [(0, 0), (1500000, 300), (7500000, 500), (35000000, 900)]

def derramaStatute : String := "CIRC art. 87.º-A n.º 1, 2 (derrama estadual: 3 % de 1 500 000 a 7 500 000 €, 5 % até 35 000 000 €, 9 % acima; Lei n.º 114/2017)"

def derramaCharge (co : Company) : Charge :=
  charge .cit "Derrama estadual" (cit.beforeLosses co) id (fun b => derramaEstadual.tax {} b) (statute := derramaStatute)

/-- CIRC art. 4.º n.º 3 c) 7), art. 87.º n.º 4, art. 94.º n.º 1 a), c), g), n.º 3 b) -/
def p8wht : Wht :=
  { name := "Retenção na fonte de IRC (não residentes)", rules := [
    { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 2500, statute := "CIRC art. 94.º n.º 1 c), n.º 3 b), art. 87.º n.º 4: 25 % (definitive) on dividends" },   { kind := .interest, toCompany := some true, minStakeBp := 0, rateBp := 2500, statute := "CIRC art. 94.º n.º 1 c), n.º 3 b), art. 87.º n.º 4: 25 % (definitive) on interest" },   { kind := .royalty, toCompany := some true, minStakeBp := 0, rateBp := 2500, statute := "CIRC art. 94.º n.º 1 a), n.º 3 b), art. 87.º n.º 4: 25 % (definitive) on royalties" },   { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 2500, statute := "CIRC art. 94.º n.º 1 g), n.º 3 b), art. 87.º n.º 4: 25 % (definitive) on services performed or used in Portugal" }] }

/-- CIRS art. 71.º n.º 1 a), n.º 4 a) -/
def p9whti : Wht :=
  { name := "Retenção na fonte de IRS (não residentes)", rules := [
    { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 2800, statute := "CIRS art. 71.º n.º 1 a): taxa liberatória 28 % on capital income obtained in Portugal" },   { kind := .interest, toCompany := some false, minStakeBp := 0, rateBp := 2800, statute := "CIRS art. 71.º n.º 1 a): taxa liberatória 28 % on capital income obtained in Portugal" },   { kind := .royalty, toCompany := some false, minStakeBp := 0, rateBp := 2800, statute := "CIRS art. 71.º n.º 1 a): royalties of a holder other than the author are capital income: 28 %" },   { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 2500, statute := "CIRS art. 71.º n.º 4 a): taxa liberatória 25 % on business and professional income of non-residents, even from isolated acts" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Imposto sobre o Rendimento das Pessoas Coletivas", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute, derramaCharge g.company] else []) },
   { name := "1200 Retenção na fonte de IRC (não residentes) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) },
   { name := "1200 Retenção na fonte de IRS (não residentes) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9whti.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["PT 1200: Lei 45-A/2024 (in force 1.1.2025)", "PT 1200 withholding pass 8 (dividend, interest, royalty, services): Portal das Finanças, código consolidado fetched 2026-11-21 (`pt/law/irc87.txt`, `irc94.txt`, `irc4.txt`) (grade A)", "PT 1200 withholding pass 9 (dividend, interest, royalty, services; individuals): Portal das Finanças, código consolidado fetched 2026-11-21 (`pt/law/cirs71.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company then ["derrama municipal (Lei 73/2013 art. 18, up to 1,5 %) not modelled; derrama estadual: the principal-activity condition (commercial, industrial or agricultural) taken as met"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as performed or used in Portugal and not transport, communications or financial"] else [])
  ++ (if g.entity == .company && !g.company.paymentsAbroad.isEmpty then ["1200 withholding: 35 % to listed tax havens and the EU directive exemptions not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .royalty && !p.toCompany) then ["1200 withholding: royalties are taken as received by a holder other than the original author (capital income); an author's royalties are professional income at 25 % (n.º 4 a))"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && !p.toCompany) then ["1200 withholding: services are taken as performed or used in Portugal (CIRS art. 18.º)"] else [])

#guard cit.citTax { profit := 100000, turnover := 150000000 } == 20000
#guard cit.citTax { profit := 1000000, turnover := 150000000 } == 200000
#guard cit.citTax { profit := 100000, turnover := 50000000 } == 18000
#guard cit.citTax { profit := 100000, turnover := 50000001 } == 20000
#guard (derramaCharge { profit := 1500000 }).due == 0
#guard (derramaCharge { profit := 7500000 }).due == 180000
#guard (derramaCharge { profit := 35000000 }).due == 1555000
#guard (derramaCharge { profit := 40000000 }).due == 2005000
#guard (derramaCharge { profit := 40000000, lossesForward := 40000000 }).due == 2005000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 25000
#guard p9whti.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 28000
#guard p9whti.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 28000
#guard p9whti.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 28000
#guard p9whti.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 25000

end PtGlobal.Corporate
