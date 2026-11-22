import AdGlobal.Pit

/-!
# AD 2025: Corporate family not reached (grade C)

* 1200 Corporate income tax (Llei 95/2010 de l'impost sobre societats (10 %)): tried bopa.ad not fetched in the P2 pass; Global law (the registry's source) not used (coordinator, 2026-11-21); would unlock: the IS law consolidated (bopa.ad)
* 1200 Withholding on payments abroad (statutory withholding on dividends, interest, royalties): tried bopa.ad not fetched in the P2 pass; Global law (the registry's source) not used (coordinator, 2026-11-21); would unlock: the IS law consolidated (bopa.ad)


## 1200 Impost sobre la renda dels no-residents fiscals (retenció): dividend, interest, royalty, services (pass 9, grade B)
Source: Llei 94/2010, del 29 de desembre, BOPA núm. 5 (26.1.2011), consellgeneral.ad (`ad/law/llei94_2010.pdf`); Llei 18/2011, BOPA núm. 80 (28.12.2011) (`ad/law/llei18_2011.pdf`).
* art. 29 (Llei 18/2011): "a) amb caràcter general, el 10 per 100; b) quan es tracti de rendiments derivats d'operacions de reassegurança, l'1,5 per 100"; c) cànons, "el 5 per 100"
* art. 15 b) (Llei 18/2011): exempt "Totes les rendes del capital mobiliari a les quals es refereix l'article 13" (dividends and interest of Andorran payers)
* art. 10 a): services used in Andorra, in particular studies, projects, technical assistance and management support, are income obtained in Andorra; art. 34-35: the payer withholds the tax due
* grade B: the 2010 law and its 2011 amendment are read; the 2015 consolidated text and later amendments (Llei 5/2014 IRPF, 2022) are not, so the rates are not confirmed for 2025


## 1200 Impost sobre societats (pass 9, grade B)
Source: Llei 95/2010, del 29 de desembre, de l'impost sobre societats, consellgeneral.ad (`ad/law/llei95_2010.pdf`).
* art. 41.1: "El tipus general de gravamen per als obligats tributaris d'aquest impost és del 10 per cent"; art. 41.2: 0 per cent for collective investment undertakings
* grade B: the 2010 text is read; the consolidated text in force for 2025 is not


## 1200 IS and IRNR: 2025 texts read, back to A (gap pass, grade C)
Source: BOPA; read from lexifina/andorra-law `lleis/2010-095, 2010-094, 2011-018, 2023-005, 2025-005` (commit c6d5886, 0d71a31, 88914d2, 545f120, f246318, in force 2011-2025).
* Llei 95/2010 art. 41.1: "tipus general ... és del 10 per cent"
* Llei 94/2010 art. 15 b) (Llei 18/2011): all income from movable capital of art. 13 (dividends, interest) is exempt
* art. 29 (Llei 18/2011): general rate 10 % (services), royalties 5 %, reinsurance 1,5 %
-/

namespace AdGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- Llei 94/2010 de l'impost sobre la renda dels no-residents fiscals art. 10, 13, 15, 29, 34-35 (redacció Llei 18/2011) -/
def p9wht : Wht :=
  { name := "Impost sobre la renda dels no-residents fiscals (retenció)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Llei 94/2010 art. 15 b) (redacció Llei 18/2011): all income from movable capital of art. 13 is exempt: none on dividends" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "Llei 94/2010 art. 15 b) (redacció Llei 18/2011): all income from movable capital of art. 13 is exempt: none on interest" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 500, statute := "Llei 94/2010 art. 29 c) (redacció Llei 18/2011): cànons 5 per 100" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "Llei 94/2010 art. 10 a), art. 29 a): services used in Andorra, 10 per 100" }] }

/-- Llei 95/2010 de l'impost sobre societats art. 41.1 (10 per cent) -/
def p9cit : CorpRegime :=
  { name := "Impost sobre societats", sched := Schedule.flat 1000 }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Impost sobre la renda dels no-residents fiscals (retenció) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9wht.charges g.company else []) },
   { name := "1200 Impost sobre societats (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [p9cit.citCharge g.company "Llei 95/2010 de l'impost sobre societats art. 41.1 (10 per cent)"] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["AD 1200 withholding pass 9 (dividend, interest, royalty, services; all recipients): BOPA 5/2011 and 80/2011 (later amendments not read) (grade B)", "AD 1200 Impost sobre societats pass 9: BOPA 5/2011 (original text; later amendments not read) (grade B)", "AD gap pass: 1200 IS and IRNR: 2025 texts read, back to A"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as used in Andorra (art. 10 a))"] else [])
  ++ (if g.entity == .company then ["the deductions of art. 43-45 (double taxation, job creation and investment) and the special regimes are not applied"] else [])

#guard p9wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p9wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p9wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p9wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p9wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 5000
#guard p9wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 5000
#guard p9wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p9wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 10000
#guard p9cit.citTax { profit := 100000, turnover := 10000000 } == 10000
#guard p9cit.citTax { profit := 0, turnover := 10000000 } == 0

end AdGlobal.Corporate
