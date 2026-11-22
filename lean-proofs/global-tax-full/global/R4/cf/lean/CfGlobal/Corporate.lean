import R4Common

/-!
# Central African Republic 2025: corporate income tax (1200) and withholding (generated from `R4/specs/cf.json`)

Sources: Code général des impôts, édition officielle mise à jour 2023 (`cmp20/world/B08-central-africa-fr/cf/law/cgi2023.txt`); LF 2025 OCR pages 1-60 (`lf2025.ocr1-60.txt`).

art. 133: "Le taux de l'impôt est fixé à 30%, mais il est réduit à 20% pour les activités agricoles. Cependant, le montant de l'impôt dû par chaque personne morale ne peut être inférieur au minimum obtenu par application des taux au chiffre d'affaires" (art. 133 bis rates not read). art. 130: losses carried forward "jusqu'au troisième exercice qui suit l'exercice déficitaire".

art. 166 bis 1: "en ce qui concerne les revenus des capitaux mobiliers, la retenue à la source est effectuée au taux de 15% des revenus bruts distribués. S'agissant des rémunérations des prestations de services versées à l'étranger et sous réserve des conventions internationales, le taux de la retenue est de 15%. Cette retenue constitue pour le redevable un prélèvement libératoire"; services include "les travaux d'études, de recherches, et d'expertises ... les prestations de professions libérales" and assimilated "livraisons de biens meubles incorporels (brevets, marques etc.)". Art. 52 e: capital income paid to persons without domicile or seat in the CAR bears a final IRPP withholding at the art. 84 rate; art. 84: "application de 15% du montant brut des revenus distribués".
-/

namespace CfGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 300000
def whtR : Wht :=
  { name := "Retenues sur paiements à l'étranger",
    rules := [{ kind := .services, rateBp := 1500, statute := "CGI art. 166 bis 1 (15 %)" },
              { kind := .royalty, rateBp := 1500, statute := "CGI art. 166 bis 1 (patents, trademarks assimilated to services: 15 %)" },
              { kind := .dividend, rateBp := 1500, statute := "CGI art. 52 e, 84 (15 %)" },
              { kind := .interest, rateBp := 1500, statute := "CGI art. 52 e, 84 (15 %)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "CGI art. 133 (30 %; 20 % agriculture)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CGI art. 133: minimum on turnover (rates in art. 133 bis not read): not applied", "CGI art. 130: losses carry forward 3 years (age not an input)", "grade B: 2023 edition of the CGI; LF 2025 pages 1-60 held with no change to these articles found"]

end CfGlobal
