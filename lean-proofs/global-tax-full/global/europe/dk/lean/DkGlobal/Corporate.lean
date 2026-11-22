import DkGlobal.Pit

/-!
# DK 2025: Selskabsskat (1200) and withholding on payments abroad

Source: Bekendtgørelse af selskabsskatteloven, LBK nr 279 af 13/03/2025 (retsinformation ELI XML `eli/lta/2025/279/xml`, `dk/law/sel_lbk2025_279.xml`; in force from March 2025 until LBK nr 984 af 15/10/2026); sha256 in `law/SHA256SUMS`.
* § 17, stk. 1: "Indkomstskatten for de i § 1, stk. 1, nr. 1-2 i og 3 a-5 b ... nævnte selskaber og foreninger m.v. (selskabsskatten) beregnes af den skattepligtige indkomst og udgør 22 pct."
* § 13, stk. 1, nr. 2: "Udbytte, som de i § 1 ... nævnte selskaber ... modtager ... Dette gælder dog kun udbytter af datterselskabsaktier og koncernselskabsaktier, jf. aktieavancebeskatningslovens §§ 4 A og 4 B" (datterselskabsaktier: at least 10 %)
* § 12, stk. 2: losses in full up to "et grundbeløb på 15,9 mio. kr. (2010-niveau)", the rest in 60 pct. of the excess; the grundbeløb is indexed (personskattelovens § 20) and its 2025 amount is not in the act


## 1200 Begrænset skattepligt (udbytte, renter, royalty): dividend, interest, royalty, services (pass 8, grade A)
Source: Selskabsskatteloven, LBK nr 279 af 13/03/2025, retsinformation.dk (`dk/law/sel_lbk2025_279.txt`).
* § 2, stk. 1: limited liability on dividends (litra c), interest on controlled debt (litra d) and royalties (litra g); the tax is "22 pct." of the dividends, interest and royalties (15 pct. on dividends where the recipient's state exchanges information, not applied)
* controlled debt: the payee controls the payer (skattekontrolloven kap. 4); taken here as a stake above 50 %


## 1200 Kildeskat, personer (udbytte, renter, royalty, tjenesteydelser): dividend, interest, royalty, services (pass 9, grade A)
Source: Bekendtgørelse af kildeskatteloven, LBK nr 460 af 03/05/2024, retsinformation.dk (`dk/law/ksl_lbk2024_460.txt`).
* § 65, stk. 1: the distributing company "skal ... indeholde 27 pct. af det samlede udbytte" (udbytteskat)
* § 65 C, stk. 1: on royalty to a person or company liable under § 2, stk. 1, nr. 8, or selskabsskatteloven § 2, stk. 1, litra g, the payer "skal ... indeholde 22 pct. af den samlede royalty"
* § 2, stk. 1: limited liability of individuals covers work in Denmark (nr. 1-3), a permanent establishment (nr. 4), real property (nr. 5), dividends (nr. 6), adviser fees (nr. 7, limited by stk. 13 to former residents linked to the payer) and royalty (nr. 8); interest is not listed
* lov nr. 333 af 9. april 2024 (royalty paid abroad without withholding, in force 1 July 2024) is not incorporated in LBK 460/2024: not read
-/

namespace DkGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "Selskabsskat",   sched := Schedule.flat 2200,   participationBp := 10000,   participationMinBp := 1000 }

def citStatute : String := "Selskabsskatteloven (LBK nr 279 af 13/03/2025) § 17, stk. 1 (22 pct.), § 13, stk. 1, nr. 2 (udbytte af datterselskabsaktier)"

/-- selskabsskatteloven § 2, stk. 1, litra c, d, g (rates 22 pct.) -/
def p8wht : Wht :=
  { name := "Begrænset skattepligt (udbytte, renter, royalty)", rules := [
    { kind := .dividend, toCompany := some true, minStakeBp := 0, rateBp := 2200, statute := "selskabsskatteloven § 2, stk. 1, litra c, stk. 4: 22 pct. of dividends" },   { kind := .interest, toCompany := some true, minStakeBp := 5001, rateBp := 2200, statute := "selskabsskatteloven § 2, stk. 1, litra d: 22 pct. on interest on controlled debt" },   { kind := .interest, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "selskabsskatteloven § 2, stk. 1, litra d: only interest on controlled debt is taxable: none on other interest" },   { kind := .royalty, toCompany := some true, minStakeBp := 0, rateBp := 2200, statute := "selskabsskatteloven § 2, stk. 1, litra g: 22 pct. of royalties" },   { kind := .services, toCompany := some true, minStakeBp := 0, rateBp := 0, statute := "selskabsskatteloven § 2, stk. 1: service fees are not among the items of limited tax liability: none" }] }

