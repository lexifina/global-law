import R4Common
import R4Common.K21

/-!
# Senegal 2025: corporate income tax (1200) and withholding on payments abroad

Source: CGI annoté Janvier 2025 (`cmp20/world/B07-west-africa-fr-pt/sn/src/CGI-2025.txt`).

* **Impôt sur les sociétés** art. 36: "Le taux de l'impôt sur les sociétés est fixé à 30 % du bénéfice imposable.
  Toute fraction du bénéfice imposable inférieure à mille francs est négligée."
* **Impôt minimum forfaitaire** art. 38-40: due by companies whose result does not generate an IS above the tariff;
  art. 40: "dû sur le chiffre d'affaires hors taxes réalisé l'année précédant celle de l'imposition, à raison de
  0,5 %. … En aucun cas, le montant dû ne peut être supérieur à 5.000.000 francs." (no floor in the 2025 text).
* **Déficits** art. 16-1: deducted from the following years' profits "jusqu'au 3ème exercice qui suit l'exercice
  déficitaire" (no amount cap).
* **Revenus de capitaux mobiliers** art. 173 (rates of the tax withheld under art. 203 and 208, cf. art. 37): "10 %,
  pour les produits des actions, parts sociales …; 13 %, pour les revenus d'obligations; … 16 %, pour les autres
  revenus de capitaux mobiliers, notamment … les revenus des créances, dépôts et cautionnements".
* **Non-residents' fees and royalties** art. 202-3: "Le taux de la retenue, est fixé à 25 % du montant net des sommes
  imposables … Ce montant net est déterminé en appliquant aux encaissements bruts une déduction de 20 %" (20 % of the
  gross).
-/

namespace SnGlobal
open TaxKernel TaxKernel.Global

def is : CorpRegime := { name := "Impôt sur les sociétés", sched := Schedule.flat 3000 }

def imf : R4.MinTax := { bp := 50, cap := 5000000 }

def retenues : Wht :=
  { name := "Retenue à la source (non-résidents)",
    rules := [{ kind := .dividend, rateBp := 1000, statute := "CGI art. 173 (10 %), art. 203" },
              { kind := .interest, rateBp := 1600, statute := "CGI art. 173 (16 %, revenus des créances), art. 208" },
              { kind := .royalty, rateBp := 2000, statute := "CGI art. 202-3 (25 % of the gross less 20 %)" },
              { kind := .services, rateBp := 2000, statute := "CGI art. 202-3 (25 % of the gross less 20 %)" }] }

def corporate : Family :=
  (R4.corpRule is imf 1000).family "impôt sur les sociétés" "CGI art. 36 (30 %, base rounded down to 1 000 F), art. 38-40 (IMF 0,5 % of turnover, at most 5 000 000 F)" retenues

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.lossesForward ≠ 0 then ["CGI art. 16-1: losses carry forward 3 years; their age is not an input (all offset)"] else [])
  ++ ["CGI art. 40: the IMF is assessed on the previous year's turnover; the year's turnover is used"]

-- 30 % on 10 000 999 F: the fraction below 1 000 F is dropped
#guard R4.corpTax is imf { profit := 10000999, turnover := 100000000 } 1000 == 3000000
-- a loss-making company with 2 milliards of turnover pays the IMF cap (0,5 % = 10 M > 5 M)
#guard R4.corpTax is imf { profit := -5000000, turnover := 2000000000 } 1000 == 5000000
-- 0,5 % of 400 M = 2 M when the IS is lower
#guard R4.corpTax is imf { profit := 1000000, turnover := 400000000 } 1000 == 2000000
#guard retenues.amount { kind := .royalty, amount := 1000000 } == 200000


-- kernel 2.1 `CorpRule` (OHADA minimum, step 1 000) gives the R4 figures
#guard [(10000999, 100000000, 0), (-5000000, 2000000000, 0), (1000000, 400000000, 0), (10000000, 50000000, 30000000), (0, 1000000, 0)].all fun (p, t, l) => (R4.corpRule is imf 1000).tax 10000 { profit := p, turnover := t, lossesForward := l } == R4.corpTax is imf { profit := p, turnover := t, lossesForward := l } 1000

end SnGlobal
