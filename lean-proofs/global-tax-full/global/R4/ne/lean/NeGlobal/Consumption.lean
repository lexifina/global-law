import R4Common

/-!
# Niger 2025: VAT (5111) and excises (5121)

Sources: CGI 2013 updated to the LF 2022 (`cmp20/world/B07-west-africa-fr-pt/ne/src/CGI-2013-MAJ-LF2022.txt`) and
the LF 2025 (ordonnance n° 2024-59, `Ord-2024-59-LF2025.txt`), which rewrites art. 260 and leaves art. 226 as is.

* **TVA** art. 226: "Le taux normal de la taxe sur la valeur ajoutée est de 19%. Toutefois, sont soumises à un taux
  réduit : de 10% les activités de transport terrestre de personnes et de marchandises; de 10%, les activités de
  prestations d'hébergement et de restauration fournies par les hôtels; de 5% … le sucre; l'huile alimentaire; … le
  lait manufacturé; la farine …". Exemptions (art. 222) not read.
* **Droits d'accises** art. 260 (LF 2025): "Boissons non alcoolisées à l'exclusion de l'eau 15%; Eau minérale 15%;
  Boissons non alcoolisées énergisantes 20%; Bières de malt, vins, vermouths et autres boissons fermentées 45%;
  Alcool éthylique non dénaturé …, eau de vie, liqueurs et autres boissons spiritueuses 50%; Cigares … cigarettes …
  50 %".
* **Taxe intérieure sur les produits pétroliers** art. 271: at production "La base taxable est le prix de cession des
  produits raffinés sortis usine. Le taux, pour le Super sans plomb et le Gas-oil, est de 7,5%" (imports: art. 272
  tariff, not read).
-/

namespace NeGlobal
open TaxKernel TaxKernel.Global

def tva : Vat :=
  { name := "Taxe sur la valeur ajoutée", standard := 1900, reduced := 1000,
    classOf := fun gd => match gd with
      | .transport | .hotels => .reduced
      | _ => .standard }

def vat : Family := R4.vatFamily tva "CGI art. 226 (19 %; 10 % land transport and hotel lodging/catering; 5 % listed staples)"

def accises : List R4.Exc :=
  [ { good := .nonAlcoholic, name := "Droits d'accises (boissons non alcoolisées)", advBp := 1500, vatBp := 1900, statute := "CGI art. 260 (LF 2025) (15 %)" },
    { good := .beer, name := "Droits d'accises (bières, vins)", advBp := 4500, vatBp := 1900, statute := "CGI art. 260 (LF 2025) (45 %)" },
    { good := .wine, name := "Droits d'accises (bières, vins)", advBp := 4500, vatBp := 1900, statute := "CGI art. 260 (LF 2025) (45 %)" },
    { good := .spirits, name := "Droits d'accises (spiritueux)", advBp := 5000, vatBp := 1900, statute := "CGI art. 260 (LF 2025) (50 %)" },
    { good := .cigarettes, name := "Droits d'accises (tabacs)", advBp := 5000, vatBp := 1900, statute := "CGI art. 260 (LF 2025) (50 %)" },
    { good := .tobaccoOther, name := "Droits d'accises (tabacs)", advBp := 5000, vatBp := 1900, statute := "CGI art. 260 (LF 2025) (50 %)" },
    { good := .petrol, name := "Taxe intérieure sur les produits pétroliers", advBp := 750, vatBp := 1900, statute := "CGI art. 271 (7,5 % of the ex-refinery price)" },
    { good := .diesel, name := "Taxe intérieure sur les produits pétroliers", advBp := 750, vatBp := 1900, statute := "CGI art. 271 (7,5 % of the ex-refinery price)" } ]

def excise : Family := R4.exciseFamily "droits d'accises (CGI art. 259-260), TIPP (art. 271)" accises

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["CGI art. 222 VAT exemptions not read; the 5 % staples (sugar, oil, manufactured milk, flour …) are inside the food line, taxed at 19 %",
   "CGI art. 226: the 10 % hotel rate covers lodging and catering supplied by hotels; restaurants outside hotels at 19 %",
   "TIPP: imported fuel (art. 272 tariff) not read; the 7,5 % ex-refinery rate is applied to all fuel"]

#guard (R4.exciseCharges accises [{ good := .beer, amount := 1190, quantity := 1000 }]).map (·.due) == [310]
#guard tva.embedded { good := .transport, amount := 11000 } == 1000

end NeGlobal
