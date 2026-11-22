import LuGlobal.Pit

/-!
# LU 2025: Impôt sur le revenu des collectivités (1200) and withholding on payments abroad

Source: Loi modifiée du 4 décembre 1967 concernant l'impôt sur le revenu, consolidated text 1 January 2025 (legilux PDF kept by the 1.x model, `lu/law/LIR_2025-01-01.pdf`); sha256 in `law/SHA256SUMS`.
* art. 174 (1): "1° 14 pour cent lorsque le revenu imposable ne dépasse pas 175 000 euros ; 2° 24 500 euros plus 30 pour cent du revenu dépassant 175 000 euros lorsque le revenu imposable est compris entre 175 000 euros et 200 001 euros ; 3° 16 pour cent lorsque le revenu imposable dépasse 200 000 euros" (as a marginal schedule: 14 % to 175 000, 30 % to 200 000, 16 % above: at 200 000 both give 32 000)


## 1200 Retenue à la source (revenus de capitaux): dividend, interest, royalty, services (pass 8, grade A)
Source: Loi concernant l'impôt sur le revenu, texte coordonné 1.1.2025 (`lu/law/LIR_2025-01-01.txt`).
* art. 146 (1): subject to retenue: dividends and profit shares (1., 2.) and interest of bonds carrying a profit-dependent supplement (3.)
* art. 148 (1): "Le taux de la retenue est fixé à 15%"; art. 152: retenue on literary/artistic and professional sports income of non-residents and on directors' fees
-/

namespace LuGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Impôt sur le revenu des collectivités",   sched := Schedule.ofList [(0, 1400), (175000, 3000), (200000, 1600)] }

def citStatute : String := "LIR art. 174 (1) (14 % / 24 500 € + 30 % / 16 %), as amended by L. 20.12.24"

/-- L.I.R. art. 146, 148, 152 -/
def p8wht : Wht :=
  { name := "Retenue à la source (revenus de capitaux)", rules := [
    { kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 1500, statute := "L.I.R. art. 146 (1) 1., art. 148 (1): retenue 15 % on dividends" },   { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "L.I.R. art. 146 (1) 3.: only profit-sharing bond interest is subject: none on ordinary interest" },   { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "L.I.R. art. 146, 152: royalties are not among the income subject to retenue: none" },   { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "L.I.R. art. 152: retenue only on literary, artistic and sports activities in Luxembourg and directors' fees: none on other service fees" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Impôt sur le revenu des collectivités", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Retenue à la source (revenus de capitaux) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["LU 1200: legilux consolidation 2025-01-01 (L. 20.12.24 art. 12)", "LU 1200 withholding pass 8 (dividend, interest, royalty, services): loi modifiée du 4 décembre 1967, texte coordonné au 1.1.2025 (`lu/law/LIR_2025-01-01.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend) then ["1200 withholding: the art. 147 exemption (parent companies, 10 % / EUR 1,2 m) not applied"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 14000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 160000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 15000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 15000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end LuGlobal.Corporate
