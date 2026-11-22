import FiGlobal.Pit
import TaxKernel.Global2

/-!
# FI 2025: Arvonlisävero (5111); excises not modelled in this pass

Source: Finlex open data (official): the amending acts 462/2024 (in force 1.9.2024), 691/2024 and 448/2024 (in force 1.1.2025) (`fi/law/alvl_muutos_2024_*.html`) and the consolidated text fin@20240935 for 85 § items 1-2 (`fi/law/alvl_cons_fin20240935.html`); sha256 in `law/SHA256SUMS`.
* 84 § (462/2024): "Suoritettava vero on 25,5 prosenttia veron perusteesta, ellei 85 tai 85 a §:ssä toisin säädetä."
* 85 § (fin@20240935 items 1-2; 691/2024 items 4-12): "... vero on 14 prosenttia veron perusteesta: 1) ruokatavara, juoma ... (elintarvike); 2) ravintola- ja ateriapalvelu ...; 4) henkilökuljetus; 5) majoitustilan ... luovuttaminen; 6) lääkelaissa (395/1987) tarkoitettu lääke ...; 7) fyysisellä alustalla oleva tai sähköisesti luovutettava kirja; ..."
* 85 a § (691/2024): "... 10 prosenttia veron perusteesta: 1) fyysisellä alustalla olevat tai sähköisesti luovutettavat sanoma- ja aikakauslehdet ..."
* 3 § (448/2024): "Myyjä ei ole verovelvollinen, jos kuluvan kalenterivuoden ja sitä edeltäneen kalenterivuoden liikevaihto on enintään 20 000 euroa"


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), FI excise records for the situation on 1 July 2025 (tobacco 4078, alcohol 4076; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `fi/law/tedb_*.json`).
* TEDB FI beer (1.7.2025): 36.2 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB FI still wine (1.7.2025): 456 EUR per hl of product
* TEDB FI ethyl alcohol (1.7.2025): 5550 EUR per hl of pure alcohol


## 5121 Tupakkavero, savukkeet (kaksi verotaulukkoa 2025) (gap pass 2) (gap pass, grade A)
Source: lexifina/finland-law `saadoskokoelma/2024/0xxx/565.md` (commit 128fb4a261, in force 1.11.2024); matches the TEDB at 1.1 and 1.7.2025.
* Laki tupakkaverosta 1470/1994 liite, verotaulukko A (1.11.2024-30.6.2025): savukkeet 9,97 snt/kpl + 52,0 %, vähimmäisvero 37,16 snt/kpl (laki 565/2024)
* Laki tupakkaverosta 1470/1994 liite, verotaulukko B (1.7.-31.12.2025): savukkeet 10,51 snt/kpl + 52,0 %, vähimmäisvero 38,96 snt/kpl (laki 565/2024)
-/

namespace FiGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Arvonlisävero", standard := 2550, reduced := 1400, reduced2 := 1000, threshold := 20000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .nonAlcoholic | .restaurants | .transport | .hotels | .medicines | .books => .reduced
      | .newspapers => .reduced2
      | _ => .standard }

def vatStatute : String := "Arvonlisäverolaki (1501/1993) 84 § (25,5 %, L 462/2024), 85 § (14 %, items 1-2 and L 691/2024 items 4-12), 85 a § (10 %, L 691/2024), 3 § (20 000 euroa, L 448/2024)"

def excise : Excise :=
  { rates := [
      { good := .beer, name := "Excise duty on beer", perUnitNum := 181, perUnitDen := 5, onPureAlcohol := true, statute := "TEDB FI beer (1.7.2025): 36.2 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 114, perUnitDen := 25, statute := "TEDB FI still wine (1.7.2025): 456 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 111, perUnitDen := 2, onPureAlcohol := true, statute := "TEDB FI ethyl alcohol (1.7.2025): 5550 EUR per hl of pure alcohol" }] }

/-- Tupakkavero, savukkeet (kaksi verotaulukkoa 2025) (gap pass 2; kernel 2.1 `ExciseRule` date windows). -/
def gxDated0 : ExciseRule :=
  { good := .cigarettes,   name := "Tupakkavero (savukkeet)",   perUnitNum := 997,   perUnitDen := 10000,   adValoremBp := 5200,   minNum := 3716,   minDen := 100000,   validTo := "2025-07-01",   statute := "Laki tupakkaverosta 1470/1994 liite, verotaulukko A (1.11.2024-30.6.2025): savukkeet 9,97 snt/kpl + 52,0 %, vähimmäisvero 37,16 snt/kpl (laki 565/2024)" }
def gxDated1 : ExciseRule :=
  { good := .cigarettes,   name := "Tupakkavero (savukkeet)",   perUnitNum := 1051,   perUnitDen := 10000,   adValoremBp := 5200,   minNum := 3896,   minDen := 100000,   validFrom := "2025-07-01",   statute := "Laki tupakkaverosta 1470/1994 liite, verotaulukko B (1.7.-31.12.2025): savukkeet 10,51 snt/kpl + 52,0 %, vähimmäisvero 38,96 snt/kpl (laki 565/2024)" }

def gxDatedRules : List ExciseRule := [gxDated0, gxDated1]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Arvonlisävero", covers := [.vat, .excise, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges gxDatedRules g }]

def absent : List Absent :=
  []

def notes : List String := ["FI 5111: wording in force 1.1.2025 (acts 462/2024, 691/2024, 448/2024)", "FI 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)", "FI 5121 gap pass 2: Tupakkavero, savukkeet (kaksi verotaulukkoa 2025) (A, table A to 30.6.2025, table B from 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food || s.good == .nonAlcoholic) then ["alcoholic drinks and tobacco excluded from the 14 % food item: the household's alcohol is in the excise goods, taken at 25,5 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Laki alkoholijuomaverosta, laki tupakkaverosta, laki nestemäisten polttoaineiden valmisteverosta (not read)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .heatingOil) then ["5121 FI liquid fuel excise not modelled (the TEDB reports a weighted average, not the statutory rates of laki nestemäisten polttoaineiden valmisteverosta)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 FI: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12550 } == 2550
#guard vat.embedded { good := .food, amount := 11400 } == 1400
#guard vat.embedded { good := .newspapers, amount := 11000 } == 1000
#guard vat.net { turnover := 20000, sales := [{ good := .other, net := 20000 }] } == 0
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 181
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 456
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 2220
#guard gxDated0.dutyOn { good := .cigarettes, amount := 5000, quantity := 1000000 } {} == 2699
#guard gxDated1.dutyOn { good := .cigarettes, amount := 5000, quantity := 1000000 } {} == 2705
#guard gxDated0.windowDays 2025 + gxDated1.windowDays 2025 == 365

end FiGlobal.Consumption
