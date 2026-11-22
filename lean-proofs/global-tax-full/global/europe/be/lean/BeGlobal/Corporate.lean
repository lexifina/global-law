import BeGlobal.Pit

/-!
# BE 2025: Impôt des sociétés (1200) and withholding on payments abroad

Source: Loi du 25 décembre 2017 portant réforme de l'impôt des sociétés (MB 29.12.2017, numac 2017014414), eTaamb (etaamb.openjustice.be, `be/law/loi20171225_reforme_isoc_n2017014414.html`); sha256 in `law/SHA256SUMS`.
* art. 54, 1°: "Art. 215. Le taux de l'impôt des sociétés est fixé à 29 p.c. Pour les sociétés qui ... sont considérées comme des petites sociétés, le taux de l'impôt sur la première tranche de 0 à 100 000 euros est toutefois fixé à 20 p.c."
* art. 54, 3°: "dans l'alinéa 1er, remplacé par le 1°, les mots \"29 p.c.\" sont remplacés par les mots \"25 p.c.\""
* art. 86 B2: "Les articles ... 54, 3° ... entrent en vigueur le 1er janvier 2020 et sont applicables à partir de l'exercice d'imposition 2021"


## 1200 Précompte mobilier: dividend, interest, royalty (pass 8, grade B)
Source: PwC Worldwide Tax Summaries, Belgium, Corporate - Withholding taxes, accessed 2025-08-02 (Wayback capture; `law/pwc_wht_wb2025.txt`).
* non-treaty rates: dividends 30 %, interest 30 %, royalties and certain rentals 30 %


## 1200 withholding still grade C (pass 9)
* no Belgian provision on service fees paid to non-residents is on disk (CIR 92 art. 228 § 3 and the précompte professionnel on non-residents' service income, art. 248, 270)
* would unlock: CIR 92 art. 228 § 3, 248 and 270 (Justel / Fisconetplus text)
-/

namespace BeGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Impôt des sociétés",   sched := Schedule.flat 2500 }

def citStatute : String := "CIR 92 art. 215, al. 1 (25 p.c.), as replaced by the Loi du 25 décembre 2017 art. 54, 1° and 3° (in force for exercice d'imposition 2021 onwards, art. 86 B2)"

/-- CIR 92 art. 261, 269 (précompte mobilier) -/
def p8wht : Wht :=
  { name := "Précompte mobilier", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 3000, statute := "CIR 92 art. 269: précompte mobilier 30 % on dividends" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 3000, statute := "CIR 92 art. 269: précompte mobilier 30 % on interest" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 3000, statute := "CIR 92 art. 269: précompte mobilier 30 % on royalties" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Impôt des sociétés", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Précompte mobilier (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["BE 1200: amending act of 25.12.2017 read (25 % from exercice d'imposition 2021); the consolidated CIR 92 text as in force in 2025 not reached (later amendments of art. 215 not checked)", "BE 1200 withholding pass 8 (dividend, interest, royalty): 2025-08-02 (grade B)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 25000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 250000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 30000
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 30000

end BeGlobal.Corporate
