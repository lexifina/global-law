import R4Common

/-!
# Benin 2025: VAT (5111) and excises (5121) — grade B (2023 edition of the code)

Source: Code général des impôts 2023 (DGI, "officiel"; `cmp20/world/B07-west-africa-fr-pt/bj/src/CGI-2023.txt`).
The LF 2024 and LF 2025 were not available: values are the 2023 text's (grade B, flagged).

* **TVA** art. 241: "Le taux de la taxe sur la valeur ajoutée est fixé à 18%." Exemptions (art. 238) not read.
* **Taxe sur certains produits** art. 277: "1) cigarettes, cigares, cigarillos, tabac à fumer … : 50 %; 2) boissons
  alcoolisées : bières et cidres : 20 %; vins : 40 %; liqueurs et champagnes : 45 %; 3) boissons non alcoolisées : …
  énergisantes : 20 %; boissons non alcoolisées à l'exception de l'eau non gazéifiée : 7 %". Base (art. 276): the
  sale price excluding VAT (`R4.Exc`).
* **Taxe sur les produits pétroliers** art. 283 2): "65 francs CFA/litre pour le super carburant; … 20 francs
  CFA/litre pour le gas-oil".
-/

namespace BjGlobal
open TaxKernel TaxKernel.Global

def tva : Vat := { name := "Taxe sur la valeur ajoutée", standard := 1800 }

def vat : Family := R4.vatFamily tva "CGI 2023 art. 241 (18 %); exemptions (art. 238) not read"

def accises : List R4.Exc :=
  [ { good := .cigarettes, name := "Taxe sur les tabacs", advBp := 5000, vatBp := 1800, statute := "CGI 2023 art. 277 1) (50 %)" },
    { good := .tobaccoOther, name := "Taxe sur les tabacs", advBp := 5000, vatBp := 1800, statute := "CGI 2023 art. 277 1) (50 %)" },
    { good := .beer, name := "Taxe sur les boissons alcoolisées", advBp := 2000, vatBp := 1800, statute := "CGI 2023 art. 277 2) (bières 20 %)" },
    { good := .wine, name := "Taxe sur les boissons alcoolisées", advBp := 4000, vatBp := 1800, statute := "CGI 2023 art. 277 2) (vins 40 %)" },
    { good := .spirits, name := "Taxe sur les boissons alcoolisées", advBp := 4500, vatBp := 1800, statute := "CGI 2023 art. 277 2) (liqueurs 45 %)" },
    { good := .nonAlcoholic, name := "Taxe sur les boissons non alcoolisées", advBp := 700, vatBp := 1800, statute := "CGI 2023 art. 277 3) (7 %)" },
    { good := .petrol, name := "Taxe sur les produits pétroliers", perUnitNum := 65, vatBp := 1800, statute := "CGI 2023 art. 283 2) (65 F/l super)" },
    { good := .diesel, name := "Taxe sur les produits pétroliers", perUnitNum := 20, vatBp := 1800, statute := "CGI 2023 art. 283 2) (20 F/l gas-oil)" } ]

def excise : Family := R4.exciseFamily "taxes spécifiques (CGI 2023 art. 275-283)" accises

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["Benin: CGI 2023 edition (LF 2024-2025 not available): rates as of 2023",
   "CGI art. 238 VAT exemptions not read: every basket line at 18 %"]

#guard (R4.exciseCharges accises [{ good := .beer, amount := 1180, quantity := 1000 }]).map (·.due) == [166]
#guard (R4.exciseCharges accises [{ good := .petrol, amount := 0, quantity := 1000000 }]).map (·.due) == [65000]

end BjGlobal
