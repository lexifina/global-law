import R4Common
import R4Common.K21

/-!
# Togo 2025: corporate income tax (1200) and withholding on payments abroad

Source: CGI et LPF édition 2025 (`cmp20/world/B07-west-africa-fr-pt/tg/law/rescue2/otr_cgi_lpf_2025.txt`).

* **IS** art. 113: "toute fraction du bénéfice imposable inférieure à mille (1 000) francs CFA est négligée. Le taux
  de l'impôt sur les sociétés est fixé à 27 % du bénéfice imposable."
* **Minimum forfaitaire de perception** art. 120: "dû en cas de déficit ou lorsque le résultat fiscal ne permet pas
  de déterminer un impôt supérieur à celui-ci. Il est fait application d'un taux de 1% du chiffre d'affaires hors
  taxe … du dernier exercice clos. … En aucun cas, son montant ne peut être inférieur à vingt mille (20 000) francs CFA
  pour les contribuables qui sont au régime du bénéfice réel".
* **Déficit** art. 101: "déduit dans la limite de 50% du bénéfice réalisé pendant ledit exercice. Le solde du déficit
  est reporté sur les exercices suivants sans limitation de durée".
* **IRCM** art. 79 (revenus variables, personne morale): "13% du montant des revenus distribués"; art. 80 (revenus
  fixes): companies "6% pour les autres revenus", individuals "13% libératoire".
* **Non-residents** LPF art. 98: fees, royalties and "prestations de toute nature" paid to persons without a
  permanent installation in Togo: "Le taux de la retenue est fixé à 20 % des sommes et produits bruts".
-/

namespace TgGlobal
open TaxKernel TaxKernel.Global

def is : CorpRegime := { name := "Impôt sur les sociétés", sched := Schedule.flat 2700, lossFull := 0, lossExcessBp := 5000 }

def mfp : R4.MinTax := { bp := 100, floor := 20000 }

def retenues : Wht :=
  { name := "Retenue à la source (non-résidents)",
    rules := [{ kind := .dividend, rateBp := 1300, statute := "CGI art. 79 (13 %)" },
              { kind := .interest, toCompany := some true, rateBp := 600, statute := "CGI art. 80 (6 %, personne morale)" },
              { kind := .interest, toCompany := some false, rateBp := 1300, statute := "CGI art. 80 (13 %, personne physique)" },
              { kind := .royalty, rateBp := 2000, statute := "LPF art. 98 (20 % of the gross)" },
              { kind := .services, rateBp := 2000, statute := "LPF art. 98 (20 % of the gross)" }] }

def corporate : Family :=
  (R4.corpRule is mfp 1000).family "impôt sur les sociétés" "CGI art. 101 (losses: 50 % of the profit, no time limit), art. 113 (27 %), art. 120 (minimum 1 % of turnover, at least 20 000 F)" retenues

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CGI art. 120: the minimum is on the last closed year's turnover; the year's turnover is used"]
  ++ (if g.company.flags.contains "usedCarImporter" then ["CGI art. 120: 2 % for importers of used vehicles not modelled"] else [])

-- art. 101: 10 M profit, 30 M losses: half the profit offset, IS 27 % of 5 M
#guard R4.corpTax is mfp { profit := 10000000, lossesForward := 30000000, turnover := 50000000 } 1000 == 1350000
-- loss year: 1 % of 400 M
#guard R4.corpTax is mfp { profit := -1, turnover := 400000000 } 1000 == 4000000
-- the floor: 20 000 F
#guard R4.corpTax is mfp { profit := 0, turnover := 1000000 } 1000 == 20000
#guard retenues.amount { kind := .interest, amount := 1000000, toCompany := false } == 130000


-- kernel 2.1 `CorpRule` (OHADA minimum, step 1 000) gives the R4 figures
#guard [(10000999, 100000000, 0), (-5000000, 2000000000, 0), (1000000, 400000000, 0), (10000000, 50000000, 30000000), (0, 1000000, 0)].all fun (p, t, l) => (R4.corpRule is mfp 1000).tax 10000 { profit := p, turnover := t, lossesForward := l } == R4.corpTax is mfp { profit := p, turnover := t, lossesForward := l } 1000

end TgGlobal
