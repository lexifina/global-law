import R4Common

/-!
# Cameroon 2025: VAT (5111) and excises (5121) — partial (grade B)

Source: Code général des impôts, édition 2024 (DGI; `cmp20/world/B08-central-africa-fr/cm/law/cgi2024.raw.txt`),
with the LF 2025 circular (`circ_lf2025.ocr.txt`: LF 2025 changes art. 17 ter, 70, 142 for ball-point pens, 228
quinquies, 242; none touches the rates used here).

* art. 142 (1): "a) Taxe sur la Valeur Ajoutée : Taux général …… 17,5 %; Taux zéro …. 0 %; b) Droit d'accises : Taux
  super élevé : 50 %; Taux élevé : 30 %; Taux général 25 %; Taux moyen 12,5 %". e): "Le taux élevé s'applique aux
  cigares, cigarettes, et autres tabacs du chapitre 24"; (7): for tobacco the duty "ne peut être inférieur à 5 000 F
  CFA pour 1000 tiges de cigarettes, s'agissant des produits finis de tabac importés".
* **CGI Livre deuxième (fiscalité locale), Titre III, art. C 53**: "Il est institué au profit des communes, des
  centimes additionnels sur les impôts et taxes ci-après : ... - la taxe sur la valeur ajoutée (TVA)"; **art. C 54
  (1)**: "Le taux des centimes additionnels est fixé à 10 % du principal de l'impôt concerné" (`cgi2024.raw.txt`
  lines 29584-29600; FT review 2026-11-21). VAT and CAC together: 17,5 % x 1,10 = 19,25 % of the price before tax,
  booked as one 5111 charge (the price on a basket line includes both).
* Not read (OCR of the two-column edition interleaves the columns): the art. 128 exemption list, the products of the general and medium excise rates and the
  specific duties per centilitre on alcoholic drinks (art. 142 (8)-(9)): every basket line is at 17,5 %, alcohol is
  not taxed by excise here (listed in `unsupported`).
-/

namespace CmGlobal
open TaxKernel TaxKernel.Global

/-- CGI art. 142 (1) a) 17,5 % plus the centimes additionnels communaux, art. C 53-C 54 (1): 10 % of the principal. -/
def tva : Vat := { name := "Taxe sur la valeur ajoutée + centimes additionnels communaux", standard := 1925 }

def vat : Family := R4.vatFamily tva "CGI art. 142 (1) a) (17,5 %); art. C 53, C 54 (1) (centimes additionnels communaux 10 % of the VAT: 19,25 %); art. 128 exemptions not read"

def accises : List R4.Exc :=
  [ { good := .cigarettes, name := "Droit d'accises (tabacs)", advBp := 3000, vatBp := 1925, imported := some false,
      statute := "CGI art. 142 (1) b), e) (taux élevé 30 %)" },
    { good := .cigarettes, name := "Droit d'accises (tabacs)", advBp := 3000, vatBp := 1925, imported := some true,
      minNum := 5, statute := "CGI art. 142 (1) b), e), (7) (30 %, at least 5 000 F per 1 000 imported cigarettes)" },
    { good := .tobaccoOther, name := "Droit d'accises (tabacs)", advBp := 3000, vatBp := 1925, statute := "CGI art. 142 (1) b), e)" } ]

def excise : Family := R4.exciseFamily "droit d'accises (CGI art. 142)" accises

def consumptionNotes (g : CanonGlobal) : List String :=
  (if g.consumption.isEmpty then [] else
    ["CGI art. 128 (VAT exemptions) not read: every basket line at 17,5 % + 10 % CAC"])
  ++ (if g.consumption.any (fun s => s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .nonAlcoholic) then
    ["CGI art. 142: excise on drinks (rate class and specific duties per centilitre) not read: not modelled"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel) then
    ["taxe spéciale sur les produits pétroliers: not read, not modelled"] else [])

-- 100 imported cigarettes at 1 000 F: net of VAT and CAC 838, base 645, 30 % = 193; minimum 500
#guard (R4.exciseCharges accises [{ good := .cigarettes, amount := 1000, quantity := 100000 }] ["cigarettes"]).map (·.due) == [500]
#guard (R4.exciseCharges accises [{ good := .cigarettes, amount := 1000, quantity := 100000 }]).map (·.due) == [193]
-- art. 142 (1) a) and C 54 (1): 17,5 % + 1,75 % = 19,25 % on the price before tax
#guard tva.embedded { good := .food, amount := 11925 } == 1925
#guard tva.embedded { good := .food, amount := 11924 } == 1924

end CmGlobal
