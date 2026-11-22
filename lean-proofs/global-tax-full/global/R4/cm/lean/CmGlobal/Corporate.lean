import R4Common

/-!
# Cameroon 2025: impôt sur les sociétés (1200) and withholding — grade B

Source: CGI édition 2024 (`cmp20/world/B08-central-africa-fr/cm/law/cgi2024.raw.txt`) and the LF 2025 circular.

* **IS** art. 17 (1): "Le taux de l'impôt est fixé à 30 %"; (3): "toute fraction du bénéfice imposable inférieure à
  F CFA 1 000 est négligée".
* **Acompte / minimum de perception** art. 21 (1) a: "un acompte représentant 2 % du chiffre d'affaires réalisé au
  cours de chaque mois … Cet acompte est majoré de 10% au titre des centimes additionnels communaux"; art. 22: "Ce
  montant constitue le minimum de perception". Minimum = 2 % × 1,1 = 2,2 % of turnover.
* **CAC on the IS**: the acompte and minimum carry 10 % CAC (art. 21-22); the CAC article on the principal itself
  (Titre III of the local taxes book) was not read: the IS is booked at 30 % and the CAC at 10 % of it as a local
  charge, both cited to art. 17 and 21-22 (grade B).
* **Déficits** art. 12: carried forward "jusqu'au quatrième exercice qui suit l'exercice déficitaire".
* **IRCM** art. 70 (1): "un taux libératoire de 15 % sur le revenu imposable" (30 % to a tax haven; LF 2025 changes
  that and adds a reduced SME dividend rate: neither applies by default).
* Taxe spéciale sur les revenus (art. 225, non-residents' fees and royalties): rate not read (two-column OCR).
-/

namespace CmGlobal
open TaxKernel TaxKernel.Global

def is : CorpRegime := { name := "Impôt sur les sociétés", sched := Schedule.flat 3000 }

def minimum : R4.MinTax := { bp := 220 }

def ircm : Wht :=
  { name := "IRCM (retenue)",
    rules := [{ kind := .dividend, rateBp := 1500, statute := "CGI art. 70 (1) (15 %)" },
              { kind := .interest, rateBp := 1500, statute := "CGI art. 70 (1) (15 %)" }] }

/-- CGI (édition 2024) art. 225 (1): taxe spéciale sur les revenus on sums paid to persons domiciled outside Cameroon
for copyrights, software, patents and trade marks, and "d'une manière générale, des sommes versées à l'étranger, en
rémunération des prestations de toute nature fournies ou utilisées au Cameroun"; art. 225 ter (1)-(2): "taux général :
15 %" applies to all remunerations subject to it; art. 227: base = gross amount, TSR included. Twelfth pass. -/
def tsr : Wht :=
  { name := "Taxe spéciale sur les revenus (non-résidents)",
    rules := [{ kind := .royalty, rateBp := 1500, statute := "CGI 2024 art. 225 (1), 225 ter (1)-(2) (TSR 15 %)" },
              { kind := .services, rateBp := 1500, statute := "CGI 2024 art. 225 (1), 225 ter (1)-(2) (TSR 15 %)" }] }

def corporate : Family :=
  { name := "1200 impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      let isDue := R4.corpTax is minimum co 1000
      [R4.citCharge is minimum co "CGI art. 17 (30 %, fraction below 1 000 F dropped), art. 21-22 (minimum 2 % + 10 % CAC of turnover)" (step := 1000),
       charge .cit "Centimes additionnels communaux (IS)" isDue id
         (fun x => if x == R4.MinTax.amount minimum co && x > R4.regularStep is 1000 co then 0 else divR .down (1000 * x) BP)
         (level := .local) (statute := "10 % of the IS principal (CGI art. 21-22 show the 10 % CAC; Titre III not read)")]
      ++ ircm.charges co ++ tsr.charges co }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CGI art. 225 ter: TSR at the general 15 % (10 % / 3 % reduced rates for petroleum and one-off material services not applied)"]
  ++ (if g.company.lossesForward ≠ 0 then ["CGI art. 12: losses carry forward 4 years; their age is not an input"] else [])

#guard R4.corpTax is minimum { profit := 10000999, turnover := 100000000 } 1000 == 3000000
#guard R4.corpTax is minimum { profit := 0, turnover := 100000000 } 1000 == 2200000

end CmGlobal
