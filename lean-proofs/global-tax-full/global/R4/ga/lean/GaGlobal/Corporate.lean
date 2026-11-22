import R4Common

/-!
# Gabon 2025: corporate income tax (1200) and withholding on payments abroad

Source: CGI 2025 (`cmp20/world/B08-central-africa-fr/ga/law/cgi2025.txt`).

* **IS** art. 16 (LF 2022): "le bénéfice imposable est arrondi au millier FCFA inférieur. Le taux est fixé à 30 %. Ce
  taux est porté à 35 % pour les entreprises du secteur pétrolier et minier."
* **IMF** art. 24 (LF 2024, LF 2025): "ne peut être inférieur à l'impôt minimum forfaitaire qui résulterait de
  l'application du taux de 1 % à la base de référence … ou à la somme de 500.000 FCFA correspondant au minimum de
  perception" (base, art. 25: the turnover).
* **Déficits** art. 11-IV: carried forward "jusqu'au cinquième exercice qui suit l'exercice déficitaire".
* **RCM** art. 109: "un prélèvement libératoire dont le taux est fixé à 20 %"; the revenues of "créances, dépôts et
  cautionnement" of persons not domiciled in Gabon: "un prélèvement dont le taux est de 20 %"; art. 116: companies 20 %.
* **Non-residents** art. 206 (LF 2024): fees, royalties, "prestations de toute nature" and interest in professional
  receipts: "Le taux de la retenue à la source est fixé à 25 % du montant brut des sommes versées hors taxe".
-/

namespace GaGlobal
open TaxKernel TaxKernel.Global

def isOf (co : Company) : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat (if co.flags.contains "petroleumMining" then 3500 else 3000) }

def imf : R4.MinTax := { bp := 100, floor := 500000 }

def retenues : Wht :=
  { name := "Retenue à la source (non-résidents)",
    rules := [{ kind := .dividend, rateBp := 2000, statute := "CGI art. 109, 116 (20 %)" },
              { kind := .interest, rateBp := 2000, statute := "CGI art. 109 al. 2 (20 %, non-domiciled)" },
              { kind := .royalty, rateBp := 2500, statute := "CGI art. 206 b) (25 % of the gross)" },
              { kind := .services, rateBp := 2500, statute := "CGI art. 206 a), c) (25 % of the gross)" }] }

def corporate : Family :=
  { name := "1200 impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [R4.citCharge (isOf g.company) imf g.company
        "CGI art. 16 (30 %; 35 % oil and mining; base rounded down to 1 000 F), art. 24-25 (IMF 1 %, at least 500 000 F)" (step := 1000)]
      ++ retenues.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.lossesForward ≠ 0 then ["CGI art. 11-IV: losses carry forward 5 years; their age is not an input"] else [])

#guard R4.corpTax (isOf {}) imf { profit := 10000999, turnover := 100000000 } 1000 == 3000000
#guard R4.corpTax (isOf { flags := ["petroleumMining"] }) imf { profit := 10000000, turnover := 1 } 1000 == 3500000
#guard R4.corpTax (isOf {}) imf { profit := 0, turnover := 10000000 } 1000 == 500000
#guard retenues.amount { kind := .services, amount := 1000000 } == 250000

end GaGlobal
