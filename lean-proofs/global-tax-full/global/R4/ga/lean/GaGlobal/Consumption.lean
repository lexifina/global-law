import R4Common

/-!
# Gabon 2025: VAT (5111) and excises (5121)

Source: Code général des impôts 2025 (DGI), with the LF 2025 notes: `cmp20/world/B08-central-africa-fr/ga/law/cgi2025.txt`.

* **TVA** art. 221 (LF 2025): "Taux normal : 18 % …; Taux réduit : 10 % … viandes et volailles d'importation; huiles
  de table importées; sucre …; Taux réduit : 5 % … eau minérale produite au Gabon; … fourniture d'eau et
  d'électricité sur la consommation des compteurs sociaux et classiques". Exemptions (art. 210-211): locations civiles
  "de locaux nus"; manuels scolaires, journaux et périodiques; school fees; "les examens, consultations, soins,
  hospitalisations"; "médicaments; produits pharmaceutiques"; staple foods listed (pain, farine, riz, œufs, sardine
  tins …); "les ventes de gaz butane"; insurance contracts (taxe sur les contrats d'assurances).
* **Droits d'accises** art. 250 (LF 2023, LF 2024): "Bières locales 22 % 20 FCFA par litre; Bières d'importation
  25 % 180 FCFA par litre; Vins locaux 22 % 100 FCFA par litre; Vins d'importation dont le prix d'achat est inférieur
  ou égal à 50.000 FCFA 25 % 500 FCFA par litre; … Autres boissons locales titrant … supérieur à 12 % 25 % 500 FCFA
  par litre; Autres boissons importées … 30 % 500 FCFA par litre; Boissons sucrées et autres boissons titrant …
  inférieur à 12 % 5 %; Cigarettes, cigares, cigarillos, tabacs 32 % 250 FCFA par paquet". "Les eaux sont exonérées".
  Base: customs value plus duties, "à l'exclusion de la TVA"; local: "le prix de revient sortie usine".
* **Redevance d'usage routier** art. 366: "supercarburant : 53,20 FCFA par litre; gasoil : 47,08 FCFA par litre"
  (levied on the sale prices of refined products).
-/

namespace GaGlobal
open TaxKernel TaxKernel.Global

def tva : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1800, reduced := 1000, reduced2 := 500,
    classOf := fun gd => match gd with
      | .water | .electricity => .reduced2
      | .health | .medicines | .education | .insurance | .rent | .newspapers | .gas => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily tva "CGI art. 221 (18 / 10 / 5 %), art. 210-211 (exemptions)"

def accises : List R4.Exc :=
  [ { good := .beer, name := "Droits d'accises (bières)", advBp := 2200, perUnitNum := 20, vatBp := 1800, imported := some false,
      statute := "CGI art. 250 (bières locales 22 % + 20 F/l)" },
    { good := .beer, name := "Droits d'accises (bières)", advBp := 2500, perUnitNum := 180, vatBp := 1800, imported := some true,
      statute := "CGI art. 250 (bières d'importation 25 % + 180 F/l)" },
    { good := .wine, name := "Droits d'accises (vins)", advBp := 2200, perUnitNum := 100, vatBp := 1800, imported := some false,
      statute := "CGI art. 250 (vins locaux 22 % + 100 F/l)" },
    { good := .wine, name := "Droits d'accises (vins)", advBp := 2500, perUnitNum := 500, vatBp := 1800, imported := some true,
      statute := "CGI art. 250 (vins d'importation ≤ 50 000 F: 25 % + 500 F/l)" },
    { good := .spirits, name := "Droits d'accises (autres boissons > 12 %)", advBp := 2500, perUnitNum := 500, vatBp := 1800,
      imported := some false, minAbvBp := 1200, statute := "CGI art. 250 (locales > 12 %: 25 % + 500 F/l)" },
    { good := .spirits, name := "Droits d'accises (autres boissons > 12 %)", advBp := 3000, perUnitNum := 500, vatBp := 1800,
      imported := some true, minAbvBp := 1200, statute := "CGI art. 250 (importées > 12 %: 30 % + 500 F/l)" },
    { good := .nonAlcoholic, name := "Droits d'accises (boissons sucrées)", advBp := 500, vatBp := 1800,
      statute := "CGI art. 250 (boissons sucrées 5 %)" },
    { good := .cigarettes, name := "Droits d'accises (tabacs)", advBp := 3200, perUnitNum := 250, perUnitDen := 20, vatBp := 1800,
      statute := "CGI art. 250 (32 % + 250 F par paquet; a pack taken as 20 cigarettes)" },
    { good := .petrol, name := "Redevance d'usage routier", perUnitNum := 5320, perUnitDen := 100, vatBp := 1800,
      statute := "CGI art. 366 (53,20 F/l supercarburant)" },
    { good := .diesel, name := "Redevance d'usage routier", perUnitNum := 4708, perUnitDen := 100, vatBp := 1800,
      statute := "CGI art. 366 (47,08 F/l gasoil)" } ]

def excise : Family := R4.exciseFamily "droits d'accises (CGI art. 249-250), RUR (art. 366)" accises

def consumptionNotes (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
     ["CGI art. 210-211 / 221: staple foods listed are exempt (bread, flour, rice, eggs, tins) and imported meat, oils and sugar pay 10 %; the food line is taxed at 18 %"] else [])
  ++ (if g.consumption.any (·.good == .tobaccoOther) then ["CGI art. 250: tobacco other than cigarettes (32 % + 250 F per pack): not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .wine || s.good == .spirits) then
     ["CGI art. 250: wines and champagnes bought above 50 000 F (40 % + 3 000 / 4 000 F/l) and spirits ≤ 12 % not separated"] else [])
  ++ (if g.consumption.any (·.good == .communication) then ["CGI art. 250: 5 % excise on mobile calls not modelled (basket line is all communication)"] else [])

-- local beer, 1 180 F per litre: net 1 000, base (1 000 − 20) / 1,22 = 803, duty 20 + 176
#guard (R4.exciseCharges accises [{ good := .beer, amount := 1180, quantity := 1000 }]).map (·.due) == [196]
-- a pack of 20 imported or local cigarettes at 0 F: the specific 250 F
#guard (R4.exciseCharges accises [{ good := .cigarettes, amount := 0, quantity := 20000 }]).map (·.due) == [250]
#guard tva.embedded { good := .electricity, amount := 10500 } == 500
#guard tva.embedded { good := .rent, amount := 10500 } == 0

end GaGlobal
