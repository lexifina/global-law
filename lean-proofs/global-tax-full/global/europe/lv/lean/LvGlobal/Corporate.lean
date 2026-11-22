import LvGlobal.Pit

/-!
# Latvia 2025: uzņēmumu ienākuma nodoklis on distributed profit (1200)

Source: Uzņēmumu ienākuma nodokļa likums, likumi.lv "Redakcija uz" 01.07.2025 (`lv/law/uin_2025-07-01.html`; sha256 in
`law/SHA256SUMS`).
* **4. pants (9)**: "Nosakot taksācijas perioda ar uzņēmumu ienākuma nodokli apliekamo bāzi, ar uzņēmumu ienākuma
  nodokli apliekamā objekta vērtību dala ar koeficientu 0,8."
* **4. pants (1)** (rate): "Nodokļa likme ir 20 procenti no aprēķinātās ar nodokli apliekamās bāzes".
The tax falls on distributed profit (dividends, deemed distributions), not on the year's accounting profit: the base is
the dividends paid grossed up by 0,8.


## 1200 Uzņēmumu ienākuma nodoklis, ko ietur no nerezidentiem: dividend, interest, royalty, services (pass 8, grade A)
Source: Uzņēmumu ienākuma nodokļa likums, likumi.lv redakcija 1.7.2025 (`lv/law/uin_2025-07-01.txt`).
* 5. panta 1. daļa: withheld from "1) atlīdzības par vadības un konsultatīvajiem pakalpojumiem — 20 procenti"; 2) Latvian real estate 3 %; 4) rent 5 %; 3) payments under (6) and (8)
* 5. panta 6. daļa: 20 % on all payments and dividends to persons in low-tax or no-tax jurisdictions (not applied)


## 1200 Iedzīvotāju ienākuma nodoklis, ko ietur no nerezidentiem: dividend, interest, royalty, services (pass 9, grade A)
Source: Likums Par iedzīvotāju ienākuma nodokli, likumi.lv redakcija uz 1.7.2025 (`lv/law/iin_2025-07-01.txt`).
* 3. panta 3. daļa: a non-resident's taxable income includes 2) professional activity for Latvian residents in or outside Latvia, 10) dividends unless 9. pants provides otherwise, 11) interest, 12) a) authors' fees and b) payments for other intellectual property
* 17. panta 12. daļa: on the income in 3. panta 3. daļas 1., 2., 3., 4., ... 10., 11., 12. ... punkts "nodoklis tiek ieturēts ienākuma izmaksas vietā"
* 15. panta 5. daļa: 25,5 % on capital income; 8. daļa: 5 % on 12. punkta b); 7.1 daļa: 25,5 % on authors' fees; 2. daļa: 25,5 % up to the contribution ceiling, 33 % above
* 9. panta 1. daļas 2.1 punkts: dividends are exempt where UIN was paid on the distributed profit under the Uzņēmumu ienākuma nodokļa likums
-/

namespace LvGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- 4. pants (9): the object's value divided by 0,8. -/
def grossedBase (paid : Int) : Int := divR .down (pos paid * 10) 8

/-- 4. pants (1): 20 % of the grossed-up base. -/
def citOnDistribution (paid : Int) : Int := divR .down (2000 * grossedBase paid) BP

/-- likums Par uzņēmumu ienākuma nodokli 5. pants (1), (5), (6) -/
def p8wht : Wht :=
  { name := "Uzņēmumu ienākuma nodoklis, ko ietur no nerezidentiem", rules := [
    { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 2000, statute := "likums Par uzņēmumu ienākuma nodokli 5. panta 1. daļas 1. punkts: 20 % on management and consultancy services" },   { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "UIN likums 5. panta 1. daļa: dividends are not among the payments withheld (20 % only to low-tax jurisdictions, 6. daļa): none" },   { kind := .interest, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "UIN likums 5. panta 1. daļa: interest not withheld (20 % only to low-tax jurisdictions): none" },   { kind := .royalty, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "UIN likums 5. panta 1. daļa: royalties not withheld (20 % only to low-tax jurisdictions): none" }] }

/-- likums Par iedzīvotāju ienākuma nodokli 3. panta 3. daļa, 9. panta 1. daļa, 15. panta 2., 5., 8. daļa, 17. panta 12. daļa -/
def p9whti : Wht :=
  { name := "Iedzīvotāju ienākuma nodoklis, ko ietur no nerezidentiem", rules := [
    { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 0, statute := "likums Par IIN 9. panta 1. daļas 2.1 punkts: dividends are not taxable where the company paid UIN on the distributed profit: none" },   { kind := .interest, toCompany := some false, minStakeBp := 0, rateBp := 2550, statute := "likums Par IIN 3. panta 3. daļas 11. punkts, 15. panta 5. daļa, 17. panta 12. daļa: 25,5 % on interest, withheld at payment" },   { kind := .royalty, toCompany := some false, minStakeBp := 0, rateBp := 500, statute := "likums Par IIN 3. panta 3. daļas 12. punkta b) apakšpunkts, 15. panta 8. daļa: 5 % on payments for intellectual property other than authors' fees" },   { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 2550, statute := "likums Par IIN 3. panta 3. daļas 2. punkts, 15. panta 2. daļas 1. punkts, 17. panta 12. daļa: 25,5 % on income from professional activity for Latvian residents" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 UIN (sadalītā peļņa)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company && g.company.dividendsPaid > 0 then [charge .cit "Uzņēmumu ienākuma nodoklis (sadalītā peļņa)" g.company.dividendsPaid grossedBase (fun b => divR .down (2000 * b) BP) (statute := "UIN likums 4. pants (1) (20 %), (9) (/ 0,8)")] else []) },
   { name := "1200 Uzņēmumu ienākuma nodoklis, ko ietur no nerezidentiem (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) },
   { name := "1200 Iedzīvotāju ienākuma nodoklis, ko ietur no nerezidentiem (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9whti.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["LV 1200: distribution tax (no tax on retained profit)", "LV 1200 withholding pass 8 (dividend, interest, royalty, services): likumi.lv, redakcija 2025-07-01 (`lv/law/uin_2025-07-01.txt`) (grade A)", "LV 1200 withholding pass 9 (dividend, interest, royalty, services; individuals): likumi.lv, redakcija 2025-07-01 (`lv/law/iin_2025-07-01.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["deemed distributions (non-business expenses, bad debts, loans to related parties, 4. pants (2) 2)) and the dividend reduction for earlier taxed profit not modelled"] else [])
  ++ (if g.entity == .company && !g.company.paymentsAbroad.isEmpty then ["withholding on payments to non-residents (5. pants: 20 % on management fees, payments to low-tax jurisdictions) not modelled"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taken as management and consultancy services (5. panta 5. daļa)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .royalty && !p.toCompany) then ["1200 withholding: royalties are taken as payments for intellectual property other than authors' fees (authors' fees 25,5 %, 15. panta 7.1 daļa)"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && !p.toCompany) then ["1200 withholding: the 33 % band above the contribution ceiling (15. panta 2. daļas 2. punkts) and the EU/EEA 75 % option are not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .dividend && !p.toCompany) then ["1200 withholding: dividends are taken as paid from profit on which UIN was paid"] else [])

#guard grossedBase 80000 == 100000
#guard citOnDistribution 80000 == 20000
#guard citOnDistribution 0 == 0
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 20000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p9whti.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p9whti.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 25500
#guard p9whti.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 5000
#guard p9whti.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 25500

end LvGlobal.Corporate
