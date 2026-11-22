import EeGlobal.Pit

/-!
# Estonia 2025: tulumaks on distributed profit (1200)

Source: Tulumaksuseadus (TuMS), Riigi Teataja (official) as captured by the Internet Archive on 2025-06-13
(`ee/law/tums_wb.html`; sha256 in `law/SHA256SUMS`).
* **§ 4 (1)**: "Tulumaksu määr, välja arvatud lõigetes 2 ja 5 ning § 43 lõikes 4 nimetatud juhtudel, on 22%. [RT I,
  30.06.2023, 107 - jõust. 01.01.2025]"
* **§ 4 (1¹)**: "Paragrahvi 1 lõigetes 2, 3, 4 ja 6‒8 nimetatud maksuobjekti puhul jagatakse maksustatav summa enne
  maksumääraga korrutamist arvuga 0,78"
* **§ 1 (3)**: "Paragrahvides 49–52 ... sätestatud tulumaksuga maksustatakse residendist juriidilise isiku ... kasum selle
  jaotamisel"; **§ 50 (1)**: "Residendist äriühing ... maksab tulumaksu dividendide või muude kasumieraldistena jaotatud
  kasumilt nende väljamaksmisel".
The tax falls on distributed profit, not on the year's profit: 22 % of the dividends paid divided by 0,78 (= 22/78).


## 1200 withholding on payments abroad (pass 6)
Source: Tulumaksuseadus (TuMS), Riigi Teataja, Wayback capture 2025-06-13 (`ee/law/tums_wb.txt`).
* § 41: "Tulumaks peetakse kinni: ... 8) mitteresidendile makstavalt litsentsitasult (§ 29 lõike 6 punkt 4); ... 10) mitteresidendile Eestis osutatud teenuste eest makstavalt tasult (§ 29 lõige 3)"; dividends are not listed
* § 43 (1): "2) punktides 8–10 ja punktis 12 nimetatud väljamaksetelt – 10%."
* § 41 p. 4 with § 29 (7): interest withheld only where it is taxable under § 29 (7) (funds holding mostly Estonian real estate)
-/

namespace EeGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- TuMS § 4 (1¹): the distributed amount divided by 0,78. -/
def grossedBase (paid : Int) : Int := divR .down (pos paid * 100) 78

/-- TuMS § 4 (1): 22 % of the grossed-up amount. -/
def citOnDistribution (paid : Int) : Int := divR .down (2200 * grossedBase paid) BP

/-- Tulumaksuseadus §§ 29, 41, 43 (withholding on payments to non-residents) -/
def p7wht : Wht :=
  { name := "kinnipeetav tulumaks (mitteresident)", rules := [{ kind := .dividend, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "TuMS § 41 (dividends not listed: no withholding; the distributing company pays the § 50 income tax)" }, { kind := .interest, toCompany := none, minStakeBp := 0, rateBp := 0, statute := "TuMS § 41 p. 4, § 29 (7) (interest withheld only from real-estate fund interest; none on other interest)" }, { kind := .royalty, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "TuMS § 41 p. 8, § 29 (6) p. 4, § 43 (1) p. 2 (10 %)" }, { kind := .services, toCompany := none, minStakeBp := 0, rateBp := 1000, statute := "TuMS § 41 p. 10, § 29 (3), § 43 (1) p. 2 (10 % on services provided in Estonia)" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "1200 Tulumaks (jaotatud kasum)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company && g.company.dividendsPaid > 0 then [charge .cit "Tulumaks dividendidelt (TuMS § 50)" g.company.dividendsPaid grossedBase (fun b => divR .down (2200 * b) BP) (statute := "TuMS § 50 (1), § 4 (1) (22 %), (1¹) (/ 0,78)")] else []) },
   { name := "1200 kinnipeetav tulumaks on payments abroad (pass 7)", covers := [.cit],
     run := fun args g prev =>
       (if g.entity == .company then p7wht.charges g.company else []) }]

def absent : List Absent :=
  []

def notes : List String := ["EE 1200: distribution tax (no tax on retained profit); 22 % from 1.1.2025", "EE 1200 withholding: TuMS §§ 29, 41, 43, Riigi Teataja via Wayback 2025-06-13 (A)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.entity == .company then ["other profit distributions of §§ 49-52 (gifts, fringe benefits, non-business expenses) and the § 50 (1¹) reduction for dividends from taxed income not modelled"] else [])
  ++ (if g.entity == .company && !g.company.paymentsAbroad.isEmpty then ["withholding on payments to non-residents not modelled"] else [])
  ++ (if g.entity == .company && g.company.paymentsAbroad.any (·.kind == .services) then ["1200 withholding: services are taxed only when provided in Estonia (§ 29 (3)); all are taken as provided in Estonia; payments to a non-cooperative jurisdiction (§ 41 p. 11) not separated"] else [])

#guard grossedBase 78000 == 100000
#guard citOnDistribution 78000 == 22000
#guard citOnDistribution 0 == 0
#guard p7wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p7wht.amount { kind := .interest, amount := 100000, toCompany := true, stakeBp := 0 } == 0
#guard p7wht.amount { kind := .royalty, amount := 100000, toCompany := true, stakeBp := 0 } == 10000
#guard p7wht.amount { kind := .services, amount := 100000, toCompany := true, stakeBp := 0 } == 10000

end EeGlobal.Corporate
