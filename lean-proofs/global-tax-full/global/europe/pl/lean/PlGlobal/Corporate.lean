import PlGlobal.Pit

/-!
# PL 2025: Podatek dochodowy od osób prawnych (1200) and withholding on payments abroad

Source: ustawa z 15 lutego 1992 r. o podatku dochodowym od osób prawnych, tekst jednolity Dz.U. 2025 poz. 278 (Sejm ELI API, `pl/law/cit_tj2025.pdf`); sha256 in `law/SHA256SUMS`.
* art. 19 ust. 1: "1) 19 % podstawy opodatkowania; 2) 9 % podstawy opodatkowania ... – w przypadku podatników, u których przychody ... nie przekroczyły ... równowartości 2 000 000 euro"
* art. 22 ust. 1: dividends "ustala się w wysokości 19 % uzyskanego przychodu (dochodu)"


## 1200 Zryczałtowany podatek (odsetki, należności licencyjne, usługi): interest, royalty, services (pass 8, grade A)
Source: Ustawa o podatku dochodowym od osób prawnych (t.j. 2025, `pl/law/cit_tj2025.txt`) and od osób fizycznych (t.j. 2025, `pl/law/pit_tj2025.txt`).
* CIT art. 21 ust. 1: interest, royalties (pkt 1) and the listed intangible services (pkt 2a) "ustala się w wysokości 20 % przychodów"
* PIT art. 29 ust. 1 pkt 1 and 5: "20 % przychodu"; art. 30a ust. 1: "19 % zryczałtowany podatek dochodowy" on loan interest (pkt 1) and securities interest (pkt 2)
-/

namespace PlGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Podatek dochodowy od osób prawnych",   sched := Schedule.flat 1900 }

def wht : Wht :=
  { name := "Zryczałtowany podatek dochodowy (dywidendy)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1900, statute := "ustawa o CIT art. 22 ust. 1: 19 %" }] }

def citStatute : String := "ustawa o CIT art. 19 ust. 1 pkt 1 (19 %)"

/-- ustawa o CIT art. 21 ust. 1 pkt 1, 2a; ustawa o PIT art. 29 ust. 1 pkt 1, 5, art. 30a ust. 1 pkt 1-2 -/
def p8wht2 : Wht :=
  { name := "Zryczałtowany podatek (odsetki, należności licencyjne, usługi)", rules := [
    { kind := .interest, toCompany := some true, minStakeBp := 0, rateBp := 2000, statute := "ustawa o CIT art. 21 ust. 1 pkt 1: 20 % on interest" },   { kind := .royalty, toCompany := some true, minStakeBp := 0, rateBp := 2000, statute := "ustawa o CIT art. 21 ust. 1 pkt 1: 20 % on royalties and know-how" },   { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 2000, statute := "ustawa o CIT art. 21 ust. 1 pkt 2a: 20 % on advisory, accounting, market research, legal, advertising, management and control, data processing, recruitment and guarantee services" },   { kind := .interest, toCompany := some false, minStakeBp := 0, rateBp := 1900, statute := "ustawa o PIT art. 30a ust. 1 pkt 1-2: 19 % on loan and securities interest" },   { kind := .royalty, toCompany := some false, minStakeBp := 0, rateBp := 2000, statute := "ustawa o PIT art. 29 ust. 1 pkt 1: 20 % on royalties" },   { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 2000, statute := "ustawa o PIT art. 29 ust. 1 pkt 5: 20 % on advisory, accounting, market research, legal, advertising, management services" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Podatek dochodowy od osób prawnych", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else [])
       ++ (if g.entity == .company then wht.charges g.company else []) },
   { name := "1200 Zryczałtowany podatek (odsetki, należności licencyjne, usługi) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht2.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["PL 1200: t.j. Dz.U. 2025 poz. 278", "PL 1200 withholding pass 8 (interest, royalty, services): teksty jednolite 2025 (`pl/law/cit_tj2025.txt`, `pl/law/pit_tj2025.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as the intangible services listed in CIT art. 21 ust. 1 pkt 2a / PIT art. 29 ust. 1 pkt 5; other services bear none"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest || p.kind == .royalty) then ["1200 withholding: the art. 21 ust. 3 exemption for EU associated companies and the 2 000 000 zł pay-and-refund threshold (art. 26 ust. 2e) not applied"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 19000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 190000
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 19000
#guard p8wht2.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht2.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht2.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 19000
#guard p8wht2.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 20000
#guard p8wht2.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 20000

end PlGlobal.Corporate
