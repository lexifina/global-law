import IsGlobal.Pit

/-!
# IS 2025: Tekjuskattur lögaðila (1200) and withholding on payments abroad

Source: Lög um tekjuskatt nr. 90/2003, Lagasafn útgáfa 156b (Íslensk lög 1. september 2025), althingi.is capture (`is/law/tsl_wb.html`); sha256 in `law/SHA256SUMS`.
* 71. gr. 1. mgr.: "Tekjuskattur lögaðila skv. 1. og 2. tölul. 1. mgr. 2. gr. skal vera [20%] af tekjuskattsstofni, sbr. 2. tölul. 61. gr."
* 71. gr. 2. mgr.: other legal entities (3.-5. tölul.) 37,6%


## 1200 Tekjuskattur aðila með takmarkaða skattskyldu (afdráttur): dividend, interest, royalty, services (pass 9, grade A)
Source: Lög um tekjuskatt nr. 90/2003, Lagasafn útgáfa 156b, althingi.is via the Internet Archive (`is/law/tsl_wb.html`).
* 3. gr.: limited tax liability on payment for services or activity performed in Iceland (3. tölul.), on income from the use of movables, patents, rights or know-how (6.), on dividends of Icelandic companies (7.) and on interest from Icelandic sources (8.)
* 70. gr. 3. tölul.: "a. [20%] af greiðslunni ef um menn er að ræða"; "b. [20%] af greiðslunni ef um lögaðila skv. 1. og 2. tölul. 1. mgr. 2. gr. er að ræða"; c. 37,6% for other legal entities
* 70. gr. 6. tölul.: 22% af tekjum; 7. tölul.: a. 22% (individuals), b. 20% (legal entities); 8. tölul.: a. 12% (individuals, interest up to 300.000 kr. a year untaxed), b. 12% (legal entities)
* bráðabirgðaákvæði LXXVI: 21% / 13% / 38,4% for the operating year 2024 only (assessment 2025); the 2025 rates are those of 70. gr.
-/

namespace IsGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Tekjuskattur lögaðila",   sched := Schedule.flat 2000 }

def citStatute : String := "Lög um tekjuskatt nr. 90/2003, 71. gr. 1. mgr. (20% for hlutafélög and einkahlutafélög)"

/-- Lög um tekjuskatt nr. 90/2003, 3. gr. 3., 6., 7. og 8. tölul.; 70. gr. 3., 6., 7. og 8. tölul. -/
def p9wht : Wht :=
  { name := "Tekjuskattur aðila með takmarkaða skattskyldu (afdráttur)", rules := [
    { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 2000, statute := "lög nr. 90/2003, 3. gr. 7. tölul., 70. gr. 7. tölul. b-liður: 20% of dividends to legal entities" },   { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 2200, statute := "lög nr. 90/2003, 3. gr. 7. tölul., 70. gr. 7. tölul. a-liður: 22% of dividends to individuals" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1200, statute := "lög nr. 90/2003, 3. gr. 8. tölul., 70. gr. 8. tölul. a- og b-liður: 12% of interest" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2200, statute := "lög nr. 90/2003, 3. gr. 6. tölul., 70. gr. 6. tölul.: 22% of income from the use of rights, patents and know-how" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "lög nr. 90/2003, 3. gr. 3. tölul., 70. gr. 3. tölul. a- og b-liður: 20% of the payment for services performed in Iceland" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Tekjuskattur lögaðila", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Tekjuskattur aðila með takmarkaða skattskyldu (afdráttur) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["IS 1200: Lagasafn 156b, 1 September 2025", "IS 1200 withholding pass 9 (dividend, interest, royalty, services; companies, individuals): Lagasafn 156b, 1 September 2025 (`is/law/tsl_wb.html`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as performed in Iceland (3. gr. 3. tölul.); recipients other than hf./ehf.-type companies bear 37,6% (70. gr. 3. tölul. c), not separated"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest && !p.toCompany) then ["1200 withholding: the 300.000 kr. annual interest exemption for individuals (70. gr. 8. tölul. a) is not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend) then ["1200 withholding: the dividend deduction for EEA companies (31. gr. 1. mgr. 9. tölul.) is not applied"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 20000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 200000
#guard p9wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p9wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 22000
#guard p9wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 12000
#guard p9wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 12000
#guard p9wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 22000
#guard p9wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 22000
#guard p9wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p9wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 20000

end IsGlobal.Corporate
