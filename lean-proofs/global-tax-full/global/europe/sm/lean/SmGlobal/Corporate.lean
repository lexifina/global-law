import SmGlobal.Pit

/-!
# SM 2025: Corporate family not reached (grade C)

* 1200 Corporate income tax (Legge 16 dicembre 2013 n. 166 (IGR) art. 81 (17 %)): tried not fetched; Global law (the registry's source) not used (coordinator, 2026-11-21); would unlock: the IGR text with its 2025 wording
* 1200 Withholding on payments abroad (statutory withholding on dividends, interest, royalties): tried not fetched; Global law (the registry's source) not used (coordinator, 2026-11-21); would unlock: the IGR text with its 2025 wording


## 1200 Imposta generale sui redditi (persone giuridiche) (pass 9, grade A)
Source: Legge 16 dicembre 2013 n.166, testo coordinato (senza note), consigliograndeegenerale.sm documento17086436 (`sm/law/igr_166_2013_coord_senzanote.pdf`).
* art. 43 c. 1: "L'imposta generale sui redditi di cui al presente Titolo III è determinata applicando l'aliquota proporzionale, nella misura del 17%, al reddito imponibile"
* the coordinated text includes amendments to December 2025; the 17 % rate is the one in force throughout 2025


## 1200 Ritenute alla fonte su redditi corrisposti a non residenti: dividend, interest, services (pass 9, grade A)
Source: Legge 16 dicembre 2013 n.166, testo coordinato (senza note), consigliograndeegenerale.sm (`sm/law/igr_166_2013_coord_senzanote.pdf`).
* art. 102 c. 1: payers of fees for self-employed or assimilated services "a soggetti residenti all'estero, anche quando le prestazioni siano effettuate in regime d'impresa, devono operare una ritenuta a titolo d'imposta del 20 per cento" (3 % for listed artistic, sports and airport/naval services)
* art. 103 c. 1: on capital income paid to persons other than San Marino banks and financial companies "una ritenuta, a titolo d'imposta e con obbligo di rivalsa, del 13 per cento"; c. 6: profits to individuals 5 %, to others none
* art. 5 c. 2 b): royalties paid by residents are San Marino income; no withholding article for them was found (art. 104 c. 5: 10 % on rentals of equipment used in San Marino)


## 1200 Ritenuta sui redditi di lavoro autonomo (royalty): royalty (pass 10, grade A)
Source: Legge 166/2013 (imposta generale sui redditi), testo coordinato (`sm/law/igr_166_2013_coord_senzanote.txt`).
* art. 27 c. 6 b): income from the economic use of trade marks, works of the mind, copyrights, industrial inventions and the like is income from lavoro autonomo
* art. 102 c. 1: whoever pays compensation for lavoro autonomo or assimilated services as defined in art. 27 to persons resident abroad, also where performed as a business, withholds a final tax of 20 per cent
* art. 7 c. 2 b): such compensation paid by San Marino residents is produced in San Marino whatever the place of use


## year-in-force re-cite (pass 12, FT reviewer 6 Y-12)
* the held testo coordinato of Legge 166/2013 prints the wording in force from the 2026 tax period (L. 141/2025); for 2025 art. 148 c. 8 keeps the earlier wording ("Fino al 31 dicembre 2025"); the modelled IGR rate and withholding rates are the same in both wordings (bank interest under art. 103 c. 2 is 11 % in 2025: not a modelled kind)
-/

namespace SmGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- Legge 16 dicembre 2013 n.166 art. 43 c. 1 (17%) -/
def p9cit : CorpRegime :=
  { name := "Imposta generale sui redditi (persone giuridiche)", sched := Schedule.flat 1700 }

/-- Legge 16 dicembre 2013 n.166 art. 5, 102, 103 -/
def p9wht : Wht :=
  { name := "Ritenute alla fonte su redditi corrisposti a non residenti", rules := [
    { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "Legge 166/2013 art. 103 c. 6: profits paid to persons other than individuals bear no withholding (recipient's declaration that it does not act for an individual)" },   { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 500, statute := "Legge 166/2013 art. 103 c. 6: ritenuta a titolo d'imposta del 5% on profits paid to individuals" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 1300, statute := "Legge 166/2013 art. 103 c. 1: ritenuta a titolo d'imposta del 13 per cento on capital income" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "Legge 166/2013 art. 102 c. 1: ritenuta a titolo d'imposta del 20 per cento on fees for self-employed or assimilated services paid to non-residents, also when supplied by a business" }] }

/-- Legge 16 dicembre 2013 n. 166 art. 7 c. 2 b), art. 27 c. 6 b), art. 102 c. 1 -/
def p10whtr : Wht :=
  { name := "Ritenuta sui redditi di lavoro autonomo (royalty)", rules := [
    { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 2000, statute := "Legge 166/2013 art. 27 c. 6 b), art. 102 c. 1: income from the economic use of trade marks, works, copyrights and inventions is lavoro autonomo income; ritenuta a titolo d'imposta del 20 per cento on payments to persons resident abroad" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Imposta generale sui redditi (persone giuridiche) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [p9cit.citCharge g.company "Legge 16 dicembre 2013 n.166 art. 43 c. 1 (17%)"] else []) },
   { name := "1200 Ritenute alla fonte su redditi corrisposti a non residenti (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9wht.charges g.company else []) },
   { name := "1200 Ritenuta sui redditi di lavoro autonomo (royalty) (pass 10)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p10whtr.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["SM 1200 Imposta generale sui redditi (persone giuridiche) pass 9: testo coordinato fino alla Legge 22 dicembre 2025 n.158 (grade A)", "SM 1200 withholding pass 9 (dividend, interest, services; companies, individuals): testo coordinato fino alla Legge 22 dicembre 2025 n.158 (grade A)", "SM 1200 withholding pass 10 (royalty; all recipients): testo coordinato (`sm/law/igr_166_2013_coord_senzanote.txt`) (grade A)", "SM year-in-force re-cite (pass 12): the held testo coordinato of Legge 166/2013 prints the wording in force from the 2026 tax period (L. 141/2025); for 2025 art. 148 c. 8 keeps the earlier wording"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["new-business reductions (50 % rate cut for the first five periods) and the reinvested-profit relief (art. 61) are not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as self-employed or assimilated services (art. 27); the 3 % rate for listed services is not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .interest) then ["1200 withholding: interest is taken as paid by a non-financial company (art. 103 c. 1); bank interest follows c. 2"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .royalty) then ["1200 withholding: royalties are taken as paid by a San Marino operator (art. 7 c. 2 b)); the 3 % rate of art. 102 c. 2 (artistic, cultural, sporting services) does not concern royalties"] else [])

#guard p9cit.citTax { profit := 100000, turnover := 10000000 } == 17000
#guard p9cit.citTax { profit := 0, turnover := 10000000 } == 0
#guard p9wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p9wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 5000
#guard p9wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 13000
#guard p9wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 13000
#guard p9wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p9wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 20000
#guard p10whtr.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p10whtr.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 20000

end SmGlobal.Corporate
