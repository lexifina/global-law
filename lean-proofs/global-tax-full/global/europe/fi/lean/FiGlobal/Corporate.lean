import FiGlobal.Pit

/-!
# FI 2025: Yhteisön tulovero (1200) and withholding on payments abroad

Source: Tuloverolaki 1535/1992, Finlex `lainsaadanto/1992/1535`, Internet Archive capture of 2025-07-03 (`fi/law/tvl_wb20250703.html`); sha256 in `law/SHA256SUMS`.
* 124 § 2 mom.: "Yhteisön tuloveroprosentti on 20. Yhteisetuuden tuloveroprosentti on 26,5." (21.12.2016/1323)


## 1200 Lähdevero rajoitetusti verovelvolliselle: dividend, interest, royalty, services (pass 8, grade A)
Source: Laki rajoitetusti verovelvollisen tulon ja varallisuuden verottamisesta 627/1978, Finlex, Wayback 2025-05-21 (`fi/law/lahdeverolaki_wb2025.txt`); tuloverolaki 1535/1992 (`fi/law/tvl_wb20250703.txt`).
* 7 § 1 mom.: "2) 20 prosenttia rajoitetusti verovelvolliselle yhteisölle maksettavasta osingosta, korosta ja rojaltista"; "4) 30 prosenttia" to others; "6) 13 prosenttia yhteisölle ... maksettavasta ... työkorvauksesta"; "1) 35 prosenttia" on an individual's työkorvaus
* tuloverolaki 9 §: "Rajoitetusti verovelvollinen ei ole verovelvollinen täältä saamastaan korkotulosta" on foreign loans, deposits, bonds and trade receivables
-/

namespace FiGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Yhteisön tulovero",   sched := Schedule.flat 2000 }

def citStatute : String := "Tuloverolaki (1535/1992) 124 § 2 mom. (yhteisön tuloveroprosentti 20), 21.12.2016/1323"

/-- lähdeverolaki 627/1978 3 §, 7 § 1 mom.; tuloverolaki 1535/1992 9 § -/
def p8wht : Wht :=
  { name := "Lähdevero rajoitetusti verovelvolliselle", rules := [
    { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 2000, statute := "lähdeverolaki 3 §, 7 § 1 mom. 2 kohta: 20 % on dividends to a non-resident company" },   { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 3000, statute := "lähdeverolaki 3 §, 7 § 1 mom. 4 kohta: 30 % on dividends to others" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "tuloverolaki 9 §: a non-resident is not liable on interest on loans from abroad, bonds, deposits and trade receivables: none" },   { kind := .royalty, toCompany := some true, minStakeBp := 0, rateBp := 2000, statute := "lähdeverolaki 3 §, 7 § 1 mom. 2 kohta: 20 % on royalties to a non-resident company" },   { kind := .royalty, toCompany := some false, minStakeBp := 0, rateBp := 3000, statute := "lähdeverolaki 7 § 1 mom. 4 kohta: 30 % on royalties to others" },   { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 1300, statute := "lähdeverolaki 3 §, 7 § 1 mom. 6 kohta: 13 % on work compensation (työkorvaus) to a company" },   { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 3500, statute := "lähdeverolaki 7 § 1 mom. 1 kohta: 35 % on an individual's work compensation" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Yhteisön tulovero", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Lähdevero rajoitetusti verovelvolliselle (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["FI 1200: Finlex capture 2025-07-03 (124 § in the wording of 21.12.2016/1323)", "FI 1200 withholding pass 8 (dividend, interest, royalty, services): Finlex, Wayback captures 2025-05-21 / 2025-07-03 (`fi/law/lahdeverolaki_wb2025.txt`, `fi/law/tvl_wb20250703.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as work done in Finland; the 10 f § release (prepayment register, tax card) is not applied; the 510 €/month deduction on 35 % income not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend) then ["1200 withholding: dividends exempt for EU/treaty parent companies (3 § 4 mom.) not separated"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 20000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 200000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 13000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 35000

end FiGlobal.Corporate
