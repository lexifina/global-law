import LuGlobal.Pit
import TaxKernel.Global2

/-!
# LU 2025: Taxe sur la valeur ajoutée (5111); excises not modelled in this pass

Source: Loi TVA, texte coordonné au 1er janvier 2025 (Administration de l'enregistrement, des domaines et de la TVA; official coordinated text, not the authentic Mémorial text), pfi.public.lu PDF (`lu/law/loi_tva_2025-01-01.pdf`); sha256 in `law/SHA256SUMS`.
* art. 39, 3.: "Le taux normal ... est fixé à dix-sept pour cent ... Le taux réduit de la taxe est fixé à huit pour cent ... Le taux super-réduit de la taxe est fixé à trois pour cent ... Le taux intermédiaire de la taxe est fixé à quatorze pour cent"
* annexe A (8 %): "1° Gaz liquéfiés ... 2° Énergie électrique 3° Chaleur fournie au moyen d'un réseau de chauffage ..."; annexe B (3 %): "1° Produits alimentaires destinés à la consommation humaine, à l'exclusion des boissons alcooliques ... 5° Livres, journaux et périodiques ... 7° Distribution d'eau 8° Produits pharmaceutiques ... 9° Services de restaurant ... à l'exclusion ... boissons alcooliques 10° Hébergement ... 11° Transports de personnes"; annexe C (14 %): "1° Vins de raisins frais titrant 13° ou moins ... 2° Combustibles minéraux solides ; huiles minérales ... destinés à être utilisés comme combustibles"
* art. 57bis, 1.: exempt where "le chiffre d'affaires annuel ... n'excède pas le seuil de 50 000 euros"

## FT review (2026-11-21, third pass): gas
Same coordinated text (`lu/law/loi_tva_2025-01-01.txt`), **Annexe A - Liste des biens et services soumis au taux
réduit**: "1° Gaz liquéfiés ou à l'état gazeux, propres au chauffage, à l'éclairage et à l'alimentation de moteurs";
"2° Énergie électrique" (art. 40: taux réduit 8 %). The model had electricity at 8 % and gas at 17 %.


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), LU excise records for the situation on 1 July 2025 (tobacco 4104, alcohol 4102, energy 4103; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `lu/law/tedb_*.json`).
* TEDB LU manufactured tobacco (1.7.2025): 22.1414 EUR per 1 000 cigarettes + 48.14 % of the retail selling price, at least 144.5 EUR per 1 000
* TEDB LU beer (1.7.2025): 0.7933 EUR per hl and degree Plato
* TEDB LU still wine (1.7.2025): 0 EUR per hl of product
* TEDB LU ethyl alcohol (1.7.2025): 1123.1042 EUR per hl of pure alcohol
* TEDB LU energy products (1.7.2025): unleaded petrol 559.0846 EUR per 1 000 l
* TEDB LU energy products (1.7.2025): gas oil used as propellant 452.55 EUR per 1 000 l
* TEDB LU energy products (1.7.2025): gas oil used as heating fuel (non-business use) 116.96 EUR per 1 000 l
-/

namespace LuGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1700, reduced := 800, reduced2 := 1400, superReduced := 300, threshold := 50000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .nonAlcoholic | .water | .medicines | .books | .newspapers | .restaurants | .hotels | .transport => .superReduced
      | .electricity | .gas => .reduced
      | .wine | .heatingOil => .reduced2
      | _ => .standard }

def vatStatute : String := "Loi modifiée du 12 février 1979 concernant la TVA art. 39 (17 %, 8 %, 3 %, 14 %), art. 40 et annexes A-C, art. 44 (exonérations), art. 57bis (50 000 euros)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 110707, perUnitDen := 5000000, adValoremBp := 4814, minNum := 289, minDen := 2000, statute := "TEDB LU manufactured tobacco (1.7.2025): 22.1414 EUR per 1 000 cigarettes + 48.14 % of the retail selling price, at least 144.5 EUR per 1 000" },
      { good := .wine, name := "Excise duty on still wine", statute := "TEDB LU still wine (1.7.2025): 0 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 5615521, perUnitDen := 500000, onPureAlcohol := true, statute := "TEDB LU ethyl alcohol (1.7.2025): 1123.1042 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 2795423, perUnitDen := 5000000, statute := "TEDB LU energy products (1.7.2025): unleaded petrol 559.0846 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 9051, perUnitDen := 20000, statute := "TEDB LU energy products (1.7.2025): gas oil used as propellant 452.55 EUR per 1 000 l" },
      { good := .heatingOil, name := "Excise duty on gas oil used as heating fuel (non-business use)", perUnitNum := 731, perUnitDen := 6250, statute := "TEDB LU energy products (1.7.2025): gas oil used as heating fuel (non-business use) 116.96 EUR per 1 000 l" }] }

/-- TEDB LU beer (1.7.2025): 0.7933 EUR per hl and degree Plato (kernel 2.1 `ExciseRule`, line field "platoBp"). -/
def gxBeerRule : ExciseRule :=
  { good := .beer, name := "Excise duty on beer", perPlatoNum := 7933, perPlatoDen := 1000000,   statute := "TEDB LU beer (1.7.2025): 0.7933 EUR per hl and degree Plato" }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Taxe sur la valeur ajoutée", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges [gxBeerRule] g }]

def absent : List Absent :=
  []

def notes : List String := ["LU 5111: texte coordonné 2025-01-01 (to the loi du 20 décembre 2024)", "LU 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .wine) then ["wine taken at 14 % (annexe C 1°: still wine of 13 % vol or less; sparkling and stronger wine 17 %)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .clothing) then ["children's clothing (annexe B 6°, 3 %) not separated: clothing at 17 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Loi du 17 décembre 2010 fixant les droits d'accise (not read)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer) then ["5121 Excise duty on beer: charged by the line's \"platoBp\" (degree Plato x 100); a beer line without it bears no beer duty"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 LU: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 11700 } == 1700
#guard vat.embedded { good := .electricity, amount := 10800 } == 800
#guard vat.embedded { good := .wine, amount := 11400 } == 1400
#guard vat.embedded { good := .food, amount := 10300 } == 300
#guard vat.net { turnover := 50000, sales := [{ good := .other, net := 50000 }] } == 0
#guard vat.embedded { good := .gas, amount := 108 } == 8
#guard gxBeerRule.dutyOn { good := .beer, amount := 300, quantity := 100000 } { platoBp := 1200 } == 9
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 2429
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 0
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 449
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 559
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 452
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 116

end LuGlobal.Consumption