/-- kildeskatteloven § 2, stk. 1, nr. 6-8, stk. 13; § 65, stk. 1; § 65 C, stk. 1 -/
def p9whti : Wht :=
  { name := "Kildeskat, personer (udbytte, renter, royalty, tjenesteydelser)", rules := [
    { kind := .dividend, toCompany := some false, minStakeBp := 0, rateBp := 2700, statute := "kildeskatteloven § 2, stk. 1, nr. 6, § 65, stk. 1: udbytteskat 27 pct. of the dividend" },   { kind := .interest, toCompany := some false, minStakeBp := 0, rateBp := 0, statute := "kildeskatteloven § 2, stk. 1: interest is not among the income of non-resident individuals liable to tax: none" },   { kind := .royalty, toCompany := some false, minStakeBp := 0, rateBp := 2200, statute := "kildeskatteloven § 2, stk. 1, nr. 8, § 65 C, stk. 1: royaltyskat 22 pct." },   { kind := .services, toCompany := some false, minStakeBp := 0, rateBp := 0, statute := "kildeskatteloven § 2, stk. 1, nr. 7, stk. 13: fees as adviser or consultant are taxable only for former residents with a share in the management, control or capital of the payer: none otherwise" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Selskabsskat", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then [cit.citCharge g.company citStatute] else []) },
   { name := "1200 Begrænset skattepligt (udbytte, renter, royalty) (pass 8)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p8wht.charges g.company else []) },
   { name := "1200 Kildeskat, personer (udbytte, renter, royalty, tjenesteydelser) (pass 9)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p9whti.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["DK 1200: LBK nr 279 af 13/03/2025", "DK 1200 withholding pass 8 (dividend, interest, royalty, services): LBK nr 279 af 13/03/2025 (`dk/law/sel_lbk2025_279.txt`) (grade A)", "DK 1200 withholding pass 9 (dividend, interest, royalty, services; individuals): LBK nr 460 af 03/05/2024 (`dk/law/ksl_lbk2024_460.txt`) (grade A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company && g.company.lossesForward > 0 then ["DK § 12, stk. 2 loss cap (indexed grundbeløb + 60 %) not applied: losses offset in full"] else [])
  ++ (if g.entity == .company && g.company.interestExpense > 0 then ["interest limitation (ATAD art. 4 transposition) not modelled"] else [])
  ++ (if g.entity == .company then ["group regimes, CFC, transfer pricing and treaties out of scope"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .dividend) then ["1200 withholding: withholding mechanics (kildeskatteloven § 65: 27 % withheld, excess refunded) not read; the 22 pct. tax is booked; the 15 pct. rate and the subsidiary-share exemption not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .dividend && !p.toCompany) then ["1200 withholding: 27 pct. is the amount withheld; the refund to 15 pct. for residents of information-exchange states is not applied"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .services && !p.toCompany) then ["1200 withholding: the recipient is taken as never resident in Denmark and without a Danish permanent establishment (§ 2, stk. 1, nr. 4: assessed, not withheld)"] else [])

#guard cit.citTax { profit := 100000, turnover := 10000000 } == 22000
#guard cit.citTax { profit := 1000000, turnover := 10000000 } == 220000
#guard cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 1000 } == 600000
#guard cit.taxableProfit { profit := 1000000, dividendsReceived := 400000, participationBp := 999 } == 1000000
#guard p8wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 22000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 5001 } == 22000
#guard p8wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p8wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 22000
#guard p8wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p9whti.amount { kind := .dividend, amount := 100000, toCompany := false, stakeBp := 0 } == 27000
#guard p9whti.amount { kind := .interest, amount := 100000, toCompany := false, stakeBp := 0 } == 0
#guard p9whti.amount { kind := .royalty, amount := 100000, toCompany := false, stakeBp := 0 } == 22000
#guard p9whti.amount { kind := .services, amount := 100000, toCompany := false, stakeBp := 0 } == 0

end DkGlobal.Corporate
