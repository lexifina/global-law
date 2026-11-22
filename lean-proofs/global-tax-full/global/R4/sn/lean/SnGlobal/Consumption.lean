import R4Common
import R4Common.K21

/-!
# Senegal 2025: VAT (5111) and excises (5121)

Source: Code général des impôts (loi n° 2012-31 du 31 décembre 2012), "CGI annoté Janvier 2025" (DGID), which carries
the LFI 2025 (loi n° 2025-02 du 6 janvier 2025) amendments: `cmp20/world/B07-west-africa-fr-pt/sn/src/CGI-2025.txt`.

* **TVA** art. 369: "Le taux de la TVA est fixé à 18%. … Ce taux est réduit à 10% pour les prestations fournies par
  les établissements d'hébergement touristique agréés."
  Exemptions, art. 361: 1) hospitalisation and care by the medical professions; 2) "les livraisons de médicaments et
  produits pharmaceutiques"; 3) "les livraisons de produits alimentaires non transformés et de première nécessité"
  (list: arrêté n° 3517 of 11 March 2013: cereals except luxury rice, vegetables, legumes, fresh meat, eggs, fish,
  unprocessed milk); 4) "l'enseignement scolaire ou universitaire"; 5) water and electricity only within the social
  tranche; 6) "les opérations financières et les prestations d'assurance et de réassurance, qui sont imposables à une
  taxation spécifique" (TAF, art. 404: 17 %); 11) "les locations d'immeubles nus à usage d'habitation"; 20) public
  passenger transport (unless the option of art. 353); 24) "le gaz butane à usage domestique" (bottles ≤ 38 kg).
* **Taxe sur les boissons** art. 413 (loi 2023-18, LFI 2025): "a) 50 % pour les alcools et liquides alcoolisés.
  Toutefois, pour les boissons alcoolisées produites localement, le taux est de 25 %"; additional tax "800 FCFA par
  litre d'alcool pour les alcools d'un tirage supérieur à 6° d'alcool et inférieur ou égal à 15°; 3 000 FCFA par litre
  d'alcool pour les alcools d'un tirage supérieur à 15°"; "b) 5 % pour les autres boissons et liquides".
* **Taxe sur les tabacs** art. 434 (LFI 2025): "Le taux de la taxe est fixé à 70%."
* Base of the specific taxes, art. 408: "le prix normal de vente tous frais et taxes compris, à l'exclusion de la taxe
  sur la valeur ajoutée et de la taxe spécifique elle-même" (import: customs value plus duties): `R4.Exc`.
* **Taxe sur les produits pétroliers** art. 444: "21.665 FCFA par hectolitre pour le super carburant … 10.395 FCFA par
  hectolitre pour le gasoil", the amount "diminué … de 1 000 francs par hectolitre représentatif de la taxe annuelle
  sur les véhicules": 206,65 FCFA per litre of super, 93,95 per litre of gas oil.
-/

namespace SnGlobal
open TaxKernel TaxKernel.Global

def tva : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1800, reduced := 1000,
    classOf := fun gd => match gd with
      | .health | .medicines | .education | .financial | .insurance | .rent | .transport | .gas => .exempt
      | .hotels => .reduced
      | _ => .standard }

def vat : Family := R4.vatFamily tva
  "CGI art. 369 (18 %; 10 % approved tourist accommodation), art. 361 1), 2), 4), 6), 11), 20), 24) (exemptions)"

/-- art. 413 a): 50 % (25 % for local production) plus the additional tax per litre of alcohol by strength band. -/
def alcohol : List R4.Exc :=
  [Good.beer, .wine, .spirits].flatMap fun gd =>
    [(false, 2500, "25 %, local"), (true, 5000, "50 %")].flatMap fun (imp, r, rs) =>
      [(-1, 600, 0, ""), (600, 1500, 800, " + 800 FCFA/l of alcohol (6°-15°)"), (1500, 100000, 3000, " + 3 000 FCFA/l of alcohol (> 15°)")].map
        fun (lo, hi, sp, ss) =>
          { good := gd, name := "Taxe sur les boissons (alcools)", advBp := r, perUnitNum := sp, onPureAlcohol := true,
            vatBp := 1800, minAbvBp := lo, maxAbvBp := hi, imported := some imp,
            statute := s!"CGI art. 413 a) ({rs}{ss}), art. 408 (base)" }

