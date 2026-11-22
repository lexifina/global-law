import R4Common
import R4Common.K21

/-!
# Togo 2025: VAT (5111) and excises (5121)

Source: Code général des impôts et livre des procédures fiscales, édition 2025 (OTR), with the LF 2025 changes:
`cmp20/world/B07-west-africa-fr-pt/tg/law/rescue2/otr_cgi_lpf_2025.txt`.

* **TVA** art. 195: "Le taux de la taxe sur la valeur ajoutée est un taux unique de 18% applicable à toutes les
  activités et à tous les produits à l'exception de ceux exonérés en vertu de l'article 180". Exemptions art. 180:
  I 2) "les opérations bancaires et financières soumises à la taxe sur les activités financières (TAF)"; 3) insurance
  (taxe sur les conventions d'assurance); III 1) "les consultations médicales, les soins présentant un caractère
  médical, toutes les prestations médicales fournies par les hôpitaux, les cliniques …"; III 2) "les activités
  d'enseignement"; III 3) "les livraisons de journaux et de publications périodiques d'information"; V 1) the
  products of the annex (Annexe TVA: medicines of chapter 30, butane for household use 2711.13, school books
  4901.99.10, fresh fish, cereals, vegetables …). Passenger transport is exempt only from transporters under the
  taxe professionnelle unique (art. 180 I 4); rents of dwellings are not exempt.
* **Droits d'accises** art. 243 (table): sweetened soft drinks 10 %, other non-alcoholic 5 %, "Bières 20 %",
  "Autres boissons alcoolisées 60 %", "Tabacs 50 %". Base art. 245: "à l'importation, par la valeur en douane majorée
  des droits et taxes perçus à l'entrée, à l'exception de la taxe sur la valeur ajoutée; en régime intérieur, par le
  prix de vente sortie-usine, à l'exclusion de la taxe sur la valeur ajoutée" (`R4.Exc`).
* **Droit d'accises sur les produits pétroliers (DAPP)** art. 241: "Supercarburant sans plomb 57,76 FCFA par litre;
  Gas-oil ou gazole 48,06 FCFA par litre"; art. 240: "Son montant est inclus dans le prix de vente".
-/

namespace TgGlobal
open TaxKernel TaxKernel.Global

def tva : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1800,
    classOf := fun gd => match gd with
      | .health | .medicines | .education | .financial | .insurance | .newspapers | .gas => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily tva "CGI art. 195 (18 %), art. 180 I 2)-3), III 1)-3), V 1) and Annexe TVA (exemptions)"

def accises : List R4.Exc :=
  [ { good := .nonAlcoholic, name := "Droits d'accises (boissons non alcoolisées sucrées)", advBp := 1000, vatBp := 1800,
      statute := "CGI art. 243 n° 1 (10 %), art. 245 (base)" },
    { good := .beer, name := "Droits d'accises (bières)", advBp := 2000, vatBp := 1800, statute := "CGI art. 243 n° 2 (20 %)" },
    { good := .wine, name := "Droits d'accises (autres boissons alcoolisées)", advBp := 6000, vatBp := 1800, statute := "CGI art. 243 n° 2 (60 %)" },
    { good := .spirits, name := "Droits d'accises (autres boissons alcoolisées)", advBp := 6000, vatBp := 1800, statute := "CGI art. 243 n° 2 (60 %)" },
    { good := .cigarettes, name := "Droits d'accises (tabacs)", advBp := 5000, vatBp := 1800, statute := "CGI art. 243 n° 3 (50 %)" },
    { good := .tobaccoOther, name := "Droits d'accises (tabacs)", advBp := 5000, vatBp := 1800, statute := "CGI art. 243 n° 3 (50 %)" },
    { good := .petrol, name := "Droit d'accises sur les produits pétroliers", perUnitNum := 5776, perUnitDen := 100, vatBp := 1800,
      statute := "CGI art. 241 n° 1 (57,76 FCFA/l supercarburant)" },
    { good := .diesel, name := "Droit d'accises sur les produits pétroliers", perUnitNum := 4806, perUnitDen := 100, vatBp := 1800,
      statute := "CGI art. 241 n° 2 (48,06 FCFA/l gas-oil)" } ]

def excise : Family := exciseRuleFamily "droits d'accises (CGI art. 240-246)" (accises.map R4.Exc.toRule)

/-- kernel 2.1 `ExciseRule` (value before tax) gives the R4 figures on a mixed basket (local and imported). -/
def excT : CanonGlobal := { id := "x", household := { id := "x" }, consumption := [{ good := .beer, amount := 1180, quantity := 1000, abvBp := 500 }, { good := .wine, amount := 3540, quantity := 1000, abvBp := 1200 }, { good := .spirits, amount := 9000, quantity := 700, abvBp := 4000 }, { good := .cigarettes, amount := 1500, quantity := 20000 }, { good := .petrol, amount := 100000, quantity := 100000 }, { good := .nonAlcoholic, amount := 1180, quantity := 1000 }] }
#guard (exciseRuleCharges (accises.map R4.Exc.toRule) excT).map (·.due) == (R4.exciseCharges accises excT.consumption).map (·.due)

def consumptionNotes (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
     ["CGI Annexe TVA: listed unprocessed foods (fish, cereals, vegetables, dairy items) are exempt; the basket's food line is taxed at 18 %"] else [])
  ++ (if g.consumption.any (·.good == .nonAlcoholic) then
     ["CGI art. 243 n° 1: unsweetened non-alcoholic drinks pay 5 %, not 10 %: the sweetened rate is applied"] else [])
  ++ (if g.consumption.any (·.good == .transport) then
     ["CGI art. 180 I 4): passenger transport by operators under the taxe professionnelle unique is exempt; taxed at 18 %"] else [])
  ++ (if g.consumption.any (·.good == .rent) then
     ["rents: no VAT exemption in art. 180; charged at 18 % (only due when the landlord is a taxable person)"] else [])
  ++ (if g.consumption.any (·.good == .books) then
     ["Annexe TVA 4901.99.10: only school and scientific books are exempt; books taxed at 18 %"] else [])

-- 1 180 F of beer: net 1 000, base 1 000 / 1,2 = 833, 20 % = 166
#guard (R4.exciseCharges accises [{ good := .beer, amount := 1180, quantity := 1000 }]).map (·.due) == [166]
-- 1 000 l of super: 57 760 F
#guard (R4.exciseCharges accises [{ good := .petrol, amount := 0, quantity := 1000000 }]).map (·.due) == [57760]
#guard tva.embedded { good := .other, amount := 11800 } == 1800
#guard tva.embedded { good := .newspapers, amount := 11800 } == 0

end TgGlobal
