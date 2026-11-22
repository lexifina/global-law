import ItGlobal.Pit

/-!
# IT 2025: Imposta sul reddito delle società (IRES) (1200) and withholding on payments abroad

Source: DPR 22 dicembre 1986 n. 917 (TUIR), normattiva Akoma Ntoso export vigente al 2025-07-01 (`it/law/tuir917_akn20250701.xml`); sha256 in `law/SHA256SUMS`.
* art. 77 c. 1: "L'imposta e' commisurata al reddito complessivo netto con l'aliquota del 24 per cento."
* art. 84 c. 1: "La perdita di un periodo d'imposta ... puo' essere computata in diminuzione del reddito dei periodi d'imposta successivi in misura non superiore all'ottanta per cento del reddito imponibile di ciascuno di essi"
* art. 89 c. 2: gli utili distribuiti "non concorrono a formare il reddito ... in quanto esclusi dalla formazione del reddito della societa' o dell'ente ricevente per il 95 per cento del loro ammontare"


## 1200 Ritenuta (lavoro autonomo): services (pass 8, grade A)
Source: DPR 29 settembre 1973 n. 600, normattiva, vigente al 2025-07-01 (`it/law/dpr600_art25.txt`).
* art. 25 c. 1: to non-residents "deve essere operata una ritenuta a titolo d'imposta nella misura del 30 per cento, anche per le prestazioni effettuate nell'esercizio di imprese"; excluded: work performed abroad


## 1200 Ritenuta (dividendi, interessi, canoni): dividend, interest, royalty (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Italy, Corporate - Withholding taxes, accessed 2025-08-03 (Wayback capture; `law/pwc_wht_wb2025.txt`); DPR 600/1973 art. 25-27 (`it/law/dpr600_art25.txt` ... `art27.txt`).
* non-treaty rates: dividends 26 %, interest 26 %, royalties 30 % on 75 % of the amount
* art. 27 c. 3-ter: 1,20 % on dividends to EU/EEA companies (not applied); the text of art. 26-27 still shows the pre-2014 rates, the 26 % comes from a general provision
-/

namespace ItGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Imposta sul reddito delle società (IRES)",   sched := Schedule.flat 2400,   lossFull := 0,   lossExcessBp := 8000,   participationBp := 9500,   participationMinBp := 0 }

def citStatute : String := "TUIR (DPR 917/1986) art. 77 (24 %), art. 84 c. 1 (perdite: 80 % del reddito), art. 89 c. 2 (utili esclusi per il 95 %)"

/-- DPR 600/1973 art. 25 c. 1 -/
def p8wht : Wht :=
  { name := "Ritenuta (lavoro autonomo)", rules := [
    { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 3000, statute := "DPR 600/1973 art. 25 c. 1: ritenuta a titolo d'imposta del 30 % on compensi for lavoro autonomo paid to non-residents, also for services rendered in a business" }] }

/-- DPR 600/1973 art. 25 c. 4, 26 c. 5, 27 c. 3 (rate 26 %: D.L. 66/2014 art. 3) -/
def p8wht2 : Wht :=
  { name := "Ritenuta (dividendi, interessi, canoni)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 2600, statute := "DPR 600/1973 art. 27 c. 3: ritenuta a titolo d'imposta on profits paid to non-residents, 26 %" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 2600, statute := "DPR 600/1973 art. 26 c. 5: ritenuta on interest paid to non-residents, 26 %" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2250, statute := "DPR 600/1973 art. 25 c. 4: 30 % on the taxable part (75 %) of royalties" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Imposta sul reddito delle società (IRES)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Ritenuta (lavoro autonomo) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) },
   { name := "1200 Ritenuta (dividendi, interessi, canoni) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["IT 1200: normattiva vigente 2025-07-01", "IT 1200 withholding pass 8 (services): normattiva vigente 2025-07-01 (`it/law/dpr600_art25.txt`) (grade A)", "IT 1200 withholding pass 8 (dividend, interest, royalty): 2025-08-03 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as professional services performed in Italy (art. 25: none on work performed abroad)"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 24000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 240000
#guard cit.citTax { profit := 3000000, lossesForward := 5000000, turnover := 10000000 } == 144000
#guard cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 0 } == 620000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 30000
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 26000
#guard p8wht2.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 26000
#guard p8wht2.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 26000
#guard p8wht2.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 26000
#guard p8wht2.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 22500
#guard p8wht2.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 22500

end ItGlobal.Corporate