def accises : List R4.Exc :=
  alcohol ++
  [ { good := .nonAlcoholic, name := "Taxe sur les boissons (autres)", advBp := 500, vatBp := 1800,
      statute := "CGI art. 413 b) (5 %)" },
    { good := .cigarettes, name := "Taxe sur les tabacs", advBp := 7000, vatBp := 1800, statute := "CGI art. 434 (70 %), art. 408" },
    { good := .tobaccoOther, name := "Taxe sur les tabacs", advBp := 7000, vatBp := 1800, statute := "CGI art. 434 (70 %), art. 408" },
    { good := .petrol, name := "Taxe sur les produits pétroliers", perUnitNum := 20665, perUnitDen := 100, vatBp := 1800,
      statute := "CGI art. 444 (21.665 FCFA/hl super carburant less 1 000 FCFA/hl)" },
    { good := .diesel, name := "Taxe sur les produits pétroliers", perUnitNum := 9395, perUnitDen := 100, vatBp := 1800,
      statute := "CGI art. 444 (10.395 FCFA/hl gasoil less 1 000 FCFA/hl)" } ]

def excise : Family := exciseRuleFamily "taxes spécifiques (CGI livre II titre II)" (accises.map R4.Exc.toRule)

/-- kernel 2.1 `ExciseRule` (value before tax) gives the R4 figures on a mixed basket (local and imported). -/
def excT : CanonGlobal := { id := "x", household := { id := "x" }, consumption := [{ good := .beer, amount := 1180, quantity := 1000, abvBp := 500 }, { good := .wine, amount := 3540, quantity := 1000, abvBp := 1200 }, { good := .spirits, amount := 9000, quantity := 700, abvBp := 4000 }, { good := .cigarettes, amount := 1500, quantity := 20000 }, { good := .petrol, amount := 100000, quantity := 100000 }, { good := .nonAlcoholic, amount := 1180, quantity := 1000 }] }
#guard (exciseRuleCharges (accises.map R4.Exc.toRule) excT).map (·.due) == (R4.exciseCharges accises excT.consumption).map (·.due)

def consumptionNotes (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
     ["CGI art. 361 3): unprocessed staple foods (arrêté n° 3517 of 2013 list) are VAT-exempt; the basket's food line is taxed as processed food (18 %)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .water || s.good == .electricity) then
     ["CGI art. 361 5): water and electricity within the social tranche are exempt; the tranche is set by arrêté (not read): taxed at 18 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .financial || s.good == .insurance) then
     ["taxe sur les activités financières (CGI art. 404, 17 %) and insurance taxes: not modelled in the basket"] else [])

-- 1 180 FCFA of soft drinks: net of VAT 1 000, base 952, 5 % = 47
#guard (R4.exciseCharges accises [{ good := .nonAlcoholic, amount := 1180, quantity := 1000 }]).map (·.due) == [47]
-- imported beer at 5 % vol (≤ 6°): 50 % only; local beer 25 %; imported wine at 12 %: 50 % + 800 FCFA per litre of
-- alcohol (0,12 l per litre: 96)
#guard (R4.exciseCharges accises [{ good := .beer, amount := 1180, quantity := 1000, abvBp := 500 }] ["beer"]).map (·.due) == [333]
#guard (R4.exciseCharges accises [{ good := .beer, amount := 1180, quantity := 1000, abvBp := 500 }]).map (·.due) == [200]
#guard (R4.exciseCharges accises [{ good := .wine, amount := 3540, quantity := 1000, abvBp := 1200 }] ["wine"]).map (·.due) == [96 + 968]
-- the 15° edge: a 15 % vol wine is in the 800 band, 15,01 % in the 3 000 band
#guard (R4.exciseCharges accises [{ good := .wine, amount := 0, quantity := 1000, abvBp := 1500 }]).map (·.due) == [120]
#guard (R4.exciseCharges accises [{ good := .wine, amount := 0, quantity := 1000, abvBp := 1501 }]).map (·.due) == [450]
-- art. 444: 100 litres of super pay 21 665 − 1 000 = 20 665 FCFA
#guard (R4.exciseCharges accises [{ good := .petrol, amount := 100000, quantity := 100000 }]).map (·.due) == [20665]
#guard tva.embedded { good := .food, amount := 11800 } == 1800
#guard tva.embedded { good := .hotels, amount := 11000 } == 1000
#guard tva.embedded { good := .medicines, amount := 11800 } == 0

end SnGlobal
