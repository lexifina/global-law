import R4Common

/-!
# Niger 2025: impôt sur les bénéfices (1200) and IRCM

Sources: CGI 2013 updated to the LF 2022 and the LF 2025 (ordonnance n° 2024-59).

* **ISB** art. 27: "Le taux de l'impôt sur les bénéfices est fixé à 30%, sans abattement, du bénéfice net imposable
  et arrondi au millier de francs inférieur."
* **IMF** art. 37 (LF 2025) 3.: "0,75% pour les entreprises industrielles; 2,5 % pour les autres activités; 5% pour
  les entreprises pour lesquelles l'IMF est calculé sur la marge brute …" (base: the turnover, art. 37 2.; no floor
  or cap read in the LF 2025 text).
* **IRCM** art. 74 (LF 2025): "10% pour les dividendes" (7 % for CREPMF-listed companies); "6% pour les revenus des
  obligations".
-/

namespace NeGlobal
open TaxKernel TaxKernel.Global

def isb : CorpRegime := { name := "Impôt sur les bénéfices", sched := Schedule.flat 3000 }

def imfOf (co : Company) : R4.MinTax := { bp := if co.flags.contains "industrial" then 75 else 250 }

def ircm : Wht :=
  { name := "IRCM (retenue)", rules := [{ kind := .dividend, rateBp := 1000, statute := "CGI art. 74 (LF 2025) (10 %)" },
      { kind := .interest, rateBp := 2000, statute := "CGI 2013 (MAJ LF 2022) art. 79-81 (impôt sur le revenu des créances 20 %; 10 % only on bank deposit and current accounts)" }] }

/-- CGI 2013 (MAJ LF 2022) art. 47: retenue à la source on "commissions, courtages, ristournes, honoraires, vacations,
redevances, droits d'auteur ou d'inventeur ou toutes autres prestations de service" paid by a debtor established in Niger
to persons without a fixed professional installation there; art. 48: "Le taux de la retenue est de 16 % du montant hors
TVA". LF 2025 (Ord. 2024-59) adds art. 49 ter-septies (retenue de conformité) and leaves art. 48. Twelfth pass. -/
def nonRes : Wht :=
  { name := "Retenue à la source (non-résidents)",
    rules := [{ kind := .royalty, rateBp := 1600, statute := "CGI art. 47-48 (16 %)" },
              { kind := .services, rateBp := 1600, statute := "CGI art. 47-48 (16 %)" }] }

def corporate : Family :=
  { name := "1200 impôt sur les bénéfices", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [R4.citCharge isb (imfOf g.company) g.company "CGI art. 27 (30 %, rounded down to 1 000 F), art. 37 (LF 2025) (IMF 2,5 %; 0,75 % industry)" (step := 1000)]
      ++ ircm.charges g.company ++ nonRes.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["withholding: LF 2023-2024 not held (art. 48, 80 as in the 2022 update and LF 2025)",
   "IMF on gross margin (5 % / 15 %) for traders and hydrocarbon marketers: not modelled"]

#guard R4.corpTax isb (imfOf {}) { profit := 10000999, turnover := 100000000 } 1000 == 3000000
#guard R4.corpTax isb (imfOf {}) { profit := 0, turnover := 100000000 } 1000 == 2500000

end NeGlobal
