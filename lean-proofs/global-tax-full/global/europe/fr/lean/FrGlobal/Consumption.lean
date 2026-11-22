import FrGlobal.Pit

/-!
# France 2025: taxe sur la valeur ajoutée (5111); excises (CIBS) not reached

Sources: the CGI article copies kept by the French 1.x model (`fr/law/y2025/<article>.md`, each with a `.md.src`
naming the version's start date and the amending act; Légifrance itself is blocked from the build server and a second machine).
* **CGI art. 278**: "Le taux normal de la taxe sur la valeur ajoutée est fixé à 20 %" (version from 2014-01-01).
* **art. 278-0 bis**: 5,5 % "A. – Les livraisons portant sur : 1° Les denrées alimentaires destinées à la consommation
  humaine" (except confectionery, chocolate, margarine, caviar, "Les boissons alcooliques"); books.
* **art. 279**: 10 %: "a. ... la fourniture d'un hébergement dans le cadre du secteur hôtelier", restaurant meals
  (m), passenger transport (b quater).
* **art. 281 octies**: "2,10 % pour les livraisons portant sur les préparations magistrales, médicaments ... " (version
  2022-01-01); **art. 278 quater**: other medicines 10 %.
* **art. 293 B I** (version 2025-03-01, Loi n° 2025-127): franchise when the prior-year turnover does not exceed
  "85 000" (services: "37 500"), current year "93 500" / "41 250".
* Exemptions: art. 261 (medical care 4 1°, education 4 4°), 261 C (financial and insurance), 261 D (unfurnished
  residential letting).
Dating (pass 16): art. 279 read in its version of 31.12.2023 (in force to 28.2.2026; `fr/law/cgi279_v20231231.md`) and art. 278-0 bis
in its versions of 1.3.2025 (Légifrance capture 2025-04-04) and 1.10.2025 (`fr/law/cgi278-0bis_v20251001.md`); January-February 2025 not read. Their rates (5,5 % and 10 %) are the 2025 rates but the item lists are read in the 2026
wording: grade B.


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), FR excise records for the situation on 1 July 2025 (tobacco 4081, alcohol 4079, energy 4080 (situation 1.2.2025); data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `fr/law/tedb_*.json`).
* TEDB FR manufactured tobacco (1.7.2025): 72.7 EUR per 1 000 cigarettes + 55.0 % of the retail selling price, at least 378.8 EUR per 1 000
* TEDB FR beer (1.7.2025): 8.1 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB FR still wine (1.7.2025): 4.12 EUR per hl of product
* TEDB FR ethyl alcohol (1.7.2025): 2508.98 EUR per hl of pure alcohol
* TEDB FR ethyl alcohol: 1 899.18 EUR per hl of pure alcohol (accise) and 609.80 EUR per hl of pure alcohol (cotisation sécurité sociale, CSS art. L. 245-9): 2 508.98 together
-/

namespace FrGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 2000, reduced := 1000, reduced2 := 550, superReduced := 210, threshold := 85000,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .water | .books => .reduced2
      | .hotels | .restaurants | .transport => .reduced
      | .medicines => .superReduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "CGI art. 278 (20 %), 279 (10 %), 278-0 bis (5,5 %), 281 octies (2,1 %), 293 B (franchise 85 000 €); art. 261, 261 C, 261 D (exonérations)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 727, perUnitDen := 10000, adValoremBp := 5500, minNum := 947, minDen := 2500, statute := "TEDB FR manufactured tobacco (1.7.2025): 72.7 EUR per 1 000 cigarettes + 55.0 % of the retail selling price, at least 378.8 EUR per 1 000" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 81, perUnitDen := 10, onPureAlcohol := true, statute := "TEDB FR beer (1.7.2025): 8.1 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 103, perUnitDen := 2500, statute := "TEDB FR still wine (1.7.2025): 4.12 EUR per hl of product" },
      { good := .spirits, name := "Accise sur les alcools + cotisation sécurité sociale", perUnitNum := 125449, perUnitDen := 5000, onPureAlcohol := true, statute := "TEDB FR ethyl alcohol (1.7.2025): 2508.98 EUR per hl of pure alcohol" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 TVA", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["FR 5111: CGI copies of the 1.x model (fr/law/y2025)", "FR 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .medicines) then ["medicines at 2,1 % (reimbursable, art. 281 octies); non-reimbursable medicines are 10 % (art. 278 quater)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .newspapers) then ["press (2,1 %, art. 298 septies) not read: taken at 20 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .electricity || s.good == .gas) then ["accises (code des impositions sur les biens et services) not reached: Légifrance blocked, CIBS not in the local copies"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas) then ["5111: electricity and gas taken at 20 %; the subscription part (abonnements, ≤ 36 kVA) was 5,5 % until 31.7.2025 (CGI art. 278-0 bis B, version from 1.3.2025), not separated"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .heatingOil) then ["5121 FR: excise on petrol, diesel, heatingOil not charged: the 2025 rate changed during the year and the purchase is undated (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 FR: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 120 } == 20
#guard vat.embedded { good := .food, amount := 1055 } == 55
#guard vat.embedded { good := .restaurants, amount := 110 } == 10
#guard vat.embedded { good := .medicines, amount := 1021 } == 21
#guard vat.net { turnover := 85000, sales := [{ good := .other, net := 85000 }] } == 0
#guard vat.net { turnover := 85001, sales := [{ good := .other, net := 85001 }] } == 17000
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 2822
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 40
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 4
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 1003

end FrGlobal.Consumption
